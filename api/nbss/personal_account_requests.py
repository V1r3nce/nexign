from dataclasses import dataclass
from datetime import datetime

import allure
from playwright.sync_api import APIRequestContext, APIResponse

from api.base_requests import BaseRequests
from api.exceptions import (
    BalanceException,
    CreateEntityException,
    GetAccrualsException,
    GetLinkedInquiryException,
    UpdateStatusException,
    WaitSubscriptionCallsException,
)
from common.helpers.checker import wait_that
from common.helpers.data_generator import get_current_datetime_string_for_api
from common.helpers.env_helper import BASE_URL_API
from models.context import test_context
from models.user import EntrepreneurClient, IndividualClient, OrganizationClient


@dataclass
class PersonalAccountData:
    """
    Класс для данных для создания лицевого счета клиента

    agreement_id (int): id договора, для которого создается ЛС
    account_type_id (int): Тип ЛС (1 - Биллинговый, 2 - Доходный, 3 - Персональный)
    raiting_type (int): Способ оплаты (1 - Предоплатный, 2 - Постоплатный)
    is_cash_payment_enabled (bool): Запрет приема наличных платежей
    currency_id (int): id валюты (1 - RUB, 2 - USD и т. д.)
    threshold_break (int): Кредит - Порог отключения
    threshold_control (bool): Кредит - Контроль порога
    """

    agreement_id: int
    account_type_id: int = 1
    raiting_type: int = 1
    is_cash_payment_enabled: bool = True
    currency_id: int = 1
    threshold_break: int = 0
    threshold_control: bool = False


@dataclass
class ClientAccountData:
    """Класс для данных связки Клиент - Аккаунт"""

    customer_id: int
    customer_name: str
    account_id: int
    account_number: str


@dataclass
class ProductData:
    """Класс для данных Продукт"""

    customer_id: int
    product_name: str
    product_amount: int
    product_status: str


class PersonalAccountRequests(BaseRequests):
    def __init__(self, api_request_auth_context: APIRequestContext):
        super().__init__(api_request_auth_context)

    def generate_unique_id(self, body: dict) -> APIResponse:
        """
        Метод посылает запрос на генерацию уникального номера.

        Parameters:
        body: тело с которым посылается запрос
        Returns:
        APIResponse ответ на запрос
        """
        request = self.post(url=f"{BASE_URL_API}/ps/v1/tailored-rm/generateUniqueId", data=body)
        self.check_response_status(request, 200, "Не выполнен запрос на генерацию id")
        return request

    def generate_agreement_number(self, client: IndividualClient | OrganizationClient | EntrepreneurClient) -> str:
        """
        Метод генерирует уникальный номер договора для клиента

        :param client: клиент для которого создается договор
        :return: строка с уникальным номером договора клиента
        """
        operation_year = datetime.now().year
        payload = {
            "type": "agreement_number",
            "customerIdForAgreement": str(client.user_id),
            "operationYear": str(operation_year),
        }
        return self.generate_unique_id(payload).json()["conclusions"][-1]["agreement_number"]

    def generate_account_number(self, client_id: int, client_agreement_id: int) -> int:
        """
         Метод генерирует уникальный номер лицевого счета для клиента

        :param client_id: Идентификатор клиента которому создается номер лицевого счета.
        :param client_agreement_id: Идентификатор договора клиента которому создается номер лицевого счета
        :return: строка с уникальным номером лицевого счета клиента
        """
        payload = {"type": "account_number", "customerId": client_id, "agreementId": client_agreement_id}
        return self.generate_unique_id(payload).json()["conclusions"][-1]["accountNumber"]

    @allure.step("API: Добавление договора для клиента")
    def create_agreement(self, client: IndividualClient | OrganizationClient | EntrepreneurClient) -> tuple[int, str]:
        """
        Метод создает новый договор на клиенте

        Parameters:
        user_id (int): id клиента, для которого создается договор
        date (str): дата подписания договора

        Returns:
        int: id договора
        int: номер договора
        """
        headers = {"Content-Type": "application/json"}
        agreement_number = self.generate_agreement_number(client)
        payload = {
            "agreementNumber": f"{agreement_number}",
            "agreementType": {},
            "category": {"agreementCategoryId": 1},
            "isPermanent": True,
            "partnerType": [],
            "paymentMethod": {
                "bank": {"bankId": client.bank_id},
                "bankAccountNumber": client.bank_account,
                "type": "BANK_ACCOUNT_TRANSFER",
            },
            "paymentReceiptMethod": {"bankDetails": {"bankDetailsId": 1}, "type": "EXTERNAL_BANK_DETAILS"},
            "signingDate": client.date_for_api,
            "signingUser": {
                "firstName": "Иван",
                "patronymic": "Иванович",
                "proxyNumber": "12345",
                "proxyStartDate": "2024-09-10",
                "surname": "Иванов",
            },
            "status": {"agreementStatusId": 2},
        }
        request = self.post(
            url=f"{BASE_URL_API}/openapi/v1/customerManagement/customers/{test_context.client.user_id}/agreements",
            headers=headers,
            data=payload,
        )
        self.check_response_status(
            request, 200, f"Не выполнен запрос на добавлению нового договора для клиента {test_context.client.user_id}"
        )

        agreement_id = request.json()["agreementId"]
        self.wait_create_entity("AGREEMENT", agreement_id)
        return agreement_id, agreement_number

    @allure.step("API: Ожидание выполнения создания переданной сущности")
    def wait_create_entity(self, entity_type_code: str, entity_id: int) -> None:
        payload = {"entityTypeCode": entity_type_code, "extEntityId": entity_id}
        wait_that(
            lambda: self.post(url=f"{BASE_URL_API}/openapi/v1/lifeCycleManagement/entities", data=payload).status == 200,
            timeout=15,
            sleep_seconds=0.5,
            exception=CreateEntityException,
            message=f"Не выполнилось создание сущности {entity_type_code}: {entity_id} за указанное время",
        )

    @allure.step("API: Добавление лицевого счета")
    def create_personal_account(self, account_data: PersonalAccountData, client_id: int) -> tuple[int, int]:
        """
        Метод создает новый лицевой счет на договоре

        Parameters:
        account_data (PersonalAccountData): данные для создания Лицевого счета

        Returns:
        int: id лицевого счета
        int: номер лицевого счета
        """
        headers = {"Content-Type": "application/json"}
        account_number = self.generate_account_number(client_id, account_data.agreement_id)
        payload = {
            "accountNumber": f"{account_number}",
            "additionalAttributes": [
                {"code": "raitingType", "value": account_data.raiting_type, "valueType": "NUMBER"},
                {"code": "isCashPaymentEnabled", "value": account_data.is_cash_payment_enabled, "valueType": "BOOLEAN"},
                {"code": "priorityAccountForPayment", "value": False, "valueType": "BOOLEAN"},
            ],
            "currency": {"currencyId": account_data.currency_id},
            "thresholds": {
                "thresholdBreak": account_data.threshold_break,
                "thresholdControl": account_data.threshold_control,
            },
            "type": {"accountTypeId": account_data.account_type_id},
        }
        request = self.post(
            url=f"{BASE_URL_API}/openapi/v1/customerManagement/agreements/{account_data.agreement_id}/accounts",
            headers=headers,
            data=payload,
        )
        self.check_response_status(
            request,
            200,
            f"Не выполнен запрос на добавлению нового лицевого счета для договора {account_data.agreement_id}",
        )
        account_id = request.json()["accountId"]

        date = get_current_datetime_string_for_api()
        payload = {
            "entityTypeCode": "account",
            "entityId": f"{account_id}",
            "startDate": date,
            "endDate": "2300-01-01T00:00:00",
            "values": [
                {"attributeCode": "ratingType", "valueType": "VARCHAR", "value": f"{account_data.raiting_type}"},
                {
                    "attributeCode": "isCashPaymentEnabled",
                    "valueType": "BOOLEAN",
                    "value": account_data.is_cash_payment_enabled,
                },
                {"attributeCode": "thresholdBreak", "valueType": "INTEGER", "value": account_data.threshold_break},
                {"attributeCode": "thresholdControl", "valueType": "BOOLEAN", "value": account_data.threshold_control},
            ],
        }
        add_values = self.post(
            url=f"{BASE_URL_API}/openapi/v1/attribute-service/entityTypes/entities/values/add",
            headers=headers,
            data=payload,
        )
        self.check_response_status(
            add_values,
            200,
            f"Не выполнен запрос на добавление значений дополнительных атрибутов для лицевого счета {account_id}",
        )
        return account_id, account_number

    def get_personal_accounts(self, entity_code: str, entity_id: int) -> APIResponse:
        """
        Метод получает список лицевых счетов

        Parameters:
        entity_code (str): код объекта, для которого возвращаются лицевые счета (customer, subdivision, agreement)
        entity_id (int): id объекта

        Returns:
        APIResponse: объект ответа API со списком лицевых счетов.
        """
        payload = {"entity": {"code": entity_code, "id": entity_id}}
        search = self.post(url=f"{BASE_URL_API}/openapi/v1/customerManagement/accounts/search", data=payload)
        self.check_response_status(
            search, 200, f"Не выполнен запрос на поиск лицевых счетов для {entity_code} {entity_id}"
        )
        return search

    def get_client_with_currency_type(self, client_search_response: APIResponse, currency: str) -> ClientAccountData:
        """Найти клиента с валютой счета {currency}"""
        client_ids = [(item["customerId"], item["customerName"]) for item in client_search_response.json()["items"]]
        for item in client_ids:
            personal_account = self.get_personal_accounts("customer", item[0])
            if personal_account.json()["items"][0]["currency"]["name"] == currency:
                account_id, account_number = (
                    personal_account.json()["items"][0]["accountId"],
                    personal_account.json()["items"][0]["accountNumber"],
                )
                client_data = ClientAccountData(item[0], item[1], account_id, account_number)
                return client_data
        raise AssertionError(f"Отсутствует ЛС с валютой {currency}")

    def get_account_balances(self, account_id: int) -> APIResponse:
        """Метод получает доступные балансы ЛС клиента"""
        params = {"customerDatabaseId": 999, "mode": "ALL"}
        balances = self.get(url=f"{BASE_URL_API}/openapi/v1/customers/{account_id}/balances", params=params)
        self.check_response_status(balances, 200, "Не удалось получить балансы ЛС")
        return balances

    def get_current_main_balance(self, account_id: int) -> float | None:
        """Метод получает текущий баланс кошелька 'Основной баланс лицевого счета', идентификатор кошелька - wallet_id"""
        wallet_id = 5
        wallets = self.get_account_balances(account_id).json()["aggregatesByWallet"]
        for wallet in wallets:
            if wallet["walletId"] == str(wallet_id):
                return wallet["currentBalance"]
        return None

    @allure.step("Ожидание что основной баланс ЛС {account_id} станет равен {desired_balance}")
    def wait_check_current_main_balance(self, account_id: int, desired_balance: float) -> None:
        wait_that(
            lambda: self.get_current_main_balance(account_id) == desired_balance,
            timeout=60,
            sleep_seconds=0.5,
            exception=BalanceException,
            message=f"Баланс ЛС {account_id} не стал равен {desired_balance} за указанное время.",
        )

    def get_client_subscriptions(self, user_id: int) -> APIResponse:
        """Метод получает список абонентов клиента"""
        payload = {"subscriptionInfoBaseFilter": {"customerId": user_id}}
        subscriptions = self.post(
            url=f"{BASE_URL_API}/openapi/v1/subscriptionManagement/subscriptions/search", data=payload
        )
        self.check_response_status(subscriptions, 200, "Не удалось получить список абонентов клиента")
        return subscriptions

    def get_subscription_accruals(
        self, subscription_id: int, get_billing_info: bool = False, customer_ids: list[int] = None
    ) -> APIResponse:
        """Метод получает список начислений абонента"""
        params = {"limit": 10, "sort": "-chargeDate", "offset": 0}
        payload = {
            "getBillingInfo": get_billing_info,
        }
        if customer_ids:
            payload["customerIds"] = customer_ids

        accruals = self.post(
            url=f"{BASE_URL_API}/ps/v2/gus/subscribers/{subscription_id}/charges/search", params=params, data=payload
        )
        self.check_response_status(accruals, 200, "Не удалось получить список начислений абонента")
        return accruals

    @allure.step("Ожидание появления начислений у абонента {subscription_id}")
    def wait_accruals(self, user_id: int | None = None, subscription_id: int | None = None) -> None:
        """
        используется subscription_id, если он не задан, используется первый абонент клиента с идентификатором user_id
        """
        if subscription_id is None:
            subscription_id = self.get_client_subscriptions(user_id).json()["items"][0]["subscriptionId"]
        wait_that(
            lambda: len(self.get_subscription_accruals(subscription_id).json()["items"]) > 0,
            timeout=40,
            sleep_seconds=0.5,
            exception=GetAccrualsException,
            message="У абонента не появились начисления за указанное время",
        )

    @allure.step("Ожидание связки последнего начисления абонента {subscription_id} с заявкой {inquiry_id}")
    def wait_link_last_accrual_with_inquiry(self, subscription_id: int, inquiry_id: int) -> None:
        wait_that(
            lambda: self.get_subscription_accruals(subscription_id).json()["items"][0]["inquiryId"] == inquiry_id,
            timeout=40,
            sleep_seconds=0.5,
            exception=GetLinkedInquiryException,
            message="Заявка не связалась с начислением за указанное время",
        )

    def get_product_data_by_subscriptions_id(self, subscription_id: int) -> APIResponse:
        """Метод получает продукт по subscriptionId"""
        payload = {
            "classificationCode": "all",
            "params": {"limit": 100, "offset": 0},
            "subscriptionId": subscription_id,
            "productStatusCodes": ["ACTIVE", "BLOCKED", "INACTIVE"],
        }
        products = self.post(
            url=f"{BASE_URL_API}/openapi/v1/productManagement/products/searchBySubscription", data=payload
        )
        self.check_response_status(products, 200, "Не удалось получить данные о продукте")
        return products

    def get_client_product_with_status(self, client_search_response: APIResponse, status: str) -> ProductData:
        """Найти клиента с определенным статусом продукта, INACTIVE - не активный, ACTIVE - активный"""
        client_ids = [item["customerId"] for item in client_search_response.json()["items"]]
        for item in client_ids:
            subscriptions = self.get_client_subscriptions(item)
            subscription_id = subscriptions.json()["items"][0]["subscriptionId"]
            products = self.get_product_data_by_subscriptions_id(subscription_id)
            if len(products.json()["items"]) > 0:
                product_item = products.json()["items"][0]
                if product_item["status"]["code"] == status:
                    product_data = ProductData(
                        item, product_item["name"], product_item["totalPrice"]["amount"], product_item["status"]["name"]
                    )
                    return product_data
        raise AssertionError(f"Отсутствует клиент с {status} продуктом")

    @allure.step("Создание договора и ЛС для клиента")
    def create_agreement_and_account(
        self, client: IndividualClient | OrganizationClient | EntrepreneurClient
    ) -> IndividualClient | OrganizationClient | EntrepreneurClient:
        """
        Метод создает договор и лицевой счет для клиента
        :param client: объект с информацией о клиенте (ФЛ, ЮЛ, ИП)

        :return: IndividualClient | OrganizationClient | EntrepreneurClient: объект с информацией о клиенте (ФЛ, ЮЛ, ИП)
        """
        agreement_id, agreement_number = self.create_agreement(client)
        account_id, account_number = self.create_personal_account(
            PersonalAccountData(agreement_id=agreement_id, is_cash_payment_enabled=False), client.user_id
        )
        wait_that(
            lambda: account_id
            in [i["accountId"] for i in self.get_personal_accounts("customer", client.user_id).json()["items"]],
            exception=UpdateStatusException,
            timeout=10,
            sleep_seconds=0.5,
            message="Аккаунт не создался в указанное время",
        )
        client.add_agreement(agreement_id, agreement_number)
        client.get_agreement(agreement_id).add_account(account_id, account_number)
        return client

    @allure.step("API: Получение трафика для абонента {subscription_id}")
    def get_subscription_calls(self, account_id: int, subscription_id: int) -> list:
        """
        Метод получает записи о трафике по абоненту subscriptionId

        :param account_id: идентификатор лицевого счета
        :param subscription_id: идентификатор абонента
        :return: список объектов с информацией о трафике абонента
        """
        params = {"limit": 10, "sort": "-eventDate", "offset": 0}
        payload = {
            "customerIds": [account_id],
            "balancePeriod": {},
            "eventPeriod": {},
            "getBillingInfo": True,
            "rollbackPeriod": {},
        }
        calls = self.post(
            url=f"{BASE_URL_API}/ps/v2/gus/subscribers/{subscription_id}/calls/search", params=params, data=payload
        )
        self.check_response_status(calls, 200, "Не удалось получить данные о продукте")
        return calls.json()["items"]

    @allure.step("Ожидание, что у абонента {subscription_id} будет {call_count} записей о трафике")
    def wait_subscription_calls(self, account_id: int, subscription_id: int, call_count: int = 1) -> None:
        wait_that(
            lambda: len(self.get_subscription_calls(account_id, subscription_id)) == call_count,
            timeout=30,
            sleep_seconds=0.5,
            exception=WaitSubscriptionCallsException,
            message="Трафик не появился у абонента за указанное время",
        )
