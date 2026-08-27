import copy
from copy import deepcopy
from datetime import datetime
from random import choice
from typing import List, Tuple

import allure
import pytest

from api.base_requests import BaseRequests
from api.dgs_requests.dgs_requests import DGSRequests
from api.exceptions import (
    AdditionalProductCantBeAdded,
    InquiryTechnicalSolutionException,
    ResourceReserveFailedException,
    SubscriptionNotFoundException,
)
from api.lis_requests.phone_numbers import PhoneNumbersRequests
from api.lis_requests.sim_cards import SimCardsRequests
from api.nbss.address_requests import AddressRequests
from api.nbss.client_requests.client_requests import ClientRequests
from api.nbss.inquiry_requests.commercial_order_requests import CommercialOrderRequests
from api.nbss.inquiry_requests.inquiry_requests import InquiriesRequests
from api.nbss.inquiry_requests.technical_order_requests import TechnicalOrderRequests
from api.nbss.linked_person_requests import LinkedPersonRequests
from api.nbss.resources_requests import ResourcesRequests
from common.enums.dgs import DocumentTypes
from common.enums.inquiry import (
    InquiryAddAgreementAdd,
    InquiryApiSteps,
    TechnicalOrderStageCodes,
)
from common.enums.lis import LogicalStatuses, PhoneNumberStates
from common.enums.topic import ActionTopic
from common.enums.user import User
from common.helpers.checker import assert_that, check_that, wait_that
from common.helpers.data_generator import get_current_datetime_string
from common.helpers.env_helper import BASE_URL_API
from common.helpers.retry import execute_with_retry
from models.client import BaseClient, EntrepreneurClient, IndividualClient, OrganizationClient
from models.context import test_context
from models.inquiry import InquiryInfo
from models.lis_resources import PhoneNumberData
from models.product import AdditionalProduct, CurrentResource, MainProduct, Product, get_filled_attributes
from models.stand_context import stand_context


class ClientInquiriesRequests(BaseRequests):
    def __init__(self) -> None:
        super().__init__()
        self.phone_numbers_requests = PhoneNumbersRequests()
        self.sim_cards_requests = SimCardsRequests()
        self.inquiry_requests = InquiriesRequests()
        self.client_requests = ClientRequests()
        self.linked_person_requests = LinkedPersonRequests()
        self.address_requests = AddressRequests()
        self.resources_requests = ResourcesRequests()
        self.commercial_order_requests = CommercialOrderRequests()
        self.technical_order_requests = TechnicalOrderRequests()

        test_context.switch_api_context_to_user(User.ADMIN)

    @pytest.mark.lis
    @allure.step("API: Бронирование ресурсов")
    def resources_reserve(self, product: MainProduct | AdditionalProduct) -> None:
        """
        Бронирование ресурсов для продажи продукта, если ресурсы были найдены.
        :param product: продукт, который хотим добавить клиенту из select_product_offer.
        Упадет с ошибкой, если бронирование не завершилось успешно.
        """
        self.commercial_order_requests.get_order_resources(product)
        if product.resources:
            for resource in get_filled_attributes(product.resources):
                execute_with_retry(
                    lambda: self.resources_requests.resource_match_and_do_reserve(product, resource),
                    tries=3,
                    delay=1,
                    exceptions=(ResourceReserveFailedException, AssertionError),
                )

    @allure.step("API: Проверка технической возможности")
    def _technical_solution_verifying(self, commercial_order_number: int) -> None:
        """
        Проверка технической возможности подключения продукта по параметрам заявки
        :param: commercial_order_number номер заявки коммерческого заказа из get_commercial_order_number

        Упадет с ошибкой, если проверка не завершилась успешно
        """
        self.inquiry_requests.wait_allowed_next_activity(InquiryApiSteps.technical_solution_verifying)
        wait_that(
            lambda: self.inquiry_requests.inquiry_forward_step(
                app_id=commercial_order_number, step=InquiryApiSteps.technical_solution_verifying
            ),
            timeout=75,
            sleep_seconds=15,
            exception=InquiryTechnicalSolutionException,
            message="Не прошла проверка технической возможности",
        )

    @allure.step("API: Проверка статуса заявки")
    def _check_inquiry_done_status(self, inquiry: InquiryInfo) -> bool | None:
        """
        Проверка завершенности заявки. Если технический заказ завершится ошибкой - выбросится AssertionError
        :param inquiry: объект InquiryInfo - заявка у которой проверяем статус завершенности
        :return: булево значение. True - заявка завершилась
        """
        init_inquiry = test_context.client.inquiry
        test_context.client.inquiry = inquiry
        technical_order_id, order_code = self.technical_order_requests.get_technical_order_id_and_code(inquiry)
        if technical_order_id is None or order_code not in [
            TechnicalOrderStageCodes.service_organization,
            TechnicalOrderStageCodes.completed,
        ]:
            command_result = self.inquiry_requests.search_failed_events(inquiry=inquiry)
            assert_that(
                lambda: command_result is None,
                lambda: (
                    f"У заявки {inquiry.id} ошибка выполнения операции {command_result.command_name}\nСтатус: {command_result.result_text}\nДетали: {command_result.result_note}"
                ),
            )
        if technical_order_id is not None:
            technical_order_status = self.technical_order_requests.get_technical_order_status(technical_order_id)
            assert_that(
                lambda: technical_order_status is None or technical_order_status != "ERR",
                lambda: (
                    f"У заявки {inquiry.id} технический заказ №{inquiry.technical_order_id} завершился с ошибкой\n{self.technical_order_requests.get_technical_order_error(technical_order_id)}"
                ),
            )
        test_context.client.inquiry = init_inquiry
        return (
            TechnicalOrderStageCodes.completed in order_code if inquiry.commercial_order is not None else False
        ) or self.inquiry_requests.get_appeal_status(inquiry.id) == "CLOSE"

    @allure.step("API: Ожидание выполнения заявок")
    def _wait_sale_done(self) -> None:
        """
        Метод для ожидания выполнения заявки или заявок. Заявки берутся из test_context.client.inquiry_list
        Упадет с ошибкой, если продажа не завершилась успешно.
        """
        sale_timeout = 400

        wait_that(
            lambda: all(self._check_inquiry_done_status(inquiry=inq) for inq in test_context.client.inquiry_list),
            timeout=sale_timeout,
            sleep_seconds=5,
            exception=AssertionError,
            message=f"Заявка/и {[inq.id for inq in test_context.client.inquiry_list]} не завершились за {sale_timeout} секунд.",
        )

        for inquiry in test_context.client.inquiry_list:
            inquiry.is_completed = True

    @allure.step("API: Получение абонента клиента")
    def _get_client_subscriber(self) -> Tuple[int, int]:
        """
        Метод для получения последнего по дате создания абонента у клиента
        :return: subs_id, msisdn/internet - идентификатор абонента, номер телефона/интернета
        """
        body_subs = {"subscriptionInfoBaseFilter": {"subscriptionIds": [test_context.client.inquiry.product.subs_id]}}
        response_subs = self.post(
            url=f"{BASE_URL_API}/openapi/v1/subscriptionManagement/subscriptions/search", json=body_subs
        )
        self.check_response_status(response_subs, 200, "Не получены данные об абонентах")
        item = self.get_last_created_item_response(response_subs.json()["items"])
        check_that(lambda: item != {}, SubscriptionNotFoundException, "Не найден абонент клиента")
        return item["subscriptionId"], item["identification"]["identificationValue"]

    @pytest.mark.nwm
    @allure.step("API: Получение информации о первом элементе заказа")
    def _get_subscriber_info(self) -> None:
        """Метод для заполнения информации абонента"""
        body_info_subs = {"params": {"limit": 100, "offset": 0}}
        subs_item = self.commercial_order_requests.get_order_products(body_info_subs)["items"]
        for item, product in zip(subs_item, test_context.client.inquiry.product_list):
            product.product_name = item["name"]
            product.total_amount = float(item["totalPrice"]["amount"])
            product.subs_id = int(item["productPrototypes"][0]["holderPrototype"]["holderMapping"]["holderId"])
            product.product_id = int(item["productPrototypes"][0]["productMapping"]["productId"])
            product.is_connected = True
            additional_list = product.additional_product_list if hasattr(product, "additional_product_list") else []
            for additional_product in additional_list:
                additional_item = next(item for item in subs_item if item.get("name") == additional_product.product_name)
                additional_product.product_id = int(
                    additional_item["productPrototypes"][0]["productMapping"]["productId"]
                )
                additional_product.is_connected = True
            for part in item["totalPrice"]["includedParts"]:
                if part["priceTypeCode"] == "FeeProdOfferingPrice":
                    product.one_time_payment = float(part["amount"])
                if part["priceTypeCode"] == "RecurringChargeProdOfferPriceCharge":
                    product.subscription_fee = float(part["amount"])
        agreement_id = int(subs_item[0].get("payerInformation", {}).get("agreement", {}).get("agreementId", "-1"))
        agreement_number = subs_item[0].get("payerInformation", {}).get("agreement", {}).get("agreementNumber", None)
        assert_that(
            lambda: agreement_id != -1 and agreement_number is not None, "Получены некорректные данные о договоре"
        )
        if not any(a.id == agreement_id for a in test_context.client.agreements):
            test_context.client.add_agreement(agreement_id, agreement_number)
        test_context.client.inquiry.agreement_id = agreement_id
        test_context.client.inquiry.agreement_number = agreement_number

        account_id = int(subs_item[0].get("payerInformation", {}).get("account", {}).get("accountId", "-1"))
        account_number = int(subs_item[0].get("payerInformation", {}).get("account", {}).get("accountNumber", "-1"))
        assert_that(lambda: agreement_id != -1 and agreement_number != -1, "Получены некорректные данные о ЛС")
        agreement = test_context.client.get_agreement(agreement_id)
        if agreement is not None and not any(acc.id == account_id for acc in agreement.accounts):
            agreement.add_account(account_id, account_number)
        test_context.client.inquiry.product.account_id = account_id
        test_context.client.inquiry.product.account_number = account_number

    def sale_prepare_and_add_product(self, need_spd: bool, need_create_link_person: bool | None) -> None:
        """
        Метод для подготовки продажи и проведения обязательных шагов
        :param need_spd: флаг отвечающий за Формирование комплектов РПД
        :param need_create_link_person: флаг, отвечающий за создание связанного лица
        """
        inquiry = test_context.client.inquiry
        inquiry.address_id = self.address_requests.get_address_id(test_context.client.user_id)

        if need_create_link_person:
            linked_persons = self.linked_person_requests.get_linked_person(test_context.client.user_id)
            if len(linked_persons) > 0:
                inquiry.linked_person_id = linked_persons[0]["linkedPerson"]["linkedPersonId"]
            else:
                inquiry.linked_person_id = self.linked_person_requests.make_linked_person(
                    inquiry.date, test_context.client.user_id
                )
                self.linked_person_requests.add_linked_person_to_uds(
                    test_context.client.user_id, inquiry.linked_person_id
                )
        else:
            inquiry.linked_person_id = None

        self.inquiry_requests.add_inquiry_properties(test_context.client.user_id)

        inquiry.id = self.inquiry_requests.form_and_register_inquiry(need_spd)
        inquiry.commercial_order = self.commercial_order_requests.get_commercial_order_id(inquiry.id)
        inquiry.commercial_order_number = self.commercial_order_requests.get_commercial_order_number(inquiry.id)

        linked_objects = self.address_requests.get_linked_objects("regions")
        if len(linked_objects) != 0:
            inquiry.region_id = linked_objects[0]["attributes"]["regionId"]

        for product in inquiry.product_list:
            inquiry.product = product
            if isinstance(product, MainProduct) and len(product.additional_product_list) > 0:
                self._get_available_additional_products()
                self._parse_additional_products_by_name()

            # для продажи бандлов в будущем, нужно обрабатывать список product_id
            inquiry.product.product_id = self.commercial_order_requests._select_product_offer(inquiry.product)[0]

            for add_product in inquiry.product.additional_product_list:
                add_product.product_id = self.commercial_order_requests._select_product_offer(add_product)[0]

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

    @pytest.mark.crab
    @pytest.mark.praim
    @pytest.mark.dgs
    @pytest.mark.nlm
    @pytest.mark.psc
    @allure.step("API: Продажа продуктов. Одна заявка")
    def _product_sale(
        self,
        need_spd: bool = False,
        need_create_link_person: bool | None = True,
    ) -> None:
        """Внутренний метод для продажи продукта. Создан для уменьшения дублирования кода"""
        self.sale_prepare_and_add_product(need_spd, need_create_link_person)

        for product in test_context.client.inquiry.product_list:
            test_context.client.inquiry.product = product
            self.resources_reserve(product)
            for add_product in test_context.client.inquiry.product.additional_product_list:
                self.resources_reserve(add_product)
                if add_product.individualized_subs_fee is not None:
                    self.commercial_order_requests.product_individualization(add_product)
            if product.individualized_subs_fee is not None:
                self.commercial_order_requests.product_individualization(product)

        self.inquiry_requests.forward_step_with_check(test_context.client.inquiry.commercial_order_number)
        self.commercial_order_requests.check_commercial_status()

        if any(product.category in ["internet", "fixed_phone"] for product in test_context.client.inquiry.product_list):
            self._technical_solution_verifying(test_context.client.inquiry.commercial_order_number)

        self.inquiry_requests.connect_inquiry(test_context.client.inquiry.id)

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
            inquiry.is_completed = True

        for inquiry in test_context.client.inquiry_list:
            is_activation_date_set = False
            for product in inquiry.product_list:
                if product.activation_date:
                    self._set_product_activation_date(
                        product.activation_date, inquiry.id, product.subs_id, product.product_id
                    )
                    is_activation_date_set = True
                for additional_product in product.additional_product_list:
                    if additional_product.activation_date:
                        self._set_product_activation_date(
                            additional_product.activation_date,
                            inquiry.id,
                            product.subs_id,
                            additional_product.product_id,
                        )
                        is_activation_date_set = True
            if is_activation_date_set:
                self.inquiry_requests.forward_after_activation_date_set(inquiry.id)

        return (
            test_context.client.inquiry
            if len(test_context.client.inquiry_list) == 1
            else test_context.client.inquiry_list
        )

    @allure.step("Обогатить заявку информацией о продаже")
    def get_client_inquiries_info_and_enrich(self, client: BaseClient | None = None) -> None:
        """Дополняет заявки клиента и обогащает пустые"""
        client = test_context.client if client is None else client
        inquiries = self.inquiry_requests.get_inquiries(test_context.client.user_id)
        if not inquiries:
            return

        existing_inquiry_ids = [test_context_inquiry.id for test_context_inquiry in client.inquiry_list]
        for inquiry_id in inquiries:
            if inquiry_id not in existing_inquiry_ids:
                client.inquiry_list.append(InquiryInfo(id=inquiry_id))

        for inquiry in client.inquiry_list:
            test_context.client.inquiry = inquiry
            if inquiry.id != 0 and inquiry.commercial_order == 0:
                inquiry.commercial_order = self.commercial_order_requests.get_commercial_order_id(inquiry.id)
            if inquiry.id != 0 and inquiry.commercial_order != 0:
                self.commercial_order_requests.create_products_in_inquiry(inquiry)
                if self._check_inquiry_done_status(inquiry=inquiry):
                    self._get_sale_info()

    @allure.step("API: Выбор ЛС для продукта")
    def lock_product_to_account_and_agreement(
        self, commercial_order_id: int, account_id: int, agreement_id: int
    ) -> None:
        product_id = self.get_product_id()
        payload = {
            "orderProductsPayerInfo": [
                {
                    "orderProductId": product_id,
                    "payerInformation": {"accountId": account_id, "agreementId": agreement_id},
                }
            ]
        }
        response = self.post(
            f"{BASE_URL_API}/openapi/v1/productManagement/commercialOrders/{commercial_order_id}/orderProducts/payerInformation/update/bulk",
            json=payload,
        )
        self.check_response_status(response, 200, "Не удалось выбрать ЛС для продукта")

    def get_product_id(self, product: MainProduct | AdditionalProduct = None) -> str:
        """
        Получение идентификатора продукта после продажи
        :param product: продукт у которого мы хотим узнать идентификатор
        :return: id продукта в виде строки
        """
        payload = {
            "classificationCode": "all",
            "showCFSInfo": True,
            "subscriptionId": test_context.client.inquiry.product.subs_id if product is None else product.subs_id,
        }
        response = self.post(f"{BASE_URL_API}/openapi/v1/productManagement/products/searchBySubscription", json=payload)
        self.check_response_status(response, 200, "Не получена информация по абоненту")
        return self.get_response_content_by_jsonpath("$.items[0].productId", response)

    @allure.step("API: Создание заявки на отключение продукта")
    def _create_product_disconnect_inquiry(self) -> int:
        """
        Метод для создания заявки с нужными параметрами.
        Составляется по test_context
        :return: id заявки на управление продуктами
        """
        product_id = self.get_product_id()
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
                    self.inquiry_requests.get_inquiry_property(
                        "subscriptionId", "STRING", stringValue=test_context.client.inquiry.product.subs_id
                    ),
                    self.inquiry_requests.get_inquiry_property(
                        "saleAgreement", "DICTIONARY", [{"itemCode": test_context.client.inquiry.agreement_id}]
                    ),
                    self.inquiry_requests.get_inquiry_property(
                        "saleAddAgreementAdd", "DICTIONARY", [{"itemCode": "CREATE_AUTO"}]
                    ),
                    self.inquiry_requests.get_inquiry_property(
                        "saleAccount", "DICTIONARY", [{"itemCode": test_context.client.inquiry.product.account_id}]
                    ),
                    self.inquiry_requests.get_inquiry_property("COproductsToDisconnect", "STRING", stringValue=co_str),
                    self.inquiry_requests.get_inquiry_property(
                        "disconnectionType", "DICTIONARY", [{"itemCode": disc_type}]
                    ),
                    self.inquiry_requests.get_inquiry_property(
                        "disconnectionInfo",
                        "DB_QUERY",
                        [
                            {
                                "value": "<INFO>Будет отключен выбранный продукт и все его зависимые продукты и опции (при наличии)."
                            }
                        ],
                    ),
                    self.inquiry_requests.get_inquiry_property(
                        "subscriptionCurrentProductId",
                        "STRING",
                        stringValue=product_id,
                    ),
                    self.inquiry_requests.get_inquiry_property(
                        "subscriptionCurrentProduct",
                        "DB_QUERY",
                        [{"value": test_context.client.inquiry.product.product_name}],
                    ),
                    self.inquiry_requests.get_inquiry_property("needConfig", "STRING", stringValue=False),
                    self.inquiry_requests.get_inquiry_property(
                        "saleWarn", "DB_QUERY", [{"value": "<INFO>Выполнение заявки пройдет в автоматическом режиме."}]
                    ),
                    self.inquiry_requests.get_inquiry_property(
                        "partnerPointId", "STRING", stringValue=f"{test_context.client.inquiry.product.partner_point_id}"
                    ),
                    self.inquiry_requests.get_inquiry_property(
                        "partnerPointInfo", "DB_QUERY", [{"value": "Торговая точка 1"}]
                    ),
                    self.inquiry_requests.get_inquiry_property(
                        "inqrLinkedPerson",
                        "DICTIONARY",
                        [{"itemCode": f"{test_context.client.inquiry.linked_person_id}"}],
                    ),
                    self.inquiry_requests.get_inquiry_property("subscription", "DB_QUERY", [{"value": subs_str}]),
                ],
                "email": "",
                "phone": "",
                "priority": {"inquiryPriorityId": 1},
                "topic": {"topicId": ActionTopic.SaleTopic.id},
            },
        }
        if test_context.client.inquiry.product.category == "satellite_rent":
            payload["inquiry"]["customProperties"].append(
                self.inquiry_requests.get_inquiry_property(
                    "equipmentRentStateAction", "DICTIONARY", [{"itemCode": "MOVE_TO_STORAGE"}]
                )
            )
        return self.inquiry_requests.register_inquiry(payload)

    @allure.step("API: Отключение продукта")
    def product_disconnect(
        self, client: BaseClient = None, product: MainProduct = None, existing_inquiry_id: int | None = None
    ) -> None:
        """
        Метод для отключения продукта абоненту.
        По умолчанию, если не указан клиент, то берет из контекста.
        :param client: Информация о клиенте. Если не передать, то берет из контекста
        :param product: Информация о продукте. Если не передать, то берет из контекста
        :param existing_inquiry_id: id заявки, если она уже создана
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
        if existing_inquiry_id is not None:
            new_inquiry.id = existing_inquiry_id
        else:
            new_inquiry.id = self._create_product_disconnect_inquiry()
        new_inquiry.commercial_order = self.commercial_order_requests.get_commercial_order_id(new_inquiry.id)
        new_inquiry.commercial_order_number = self.commercial_order_requests.get_commercial_order_number(new_inquiry.id)
        test_context.client.inquiry_list.append(new_inquiry)
        test_context.client.inquiry = new_inquiry

        self._wait_sale_done()

    @allure.step("API: Создание заявки на продажу доп ПП для основного продукта")
    def additional_product_for_main_create_inquiry(
        self,
        main_product: MainProduct,
        additional_product_name: str,
        agreement_add: InquiryAddAgreementAdd = InquiryAddAgreementAdd.auto,
    ) -> None:
        check_that(
            lambda: main_product.product_offering_id is not None,
            exception=ValueError,
            message="Получен некорректный продукт",
        )
        additional_po_id = self.get_additional_po_id_by_name(
            main_po_id=main_product.product_offering_id, additional_po_name=additional_product_name
        )
        client = test_context.client
        co_str = f'{{"addProductsParameters":[{{"payerInformation":{{"accountId":{client.agreements[0].accounts[0].id},"agreementId":{client.agreements[0].id}}},"productParameters":{{"productOfferingId":{additional_po_id}}}}}],"mainProduct":{{"holderId":{main_product.subs_id}}},"operation":"CONNECT_ADDITIONAL_FOR_CUSTOMER_PRODUCT"}}'
        payload = {
            "contact": {"customer": {"customerId": str(test_context.client.user_id)}},
            "inquiry": {
                "customProperties": [
                    self.inquiry_requests.get_inquiry_property(
                        "subscriptionId", "STRING", stringValue=main_product.subs_id
                    ),
                    self.inquiry_requests.get_inquiry_property(
                        "COAddOptionOffersToConnect", "STRING", stringValue=co_str
                    ),
                    self.inquiry_requests.get_inquiry_property(
                        "saleAgreement", "DICTIONARY", [{"itemCode": str(client.agreements[0].id)}]
                    ),
                    self.inquiry_requests.get_inquiry_property(
                        "saleAddAgreementAdd", "DICTIONARY", [{"itemCode": agreement_add}]
                    ),
                    self.inquiry_requests.get_inquiry_property(
                        "saleAccount", "DICTIONARY", [{"itemCode": str(client.agreements[0].accounts[0].id)}]
                    ),
                    self.inquiry_requests.get_inquiry_property(
                        "inqrLinkedPerson", "DICTIONARY", [{"itemCode": str(client.inquiry.linked_person_id)}]
                    ),
                    self.inquiry_requests.get_inquiry_property("saleAddKp", "DICTIONARY", [{"itemCode": "NOT_CREATE"}]),
                    self.inquiry_requests.get_inquiry_property(
                        "subscriptionCurrentProduct", "DB_QUERY", [{"value": main_product.product_name}]
                    ),
                    self.inquiry_requests.get_inquiry_property(
                        "subscription",
                        "DB_QUERY",
                        [
                            {
                                "value": f"MSISDN: {main_product.phone_number} (стандарт {'Спутниковая связь' if 'satellite' in main_product.category else 'Мобильная связь'})"
                            }
                        ],
                    ),
                    self.inquiry_requests.get_inquiry_property("needSPD", "DICTIONARY", [{"itemCode": "NOT_CREATE"}]),
                    self.inquiry_requests.get_inquiry_property("needConfig", "STRING", stringValue=True),
                    self.inquiry_requests.get_inquiry_property(
                        "saleWarn",
                        "DB_QUERY",
                        [
                            {
                                "value": "<INFO>При выполнении заявки требуется участие пользователя. После сохранения будет выполнен переход в продажу."
                            }
                        ],
                    ),
                ],
                "priority": {"inquiryPriorityId": 1},
                "topic": {"topicId": ActionTopic.SaleTopic.id},
            },
        }
        previous_inquiry = test_context.client.inquiry
        new_inquiry = deepcopy(previous_inquiry)
        new_inquiry.id = self.inquiry_requests.register_inquiry(payload)
        test_context.client.inquiry_list.append(new_inquiry)
        test_context.client.inquiry = new_inquiry
        additional_product = AdditionalProduct(product_name=additional_product_name)
        additional_product.product_offering_id = additional_po_id
        new_inquiry.product.additional_product_list.append(additional_product)
        new_inquiry.product.additional_product = additional_product
        new_inquiry.commercial_order = self.commercial_order_requests.get_commercial_order_id(new_inquiry.id)
        new_inquiry.commercial_order_number = self.commercial_order_requests.get_commercial_order_number(new_inquiry.id)
        self.commercial_order_requests.fill_product_id_for_product(additional_product)
        test_context.client.inquiry = previous_inquiry

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
            url=f"{BASE_URL_API}/openapi/v1/tailored_nbss/productOfferings/availableForAction/search", json=payload
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

        additional_product_list = []
        for add_product in additional_list:
            product = available_products[add_product.product_name]
            product.activation_date = add_product.activation_date
            if add_product.individualized_subs_fee is not None:
                product = copy.deepcopy(product)
                product.individualized_subs_fee = add_product.individualized_subs_fee
            additional_product_list.append(product)
        inquiry.product.additional_product_list = additional_product_list

    @allure.step("API: Замена номера")
    def replace_number(self, product: MainProduct) -> Tuple[str, int]:
        """
        Метод ищет свободные номера. Выбирает рандомный. Резервирует его. Создает заявку на замену номера.
        :param product: продукт, по которому создается заявка на замену номера
        :return: новый номер, id заявки
        """
        numbers = self.phone_numbers_requests.get_phone_numbers(
            equipment_ids=[test_context.client.inquiry.product.switch_id],
            standard_ids=[test_context.client.inquiry.product.standard_id],
            macro_region_id=stand_context.stand_equipment.macro_region_id,
            type_def=True,
            is_reserved=False,
            number_category_ids=[1],
            number_class_ids=[1],
            status_id=[LogicalStatuses.free.id],
            state_date_ranges={
                PhoneNumberStates.open_for_use.id: None,
                PhoneNumberStates.freed.id: get_current_datetime_string(),
            },
        )
        phone_number_list = self.phone_numbers_requests.get_numbers_data(numbers)
        new_number = choice(phone_number_list).MSISDN

        lock_id = self.resources_requests.reserve_number(
            product.product_id, new_number, product.resources.phone_number, product.switch_id, replace=True
        )
        inquiry_id = self._create_number_replace_inquiry(product, new_number, lock_id)
        wait_that(
            lambda: self.inquiry_requests.get_appeal_status(test_context.client.inquiry.id) == "CLOSE",
            AssertionError,
            lambda: (
                f"Заявка на замену номера не выполнена успешно. Текущий статус заявки {self.inquiry_requests.get_appeal_status(test_context.client.inquiry.id)}"
            ),
            timeout=20,
        )
        test_context.client.inquiry.product.phone_number = new_number
        return new_number, inquiry_id

    @allure.step("API: Создание заявки на замену номера")
    def _create_number_replace_inquiry(
        self, product: MainProduct, new_number: PhoneNumberData, lock_id: str, cost: str = "100"
    ) -> int:
        """
        Метод создает заявку на замену номера
        :param product: продукт, по которому создается заявка на замену номера
        :param new_number: новый номер
        :param lock_id: id бронирования
        :return: номер заявки
        """
        product_id = self.get_product_id()
        resources = self.get_current_product_resources()
        payload = {
            "contact": {"customer": {"customerId": f"{test_context.client.user_id}"}},
            "inquiry": {
                "customProperties": [
                    self.inquiry_requests.get_inquiry_property(
                        "resourceType", "DICTIONARY", [{"itemCode": "defPhoneNumber"}]
                    ),
                    self.inquiry_requests.get_inquiry_property("subscriptionId", "STRING", stringValue=product.subs_id),
                    self.inquiry_requests.get_inquiry_property(
                        "resourceId", "STRING", stringValue=str(resources["defPhoneNumber"].resource_id)
                    ),
                    self.inquiry_requests.get_inquiry_property(
                        "resourceName", "STRING", stringValue="Телефонный номер (мобильный)"
                    ),
                    self.inquiry_requests.get_inquiry_property("productId", "STRING", stringValue=product_id),
                    self.inquiry_requests.get_inquiry_property(
                        "productOfferingId", "STRING", stringValue=product.product_offering_id
                    ),
                    self.inquiry_requests.get_inquiry_property(
                        "productName", "STRING", stringValue=product.product_name
                    ),
                    self.inquiry_requests.get_inquiry_property(
                        "agreementId", "STRING", stringValue=test_context.client.inquiry.agreement_id
                    ),
                    self.inquiry_requests.get_inquiry_property("resourceLockId", "STRING", stringValue=lock_id),
                    self.inquiry_requests.get_inquiry_property(
                        "changeType", "DICTIONARY", [{"itemCode": "createResource"}]
                    ),
                    self.inquiry_requests.get_inquiry_property("hasLinkedResources", "BOOL", booleanValue=False),
                    self.inquiry_requests.get_inquiry_property(
                        "isNeedAdditionalAgreement", "STRING", stringValue="false"
                    ),
                    self.inquiry_requests.get_inquiry_property("newMSISDN", "STRING", stringValue=new_number.MSISDN),
                    self.inquiry_requests.get_inquiry_property("cost", "STRING", stringValue=cost),
                ],
                "topic": {"topicCode": "UDS_CHANGE_RESOURCE"},
            },
        }
        response = self.post(f"{BASE_URL_API}/openapi/v1/inquiries", json=payload)
        self.check_response_status(response, 201, "API: Заявка на замену номера не создана")
        inquiry = copy.deepcopy(test_context.client.inquiry_list[-1])
        inquiry.id = response.json()["inquiryId"]
        inquiry.type = "change"
        test_context.client.inquiry_list.append(inquiry)
        test_context.client.inquiry = inquiry
        return inquiry.id

    @allure.step("API: Получение ресурсов текущего продукта")
    def get_current_product_resources(self, product: AdditionalProduct | MainProduct | None = None) -> dict:
        """
        Метод возвращает словарь ресурсов текущего продукта. А также записывает его в контекст
        :param product: продукт у которого мы хотим узнать ресурсы
        :return: словарь, где ключ - resourceType, значение - объект класса CurrentResource
        """
        if product is None:
            product = test_context.client.inquiry.product
        response = self.get(
            f"{BASE_URL_API}/openapi/v1/productManagement/subscriptions/{product.subs_id}/products/{self.get_product_id(product)}"
        )
        self.check_response_status(response, 200, "API: Не удалось получить ресурсы текущего продукта")
        resource_list = []
        product_info = response.json()
        for parameter in product_info["customerFacingServices"]:
            for resource in parameter["resources"]:
                resource_list.append(resource)

        resources = {}
        for resource in resource_list:
            if (
                resource.get("characteristics", None) is None
                or len(resource["characteristics"]) == 0
                or resource["characteristics"][0].get("values", None) is None
            ):
                raise AssertionError("API: Проблема парсинга данных о ресурсах продукта")
            resources[resource["resourceType"]] = CurrentResource(
                resource_id=resource["resourceId"],
                resource_name=resource["resourceSpecName"],
                resource_values=resource["characteristics"][0]["values"][0]
                if len(resource["characteristics"][0]["values"]) == 1
                else resource["characteristics"][0]["values"],
            )
        test_context.client.inquiry.product.current_resources = resources
        return resources

    @allure.step("API: Получить номер линии продукта")
    def get_product_copper_line_number(
        self, product: AdditionalProduct | MainProduct | None = None
    ) -> str | list[str] | None:
        """
        Получение номера линии (accessLineCopper) из основных характеристик продукта абонента
        :param product: продукт у которого мы хотим узнать номер линии
        :return: номер линии (строка) или None если не найден
        """
        if product is None:
            product = test_context.client.inquiry.product
        self.get_current_product_resources(product)
        if product.current_resources is not None and product.current_resources.get("accessLineCopper"):
            return product.current_resources.get("accessLineCopper").resource_values

        return None

    @allure.step("Найти продукт у клиента")
    def search_by_hierarchy(
        self, user_id: int, subs_id: int | None = None, agreement_id: int | None = None
    ) -> list[Product]:
        body = {"customerIds": [user_id]}
        if subs_id is not None:
            body.update({"subscriptionIds": [subs_id]})
        if agreement_id is not None:
            body.update({"agreementIds": [agreement_id]})
        response = self.post(
            url=f"{BASE_URL_API}/openapi/v1/productManagement/products/searchByHierarchy",
            json=body,
        )
        self.check_response_status(response, 200, "Невозможно получить продукт по ЛС")

        products = []
        for product in response.json().get("items", []):
            products.append(Product.model_validate(product))

        return products

    @allure.step("API: Ожидание активности всех продуктов по заданному ЛС")
    def wait_products_active_by_agreement(self, user_id: int, agreement_id: int, timeout_seconds: int = 45) -> None:
        wait_that(
            lambda: all(
                [
                    "ACTIVE" == product.status.code
                    for product in self.search_by_hierarchy(user_id, agreement_id=agreement_id)
                ]
            ),
            timeout=timeout_seconds,
            sleep_seconds=1,
            exception=AssertionError,
            message="На заданном ЛС есть не активированные продукты",
        )

    @allure.step("API: получить список основных ПП на заданном абоненте")
    def get_product_personal_account_by_subs_id(self, user_id: int, subs_id: int) -> dict:
        response = self.search_by_hierarchy(user_id, subs_id=subs_id)
        result = {}
        for item in response:
            classification = item.classification.code
            if classification == "main":
                payer = item.payerInformation.account
                account_number = payer.accountNumber
                subs_info = item.subscriptionInfo
                subs_id = subs_info.subscriptionId
                if subs_id is not None and account_number is not None:
                    result[subs_id] = int(account_number)
        return result

    @allure.step("API: Ожидание указанного ЛС на продукте")
    def wait_account_num_update(self, user_id: int, subs_id: int, account_num: int) -> None:
        wait_that(
            lambda: (self.get_product_personal_account_by_subs_id(user_id, subs_id).get(subs_id)) == int(account_num),
            timeout=60,
            sleep_seconds=1,
            exception=AssertionError,
            message=lambda: (
                f"На абоненте {subs_id} номер ЛС {self.get_product_personal_account_by_subs_id(user_id, subs_id).get(subs_id)} не совпал с ожидаемым {account_num}"
            ),
        )

    @allure.step("API: Установка даты активации продукта")
    def _set_product_activation_date(
        self, activation_date: datetime, commercial_order_id: int, subscription_id: int, product_id: int
    ) -> None:
        payload = {
            "action": "NBSS_CHANGE_ACTIVATION_DATE",
            "orderEntity": {"orderEntityId": commercial_order_id, "orderEntityType": "INQUIRY"},
            "orderParams": {
                "activationDate": activation_date.isoformat(),
                "holderIds": [subscription_id],
                "inquiryId": commercial_order_id,
                "productIds": [product_id],
            },
            "orderRecipient": {"orderRecipientId": commercial_order_id, "orderRecipientType": "INQUIRY"},
            "processingType": "SEQUENTIAL",
            "type": "NBSS_PORTAL",
        }
        response = self.post(
            url=f"{BASE_URL_API}/openapi/v2/orders",
            json=payload,
        )
        self.check_response_status(response, 200, "Не удалось установить дату активации продукта")

    @allure.step("API: Прохождение шагов договора и ЛС ручной заявки")
    def pass_manual_agreement_and_account_steps(
        self,
        inquiry: InquiryInfo,
        need_agreement_lock: bool = True,
        need_account_distribution: bool = True,
        need_last_forward: bool = True,
    ) -> None:
        dgs_requests = DGSRequests()
        self.inquiry_requests.connect_inquiry(inquiry.id)
        expected_document_type = DocumentTypes.agreement
        if need_agreement_lock:
            self.inquiry_requests.lock_agreement_to_inquiry(agreement_id=inquiry.agreement_id, inquiry_id=inquiry.id)
            self.inquiry_requests.wait_forward_allowed(inquiry.id)
            self.inquiry_requests.forward_step_with_check(app_id=inquiry.id, step=InquiryApiSteps.account_step)
        else:
            expected_document_type = DocumentTypes.additional_agreement
        if need_account_distribution:
            for main_product in inquiry.product_list or []:
                if not main_product.is_connected:
                    self.lock_product_to_account_and_agreement(
                        agreement_id=inquiry.agreement_id,
                        commercial_order_id=inquiry.commercial_order,
                        account_id=main_product.account_id,
                    )
                for additional_product in main_product.additional_product_list:
                    if not additional_product.is_connected:
                        self.lock_product_to_account_and_agreement(
                            agreement_id=inquiry.agreement_id,
                            commercial_order_id=inquiry.commercial_order,
                            account_id=additional_product.account_id,
                        )
            self.inquiry_requests.wait_forward_allowed(inquiry.id)
            self.inquiry_requests.forward_step_with_check(app_id=inquiry.id, step=InquiryApiSteps.document_approval)
        document = dgs_requests.wait_document_generation(recipient_id=inquiry.id, document_type=expected_document_type)
        dgs_requests.approve_document(document)
        if need_last_forward:
            self.inquiry_requests.wait_forward_allowed(inquiry.id)
            self.inquiry_requests.forward_step_with_check(
                app_id=inquiry.id, step=InquiryApiSteps.control_check_commercial_order
            )
