from dataclasses import dataclass

import allure
from playwright.sync_api import APIRequestContext, APIResponse

from api.exceptions import CreateAdjustmentException, CreatePaymentException, UpdateStatusException
from api.requests.base_requests import BaseRequests
from common.helpers.checker import wait_that
from common.helpers.data_generator import generate_random_number, get_current_datetime_string_for_api
from common.helpers.env_helper import BASE_URL_API, UniblpUserData
from common.helpers.string_helper import convert_string_to_base64
from models.user import PaymentInfo


class PaymentsRequests(BaseRequests):
    def __init__(self, api_request_auth_context: APIRequestContext):
        super().__init__(api_request_auth_context)

    @allure.step("API: Проверка возможности создать новый платеж")
    def check_create_payment(self, payment: PaymentInfo) -> APIResponse:
        """
        Метод проверяет, возникнут ли конфликты при создании нового платежа.

        Parameters:
        payment (PaymentInfo): параметры платежа

        Returns:
        APIResponse: объект ответа API с данными о конфликте при создании платежа.
        """
        params = {"getObject": True}
        payload = {
            "paymentItems": [
                {
                    "itemType": payment.item_type,
                    "amount": {"amount": payment.amount, "currencyCode": payment.currency_code},
                    "accountId": f"{payment.account_id}",
                }
            ],
            "documentNumber": payment.document_number,
            "amount": {"amount": payment.amount, "currencyCode": payment.currency_code},
            "paymentPointId": payment.point_id,
            "paymentType": "REGULAR",
            "paymentMethod": {"paymentMethodType": payment.payment_method_type},
        }
        conflicts = self.post(
            url=f"{BASE_URL_API}/openapi/v2/payments-gateway/payments/accept/check", params=params, data=payload
        )
        self.check_response_status(conflicts, 200, "Не удалось проверить возможность создания нового платежа")
        return conflicts

    @allure.step("Ожидание возможности создания платежа")
    def wait_check_create_payment(self, payment_data: PaymentInfo) -> None:
        wait_that(
            lambda: len(self.check_create_payment(payment_data).json()["conflicts"]) == 0,
            timeout=10,
            sleep_seconds=0.5,
            exception=CreatePaymentException,
            message="При создании платежа возникла ошибка. Смотри ответ API в логах.",
        )

    @allure.step("API: Создание нового платежа")
    def create_payment(self, payment: PaymentInfo) -> APIResponse:
        """
        Метод создает новый платеж.

        Parameters:
        payment (PaymentInfo): параметры платежа

        Returns:
        APIResponse: объект ответа API с данными созданного платежа.
        """
        params = {"getObject": True}
        payload = {
            "paymentItems": [
                {
                    "itemType": payment.item_type,
                    "amount": {"amount": payment.amount, "currencyCode": payment.currency_code},
                }
            ],
            "documentNumber": payment.document_number,
            "amount": {"amount": payment.amount, "currencyCode": payment.currency_code},
            "paymentPointId": payment.point_id,
            "paymentType": "REGULAR",
            "paymentMethod": {"paymentMethodType": payment.payment_method_type},
        }

        match payment.item_type:
            case "CUSTOMER_ACCOUNT":
                payload["paymentItems"][0]["accountId"] = f"{payment.account_id}"
            case "PHONE_NUMBER":
                payload["paymentItems"][0]["phoneNumber"] = payment.phone_number

        response = self.post(
            url=f"{BASE_URL_API}/openapi/v2/payments-gateway/payments/accept", params=params, data=payload
        )
        self.check_response_status(response, 200, "Не удалось провести платеж")
        return response

    @allure.step("API: Получить платежи клиента")
    def get_payments(self, customer_id: int, sort_by: str | None = None) -> APIResponse:
        params = {"limit": 10, "sort": sort_by, "offset": 0}
        payments = self.post(
            url=f"{BASE_URL_API}/bss-box/v2/payments-gateway/private/customers/{customer_id}/payments/search",
            params=params,
            data={},
        )
        self.check_response_status(payments, 200, "Не удалось получить список платежей")
        return payments

    @allure.step("Ожидание появления платежа на сумму {payment_amount}")
    def wait_last_payment_amount(self, account_id: int, payment_amount: int) -> None:
        wait_that(
            lambda: self.get_payments(account_id, "-paymentDate").json()["items"][0]["amount"]["amount"]
            == payment_amount,
            timeout=25,
            sleep_seconds=0.5,
            exception=CreatePaymentException,
            message="Платеж не появился в указанное время",
        )

    @allure.step("Ожидание статуса SUCCEEDED для последнего платежа")
    def wait_last_payment_successful(self, account_id: int) -> None:
        wait_that(
            lambda: self.get_payments(account_id, "-paymentDate").json()["items"][0]["status"]["code"] == "SUCCEEDED",
            timeout=25,
            sleep_seconds=0.5,
            exception=UpdateStatusException,
            message="Статус не обновился в указанное время",
        )

    @allure.step("Проведение платежа")
    def create_default_payment(self, account_id: int, payment_amount: float) -> str:
        payment_data = PaymentInfo(
            amount=payment_amount,
            account_id=account_id,
        )
        self.wait_check_create_payment(payment_data)
        response = self.create_payment(payment_data)
        self.wait_last_payment_successful(account_id)
        return response.json()["documentNumber"]

    @allure.step("Получение информации о доступных действиях с платежом")
    def get_allowed_actions_status(self, billing_payment_id: int, allowed_actions: str) -> list:
        params = {"actions": allowed_actions}
        statuses = self.get(
            url=f"{BASE_URL_API}/bss-box/v2/payments-gateway/payments/{billing_payment_id}/allowedActions",
            params=params,
        )
        self.check_response_status(statuses, 200, "Не удалось получить информацию о доступных действиях над платежом")
        return statuses.json()["items"]

    @allure.step("Ожидание возможности добавить корректировку для платежа")
    def wait_check_add_adjustment_for_payment(self, billing_payment_id: int) -> None:
        wait_that(
            lambda: self.get_allowed_actions_status(billing_payment_id, "ADJUSTMENT_ADD")[0]["access"] == "ALLOWED",
            timeout=40,
            sleep_seconds=0.5,
            exception=CreateAdjustmentException,
            message="За указанное время не появилась возможность добавить корректировку платежа",
        )


@dataclass
class PaymentUniblpInfo:
    """
    Класс данных платежа для платежа от UNIBLP, account_number и bic имеются по умолчанию на стенде
    """

    item_type: str = "CUSTOMER_ACCOUNT"
    amount: float = 0
    currency_code: str = "RUB"
    account_id: int = 0
    document_number: int = generate_random_number(4)
    point_id: int = 2
    payment_date: str = get_current_datetime_string_for_api()
    payment_method_type: str = "BANK_ACCOUNT_TRANSFER"
    account_number: str = "40702810538050107202"
    bic: str = "044585272"


class PaymentsUniblpRequests(BaseRequests):
    def __init__(self, api_request_auth_context: APIRequestContext):
        super().__init__(api_request_auth_context)

    @allure.step("API: Проверка возможности создать новый платеж")
    def check_create_payment(self, payment: PaymentUniblpInfo, payment_date: None | str = None) -> APIResponse:
        """
        Метод проверяет, возникнут ли конфликты при создании нового платежа UNIBLP.

        Parameters:
        payment (PaymentUniblpInfo): параметры платежа

        Returns:
        APIResponse: объект ответа API с данными о конфликте при создании платежа.
        """
        username = UniblpUserData.login
        password = UniblpUserData.password

        auth = f"{username}:{password}"
        base64_auth = convert_string_to_base64(auth)

        headers = {"Authorization": f"Basic {base64_auth}", "Content-Type": "application/json"}
        params = {"getObject": True}
        payload = {
            "paymentItems": [
                {
                    "itemType": payment.item_type,
                    "amount": {"amount": payment.amount, "currencyCode": payment.currency_code},
                    "accountId": f"{payment.account_id}",
                }
            ],
            "documentNumber": payment.document_number,
            "amount": {"amount": payment.amount, "currencyCode": payment.currency_code},
            "paymentPointId": payment.point_id,
            "paymentType": "REGULAR",
            "paymentMethod": {
                "paymentMethodType": payment.payment_method_type,
                "accountNumber": payment.account_number,
                "BIC": payment.bic,
            },
        }
        if payment_date:
            payload["paymentDate"] = f"{payment.payment_date}"
        conflicts = self.post(
            url=f"{BASE_URL_API}/openapi/v2/payments-gateway/payments/accept/check",
            params=params,
            data=payload,
            headers=headers,
        )
        self.check_response_status(conflicts, 200, "Не удалось проверить возможность создания нового платежа")
        return conflicts

    @allure.step("API: Создание нового платежа UNIBLP")
    def create_payment(self, payment: PaymentUniblpInfo, payment_date: None | str = None) -> APIResponse:
        """
        Метод создает новый платеж UNIBLP.

        Parameters:
        payment (PaymentUniblpInfo): параметры платежа

        Returns:
        APIResponse: объект ответа API с данными созданного платежа.
        """
        username = UniblpUserData.login
        password = UniblpUserData.password

        auth = f"{username}:{password}"
        base64_auth = convert_string_to_base64(auth)

        headers = {"Authorization": f"Basic {base64_auth}", "Content-Type": "application/json"}
        params = {"getObject": True}
        payload = {
            "paymentItems": [
                {
                    "itemType": payment.item_type,
                    "amount": {"amount": payment.amount, "currencyCode": payment.currency_code},
                    "accountId": f"{payment.account_id}",
                }
            ],
            "documentNumber": payment.document_number,
            "amount": {"amount": payment.amount, "currencyCode": payment.currency_code},
            "paymentPointId": payment.point_id,
            "paymentDate": f"{payment.payment_date}",
            "paymentType": "REGULAR",
            "paymentMethod": {
                "paymentMethodType": payment.payment_method_type,
                "accountNumber": payment.account_number,
                "BIC": payment.bic,
            },
        }
        if payment_date:
            payload["paymentDate"] = f"{payment.payment_date}"
        response = self.post(
            url=f"{BASE_URL_API}/openapi/v2/payments-gateway/payments/accept",
            headers=headers,
            params=params,
            data=payload,
        )
        self.check_response_status(response, 200, "Не удалось провести платеж")
        return response

    @allure.step("Ожидание возможности создания платежа UNIBLP")
    def wait_check_create_payment(self, payment_data: PaymentUniblpInfo, payment_date: None | str = None) -> None:
        wait_that(
            lambda: len(self.check_create_payment(payment_data, payment_date).json()["conflicts"]) == 0,
            timeout=10,
            sleep_seconds=0.5,
            exception=CreatePaymentException,
            message="При создании платежа возникнет ошибка",
        )
