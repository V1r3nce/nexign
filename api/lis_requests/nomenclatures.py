import allure

from api.base_requests import BaseRequests
from common.helpers.env_helper import BASE_URL_LIS


class NomenclatureRequests(BaseRequests):
    @allure.step("API: Получение номенклатур")
    def get_nomenclatures(self) -> list:
        response = self.post(f"{BASE_URL_LIS}/openapi/v1/inventoryManagement/nomenclatures/search")
        self.check_response_status(response, 200, "Не получен список номенклатур")
        return response.json().get("items", [])

    @allure.step("API: Добавление номенклатуры")
    def add_nomenclature(self, stock_system_id: int, code: str, is_serial: bool = True) -> None:
        payload = {
            "stockSystemId": stock_system_id,
            "items": [{"code": code, "name": code, "isSerial": is_serial, "isActive": True}],
        }
        response = self.post(f"{BASE_URL_LIS}/openapi/v1/inventoryManagement/nomenclatures/insert/bulk", json=payload)
        self.check_response_status(response, 204, "Не выполнен запрос на добавление номенклатуры")
