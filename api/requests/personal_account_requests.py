from dataclasses import dataclass

from playwright.sync_api import APIRequestContext

from common.helpers.data_generator import get_current_datetime_string_for_api
from common.helpers.env_helper import BASE_URL_API


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


class PersonalAccountRequests:
    def __init__(self, api_request_auth_context: APIRequestContext):
        self.api_request_auth_context = api_request_auth_context

    def generate_sequence_id(self, seq_name: str) -> int:
        """
        Метод предоставляет очередное значение из заданной последовательности

        Parameters:
        seq_name (str): наименование последовательности (например, resource_instance или product_instance)

        Returns:
        int: значение заданной последовательности
        """
        params = {"seqName": seq_name}
        request = self.api_request_auth_context.get(url=f"{BASE_URL_API}/ps/v1/tailored-rm/generateSequenceId",
                                                    params=params)
        assert request.status == 200, f"Не выполнен запрос на генерацию id, ошибка: {request.status} {request.text()}"
        return request.json()['id']

    def generate_unique_id(self, type_name: str) -> int:
        """
        Метод возвращает уникальный Id для сущности

        Parameters:
        type_name (str): тип сущности, для которой генерируется id

        Returns:
        int: сгенерированный id
        """
        entity_type = {
            "account_number": "accountNumber"
        }
        payload = {"type": f"{type_name}"}
        request = self.api_request_auth_context.post(url=f"{BASE_URL_API}/ps/v1/tailored-rm/generateUniqueId",
                                                     data=payload)
        assert request.status == 200, (f"Не выполнен запрос на генерацию id, " 
                                       f"ошибка: {request.status} {request.json()['status']['message']}")
        return request.json()['conclusions'][0][entity_type[type_name]]

    def create_agreement(self, user_id: int, date: str) -> (int, int):
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
        agreement_number = self.generate_sequence_id("agreement_number")
        payload = {"agreementNumber": f"{agreement_number}", "agreementType": {},
                   "category": {"agreementCategoryId": 1},
                   "isPermanent": True, "partnerType": [],
                   "paymentMethod": {"bank": {}, "type": "BANK_ACCOUNT_TRANSFER"},
                   "paymentReceiptMethod": {"bankDetails": {"bankDetailsId": 1}, "type": "EXTERNAL_BANK_DETAILS"},
                   "signingDate": date, "signingUser": {"firstName": "Иван", "surname": "Иванов"},
                   "status": {"agreementStatusId": 2}}
        request = self.api_request_auth_context.post(
            url=f"{BASE_URL_API}/openapi/v1/customerManagement/customers/{user_id}/agreements",
            headers=headers, data=payload)
        assert request.status == 200, (f"Не выполнен запрос на добавлению нового договора для клиента {user_id}, "
                                       f"ошибка: {request.status} {request.json()['userMessage']}")
        return request.json()['agreementId'], agreement_number

    def create_personal_account(self, account_data: PersonalAccountData) -> (int, int):
        """
        Метод создает новый лицевой счет на договоре

        Parameters:
        account_data (PersonalAccountData): данные для создания Лицевого счета

        Returns:
        int: id лицевого счета
        int: номер лицевого счета
        """
        headers = {"Content-Type": "application/json"}
        account_number = self.generate_unique_id("account_number")
        payload = {
            "accountNumber": f"{account_number}",
            "additionalAttributes": [
                {
                    "code": "raitingType",
                    "value": account_data.raiting_type,
                    "valueType": "NUMBER"
                },
                {
                    "code": "isCashPaymentEnabled",
                    "value": account_data.is_cash_payment_enabled,
                    "valueType": "BOOLEAN"
                },
                {
                    "code": "priorityAccountForPayment",
                    "value": False,
                    "valueType": "BOOLEAN"
                }
            ],
            "currency": {
                "currencyId": account_data.currency_id
            },
            "thresholds": {
                "thresholdBreak": account_data.threshold_break,
                "thresholdControl": account_data.threshold_control
            },
            "type": {
                "accountTypeId": account_data.account_type_id
            }
        }
        request = self.api_request_auth_context.post(
            url=f"{BASE_URL_API}/openapi/v1/customerManagement/agreements/{account_data.agreement_id}/accounts",
            headers=headers, data=payload)
        assert request.status == 200, (f"Не выполнен запрос на добавлению нового лицевого счета для договора "
                                       f"{account_data.agreement_id}, "
                                       f"ошибка: {request.status} {request.json()['userMessage']}")
        account_id = request.json()['accountId']

        date = get_current_datetime_string_for_api()
        payload = {
            "entityTypeCode": "account",
            "entityId": f"{account_id}",
            "startDate": date,
            "endDate": "2300-01-01T00:00:00",
            "values": [
                {
                    "attributeCode": "ratingType",
                    "valueType": "VARCHAR",
                    "value": f"{account_data.raiting_type}"
                },
                {
                    "attributeCode": "isCashPaymentEnabled",
                    "valueType": "BOOLEAN",
                    "value": account_data.is_cash_payment_enabled
                },
                {
                    "attributeCode": "thresholdBreak",
                    "valueType": "INTEGER",
                    "value": account_data.threshold_break
                },
                {
                    "attributeCode": "thresholdControl",
                    "valueType": "BOOLEAN",
                    "value": account_data.threshold_control
                }
            ]
        }
        add_values = self.api_request_auth_context.post(
            url=f"{BASE_URL_API}/openapi/v1/attribute-service/entityTypes/entities/values/add",
            headers=headers, data=payload)
        assert add_values.status == 200, (f"Не выполнен запрос на добавление значений дополнительных атрибутов "
                                          f"для лицевого счета {account_id}, "
                                          f"ошибка: {add_values.status} {add_values.json()['userMessage']}")
        return account_id, account_number
