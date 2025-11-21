from dataclasses import dataclass, field
from typing import Any, Literal

import allure
from playwright.sync_api import APIRequestContext, APIResponse

from api.base_requests import BaseRequests
from api.exceptions import (
    ClientNotFoundException,
    LinkedPersonException,
    LinkedPersonFunctionException,
    LinkedPersonPullAddressException,
    UpdateStatusException,
)
from api.nbss.address_requests import AddressRequests
from api.nbss.finances.payments_requests import PaymentInfo, PaymentsRequests
from api.nbss.personal_account_requests import PersonalAccountData, PersonalAccountRequests
from common.helpers.checker import wait_that
from common.helpers.env_helper import BASE_URL_API
from common.helpers.time_helpers import delay
from models.address_info import BasicSystemAddress
from models.context import test_context
from models.product import ProductInfo
from models.user import EntrepreneurClient, IndividualClient, OrganizationClient


@dataclass
class InfoAboutBundle:
    bundle_name: str = ""
    products: list[ProductInfo] = field(default_factory=list)
    one_time_payment: float = 0.0
    subscription_fee: float = 0.0

    def add_product(self, product: ProductInfo) -> None:
        self.products.append(product)
        self.one_time_payment += product.one_time_payment
        self.subscription_fee += product.subscription_fee


@dataclass
class ClientDataFromResponseGetClientData:
    """Класс данных по клиенту для парсинга ответа API запроса get_client_data
    organization: ЮЛ
    individual: ФЛ"""

    client_data: dict
    client_type: str = "organization"

    def __post_init__(self) -> None:
        self.customer_id = self.client_data["customerId"]
        self.full_name = self.client_data["party"]["nameInfo"]["name"]
        self.nationality = self.client_data["party"]["nationality"]["name"]
        self.tax_number = self.client_data["party"]["taxRegistrationCertificate"]["taxIdentificationNumber"]
        self.isResident = "Да" if self.client_data["party"]["isResident"] else "Нет"
        if self.client_type == "individual":
            self.birth_date = self.client_data["party"]["birthDate"]
            self.gender = self.client_data["party"]["gender"]["name"]
            self.document_series = self.client_data["party"]["identificationDocument"]["series"]
            self.document_num = self.client_data["party"]["identificationDocument"]["number"]
            self.document_type = self.client_data["party"]["identificationDocument"]["type"]["name"]


class ClientRequests(BaseRequests):
    def __init__(self, api_request_auth_context: APIRequestContext):
        super().__init__(api_request_auth_context)
        self.personal_account_api = PersonalAccountRequests(api_request_auth_context)
        self.payment_api = PaymentsRequests(api_request_auth_context)

    @allure.step("API: Создание нового клиента ФЛ")
    def create_individual_client(self, client_data: IndividualClient) -> IndividualClient:
        """
        Метод создает клиента типа Физическое лицо

        :param client_data: инстанс класса IndividualClient
        :return: инстанс класса IndividualClient с заполненным user_id
        """
        api_addresses = AddressRequests(self.api_request_auth_context)
        payload = {
            "businessActivity": {},
            "party": {
                "INILA": client_data.snils,
                "biometricData": False,
                "birthDate": client_data.birth_date_for_api,
                "birthPlace": client_data.birth_place,
                "gender": {"genderId": client_data.gender_id},
                "identificationDocument": {
                    "dateOfIssue": client_data.issue_date_for_api,
                    "providedByOrganization": client_data.document_provide_by,
                    "divisionCode": client_data.document_division_code,
                    "number": client_data.document_num,
                    "series": client_data.document_serial,
                    "type": {"identificationTypeId": client_data.document_type_id},
                    "validFor": client_data.document_valid_date_for_api,
                },
                "isResident": client_data.is_resident_bool,
                "nameInfo": {
                    "firstName": client_data.first_name,
                    "patronymic": client_data.patronymic,
                    "surname": client_data.sur_name,
                },
                "nationality": {"nationalityId": client_data.nationality_id},
                "publicOfficial": client_data.is_public_bool,
                "speakingLanguage": {"languageId": client_data.speaking_language_id},
                "taxRegistrationCertificate": {"taxIdentificationNumber": client_data.inn},
            },
            "type": "INDIVIDUAL",
        }
        request = self.post(url=f"{BASE_URL_API}/openapi/v1/customerManagement/customers", data=payload)
        self.check_response_status(request, 200, "Не выполнен запрос на создание нового клиента ФЛ")

        client_data.user_id = request.json()["customerId"]
        self.set_additional_attribute(
            "customer_individual",
            client_data.user_id,
            [
                {
                    "attributeCode": "taxSchemeId",
                    "value": client_data.tax_scheme_id,
                    "valueType": client_data.tax_scheme_type,
                }
            ],
        )
        api_addresses.add_base_address_to_client(client_data.registration_address, client_data.user_id)

        wait_that(
            lambda: self.get_client_data(client_data.user_id).status == 200,
            timeout=5,
            sleep_seconds=0.5,
            exception=ClientNotFoundException,
            message="Пользователь не был создан в установленное время",
        )
        delay(1, reason="UI не успевает за API")
        test_context.client_list.append(client_data)
        test_context.client = client_data
        return client_data

    @allure.step("API: Создание нового клиента ЮЛ")
    def create_organization(self, client_data: OrganizationClient) -> OrganizationClient:
        """
        Метод создает клиента типа Юридическое лицо с названием АвтоЮЛ_...

        :param client_data: инстанс класса OrganizationClient
        :return: инстанс класса OrganizationClient с заполненным user_id
        """
        api_addresses = AddressRequests(self.api_request_auth_context)
        payload = {
            "additionalAttributes": [{"code": "isVIP", "value": client_data.is_vip_bool, "valueType": "BOOLEAN"}],
            "businessActivity": {},
            "businessInfo": {},
            "party": {
                "isResident": client_data.is_resident_bool,
                "nameInfo": {"corporateName": client_data.customer_name},
                "nationality": {"nationalityId": client_data.nationality_id},
                "proprietaryForm": {"proprietaryFormId": client_data.proprietary_form_id},
                "speakingLanguage": {"languageId": client_data.speaking_language_id},
                "taxRegistrationCertificate": {
                    "taxIdentificationNumber": client_data.inn,
                    "registrationReasonCode": client_data.kpp,
                    "PSRN": client_data.ogrn,
                },
            },
            "type": "ORGANIZATION",
        }
        response = self.post(url=f"{BASE_URL_API}/openapi/v1/customerManagement/customers", data=payload)
        self.check_response_status(response, 200, "Не выполнен запрос на создание нового клиента ЮЛ")

        client_data.user_id = response.json()["customerId"]
        self.set_additional_attribute(
            "customer_organization",
            client_data.user_id,
            [
                {
                    "attributeCode": "AuthorizationСode",
                    "value": client_data.auth_code,
                    "valueType": client_data.auth_code_type,
                },
                {
                    "attributeCode": "taxSchemeId",
                    "value": client_data.tax_scheme_id,
                    "valueType": client_data.tax_scheme_type,
                },
            ],
        )
        api_addresses.add_base_address_to_client(client_data.registration_address, client_data.user_id)

        wait_that(
            lambda: self.get_client_data(client_data.user_id).status == 200,
            timeout=5,
            sleep_seconds=0.5,
            exception=ClientNotFoundException,
            message="Пользователь не был создан в установленное время",
        )
        delay(1, reason="UI не успевает за API")
        test_context.client_list.append(client_data)
        test_context.client = client_data
        return client_data

    @allure.step("API: Создание нового клиента ИП")
    def create_entrepreneur_client(self, client_data: EntrepreneurClient) -> EntrepreneurClient:
        """
        Метод создает клиента типа Индивидуальный предприниматель

        :param client_data: инстанс класса EntrepreneurClient
        :return: инстанс класса EntrepreneurClient с заполненным user_id
        """
        api_addresses = AddressRequests(self.api_request_auth_context)
        payload = {
            "businessActivity": {},
            "businessInfo": {},
            "party": {
                "isResident": client_data.is_resident_bool,
                "nameInfo": {
                    "firstName": client_data.first_name,
                    "surname": client_data.sur_name,
                    "patronymic": client_data.patronymic,
                },
                "nationality": {"nationalityId": client_data.nationality_id},
                "proprietaryForm": {"proprietaryFormId": client_data.proprietary_form_id},
                "speakingLanguage": {"languageId": client_data.speaking_language_id},
                "publicOfficial": client_data.is_public_bool,
                "gender": {"genderId": client_data.gender_id},
                "birthDate": client_data.birth_date_for_api,
                "birthPlace": client_data.birth_place,
                "taxRegistrationCertificate": {
                    "taxIdentificationNumber": client_data.inn,
                    "PSRN": client_data.ogrn,
                },
                "identificationDocument": {
                    "dateOfIssue": client_data.issue_date_for_api,
                    "providedByOrganization": client_data.document_provide_by,
                    "divisionCode": client_data.document_division_code,
                    "number": client_data.document_num,
                    "series": client_data.document_serial,
                    "type": {"identificationTypeId": client_data.document_type_id},
                    "validFor": client_data.document_valid_date_for_api,
                },
            },
            "type": "ENTREPRENEUR",
        }
        response = self.post(url=f"{BASE_URL_API}/openapi/v1/customerManagement/customers", data=payload)
        self.check_response_status(response, 200, "Не выполнен запрос на создание нового клиента ИП")

        client_data.user_id = response.json()["customerId"]
        self.set_additional_attribute(
            "customer_entrepreneur",
            client_data.user_id,
            [
                {
                    "attributeCode": "taxSchemeId",
                    "value": client_data.tax_scheme_id,
                    "valueType": client_data.tax_scheme_type,
                }
            ],
        )
        api_addresses.add_base_address_to_client(client_data.registration_address, client_data.user_id)

        wait_that(
            lambda: self.get_client_data(client_data.user_id).status == 200,
            timeout=5,
            sleep_seconds=0.5,
            exception=ClientNotFoundException,
            message="Пользователь не был создан в установленное время",
        )
        delay(1, reason="UI не успевает за API")
        test_context.client_list.append(client_data)
        test_context.client = client_data
        return client_data

    def create_individual_client_with_agreement_and_account(self, client_data: IndividualClient) -> IndividualClient:
        """Метод создает клиента типа Физическое лицо, создает договор и лицевой счёт для него"""
        created_individual_client = self.create_individual_client(client_data)
        return self.personal_account_api.create_agreement_and_account(created_individual_client)

    def create_individual_client_with_agreement(self, client_data: IndividualClient) -> IndividualClient:
        """Метод создает клиента типа Физическое лицо и создает договор для него"""
        client = self.create_individual_client(client_data)
        agreement_id, agreement_number = self.personal_account_api.create_agreement(client)
        client.add_agreement(agreement_id, agreement_number)
        return client

    def create_organization_with_agreement_and_account(self, client_data: OrganizationClient) -> OrganizationClient:
        """Метод создает клиента типа Юридическое лицо, создает договор и лицевой счёт для него"""
        created_organization = self.create_organization(client_data)
        return self.personal_account_api.create_agreement_and_account(created_organization)

    def create_individual_client_with_postpaid_account(self, client_data: IndividualClient) -> IndividualClient:
        """Метод создает клиента типа Физическое лицо, создает договор и постоплатный лицевой счёт для него"""
        client = self.create_individual_client(client_data)
        agreement_id, agreement_number = self.personal_account_api.create_agreement(client)
        account_id, account_number = self.personal_account_api.create_personal_account(
            PersonalAccountData(
                agreement_id=agreement_id,
                raiting_type=2,
                threshold_break=2000,
                threshold_control=True,
            ),
            client.user_id,
        )
        wait_that(
            lambda: self.personal_account_api.get_personal_accounts("customer", client.user_id).json()["items"][0][
                "accountId"
            ]
            == account_id,
            exception=UpdateStatusException,
            timeout=10,
            sleep_seconds=0.5,
            message="Аккаунт не создался за 10 секунд",
        )
        client.add_agreement(agreement_id, agreement_number)
        client.get_agreement(agreement_id).add_account(account_id, account_number)
        test_context.client_list.append(client)
        return client

    def create_individual_client_with_agreement_and_usd_account(self, client_data: IndividualClient) -> IndividualClient:
        """Метод создает клиента типа Физическое лицо, создает договор и личный счёт для него в валюте USD"""
        client = self.create_individual_client(client_data)
        agreement_id, agreement_number = self.personal_account_api.create_agreement(client)
        account_data = PersonalAccountData(agreement_id=agreement_id, is_cash_payment_enabled=False, currency_id=2)
        account_id, account_number = self.personal_account_api.create_personal_account(account_data, client.user_id)
        wait_that(
            lambda: self.personal_account_api.get_personal_accounts("customer", client.user_id).json()["items"][0][
                "currency"
            ]["name"]
            == "USD",
            exception=UpdateStatusException,
            timeout=10,
            sleep_seconds=0.5,
            message="Аккаунт не создался в указанное время",
        )
        client.add_agreement(agreement_id, agreement_number)
        client.get_agreement(agreement_id).add_account(account_id, account_number)
        test_context.client_list.append(client)
        return client

    @allure.step("API: Создание клиента ЮЛ, договора со статусом по гарантии и ЛС")
    def create_organization_with_agreement_guarantee_and_account(
        self, client_data: OrganizationClient
    ) -> OrganizationClient:
        """
        Метод создает клиента типа Юридическое лицо, затем создает договор со статусом по гарантии и лицевой счёт
        Не дублирует логику создания клиента — переиспользует create_individual_client и create_agreement_and_account
        """
        created_org = self.create_organization(client_data)
        return self.personal_account_api.create_agreement_and_account(created_org, status_id=3)

    @allure.step("API: Получить данные по клиенту '{customer_id}'")
    def get_client_data(self, customer_id: int, check_status: bool = False) -> APIResponse:
        """
        Получить данные по клиенту.

        Parameters:
        customer_id (int): id Клиента.
        check_status (bool): проверять ли статус ответа (по умолчанию False для обратной совместимости).

        Returns:
        Response: объект ответа API с данными клиента.
        """
        client = self.get(url=f"{BASE_URL_API}/openapi/v1/customerManagement/customers/{customer_id}")
        if check_status:
            self.check_response_status(client, 200, "Не удалось получить данные клиента")
        return client

    @allure.step("API: Обновить данные по клиенту '{customer_id}'")
    def put_client_data(
        self, customer_id: int, apply_date: str, client_type: str, expected_code: int, **kwargs: Any
    ) -> APIResponse:
        """
        Обновить данные по клиенту.

        Parameters:
        customer_id (int): id Клиента.
        apply_date (str): дата обновления данных по клиенту
        if client_type == "organization" - reputation_message, customer_name, inn, kpp (str)
        elif client_type == "individual" - patronymic, series, number, inn, snils (str)
        elif client_type == "entrepreneur" - surname, first_name, patronymic, series, number, inn, snils (str)
        else - without attributes
        Returns:
        Response: объект ответа API с данными клиента.
        """
        params = {"applyDate": apply_date, "getObject": "true"}
        if client_type == "organization":
            payload = {
                "note": None,
                "businessInfo": {"reputation": kwargs.get("reputation_message")},
                "businessActivity": {"businessActivityId": 3},
                "externalReference": {"externalCustomerId": "212345"},
                "party": {
                    "nameInfo": {"corporateName": kwargs.get("customer_name")},
                    "proprietaryForm": {"proprietaryFormId": 4},
                    "isResident": True,
                    "nationality": {"nationalityId": 1},
                    "taxRegistrationCertificate": {
                        "taxIdentificationNumber": kwargs.get("inn"),
                        "registrationReasonCode": kwargs.get("kpp"),
                        "PSRN": "1172375467400",
                        "registrationDate": "2022-11-02",
                        "PSRNInfo": "00D67D7D5751F",
                        "foreignRegistrationNumber": None,
                        "RNNBO": "09513533",
                    },
                    "speakingLanguage": {"languageId": 3},
                    "note": None,
                    "ARCPS": "46439000156",
                    "economicActivities": "4622",
                },
            }
        elif client_type == "individual":
            payload = {
                "note": None,
                "businessInfo": None,
                "businessActivity": {"businessActivityId": 3},
                "externalReference": {"externalCustomerId": "212345"},
                "party": {
                    "nameInfo": {"patronymic": kwargs.get("patronymic")},
                    "birthPlace": "Самара",
                    "birthDate": "1994-01-01",
                    "isResident": True,
                    "nationality": {"nationalityId": 1},
                    "identificationDocument": {
                        "type": {"identificationTypeId": 5},
                        "series": kwargs.get("series"),
                        "number": kwargs.get("number"),
                        "dateOfIssue": "2022-03-09",
                        "providedByOrganization": "МВД",
                        "divisionCode": "770094",
                        "validFor": None,
                    },
                    "taxRegistrationCertificate": {"taxIdentificationNumber": kwargs.get("inn")},
                    "INILA": kwargs.get("snils"),
                    "biometricData": False,
                    "publicOfficial": False,
                    "speakingLanguage": {"languageId": 3},
                    "note": None,
                },
                "additionalAttributes": [  # type: ignore
                    {"code": "stringAttribute", "valueType": "STRING", "value": "test string value 2"},
                    {"code": "numberAttribute", "valueType": "NUMBER", "value": 1000001},
                    {"code": "booleanAttribute", "valueType": "BOOLEAN", "value": True},
                    {"code": "dateAttribute", "valueType": "STRING", "value": None},
                    {"code": "dateTimeAttribute", "valueType": "STRING", "value": None},
                    {"code": "int32Attribute", "valueType": "NUMBER", "value": None},
                    {"code": "int64Attribute", "valueType": "NUMBER", "value": None},
                    {"code": "stringArray", "valueType": "STRING", "value": "test string value 3"},
                    {"code": "stringArray", "valueType": "STRING", "value": "test string value 4"},
                    {"code": "stringArray", "valueType": "STRING", "value": "test string value 5"},
                    {"code": "numberArray", "valueType": "NUMBER", "value": 100000},
                    {"code": "booleanArray", "valueType": "BOOLEAN", "value": False},
                ],
            }
        elif client_type == "entrepreneur":
            payload = {
                "note": None,
                "businessInfo": None,
                "businessActivity": {"businessActivityId": 3},
                "externalReference": {"externalCustomerId": "212345"},
                "party": {
                    "nameInfo": {
                        "surname": kwargs.get("surname"),
                        "firstName": kwargs.get("first_name"),
                        "patronymic": kwargs.get("patronymic"),
                    },
                    "proprietaryForm": {"proprietaryFormId": 34},
                    "birthPlace": "Самара",
                    "birthDate": "1994-01-01",
                    "gender": {"genderId": 1},
                    "isResident": True,
                    "nationality": {"nationalityId": 1},
                    "identificationDocument": {
                        "type": {"identificationTypeId": 5},
                        "series": kwargs.get("series"),
                        "number": kwargs.get("number"),
                        "dateOfIssue": "2022-03-09",
                        "providedByOrganization": "МВД",
                        "divisionCode": "770094",
                        "validFor": None,
                    },
                    "taxRegistrationCertificate": {
                        "taxIdentificationNumber": kwargs.get("inn"),
                        "PSRN": "312506377281216",
                        "registrationDate": "2016-02-15",
                        "PSRNInfo": "F377B812AABD83F",
                        "RNNBO": "0742491350",
                    },
                    "INILA": kwargs.get("snils"),
                    "publicOfficial": False,
                    "speakingLanguage": {"languageId": 3},
                    "note": None,
                    "ARCPS": "46439000156",
                    "economicActivities": "4622",
                },
            }
        else:
            payload = {}
        client = self.put(
            url=f"{BASE_URL_API}/openapi/v1/customerManagement/customers/{customer_id}", params=params, data=payload
        )
        self.check_response_status(client, expected_code, "Не обновились данные по клиенту")
        return client

    @allure.step("API: Обновить данные по подразделению клиента '{subdivision_id}'")
    def put_client_subdivision_data(
        self, subdivision_id: int, apply_date: str, expected_code: int, payload_data: bool, **kwargs: Any
    ) -> APIResponse:
        """
        Обновить данные по подразделению клиента
        Parameters:
        subdivision_id (int): id подразделения.
        apply_date (str): дата обновления данных по клиенту
        expected_code (int): ожидаемый код ответа
        payload_data (bool): нужно ли отправлять данные в теле запроса
        **kwargs - new_name, kpp (str) новые данные для подразделения
        Returns:
        Response: объект ответа API с данными клиента.
        """
        params = {"applyDate": apply_date, "getObject": "true"}
        if payload_data:
            payload = {
                "businessActivity": {"businessActivityId": 3},
                "note": None,
                "externalReference": {"externalSubdivisionId": "2"},
                "party": {
                    "nameInfo": {"corporateName": kwargs.get("new_name")},
                    "nationality": {"nationalityId": 1},
                    "note": None,
                    "taxRegistrationCertificate": {"registrationReasonCode": kwargs.get("kpp")},
                },
            }
        else:
            payload = {}
        subdivision = self.put(
            url=f"{BASE_URL_API}/openapi/v1/customerManagement/subdivisions/{subdivision_id}",
            params=params,
            data=payload,
        )
        self.check_response_status(subdivision, expected_code, "Не обновились данные по подразделению")
        return subdivision

    @allure.step("API: Получить данные по связанному лицу '{linked_person_id}'")
    def get_linked_person_data(self, linked_person_id: int) -> APIResponse:
        """
        Получить данные по связанному лицу.

        Parameters:
        linked_person_id (int): id связанного лица.

        Returns:
        Response: объект ответа API с данными связанного лица.
        """
        linked_person = self.get(url=f"{BASE_URL_API}/openapi/v1/customerManagement/linkedPersons/{linked_person_id}")
        return linked_person

    @allure.step("API: Получить данные по специализации связанного лица '{linked_function_id}'")
    def get_linked_person_specialisation(self, linked_function_id: int) -> APIResponse:
        """
        Получить данные по специализации связанного лица.

        Parameters:
        linked_function_id (int): id функции связанного лица.

        Returns:
        Response: объект ответа API с данными связанного лица.
        """
        linked_person = self.get(
            url=f"{BASE_URL_API}/openapi/v1/customerManagement/linkedPersons/linkedPersonFunctions/{linked_function_id}"
        )
        return linked_person

    @allure.step("API: Создать 'Обезличенное' связанное лицо для клиента '{client_id}' с названием '{name}'")
    def create_linked_person(self, client_id: int, name: str) -> int:
        """
        Метод создает обезличенное связанное лицо

        Parameters:
        client_id (int): id Клиента.
        name (str): название связанного лица.

        Returns:
        int: id связанного лица.
        """
        payload = {
            "party": {
                "nameInfo": {"impersonalName": name},
                "note": None,
                "speakingLanguage": {"languageId": 3},
                "type": "IMPERSONAL",
            }
        }
        response = self.post(
            url=f"{BASE_URL_API}/openapi/v1/customerManagement/customers/{client_id}/linkedPersons", data=payload
        )
        self.check_response_status(response, 200, "Не привязалось связанное лицо")
        delay(0.5, "Нужно время на сохранение данных")
        linked_person_id = response.json()["linkedPersonId"]
        payload_add_funk = {
            "entity": {"code": "customer", "id": client_id},
            "linkedPersonFunctionType": "CONTACT_PERSON",
            "specializationTypes": [{"specializationTypeId": 4}],
        }
        response_add_func = self.post(
            url=f"{BASE_URL_API}/openapi/v1/customerManagement/linkedPersons/{linked_person_id}/linkedPersonFunctions",
            data=payload_add_funk,
        )
        self.check_response_status(response, 200, "Не привязалась функция связанного лица")
        linked_function_id = response_add_func.json()["linkedPersonFunctionId"]
        wait_that(
            lambda: self.get_linked_person_data(linked_person_id).status == 200,
            timeout=5,
            sleep_seconds=0.5,
            exception=LinkedPersonException,
            message="Связанное лицо не было создано в установленное время",
        )
        wait_that(
            lambda: self.get_linked_person_specialisation(linked_function_id).status == 200,
            timeout=5,
            sleep_seconds=0.5,
            exception=LinkedPersonFunctionException,
            message="Функция связанного лица не была создана в установленное время",
        )
        api_addresses = AddressRequests(self.api_request_auth_context)
        wait_that(
            lambda: api_addresses.get_client_addresses(linked_person_id).status == 200,
            timeout=5,
            sleep_seconds=0.5,
            exception=LinkedPersonPullAddressException,
            message="Не сформирован пул адресов связанного лица",
        )
        delay(1, reason="Даже при наличии нового связного лица через API, на UI возникает ошибка если рано перейти")
        return linked_person_id

    @allure.step(
        "API: Создать 'Обезличенное' связанное лицо для клиента '{client_id}' с названием '{name}' и базовым "
        "адресом регистрации"
    )
    def create_linked_person_with_registration_address(
        self, client_id: int, name: str, map_url: list[None | str] = None
    ) -> int:
        """
        Метод создает обезличенное связанное лицо с адресом регистрации

        Parameters:
        client_id (int): id Клиента.
        name (str): название связанного лица.

        Returns:
        int: id связанного лица.
        """
        linked_person_id = self.create_linked_person(client_id=client_id, name=name)
        api_addresses = AddressRequests(self.api_request_auth_context)
        api_addresses.add_registry_address_linked_person(linked_person_id=linked_person_id, map_url=map_url)
        return linked_person_id

    @allure.step("API: Создание комментария для {entity_type} с идентификатором {entity_id}")
    def create_comment(self, entity_type: Literal["INQUIRY", "CUSTOMER"], entity_id: int, comment: str) -> int:
        """
        Метод создает комментарий для Клиента/Заявки

        :param entity_type: тип сущности, для которой добавляется комментарий ("INQUIRY" - Заявка, "CUSTOMER" - Клиент)
        :param entity_id: идентификатор сущности (заявки/клиента)
        :param comment: текст комментария
        :return: идентификатор комментария
        """
        payload = {"entity": {"entityId": entity_id, "entityTypeCode": entity_type}, "text": comment}
        response = self.post(url=f"{BASE_URL_API}/openapi/v1/crm/notes", data=payload)
        self.check_response_status(
            response, 201, f"Не удалось создать комментарий для {entity_type} с идентификатором {entity_id}"
        )
        return response.json()["noteId"]

    @allure.step("Найти клиента")
    def search_client(
        self, account_status_ids: list, agreement_status_ids: list, customer_status_ids: list, customer_name: str
    ) -> APIResponse:
        params = {"hierarchyLevel": "account", "limit": "60", "offset": 0}
        payload = {
            "accountStatusIds": account_status_ids,
            "agreementStatusIds": agreement_status_ids,
            "customerName": f"%{customer_name}%",
            "customerStatusIds": customer_status_ids,
        }
        search_data = self.post(
            url=f"{BASE_URL_API}/ps/v1/tailored-rm/integration/searchGeneral", params=params, data=payload
        )
        self.check_response_status(search_data, 200, "Не получен список поиска")
        return search_data

    @allure.step("API: Создать подразделение для ЮЛ")
    def make_subdivision(self, client_id: int, unit_name: str) -> int:
        """
        Метод для создания подразделения для ЮЛ
        """
        payload = {
            "party": {
                "nameInfo": {"corporateName": unit_name},
                "nationality": {"nationalityId": 1},
                "note": None,
                "taxRegistrationCertificate": {},
            }
        }
        subdivision = self.post(
            url=f"{BASE_URL_API}/openapi/v1/customerManagement/customers/{client_id}/subdivisions", data=payload
        )
        self.check_response_status(subdivision, 200, "Не создано подразделение ЮЛ")
        payload_add_places = {
            "addressString": BasicSystemAddress.address,
            "entity": {"code": "subdivision", "id": subdivision.json()["subdivisionId"]},
            "externalAddressId": BasicSystemAddress.external_address_id,
            "type": {"placeTypeId": 1},
        }
        places = self.post(url=f"{BASE_URL_API}/openapi/v1/customerManagement/places", data=payload_add_places)
        self.check_response_status(places, 200, "Не добавлен адрес регистрации для подразделения")
        return subdivision.json()["subdivisionId"]

    @allure.step("API: Установка значений дополнительных атрибутов для экземпляра сущности")
    def set_additional_attribute(self, entity_type_code: str, entity_id: int, values: Any) -> dict:
        payload = {"entityId": entity_id, "entityTypeCode": entity_type_code, "values": values}
        response = self.post(
            url=f"{BASE_URL_API}/openapi/v1/attribute-service/entityTypes/{entity_type_code}/entities/{entity_id}/values/set",
            data=payload,
        )
        self.check_response_status(response, 200, "Не добавлен адрес регистрации для подразделения")
        return response.json()

    @allure.step("API: Установка значений дополнительных атрибутов для экземпляра сущности")
    def create_client_with_payment(
        self, client: IndividualClient | OrganizationClient, balance: float
    ) -> IndividualClient | OrganizationClient:
        if client.type == "Физическое лицо":
            client = self.create_individual_client_with_agreement_and_account(client)
        if client.type == "Юридическое лицо":
            client = self.create_organization_with_agreement_and_account(client)
        self.payment_api.create_default_payment(client.agreements[0].accounts[0].id, balance)
        self.personal_account_api.wait_check_current_main_balance(client.agreements[0].accounts[0].id, balance)
        return client

    @allure.step("Создание договора и ЛС. Пополнение ЛС на сумму {balance}")
    def create_agreement_and_account_with_payment(
        self, client: IndividualClient | OrganizationClient | EntrepreneurClient, balance: float
    ) -> PaymentInfo:
        client = self.personal_account_api.create_agreement_and_account(client)
        payment = PaymentInfo()
        payment.document_number = int(
            self.payment_api.create_default_payment(client.agreements[-1].accounts[0].id, balance)
        )
        self.personal_account_api.wait_check_current_main_balance(client.agreements[-1].accounts[0].id, balance)
        return payment
