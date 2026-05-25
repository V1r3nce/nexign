import allure

from api.base_requests import BaseRequests
from common.helpers.env_helper import BASE_URL_LIS


class NomenclatureRequests(BaseRequests):
    @allure.step("API: Получение номенклатур")
    def get_nomenclatures(self) -> list:
        response = self.post(f"{BASE_URL_LIS}/openapi/v1/inventoryManagement/nomenclatures/search")
        self.check_response_status(response, 200, "Не получен список номенклатур")
        return response.json().get("items", [])
