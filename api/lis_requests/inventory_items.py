import allure

from api.base_requests import BaseRequests
from common.const import Constants
from common.helpers.checker import check_that, wait_that
from common.helpers.env_helper import BASE_URL_LIS
from common.helpers.retry import retry
from models.lis_resources import InventoryItem, Nomenclature, SimCardData
from models.stand_context import stand_context


class InventoryItemsRequests(BaseRequests):
    @allure.step("API: Получение списка оборудования")
    def get_inventory_items(
        self, nomenclature: Nomenclature | None, sort: str | None = None, limit: int = 20
    ) -> list[InventoryItem]:
        if sort is None:
            if nomenclature.is_serial:
                sort = "-inventoryItemId"
            else:
                sort = "code"
        payload = {}
        if nomenclature is not None:
            payload = {
                "nomenclatures": [
                    {"code": nomenclature.code, "stockSystemId": nomenclature.stock_system.stock_system_id}
                ]
            }
        params = {"sort": sort, "limit": limit}
        response = self.post(
            f"{BASE_URL_LIS}/openapi/v1/inventoryManagement/inventoryItems/search", json=payload, params=params
        )
        self.check_response_status(response, 200, "Не удалось получить список оборудования у номенклатуры")
        result = []
        for item in response.json().get("items", []):
            result.append(InventoryItem.model_validate(item))
        return result

    @allure.step("API: Добавить оборудование")
    def add_inventory_item(
        self, nomenclature: Nomenclature, item_serial_numbers: list | None, partner_point_id: int, count: int = 1
    ) -> None:
        item_list = []
        for serial_number in item_serial_numbers:
            item_list.append(
                {
                    "code": nomenclature.code,
                    "partnerPointId": partner_point_id,
                    "serialNumber": str(serial_number),
                }
            )
        payload = {
            "stockSystemId": nomenclature.stock_system.stock_system_id,
            "items": item_list
            if item_serial_numbers is not None
            else {
                "code": nomenclature.code,
                "partnerPointId": partner_point_id,
                "goodsCount": count,
            },
        }
        response = self.post(f"{BASE_URL_LIS}/openapi/v1/inventoryManagement/inventoryItems/insert/bulk", json=payload)
        self.check_response_status(response, 204, "Не выполнен запрос на добавление оборудования для номенклатуры")

    @allure.step("API: Ожидание появления оборудования")
    def wait_added_inventory_items(self, nomenclature: Nomenclature, item_serial_numbers: list) -> list[InventoryItem]:
        items_count = len(item_serial_numbers)
        wait_that(
            lambda: (
                item_serial_numbers[-1] in [int(item.serial_number) for item in self.get_inventory_items(nomenclature)]
            ),
            timeout=120,
            sleep_seconds=5,
            exception=AssertionError,
            message="Добавленное оборудование не появилось в списке",
        )
        items = self.get_inventory_items(nomenclature, limit=2 * items_count)
        founded = 0
        i = 0
        result = []
        while i < 2 * items_count and founded != items_count:
            if int(items[i].serial_number) in item_serial_numbers:
                founded += 1
                result.append(items[i])
            i += 1
        check_that(lambda: founded == items_count, ValueError, "Не удалось добавить оборудование")
        return result

    @allure.step("API: Генерация оборудования для номенклатуры")
    @retry(delay=Constants.LIS_RETRY_DELAY, exceptions=Constants.LIS_RETRY_EXCEPTIONS)
    def generate_inventory_item(
        self, nomenclature: Nomenclature, count: int, partner_point_id: int, force: bool = False
    ) -> list[InventoryItem] | None:
        inventory_items = self.get_inventory_items(nomenclature=nomenclature, limit=count * 2)
        available_count = 0
        for inventory_item in inventory_items:
            if inventory_item.reserved_code is None:
                available_count += 1
        if not force and not stand_context.force_generate and available_count >= count:
            return None
        if nomenclature.is_serial:
            items = self.get_inventory_items(nomenclature)
            if len(items) == 0:
                start_number = 0
            else:
                start_number = int(items[0].serial_number) + 1
            item_serial_numbers = [start_number + i for i in range(count)]
            self.add_inventory_item(nomenclature, item_serial_numbers, partner_point_id)
            return self.wait_added_inventory_items(nomenclature, item_serial_numbers)
        else:
            self.add_inventory_item(
                nomenclature, item_serial_numbers=None, count=count, partner_point_id=partner_point_id
            )
            return None

    @allure.step("API: Связывание оборудования и SIM")
    @retry(delay=Constants.LIS_RETRY_DELAY, exceptions=Constants.LIS_RETRY_EXCEPTIONS)
    def inventory_items_link(
        self, inventory_item_list: list[InventoryItem], linked_resource_list: list[SimCardData]
    ) -> None:
        check_that(
            lambda: len(inventory_item_list) == len(linked_resource_list),
            ValueError,
            "Переданы некорректные данные для связывания",
        )
        bundle_items_list = []
        inventory_item_bundle_item_type_id = stand_context.stand_equipment.inventory_item_bundle_item_type_id
        sim_bundle_item_type_id = stand_context.stand_equipment.sim_bundle_item_type_id
        for i in range(len(inventory_item_list)):
            bundle_item = []
            bundle_item.append(
                {
                    "bundleItemTypeId": inventory_item_bundle_item_type_id,
                    "inventoryItemId": inventory_item_list[i].inventory_item_id,
                }
            )
            bundle_item.append(
                {"bundleItemTypeId": sim_bundle_item_type_id, "externalItemId": int(linked_resource_list[i].icc)}
            )
            bundle_items_list.append({"inventoryBundleItems": bundle_item})
        payload = {"items": bundle_items_list}
        response = self.post(f"{BASE_URL_LIS}/openapi/v1/inventoryManagement/inventoryBundles/bind/bulk", json=payload)
        self.check_response_status(response, 200, "Неудачная попытка связывания оборудования")
