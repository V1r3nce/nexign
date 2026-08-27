from dataclasses import dataclass
from typing import Any, Literal

import allure
import pytest

from api.base_requests import BaseRequests
from api.exceptions import (
    GetStatusAppealException,
    GetStatusFileException,
    InquiryAllowedActionsException,
    InquirySearchException,
)
from common.enums.inquiry import (
    InquiryAddAccount,
    InquiryAddAgreementAdd,
    InquiryApiSteps,
    InquiryEventResultCodes,
    InquiryEventStates,
    InquiryNeedSPD,
)
from common.enums.topic import BaseTopic
from common.enums.user import User
from common.helpers.checker import assert_that, wait_that
from common.helpers.env_helper import BASE_URL_API
from models.client import OrganizationClient
from models.context import test_context
from models.inquiry import CommandResult, InquiryDetails, InquiryEvent, InquiryInfo
from models.playwright_bridge import GeneralResponse


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


class InquiriesRequests(BaseRequests):
    def __init__(self) -> None:
        super().__init__()

        test_context.switch_api_context_to_user(User.ADMIN)

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

    @pytest.mark.cpm
    @allure.step("API: Создание заявки")
    def register_inquiry(self, body_reg_inquiry: dict) -> int:
        """
        Создание заявки
        :param body_reg_inquiry: тело запроса
        :return: inquiry_id идентификатор заявки
        """
        response_reg_inquiry = self.post(
            url=f"{BASE_URL_API}/openapi/v1/inquiries",
            json=body_reg_inquiry,
        )
        self.check_response_status(response_reg_inquiry, 201, "Заявка не создалась")
        inquiry_id = response_reg_inquiry.json()["inquiryId"]
        return inquiry_id

    @allure.step("API: Создание заявки c topic = {topic}")
    def register_inquiry_with_topic(self, customer_id: str, topic: BaseTopic) -> int:
        body_reg_inquiry = {
            "contact": {"customer": {"customerId": customer_id}},
            "inquiry": {"customProperties": [], "priority": {"inquiryPriorityId": 1}, "topic": {"topicId": topic.id}},
        }

        inquiry_id = self.register_inquiry(body_reg_inquiry)
        return inquiry_id

    @allure.step("API: Сформировать и создать заявку")
    def form_and_register_inquiry(self, need_spd: bool) -> int:
        """
        Формирование и создание заявки
        :param need_spd: флаг необходимости РПД
        :return: inquiry_id идентификатор заявки
        """
        body_reg_inquiry = {
            "inquiry": {
                "topic": {"topicCode": "SALE_TOPIC"},
                "customProperties": [
                    self.get_inquiry_property("inqrLinkedPerson", "DICTIONARY", []),
                ],
                "email": "mail@mail.ru",
            },
            "contact": {"customer": {"customerId": test_context.client.user_id}},
        }
        if isinstance(test_context.client, OrganizationClient):
            body_reg_inquiry["inquiry"]["customProperties"].extend(
                [
                    self.get_inquiry_property("saleAddKp", "DICTIONARY", [{"itemCode": "NOT_CREATE"}]),
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
                    self.get_inquiry_property(
                        "saleAgreement",
                        "DICTIONARY",
                        [{"itemCode": str(test_context.client.agreements[0].id)}],
                    ),
                    self.get_inquiry_property(
                        "saleAccount",
                        "DICTIONARY",
                        [{"itemCode": str(test_context.client.agreements[0].accounts[0].id)}],
                    ),
                    self.get_inquiry_property(
                        "saleAddAgreementAdd", "DICTIONARY", [{"itemCode": InquiryAddAgreementAdd.auto}]
                    ),
                ]
            )
        else:
            body_reg_inquiry["inquiry"]["customProperties"].extend(
                [
                    self.get_inquiry_property("saleAgreement", "DICTIONARY", []),
                    self.get_inquiry_property("saleAddAccount", "DICTIONARY", [{"itemCode": InquiryAddAccount.auto}]),
                    self.get_inquiry_property(
                        "saleAddAgreementAdd", "DICTIONARY", [{"itemCode": InquiryAddAgreementAdd.auto}]
                    ),
                ]
            )

        if need_spd:
            body_reg_inquiry["inquiry"]["customProperties"].extend(
                [
                    self.get_inquiry_property("needSPD", "DICTIONARY", [{"itemCode": InquiryNeedSPD.auto}]),
                    self.get_inquiry_property("deliveryTypeSPD", "DICTIONARY", [{"itemCode": "email"}]),
                    self.get_inquiry_property("emailForSendSPD", "STRING", stringValue="mail@mail.ru"),
                ]
            )
        else:
            body_reg_inquiry["inquiry"]["customProperties"].append(
                self.get_inquiry_property("needSPD", "DICTIONARY", [{"itemCode": InquiryNeedSPD.not_create}])
            )
        inquiry_id = self.register_inquiry(body_reg_inquiry)
        test_context.client.inquiry.id = inquiry_id
        return inquiry_id

    @staticmethod
    def get_inquiry_property(code: str, prop_type: str, values: list = None, **kwargs: Any) -> dict:
        """
        Вспомогательный метод для создания кастомных свойств.

        :param code: код свойства (customPropertyDeclarationCode)
        :param prop_type: тип свойства (например, DICTIONARY, STRING)
        :param values: список значений или пустой список
        :param kwargs: дополнительные параметры (например, stringValue, booleanValue, numberValue, dateValue)
        :return: готовый объект свойства
        """
        prop = {
            "customPropertyDeclaration": {"customPropertyDeclarationCode": code},
            "type": prop_type,
        }

        if values is not None:
            prop["values"] = values

        for key, value in kwargs.items():
            prop[key] = value

        return prop

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
        self.check_response_status(response, 200, "Не получен статус заявки")
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

    @allure.step("API: Получение заявок клиента")
    def get_inquiries(self, user_id: int) -> list[int]:
        response = self.post(
            url=f"{BASE_URL_API}/openapi/v1/customers/{user_id}/inquiries/search?sort=inquiryId&limit=60&offset=0&useTemplate=true"
        )
        self.check_response_status(response, 200, "Не найдено заявок")
        return [item["inquiryId"] for item in response.json()["items"]]

    @pytest.mark.csm
    @pytest.mark.apc
    @allure.step("API: Получение информации о заявке по идентификатору")
    def get_inquiry_info(self, inquiry_id: int) -> InquiryDetails:
        """
        Возвращает информацию о заявке по id
        :param inquiry_id: id заявки
        :return: ответ на запрос
        """
        response = self.get(url=f"{BASE_URL_API}/openapi/v1/inquiries/{inquiry_id}")
        self.check_response_status(response, 200, "Невозможно получить информацию по заявке")
        return InquiryDetails.model_validate(response.json())

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

    @allure.step("API: Получение {seq_number} заявки у клиента")
    def get_nth_inquiry(self, user_id: int, seq_number: int) -> int:
        wait_timeout = 10
        wait_that(
            lambda: len(self.get_inquiries(user_id)) >= seq_number,
            timeout=wait_timeout,
            sleep_seconds=5,
            exception=InquirySearchException,
            message=f"Количество заявок у клиента {user_id} меньше чем {seq_number}",
        )
        return self.get_inquiries(user_id)[seq_number - 1]

    @allure.step("API: Получение статуса возможности перехода на следующий шаг")
    def check_forward_allowed_action(self, inquiry_id: int) -> bool:
        params = {"fields": "action(inquiryActionCode),access"}
        response = self.post(f"{BASE_URL_API}/openapi/v1/inquiries/{inquiry_id}/allowedActions", params=params)
        self.check_response_status(response, 200, "Не получены разрешенные действия для заявки")
        for action in response.json().get("items", []):
            if action.get("action", {}).get("inquiryActionCode") == "FORWARD":
                return action.get("access", False)
        return False

    @allure.step("API: Продвижение заявки")
    def inquiry_forward_step(
        self, app_id: int, step: InquiryApiSteps = InquiryApiSteps.clarifying_needs
    ) -> GeneralResponse:
        """
        Возвращает информацию о продвижении заявки
        :param app_id: id заявки
        :param step: шаг заявки
        :return: ответ на запрос
        """
        body = {"activity": {"activityCode": step}, "login": "Admin"}
        response = self.post(url=f"{BASE_URL_API}/openapi/v1/inquiries/{app_id}/forward", json=body)
        return response

    @allure.step("API: Проверка корректности заказа")
    def forward_step_with_check(self, app_id: int, step: InquiryApiSteps = InquiryApiSteps.clarifying_needs) -> None:
        """
        Возвращает информацию о продвижении заявки и проверяет успешность запроса
        :param app_id: id заявки
        :param step: шаг заявки
        :return: ответ на запрос
        """
        response = self.inquiry_forward_step(app_id, step)
        self.check_response_status(response, 204, f"Ошибка перехода заявки на шаг {step}")

    @allure.step("API: Ожидание возможности продвижения заявки")
    def wait_forward_allowed(self, inquiry_id: int) -> None:
        wait_that(
            lambda: self.check_forward_allowed_action(inquiry_id),
            timeout=30,
            sleep_seconds=3,
            exception=InquiryAllowedActionsException,
            message="Продвижение заявки недоступно",
        )

    @allure.step("API: Ожидание шага заявки")
    def wait_inquiry_step(self, inquiry_id: int, expected_step: str) -> None:
        wait_that(
            lambda: self.get_inquiry_info(inquiry_id).currentState.activity.activityCode == expected_step,
            timeout=30,
            sleep_seconds=5,
            exception=AssertionError,
            message=lambda: f"Заявка не перешла на шаг {expected_step}",
        )

    @allure.step("Найти заявки у клиента по типу")
    def wait_inquiry_number_by_topic(self, user_id: int, topic: str, seq_num: int = 1) -> None:
        wait_that(
            lambda: len(self.get_inquiry_by_topic(user_id, topic)) >= seq_num,
            timeout=30,
            sleep_seconds=0.5,
            exception=AssertionError,
            message="Не найдено нужное количество указанных типов заявок на договоре",
        )

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
        response_properties = self.post(url=f"{BASE_URL_API}/openapi/v1/inquiries/add/parameters", json=body_properties)
        self.check_response_status(response_properties, 200, "Не добавились параметры для заявки")

    @allure.step("API: Проверка customProperties заявки")
    def check_inquiry_properties(self, inquiry_id: int, property_index: int, expected: dict[str, object]) -> None:
        inquiry_info = self.get_inquiry_info(inquiry_id)
        custom_property = inquiry_info.customProperties[property_index]
        for field, value in expected.items():
            actual = custom_property
            for attr in field.split("."):
                actual = getattr(actual, attr)
            assert_that(
                lambda: actual == value,
                f"В ответе получено некорректное значение атрибута {field}: '{actual}' != '{value}'",
            )

    @allure.step("API: Выбор договора для заявки")
    def lock_agreement_to_inquiry(self, agreement_id: int, inquiry_id: int | None = None) -> None:
        if inquiry_id is None:
            if test_context.client.inquiry is not None:
                inquiry_id = test_context.client.inquiry.id
            else:
                raise ValueError("Передан некорректны id заявки")
        payload = {
            "customProperties": [
                {
                    "type": "DICTIONARY",
                    "customPropertyDeclaration": {"customPropertyDeclarationCode": "saleAgreement"},
                    "values": [{"itemCode": str(agreement_id)}],
                }
            ]
        }
        response = self.put(f"{BASE_URL_API}/openapi/v1/inquiries/{inquiry_id}", json=payload)
        self.check_response_status(response, 200, "Добавление договора на заявку прошло неуспешно")

    @allure.step("API: Получение событий заявки")
    def search_inquiry_events(self, inquiry: InquiryInfo) -> list[InquiryEvent]:
        response = self.get(f"{BASE_URL_API}/openapi/v1/inquiries/{inquiry.id}/events")
        self.check_response_status(response, 200, "Не получены события заявки")
        result: list[InquiryEvent] = []
        items = response.json().get("items", [])
        for item in items:
            result.append(InquiryEvent.model_validate(item))
        return result

    @allure.step("API: Поиск событий заявки с ошибками")
    def search_failed_events(self, inquiry: InquiryInfo) -> CommandResult | None:
        inquiry_events = self.search_inquiry_events(inquiry)
        for inquiry_event in inquiry_events:
            if inquiry_event.event_state.event_state_id == InquiryEventStates.done.id:
                for business_function in inquiry_event.business_function_result:
                    if business_function.result_code == InquiryEventResultCodes.error:
                        for command_result in business_function.command_result:
                            if command_result.result_code == InquiryEventResultCodes.error:
                                return command_result
        return None

    @allure.step("API: Заявка на подключение продукта клиенту")
    def connect_inquiry(self, inquiry_id: int) -> None:
        """
        Подключение продукта клиенту
        :param inquiry_id: id заявки на продажу продукта из register_inquiry
        Упадет с ошибкой, если подключение не завершилось успешно
        """
        connect_timeout = 75
        self.wait_allowed_next_activity("WAITING_FOR_A_PERMISSION")
        wait_that(
            lambda: self.inquiry_forward_step(app_id=inquiry_id, step=InquiryApiSteps.agreement_step).status_code == 204,
            timeout=connect_timeout,
            sleep_seconds=15,
            exception=AssertionError,
            message=f"Заявка на подключение не выполнилась за {connect_timeout} секунд",
        )

    @allure.step("API: Перейти на следующий шаг после установки даты активации")
    def forward_after_activation_date_set(self, inquiry_id: int) -> None:
        """
        Смена даты активации продукта
        :param inquiry_id: id заявки на продажу продукта
        """
        connect_timeout = 75
        self.wait_allowed_next_activity("SALE_CLOSE", test_context.client.inquiry.id)
        wait_that(
            lambda: self.inquiry_forward_step(inquiry_id, InquiryApiSteps.sale_close).status_code == 204,
            timeout=connect_timeout,
            sleep_seconds=15,
            exception=AssertionError,
            message=f"Заявка на смену даты активации не выполнилась за {connect_timeout} секунд",
        )

    def _normalize_custom_properties_for_update(self, custom_properties: list[CustomProperty]) -> list[dict]:
        """
        Метод для нормализации customProperties перед обновлением заявки.

        :param custom_properties: список customProperties из GET заявки.
        :return: список customProperties в формате PUT запроса.
        """
        normalized: list[dict] = []

        scalar_value_key_by_type: dict[str, str] = {
            "BOOL": "booleanValue",
            "NUMBER": "numberValue",
            "STRING": "stringValue",
            "DATE": "dateValue",
        }

        for prop in custom_properties:
            declaration = prop.customPropertyDeclaration
            code = declaration.customPropertyDeclarationCode
            prop_type = prop.type

            scalar_key = scalar_value_key_by_type.get(prop_type)
            if scalar_key is not None:
                normalized.append(
                    self.get_inquiry_property(
                        code,
                        prop_type,
                        **{scalar_key: getattr(prop, scalar_key)},
                    )
                )
                continue

            if prop_type in {"DICTIONARY", "WEB_COMPONENT"}:
                values: list[dict] = []

                for value in prop.values:
                    cleaned: dict = {}

                    if value.get("prefix") is not None:
                        cleaned["prefix"] = value["prefix"]

                    if value.get("itemId") is not None:
                        cleaned["itemId"] = value["itemId"]
                    elif value.get("itemCode") is not None:
                        cleaned["itemCode"] = value["itemCode"]
                    else:
                        continue

                    values.append(cleaned)

                normalized.append(self.get_inquiry_property(code, prop_type, values=values))
                continue

            if prop_type == "DB_QUERY":
                values = [{"value": v["value"]} for v in (prop.values or []) if v.get("value") is not None]
                normalized.append(self.get_inquiry_property(code, prop_type, values=values))
                continue

            raise ValueError(f"Неподдерживаемый тип customProperty: {prop_type}")

        return normalized

    @allure.step("API: updateInquiry — обновить BOOL customProperty '{property_code}' = {value}")
    def update_inquiry_boolean_custom_property(
        self,
        inquiry_id: int,
        property_code: str,
        value: bool,
    ) -> GeneralResponse:
        """
        Метод для обновления BOOL customProperty в заявке.

        :param inquiry_id: id заявки.
        :param property_code: код customProperty.
        :param value: значение BOOL customProperty.
        :return: ответ API после обновления заявки.
        """
        inquiry = self.get_inquiry_info(inquiry_id)

        target_property = next(
            (
                prop
                for prop in inquiry.customProperties
                if prop.customPropertyDeclaration.customPropertyDeclarationCode == property_code
            ),
            None,
        )

        assert target_property, f"customProperty '{property_code}' не найден в заявке {inquiry_id}"

        target_property.type = "BOOL"
        target_property.booleanValue = value

        cleaned_properties: list[CustomProperty] = []

        for prop in inquiry.customProperties:
            code = prop.customPropertyDeclaration.customPropertyDeclarationCode

            if code == "agtrmTermAgreement":
                text_value = str(prop.textValue).lower()
                values = prop.values

                first_value_name = (
                    str(values[0].get("name")).lower()
                    if values and isinstance(values, list) and isinstance(values[0], dict)
                    else ""
                )

                if "unknown item" in text_value or "unknown item" in first_value_name:
                    continue

            cleaned_properties.append(prop)

        payload = {
            "externalId": inquiry.externalId,
            "topic": {
                "topicId": inquiry.topic.topicId,
                "topicCode": inquiry.topic.topicCode,
            },
            "subscriber": ({"subscriberId": inquiry.subscriber.subscriberId} if inquiry.subscriber else None),
            "priority": {
                "inquiryPriorityId": inquiry.priority.inquiryPriorityId,
                "inquiryPriorityCode": inquiry.priority.inquiryPriorityCode,
            },
            "planCloseDate": inquiry.planCloseDate,
            "description": inquiry.description,
            "currentState": {"reportNote": inquiry.currentState.reportNote},
            "phone": inquiry.phone,
            "email": inquiry.email,
            "customProperties": self._normalize_custom_properties_for_update(cleaned_properties),
            "attachments": [],
        }

        response = self.put(
            url=f"{BASE_URL_API}/openapi/v1/inquiries/{inquiry_id}",
            params={"getObject": "true"},
            json=payload,
        )
        self.check_response_status(response, 200, "Не удалось обновить заявку")
        return response

    def assert_custom_property_bool_by_code(
        self,
        inquiry_id: int,
        custom_property_code: str,
        expected_value: bool,
    ) -> None:
        """
        Проверяет boolean custom property по declarationCode в данных заявки.

        Получает информацию по заявке через API, находит custom property
        с указанным declarationCode и валидирует:
        - наличие customProperties в ответе;
        - наличие custom property с заданным code;
        - тип custom property равен BOOL;
        - значение booleanValue соответствует ожидаемому.

        :param inquiry_id: ID заявки, по которой выполняется проверка
        :param custom_property_code: declarationCode custom property
        :param expected_value: ожидаемое boolean значение custom property
        :raises AssertionError: если custom property отсутствует, имеет неверный тип
                                или значение не соответствует ожидаемому
        """
        response = self.get_inquiry_info(inquiry_id)

        custom_properties = response.customProperties
        assert custom_properties, "В ответе отсутствует customProperties"

        prop = next(
            (
                p
                for p in custom_properties
                if p.customPropertyDeclaration.customPropertyDeclarationCode == custom_property_code
            ),
            None,
        )

        assert prop is not None, f"Custom property с code '{custom_property_code}' не найден"

        assert prop.type == "BOOL", f"Custom property '{custom_property_code}' имеет тип {prop.type}, ожидается BOOL"

        assert prop.booleanValue == expected_value, (
            f"Custom property '{custom_property_code}': booleanValue={prop.booleanValue}, ожидалось {expected_value}"
        )

    @allure.step("API: Ожидание появления у заявки нужной активности")
    def wait_allowed_next_activity(self, activity_code: str, id: int = None) -> None:
        """
        Ожидание появления доступного действия для заявки
        :param id: Id заявки или коммерческого заказа (test_context.client.inquiry.id, test_context.client.inquiry.commercial_order_number)
        """
        id = id if id is not None else test_context.client.inquiry.commercial_order_number

        wait_that(
            lambda: activity_code in self.get_next_activity(id),
            timeout=45,
            sleep_seconds=5,
            exception=AssertionError,
            message=lambda: f"Не появилось доступное действие {activity_code} для заявки",
        )

    @allure.step("API: Получение следующих доступных активностей")
    def get_next_activity(self, id: int) -> list | None:
        """
        Получение списка доступных действий заявки
        :param id: Id заявки или коммерческого заказа (test_context.client.inquiry.id, test_context.client.inquiry.commercial_order_number)
        :return: возвращает список доступных действий или None, если таковых нет
        """
        params = {"includeDisabled": False}
        response_activity = self.post(
            f"{BASE_URL_API}/openapi/v1/inquiries/{id}/nextActivities",
            params=params,
        )
        self.check_response_status(response_activity, 200, "Не получены доступные действия для заявки")
        activity_json = response_activity.json()
        if activity_json.get("items") is not None:
            return [item.get("targetActivity").get("activityCode") for item in activity_json.get("items")]
        return None
