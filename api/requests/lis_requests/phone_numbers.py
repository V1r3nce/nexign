import allure
from playwright.sync_api import APIRequestContext


class PhoneNumbersRequests:
    def __init__(self, api_request_auth_context: APIRequestContext):
        self.api_request_auth_context = api_request_auth_context

    @allure.step("Получить список телефонных номеров LIS")
    def get_phone_numbers(self, server_url: str, type_def: bool = True):
        """
        Получить список телефонных номеров LIS
        """
        payload = {"returnCount": True, "macroRegionIds": [1], "isTypeDEF": type_def, "includeInternalMNP": True}
        params = {"limit": 50, "offset": 0}
        phone_numbers = self.api_request_auth_context.post(url=f"{server_url}/OAPI/v1/lis/logicalResources/phoneNumbers/search",
                                                           data=payload, params=params)
        assert phone_numbers.status == 200, "Не получен список телефонных номеров"
        return phone_numbers
