from dataclasses import dataclass, field
from typing import Any, Tuple

import allure
from playwright.sync_api import APIRequestContext, APIResponse

from api.exceptions import (
    CommercialOrderIdNotFoundException,
    CommercialOrderNumberNotFoundException,
    InquiryConnectException,
    InquiryTechnicalSolutionException,
    LinkedPersonException,
    LinkedPersonFunctionException,
    LinkedPersonPullAddressException,
    SaleStatusException,
    SearchCommercialOrderException,
    UserIdNotFoundException,
)
from api.requests.address_requests import AddressRequests
from api.requests.base_requests import BaseRequests
from api.requests.lis_requests.phone_numbers import PhoneNumberData, PhoneNumbersRequests
from api.requests.lis_requests.sim_cards import SimCardData, SimCardsRequests
from common.helpers.checker import assert_that, check_that, wait_that
from common.helpers.data_generator import get_current_datetime_string
from common.helpers.env_helper import BASE_URL_API
from common.helpers.time_helpers import delay
from models.address_info import BasicSystemAddress
from models.user import BaseClient


@dataclass
class InfoAboutProduct:
    subs_id: int = 0
    product_name: str = ""
    phone_number: str = ""
    internet_number: str = ""
    one_time_payment: float = 0.0
    subscription_fee: float = 0.0
    total_amount: float = 0.0


@dataclass
class InfoAboutBundle:
    bundle_name: str = ""
    products: list[InfoAboutProduct] = field(default_factory=list)
    one_time_payment: float = 0.0
    subscription_fee: float = 0.0

    def add_product(self, product: InfoAboutProduct) -> None:
        self.products.append(product)
        self.one_time_payment += product.one_time_payment
        self.subscription_fee += product.subscription_fee


@dataclass
class SaleProduct:
    client: BaseClient
    product: InfoAboutProduct
    commercial_order: int
    commercial_order_number: int
    inquiry_id: int
    product_id: list[int]
    linked_person_id: int
    date: str

    def __init__(self) -> None:
        self.client = BaseClient()
        self.product = InfoAboutProduct()
        self.commercial_order = 0
        self.commercial_order_number = 0
        self.inquiry_id = 0
        self.product_id = [0]
        self.linked_person_id = 0
        self.date = get_current_datetime_string().replace(" ", "-").replace(".", "/")


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

    @allure.step("API: Получить данные по клиенту '{customer_id}'")
    def get_client_data(self, customer_id: int) -> APIResponse:
        """
        Получить данные по клиенту.

        Parameters:
        customer_id (int): id Клиента.

        Returns:
        Response: объект ответа API с данными клиента.
        """
        client = self.get(url=f"{BASE_URL_API}/openapi/v1/customerManagement/customers/{customer_id}")
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

    @allure.step("API: Получение информации о заявке по идентификатору")
    def get_inquiry(self, inquiry_id: int) -> APIResponse:
        """
        Возвращает информацию о заявке по id
        :param inquiry_id: id заявки
        :return: ответ на запрос
        """
        response = self.get(url=f"{BASE_URL_API}/openapi/v1/inquiries/{inquiry_id}")
        self.check_response_status(response, 200, "Невозможно получить информацию по заявке")
        return response

    @allure.step("API: Продвижение заявки")
    def inquiry_forward(self, app_id: int, body: dict) -> APIResponse:
        """
        Возвращает информацию о продвижении заявки
        :param app_id: id заявки
        :param body: dict тело заявки
        :return: ответ на запрос
        """
        return self.post(url=f"{BASE_URL_API}/openapi/v1/inquiries/{app_id}/forward", data=body)

    @allure.step("API: Получение информации о статусе выполнения заявки")
    def get_commercial_order_stage(self, commercial_order: int) -> dict:
        """
        Возвращает информацию о статусе выполнения заявки
        :param commercial_order: id коммерческого заказа
        :return: словарь со статусом заказа
        """
        response = self.get(
            url=f"{BASE_URL_API}/openapi/v1/productManagement/commercialOrders/{commercial_order}/commonInfo"
        )
        self.check_response_status(response, 200, "Невозможно получить информацию по коммерческому заказу")
        return response.json()["stage"]

    @allure.step("API: Получение идентификатора адреса клиента")
    def get_address_id(self, user_id: int) -> int:
        """
        Возвращает id адреса клиента
        :param user_id: id клиента, созданного фикстурой create_user
        :return: id адреса
        """
        api_addresses = AddressRequests(self.api_request_auth_context)
        response_address = api_addresses.get_client_addresses(user_id)
        return response_address.json()["items"][0]["externalAddressId"]

    @allure.step("API: Получение объектов из классификаторов {classifiers}, связанные с адресным объектом {address_id}")
    def get_linked_objects(self, address_id: int, classifiers: str) -> list:
        """
        Возвращает объекты из указанных классификаторов, связанные с заданным адресным объектом или его родительскими объектами
        :param address_id: id клиента, адресного объекта
        :param classifiers: коды классификаторов, связанные объекты из которых будут возвращены
        :return: список объектов
        """
        response = self.get(
            url=f"{BASE_URL_API}/openapi/v1/locationManagement/addresses/{address_id}/linkedObjects?classifiers={classifiers}"
        )
        self.check_response_status(response, 200, "Невозможно получить связанные объекты")
        return response.json()["linkedObjects"]

    @allure.step("API: Получение связанных лиц клиента")
    def get_linked_person(self, user_id: int) -> list:
        """
        Получение связанных лиц клиента
        :param user_id: id клиента
        :return: список объектов с информацией о связанных лицах клиента
        """
        body_person = {
            "entity": {"code": "customer", "id": user_id},
            "linkedPerson": {},
            "linkedPersonFunctionStatusIds": [1],
        }
        response_person = self.post(
            url=f"{BASE_URL_API}/openapi/v1/customerManagement/linkedPersons/linkedPersonFunctions/search?returnCount=true&limit=60&offset=0",
            data=body_person,
        )
        self.check_response_status(response_person, 200, "Не удалось получить связанные лица клиента")
        return response_person.json()["items"]

    @allure.step("API: Создание связанного лица")
    def make_linked_person(self, date: str, user_id: int) -> int:
        """
        Создание связанного лица
        :param date: строка с датой создания вида "05/12/2025-15:31:05"
        :param user_id: id клиента, созданного фикстурой create_user
        :return: id связанного лица клиента
        """
        body_person = {
            "party": {
                "type": "IMPERSONAL",
                "nameInfo": {"impersonalName": f"IMPERSONAL - {date}"},
                "speakingLanguage": {"languageId": 3},
            }
        }
        response_person = self.post(
            url=f"{BASE_URL_API}/openapi/v1/customerManagement/customers/{user_id}/linkedPersons", data=body_person
        )
        self.check_response_status(response_person, 200, "Не получилось добавить связанное лицо клиенту")
        return response_person.json()["linkedPersonId"]

    @allure.step("API: Добавление связанного лица в UDS")
    def add_linked_person_to_uds(self, user_id: int, linked_person_id: int) -> None:
        """
        Добавление связанного лица в UDS
        :param user_id: id клиента, созданного фикстурой create_user
        :param linked_person_id: id связанного лица из make_linked_person
        Упадет с ошибкой, если добавление не завершилось успешно
        """
        body_uds = {
            "entity": {"code": "customer", "id": user_id},
            "linkedPersonFunctionType": "CONTACT_PERSON",
            "specializationTypes": [
                {"specializationTypeId": 1},
                {"specializationTypeId": 2},
                {"specializationTypeId": 3},
                {"specializationTypeId": 4},
            ],
            "emailContacts": [{"email": "mail@mail.ru", "isMain": True}],
        }
        response_uds = self.post(
            url=f"{BASE_URL_API}/openapi/v1/customerManagement/linkedPersons/{linked_person_id}/linkedPersonFunctions",
            data=body_uds,
        )
        self.check_response_status(response_uds, 200, "Связанное лицо не добавлено в UDS")
        assert response_uds.json()["linkedPersonFunctionId"] is not None

    @allure.step("API: Добавление параметров продажи")
    def add_inquiry_properties(self, user_id: int) -> None:
        """
        Добавление кастомных параметров заявки
        :param user_id: id клиента, созданного фикстурой create_user
        Упадет с ошибкой, если добавление не завершилось успешно
        """
        body_properties = {
            "inquiryContext": {"topic": {"topicCode": "SALE_TOPIC"}},
            "contact": {"customer": {"customerId": user_id}},
        }
        response_properties = self.post(
            url=f"{BASE_URL_API}/openapi/v1/inquiries/add/parameters",
            data=body_properties,
        )
        self.check_response_status(response_properties, 200, "Не добавились параметры для заявки")

    @allure.step("API: Создание заявки")
    def register_inquiry(
        self, user_id: int, linked_person_id: int, agreement_id: int | None = None, account_id: int | None = None
    ) -> int:
        """
        Создание заявки
        :param user_id: id клиента, созданного фикстурой create_user
        :param linked_person_id: id связанного лица из make_linked_person
        :param agreement_id: id договора клиента, для которого нужно провести продажу
        :param account_id: id лицевого счета, для которого нужно провести продажу
        :return: inquiry_id идентификатор заявки
        """
        body_reg_inquiry = {
            "inquiry": {
                "topic": {"topicCode": "SALE_TOPIC"},
                "customProperties": [
                    {
                        "customPropertyDeclaration": {"customPropertyDeclarationCode": "inqrLinkedPerson"},
                        "type": "DICTIONARY",
                        "values": [{"itemCode": linked_person_id}],
                    },
                ],
                "email": "mail@mail.ru",
            },
            "contact": {"customer": {"customerId": user_id}},
        }
        if agreement_id is not None and account_id is not None:
            body_reg_inquiry["inquiry"]["customProperties"].extend(
                [
                    {
                        "customPropertyDeclaration": {"customPropertyDeclarationCode": "saleAgreement"},
                        "type": "DICTIONARY",
                        "values": [{"itemCode": str(agreement_id)}],
                    },
                    {
                        "customPropertyDeclaration": {"customPropertyDeclarationCode": "saleAccount"},
                        "type": "DICTIONARY",
                        "values": [{"itemCode": str(account_id)}],
                    },
                    {
                        "customPropertyDeclaration": {"customPropertyDeclarationCode": "saleAddAgreementAdd"},
                        "type": "DICTIONARY",
                        "values": [{"itemCode": "CREATE_AUTO"}],
                    },
                ]
            )
        else:
            body_reg_inquiry["inquiry"]["customProperties"].append(
                {
                    "customPropertyDeclaration": {"customPropertyDeclarationCode": "saleAddAgreement"},
                    "type": "DICTIONARY",
                    "values": [{"itemCode": "AUTO"}],
                }
            )
        response_reg_inquiry = self.post(
            url=f"{BASE_URL_API}/openapi/v1/inquiries?fields=inquiryId%2Ccontact%28contactId%29%2CcreateDate&getObject=True",
            data=body_reg_inquiry,
        )
        self.check_response_status(response_reg_inquiry, 201, "Заявка не создалась")
        return response_reg_inquiry.json()["inquiryId"]

    @allure.step("API: Получение идентификатора коммерческого заказа")
    def get_commercial_order_id(self, inquiry_id: int) -> int:
        """
        Возвращает id ком заказа
        :param inquiry_id: id заявки из register_inquiry
        :return: id ком заказа
        """
        wait_that(
            lambda: True
            in [
                custom_property["customPropertyDeclaration"]["customPropertyDeclarationCode"] == "commercialOrderId"
                and len(custom_property["textValue"]) > 0
                for custom_property in self.get_inquiry(inquiry_id).json()["customProperties"]
            ],
            timeout=30,
            sleep_seconds=2,
            exception=SearchCommercialOrderException,
            message="Поиск не нашел созданного КЗ",
        )
        custom_properties = self.get_inquiry(inquiry_id).json()["customProperties"]
        for custom_property in custom_properties:
            if custom_property["customPropertyDeclaration"]["customPropertyDeclarationCode"] == "commercialOrderId":
                return int(custom_property["textValue"])
        raise CommercialOrderIdNotFoundException(f'Не найден коммерческий заказ "{inquiry_id}"')

    @allure.step("API: Получение идентификатора заявки коммерческого заказа")
    def get_commercial_order_number(self, inquiry_id: int) -> int:
        """
        Возвращает id заявки ком заказа
        :param inquiry_id: id заявки из register_inquiry
        :return: id заявки ком заказа
        """
        response_commercial_order = self.get_inquiry(inquiry_id).json()["customProperties"]
        for custom_property in response_commercial_order:
            if custom_property["customPropertyDeclaration"]["customPropertyDeclarationCode"] == "orderInquiryId":
                return int(custom_property["textValue"])
        raise CommercialOrderNumberNotFoundException(f'Не найдена заявка коммерческого заказа "{inquiry_id}"')

    @allure.step("API: Добавление продукта в заказ")
    def select_product_offer(
        self, address_id: int, commercial_order: int, product_offering_id: int, region_id: int
    ) -> list[int]:
        """
        Возвращает id продукта выбранного ПП для проведения заявки
        :param address_id: id адреса клиента из get_address_id
        :param commercial_order: id ком заказа продажи продукта из get_commercial_order_id
        :param product_offering_id: id продуктового предложения, которое планируется продать
        :param region_id: id региона, в котором проводится продажа
        :return: список id продуктов для подключения
        """
        body_prod_select = {
            "addProductsParameters": [
                {
                    "productParameters": {
                        "addressId": address_id,
                        "productOfferingId": product_offering_id,
                        "regionId": region_id,
                    }
                }
            ],
            "operation": "CONNECT_INDEPENDENT_PRODUCT",
        }
        response_product = self.post(
            url=f"{BASE_URL_API}/openapi/v1/productManagement/commercialOrders/{commercial_order}/orderProducts/add/bulk",
            data=body_prod_select,
        )
        self.check_response_status(response_product, 200, "Не получен список продуктов")
        return [product["productId"] for product in response_product.json()["addedProducts"]]

    @allure.step("API: Получение информации по ресурсам, которые нужно забронировать")
    def get_order_resource_ids(self, product_id: int, commercial_order: int) -> list:
        """
        Получение id ресурсов продукта, которые необходимо заполнить.
        :param product_id: id продукта, который хотим инстанцировать клиенту из select_product_offer
        :param commercial_order: id ком заказа продажи продукта из get_commercial_order_id
        :return: список id ресурсов
        """
        response = self.get(
            url=f"{BASE_URL_API}/openapi/v1/productManagement/commercialOrders/{commercial_order}/orderProducts/{product_id}"
        )
        self.check_response_status(response, 200, "Невозможно получить информацию по бронированию ресурсов")
        resource_list = []
        for parameter in response.json()["orderCustomerFacingServices"]:
            if len(parameter["orderResources"]) > 0:
                for resource in parameter["orderResources"]:
                    resource_list.append(resource)
        return [
            {"resource_type": resource["resourceType"], "resource_id": resource["orderResourceId"]}
            for resource in resource_list
        ]

    @allure.step("API: Получение SIM карт доступных для бронирования")
    def get_sim_cards_list(self) -> APIResponse:
        """
        Получение списка sim-карт
        :return: ответ сервиса, содержащий информацию по sim-картам
        """
        request_body = {
            "isReserved": False,
            "macroRegionIds": [999],
            "SIMCardTechnologyIds": [1],
            "stateIds": [9],
            "statusIds": [1],
        }
        response = self.post(
            url=f"{BASE_URL_API}/openapi/v1/logicalResources/SIMCards/search?fields=ICC,IMSI,expirationDate,SIMCardType(name),switch(equipmentId,name)&sort=ICC&limit=10&offset=0",
            data=request_body,
        )
        self.check_response_status(response, 200, "Невозможно получить список доступных sim карт")
        return response

    @allure.step("API: Бронирование SIM карты")
    def lock_sim_card(
        self, product_id: int, commercial_order: int, sim_card: SimCardData, order_resource_id: int
    ) -> None:
        """
        Бронирование sim-карты телефона
        :param product_id: id продукта, который хотим инстанцировать клиенту из select_product_offer
        :param commercial_order: id ком заказа продажи продукта из get_commercial_order_id
        :param sim_card: объект класса. В нем хранится информация о сущности, которую хотим забронировать
        :param order_resource_id: id ресурса продукта, который бронируем
        Упадет с ошибкой, если бронировние не завершилось успешно
        """
        request_body = {
            "commercialOrderId": commercial_order,
            "fillSource": "LIS",
            "orderProductId": product_id,
            "resources": [
                {
                    "fillCharacteristics": [
                        {"code": "iccid", "type": "string", "values": [sim_card.icc]},
                        {"code": "lockId", "type": "string", "values": []},
                    ],
                    "orderResourceIds": [order_resource_id],
                }
            ],
            "switchId": sim_card.switchId,
        }
        response = self.post(
            url=f"{BASE_URL_API}/openapi/v1/tailored_nbss/resources/SIMCard/lock/bulk",
            data=request_body,
        )
        self.check_response_status(response, 200, "Невозможно забронировать sim карту")

    @allure.step("API: Получение MSISDN доступных для бронирования")
    def get_phone_list(self, switch_id: int, macro_region_id: int) -> APIResponse:
        """
        Получение списка номеров телефонов
        :param switch_id: id коммутатора
        :param macro_region_id: id макро региона
        :return: ответ сервиса, содержащий информацию по номерам
        """
        request_body = {
            "equipmentFilters": {"equipmentIds": [switch_id], "standardIds": [1]},
            "isReserved": False,
            "isTypeDef": True,
            "macroRegionIds": [macro_region_id],
            "numberCategoryIds": [1],
            "numberClassIds": [1],
            "stateDateRanges": [
                {"stateId": 2},
                {"stateDateRange": {"stateDateRangeTo": get_current_datetime_string()}, "stateId": 4},
            ],
            "statusIds": [1],
        }
        response = self.post(
            url=f"{BASE_URL_API}/openapi/v1/logicalResources/phoneNumbers/search?numberFilter=FREE&fields=MSISDN,numberClass(numberClassId,name),type(name),switch(equipmentId,name)&sort=MSISDN&limit=60&offset=0",
            data=request_body,
        )
        self.check_response_status(response, 200, "Невозможно получить список доступных номеров телефонов")
        return response

    @allure.step("API: Бронирование MSISDN")
    def lock_number(
        self,
        product_id: int,
        commercial_order: int,
        phone_number: PhoneNumberData,
        order_resource_id: int,
        switch_id: int,
    ) -> None:
        """
        Бронирование номера телефона
        :param product_id: id продукта, который хотим инстанцировать клиенту из select_product_offer
        :param commercial_order: id ком заказа продажи продукта из get_commercial_order_id
        :param phone_number: объект класса. В нем хранится информация о сущности, которую хотим забронировать
        :param order_resource_id: id ресурса продукта, который бронируем
        :param switch_id: id коммутатора
        Упадет с ошибкой, если бронировние не завершилось успешно
        """
        request_body = {
            "commercialOrderId": commercial_order,
            "connectionType": "Regular",
            "fillSource": "LIS",
            "orderProductId": product_id,
            "resources": [
                {
                    "fillCharacteristics": [
                        {"code": "phoneNumber", "type": "string", "values": [phone_number.MSISDN]},
                        {"code": "lockId", "type": "string", "values": []},
                    ],
                    "orderResourceIds": [order_resource_id],
                }
            ],
            "switchId": switch_id,
        }
        response = self.post(
            url=f"{BASE_URL_API}/openapi/v1/tailored_nbss/resources/defPhoneNumber/lock/bulk",
            data=request_body,
        )
        self.check_response_status(response, 200, "Невозможно получить список доступных sim карт")

    @allure.step("API: Бронирование ресурсов")
    def resources_reserve(self, product_id: int, commercial_order: int) -> None:
        """
        Бронирование ресурсов для продажи продукта
        :param product_id: id продукта, который хотим инстанцировать клиенту из select_product_offer
        :param commercial_order: id ком заказа продажи продукта из get_commercial_order_id
        Упадет с ошибкой, если бронировние не завершилось успешно
        """
        order_resource_list = self.get_order_resource_ids(product_id, commercial_order)
        order_sim = None
        order_number = None
        for order_resource in order_resource_list:
            if order_resource["resource_type"] == "SIMCard":
                order_sim = order_resource["resource_id"]
            elif order_resource["resource_type"] == "defPhoneNumber":
                order_number = order_resource["resource_id"]
        assert_that(
            lambda: order_sim is not None and order_number is not None,
            "Не получена информация по ресурсам для бронирования",
        )
        sim_request = SimCardsRequests(self.api_request_auth_context)
        number_request = PhoneNumbersRequests(self.api_request_auth_context)
        sims = self.get_sim_cards_list()
        chosen_sim = sim_request.get_sim_cards_data(sims)[0]
        self.lock_sim_card(product_id, commercial_order, chosen_sim, order_sim)
        numbers = self.get_phone_list(chosen_sim.switchId, number_request.macro_region_id)
        self.lock_number(
            product_id, commercial_order, number_request.get_numbers_data(numbers)[0], order_number, chosen_sim.switchId
        )

    @allure.step("API: Проверка корректности заказа")
    def order_check(self, commercial_order_number: int) -> None:
        """
        Проверка корректности заказа
        :param commercial_order_number: номер заявки коммерческого заказа из get_commercial_order_number
        Упадет с ошибкой, если проверка не завершилась успешно
        """
        body_clarifying = {"activity": {"activityCode": "CLARIFYING_NEEDS_VERIFYING"}}
        response_clarifying = self.inquiry_forward(commercial_order_number, body_clarifying)
        self.check_response_status(response_clarifying, 204, "Проверка корректности заказа не прошла")

    @allure.step("API: Проверка технической возможности")
    def technical_solution_verifying(self, commercial_order_number: int) -> None:
        """
        Проверка технической возможности подключения продукта по параметрам заявки
        :param: commercial_order_number номер заявки коммерческого заказа из get_commercial_order_number

        Упадет с ошибкой, если проверка не завершилась успешно
        """
        body_technical = {"activity": {"activityCode": "TECHNICAL_SOLUTION"}}
        wait_that(
            lambda: self.inquiry_forward(commercial_order_number, body_technical).status == 204,
            timeout=15,
            sleep_seconds=2,
            exception=InquiryTechnicalSolutionException,
            message="Не прошла проверка технической возможности",
        )

    @allure.step("API: Заявка на подключение продукта клиенту")
    def connect_inquiry(self, inquiry_id: int) -> None:
        """
        Подключение продукта клиенту
        :param inquiry_id: id заявки на продажу продукта из register_inquiry
        Упадет с ошибкой, если подключение не завершилось успешно
        """
        connect_timeout = 75
        body_connect = {"activity": {"activityCode": "AUTO_CREATE_AGR_ACC"}, "login": "Admin"}
        wait_that(
            lambda: self.inquiry_forward(inquiry_id, body_connect).status == 204,
            timeout=connect_timeout,
            sleep_seconds=2,
            exception=InquiryConnectException,
            message=f"Заявка на подключение не выполнилась за {connect_timeout} секунд",
        )

    @allure.step("API: Ожидание выполнения заявки")
    def get_sale_status(self, commercial_order: int) -> None:
        """
        Метод для ожидания выполнения заявки
        :param commercial_order: id ком заказа продажи продукта из get_commercial_order_id
        Упадет с ошибкой, если продажа не завершилась успешно
        """
        sale_timeout = 400
        wait_that(
            lambda: "COMPLETED" in self.get_commercial_order_stage(commercial_order)["code"],
            timeout=sale_timeout,
            sleep_seconds=5,
            exception=SaleStatusException,
            message=f"Заявка не завершилась за {sale_timeout} секунд.'",
        )

    @allure.step("API: Получение абонента клиента")
    def get_client_subscriber(self, user_id: int | None = None, subscription_id: int | None = None) -> Tuple[int, int]:
        """
        Метод для получения последнего по дате создания абонента у клиента
        :param: user_id: id клиента, созданного фикстурой create_user
        :return: subs_id, msisdn/internet - идентификатор абонента, номер телефона/интернета
        """
        body_subs: dict[str, dict[str, int | list[int]]] = {}
        if user_id:
            body_subs = {"subscriptionInfoBaseFilter": {"customerId": user_id}}
        if subscription_id:
            body_subs = {"subscriptionInfoBaseFilter": {"subscriptionIds": [subscription_id]}}
        response_subs = self.post(
            url=f"{BASE_URL_API}/openapi/v1/subscriptionManagement/subscriptions/search", data=body_subs
        )
        self.check_response_status(response_subs, 200, "Не получены данные об абонентах")
        item = self.get_last_created_item_response(response_subs.json()["items"])
        return item["subscriptionId"], item["identification"]["identificationValue"]

    @allure.step("API: Получение информации о первом элементе заказа")
    def get_subscriber_info(self, sale: SaleProduct) -> SaleProduct:
        """
        Метод для заполнения информации абонента
        :param sale: объект класса SaleProduct
        :return: объект класса SaleProduct,
        """
        body_info_subs = {"params": {"limit": 100, "offset": 0}}
        response_info_subs = self.post(
            url=f"{BASE_URL_API}/openapi/v1/productManagement/commercialOrders/{sale.commercial_order}/orderProducts/search",
            data=body_info_subs,
        )
        self.check_response_status(response_info_subs, 200, "Не получены данные о подписке абонента")
        subs_item = response_info_subs.json()["items"][0]
        sale.product.product_name = subs_item["name"]
        sale.product.total_amount = float(subs_item["totalPrice"]["amount"])
        for part in subs_item["totalPrice"]["includedParts"]:
            if part["priceTypeCode"] == "FeeProdOfferingPrice":
                sale.product.one_time_payment = float(part["amount"])
            if part["priceTypeCode"] == "RecurringChargeProdOfferPriceCharge":
                sale.product.subscription_fee = float(part["amount"])
        agreement_id = subs_item["payerInformation"]["agreement"]["agreementId"]
        agreement_number = subs_item["payerInformation"]["agreement"]["agreementNumber"]
        sale.client.add_agreement(agreement_id, agreement_number)
        sale.client.get_agreement(agreement_id).add_account(
            subs_item["payerInformation"]["account"]["accountId"],
            subs_item["payerInformation"]["account"]["accountNumber"],
        )
        sale.product.subs_id = int(subs_item["productPrototypes"][0]["holderPrototype"]["holderMapping"]["holderId"])
        return sale

    def sale_prepare_and_add_product(
        self, user_id: int, product_offering_id: int, agreement_id: int | None = None, account_id: int | None = None
    ) -> SaleProduct:
        """
        Метод для подготовки продажи и проведения обязательных шагов
        :param user_id: id клиента, для которого инициируется продажа
        :param product_offering_id: id продуктового предложения, которое планируется продать
        :param agreement_id: id договора клиента, для которого инициируется продажа
        :param account_id: id лицевого счета, для которого инициируется продажа
        :return: объект класса SaleProduct c заполненной базовой информацией
        """
        sale = SaleProduct()
        sale.client.user_id = user_id

        address_id = self.get_address_id(user_id)

        linked_persons = self.get_linked_person(user_id)
        if len(linked_persons) > 0:
            sale.linked_person_id = linked_persons[0]["linkedPerson"]["linkedPersonId"]
        else:
            sale.linked_person_id = self.make_linked_person(sale.date, user_id)
            self.add_linked_person_to_uds(user_id, sale.linked_person_id)

        self.add_inquiry_properties(user_id)

        sale.inquiry_id = self.register_inquiry(user_id, sale.linked_person_id, agreement_id, account_id)

        sale.commercial_order = self.get_commercial_order_id(sale.inquiry_id)

        sale.commercial_order_number = self.get_commercial_order_number(sale.inquiry_id)

        linked_objects = self.get_linked_objects(address_id, "regions")
        region_id = 0 if len(linked_objects) == 0 else linked_objects[0]["attributes"]["regionId"]

        sale.product_id = self.select_product_offer(address_id, sale.commercial_order, product_offering_id, region_id)
        return sale

    def get_sale_info(self, sale: SaleProduct, category: str) -> SaleProduct:
        """
        Метод для дополнения информации о продаже
        :param sale: объект класса SaleProduct, полученный из sale_prepare_and_add_product
        :param category: категория продажи продукта
        :return: объект класса SaleProduct
        """
        sale = self.get_subscriber_info(sale)
        if category == "internet":
            sale.product.internet_number = self.get_client_subscriber(subscription_id=sale.product.subs_id)[1]
        elif category == "mobile":
            sale.product.phone_number = self.get_client_subscriber(subscription_id=sale.product.subs_id)[1]
        return sale

    @allure.step("API: Продажа монопродукта B2C")
    def product_sale(
        self,
        user_id: int,
        product_offering_id: int = None,
        category: str = "mobile",
        agreement_id: int | None = None,
        account_id: int | None = None,
    ) -> Tuple[BaseClient, InfoAboutProduct]:
        """
        Метод для продажи продукта абоненту в категориях Мобильная связь и Интернет
        :param user_id: id клиента
        :param product_offering_id: id ПП, который нужно продать
        :param category: строка вида "mobile", "internet"
        :param agreement_id: id договора клиента, для которого нужно провести продажу
        :param account_id: id лицевого счета, для которого нужно провести продажу
        :return: объекты класса BaseUser, InfoAboutProduct
        возможно использование в виде product_sale(user_id, category="internet")
        """
        check_that(lambda: user_id is not None, UserIdNotFoundException, "Не передан id клиента")

        default_offering_ids = {"internet": 500004, "mobile": 500012}
        if not product_offering_id:
            product_offering_id = default_offering_ids[category]
        sale = self.sale_prepare_and_add_product(user_id, product_offering_id, agreement_id, account_id)

        if category == "mobile":
            self.resources_reserve(sale.product_id[0], sale.commercial_order)

        self.order_check(sale.commercial_order_number)

        if category == "internet":
            self.technical_solution_verifying(sale.commercial_order_number)

        self.connect_inquiry(sale.inquiry_id)

        self.get_sale_status(sale.commercial_order)

        sale = self.get_sale_info(sale, category)

        return sale.client, sale.product

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
