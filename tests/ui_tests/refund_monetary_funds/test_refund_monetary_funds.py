import re

import allure
import pytest
from playwright.sync_api import APIRequestContext, Page

from api.nbss.finances.payments_requests import PaymentsRequests
from api.nbss.inquiry_requests import InquiryRequests
from api.nbss.personal_account_requests import PersonalAccountRequests
from common.helpers.time_helpers import delay
from models.user import IndividualClient
from pages.base_page import BasePage
from pages.client_profile_page import ClientProfilePage
from pages.locators.dynamic_form_elements import ChooseRequestTopic, ForwardInquiryForm, RequestCreate
from pages.locators.inquiries_elements import RefundInquiryForm


@allure.epic("E2E_70 Возврат монетарных средств")
@allure.suite("E2E_70 Возврат монетарных средств")
@allure.link(
    url="confluence.nexign.com/pages/viewpage.action?pageId=725107101",
    name="RMBSS-6990 Возврат монетарных средств",
)
@pytest.mark.regress
class TestRefundMonetaryFunds:
    @pytest.fixture(autouse=True)
    def setup(
        self,
        nexign_ui_stand_login: Page,
        api_request_context: APIRequestContext,
        create_user_with_agreement_and_account: IndividualClient,
    ) -> None:
        self.base_page = BasePage(nexign_ui_stand_login)
        self.client_profile = ClientProfilePage(nexign_ui_stand_login)
        self.request_create = RequestCreate(nexign_ui_stand_login)
        self.inquiries_page = RefundInquiryForm(nexign_ui_stand_login)
        self.choose_request_topic = ChooseRequestTopic(nexign_ui_stand_login)
        self.forward_inquiry_form = ForwardInquiryForm(nexign_ui_stand_login)
        self.personal_account_api = PersonalAccountRequests(api_request_context)
        self.payment_api = PaymentsRequests(api_request_context)
        self.client_info = create_user_with_agreement_and_account
        self.inquiry_api = InquiryRequests(api_request_context)

        with allure.step("Подготовить тестовые данные"):
            self.payment_api.create_default_payment(self.client_info.agreements[0].accounts[0].id, 1000)
            self.personal_account_api.wait_check_current_main_balance(
                self.client_info.agreements[0].accounts[0].id, 1000
            )

    @allure.title("Регистрация возврата суммы")
    @allure.description("Регистрация возврата суммы")
    @allure.id(579567)
    def test_registering_refund(self, base_url: str) -> None:
        with allure.step("Перейти в контекст клиента и создать заявку"):
            self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{self.client_info.user_id}/overview")
            self.client_profile.locators.CLIENT_FIO.wait_to_be_visible()
            self.client_profile.locators.CREATE_REQUEST.click()
            self.request_create.CREATE_FORM.wait_to_be_visible()
            self.request_create.TITLE.to_contain_text("Создание заявки")

        with allure.step("Выбрать тему заявки"):
            self.request_create.TOPIC.check_attribute_by_value("aria-required", "true")
            self.request_create.TOPIC.click()
            self.choose_request_topic.choose_topic(
                ["(2) 02 Расчетно-справочное обслуживание", "(202) Возврат денежных средств"]
            )
            self.choose_request_topic.CHOOSE_REQUEST_TOPIC_FORM.not_to_be_visible()
            self.request_create.CREATE_FORM.wait_to_be_visible()
            delay(2, reason="Ожидание подгрузки данных в полях")
            self.request_create.CODE.to_contain_text("202")
            self.request_create.TOPIC.to_contain_text("Возврат денежных средств")

        with allure.step("Заполнить параметры и создать заявку"):
            self.request_create.ACCOUNT_FIELD.select_by_value(self.client_info.agreements[0].accounts[0].number)
            self.request_create.RETURN_TYPE_FIELD.select_by_value("Сумма")
            self.request_create.REFUND_BALANCE.fill("500")
            self.request_create.FORWARD_BTN.wait_to_be_enabled()
            self.request_create.FORWARD_BTN.click()
            self.forward_inquiry_form.FORWARD_FORM.wait_to_be_visible()
            self.forward_inquiry_form.TITLE.wait_to_have_text("Передача на обработку")
            self.forward_inquiry_form.PROCESS_FIELD.to_contain_text("Согласование возврата денежных средств")
            self.forward_inquiry_form.QUEUE_FIELD.to_contain_text("Согласование возврата денежных средств")
            self.forward_inquiry_form.FORWARD_BTN.wait_to_be_enabled()
            self.forward_inquiry_form.FORWARD_BTN.click()
            self.forward_inquiry_form.INFO_MESSAGE.wait_to_be_visible()
            self.forward_inquiry_form.INFO_MESSAGE.wait_to_have_text(re.compile(r"Заявка \d+ создана\."))
            inquiry_id = self.forward_inquiry_form.INFO_MESSAGE.text.split()[1]

        with allure.step("Перейти на созданную заявку"):
            self.client_profile.locators.REQUESTS_TAB.click()
            delay(5, reason="Ожидание подгрузки данных в полях")
            self.client_profile.locators.REQUESTS.wait_to_be_visible()
            self.client_profile.locators.REQUESTS.wait_to_have_count(1)
            self.client_profile.locators.REQUEST_NUMBER[0].wait_to_have_text(inquiry_id)
            self.client_profile.locators.REQUEST_NUMBER[0].click()
            self.inquiries_page.REFUND_INQUIRY_NAME.wait_to_have_text(re.compile(r"\d\. Возврат денежных средств"))
            self.inquiries_page.REFUND_INQUIRY_STATUS.wait_to_have_text("Ожидает обработки")

        with allure.step("Взять созданную заявку в работу"):
            self.inquiries_page.REFUND_PROCESSING_BTN.click()
            self.inquiries_page.REFUND_TAKE_IN_PROC_BTN.click()
            self.inquiries_page.REFUND_REFRESH_BTN.click()
            self.inquiries_page.REFUND_INQUIRY_STATUS.wait_to_have_text("Обрабатывается")

        with allure.step("Согласовать созданную заявку"):
            self.inquiries_page.REFUND_EDIT_BTN.wait_to_be_enabled()
            self.inquiries_page.REFUND_EDIT_BTN.click()
            self.inquiries_page.APPROVAL_STATUS_REFUND_FORM.select_by_value("Согласовано")
            self.inquiries_page.REFUND_SAVE_BTN.click()
            self.inquiries_page.REFUND_INQUIRY_SOLUTION_STATUS.wait_to_have_text("Согласовано")

        with allure.step("Передать заявку в автоматическую очередь"):
            self.inquiries_page.REFUND_PROCESSING_BTN.click()
            self.inquiries_page.REFUND_SUBMIT_PROC_BTN.click()
            self.forward_inquiry_form.FORWARD_FORM.wait_to_be_visible()
            self.forward_inquiry_form.TITLE.wait_to_have_text("Передача на обработку")
            self.forward_inquiry_form.PROCESS_FIELD.to_contain_text("Выполнение возврата")
            self.forward_inquiry_form.QUEUE_FIELD.to_contain_text("Автоматичеcкая очередь возврата денежных средств")
            self.forward_inquiry_form.FORWARD_BTN.wait_to_be_enabled()
            self.forward_inquiry_form.FORWARD_BTN.click()
            self.inquiries_page.REFUND_INQUIRY_STATUS.wait_to_have_text("Ожидает обработки")
            self.inquiry_api.wait_inquiry_status(inquiry_id)
            self.inquiries_page.REFUND_REFRESH_BTN.click()
            self.inquiries_page.REFUND_INQUIRY_STATUS.wait_to_have_text("Закрыто")
            self.personal_account_api.wait_check_current_main_balance(self.client_info.agreements[0].accounts[0].id, 500)

    @allure.title("Регистрация возврата платежа")
    @allure.description("Регистрация возврата платежа")
    @allure.id(580011)
    def test_registering_refund_payment(self, base_url: str) -> None:
        with allure.step("Перейти в контекст клиента и создать заявку"):
            self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{self.client_info.user_id}/overview")
            self.client_profile.locators.CLIENT_FIO.wait_to_be_visible()
            self.client_profile.locators.CREATE_REQUEST.click()
            self.request_create.CREATE_FORM.wait_to_be_visible()
            self.request_create.TITLE.to_contain_text("Создание заявки")

        with allure.step("Выбрать тему заявки"):
            self.request_create.TOPIC.check_attribute_by_value("aria-required", "true")
            self.request_create.TOPIC.click()
            self.choose_request_topic.choose_topic(
                ["(2) 02 Расчетно-справочное обслуживание", "(202) Возврат денежных средств"]
            )
            self.choose_request_topic.CHOOSE_REQUEST_TOPIC_FORM.not_to_be_visible()
            self.request_create.CREATE_FORM.wait_to_be_visible()
            delay(2, reason="Ожидание подгрузки данных в полях")
            self.request_create.CODE.to_contain_text("202")
            self.request_create.TOPIC.to_contain_text("Возврат денежных средств")

        with allure.step("Заполнить параметры и создать заявку"):
            self.request_create.ACCOUNT_FIELD.select_by_value(self.client_info.agreements[0].accounts[0].number)
            self.request_create.RETURN_TYPE_FIELD.select_by_value("Платеж")
            self.request_create.RETURN_PAYMENT_FIELD.click()
            self.request_create.RETURN_PAYMENT_ELEMENT_FIELD.wait_to_be_visible()
            self.request_create.RETURN_PAYMENT_ELEMENT_FIELD.click()
            self.request_create.REFUND_BALANCE.fill("1000")
            self.request_create.FORWARD_BTN.wait_to_be_enabled()
            self.request_create.FORWARD_BTN.click()
            self.forward_inquiry_form.FORWARD_FORM.wait_to_be_visible()
            self.forward_inquiry_form.TITLE.wait_to_have_text("Передача на обработку")
            self.forward_inquiry_form.PROCESS_FIELD.to_contain_text("Согласование возврата денежных средств")
            self.forward_inquiry_form.QUEUE_FIELD.to_contain_text("Согласование возврата денежных средств")
            self.forward_inquiry_form.FORWARD_BTN.wait_to_be_enabled()
            self.forward_inquiry_form.FORWARD_BTN.click()
            self.forward_inquiry_form.INFO_MESSAGE.wait_to_be_visible()
            self.forward_inquiry_form.INFO_MESSAGE.wait_to_have_text(re.compile(r"Заявка \d+ создана\."))
            inquiry_id = self.forward_inquiry_form.INFO_MESSAGE.text.split()[1]

        with allure.step("Перейти на созданную заявку"):
            self.client_profile.locators.REQUESTS_TAB.click()
            delay(5, reason="Ожидание подгрузки данных в полях")
            self.client_profile.locators.REQUESTS.wait_to_be_visible()
            self.client_profile.locators.REQUESTS.wait_to_have_count(1)
            self.client_profile.locators.REQUEST_NUMBER[0].wait_to_have_text(inquiry_id)
            self.client_profile.locators.REQUEST_NUMBER[0].click()
            self.inquiries_page.REFUND_INQUIRY_NAME.wait_to_have_text(re.compile(r"\d\. Возврат денежных средств"))
            self.inquiries_page.REFUND_INQUIRY_STATUS.wait_to_have_text("Ожидает обработки")

        with allure.step("Взять созданную заявку в работу"):
            self.inquiries_page.REFUND_PROCESSING_BTN.click()
            self.inquiries_page.REFUND_TAKE_IN_PROC_BTN.click()
            self.inquiries_page.REFUND_REFRESH_BTN.click()
            self.inquiries_page.REFUND_INQUIRY_STATUS.wait_to_have_text("Обрабатывается")

        with allure.step("Согласовать созданную заявку"):
            self.inquiries_page.REFUND_EDIT_BTN.wait_to_be_enabled()
            self.inquiries_page.REFUND_EDIT_BTN.click()
            self.inquiries_page.APPROVAL_STATUS_REFUND_FORM.select_by_value("Согласовано")
            self.inquiries_page.REFUND_SAVE_BTN.click()
            self.inquiries_page.REFUND_INQUIRY_SOLUTION_STATUS.wait_to_have_text("Согласовано")

        with allure.step("Передать заявку в автоматическую очередь"):
            self.inquiries_page.REFUND_PROCESSING_BTN.click()
            self.inquiries_page.REFUND_SUBMIT_PROC_BTN.click()
            self.forward_inquiry_form.FORWARD_FORM.wait_to_be_visible()
            self.forward_inquiry_form.TITLE.wait_to_have_text("Передача на обработку")
            self.forward_inquiry_form.PROCESS_FIELD.to_contain_text("Выполнение возврата")
            self.forward_inquiry_form.QUEUE_FIELD.to_contain_text("Автоматичеcкая очередь возврата денежных средств")
            self.forward_inquiry_form.FORWARD_BTN.wait_to_be_enabled()
            self.forward_inquiry_form.FORWARD_BTN.click()
            self.inquiries_page.REFUND_INQUIRY_STATUS.wait_to_have_text("Ожидает обработки")
            self.inquiry_api.wait_inquiry_status(inquiry_id)
            self.inquiries_page.REFUND_REFRESH_BTN.click()
            self.inquiries_page.REFUND_INQUIRY_STATUS.wait_to_have_text("Закрыто")
            self.personal_account_api.wait_check_current_main_balance(self.client_info.agreements[0].accounts[0].id, 0)

    @allure.title("Попытка возврата монетарных средств при недостаточной доступной для возврата сумме ФЛ")
    @allure.description("Попытка возврата монетарных средств при недостаточной доступной для возврата сумме ФЛ")
    @allure.id(579684)
    def test_refund_amount_exceeds_allowed_amount(self, base_url: str) -> None:
        with allure.step("Перейти в контекст клиента и создать заявку"):
            self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{self.client_info.user_id}/overview")
            self.client_profile.locators.CLIENT_FIO.wait_to_be_visible()
            self.client_profile.locators.CREATE_REQUEST.click()
            self.request_create.CREATE_FORM.wait_to_be_visible()
            self.request_create.TITLE.to_contain_text("Создание заявки")

        with allure.step("Выбрать тему заявки"):
            self.request_create.TOPIC.check_attribute_by_value("aria-required", "true")
            self.request_create.TOPIC.click()
            self.choose_request_topic.choose_topic(
                ["(2) 02 Расчетно-справочное обслуживание", "(202) Возврат денежных средств"]
            )
            self.choose_request_topic.CHOOSE_REQUEST_TOPIC_FORM.not_to_be_visible()
            self.request_create.CREATE_FORM.wait_to_be_visible()
            delay(2, reason="Ожидание подгрузки данных в полях")
            self.request_create.CODE.to_contain_text("202")
            self.request_create.TOPIC.to_contain_text("Возврат денежных средств")

        with allure.step("Заполнить параметры и создать заявку"):
            self.request_create.ACCOUNT_FIELD.select_by_value(self.client_info.agreements[0].accounts[0].number)
            self.request_create.RETURN_TYPE_FIELD.select_by_value("Сумма")
            self.request_create.REFUND_BALANCE.fill("2000")
            self.request_create.WARNING_REFUND_FIELD.wait_to_be_visible()
            self.request_create.WARNING_REFUND_FIELD.to_contain_text("Сумма возврата превышает текущий баланс")
            self.request_create.FORWARD_BTN.wait_to_be_enabled()
            self.request_create.FORWARD_BTN.click()
            self.forward_inquiry_form.FORWARD_FORM.wait_to_be_visible()
            self.forward_inquiry_form.ERROR_FIELD.to_contain_text(
                "Передача заявки невозможна: сумма к возврату некорректна или возврат запрещен для клиента с повышенным уровнем риска"
            )

    @allure.title("Несогласование заявки на возврат суммы")
    @allure.description("Несогласование заявки на возврат суммы")
    @allure.id(580014)
    def test_disagreement_refund(self, base_url: str) -> None:
        with allure.step("Перейти в контекст клиента и создать заявку"):
            self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{self.client_info.user_id}/overview")
            self.client_profile.locators.CLIENT_FIO.wait_to_be_visible()
            self.client_profile.locators.CREATE_REQUEST.click()
            self.request_create.CREATE_FORM.wait_to_be_visible()
            self.request_create.TITLE.to_contain_text("Создание заявки")

        with allure.step("Выбрать тему заявки"):
            self.request_create.TOPIC.check_attribute_by_value("aria-required", "true")
            self.request_create.TOPIC.click()
            self.choose_request_topic.choose_topic(
                ["(2) 02 Расчетно-справочное обслуживание", "(202) Возврат денежных средств"]
            )
            self.choose_request_topic.CHOOSE_REQUEST_TOPIC_FORM.not_to_be_visible()
            self.request_create.CREATE_FORM.wait_to_be_visible()
            delay(2, reason="Ожидание подгрузки данных в полях")
            self.request_create.CODE.to_contain_text("202")
            self.request_create.TOPIC.to_contain_text("Возврат денежных средств")

        with allure.step("Заполнить параметры и создать заявку"):
            self.request_create.ACCOUNT_FIELD.select_by_value(self.client_info.agreements[0].accounts[0].number)
            self.request_create.RETURN_TYPE_FIELD.select_by_value("Сумма")
            self.request_create.REFUND_BALANCE.fill("500")
            self.request_create.FORWARD_BTN.wait_to_be_enabled()
            self.request_create.FORWARD_BTN.click()
            self.forward_inquiry_form.FORWARD_FORM.wait_to_be_visible()
            self.forward_inquiry_form.TITLE.wait_to_have_text("Передача на обработку")
            self.forward_inquiry_form.PROCESS_FIELD.to_contain_text("Согласование возврата денежных средств")
            self.forward_inquiry_form.QUEUE_FIELD.to_contain_text("Согласование возврата денежных средств")
            self.forward_inquiry_form.FORWARD_BTN.wait_to_be_enabled()
            self.forward_inquiry_form.FORWARD_BTN.click()
            self.forward_inquiry_form.INFO_MESSAGE.wait_to_be_visible()
            self.forward_inquiry_form.INFO_MESSAGE.wait_to_have_text(re.compile(r"Заявка \d+ создана\."))
            inquiry_id = self.forward_inquiry_form.INFO_MESSAGE.text.split()[1]

        with allure.step("Перейти на созданную заявку"):
            self.client_profile.locators.REQUESTS_TAB.click()
            delay(5, reason="Ожидание подгрузки данных в полях")
            self.client_profile.locators.REQUESTS.wait_to_be_visible()
            self.client_profile.locators.REQUESTS.wait_to_have_count(1)
            self.client_profile.locators.REQUEST_NUMBER[0].wait_to_have_text(inquiry_id)
            self.client_profile.locators.REQUEST_NUMBER[0].click()
            self.inquiries_page.REFUND_INQUIRY_NAME.wait_to_have_text(re.compile(r"\d\. Возврат денежных средств"))
            self.inquiries_page.REFUND_INQUIRY_STATUS.wait_to_have_text("Ожидает обработки")

        with allure.step("Взять созданную заявку в работу"):
            self.inquiries_page.REFUND_PROCESSING_BTN.click()
            self.inquiries_page.REFUND_TAKE_IN_PROC_BTN.click()
            self.inquiries_page.REFUND_REFRESH_BTN.click()
            self.inquiries_page.REFUND_INQUIRY_STATUS.wait_to_have_text("Обрабатывается")

        with allure.step("Не согласовать созданную заявку"):
            self.inquiries_page.REFUND_EDIT_BTN.wait_to_be_enabled()
            self.inquiries_page.REFUND_EDIT_BTN.click()
            self.inquiries_page.APPROVAL_STATUS_REFUND_FORM.select_by_value("Не согласовано")
            self.inquiries_page.REFUND_SAVE_BTN.click()
            self.inquiries_page.REFUND_INQUIRY_SOLUTION_STATUS.wait_to_have_text("Не согласовано")

        with allure.step("Передать заявку в автоматическую очередь"):
            self.inquiries_page.REFUND_PROCESSING_BTN.click()
            self.inquiries_page.REFUND_SUBMIT_PROC_BTN.click()
            self.forward_inquiry_form.FORWARD_FORM.wait_to_be_visible()
            self.forward_inquiry_form.ERROR_FIELD.to_contain_text(
                "Невозможно перейти на данный шаг, т.к. возврат не согласован"
            )

    @allure.title("Согласование заявки на возврат")
    @allure.description("Согласование заявки на возврат")
    @allure.id(580028)
    def test_re_agreement_refund(self, base_url: str) -> None:
        with allure.step("Перейти в контекст клиента и создать заявку"):
            self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{self.client_info.user_id}/overview")
            self.client_profile.locators.CLIENT_FIO.wait_to_be_visible()
            self.client_profile.locators.CREATE_REQUEST.click()
            self.request_create.CREATE_FORM.wait_to_be_visible()
            self.request_create.TITLE.to_contain_text("Создание заявки")

        with allure.step("Выбрать тему заявки"):
            self.request_create.TOPIC.check_attribute_by_value("aria-required", "true")
            self.request_create.TOPIC.click()
            self.choose_request_topic.choose_topic(
                ["(2) 02 Расчетно-справочное обслуживание", "(202) Возврат денежных средств"]
            )
            self.choose_request_topic.CHOOSE_REQUEST_TOPIC_FORM.not_to_be_visible()
            self.request_create.CREATE_FORM.wait_to_be_visible()
            delay(2, reason="Ожидание подгрузки данных в полях")
            self.request_create.CODE.to_contain_text("202")
            self.request_create.TOPIC.to_contain_text("Возврат денежных средств")

        with allure.step("Заполнить параметры и создать заявку"):
            self.request_create.ACCOUNT_FIELD.select_by_value(self.client_info.agreements[0].accounts[0].number)
            self.request_create.RETURN_TYPE_FIELD.select_by_value("Сумма")
            self.request_create.REFUND_BALANCE.fill("500")
            self.request_create.FORWARD_BTN.wait_to_be_enabled()
            self.request_create.FORWARD_BTN.click()
            self.forward_inquiry_form.FORWARD_FORM.wait_to_be_visible()
            self.forward_inquiry_form.TITLE.wait_to_have_text("Передача на обработку")
            self.forward_inquiry_form.PROCESS_FIELD.to_contain_text("Согласование возврата денежных средств")
            self.forward_inquiry_form.QUEUE_FIELD.to_contain_text("Согласование возврата денежных средств")
            self.forward_inquiry_form.FORWARD_BTN.wait_to_be_enabled()
            self.forward_inquiry_form.FORWARD_BTN.click()
            self.forward_inquiry_form.INFO_MESSAGE.wait_to_be_visible()
            self.forward_inquiry_form.INFO_MESSAGE.wait_to_have_text(re.compile(r"Заявка \d+ создана\."))
            inquiry_id = self.forward_inquiry_form.INFO_MESSAGE.text.split()[1]

        with allure.step("Перейти на созданную заявку"):
            self.client_profile.locators.REQUESTS_TAB.click()
            delay(5, reason="Ожидание подгрузки данных в полях")
            self.client_profile.locators.REQUESTS.wait_to_be_visible()
            self.client_profile.locators.REQUESTS.wait_to_have_count(1)
            self.client_profile.locators.REQUEST_NUMBER[0].wait_to_have_text(inquiry_id)
            self.client_profile.locators.REQUEST_NUMBER[0].click()
            self.inquiries_page.REFUND_INQUIRY_NAME.wait_to_have_text(re.compile(r"\d\. Возврат денежных средств"))
            self.inquiries_page.REFUND_INQUIRY_STATUS.wait_to_have_text("Ожидает обработки")

        with allure.step("Взять созданную заявку в работу"):
            self.inquiries_page.REFUND_PROCESSING_BTN.click()
            self.inquiries_page.REFUND_TAKE_IN_PROC_BTN.click()
            self.inquiries_page.REFUND_REFRESH_BTN.click()
            self.inquiries_page.REFUND_INQUIRY_STATUS.wait_to_have_text("Обрабатывается")

        with allure.step("Не согласовывать созданную заявку"):
            self.inquiries_page.REFUND_EDIT_BTN.wait_to_be_enabled()
            self.inquiries_page.REFUND_EDIT_BTN.click()
            self.inquiries_page.APPROVAL_STATUS_REFUND_FORM.select_by_value("Не согласовано")
            self.inquiries_page.REFUND_SAVE_BTN.click()
            self.inquiries_page.REFUND_INQUIRY_SOLUTION_STATUS.wait_to_have_text("Не согласовано")

        with allure.step("Передать заявку в автоматическую очередь"):
            self.inquiries_page.REFUND_PROCESSING_BTN.click()
            self.inquiries_page.REFUND_SUBMIT_PROC_BTN.click()
            self.forward_inquiry_form.FORWARD_FORM.wait_to_be_visible()
            self.forward_inquiry_form.ERROR_FIELD.to_contain_text(
                "Невозможно перейти на данный шаг, т.к. возврат не согласован"
            )

        with allure.step("Перейти в контекст клиента и открыть заявку"):
            self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{self.client_info.user_id}/overview")
            self.client_profile.locators.CLIENT_FIO.wait_to_be_visible()
            self.client_profile.locators.REQUESTS_TAB.click()
            delay(5, reason="Ожидание подгрузки данных в полях")
            self.client_profile.locators.REQUESTS.wait_to_be_visible()
            self.client_profile.locators.REQUESTS.wait_to_have_count(1)
            self.client_profile.locators.REQUEST_NUMBER[0].wait_to_have_text(inquiry_id)
            self.client_profile.locators.REQUEST_NUMBER[0].click()
            self.inquiries_page.REFUND_REFRESH_BTN.click()
            self.inquiries_page.REFUND_INQUIRY_NAME.wait_to_have_text(re.compile(r"\d\. Возврат денежных средств"))
            self.inquiries_page.REFUND_INQUIRY_STATUS.wait_to_have_text("Обрабатывается")

        with allure.step("Согласовать заявку"):
            self.inquiries_page.REFUND_EDIT_BTN.wait_to_be_enabled()
            self.inquiries_page.REFUND_EDIT_BTN.click()
            self.inquiries_page.APPROVAL_STATUS_REFUND_FORM.select_by_value("Согласовано")
            self.inquiries_page.REFUND_SAVE_BTN.click()
            self.inquiries_page.REFUND_INQUIRY_SOLUTION_STATUS.wait_to_have_text("Согласовано")

        with allure.step("Передать заявку в автоматическую очередь"):
            self.inquiries_page.REFUND_PROCESSING_BTN.click()
            self.inquiries_page.REFUND_SUBMIT_PROC_BTN.click()
            self.forward_inquiry_form.FORWARD_FORM.wait_to_be_visible()
            self.forward_inquiry_form.TITLE.wait_to_have_text("Передача на обработку")
            self.forward_inquiry_form.PROCESS_FIELD.to_contain_text("Выполнение возврата")
            self.forward_inquiry_form.QUEUE_FIELD.to_contain_text("Автоматичеcкая очередь возврата денежных средств")
            self.forward_inquiry_form.FORWARD_BTN.wait_to_be_enabled()
            self.forward_inquiry_form.FORWARD_BTN.click()
            self.inquiries_page.REFUND_INQUIRY_STATUS.wait_to_have_text("Ожидает обработки")
            self.inquiry_api.wait_inquiry_status(inquiry_id)
            self.inquiries_page.REFUND_REFRESH_BTN.click()
            self.inquiries_page.REFUND_INQUIRY_STATUS.wait_to_have_text("Закрыто")
            self.personal_account_api.wait_check_current_main_balance(self.client_info.agreements[0].accounts[0].id, 500)
