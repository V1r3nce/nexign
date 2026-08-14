import allure
import pytest

from api.base_requests import BaseRequests
from api.exceptions import GetEquipmentsException
from common.helpers.checker import assert_that, wait_that
from common.helpers.env_helper import BASE_URL_API, BASE_URL_LIS
from models.lis_resources import Equipment


class EquipmentRequests(BaseRequests):
    @pytest.mark.lis
    def __init__(self) -> None:
        super().__init__()
        self.macro_region_id = 999
        self.default_macro_list = [0, 999]

    @allure.step("API: Поиск серийных номеров оборудования")
    def search_serial_number(
        self, nomenclature: str, partner_point_id: int, limit: int = 60, inventory_status: int = 1
    ) -> list:
        """
        :param nomenclature: номенклатура, по которой мы ищем оборудование. пример: at_L_001
        :param partner_point_id: id точки партнера
        :param limit: лимит по количеству серийных номеров в ответе
        :return: список серийных номеров
        """
        default_params = {"limit": limit, "offset": 0}
        payload = {
            "inventoryItemStatusIds": [inventory_status],
            "partnerPointIds": [partner_point_id],
            "serialNumbers": [{"nomenclature": {"code": nomenclature}}],
        }
        response = self.post(
            f"{BASE_URL_API}/openapi/v1/inventoryManagement/inventoryItems/search", params=default_params, json=payload
        )
        self.check_response_status(response, 200, "Невозможно получить список доступного оборудования")
        result = []
        for item in response.json()["items"]:
            result.append(item["serialNumber"])
        return result

    @allure.step("API: Получить список коммутаторов LIS")
    def get_equipment(
        self,
        standard_id: list = None,
        equipment_type_id: list = None,
        macro_region_id: list | None = None,
        name: str = None,
        limit: int = 100,
    ) -> list:
        """
        :param standard_id: id стандарта оборудования
        :param equipment_type_id: id типа оборудования
        :param macro_region_id: id макрорегиона
        :return: словарь в котором ключ - id оборудования, значение - название оборудования
        """
        params = {"limit": limit}
        payload = {"macroRegionIds": self.default_macro_list if not macro_region_id else macro_region_id}
        if equipment_type_id:
            payload["equipmentTypeIds"] = equipment_type_id
        if standard_id:
            payload["standardIds"] = standard_id
        if name:
            payload["name"] = name

        equipment = self.post(
            url=f"{BASE_URL_LIS}/openapi/v1/logicalResources/equipments/search", json=payload, params=params
        )
        self.check_response_status(equipment, 200, "Не получен список коммутаторов")
        response = equipment.json()
        return response.get("items", [])

    @allure.step("API: Получение коммутатора по названию")
    def get_equipment_by_name(self, name: str) -> Equipment:
        item = self.get_equipment(name=name)[0]
        return Equipment.model_validate(item)

    @allure.step("API: Получение идентификаторов коммутаторов")
    def get_equipment_ids(
        self,
        standard_id: list = None,
        equipment_type_id: list = None,
        macro_region_id: list | None = None,
        name: str = None,
        limit: int = 100,
    ) -> dict:
        items = self.get_equipment(standard_id, equipment_type_id, macro_region_id, name, limit)
        result = {}
        for item in items:
            equipment_id = item.get("equipmentId", None)
            name = item.get("name", None)
            if equipment_id is not None and name is not None:
                result[equipment_id] = name

        return result

    @allure.step("API: Ожидание появления коммутатора в ответе API")
    def wait_equipment_with_name(self, switch_name: str) -> None:
        """
        :param switch_name: наименование коммутатора
        """
        wait_that(
            lambda: len(self.get_equipment_ids(name=switch_name)) == 1,
            exception=GetEquipmentsException,
            message="Коммутатор не вернулся в ответе от LIS",
            timeout=10,
            sleep_seconds=2,
        )

    @allure.step("API: Создать коммутатор с наименованием {0}")
    def create_switch(self, switch_name: str, standard_id: int, zone_id: int = 0, region_id: int = 0) -> None:
        """
        :param switch_name: наименование коммутатора
        :param standard_id: id стандарта оборудования
        :param zone_id: id зоны
        :param region_id: id региона
        """
        payload = {
            "name": switch_name,
            "equipmentStateId": 1,
            "equipmentTypeId": 1,
            "standardId": standard_id,
            "zoneId": zone_id,
            "regionId": region_id,
            "endPoint": "2",
            "isVirtual": False,
            "isActive": True,
            "isMaster": False,
            "macroRegionIds": [999],
            "macroRegionId": 999,
        }

        response = self.post(url=f"{BASE_URL_LIS}/openapi/v1/logicalResources/equipments", json=payload)
        self.check_response_status(response, 204, "Ошибка при создании коммутатора")

    @allure.step("API: Отключить коммутатор с наименованием {0}")
    def turn_off_switch(self, switch_name: str) -> None:
        """
        :param switch_name: наименование коммутатора
        """

        equipment_id = list(self.get_equipment_ids(name=switch_name).keys())[0]
        payload = {"isActive": False, "macroRegionId": 999}

        response = self.put(url=f"{BASE_URL_LIS}/openapi/v1/logicalResources/equipments/{equipment_id}", json=payload)
        self.check_response_status(response, 204, "Ошибка при отключении коммутатора")

    @allure.step("API: Получение типов коммутаторов")
    def get_equipments_types(self) -> list:
        data = {"macroRegionIds": self.default_macro_list}
        response = self.post(f"{BASE_URL_LIS}/openapi/v1/dictionaries/logicalResources/equipmentTypes/search", json=data)
        self.check_response_status(response, [200, 204], "Не получен список типов оборудования")
        result = response.json().get("items", None)
        assert_that(lambda: result is not None, "Получен пустой список типов оборудования")
        return result

    @allure.step("API: Получение стандартов коммутаторов")
    def get_equipment_standards(self) -> list:
        data = {"macroRegionIds": self.default_macro_list}
        response = self.post(
            f"{BASE_URL_LIS}/openapi/v1/dictionaries/logicalResources/netStandardsForEquipment/search", json=data
        )
        self.check_response_status(response, [200, 204], "Не получен список стандартов")
        result = response.json().get("items", None)
        assert_that(lambda: result is not None, "Получен пустой список стандартов")
        return result
