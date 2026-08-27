from random import choice
from typing import Literal

import allure

from api.base_requests import BaseRequests
from api.exceptions import (
    CityPhoneNumberListIsEmptyException,
    IPListIsEmptyException,
    MSISDNListIsEmptyException,
    ResourceReserveFailedException,
    SimCardListIsEmptyException,
    SNListIsEmptyException,
)
from api.lis_requests.equipment import EquipmentRequests
from api.lis_requests.ip_addresses import IpAddressRequests
from api.lis_requests.phone_numbers import PhoneNumbersRequests
from api.lis_requests.sim_cards import SimCardsRequests
from api.nbss.inquiry_requests.commercial_order_requests import CommercialOrderRequests
from common.enums.lis import LogicalStatuses, PhoneNumberStates, SimCardStates
from common.enums.user import User
from common.helpers.checker import check_response_conflicts, check_that
from common.helpers.data_generator import get_current_datetime_string
from common.helpers.env_helper import BASE_URL_API
from models.context import test_context
from models.lis_resources import IPInfo, PhoneNumberData, SimCardData
from models.product import AdditionalProduct, MainProduct
from models.stand_context import stand_context


class ResourcesRequests(BaseRequests):
    def __init__(self) -> None:
        super().__init__()
        self.sim_cards_requests = SimCardsRequests()
        self.commercial_order_requests = CommercialOrderRequests()

        test_context.switch_api_context_to_user(User.ADMIN)

    @allure.step("API: Бронирование MSISDN")
    def reserve_number(
        self,
        product_id: int,
        phone_number: PhoneNumberData,
        order_resource_id: int,
        switch_id: int,
        replace: bool = False,
    ) -> str:
        """
        Бронирование номера телефона
        :param product_id: id продукта, который хотим инстанцировать клиенту из select_product_offer
        :param phone_number: объект класса. В нем хранится информация о сущности, которую хотим забронировать
        :param order_resource_id: id ресурса продукта, который бронируем
        :param switch_id: id коммутатора
        :param replace: флаг, указывающий на то, что бронируется номер для замены
        Упадет с ошибкой, если бронировние не завершилось успешно
        :return: Возвращает id бронирования
        """
        request_body = {
            "connectionType": "Regular",
            "fillSource": "LIS",
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
        if not replace:
            request_body.update(
                {"commercialOrderId": test_context.client.inquiry.commercial_order, "orderProductId": product_id}
            )
        response = self.post(
            url=f"{BASE_URL_API}/openapi/v1/tailored_nbss/resources/defPhoneNumber/lock/bulk",
            json=request_body,
        )
        self.check_response_status(response, 200, "Невозможно забронировать номер")
        check_response_conflicts(response, ResourceReserveFailedException)
        return self.get_response_content_by_jsonpath(
            '$.resources[0].filledCharacteristics[?(@.code=="lockId")].value', response
        )

    @allure.step("API: Бронирование SIM карты")
    def reserve_sim_card(self, product_id: int, sim_card: SimCardData, order_resource_id: int) -> None:
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
            json=request_body,
        )
        self.check_response_status(response, 200, "Невозможно забронировать sim карту")
        check_response_conflicts(response, ResourceReserveFailedException)

    @allure.step("API: Бронирование серийного номера оборудования")
    def reserve_equipment(self, product_id: int, order_resource_id: int, serial_number: int, nomenclature: str) -> None:
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
            json=request_body,
        )
        self.check_response_status(response, 200, "Невозможно забронировать оборудование по серийному номеру")
        check_response_conflicts(response, ResourceReserveFailedException)

    def reserve_ip_address(self, product_id: int, order_resource_id: int, ip_address: IPInfo) -> None:
        """
        Внутренний метод для бронирования IP адреса
        :param order_resource_id: id ресурса продукта, который бронируем
        :param ip_address: инстанс IPInfo - бронируемый ip адрес
        Упадет с ошибкой, если бронировние не завершилось успешно
        """
        characteristics = [
            {"code": "IPAddress", "type": "string", "values": [ip_address.address]},
            {"code": "IPAddressId", "type": "long", "values": [ip_address.id]},
        ]
        if test_context.client.apn is not None:
            characteristics.append({"code": "isDynamicIP", "type": "boolean", "values": [False]})
            characteristics.append({"code": "APN", "type": "string", "values": [test_context.client.apn.name]})
        payload = {
            "commercialOrderId": test_context.client.inquiry.commercial_order,
            "fillSource": "LIS",
            "orderProductId": product_id,
            "resources": [
                {
                    "fillCharacteristics": characteristics,
                    "orderResourceIds": [order_resource_id],
                }
            ],
        }
        response = self.post(f"{BASE_URL_API}/openapi/v1/tailored_nbss/resources/accessPoint/lock/bulk", json=payload)
        self.check_response_status(response, 200, "Ошибка бронирования IP адреса")
        check_response_conflicts(response, ResourceReserveFailedException)

    @allure.step("API: Вызов нужного метода для бронирования")
    def resource_match_and_do_reserve(
        self,
        product: MainProduct | AdditionalProduct,
        resource: Literal["sim_card_id", "phone_number", "equipment", "city_phone_number", "apn", "ip_address"],
    ) -> None:
        """
        Метод для выбора метода бронирования
        Choice используется для того, чтобы, если два теста одновременно будут исполнять этот кусок кода, максимизировать шанс того, что они выберут разные ресурсы.
        Таким образом мы пытаемся избежать ситуации когда тесты попытаются забронировать один и тот же ресурс и один из них зафейлится
        """
        product_id = product.product_id
        match resource:
            case "sim_card_id":
                sims = self.sim_cards_requests.get_sim_card_list(
                    status_id=[LogicalStatuses.free.id],
                    state_id=[SimCardStates.unlinked.id],
                    equipment_id=test_context.client.inquiry.product.switch_id,
                    is_reserved=False,
                )
                sim_list = self.sim_cards_requests.get_sim_cards_data(sims)
                check_that(lambda: len(sim_list) != 0, SimCardListIsEmptyException, "Нет симок для бронирования")
                chosen_sim = choice(sim_list)
                self.reserve_sim_card(product_id, chosen_sim, product.resources.sim_card_id)
            case "phone_number":
                number_request = PhoneNumbersRequests()
                switch_id = test_context.client.inquiry.product.switch_id
                numbers = number_request.get_phone_numbers(
                    equipment_ids=[switch_id],
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
                numbers_list = number_request.get_numbers_data(numbers)
                check_that(lambda: len(numbers_list) != 0, MSISDNListIsEmptyException, "Нет номеров для бронирования")
                self.reserve_number(
                    product_id,
                    choice(numbers_list),
                    product.resources.phone_number,
                    switch_id,
                )
            case "equipment":
                equipment_request = EquipmentRequests()
                nomenclature = self.commercial_order_requests.get_nomenclature(product_id)
                serials = equipment_request.search_serial_number(
                    nomenclature, test_context.client.inquiry.product.partner_point_id
                )
                check_that(lambda: len(serials) != 0, SNListIsEmptyException, "Нет серийных номеров для бронирования")
                test_context.client.inquiry.product.serial_number = choice(serials)
                self.reserve_equipment(
                    product_id=product_id,
                    order_resource_id=product.resources.equipment,
                    nomenclature=nomenclature,
                    serial_number=test_context.client.inquiry.product.serial_number,
                )
            case "city_phone_number":
                number_request = PhoneNumbersRequests()
                switch_id = test_context.client.inquiry.product.switch_id
                numbers = number_request.get_phone_numbers(
                    equipment_ids=[switch_id],
                    standard_ids=[test_context.client.inquiry.product.standard_id],
                    macro_region_id=stand_context.stand_equipment.macro_region_id,
                    type_def=False,
                    is_reserved=False,
                    number_category_ids=[1],
                    number_class_ids=[1],
                    status_id=[LogicalStatuses.free.id],
                    state_date_ranges={
                        PhoneNumberStates.open_for_use.id: None,
                        PhoneNumberStates.freed.id: get_current_datetime_string(),
                    },
                )
                numbers_list = number_request.get_numbers_data(numbers)
                check_that(
                    lambda: len(numbers_list) != 0,
                    CityPhoneNumberListIsEmptyException,
                    "Нет фиксированных номеров для бронирования",
                )
                self.reserve_number(
                    product_id=product_id,
                    phone_number=choice(numbers_list),
                    order_resource_id=product.resources.city_phone_number,
                    switch_id=switch_id,
                )
            case "apn":
                product.ip_address = test_context.client.apn.pop_random()
                check_that(
                    lambda: test_context.client.apn is not None and len(test_context.client.apn.free_ip_list) > 0,
                    ValueError,
                    "Список доступных IP адресов пуст",
                )
                self.reserve_ip_address(
                    product_id=product_id, order_resource_id=product.resources.apn, ip_address=product.ip_address
                )
            case "ip_address":
                ip_requests = IpAddressRequests()
                available_ip_list = ip_requests.get_available_ip_addresses_objects(
                    access_point_id=stand_context.stand_equipment.default_apn.id
                )
                check_that(
                    lambda: len(available_ip_list) != 0,
                    IPListIsEmptyException,
                    "Нет доступных IP адресов для бронирования",
                )
                available_ip_address = choice(available_ip_list)
                self.reserve_ip_address(
                    product_id=product_id,
                    order_resource_id=product.resources.ip_address,
                    ip_address=available_ip_address,
                )
