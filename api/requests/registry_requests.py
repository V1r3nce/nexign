import allure
from playwright.sync_api import APIRequestContext, APIResponse

from api.requests.base_requests import BaseRequests
from common.helpers.env_helper import BASE_URL_API


class RegistryRequests(BaseRequests):
    def __init__(self, api_request_auth_context: APIRequestContext):
        super().__init__(api_request_auth_context)

    @allure.step("Получить список платежей реестра'")
    def get_registry_list(self, start_date: str, end_date: str, sort_by: str | None = None) -> APIResponse:
        """
        Получить список платежей реестра
        """
        params = {"limit": 60, "sort": sort_by, "offset": 0}
        payload = {"amount": {},
                   "paymentDate": {"maxValue": f"{end_date}T23:59:59.999Z", "minValue": f"{start_date}T00:00:00.000Z"}}
        registry_list = self.post(
            url=f"{BASE_URL_API}/bss-box/v2/payments-gateway/payments/search", params=params, data=payload)
        self.check_response_status(registry_list, 200, "Не получен список реестра")
        return registry_list
