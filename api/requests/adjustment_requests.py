import allure
from playwright.sync_api import APIRequestContext

from api.exceptions import AdjustmentStatusException
from api.requests.base_requests import BaseRequests
from api.requests.billing_requests import BillingRequests
from common.helpers.checker import wait_that
from common.helpers.env_helper import BASE_URL_API


class AdjustmentRequests(BaseRequests):
    def __init__(self, api_request_auth_context: APIRequestContext):
        super().__init__(api_request_auth_context)
        self.billing_api = BillingRequests(api_request_auth_context)

    @allure.step("API: Получение списка корректировок")
    def get_adjustment_list(self, account_id: int) -> dict:
        billing_profile_id = self.billing_api.get_billing_profile_id(account_id)
        params = {"limit": 30, "sort": "-adjustmentDate", "offset": 0}
        payload = {"billingProfileId": billing_profile_id}
        adjustments = self.post(url=f"{BASE_URL_API}/bss-box/v1/finance/adjustments/search", params=params, data=payload)
        self.check_response_status(adjustments, 200, "Не удалось получить список корректировок")
        return adjustments.json()

    @allure.step("Ожидание статуса последней корректировки")
    def wait_adjustment_status(self, account_id: int, adjustment_status_id: int = 2) -> None:
        wait_that(
            lambda: self.get_adjustment_list(account_id)["items"][0]["statusInfo"]["status"]["adjustmentStatusId"]
            == adjustment_status_id,
            timeout=20,
            sleep_seconds=0.5,
            exception=AdjustmentStatusException,
            message="Корректировка не перешла в указанный статус за указанное время",
        )
