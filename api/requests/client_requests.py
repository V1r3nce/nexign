from dataclasses import dataclass
from typing import Tuple

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
)
from api.requests.address_requests import AddressRequests
from api.requests.base_requests import BaseRequests
from common.helpers.checker import wait_that
from common.helpers.data_generator import get_current_datetime_string
from common.helpers.env_helper import BASE_URL_API
from common.helpers.time_helpers import delay


@dataclass
class ClientInfo:
    user_id: int = 0
    agreement_id: int = 0
    agreement_number: int = 0
    account_id: int = 0
    account_number: int = 0


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
class SaleProduct:
    client: ClientInfo
    product: InfoAboutProduct
    commercial_order: int
    commercial_order_number: int
    inquiry_id: int
    product_id: list[int]
    linked_person_id: int
    date: str

    def __init__(self) -> None:
        self.client = ClientInfo()
        self.product = InfoAboutProduct()
        self.commercial_order = 0
        self.commercial_order_number = 0
        self.inquiry_id = 0
        self.product_id = [0]
        self.linked_person_id = 0
        self.date = get_current_datetime_string().replace(" ", "-").replace(".", "/")


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
    def inquiry_forward(self, id: int, body: dict) -> APIResponse:
        """
        Возвращает информацию о продвижении заявки
        :param id: id заявки
        :param body: dict тело заявки
        :return: ответ на запрос
        """
        return self.post(url=f"{BASE_URL_API}/openapi/v1/inquiries/{id}/forward", data=body)

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
    def register_inquiry(self, user_id: int, linked_person_id: int) -> int:
        """
        Создание заявки
        :param user_id: id клиента, созданного фикстурой create_user
        :param linked_person_id: id связанного лица из make_linked_person
        :return: inquiry_id идентификатор заявки
        """
        body_reg_inquiry = {
            "inquiry": {
                "topic": {"topicCode": "SALE_TOPIC"},
                "customProperties": [
                    {
                        "customPropertyDeclaration": {"customPropertyDeclarationCode": "saleAddAgreement"},
                        "type": "DICTIONARY",
                        "values": [{"itemCode": "AUTO"}],
                    },
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
                property["customPropertyDeclaration"]["customPropertyDeclarationCode"] == "commercialOrderId"
                and len(property["textValue"]) > 0
                for property in self.get_inquiry(inquiry_id).json()["customProperties"]
            ],
            timeout=30,
            sleep_seconds=2,
            exception=SearchCommercialOrderException,
            message="Поиск не нашел созданного КЗ",
        )
        custom_properties = self.get_inquiry(inquiry_id).json()["customProperties"]
        for property in custom_properties:
            if property["customPropertyDeclaration"]["customPropertyDeclarationCode"] == "commercialOrderId":
                return int(property["textValue"])
        raise CommercialOrderIdNotFoundException(f'Не найден коммерческий заказ "{inquiry_id}"')

    @allure.step("API: Получение идентификатора заявки коммерческого заказа")
    def get_commercial_order_number(self, inquiry_id: int) -> int:
        """
        Возвращает id заявки ком заказа
        :param inquiry_id: id заявки из register_inquiry
        :return: id заявки ком заказа
        """
        response_commercial_order = self.get_inquiry(inquiry_id).json()["customProperties"]
        for property in response_commercial_order:
            if property["customPropertyDeclaration"]["customPropertyDeclarationCode"] == "orderInquiryId":
                return int(property["textValue"])
        raise CommercialOrderNumberNotFoundException(f'Не найдена заявка коммерческого заказа "{inquiry_id}"')

    @allure.step("API: Добавление продука в заказ")
    def select_product_offer(self, address_id: int, commercial_order: int, product_offering_id: int) -> list[int]:
        """
        Возвращает id продукта выбранного ПП для проведения заявки
        :param address_id: id адреса клиента из get_address_id
        :param commercial_order: id ком заказа продажи продукта из get_commercial_order_id
        :param product_offering_id: id продуктового предложения, которое планируется продать
        :return: список id продуктов для подключения
        """
        body_prod_select = {
            "addProductsParameters": [
                {"productParameters": {"addressId": address_id, "productOfferingId": product_offering_id}}
            ],
            "operation": "CONNECT_INDEPENDENT_PRODUCT",
        }
        response_product = self.post(
            url=f"{BASE_URL_API}/openapi/v1/productManagement/commercialOrders/{commercial_order}/orderProducts/add/bulk",
            data=body_prod_select,
        )
        self.check_response_status(response_product, 200, "Не получен список продуктов")
        return [product["productId"] for product in response_product.json()["addedProducts"]]

    @allure.step("API: Бронирование ресурсов")
    def resources_reserve(self, product_id: int, commercial_order: int) -> None:
        """
        Бронирование ресурсов для продажи продукта
        :param product_id: id продукта, который хотим инстанцировать клиенту из select_product_offer
        :param commercial_order: id ком заказа продажи продукта из get_commercial_order_id
        Упадет с ошибкой, если бронировние не завершилось успешно
        """
        body_resources = {"orderProductId": product_id}
        response_resources = self.post(
            url=f"{BASE_URL_API}/ps/v1/tailored-rm/commercialOrders/{commercial_order}/orderResources/reserve",
            data=body_resources,
        )
        self.check_response_status(response_resources, 200, "Ресурсы не забронировались")

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
        Проверка технической возможности подключения продукта по параметра заявки
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
        body_connect = {"activity": {"activityCode": "AUTO_CREATE_AGR_ACC"}, "login": "Admin"}
        wait_that(
            lambda: self.inquiry_forward(inquiry_id, body_connect).status == 204,
            timeout=75,
            sleep_seconds=2,
            exception=InquiryConnectException,
            message="Ожидание заявки на подключение",
        )

    @allure.step("API: Ожидание выполнения заказа")
    def get_sale_status(self, commercial_order: int) -> None:
        """
        Метод для ожидания выполнения заявки
        :param commercial_order: id ком заказа продажи продукта из get_commercial_order_id
        Упадет с ошибкой, если продажа не завершилась успешно
        """
        wait_that(
            lambda: "COMPLETED"
            in self.get(
                url=f"{BASE_URL_API}/openapi/v1/productManagement/commercialOrders/{commercial_order}/commonInfo",
            ).json()["stage"]["code"],
            timeout=400,
            sleep_seconds=5,
            exception=SaleStatusException,
            message="Ожидание выполнения заявки",
        )

    @allure.step("API: Получение ЛС клиента")
    def get_client_account(self, user_id: int) -> Tuple[int, int]:
        """
        Метод для получения id ЛС, номера ЛС у клиента
        :param user_id: id клиента, созданного фикстурой create_user
        :return: accountNumber, accountId - номер ЛС, идентификатор ЛС
        """
        body_account = {"entity": {"code": "customer", "id": user_id}}
        response_account = self.post(
            url=f"{BASE_URL_API}/openapi/v1/customerManagement/accounts/search", data=body_account
        )
        self.check_response_status(response_account, 200, "Не получены данные об лицевых счетах")
        item = self.get_last_created_item_response(response_account.json()["items"])
        return item["accountNumber"], item["accountId"]

    @allure.step("API: Получение абонента клиента")
    def get_client_subscriber(self, user_id: int) -> Tuple[int, int]:
        """
        Метод для получения последнего по дате создания абонента у клиента
        :param: user_id: id клиента, созданного фикстурой create_user
        :return: subs_id, msisdn/internet - идентификатор абонента, номер телефона/интернета
        """
        body_subs = {"subscriptionInfoBaseFilter": {"customerId": user_id}}
        response_subs = self.post(
            url=f"{BASE_URL_API}/openapi/v1/subscriptionManagement/subscriptions/search", data=body_subs
        )
        self.check_response_status(response_subs, 200, "Не получены данные об абонентах")
        item = self.get_last_created_item_response(response_subs.json()["items"])
        return item["subscriptionId"], item["identification"]["identificationValue"]

    @allure.step("API: Получение информации о клиенте")
    def get_subscriber_info(self, sale: SaleProduct) -> SaleProduct:
        """
        Метод для заполнения информации абонента
        :param sale: объект класса SaleProduct
        :return: объект класса SaleProduct,
        """
        body_info_subs = {"params": {"limit": 100, "offset": 0}, "subscriptionId": sale.product.subs_id}
        response_info_subs = self.post(
            url=f"{BASE_URL_API}/openapi/v1/productManagement/products/searchBySubscription", data=body_info_subs
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
        sale.client.agreement_id = subs_item["payerInformation"]["agreement"]["agreementId"]
        sale.client.agreement_number = subs_item["payerInformation"]["agreement"]["agreementNumber"]
        return sale

    def sale_prepare_and_add_product(self, user_id: int, product_offering_id: int) -> SaleProduct:
        """
        Метод для подготовки продажи и проведения обязательных шагов
        :param user_id: id клиента, для которого инициируется продажа
        :param product_offering_id: id продуктового предложения, которое планируется продать
        :return: объект класса SaleProduct c заполненной базовой информацией
        """
        sale = SaleProduct()
        sale.client.user_id = user_id

        address_id = self.get_address_id(user_id)

        sale.linked_person_id = self.make_linked_person(sale.date, user_id)

        self.add_linked_person_to_uds(user_id, sale.linked_person_id)

        self.add_inquiry_properties(user_id)

        sale.inquiry_id = self.register_inquiry(user_id, sale.linked_person_id)

        sale.commercial_order = self.get_commercial_order_id(sale.inquiry_id)

        sale.commercial_order_number = self.get_commercial_order_number(sale.inquiry_id)

        sale.product_id = self.select_product_offer(address_id, sale.commercial_order, product_offering_id)
        return sale

    def get_sale_info(self, sale: SaleProduct, category: str) -> SaleProduct:
        """
        Метод для дополнения информации о продаже
        :param sale: объект класса SaleProduct, полученный из sale_prepare_and_add_product
        :param category: категория продажи продукта
        :return: объект класса SaleProduct
        """
        sale.client.account_number, sale.client.account_id = self.get_client_account(sale.client.user_id)

        if category == "internet":
            sale.product.subs_id, sale.product.internet_number = self.get_client_subscriber(sale.client.user_id)
        elif category == "mobile":
            sale.product.subs_id, sale.product.phone_number = self.get_client_subscriber(sale.client.user_id)

        sale = self.get_subscriber_info(sale)
        return sale

    @allure.step("API: Продажа монопродукта B2C")
    def product_sale(
        self, user_id: int, product_offering_id: int = None, category: str = "mobile"
    ) -> Tuple[ClientInfo, InfoAboutProduct]:
        """
        Метод для продажи продукта абоненту в категориях Мобильная связь и Интернет
        :param user_id: id клиента, созданного фикстурой create_user
        :param product_offering_id: id ПП, который нужно продать
        :param category: строка вида "mobile", "internet"
        :return: объекты класса ClientInfo, InfoAboutProduct
        возможно использование в виде product_sale(user_id, category="internet")
        """
        default_offering_ids = {"internet": 500004, "mobile": 500012}
        if not product_offering_id:
            product_offering_id = default_offering_ids[category]
        sale = self.sale_prepare_and_add_product(user_id, product_offering_id)

        self.resources_reserve(sale.product_id[0], sale.commercial_order)

        self.order_check(sale.commercial_order_number)

        if category == "internet":
            self.technical_solution_verifying(sale.commercial_order_number)

        self.connect_inquiry(sale.inquiry_id)

        self.get_sale_status(sale.commercial_order)

        sale = self.get_sale_info(sale, category)

        return sale.client, sale.product
