import allure
from playwright.async_api import APIRequestContext

from api.requests.base_requests import BaseRequests
from common.helpers.env_helper import BASE_URL_API


class InstallmentRequests(BaseRequests):
    def __init__(self, api_request_auth_context: APIRequestContext):
        super().__init__(api_request_auth_context)

    @allure.step("API: Получение списка рассрочек по billingProfileId")
    def get_installments_by_bill_prof_id(self, bill_prof_id: int) -> list:
        payload = {"billingProfile": {"billingProfileId": bill_prof_id}}
        installments = self.post(url=f"{BASE_URL_API}/bss-box/v1/billing/installments/search", data=payload)
        self.check_response_status(installments, 200, "Не удалось получить список рассрочек")
        installments_list = [item["installmentId"] for item in installments.json()["items"]]
        return installments_list

    @allure.step("API: Получение статуса рассрочки")
    def get_installment_status(self, installment_id: int) -> str:
        installment = self.post(url=f"{BASE_URL_API}/bss-box/v1/billing/installments/{installment_id}")
        self.check_response_status(installment, 200, "Не удалось получить список рассрочек")
        return installment.json()["installmentStatus"]["name"]
