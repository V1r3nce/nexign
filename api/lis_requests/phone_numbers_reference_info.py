import allure
import pytest

from api.base_requests import BaseRequests
from common.helpers.env_helper import BASE_URL_LIS


class PhoneNumbersReferenceInfoRequests(BaseRequests):
    @pytest.mark.lis
    def __init__(self) -> None:
        super().__init__()

    @allure.step("API: Получение типов номеров")
    def get_phone_numbers_types(self, macro_region_ids: list) -> list:
        payload = {"macroRegionIds": macro_region_ids}
        response = self.post(
            f"{BASE_URL_LIS}/openapi/v1/dictionaries/logicalResources/phoneNumberTypes/search", json=payload
        )
        self.check_response_status(response, 200, "Не получена типы номеров телефонов")
        return response.json().get("items", [])

    @allure.step("API: Получение операторов")
    def get_operators(self, macro_region_ids: list) -> list:
        payload = {"macroRegionIds": macro_region_ids, "isOwn": True}
        response = self.post(f"{BASE_URL_LIS}/openapi/v1/dictionaries/logicalResources/operators/search", json=payload)
        self.check_response_status(response, 200, "Не получена информация об операторах")
        return response.json().get("items", [])

    @allure.step("API: Получение типов связок номеров")
    def get_phone_numbers_type_links(self, macro_region_ids: list) -> list:
        payload = {"macroRegionIds": macro_region_ids}
        response = self.post(
            f"{BASE_URL_LIS}/openapi/v1/dictionaries/logicalResources/phoneNumberTypeLinks/search", json=payload
        )
        self.check_response_status(response, 200, "Не получена информация о связках")
        return response.json().get("items", [])

    @allure.step("API: Получение категорий номеров")
    def get_numbers_categories(self, macro_region_ids: list) -> list:
        payload = {"macroRegionIds": macro_region_ids}
        response = self.post(
            f"{BASE_URL_LIS}/openapi/v1/dictionaries/logicalResources/numberCategories/search", json=payload
        )
        self.check_response_status(response, 200, "Не получены категории номеров")
        return response.json().get("items", [])
