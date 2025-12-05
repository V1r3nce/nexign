import allure

from api.base_requests import BaseRequests
from common.helpers.env_helper import BASE_URL_API, BASE_URL_LIS


class EquipmentRequests(BaseRequests):
    def __init__(self) -> None:
        super().__init__()
        self.macro_region_id = 999

    @allure.step("API: Поиск серийных номеров оборудования")
    def search_serial_number(self, nomenclature: str, partner_point_id: int) -> list:
        """
        :param nomenclature: номенклатура, по которой мы ищем оборудование. пример: at_L_001
        :param partner_point_id: id точки партнера
        :return: список серийных номеров
        """
        default_params = {"limit": 60, "offset": 0}
        payload = {
            "inventoryItemStatusIds": [1],
            "partnerPointIds": [partner_point_id],
            "serialNumbers": [{"nomenclature": {"code": nomenclature}}],
        }
        response = self.post(
            f"{BASE_URL_API}/openapi/v1/inventoryManagement/inventoryItems/search", params=default_params, data=payload
        )
        self.check_response_status(response, 200, "Невозможно получить список доступного оборудования")
        result = []
        for item in response.json()["items"]:
            result.append(item["serialNumber"])
        return result

    @allure.step("API: Получить список коммутаторов LIS")
    def get_equipment(
        self,
        standard_id: list,
        equipment_type_id: list,
        macro_region_id: list | None = None,
    ) -> dict:
        """
        :param standard_id: id стандарта оборудования
        :param equipment_type_id: id типа оборудования
        :param macro_region_id: id макрорегиона
        :return: словарь в котором ключ - id оборудования, значение - название оборудования
        """
        payload = {
            "equipmentTypeIds": equipment_type_id,
            "macroRegionIds": [self.macro_region_id] if not macro_region_id else macro_region_id,
            "SIMCardProjectId": None,
            "standardIds": standard_id,
        }
        equipment = self.post(url=f"{BASE_URL_LIS}/OAPI/v1/logicalResources/equipments/search", data=payload)
        self.check_response_status(equipment, 200, "Не получен список коммутаторов")
        if "items" in equipment.json() and len(equipment.json()["items"]) > 0:
            result = {}
            for item in equipment.json()["items"]:
                result[item["equipmentId"]] = item["name"]
            return result
        else:
            raise AssertionError("Список коммутаторов пуст")
