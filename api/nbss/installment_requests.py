import allure
from playwright.async_api import APIRequestContext

from api.base_requests import BaseRequests
from api.nbss.billing_requests import BillingRequests
from common.helpers.checker import wait_that
from common.helpers.env_helper import BASE_URL_API
from models.installment import InstallmentTypeStatusMap
from models.user import BaseClient


class InstallmentRequests(BaseRequests):
    def __init__(self, api_request_auth_context: APIRequestContext):
        super().__init__(api_request_auth_context)
        self.billing_api = BillingRequests(api_request_auth_context)
        self.installment_type = "default"
        self.installment_type_status_map = InstallmentTypeStatusMap().map

    @allure.step("API: Получение списка рассрочек по billingProfileId")
    def get_installments_by_bill_prof_id(self, bill_prof_id: int) -> list:
        payload = {"billingProfile": {"billingProfileId": bill_prof_id}}
        installments = self.post(url=f"{BASE_URL_API}/bss-box/v1/billing/installments/search", data=payload)
        self.check_response_status(installments, 200, "Не удалось получить список рассрочек")
        installments_list = [item["installmentId"] for item in installments.json()["items"]]
        return installments_list

    @allure.step("API: Получение списка рассрочек по клиенту")
    def get_installments(self, client: BaseClient) -> list:
        """
        Метод для получения списка рассрочек на новом клиенте. Берет самый первый договор и ЛС.
        Далее получает bill_prof_id по ЛС и передает в get_installments_by_bill_prof_id.
        :param client: объект класса BaseClient
        :return list: список id рассрочек
        """
        return self.get_installments_by_bill_prof_id(
            self.billing_api.get_billing_profile_id(client.agreements[0].accounts[0].id)
        )

    @allure.step("API: Получение статуса рассрочки")
    def get_installment_status_by_installment_id(self, installment_id: int) -> str:
        installment = self.get(url=f"{BASE_URL_API}/bss-box/v1/billing/installments/{installment_id}")
        self.check_response_status(installment, 200, "Не удалось получить список рассрочек")
        return installment.json()["installmentStatus"]["name"]

    @allure.step("API: Получение статуса первоначального платежа")
    def get_initial_payment_status(self, installment_id: int) -> str:
        """
        Метод для получения статуса первоначального платежа
        :param installment_id: id рассрочки
        :return str: строковое описание статуса (например "Оплачен")
        """
        installment = self.get(url=f"{BASE_URL_API}/bss-box/v1/billing/installments/{installment_id}")
        self.check_response_status(installment, 200, "Не удалось получить список рассрочек")
        return installment.json()["initialPayment"]["installmentPaymentStatus"]["name"]

    @allure.step("API: Получение статуса рассрочки")
    def get_installment_status(self, client: BaseClient) -> str:
        return self.get_installment_status_by_installment_id(self.get_installments(client)[-1])

    @allure.step("API: Проверка оплаты первоначального платежа")
    def check_initial_payment_done_status(self, client: BaseClient, status_timeout: int = 15) -> None:
        wait_that(
            lambda: self.get_initial_payment_status(self.get_installments(client)[-1]) == "Оплачен",
            message=f"Заявка не поменяла статус первоначального платежа на Оплачен за {status_timeout} секунд",
            timeout=status_timeout,
            exception=TimeoutError,
        )

    @allure.step("API: Проверка статуса рассрочки")
    def check_installment_done_status(self, client: BaseClient, status_timeout: int = 15) -> None:
        status = self.installment_type_status_map[self.installment_type]
        wait_that(
            lambda: self.get_installment_status(client) == status,
            message=f"Заявка не поменяла свой статус на {status} за {status_timeout} секунд",
            timeout=status_timeout,
            exception=TimeoutError,
        )
