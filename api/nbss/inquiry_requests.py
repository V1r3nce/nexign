from dataclasses import dataclass
from typing import Literal

import allure

from api.base_requests import BaseRequests
from api.exceptions import GetStatusAppealException, GetStatusFileException
from common.helpers.checker import wait_that
from common.helpers.env_helper import BASE_URL_API


@dataclass
class CustomProperty:
    """
    Класс для данных по дополнительным атрибутам

    custom_property_declaration_code (str): код дополнительного атрибута (DB: CPM, table: cms.cms_additional_attr)
    custom_property_type (Literal["STRING", "DATE", "NUMBER", "BOOL", "DICTIONARY", "WEB_COMPONENT", "DB_QUERY"]):
    тип значений доп атрибута
    custom_property_values (str | int | bool | list): список значений
    """

    custom_property_declaration_code: str
    custom_property_type: Literal["STRING", "DATE", "NUMBER", "BOOL", "DICTIONARY", "WEB_COMPONENT", "DB_QUERY"]
    custom_property_values: str | int | bool | list


@dataclass
class AppealInfo:
    """
    Класс для данных для регистрации обращения

    customer_id (int): id клиента, для которого регистрируется обращение
    custom_property (list[CustomProperty]): список дополнительных атрибутов
    topic_name (str): тема заявки ("Не согласен с расчетами" и т.д.) (DB: CPM, table: cms.cms_topic)
    priority_id (int): Приоритет обращения (1 - Низкий, 2 - Средний, 3 - Высокий)
    """

    customer_id: int
    custom_property: list[CustomProperty]
    topic_name: str
    priority_id: int = 1
    email: str = ""
    phone: str = ""


@dataclass
class ForwardInfo:
    """
    Класс для передачи обращения

    appeal_id (int): id обращения
    activity_name (str): название шага процесса, в который передается обращение (DB: CPM, table: cms.cms_process)
    queue_name (str): название очереди, в которую обращение передается на обработку (DB: CPM, table: cms.cms_queue)
    forward_note (str): сопроводительная записка
    finish_date (str): дата завершения обработки
    """

    appeal_id: int
    activity_name: str
    queue_name: str
    forward_note: str = None
    finish_date: str = None


class AppealRequests(BaseRequests):
    def __init__(self) -> None:
        super().__init__()

        self.TOPIC = {
            "Не согласен с расчетами": 301,
            "Генерация трафика": 991,
        }
        self.ACTIVITY = {
            "Обработка претензий": 180,
            "Автоматическая обработка": 177,
        }
        self.QUEUE = {
            "Обработка претензий B2C": "INQR_RP_B2C",
            "Регистрация": "REGISTRATION",
        }

    @allure.step("API: Зарегистрировать обращение")
    def create_appeal(self, appeal: AppealInfo) -> int:
        payload = {
            "contact": {"customer": {"customerId": f"{appeal.customer_id}"}},
            "inquiry": {
                "customProperties": [],
                "email": appeal.email,
                "phone": appeal.phone,
                "priority": {"inquiryPriorityId": appeal.priority_id},
                "topic": {"topicCode": self.TOPIC[appeal.topic_name]},
            },
        }
        for custom_property in appeal.custom_property:
            custom_property_el = {
                "customPropertyDeclaration": {
                    "customPropertyDeclarationCode": custom_property.custom_property_declaration_code
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

        appeal = self.post(url=f"{BASE_URL_API}/openapi/v1/inquiries", json=payload)
        self.check_response_status(appeal, 201, "Обращение не зарегистрировано")
        return appeal.json()["inquiryId"]

    @allure.step("API: Передать обращение")
    def forward_appeal(self, forward: ForwardInfo) -> None:
        payload = {
            "activity": {"activityCode": self.ACTIVITY[forward.activity_name]},
            "queue": {"queueCode": self.QUEUE[forward.queue_name]},
        }
        if forward.forward_note:
            payload["forwardNote"] = forward.forward_note
        if forward.finish_date:
            payload["finishDate"] = forward.finish_date

        forward_response = self.post(
            url=f"{BASE_URL_API}/openapi/v1/inquiries/{forward.appeal_id}/forward", json=payload
        )
        self.check_response_status(forward_response, 204, "Обращение не передано")

    @allure.step("API: Получение статуса заявки")
    def get_appeal_status(self, appeal_id: int) -> str:
        response = self.get(url=f"{BASE_URL_API}/openapi/v1/inquiries/{appeal_id}")
        return response.json()["currentState"]["status"]["inquiryStatusCode"]

    @allure.step("Ожидание статуса заявки {status}")
    def wait_appeal_status(self, appeal_id: int, status: str = "CLOSE", timeout: int = 25) -> None:
        wait_that(
            lambda: self.get_appeal_status(appeal_id) == status,
            timeout=timeout,
            sleep_seconds=0.5,
            exception=GetStatusAppealException,
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
        property_code, item_code = None, None
        match category:
            case "calls":
                property_code, item_code = "tedAmountMin", "1"
            case "SMS":
                property_code, item_code = "tedAmountSms", "2"
            case "internet":
                property_code, item_code = "tedAmountMb", "3"
        appeal_id = self.create_appeal(
            AppealInfo(
                customer_id=user_id,
                custom_property=[
                    CustomProperty("spdAccount", "DICTIONARY", [{"itemCode": account_id}]),
                    CustomProperty(property_code, "STRING", f"{volume}"),
                    CustomProperty("tedSubscriber", "DICTIONARY", [{"itemCode": subscription_id}]),
                    CustomProperty("tedServiceType", "DICTIONARY", [{"itemCode": item_code}]),
                ],
                topic_name="Генерация трафика",
            )
        )
        self.forward_appeal(
            ForwardInfo(appeal_id=appeal_id, activity_name="Автоматическая обработка", queue_name="Регистрация")
        )
        self.wait_appeal_status(appeal_id)

    @allure.step("API: Создание заявки 'Не согласен с расчетами' для клиента {user_id}")
    def claim_not_agree_with_calculation(self, user_id: int) -> int:
        appeal_id = self.create_appeal(
            AppealInfo(
                customer_id=user_id,
                custom_property=[CustomProperty("inqrLinkedPerson", "DICTIONARY", [])],
                topic_name="Не согласен с расчетами",
            )
        )
        self.forward_appeal(
            ForwardInfo(appeal_id=appeal_id, activity_name="Обработка претензий", queue_name="Обработка претензий B2C")
        )
        return appeal_id

    @allure.step("API: Получение информации о документах заявки {appeal_id}")
    def get_appeal_files(self, appeal_id: int) -> list:
        """
        Метод получает информацию о документах заявки

        :param appeal_id: идентификатор заявки
        :return: список словарей с информацией о документах
        """
        payload = {"documentTypeIds": [3, 9], "recipients": [{"recipientType": "inquiry", "recipientId": appeal_id}]}

        files_info = self.post(url=f"{BASE_URL_API}/openapi/v1/reports/digital/files/search", json=payload)
        self.check_response_status(files_info, 200, "Не удалось получить файлы заявки")
        return files_info.json()["items"]

    @allure.step("Ожидание успешного статуса первого документа")
    def wait_file_status(self, appeal_id: int, timeout: int = 120) -> None:
        wait_that(
            lambda: self.get_appeal_files(appeal_id)[0]["documentStatus"]["code"] == "COMPLETED",
            timeout=timeout,
            sleep_seconds=1,
            exception=GetStatusFileException,
            message=f"Документ не перешёл в статус COMPLETED за {timeout} c.",
        )
