from dataclasses import dataclass
from typing import Literal

import allure
from playwright.sync_api import APIRequestContext

from api.exceptions import GetStatusInquiryException
from api.requests.base_requests import BaseRequests
from common.helpers.checker import wait_that
from common.helpers.env_helper import BASE_URL_API


@dataclass
class CustomProperty:
    """
    Класс для данных по дополнительным атрибутам

    custom_property_declaration_code (str): код дополнительного атрибута (DB: CPM, table: cms.cms_additional_attr)
    custom_property_declaration_id (int): id дополнительного атрибута (DB: CPM, table: cms.cms_additional_attr)
    custom_property_type (Literal["STRING", "DATE", "NUMBER", "BOOL", "DICTIONARY", "WEB_COMPONENT", "DB_QUERY"]):
    тип значений доп атрибута
    custom_property_values (str | int | bool | list): список значений
    """

    custom_property_declaration_code: str
    custom_property_declaration_id: int
    custom_property_type: Literal["STRING", "DATE", "NUMBER", "BOOL", "DICTIONARY", "WEB_COMPONENT", "DB_QUERY"]
    custom_property_values: str | int | bool | list


@dataclass
class InquiryInfo:
    """
    Класс для данных для регистрации обращения

    customer_id (int): id клиента, для которого регистрируется обращение
    custom_property (list[CustomProperty]): список дополнительных атрибутов
    topic_id (int): id темы заявки (36 - Не согласен с расчетами и т.д.) (DB: CPM, table: cms.cms_topic)
    priority_id (int): Приоритет обращения (1 - Низкий, 2 - Средний, 3 - Высокий)
    """

    customer_id: int
    custom_property: list[CustomProperty]
    topic_id: int
    priority_id: int = 1
    email: str = ""
    phone: str = ""


@dataclass
class ForwardInfo:
    """
    Класс для передачи обращения

    inquiry_id (int): id обращения
    activity_id (int): id шага процесса, в который передается обращение (DB: CPM, table: cms.cms_process)
    queue_id (int): id очереди, в которую обращение передается на обработку (DB: CPM, table: cms.cms_queue)
    activity_code (str): код шага процесса, в который передается обращение (DB: CPM, table: cms.cms_process)
    queue_code (str): код очереди, в которую обращение передается на обработку (DB: CPM, table: cms.cms_queue)
    forward_note (str): сопроводительная записка
    finish_date (str): дата завершения обработки
    """

    inquiry_id: int
    activity_id: int
    queue_id: int
    activity_code: str = None
    queue_code: str = None
    forward_note: str = None
    finish_date: str = None


class InquiryRequests(BaseRequests):
    def __init__(self, api_request_auth_context: APIRequestContext):
        super().__init__(api_request_auth_context)

    @allure.step("API: Зарегистрировать обращение")
    def create_inquiry(self, inquiry: InquiryInfo) -> int:
        payload = {
            "contact": {"customer": {"customerId": f"{inquiry.customer_id}"}},
            "inquiry": {
                "customProperties": [],
                "email": inquiry.email,
                "phone": inquiry.phone,
                "priority": {"inquiryPriorityId": inquiry.priority_id},
                "topic": {"topicId": inquiry.topic_id},
            },
        }
        for custom_property in inquiry.custom_property:
            custom_property_el = {
                "customPropertyDeclaration": {
                    "customPropertyDeclarationCode": custom_property.custom_property_declaration_code,
                    "customPropertyDeclarationId": custom_property.custom_property_declaration_id,
                },
                "type": custom_property.custom_property_type,
            }
            match custom_property.custom_property_type:
                case "STRING":
                    custom_property_el["stringValue"] = custom_property.custom_property_values
                case "DATE":
                    custom_property_el["dateValue"] = custom_property.custom_property_values
                case "NUMBER":
                    custom_property_el["numberValue"] = custom_property.custom_property_values
                case "BOOL":
                    custom_property_el["booleanValue"] = custom_property.custom_property_values
                case _:
                    custom_property_el["values"] = custom_property.custom_property_values
            payload["inquiry"]["customProperties"].append(custom_property_el)

        inquiry = self.post(url=f"{BASE_URL_API}/openapi/v1/inquiries", data=payload)
        self.check_response_status(inquiry, 201, "Обращение не зарегистрировано")
        return inquiry.json()["inquiryId"]

    @allure.step("API: Передать обращение")
    def forward_inquiry(self, forward: ForwardInfo) -> None:
        payload = {"activity": {"activityId": forward.activity_id}, "queue": {"queueId": forward.queue_id}}
        if forward.activity_code:
            payload["activity"]["activityCode"] = forward.activity_code
        if forward.queue_code:
            payload["queue"]["queueCode"] = forward.queue_code
        if forward.forward_note:
            payload["forwardNote"] = forward.forward_note
        if forward.finish_date:
            payload["finishDate"] = forward.finish_date

        forward_response = self.post(
            url=f"{BASE_URL_API}/openapi/v1/inquiries/{forward.inquiry_id}/forward", data=payload
        )
        self.check_response_status(forward_response, 204, "Обращение не передано")

    def get_inquiry_status(self, inquiry_id: int) -> str:
        response = self.get(url=f"{BASE_URL_API}/openapi/v1/inquiries/{inquiry_id}")
        return response.json()["currentState"]["status"]["inquiryStatusCode"]

    @allure.step("Ожидание статуса заявки {status}")
    def wait_inquiry_status(self, inquiry_id: int, status: str = "CLOSE", timeout: int = 25) -> None:
        wait_that(
            lambda: self.get_inquiry_status(inquiry_id) == status,
            timeout=timeout,
            sleep_seconds=0.5,
            exception=GetStatusInquiryException,
            message=f"Заявка не перешла в статус {status} за {timeout} c.",
        )

    @allure.step("API: Генерация трафика '{category}' для абонента с идентификатором: {subscription_id}")
    def generate_traffic(
        self,
        user_id: int,
        account_id: int,
        subscription_id: int,
        category: Literal["calls", "SMS", "internet"],
        volume: int,
    ) -> None:
        """
        Метод генерирует трафик с помощью заявки с темой "Генерация трафика"

        :param user_id: идентификатор клиента
        :param account_id: идентификатор ЛС
        :param subscription_id: идентификатор абонента, для которого генерируется трафик
        :param category: сервис, calls - Звонки, SMS - SMS, internet - Интернет
        :param volume: объём генерируемых данных
        """
        property_code, property_id, item_code = None, None, None
        match category:
            case "calls":
                property_code, property_id, item_code = "tedAmountMin", 78, "1"
            case "SMS":
                property_code, property_id, item_code = "tedAmountSms", 77, "2"
            case "internet":
                property_code, property_id, item_code = "tedAmountMb", 74, "3"
        inquiry_id = self.create_inquiry(
            InquiryInfo(
                customer_id=user_id,
                custom_property=[
                    CustomProperty("spdAccount", 75, "DICTIONARY", [{"itemCode": account_id}]),
                    CustomProperty(property_code, property_id, "STRING", f"{volume}"),
                    CustomProperty("tedSubscriber", 79, "DICTIONARY", [{"itemCode": subscription_id}]),
                    CustomProperty("tedServiceType", 76, "DICTIONARY", [{"itemCode": item_code}]),
                ],
                topic_id=1,
            )
        )
        self.forward_inquiry(ForwardInfo(inquiry_id=inquiry_id, activity_id=129, queue_id=1))
        self.wait_inquiry_status(inquiry_id)
