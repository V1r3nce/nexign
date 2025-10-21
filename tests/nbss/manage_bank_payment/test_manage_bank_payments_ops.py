import re
from datetime import timedelta, timezone

import allure
import pytest
from playwright.sync_api import APIRequestContext, Page

from api.exceptions import UpdateStatusException
from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from api.nbss.finances.adjustment_requests import AdjustmentRequests
from api.nbss.finances.payments_requests import PaymentsRequests, PaymentsUniblpRequests, PaymentUniblpInfo
from api.nbss.finances.registry_requests import RegistryRequests
from api.nbss.personal_account_requests import PersonalAccountRequests
from common.helpers.checker import wait_that
from common.helpers.data_generator import (
    generate_random_number,
    get_current_datetime_string,
    get_current_datetime_string_for_api,
)
from common.helpers.time_helpers import delay, get_shifted_datetime
from models.user import IndividualClient
from pages.base_page import BasePage
from pages.locators.nbss.dynamic_form_elements import CancelPaymentForm
from pages.locators.nbss.finances.payments_elements import PaymentCorrectionForm, PaymentDetailsElements
from pages.locators.nbss.finances.registry_elements import RegistryElements
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.finances.payments_page import PaymentsPage


@allure.epic("E2E_81 Управление банковскими платежами")
@allure.suite("E2E_81 Управление банковскими платежами")
@allure.link(
    url="confluence.nexign.com/pages/viewpage.action?pageId=462935916",
    name="LLD Прием и аннулирование платежа",
)
@allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=471415127", name="ФС Прием платежей")
@pytest.mark.regress
@pytest.mark.nbss_portal
@pytest.mark.uniblp
class TestManageBankPayments:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_ui_stand_login: Page, api_request_context: APIRequestContext):
        self.base_page = BasePage(nexign_ui_stand_login)
        self.client_profile_page = ClientProfilePage(nexign_ui_stand_login)
        self.registry_elements = RegistryElements(nexign_ui_stand_login)
        self.payment_details_elements = PaymentDetailsElements(nexign_ui_stand_login)
        self.payment_page = PaymentsPage(nexign_ui_stand_login)
        self.cancel_payment_form = CancelPaymentForm(nexign_ui_stand_login)
        self.payment_correction_form = PaymentCorrectionForm(nexign_ui_stand_login)
        self.personal_account_api = PersonalAccountRequests(api_request_context)
        self.payment_api = PaymentsRequests(api_request_context)
        self.payment_api_uniblp = PaymentsUniblpRequests(api_request_context)
        self.registry_requests_api = RegistryRequests(api_request_context)
        self.client_request_api = ClientInquiriesRequests(api_request_context)
        self.adjustment_api = AdjustmentRequests(api_request_context)

    @allure.title("Аннулирование банковского платежа на форме 'Платежи'")
    @allure.id(580988)
    @allure.description("Аннулирование банковского платежа на форме 'Платежи'")
    def test_cancel_bank_payment_payments_form(
        self,
        base_url: str,
        api_request_context: APIRequestContext,
        create_user_with_agreement_and_account: IndividualClient,
    ):
        client_info = create_user_with_agreement_and_account
        payment_amount_1 = generate_random_number(3)
        payment_amount_2 = generate_random_number(3)
        today_user_friendly_view = get_current_datetime_string(is_full_format=False)
        doc_number_1 = generate_random_number(4)
        doc_number_2 = generate_random_number(4)
        payment_data_1 = PaymentUniblpInfo(
            amount=payment_amount_1, account_id=client_info.agreements[0].accounts[0].id, document_number=doc_number_1
        )
        self.payment_api_uniblp.wait_check_create_payment(payment_data_1)
        self.payment_api_uniblp.create_payment(payment_data_1)
        payment_data_2 = PaymentUniblpInfo(
            amount=payment_amount_2, account_id=client_info.agreements[0].accounts[0].id, document_number=doc_number_2
        )
        self.payment_api_uniblp.create_payment(payment_data_2)

        wait_that(
            lambda: len(
                self.payment_api.get_payments(client_info.agreements[0].accounts[0].id, "-paymentDate").json()["items"]
            )
            == 2,
            exception=UpdateStatusException,
            timeout=25,
            sleep_seconds=0.5,
            message="Платеж не появился в указанное время",
        )
        self.base_page.open(
            f"{base_url}customer-hierarchy-management/accounts/{client_info.agreements[0].accounts[0].id}/account"
        )
        self.base_page.base_elements.CONTEXT_ELEMENT.wait_for_text_in_all(["Лицевой счет"], timeout=10000)
        self.client_profile_page.locators.BURGER_MENU.select_by_value("Финансы > Платежи")

        self.payment_page.locators.CHECK_NUM_FIELDS.wait_to_be_visible()
        self.payment_page.locators.CHECK_NUM_FIELDS.to_contain_text(0, str(doc_number_2))
        self.payment_page.locators.PAYMENT_DATES_FIELDS.to_contain_text(0, today_user_friendly_view)
        self.payment_page.locators.REGISTRY_DATES_FIELDS.to_contain_text(0, today_user_friendly_view)
        self.payment_page.locators.SUM_FIELDS.to_contain_text(0, f"{payment_data_2.amount}.00")
        self.payment_page.locators.STATUS_FIELDS.to_contain_text(0, "Действует")

        self.payment_page.locators.CANCEL_PAYMENT_BTN.check_attribute_by_value("disabled", "")
        self.payment_page.locators.PAYMENT_DATES_FIELDS[0].click()
        delay(0.5, reason="Время на активацию кнопки")
        self.payment_page.locators.CANCEL_PAYMENT_BTN.element_not_contain_disabled_attribute()
        self.payment_page.locators.CANCEL_PAYMENT_BTN.click()

        self.cancel_payment_form.TITLE.wait_to_have_text("Аннулирование платежа")
        self.cancel_payment_form.SUBTITLE.to_contain_text(
            f"На сумму {payment_data_2.amount}.00 от {today_user_friendly_view}"
        )
        self.cancel_payment_form.CANCEL_OPERATION_BTN.check_attribute_by_value("disabled", "")
        self.cancel_payment_form.CANCEL_REASON_INPUT.fill("Ошибочный платеж")
        self.cancel_payment_form.CANCEL_OPERATION_BTN.element_not_contain_disabled_attribute()
        self.cancel_payment_form.CANCEL_OPERATION_BTN.click()
        self.cancel_payment_form.TITLE.not_to_be_visible()

        self.payment_page.locators.CHECK_NUM_FIELDS.wait_to_be_visible()
        self.payment_page.locators.SUM_FIELDS[0].wait_to_have_text(f"{payment_data_2.amount}.00")
        self.payment_page.locators.STATUS_FIELDS.to_contain_text(0, "Аннулирован")
        self.payment_page.locators.USER_BALANCE.wait_to_have_text(f"{payment_data_1.amount}.00")

        self.payment_page.locators.CHECK_NUM_FIELDS[0].click()

        self.payment_details_elements.FORM_TITLE.wait_to_have_text("Платёж")
        self.payment_details_elements.FORM_STATUS.wait_to_have_text("Аннулирован")
        (
            self.payment_details_elements.SUBTITLE.wait_to_have_text(
                re.compile(f"На сумму {payment_data_2.amount}.00 от {today_user_friendly_view}")
            )
        )
        self.payment_details_elements.PAYMENT_DETAILS[0].to_contain_text(today_user_friendly_view)
        self.payment_details_elements.PAYMENT_DETAILS[1].to_contain_text(today_user_friendly_view)
        self.payment_details_elements.PAYMENT_DETAILS[2].to_contain_text(str(doc_number_2))
        self.payment_details_elements.PAYMENT_DETAILS[3].to_contain_text(f"{payment_data_2.amount}.00")
        self.payment_details_elements.PAYMENT_DETAILS[4].wait_to_have_text(
            re.compile(rf"{payment_data_2.amount}.00\sRUB")
        )
        self.payment_details_elements.PAYMENT_DETAILS[6].to_contain_text("PM:pm_gateway")
        self.payment_details_elements.PAYMENT_DETAILS[8].to_contain_text("uniblp")
        self.payment_details_elements.PAYMENT_DETAILS[11].to_contain_text("Ошибочный платеж")

    @allure.title("Аннулирование банковского платежа на форме 'Реестры'")
    @allure.id(581098)
    @allure.description("Аннулирование банковского платежа на форме 'Реестры'")
    def test_cancel_bank_payment_registry_form(
        self, base_url: str, api_request_context: APIRequestContext, create_user_with_agreement_and_account
    ):
        client_info = create_user_with_agreement_and_account
        today = get_current_datetime_string_for_api(is_full_format=False)
        payment_amount = generate_random_number(3)
        today_user_friendly_view = get_current_datetime_string(is_full_format=False)
        doc_number = generate_random_number(4)
        payment_data = PaymentUniblpInfo(
            amount=payment_amount, account_id=client_info.agreements[0].accounts[0].id, document_number=doc_number
        )
        self.payment_api_uniblp.wait_check_create_payment(payment_data)
        self.payment_api_uniblp.create_payment(payment_data)
        self.registry_requests_api.wait_last_payment_amount_in_registry(today, doc_number, payment_amount)
        self.registry_requests_api.wait_payment_for_doc_successful(today, doc_number)

        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{client_info.user_id}/overview")
        self.base_page.base_elements.CONTEXT_ELEMENT.wait_for_text_in_all(["Клиент"], timeout=10000)
        self.client_profile_page.locators.BURGER_MENU.select_by_value("Платежные системы > Реестр платежей")

        self.registry_elements.CHECK_NUM_SEARCH.fill(str(doc_number))
        self.registry_elements.PAYMENT_DATES_FIELDS.wait_to_be_visible()
        self.registry_elements.PAYMENT_DATES_FIELDS.to_contain_text(0, today_user_friendly_view)
        self.registry_elements.STATUS_FIELDS.to_contain_text(0, "Действует")
        self.registry_elements.CHECK_NUM_FIELDS.to_contain_text(0, str(doc_number))
        self.registry_elements.CHECK_SUM_FIELDS.to_contain_text(0, str(payment_data.amount))
        self.registry_elements.PAYMENT_SUM_FIELDS.to_contain_text(0, str(payment_data.amount))
        self.registry_elements.CASHIER_FIELDS.to_contain_text(0, "uniblp/uniblp")

        self.registry_elements.CANCEL_PAYMENT_BTN.check_attribute_by_value("disabled", "")
        self.registry_elements.PAYMENT_DATES_FIELDS[0].click()
        self.registry_elements.CANCEL_PAYMENT_BTN.element_not_contain_disabled_attribute()
        self.registry_elements.CANCEL_PAYMENT_BTN.click()

        self.cancel_payment_form.TITLE.wait_to_have_text("Аннулирование платежа")
        self.cancel_payment_form.SUBTITLE.wait_to_have_text(
            re.compile(f"На сумму {payment_data.amount} от {today_user_friendly_view}")
        )
        self.cancel_payment_form.CANCEL_OPERATION_BTN.check_attribute_by_value("disabled", "")
        self.cancel_payment_form.CANCEL_REASON_INPUT_FROM_REGISTRY.fill("Ошибочный платеж")
        self.cancel_payment_form.CANCEL_OPERATION_BTN.element_not_contain_disabled_attribute()
        self.cancel_payment_form.CANCEL_OPERATION_BTN.click()
        self.cancel_payment_form.TITLE.not_to_be_visible()

        self.registry_elements.PAYMENT_DATES_FIELDS.wait_to_be_visible()
        self.registry_elements.PAYMENT_DATES_FIELDS.to_contain_text(0, today_user_friendly_view)
        self.registry_elements.STATUS_FIELDS.to_contain_text(0, "Аннулирован")
        self.registry_elements.CHECK_NUM_FIELDS.to_contain_text(0, str(doc_number))

    @allure.title("Корректировка банковского платежа")
    @allure.id(582583)
    @allure.description("Корректировка банковского платежа")
    def test_bank_payment_correction(
        self, base_url: str, api_request_context: APIRequestContext, create_user_with_agreement_and_account
    ):
        client_info = create_user_with_agreement_and_account
        payment_amount = 250
        correction_sum = 200
        today_user_friendly_view = get_current_datetime_string(is_full_format=False)
        doc_number = generate_random_number(4)
        payment_data = PaymentUniblpInfo(
            amount=payment_amount, account_id=client_info.agreements[0].accounts[0].id, document_number=doc_number
        )
        self.payment_api_uniblp.wait_check_create_payment(payment_data)
        self.payment_api_uniblp.create_payment(payment_data)

        self.payment_api.wait_last_payment_successful(client_info.agreements[0].accounts[0].id)
        self.base_page.open(
            f"{base_url}customer-hierarchy-management/accounts/{client_info.agreements[0].accounts[0].id}/account"
        )
        self.base_page.base_elements.CONTEXT_ELEMENT.wait_for_text_in_all(["Лицевой счет"], timeout=10000)
        self.client_profile_page.locators.BURGER_MENU.select_by_value("Финансы > Платежи")

        self.payment_page.locators.CHECK_NUM_FIELDS.wait_to_be_visible()
        self.payment_page.locators.CHECK_NUM_FIELDS.to_contain_text(0, str(doc_number))
        self.payment_page.locators.PAYMENT_DATES_FIELDS.to_contain_text(0, today_user_friendly_view)
        self.payment_page.locators.REGISTRY_DATES_FIELDS.to_contain_text(0, today_user_friendly_view)
        self.payment_page.locators.SUM_FIELDS.to_contain_text(0, f"{payment_data.amount}.00")
        self.payment_page.locators.STATUS_FIELDS.to_contain_text(0, "Действует")

        self.payment_page.locators.ADD_CORRECTION_BTN.check_attribute_by_value("disabled", "")
        self.payment_page.locators.PAYMENT_DATES_FIELDS[0].click()
        delay(0.5, reason="Время на активацию кнопки")
        self.payment_page.locators.ADD_CORRECTION_BTN.element_not_contain_disabled_attribute()
        self.payment_page.locators.ADD_CORRECTION_BTN.click()

        self.payment_correction_form.TITLE.wait_to_have_text(
            re.compile(f"Добавление корректировки платежа от {today_user_friendly_view}")
        )
        self.payment_correction_form.CORRECTION_TYPE_RADIOBUTTONS.select_by_value("Отрицательная корректировка")
        self.payment_correction_form.CORRECTION_DATE_INPUT.to_have_value(re.compile(today_user_friendly_view))
        self.payment_correction_form.CORRECTION_SUM_INPUT.to_have_value("")
        self.payment_correction_form.CORRECTION_SUM_INPUT.fill(str(correction_sum))
        self.payment_correction_form.CORRECTION_COMMENT.click()
        self.payment_correction_form.CORRECTION_REASON.select_by_value("Корректировка платежа")
        self.payment_correction_form.CORRECTION_COMMENT.wait_to_have_text("")
        self.payment_correction_form.INNER_CANCEL_BTN.wait_to_be_visible()
        self.payment_correction_form.INNER_ACCEPT_BTN.wait_to_have_text("Добавить")
        self.payment_correction_form.INNER_ACCEPT_BTN.click()

        self.payment_correction_form.INNER_ACCEPT_BTN.not_to_be_visible()
        self.adjustment_api.wait_adjustment_status(client_info.agreements[0].accounts[0].id)
        self.payment_page.locators.USER_BALANCE.wait_to_have_text(f"{payment_amount - correction_sum}.00")
        self.payment_page.locators.REFRESH_PAYMENTS_BTN.click()

        self.payment_page.locators.CHECK_NUM_FIELDS[0].click()
        self.payment_details_elements.FORM_TABS[1].click()
        self.payment_details_elements.PAYMENT_TYPE_BTN[1].click()
        self.payment_details_elements.PAYMENT_TYPE_BTN[1].element_have_css_color("color", "blue_button")

        self.payment_details_elements.PAYMENT_DATE_FIELDS[0].to_contain_text(today_user_friendly_view)
        self.payment_details_elements.CORRECTION_TYPE_FIELDS[0].to_contain_text("Отрицательная корректировка платежа")
        self.payment_details_elements.CORRECTION_SUM_FIELDS[0].to_contain_text(f"{correction_sum}.00")
        self.payment_details_elements.CORRECTION_STATUS_FIELDS[0].to_contain_text("Одобрено")
        self.payment_details_elements.CORRECTION_PURPOSE_FIELDS[0].to_contain_text("Корректировка платежа")
        self.payment_details_elements.PAYMENT_TYPE_BTN[1].wait_to_have_text(f"Корректировки: {correction_sum}.00")

    @allure.title("Ошибка при аннулировании платежа с истёкшим доступным периодом для отмены")
    @allure.id(583502)
    @allure.description("Возникновение ошибки при попытке аннулировать платеж с истёкшим доступным периодом для отмены")
    def test_cancel_bank_payment_expired_period(
        self, base_url: str, api_request_context: APIRequestContext, create_user_with_agreement_and_account
    ):
        client_info = create_user_with_agreement_and_account
        old_date_short = get_shifted_datetime("-2d").strftime("%Y-%m-%d")
        old_date_user_friendly_view = get_shifted_datetime("-2d").strftime("%d.%m.%Y")
        payment_amount = generate_random_number(3)
        doc_number = generate_random_number(4)
        payment_data = PaymentUniblpInfo(
            amount=payment_amount,
            account_id=client_info.agreements[0].accounts[0].id,
            document_number=doc_number,
            payment_date=get_shifted_datetime("-2d").replace(tzinfo=timezone(timedelta(hours=3))).isoformat(),
        )
        self.payment_api_uniblp.wait_check_create_payment(payment_data, "add_date")
        self.payment_api_uniblp.create_payment(payment_data, "add_date")
        self.registry_requests_api.wait_last_payment_amount_in_registry(old_date_short, doc_number, payment_amount)
        self.registry_requests_api.wait_payment_for_doc_successful(old_date_short, doc_number)
        payment_id = self.registry_requests_api.get_registry_list(
            old_date_short, old_date_short, str(doc_number), "-paymentDate"
        ).json()["items"][0]["paymentId"]

        self.base_page.open(
            f"{base_url}customer-hierarchy-management/accounts/{client_info.agreements[0].accounts[0].id}/account"
        )
        self.base_page.base_elements.CONTEXT_ELEMENT.wait_for_text_in_all(["Лицевой счет"], timeout=10000)
        self.client_profile_page.locators.BURGER_MENU.select_by_value("Платежные системы > Реестр платежей")

        self.registry_elements.CHECK_NUM_SEARCH.fill(str(doc_number))
        self.registry_elements.DATE_SEARCH_CROSS.click()
        delay(1, reason="Время на обновление списка")
        self.registry_elements.PAYMENT_DATES_FIELDS.wait_to_have_count(1)
        self.registry_elements.PAYMENT_DATES_FIELDS.to_contain_text(0, old_date_user_friendly_view)
        self.registry_elements.STATUS_FIELDS.to_contain_text(0, "Действует")
        self.registry_elements.CHECK_NUM_FIELDS.to_contain_text(0, str(doc_number))
        self.registry_elements.CHECK_SUM_FIELDS[0].wait_to_have_text(re.compile(rf"{payment_data.amount}.00\sRUB"))
        self.registry_elements.PAYMENT_SUM_FIELDS[0].wait_to_have_text(re.compile(rf"{payment_data.amount}.00\sRUB"))
        self.registry_elements.CASHIER_FIELDS.to_contain_text(0, "uniblp/uniblp")

        self.registry_elements.CANCEL_PAYMENT_BTN.check_attribute_by_value("disabled", "")
        self.registry_elements.PAYMENT_DATES_FIELDS[0].click()
        self.registry_elements.CANCEL_PAYMENT_BTN.element_not_contain_disabled_attribute()
        self.registry_elements.CANCEL_PAYMENT_BTN.click()

        self.cancel_payment_form.TITLE.wait_to_have_text("Аннулирование платежа")
        self.cancel_payment_form.SUBTITLE.wait_to_have_text(
            re.compile(f"На сумму {payment_data.amount} от {old_date_user_friendly_view}")
        )
        self.cancel_payment_form.CANCEL_INFO_MESSAGE.to_contain_text(
            f"Доступный период для отмены платежа с идентификатором = {payment_id} истёк. Дата платежа = {old_date_short}"
        )
        self.cancel_payment_form.CANCEL_OPERATION_BTN.check_attribute_by_value("disabled", "")
        self.cancel_payment_form.CANCEL_REASON_INPUT_FROM_REGISTRY.fill("Ошибочный платеж")
        self.cancel_payment_form.CANCEL_OPERATION_BTN.check_attribute_by_value("disabled", "")

    @allure.title("Аннулирование платежа при недостатке средств")
    @allure.id(583503)
    @allure.description(
        "Аннулирование платежа при недостатке средств на балансе ЛС "
        "и установленном на кассе параметре isCheckAvailableBalance"
    )
    def test_cancel_bank_payment_decreased_sum(
        self, base_url: str, api_request_context: APIRequestContext, create_user_with_agreement_and_account
    ):
        client_info = create_user_with_agreement_and_account
        today = get_current_datetime_string_for_api(is_full_format=False)
        payment_amount = 2000
        today_user_friendly_view = get_current_datetime_string(is_full_format=False)
        doc_number = generate_random_number(4)
        payment_data = PaymentUniblpInfo(
            amount=payment_amount, account_id=client_info.agreements[0].accounts[0].id, document_number=doc_number
        )
        self.payment_api_uniblp.wait_check_create_payment(payment_data)
        self.payment_api_uniblp.create_payment(payment_data)
        self.registry_requests_api.wait_last_payment_amount_in_registry(today, doc_number, payment_amount)
        self.registry_requests_api.wait_payment_for_doc_successful(today, doc_number)

        client_info, product = self.client_request_api.product_sale(
            client_info.user_id,
            category="internet",
            agreement_id=client_info.agreements[0].id,
            account_id=client_info.agreements[0].accounts[0].id,
        )
        self.personal_account_api.wait_check_current_main_balance(
            client_info.agreements[0].accounts[0].id,
            payment_amount - product.one_time_payment - product.subscription_fee,
        )

        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{client_info.user_id}/overview")
        self.base_page.base_elements.CONTEXT_ELEMENT.wait_for_text_in_all(["Клиент"], timeout=10000)
        self.client_profile_page.locators.BURGER_MENU.select_by_value("Платежные системы > Реестр платежей")

        self.registry_elements.CHECK_NUM_SEARCH.fill(str(doc_number))
        self.registry_elements.PAYMENT_DATES_FIELDS[0].wait_to_be_visible()
        self.registry_elements.PAYMENT_DATES_FIELDS.to_contain_text(0, today_user_friendly_view)
        self.registry_elements.STATUS_FIELDS.to_contain_text(0, "Действует")
        self.registry_elements.CHECK_NUM_FIELDS.to_contain_text(0, str(doc_number))
        self.registry_elements.CHECK_SUM_FIELDS.to_contain_text(0, "2 000.00 RUB")
        self.registry_elements.PAYMENT_SUM_FIELDS.to_contain_text(0, "2 000.00 RUB")
        self.registry_elements.CASHIER_FIELDS.to_contain_text(0, "uniblp/uniblp")

        self.registry_elements.CANCEL_PAYMENT_BTN.check_attribute_by_value("disabled", "")
        self.registry_elements.PAYMENT_DATES_FIELDS[0].click()
        self.registry_elements.CANCEL_PAYMENT_BTN.element_not_contain_disabled_attribute()
        self.registry_elements.CANCEL_PAYMENT_BTN.click()

        self.cancel_payment_form.TITLE.wait_to_have_text("Аннулирование платежа")
        self.cancel_payment_form.SUBTITLE.wait_to_have_text(
            re.compile(f"На сумму {payment_data.amount} от {today_user_friendly_view}")
        )
        self.cancel_payment_form.CANCEL_OPERATION_BTN.check_attribute_by_value("disabled", "")
        self.cancel_payment_form.CANCEL_REASON_INPUT_FROM_REGISTRY.fill("Ошибочный платеж")
        self.cancel_payment_form.CANCEL_OPERATION_BTN.element_not_contain_disabled_attribute()
        self.cancel_payment_form.CANCEL_OPERATION_BTN.click()
        self.cancel_payment_form.TITLE.not_to_be_visible()

        self.registry_elements.PAYMENT_DATES_FIELDS.wait_to_be_visible()
        self.registry_elements.PAYMENT_DATES_FIELDS.to_contain_text(0, today_user_friendly_view)
        self.registry_elements.STATUS_FIELDS.to_contain_text(0, "Аннулирован")
        self.registry_elements.CHECK_NUM_FIELDS.to_contain_text(0, str(doc_number))

    @allure.title("Ошибка при аннулировании платежа после корректировки")
    @allure.id(584465)
    @allure.description("Возникновение ошибки при попытке аннулировать платеж, после корректировки")
    def test_cancel_bank_payment_after_correction(
        self, base_url: str, api_request_context: APIRequestContext, create_user_with_agreement_and_account
    ):
        client_info = create_user_with_agreement_and_account
        payment_amount = 999
        correction_sum = 200
        today_user_friendly_view = get_current_datetime_string(is_full_format=False)
        doc_number = generate_random_number(4)
        payment_data = PaymentUniblpInfo(
            amount=payment_amount, account_id=client_info.agreements[0].accounts[0].id, document_number=doc_number
        )
        self.payment_api_uniblp.wait_check_create_payment(payment_data)
        self.payment_api_uniblp.create_payment(payment_data)

        self.payment_api.wait_last_payment_successful(client_info.agreements[0].accounts[0].id)
        self.base_page.open(
            f"{base_url}customer-hierarchy-management/accounts/{client_info.agreements[0].accounts[0].id}/account"
        )
        self.base_page.base_elements.CONTEXT_ELEMENT.wait_for_text_in_all(["Лицевой счет"], timeout=10000)
        self.client_profile_page.locators.BURGER_MENU.select_by_value("Финансы > Платежи")

        self.payment_page.locators.CHECK_NUM_FIELDS.wait_to_be_visible()
        self.payment_page.locators.CHECK_NUM_FIELDS.to_contain_text(0, str(doc_number))
        self.payment_page.locators.PAYMENT_DATES_FIELDS.to_contain_text(0, today_user_friendly_view)
        self.payment_page.locators.REGISTRY_DATES_FIELDS.to_contain_text(0, today_user_friendly_view)
        self.payment_page.locators.SUM_FIELDS.to_contain_text(0, f"{payment_data.amount}.00")
        self.payment_page.locators.STATUS_FIELDS.to_contain_text(0, "Действует")

        self.payment_page.locators.ADD_CORRECTION_BTN.check_attribute_by_value("disabled", "")
        self.payment_page.locators.PAYMENT_DATES_FIELDS[0].click()
        delay(0.5, reason="Время на активацию кнопки")
        self.payment_page.locators.ADD_CORRECTION_BTN.element_not_contain_disabled_attribute()
        self.payment_page.locators.ADD_CORRECTION_BTN.click()

        self.payment_correction_form.TITLE.wait_to_have_text(
            re.compile(f"Добавление корректировки платежа от {today_user_friendly_view}")
        )
        self.payment_correction_form.CORRECTION_TYPE_RADIOBUTTONS.select_by_value("Отрицательная корректировка")
        self.payment_correction_form.CORRECTION_DATE_INPUT.to_have_value(re.compile(today_user_friendly_view))
        self.payment_correction_form.CORRECTION_SUM_INPUT.to_have_value("")
        self.payment_correction_form.CORRECTION_SUM_INPUT.fill(str(correction_sum))
        self.payment_correction_form.CORRECTION_COMMENT.click()
        self.payment_correction_form.CORRECTION_REASON.select_by_value("Корректировка платежа")
        self.payment_correction_form.CORRECTION_COMMENT.wait_to_have_text("")
        self.payment_correction_form.INNER_CANCEL_BTN.wait_to_be_visible()
        self.payment_correction_form.INNER_ACCEPT_BTN.wait_to_have_text("Добавить")
        self.payment_correction_form.INNER_ACCEPT_BTN.click()

        self.payment_correction_form.INNER_ACCEPT_BTN.not_to_be_visible()
        self.adjustment_api.wait_adjustment_status(client_info.agreements[0].accounts[0].id)
        self.payment_page.locators.USER_BALANCE.wait_to_have_text(f"{payment_amount - correction_sum}.00")

        self.client_profile_page.locators.BURGER_MENU.select_by_value("Платежные системы > Реестр платежей")

        self.registry_elements.CHECK_NUM_SEARCH.fill(str(doc_number))
        self.registry_elements.PAYMENT_DATES_FIELDS.wait_to_be_visible()
        self.registry_elements.PAYMENT_DATES_FIELDS.to_contain_text(0, today_user_friendly_view)
        self.registry_elements.STATUS_FIELDS.to_contain_text(0, "Действует")
        self.registry_elements.CHECK_NUM_FIELDS.to_contain_text(0, str(doc_number))
        self.registry_elements.CHECK_SUM_FIELDS[0].wait_to_have_text(re.compile(rf"{payment_data.amount}.00\sRUB"))
        self.registry_elements.PAYMENT_SUM_FIELDS[0].wait_to_have_text(re.compile(rf"{payment_data.amount}.00\sRUB"))
        self.registry_elements.CASHIER_FIELDS.to_contain_text(0, "uniblp/uniblp")

        self.registry_elements.CANCEL_PAYMENT_BTN.check_attribute_by_value("disabled", "")
        self.registry_elements.PAYMENT_DATES_FIELDS[0].click()
        self.registry_elements.CANCEL_PAYMENT_BTN.element_not_contain_disabled_attribute()
        self.registry_elements.CANCEL_PAYMENT_BTN.click()

        self.cancel_payment_form.TITLE.wait_to_have_text("Аннулирование платежа")
        self.cancel_payment_form.SUBTITLE.wait_to_have_text(
            re.compile(f"На сумму {payment_data.amount} от {today_user_friendly_view}")
        )
        self.cancel_payment_form.CANCEL_INFO_MESSAGE.to_contain_text("Отмена откорректированного платежа запрещена")
        self.cancel_payment_form.CANCEL_OPERATION_BTN.check_attribute_by_value("disabled", "")
        self.cancel_payment_form.CANCEL_REASON_INPUT_FROM_REGISTRY.fill("Ошибочный платеж")
        self.cancel_payment_form.CANCEL_OPERATION_BTN.check_attribute_by_value("disabled", "")
