from random import choice
from typing import List, Tuple

import allure
from playwright.sync_api import APIRequestContext, APIResponse

from api.base_requests import BaseRequests
from api.exceptions import (
    CommercialOrderIdNotFoundException,
    CommercialOrderNumberNotFoundException,
    InquiryConnectException,
    InquirySearchException,
    InquiryTechnicalSolutionException,
    SaleStatusException,
    SearchCommercialOrderException,
    SubscriptionNotFoundException,
)
from api.lis_requests.phone_numbers import PhoneNumberData, PhoneNumbersRequests
from api.lis_requests.sim_cards import SimCardData, SimCardsRequests
from api.nbss.address_requests import AddressRequests
from api.nbss.inquiry_requests import AppealRequests
from common.helpers.checker import assert_that, check_that, wait_that
from common.helpers.data_generator import get_current_datetime_string
from common.helpers.env_helper import BASE_URL_API
from models.context import test_context
from models.inquiry import InquiryInfo
from models.user import BaseClient


class ClientInquiriesRequests(BaseRequests):
    def __init__(self, api_request_auth_context: APIRequestContext):
        super().__init__(api_request_auth_context)
        self.inquiry_api = AppealRequests(api_request_auth_context)

    @allure.step("API: Получение информации о заявке по идентификатору")
    def get_inquiry_info(self, inquiry_id: int) -> APIResponse:
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
        self,
        user_id: int,
        linked_person_id: int | None,
        agreement_id: int | None,
        account_id: int | None,
        need_spd: bool,
    ) -> int:
        """
        Создание заявки
        :param user_id: id клиента, созданного фикстурой create_user
        :param linked_person_id: id связанного лица из make_linked_person
        :param agreement_id: id договора клиента
        :param account_id: id лицевого счета
        :param need_spd: флаг отвечающий за Формирование комплектов РПД
        :return: inquiry_id идентификатор заявки
        """
        body_reg_inquiry = {
            "inquiry": {
                "topic": {"topicCode": "SALE_TOPIC"},
                "customProperties": [
                    self._get_inquiry_property("inqrLinkedPerson", "DICTIONARY", []),
                ],
                "email": "mail@mail.ru",
            },
            "contact": {"customer": {"customerId": user_id}},
        }

        if linked_person_id is not None:
            body_reg_inquiry["inquiry"]["customProperties"][0]["values"] = [{"itemCode": linked_person_id}]

        if agreement_id is not None and account_id is not None:
            body_reg_inquiry["inquiry"]["customProperties"].extend(
                [
                    self._get_inquiry_property("saleAgreement", "DICTIONARY", [{"itemCode": str(agreement_id)}]),
                    self._get_inquiry_property("saleAccount", "DICTIONARY", [{"itemCode": str(account_id)}]),
                    self._get_inquiry_property("saleAddAgreementAdd", "DICTIONARY", [{"itemCode": "CREATE_AUTO"}]),
                ]
            )
        else:
            body_reg_inquiry["inquiry"]["customProperties"].extend(
                [
                    self._get_inquiry_property("saleAgreement", "DICTIONARY", []),
                    self._get_inquiry_property("saleAddAccount", "DICTIONARY", [{"itemCode": "AUTO"}]),
                    self._get_inquiry_property("saleAddAgreementAdd", "DICTIONARY", [{"itemCode": "CREATE_AUTO"}]),
                ]
            )

        if need_spd:
            body_reg_inquiry["inquiry"]["customProperties"].extend(
                [
                    self._get_inquiry_property("needSPD", "DICTIONARY", [{"itemCode": "CREATE_AUTO"}]),
                    self._get_inquiry_property("deliveryTypeSPD", "DICTIONARY", [{"itemCode": "email"}]),
                    self._get_inquiry_property("emailForSendSPD", "STRING", stringValue="mail@mail.ru"),
                ]
            )
        else:
            body_reg_inquiry["inquiry"]["customProperties"].append(
                self._get_inquiry_property("needSPD", "DICTIONARY", [{"itemCode": "NOT_CREATE"}])
            )

        response_reg_inquiry = self.post(
            url=f"{BASE_URL_API}/openapi/v1/inquiries",
            data=body_reg_inquiry,
        )
        self.check_response_status(response_reg_inquiry, 201, "Заявка не создалась")
        inquiry_id = response_reg_inquiry.json()["inquiryId"]
        test_context.inquiry.id = inquiry_id
        return inquiry_id

    @staticmethod
    def _get_inquiry_property(code: str, prop_type: str, values: list = None, **kwargs: dict) -> dict:
        """
        Вспомогательный метод для создания кастомных свойств.
        :param code: код свойства (customPropertyDeclarationCode)
        :param prop_type: тип свойства (например, DICTIONARY, STRING)
        :param values: список значений или пустой список
        :param kwargs: дополнительные параметры (например, stringValue для типа STRING)
        :return: готовый объект свойства
        """
        prop = {
            "customPropertyDeclaration": {"customPropertyDeclarationCode": code},
            "type": prop_type,
        }

        if values is not None:
            prop["values"] = values
        if "stringValue" in kwargs:
            prop["stringValue"] = kwargs["stringValue"]

        return prop

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
                for custom_property in self.get_inquiry_info(inquiry_id).json()["customProperties"]
            ],
            timeout=60,
            sleep_seconds=2,
            exception=SearchCommercialOrderException,
            message="Поиск не нашел созданного КЗ",
        )
        custom_properties = self.get_inquiry_info(inquiry_id).json()["customProperties"]
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
        response_commercial_order = self.get_inquiry_info(inquiry_id).json()["customProperties"]
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
        :param product_offering_id: id продуктового предложения
        :param region_id: id региона
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
    def get_sim_cards_list(self, switch_id: int | None = None) -> APIResponse:
        """
        Получение списка sim-карт
        :param switch_id: идентификатор коммутатора (например, Коммутатор_DEF - 100001)
        :return: ответ сервиса, содержащий информацию по sim-картам
        """
        request_body = {
            "isReserved": False,
            "macroRegionIds": [999],
            "SIMCardTechnologyIds": [1],
            "stateIds": [9],
            "statusIds": [1],
        }
        if switch_id is not None:
            request_body["equipmentId"] = switch_id
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
        self.check_response_status(response, 200, "Невозможно забронировать номер")

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
        sims = self.get_sim_cards_list(switch_id=100001)
        sim_list = sim_request.get_sim_cards_data(sims)
        assert_that(lambda: len(sim_list) != 0, "Нет симок для бронирования")
        # Choice используется для того, чтобы, если два теста одновременно будут исполнять этот кусок кода, максимизировать шанс того, что они выберут разные ресурсы.
        # Таким образом мы пытаемся избежать ситуации когда они попытаются забронировать один и тот же ресурс и один из тестов зафейлится
        chosen_sim = choice(sim_list)
        self.lock_sim_card(product_id, commercial_order, chosen_sim, order_sim)
        numbers = self.get_phone_list(chosen_sim.switchId, number_request.macro_region_id)
        numbers_list = number_request.get_numbers_data(numbers)
        assert_that(lambda: len(numbers_list) != 0, "Нет номеров для бронирования")
        self.lock_number(product_id, commercial_order, choice(numbers_list), order_number, chosen_sim.switchId)

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

    @allure.step("API: Ожидание выполнения заявок")
    def wait_sale_done(self, commercial_order: int | List[int], inquiry_id: int | List[int]) -> None:
        """
        Метод для ожидания выполнения заявки
        :param commercial_order: id ком заказа продажи продукта из get_commercial_order_id. или список таких id
        :param inquiry_id: id заявки продажи. или список таких id
        Упадет с ошибкой, если продажа не завершилась успешно
        """
        sale_timeout = 400
        commercial_order_list = [commercial_order] if isinstance(commercial_order, int) else commercial_order
        inquiry_list = [inquiry_id] if isinstance(inquiry_id, int) else inquiry_id

        check_that(
            lambda: len(commercial_order_list) == len(inquiry_list),
            ValueError,
            "Количество коммерческих заказов и заявок не совпадает",
        )

        wait_that(
            lambda: all(
                "COMPLETED" in self.get_commercial_order_stage(com_order)["code"]
                or self.inquiry_api.get_appeal_status(inquiry) == "CLOSE"
                for com_order, inquiry in zip(commercial_order_list, inquiry_list)
            ),
            timeout=sale_timeout,
            sleep_seconds=5,
            exception=SaleStatusException,
            message=f"Заявка/и {inquiry_id} не завершились за {sale_timeout} секунд.",
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
        check_that(lambda: item != {}, SubscriptionNotFoundException, "Не найден абонент клиента")
        return item["subscriptionId"], item["identification"]["identificationValue"]

    @allure.step("API: Получение информации о первом элементе заказа")
    def get_subscriber_info(self, inquiry: InquiryInfo) -> InquiryInfo:
        """
        Метод для заполнения информации абонента
        :param inquiry: информация о заявке
        :return: информация о заявке
        """
        body_info_subs = {"params": {"limit": 100, "offset": 0}}
        response_info_subs = self.post(
            url=f"{BASE_URL_API}/openapi/v1/productManagement/commercialOrders/{inquiry.commercial_order}/orderProducts/search",
            data=body_info_subs,
        )
        self.check_response_status(response_info_subs, 200, "Не получены данные о подписке абонента")
        subs_item = response_info_subs.json()["items"][0]
        inquiry.product.product_name = subs_item["name"]
        inquiry.product.total_amount = float(subs_item["totalPrice"]["amount"])
        for part in subs_item["totalPrice"]["includedParts"]:
            if part["priceTypeCode"] == "FeeProdOfferingPrice":
                inquiry.product.one_time_payment = float(part["amount"])
            if part["priceTypeCode"] == "RecurringChargeProdOfferPriceCharge":
                inquiry.product.subscription_fee = float(part["amount"])
        agreement_id = subs_item["payerInformation"]["agreement"]["agreementId"]
        agreement_number = subs_item["payerInformation"]["agreement"]["agreementNumber"]
        test_context.client.add_agreement(agreement_id, agreement_number)
        test_context.client.get_agreement(agreement_id).add_account(
            subs_item["payerInformation"]["account"]["accountId"],
            subs_item["payerInformation"]["account"]["accountNumber"],
        )
        inquiry.product.subs_id = int(subs_item["productPrototypes"][0]["holderPrototype"]["holderMapping"]["holderId"])
        return inquiry

    def sale_prepare_and_add_product(
        self,
        client: BaseClient,
        inquiry: InquiryInfo,
        need_spd: bool,
        need_create_link_person: bool | None,
    ) -> InquiryInfo:
        """
        Метод для подготовки продажи и проведения обязательных шагов
        :param client: информация о клиенте
        :param inquiry: информация о заявке
        :param need_spd: флаг отвечающий за Формирование комплектов РПД
        :param need_create_link_person: флаг, отвечающий за создание связанного лица
        :return: объект класса SaleProduct c заполненной базовой информацией
        """
        region_id = 100004

        address_id = self.get_address_id(client.user_id)

        if need_create_link_person:
            linked_persons = self.get_linked_person(client.user_id)
            if len(linked_persons) > 0:
                inquiry.linked_person_id = linked_persons[0]["linkedPerson"]["linkedPersonId"]
            else:
                inquiry.linked_person_id = self.make_linked_person(inquiry.date, client.user_id)
                self.add_linked_person_to_uds(client.user_id, inquiry.linked_person_id)
        else:
            inquiry.linked_person_id = None

        self.add_inquiry_properties(client.user_id)

        inquiry.id = self.register_inquiry(
            client.user_id, inquiry.linked_person_id, inquiry.product.agreement_id, inquiry.product.account_id, need_spd
        )

        inquiry.commercial_order = self.get_commercial_order_id(inquiry.id)

        inquiry.commercial_order_number = self.get_commercial_order_number(inquiry.id)

        linked_objects = self.get_linked_objects(address_id, "regions")
        if len(linked_objects) != 0:
            region_id = linked_objects[0]["attributes"]["regionId"]

        inquiry.product_id = self.select_product_offer(
            address_id, inquiry.commercial_order, inquiry.product.product_offering_id, region_id
        )
        return inquiry

    def get_sale_info(self, inquiry: InquiryInfo, category: str) -> InquiryInfo:
        """
        Метод для дополнения информации о продаже
        :param inquiry: информация о заявке
        :param category: категория продажи продукта
        :return: объект класса SaleProduct
        """
        inquiry = self.get_subscriber_info(inquiry)
        if category == "internet":
            inquiry.product.internet_number = self.get_client_subscriber(subscription_id=inquiry.product.subs_id)[1]
        elif category == "mobile":
            inquiry.product.phone_number = self.get_client_subscriber(subscription_id=inquiry.product.subs_id)[1]
        return inquiry

    @allure.step("API: Продажа монопродукта B2C")
    def _product_sale(
        self,
        client: BaseClient | None,
        inquiry: InquiryInfo,
        need_spd: bool = False,
        need_create_link_person: bool | None = True,
    ) -> InquiryInfo:
        """Внутренний метод для продажи продукта. Создан для уменьшения дублирования кода"""
        if not client:
            client = test_context.client
        else:
            test_context.client = client

        inquiry = self.sale_prepare_and_add_product(client, inquiry, need_spd, need_create_link_person)

        if inquiry.product.category == "mobile":
            self.resources_reserve(inquiry.product_id[0], inquiry.commercial_order)

        self.order_check(inquiry.commercial_order_number)

        if inquiry.product.category == "internet":
            self.technical_solution_verifying(inquiry.commercial_order_number)

        self.connect_inquiry(inquiry.id)
        return inquiry

    @allure.step("API: Продажа продукта")
    def product_sale(
        self,
        client: BaseClient = None,
        inquiry: InquiryInfo = None,
        need_spd: bool = False,
        need_create_link_person: bool | None = True,
    ) -> InquiryInfo:
        """
        Метод для продажи продукта абоненту в категориях Мобильная связь и Интернет.
        :param client: информация о клиенте. Если не передать, то берет из контекста
        :param inquiry: информация о заявке. Если не передать, то берет из контекста
        :param need_spd: флаг, отвечающий за Формирование комплектов РПД
        :param need_create_link_person: флаг, отвечающий за создание связанного лица
        :return: информация о заявке
        """
        if not inquiry:
            inquiry = test_context.inquiry
        else:
            test_context.inquiry = inquiry

        inquiry = self._product_sale(client, inquiry, need_spd, need_create_link_person)

        self.wait_sale_done(inquiry.commercial_order, inquiry.id)
        inquiry = self.get_sale_info(inquiry, inquiry.product.category)
        inquiry.product.product_id = inquiry.product_id[0]

        return inquiry

    @allure.step("API: Продажа нескольких продуктов на один ЛС и договор")
    def products_sale(
        self,
        inquiry_list: List[InquiryInfo] | None = None,
        client: BaseClient = None,
        need_spd: bool = False,
        need_create_link_person: bool | None = True,
    ) -> List[InquiryInfo]:
        """Продажа нескольких продуктов на один ЛС и договор. По умолчанию - мобильная связь и интернет. Но если передать список заявок, то будет брать от туда.
        :param inquiry_list: Список информаций о заявках. Если не передать, то берет из контекста
        :param client: информация о клиенте. Если не передать, то берет из контекста
        :param need_spd: флаг, отвечающий за Формирование комплектов РПД
        :param need_create_link_person: флаг, отвечающий за создание связанного лица
        :return: объекты класса BaseUser, InfoAboutProduct"""
        if inquiry_list:
            test_context.inquiry_list = inquiry_list

        sales = [
            self._product_sale(client, inquiry, need_spd, need_create_link_person)
            for inquiry in test_context.inquiry_list
        ]

        self.wait_sale_done([sale.commercial_order for sale in sales], [sale.id for sale in sales])

        for sale in sales:
            sale = self.get_sale_info(sale, sale.product.category)
            sale.product.product_id = sale.product_id[0]

        return sales

    @allure.step("API: Получение заявок клиента по теме")
    def get_inquiry_by_topic(self, user_id: int, topic_name: str) -> list[int]:
        response = self.post(
            url=f"{BASE_URL_API}/openapi/v1/customers/{user_id}/inquiries/search?sort=inquiryId&limit=60&offset=0&useTemplate=true"
        )
        self.check_response_status(response, 200, "Не найдено заявок")
        res = []
        for item in response.json()["items"]:
            if item["topic"]["name"] == topic_name:
                res.append(item["inquiryId"])
        return res

    @allure.step("API: Получение заявок клиента")
    def get_inquiries(self, user_id: int) -> list[int]:
        response = self.post(
            url=f"{BASE_URL_API}/openapi/v1/customers/{user_id}/inquiries/search?sort=inquiryId&limit=60&offset=0&useTemplate=true"
        )
        self.check_response_status(response, 200, "Не найдено заявок")
        return [item["inquiryId"] for item in response.json()["items"]]

    @allure.step("API: Получение {seq_number} заявки у клиента")
    def get_nth_inquiry(self, user_id: int, seq_number: int) -> int:
        wait_timeout = 10
        wait_that(
            lambda: len(self.get_inquiries(user_id)) >= seq_number,
            timeout=wait_timeout,
            sleep_seconds=5,
            exception=InquirySearchException,
            message=f"Количество заявок у клиента {user_id} не стало равно {seq_number} за {wait_timeout}",
        )
        return self.get_inquiries(user_id)[seq_number - 1]
