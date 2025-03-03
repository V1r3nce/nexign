from dataclasses import dataclass

import allure
from playwright.sync_api import APIRequestContext, APIResponse

from common.helpers.data_generator import generate_random_number, get_current_datetime_string_for_api
from common.helpers.env_helper import BASE_URL_API


@dataclass
class PaymentInfo:
    """
    Класс данных платежа

    item_type (str): тип цели платежа (CUSTOMER_ACCOUNT, PARTNER_ACCOUNT, AGREEMENT, PHONE_NUMBER, ICCID)
    amount (float): сумма платежа
    currency_code (str): код валюты (USD, EUR, и т.д.)
    account_id (int): id цели платежа
    currency_id (int): id валюты (1 - RUB, 2 - USD и т. д.)
    point_id (int): идентификатор кассы (1 - voucher, 2 - uniblp, 3 - PNXL1, 4 - PNXL2, 5 - PNXUSD1, 6 - PNXUSD2)
    payment_date (str): дата когда произведён платеж
    payment_method_type (str): тип метода оплаты (CASH, BANK_CARD, PAYPAL, BANK_ACCOUNT_TRANSFER)
    """
    item_type: str = "CUSTOMER_ACCOUNT"
    amount: float = 0
    currency_code: str = "RUB"
    account_id: int = 0
    document_number: int = generate_random_number(4)
    point_id: int = 3
    payment_date: str = get_current_datetime_string_for_api()
    payment_method_type: str = "CASH"


class PaymentsRequests:
    def __init__(self, api_request_auth_context: APIRequestContext):
        self.api_request_auth_context = api_request_auth_context

    @allure.step("Создание нового платежа")
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
                    "amount": {
                        "amount": payment.amount,
                        "currencyCode": payment.currency_code
                    },
                    "accountId": f"{payment.account_id}"
                }
            ],
            "documentNumber": payment.document_number,
            "amount": {
                "amount": payment.amount,
                "currencyCode": payment.currency_code
            },
            "paymentPointId": payment.point_id,
            "paymentDate": f"{payment.payment_date}",
            "paymentType": "REGULAR",
            "paymentMethod": {
                "paymentMethodType": payment.payment_method_type
            }
        }
        payment = self.api_request_auth_context.post(url=f"{BASE_URL_API}/openapi/v2/payments-gateway/payments/accept",
                                                     params=params, data=payload)
        assert payment.status == 200, f"Не удалось провести платеж, ошибка: {payment.status} {payment.json()['userMessage']}"
        return payment
