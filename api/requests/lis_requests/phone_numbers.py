import allure
from playwright.sync_api import APIRequestContext


class PhoneNumbersRequests:
    def __init__(self, api_request_auth_context: APIRequestContext):
        self.api_request_auth_context = api_request_auth_context

    @allure.step("Получить список телефонных номеров LIS")
    def get_phone_numbers(self, server_url: str, type_def: bool = True, status_id: [None, list] = None,
                          state_id: [None, list] = None, num_sort: [None, str] = None):
        """
        Получить список телефонных номеров LIS
        """
        payload = {"returnCount": True, "macroRegionIds": [1], "isTypeDEF": type_def, "includeInternalMNP": True}
        if status_id:
            payload["statusIds"] = status_id
        if state_id:
            payload["stateIds"] = state_id
        params = {"limit": 50, "offset": 0}
        if num_sort:
            params["sort"] = num_sort
        phone_numbers = self.api_request_auth_context.post(url=f"{server_url}/OAPI/v1/lis/logicalResources/phoneNumbers/search",
                                                           data=payload, params=params)
        assert phone_numbers.status == 200, "Не получен список телефонных номеров"
        return phone_numbers
