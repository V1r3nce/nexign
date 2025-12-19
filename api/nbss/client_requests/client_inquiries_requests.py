from random import choice
from typing import Any, List, Tuple

import allure
from playwright.sync_api import APIResponse

from api.base_requests import BaseRequests
from api.exceptions import (
    AdditionalProductCantBeAdded,
    CommercialOrderIdNotFoundException,
    CommercialOrderNumberNotFoundException,
    InquirySearchException,
    InquiryTechnicalSolutionException,
    SubscriptionNotFoundException,
)
from api.lis_requests.equipment import EquipmentRequests
from api.lis_requests.phone_numbers import PhoneNumberData, PhoneNumbersRequests
from api.lis_requests.sim_cards import SimCardData, SimCardsRequests
from api.nbss.address_requests import AddressRequests
from api.nbss.inquiry_requests import AppealRequests
from common.enums.user import User
from common.helpers.checker import assert_that, check_that, wait_that
from common.helpers.data_generator import get_current_datetime_string
from common.helpers.env_helper import BASE_URL_API
from models.context import test_context
from models.inquiry import InquiryInfo
from models.product import AdditionalProduct, MainProduct, Resources, get_filled_attributes
from models.user import BaseClient, EntrepreneurClient, IndividualClient, OrganizationClient


class ClientInquiriesRequests(BaseRequests):
    def __init__(self) -> None:
        super().__init__()
        self.inquiry_api = AppealRequests()

        test_context.switch_api_context_to_user(User.ADMIN)

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
    def _get_commercial_order_stage(self, commercial_order: int) -> dict:
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
    def _get_address_id(self, user_id: int) -> int:
        """
        Возвращает id адреса клиента
        :param user_id: id клиента, созданного фикстурой create_user
        :return: id адреса
        """
        api_addresses = AddressRequests()
        response_address = api_addresses.get_client_addresses(user_id)
        return response_address.json()["items"][0]["externalAddressId"]

    @allure.step("API: Получение объектов из классификаторов {classifiers}, связанные с адресным объектом")
    def _get_linked_objects(self, classifiers: str) -> list:
        """
        Возвращает объекты из указанных классификаторов, связанные с заданным адресным объектом или его родительскими объектами
        :param classifiers: коды классификаторов, связанные объекты из которых будут возвращены
        :return: список объектов
        """
        response = self.get(
            url=f"{BASE_URL_API}/openapi/v1/locationManagement/addresses/{test_context.client.inquiry.address_id}/linkedObjects?classifiers={classifiers}"
        )
        self.check_response_status(response, 200, "Невозможно получить связанные объекты")
        return response.json()["linkedObjects"]

    @allure.step("API: Получение связанных лиц клиента")
    def _get_linked_person(self, user_id: int) -> list:
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
    def _make_linked_person(self, date: str, user_id: int) -> int:
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
    def _add_linked_person_to_uds(self, user_id: int, linked_person_id: int) -> None:
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
    def _add_inquiry_properties(self, user_id: int) -> None:
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
    def _register_inquiry(self, need_spd: bool) -> int:
        """
        Создание заявки
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
            "contact": {"customer": {"customerId": test_context.client.user_id}},
        }
        if isinstance(test_context.client, OrganizationClient):
            body_reg_inquiry["inquiry"]["customProperties"].extend(
                [
                    self._get_inquiry_property("saleAddKp", "DICTIONARY", [{"itemCode": "NOT_CREATE"}]),
                ]
            )
        if test_context.client.inquiry.linked_person_id is not None:
            body_reg_inquiry["inquiry"]["customProperties"][0]["values"] = [
                {"itemCode": test_context.client.inquiry.linked_person_id}
            ]
        if (
            test_context.client.agreements
            and test_context.client.agreements[0].id is not None
            and test_context.client.agreements[0].accounts
            and test_context.client.agreements[0].accounts[0].id is not None
        ):
            body_reg_inquiry["inquiry"]["customProperties"].extend(
                [
                    self._get_inquiry_property(
                        "saleAgreement",
                        "DICTIONARY",
                        [{"itemCode": str(test_context.client.agreements[0].id)}],
                    ),
                    self._get_inquiry_property(
                        "saleAccount",
                        "DICTIONARY",
                        [{"itemCode": str(test_context.client.agreements[0].accounts[0].id)}],
                    ),
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
        test_context.client.inquiry.id = inquiry_id
        return inquiry_id

    @staticmethod
    def _get_inquiry_property(code: str, prop_type: str, values: list = None, **kwargs: Any) -> dict:
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
    def _get_commercial_order_id(self, inquiry_id: int) -> int:
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
            timeout=75,
            sleep_seconds=7.5,
            exception=AssertionError,
            message="Поиск не нашел созданного КЗ",
        )
        custom_properties = self.get_inquiry_info(inquiry_id).json()["customProperties"]
        for custom_property in custom_properties:
            if custom_property["customPropertyDeclaration"]["customPropertyDeclarationCode"] == "commercialOrderId":
                return int(custom_property["textValue"])
        raise CommercialOrderIdNotFoundException(f'Не найден коммерческий заказ "{inquiry_id}"')

    @allure.step("API: Получение идентификатора заявки коммерческого заказа")
    def _get_commercial_order_number(self, inquiry_id: int) -> int:
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
    def _select_product_offer(self, product: MainProduct | AdditionalProduct) -> list[int]:
        """
        Возвращает id продукта выбранного ПП для проведения заявки
        :param product: продукт
        :return: список id продуктов для подключения
        """
        body_prod_select = {
            "addProductsParameters": [
                {
                    "productParameters": {
                        "addressId": test_context.client.inquiry.address_id,
                        "productOfferingId": product.product_offering_id,
                        "regionId": test_context.client.inquiry.region_id,
                    }
                }
            ],
            "operation": "CONNECT_ADDITIONAL_FOR_ORDER_PRODUCT"
            if isinstance(product, AdditionalProduct)
            else "CONNECT_INDEPENDENT_PRODUCT",
        }
        if isinstance(product, AdditionalProduct):
            body_prod_select.update(
                {"mainProduct": {"mainOrderProductId": test_context.client.inquiry.product.product_id}}  # type: ignore
            )
        if "equipment" in product.category:
            body_prod_select["addProductsParameters"][0]["productParameters"].update(
                {
                    "characteristics": [
                        {
                            "code": "typeOfSale",
                            "values": [
                                {
                                    "code": "Rent" if product.category == "equipment_rent" else "Sale",
                                    "name": "Аренда" if product.category == "equipment_rent" else "Продажа",
                                }
                            ],
                            "valueType": "dictionary",
                        }
                    ]
                }
            )
        response_product = self.post(
            url=f"{BASE_URL_API}/openapi/v1/productManagement/commercialOrders/{test_context.client.inquiry.commercial_order}/orderProducts/add/bulk",
            data=body_prod_select,
        )
        self.check_response_status(response_product, 200, "Не получен список продуктов")
        return [product["productId"] for product in response_product.json()["addedProducts"]]

    @allure.step("API: Получение информации о продукте в коммерческом заказе")
    def get_order_product_info(self, product_id: int) -> dict:
        """
        Получение информации по продукту коммерческого заказа из csm.
        :param product_id: id продукта, который хотим инстанцировать клиенту из select_product_offer
        :return: json словарь
        """
        response = self.get(
            url=f"{BASE_URL_API}/openapi/v1/productManagement/commercialOrders/{test_context.client.inquiry.commercial_order}/orderProducts/{product_id}"
        )
        self.check_response_status(response, 200, "Невозможно получить информацию о продукте в коммерческом заказе")
        return response.json()

    @allure.step("API: Получение информации по ресурсам, которые нужно забронировать")
    def get_order_resource_ids(self, product_id: int) -> list:
        """
        Получение id ресурсов продукта, которые необходимо заполнить.
        :param product_id: id продукта, который хотим инстанцировать клиенту из select_product_offer
        :return: список id ресурсов
        """
        resource_list = []
        for parameter in self.get_order_product_info(product_id)["orderCustomerFacingServices"]:
            if len(parameter["orderResources"]) > 0:
                for resource in parameter["orderResources"]:
                    resource_list.append(resource)
        for resource in self.get_order_product_info(product_id)["orderResources"]:
            if resource["resourceType"] not in resource_list:
                resource_list.append(resource)
        return [
            {"resource_type": resource["resourceType"], "resource_id": resource["orderResourceId"]}
            for resource in resource_list
        ]

    @allure.step("API: Получение кода номенклатуры для оборудования")
    def get_nomenclature(self, product_id: int) -> str:
        """
        Получение названия номенклатуры оборудования, необходимой для продукта.
        :param product_id: id продукта, который хотим инстанцировать клиенту из select_product_offer
        :return: строка - название
        """
        characteristics = self.get_order_product_info(product_id)["characteristics"]
        for characteristic in characteristics:
            if characteristic["code"] == "itemCode":
                return characteristic["values"][0]
        raise AssertionError("Не получен код номенклатуры")

    @allure.step("API: Получение SIM карт доступных для бронирования")
    def _get_sim_cards_list(self, switch_id: int | None = None) -> APIResponse:
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
    def _reserve_sim_card(self, product_id: int, sim_card: SimCardData, order_resource_id: int) -> None:
        """
        Бронирование sim-карты телефона
        :param product_id: id продукта, который хотим инстанцировать клиенту из select_product_offer
        :param sim_card: объект класса. В нем хранится информация о сущности, которую хотим забронировать
        :param order_resource_id: id ресурса продукта, который бронируем
        Упадет с ошибкой, если бронировние не завершилось успешно
        """
        request_body = {
            "commercialOrderId": test_context.client.inquiry.commercial_order,
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
    def _get_phone_list(self, switch_id: int, standard_id: int, macro_region_id: int, is_type_def: bool) -> APIResponse:
        """
        Получение списка номеров телефонов
        :param switch_id: id коммутатора
        :param standard_id: id стандарта номера
        :param macro_region_id: id макро региона
        :return: ответ сервиса, содержащий информацию по номерам
        """
        request_body = {
            "equipmentFilters": {"equipmentIds": [switch_id], "standardIds": [standard_id]},
            "isReserved": False,
            "isTypeDef": is_type_def,
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
            url=f"{BASE_URL_API}/openapi/v1/logicalResources/phoneNumbers/search?fields=MSISDN,numberClass(numberClassId,name),type(name),switch(equipmentId,name)&sort=MSISDN&limit=60&offset=0",
            data=request_body,
        )
        self.check_response_status(response, 200, "Невозможно получить список доступных номеров телефонов")
        return response

    @allure.step("API: Бронирование MSISDN")
    def _reserve_number(
        self,
        product_id: int,
        phone_number: PhoneNumberData,
        order_resource_id: int,
        switch_id: int,
    ) -> None:
        """
        Бронирование номера телефона
        :param product_id: id продукта, который хотим инстанцировать клиенту из select_product_offer
        :param phone_number: объект класса. В нем хранится информация о сущности, которую хотим забронировать
        :param order_resource_id: id ресурса продукта, который бронируем
        :param switch_id: id коммутатора
        Упадет с ошибкой, если бронировние не завершилось успешно
        """
        request_body = {
            "commercialOrderId": test_context.client.inquiry.commercial_order,
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

    @allure.step("API: Бронирование серийного номера оборудования")
    def _reserve_equipment(self, product_id: int, order_resource_id: int, serial_number: int, nomenclature: str) -> None:
        """
        Бронирование серийного номера оборудования
        :param product_id: id продукта, который хотим инстанцировать клиенту из select_product_offer
        :param order_resource_id: id ресурса продукта, который бронируем
        :param serial_number: серийный номер оборудования, который бронируем
        :param nomenclature: название номенклатуры оборудования
        Упадет с ошибкой, если бронировние не завершилось успешно
        """
        request_body = {
            "commercialOrderId": test_context.client.inquiry.commercial_order,
            "fillSource": "WIM",
            "hasLinkedResources": False,
            "orderProductId": product_id,
            "partnerPointId": test_context.client.inquiry.product.partner_point_id,
            "resources": [
                {
                    "fillCharacteristics": [
                        {"code": "serialNumber", "type": "string", "values": [f"{serial_number}"]},
                        {"code": "lockId", "type": "string", "values": []},
                        {"code": "itemCode", "type": "string", "values": [nomenclature]},
                    ],
                    "itemCode": nomenclature,
                    "orderResourceIds": [order_resource_id],
                }
            ],
        }
        response = self.post(
            url=f"{BASE_URL_API}/openapi/v1/tailored_nbss/resources/equipment/lock/bulk",
            data=request_body,
        )
        self.check_response_status(response, 200, "Невозможно забронировать оборудование по серийному номеру")

    def _reserve_ip_address(self, order_resource_id: int) -> None:
        """
        Внутренний метод для бронирования IP адреса
        :param order_resource_id: id ресурса продукта, который бронируем
        Упадет с ошибкой, если бронировние не завершилось успешно
        """
        check_that(
            lambda: test_context.client.apn is not None and len(test_context.client.apn.free_ip_list) > 0,
            ValueError,
            "Список доступных IP адресов пуст",
        )
        chosen_ip = test_context.client.apn.pop_random()
        payload = {
            "commercialOrderId": test_context.client.inquiry.commercial_order,
            "fillSource": "LIS",
            "orderProductId": test_context.client.inquiry.product.product_id,
            "resources": [
                {
                    "fillCharacteristics": [
                        {"code": "APN", "type": "string", "values": [test_context.client.apn.name]},
                        {"code": "IPAddress", "type": "string", "values": [chosen_ip.address]},
                        {"code": "IPAddressId", "type": "long", "values": [chosen_ip.id]},
                        {"code": "isDynamicIP", "type": "boolean", "values": [False]},
                    ],
                    "orderResourceIds": [order_resource_id],
                }
            ],
        }
        response = self.post(f"{BASE_URL_API}/openapi/v1/tailored_nbss/resources/accessPoint/lock/bulk", data=payload)
        self.check_response_status(response, 200, "Ошибка бронирования IP адреса")

    def _get_order_resources(self, product: MainProduct | AdditionalProduct) -> None:
        """
        Внутренний метод для заполнения id ресурсов бронирования коммерческого заказа.
        :param product: Продукт, который хотим добавить клиенту из select_product_offer.
        """
        order_resource_list = self.get_order_resource_ids(product.product_id)
        if len(order_resource_list) > 0:
            product.resources = Resources()
            for order_resource in order_resource_list:
                match order_resource["resource_type"]:
                    case "SIMCard":
                        product.resources.sim_card_id = order_resource["resource_id"]
                    case "defPhoneNumber":
                        product.resources.phone_number = order_resource["resource_id"]
                    case "equipment":
                        product.resources.equipment = order_resource["resource_id"]
                    case "accessPoint":
                        product.resources.apn = order_resource["resource_id"]
                    case "abcPhoneNumber":
                        product.resources.city_phone_number = order_resource["resource_id"]

    @allure.step("API: Бронирование ресурсов")
    def _resources_reserve(self, product: MainProduct | AdditionalProduct) -> None:
        """
        Бронирование ресурсов для продажи продукта, если ресурсы были найдены.
        :param product: продукт, который хотим добавить клиенту из select_product_offer.
        Упадет с ошибкой, если бронирование не завершилось успешно.
        """
        self._get_order_resources(product)
        product_id = product.product_id
        chosen_sim = None
        if product.resources:
            for resource in get_filled_attributes(product.resources):
                match resource:
                    case "sim_card_id":
                        sim_request = SimCardsRequests()
                        sims = self._get_sim_cards_list(switch_id=test_context.client.inquiry.product.switch_id)
                        sim_list = sim_request.get_sim_cards_data(sims)
                        assert_that(lambda: len(sim_list) != 0, "Нет симок для бронирования")
                        # Choice используется для того, чтобы, если два теста одновременно будут исполнять этот кусок кода, максимизировать шанс того, что они выберут разные ресурсы.
                        # Таким образом мы пытаемся избежать ситуации когда они попытаются забронировать один и тот же ресурс и один из тестов зафейлится
                        chosen_sim = choice(sim_list)
                        self._reserve_sim_card(product_id, chosen_sim, product.resources.sim_card_id)
                    case "phone_number":
                        number_request = PhoneNumbersRequests()
                        if chosen_sim is not None:
                            switch_id = chosen_sim.switchId
                        else:
                            switch_id = test_context.client.inquiry.product.switch_id
                        numbers = self._get_phone_list(
                            switch_id=switch_id,
                            standard_id=test_context.client.inquiry.product.standard_id,
                            macro_region_id=number_request.macro_region_id,
                            is_type_def=True,
                        )
                        numbers_list = number_request.get_numbers_data(numbers)
                        assert_that(lambda: len(numbers_list) != 0, "Нет номеров для бронирования")
                        self._reserve_number(
                            product_id,
                            choice(numbers_list),
                            product.resources.phone_number,
                            switch_id,
                        )
                    case "equipment":
                        equipment_request = EquipmentRequests()
                        nomenclature = self.get_nomenclature(product_id)
                        serials = equipment_request.search_serial_number(
                            nomenclature, test_context.client.inquiry.product.partner_point_id
                        )
                        test_context.client.inquiry.product.serial_number = choice(serials)
                        self._reserve_equipment(
                            product_id=product_id,
                            order_resource_id=product.resources.equipment,
                            nomenclature=nomenclature,
                            serial_number=test_context.client.inquiry.product.serial_number,
                        )
                    case "city_phone_number":
                        number_request = PhoneNumbersRequests()
                        switch_id = test_context.client.inquiry.product.switch_id
                        numbers = self._get_phone_list(
                            switch_id=switch_id,
                            standard_id=test_context.client.inquiry.product.standard_id,
                            macro_region_id=number_request.macro_region_id,
                            is_type_def=False,
                        )
                        numbers_list = number_request.get_numbers_data(numbers)
                        assert_that(lambda: len(numbers_list) != 0, "Нет фиксированных номеров для бронирования")
                        self._reserve_number(
                            product_id=product_id,
                            phone_number=choice(numbers_list),
                            order_resource_id=product.resources.city_phone_number,
                            switch_id=switch_id,
                        )
                    case "apn":
                        self._reserve_ip_address(order_resource_id=product.resources.apn)

    @allure.step("API: Проверка корректности заказа")
    def _order_check(self, commercial_order_number: int) -> None:
        """
        Проверка корректности заказа
        :param commercial_order_number: номер заявки коммерческого заказа из get_commercial_order_number
        Упадет с ошибкой, если проверка не завершилась успешно
        """
        body_clarifying = {"activity": {"activityCode": "CLARIFYING_NEEDS_VERIFYING"}}
        response_clarifying = self.inquiry_forward(commercial_order_number, body_clarifying)
        self.check_response_status(response_clarifying, 204, "Проверка корректности заказа не прошла")

    def _get_commercial_status_state_code(self) -> str:
        response = self.get(
            url=f"{BASE_URL_API}/openapi/v1/productManagement/commercialOrders/{test_context.client.inquiry.commercial_order}/commonInfo"
        )
        self.check_response_status(response, 200, "Не удалось получить информацию по коммерческому заказу")
        response_state = response.json().get("verificationState")
        assert_that(
            lambda: response_state is not None and response_state.get("code") is not None,
            "Информация по коммерческому заказу не получена",
        )
        return response_state.get("code")

    @allure.step("API: Проверка статуса коммерческого заказа")
    def _check_commercial_status(self) -> None:
        wait_that(
            lambda: self._get_commercial_status_state_code() == "SUCCEED",
            timeout=25,
            exception=AssertionError,
            message=lambda: f"Статус коммерческого заказа не соответствует ожидаемому SUCCEED. Конфликты: {self._get_commercial_order_conflicts()}",
        )

    @allure.step("API: Получение конфликтов коммерческого заказа")
    def _get_commercial_order_conflicts(self) -> str:
        conflicts = self.post(
            url=f"{BASE_URL_API}/openapi/v1/productManagement/commercialOrders/{test_context.client.inquiry.commercial_order}/conflicts/search",
            data={
                "objectIds": [prod.product_id for prod in test_context.client.inquiry.product.additional_product_list]
            },
        ).json()["conflicts"]
        if len(conflicts) > 0:
            return str([conflict["message"] for conflict in conflicts])
        return "Отсутствуют"

    @allure.step("API: Проверка технической возможности")
    def _technical_solution_verifying(self, commercial_order_number: int) -> None:
        """
        Проверка технической возможности подключения продукта по параметрам заявки
        :param: commercial_order_number номер заявки коммерческого заказа из get_commercial_order_number

        Упадет с ошибкой, если проверка не завершилась успешно
        """
        body_technical = {"activity": {"activityCode": "TECHNICAL_SOLUTION"}}
        wait_that(
            lambda: self.inquiry_forward(commercial_order_number, body_technical).status == 204,
            timeout=75,
            sleep_seconds=15,
            exception=InquiryTechnicalSolutionException,
            message="Не прошла проверка технической возможности",
        )

    @allure.step("API: Заявка на подключение продукта клиенту")
    def _connect_inquiry(self, inquiry_id: int) -> None:
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
            sleep_seconds=15,
            exception=AssertionError,
            message=f"Заявка на подключение не выполнилась за {connect_timeout} секунд",
        )

    @allure.step("API: Ожидание выполнения заявок")
    def _wait_sale_done(self) -> None:
        """
        Метод для ожидания выполнения заявки или заявок. Заявки берутся из test_context.client.inquiry_list
        Упадет с ошибкой, если продажа не завершилась успешно.
        """
        sale_timeout = 400

        wait_that(
            lambda: all(
                (
                    "COMPLETED" in self._get_commercial_order_stage(inq.commercial_order)["code"]
                    if inq.commercial_order is not None
                    else False
                )
                or self.inquiry_api.get_appeal_status(inq.id) == "CLOSE"
                for inq in test_context.client.inquiry_list
            ),
            timeout=sale_timeout,
            sleep_seconds=5,
            exception=AssertionError,
            message=f"Заявка/и {[inq.id for inq in test_context.client.inquiry_list]} не завершились за {sale_timeout} секунд.",
        )

    @allure.step("API: Получение абонента клиента")
    def _get_client_subscriber(self) -> Tuple[int, int]:
        """
        Метод для получения последнего по дате создания абонента у клиента
        :return: subs_id, msisdn/internet - идентификатор абонента, номер телефона/интернета
        """
        body_subs = {"subscriptionInfoBaseFilter": {"subscriptionIds": [test_context.client.inquiry.product.subs_id]}}
        response_subs = self.post(
            url=f"{BASE_URL_API}/openapi/v1/subscriptionManagement/subscriptions/search", data=body_subs
        )
        self.check_response_status(response_subs, 200, "Не получены данные об абонентах")
        item = self.get_last_created_item_response(response_subs.json()["items"])
        check_that(lambda: item != {}, SubscriptionNotFoundException, "Не найден абонент клиента")
        return item["subscriptionId"], item["identification"]["identificationValue"]

    @allure.step("API: Получение информации о первом элементе заказа")
    def _get_subscriber_info(self) -> None:
        """Метод для заполнения информации абонента"""
        body_info_subs = {"params": {"limit": 100, "offset": 0}}
        response_info_subs = self.post(
            url=f"{BASE_URL_API}/openapi/v1/productManagement/commercialOrders/{test_context.client.inquiry.commercial_order}/orderProducts/search",
            data=body_info_subs,
        )
        self.check_response_status(response_info_subs, 200, "Не получены данные о подписке абонента")
        subs_item = response_info_subs.json()["items"]
        for item, product in zip(subs_item, test_context.client.inquiry.product_list):
            product.product_name = item["name"]
            product.total_amount = float(item["totalPrice"]["amount"])
            product.subs_id = int(item["productPrototypes"][0]["holderPrototype"]["holderMapping"]["holderId"])
            for part in item["totalPrice"]["includedParts"]:
                if part["priceTypeCode"] == "FeeProdOfferingPrice":
                    product.one_time_payment = float(part["amount"])
                if part["priceTypeCode"] == "RecurringChargeProdOfferPriceCharge":
                    product.subscription_fee = float(part["amount"])
        agreement_id = subs_item[0]["payerInformation"]["agreement"]["agreementId"]
        agreement_number = subs_item[0]["payerInformation"]["agreement"]["agreementNumber"]
        test_context.client.add_agreement(agreement_id, agreement_number)
        test_context.client.inquiry.agreement_id = agreement_id
        test_context.client.inquiry.agreement_number = agreement_number

        account_id = subs_item[0]["payerInformation"]["account"]["accountId"]
        account_number = (subs_item[0]["payerInformation"]["account"]["accountNumber"],)
        test_context.client.get_agreement(agreement_id).add_account(account_id, account_number)
        test_context.client.inquiry.product.account_id = account_id
        test_context.client.inquiry.product.account_number = account_number

    def _sale_prepare_and_add_product(self, need_spd: bool, need_create_link_person: bool | None) -> None:
        """
        Метод для подготовки продажи и проведения обязательных шагов
        :param need_spd: флаг отвечающий за Формирование комплектов РПД
        :param need_create_link_person: флаг, отвечающий за создание связанного лица
        """
        inquiry = test_context.client.inquiry
        inquiry.address_id = self._get_address_id(test_context.client.user_id)

        if need_create_link_person:
            linked_persons = self._get_linked_person(test_context.client.user_id)
            if len(linked_persons) > 0:
                inquiry.linked_person_id = linked_persons[0]["linkedPerson"]["linkedPersonId"]
            else:
                inquiry.linked_person_id = self._make_linked_person(inquiry.date, test_context.client.user_id)
                self._add_linked_person_to_uds(test_context.client.user_id, inquiry.linked_person_id)
        else:
            inquiry.linked_person_id = None

        self._add_inquiry_properties(test_context.client.user_id)

        inquiry.id = self._register_inquiry(need_spd)

        inquiry.commercial_order = self._get_commercial_order_id(inquiry.id)

        inquiry.commercial_order_number = self._get_commercial_order_number(inquiry.id)

        linked_objects = self._get_linked_objects("regions")
        if len(linked_objects) != 0:
            inquiry.region_id = linked_objects[0]["attributes"]["regionId"]

        for product in inquiry.product_list:
            inquiry.product = product
            if isinstance(product, MainProduct) and len(product.additional_product_list) > 0:
                self._get_available_additional_products()
                self._parse_additional_products_by_name()

            # для продажи бандлов в будущем, нужно обрабатывать список product_id
            inquiry.product.product_id = self._select_product_offer(inquiry.product)[0]

            for add_product in inquiry.product.additional_product_list:
                add_product.product_id = self._select_product_offer(add_product)[0]

    def _get_sale_info(self) -> None:
        """Метод для дополнения информации о продаже"""
        self._get_subscriber_info()
        if test_context.client.inquiry.product.category == "internet":
            test_context.client.inquiry.product.internet_number = self._get_client_subscriber()[1]
        elif (
            test_context.client.inquiry.product.category in ["mobile", "fixed_phone"]
            or "satellite" in test_context.client.inquiry.product.category
        ):
            test_context.client.inquiry.product.phone_number = self._get_client_subscriber()[1]

    @allure.step("API: Продажа продуктов. Одна заявка")
    def _product_sale(
        self,
        need_spd: bool = False,
        need_create_link_person: bool | None = True,
    ) -> None:
        """Внутренний метод для продажи продукта. Создан для уменьшения дублирования кода"""
        self._sale_prepare_and_add_product(need_spd, need_create_link_person)

        for product in test_context.client.inquiry.product_list:
            test_context.client.inquiry.product = product
            self._resources_reserve(product)
            for add_product in test_context.client.inquiry.product.additional_product_list:
                self._resources_reserve(add_product)

        self._order_check(test_context.client.inquiry.commercial_order_number)
        self._check_commercial_status()

        if any(product.category in ["internet", "fixed_phone"] for product in test_context.client.inquiry.product_list):
            self._technical_solution_verifying(test_context.client.inquiry.commercial_order_number)

        self._connect_inquiry(test_context.client.inquiry.id)

    @allure.step("API: Продажа продуктов")
    def product_sale(
        self,
        client: EntrepreneurClient | IndividualClient | OrganizationClient = None,
        inquiry: InquiryInfo | List[InquiryInfo] = None,
        need_spd: bool = False,
        need_create_link_person: bool | None = True,
    ) -> InquiryInfo | List[InquiryInfo] | None:
        """
        Метод для продажи продуктов абоненту в категориях Мобильная связь и Интернет. Id продуктов берется по умолчанию из ProductInfo.
        По умолчанию, если не указан клиент, то берет из контекста. Если не указана заявка, то берет из контекста.
        Поддерживает множественную продажу если передать список из заявок.
        :param client: информация о клиенте. Если не передать, то берет из контекста
        :param inquiry: информация о заявке или список таких заявок. Если не передать, то берет из контекста
        :param need_spd: флаг, отвечающий за Формирование комплектов РПД
        :param need_create_link_person: флаг, отвечающий за создание связанного лица
        :return: информация о заявке
        """
        if client:
            test_context.client = client
            if client not in test_context.client_list:
                test_context.client_list.append(client)

        if inquiry:
            inquiry_list = [inquiry] if isinstance(inquiry, InquiryInfo) else inquiry
            if inquiry_list != test_context.client.inquiry_list:
                test_context.client.inquiry_list = inquiry_list

        for inquiry in test_context.client.inquiry_list:
            test_context.client.inquiry = inquiry
            self._product_sale(need_spd, need_create_link_person)

        self._wait_sale_done()

        for inquiry in test_context.client.inquiry_list:
            test_context.client.inquiry = inquiry
            for product in inquiry.product_list:
                test_context.client.inquiry.product = product
                self._get_sale_info()

        return (
            test_context.client.inquiry
            if len(test_context.client.inquiry_list) == 1
            else test_context.client.inquiry_list
        )

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
    def _get_inquiries(self, user_id: int) -> list[int]:
        response = self.post(
            url=f"{BASE_URL_API}/openapi/v1/customers/{user_id}/inquiries/search?sort=inquiryId&limit=60&offset=0&useTemplate=true"
        )
        self.check_response_status(response, 200, "Не найдено заявок")
        return [item["inquiryId"] for item in response.json()["items"]]

    @allure.step("API: Получение {seq_number} заявки у клиента")
    def _get_nth_inquiry(self, user_id: int, seq_number: int) -> int:
        wait_timeout = 10
        wait_that(
            lambda: len(self._get_inquiries(user_id)) >= seq_number,
            timeout=wait_timeout,
            sleep_seconds=5,
            exception=InquirySearchException,
            message=f"Количество заявок у клиента {user_id} меньше чем {seq_number}",
        )
        return self._get_inquiries(user_id)[seq_number - 1]

    def _get_product_id(self) -> int:
        payload = {
            "classificationCode": "all",
            "showCFSInfo": True,
            "subscriptionId": test_context.client.inquiry.product.subs_id,
        }
        response = self.post(f"{BASE_URL_API}/openapi/v1/productManagement/products/searchBySubscription", data=payload)
        self.check_response_status(response, 200, "Не получена информация по абоненту")
        return response.json()["items"][0]["productId"]

    @allure.step("API: Создание заявки на отключение продукта")
    def _create_product_disconnect_inquiry(self) -> int:
        """
        Метод для создания заявки с нужными параметрами.
        Составляется по test_context
        :return: id заявки на управление продуктами
        """
        product_id = self._get_product_id()
        co_str = f'{{"addProductsParameters":[{{"holderId":{test_context.client.inquiry.product.subs_id},"productId":{product_id}}}],"operation":"DISCONNECT_PRODUCT"}}'
        subs_str = f"MSISDN: {test_context.client.inquiry.product.phone_number} (стандарт Спутниковая связь)"
        disc_type = "DISС_INDEPEND"
        match test_context.client.inquiry.product.category:
            case "internet":
                subs_str = f"LOGIN: {test_context.client.inquiry.product.internet_number} (стандарт ШПД)"
            case "mobile":
                subs_str = f"MSISDN: {test_context.client.inquiry.product.phone_number} (стандарт GSM)"
            case "satellite_rent":
                disc_type = "DISC_INDEPEND_RETURN_EQUIP"
        payload = {
            "contact": {"customer": {"customerId": f"{test_context.client.user_id}"}},
            "inquiry": {
                "customProperties": [
                    self._get_inquiry_property(
                        "subscriptionId", "STRING", stringValue=test_context.client.inquiry.product.subs_id
                    ),
                    self._get_inquiry_property(
                        "saleAgreement", "DICTIONARY", [{"itemCode": test_context.client.inquiry.agreement_id}]
                    ),
                    self._get_inquiry_property("saleAddAgreementAdd", "DICTIONARY", [{"itemCode": "CREATE_AUTO"}]),
                    self._get_inquiry_property(
                        "saleAccount", "DICTIONARY", [{"itemCode": test_context.client.inquiry.product.account_id}]
                    ),
                    self._get_inquiry_property("COproductsToDisconnect", "STRING", stringValue=co_str),
                    self._get_inquiry_property("disconnectionType", "DICTIONARY", [{"itemCode": disc_type}]),
                    self._get_inquiry_property(
                        "disconnectionInfo",
                        "DB_QUERY",
                        [
                            {
                                "value": "<INFO>Будет отключен выбранный продукт и все его зависимые продукты и опции (при наличии)."
                            }
                        ],
                    ),
                    self._get_inquiry_property(
                        "subscriptionCurrentProductId",
                        "STRING",
                        stringValue=product_id,
                    ),
                    self._get_inquiry_property(
                        "subscriptionCurrentProduct",
                        "DB_QUERY",
                        [{"value": test_context.client.inquiry.product.product_name}],
                    ),
                    self._get_inquiry_property("needConfig", "STRING", stringValue=False),
                    self._get_inquiry_property(
                        "saleWarn", "DB_QUERY", [{"value": "<INFO>Выполнение заявки пройдет в автоматическом режиме."}]
                    ),
                    self._get_inquiry_property(
                        "partnerPointId", "STRING", stringValue=f"{test_context.client.inquiry.product.partner_point_id}"
                    ),
                    self._get_inquiry_property("partnerPointInfo", "DB_QUERY", [{"value": "Торговая точка 1"}]),
                    self._get_inquiry_property(
                        "inqrLinkedPerson",
                        "DICTIONARY",
                        [{"itemCode": f"{test_context.client.inquiry.linked_person_id}"}],
                    ),
                    self._get_inquiry_property("subscription", "DB_QUERY", [{"value": subs_str}]),
                ],
                "email": "",
                "phone": "",
                "priority": {"inquiryPriorityId": 1},
                "topic": {"topicId": 28},
            },
        }
        if test_context.client.inquiry.product.category == "satellite_rent":
            payload["inquiry"]["customProperties"].append(
                self._get_inquiry_property("equipmentRentStateAction", "DICTIONARY", [{"itemCode": "MOVE_TO_STORAGE"}])
            )
        response = self.post(f"{BASE_URL_API}/openapi/v1/inquiries", data=payload)
        self.check_response_status(response, 201, "API: Заявка на отключение продукта не создалась")
        return response.json()["inquiryId"]

    @allure.step("API: Отключение продукта")
    def product_disconnect(self, client: BaseClient = None, product: MainProduct = None) -> None:
        """
        Метод для отключения продукта абоненту.
        По умолчанию, если не указан клиент, то берет из контекста.
        :param client: Информация о клиенте. Если не передать, то берет из контекста
        :param product: Информация о продукте. Если не передать, то берет из контекста
        """
        if client:
            test_context.client = client
        inquiry_index = -1
        if product not in test_context.client.inquiry.product_list:
            for index, inquiry in enumerate(test_context.client.inquiry_list):
                if product in inquiry.product_list:
                    inquiry_index = index
                    test_context.client.inquiry = inquiry
        assert_that(
            lambda: product in test_context.client.inquiry.product_list or product is None,
            "Указанный продукт не находится у клиента",
        )

        new_inquiry = test_context.client.inquiry_list.pop(inquiry_index)
        new_inquiry.id = self._create_product_disconnect_inquiry()
        new_inquiry.commercial_order = None
        test_context.client.inquiry_list.append(new_inquiry)
        test_context.client.inquiry = new_inquiry

        self._wait_sale_done()

    @allure.step(
        "API: Получение списка дополнительных продуктов доступных для продуктового предложения {product_offering_id}"
    )
    def get_available_additional_products_by_main_po_id(
        self, product_offering_id: int, partner_point_id: int = 100001, region_id: int = 100004
    ) -> List[AdditionalProduct]:
        """
        Метод для получения списка доп.ПП по id основного ПП
        :param product_offering_id: id основного ПП.
        :param partner_point_id: id точки партнера.
        :param region_id: id региона.
        """
        payload = {
            "addRelatedByRelationshipTypes": ["BUNDLE"],
            "availabilityParameters": {"action": "CHANGE", "regionId": region_id},
            "productOfferingSegmentCodes": [test_context.client.category.upper()],
            "productOfferingsFilter": {
                "action": "ACTIVATE",
                "mainProductOfferingId": product_offering_id,
                "productOfferingSegmentCodes": [test_context.client.category.upper()],
                "productOfferingSelectMode": "DEPENDENT",
                "productOfferingTypes": ["SIMPLE_PO"],
                "subscriptionType": "REGULAR",
            },
            "segmentFilter": [
                {"code": "DMS_CLIENT_SEGMENT", "value": "DMS_CLIENT_SEGMENT_ORGANIZATION"},
                {"code": "segmentActivity", "value": "BRANCH_NOT_DEFINED"},
            ],
            "stockItemsFilter": {"partnerPointId": partner_point_id},
        }
        response = self.post(
            url=f"{BASE_URL_API}/openapi/v1/tailored_nbss/productOfferings/availableForAction/search", data=payload
        )
        self.check_response_status(
            response,
            200,
            "Не удалось получить список дополнительных продуктов для продажи по текущему основному продукту.",
        )

        additional_products = response.json()["items"]
        available_additional_products = []
        for product in additional_products:
            add_product = AdditionalProduct()

            add_product.category = product["category"]["name"]
            add_product.product_name = product["name"]
            add_product.product_offering_id = product["productOfferingId"]
            add_product.segments = [segment["code"] for segment in product["segments"]]
            add_product.main_product_relationships_ids = [
                relationship["relatedProductOfferingId"] for relationship in product["relationships"]
            ]
            add_product.technologies = [technology["code"] for technology in product["technologies"]]
            if total_price := product.get("totalPrice"):
                add_product.total_amount = total_price["amount"]
                for part in total_price["includedParts"]:
                    if part["priceTypeCode"] == "FeeProdOfferingPrice":
                        add_product.one_time_payment = float(part["amount"])
                    if part["priceTypeCode"] == "RecurringChargeProdOfferPriceCharge":
                        add_product.subscription_fee = float(part["amount"])

            available_additional_products.append(add_product)
        return available_additional_products

    @allure.step("API: Получение id дополнительного продукта по его названию")
    def get_additional_po_id_by_name(self, main_po_id: int, additional_po_name: str = "+2 ГБ") -> int | None:
        """
        Метод для получения id доп.ПП по его названию
        :param main_po_id: id основного ПП
        :param additional_po_name: название доп.ПП
        :return: id доп.ПП
        """
        for additional_product in self.get_available_additional_products_by_main_po_id(main_po_id):
            if additional_product.product_name == additional_po_name:
                return additional_product.product_offering_id
        return None

    @allure.step("API: Получение списка дополнительных продуктов для продажи по текущему основному продукту")
    def _get_available_additional_products(self) -> None:
        """Получить список доступных дополнительных продуктов для продажи по текущему основному продукту."""
        inquiry = test_context.client.inquiry
        if inquiry.product.product_offering_id not in inquiry.available_additional_products_by_main_product:
            available_additional_products = self.get_available_additional_products_by_main_po_id(
                product_offering_id=inquiry.product.product_offering_id,
                partner_point_id=inquiry.product.partner_point_id,
                region_id=inquiry.region_id,
            )

            inquiry.available_additional_products_by_main_product[inquiry.product.product_offering_id] = (
                available_additional_products
            )

    @staticmethod
    def _parse_additional_products_by_name() -> None:
        """Заполняет атрибуты переданных в заявку дополнительных продуктов, если доп. продукт присутствует в списке доступных для основного продукта."""
        inquiry = test_context.client.inquiry
        additional_list = inquiry.product.additional_product_list
        available_products = {
            ap.product_name: ap
            for ap in inquiry.available_additional_products_by_main_product[inquiry.product.product_offering_id]
        }
        requested_products = {rp.product_name: rp for rp in additional_list}

        for product_name in requested_products:
            if product_name:
                check_that(
                    lambda: product_name in available_products,
                    AdditionalProductCantBeAdded,
                    f"Переданный дополнительный продукт '{product_name}' отсутствует в списке доступных для основного продукта.\nСписок доступных продуктов: {list(available_products.keys())}",
                )

        inquiry.product.additional_product_list = [
            available_products[add_product.product_name] for add_product in additional_list
        ]
