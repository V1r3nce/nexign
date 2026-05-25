import allure

from api.base_requests import BaseRequests
from api.exceptions import CreatePaymentException
from common.helpers.checker import wait_that
from common.helpers.env_helper import BASE_URL_API
from models.playwright_bridge import GeneralResponse


class RegistryRequests(BaseRequests):
    @allure.step("API: Получить список платежей реестра'")
    def get_registry_list(
        self, start_date: str, end_date: str, doc_num: str, sort_by: str | None = None
    ) -> GeneralResponse:
        """
        Получить список платежей реестра
        """
        params = {"limit": 60, "sort": sort_by, "offset": 0}
        payload = {
            "amount": {},
            "documentNumber": doc_num,
            "paymentDate": {"maxValue": f"{end_date}T23:59:59.999Z", "minValue": f"{start_date}T00:00:00.000Z"},
        }
        registry_list = self.post(
            url=f"{BASE_URL_API}/bss-box/v2/payments-gateway/payments/search", params=params, json=payload
        )
        self.check_response_status(registry_list, 200, "Не получен список реестра")
        return registry_list

    @allure.step("Ожидание появления платежа на сумму {payment_amount} в реестре")
    def wait_last_payment_amount_in_registry(self, day: str, doc_number: str | int, payment_amount: int) -> None:
        wait_that(
            lambda: self.get_registry_list(day, day, doc_number, "-paymentDate").json()["items"][0]["amount"]["amount"]
            == payment_amount,
            timeout=25,
            sleep_seconds=0.5,
            exception=CreatePaymentException,
            message="Платеж не появился в указанное время",
        )

    @allure.step("Ожидание статуса для документа {doc_number} в реестре")
    def wait_payment_for_doc_status(self, day: str, doc_number: str | int, status: str = "SUCCEEDED") -> None:
        """
        Метод ожидает установления определенного статуса для документа в реестре

        :param day: день реестра в формате строки
        :param doc_number: номер документа (может быть строкой или числом)
        :param status: ожидаемый статус документа (по умолчанию "SUCCEEDED")
        :raises CreatePaymentException: если статус не обновился в течение указанного времени
        """
        wait_that(
            lambda: self.get_registry_list(day, day, doc_number, "-paymentDate").json()["items"][0]["status"]["code"]
            == status,
            timeout=25,
            sleep_seconds=0.5,
            exception=CreatePaymentException,
            message="Статус не обновился в указанное время",
        )
