import re

import allure
import pytest

from api.nbss.finances.adjustment_requests import AdjustmentRequests
from api.nbss.finances.payments_requests import PaymentInfo, PaymentsRequests
from api.nbss.finances.registry_requests import RegistryRequests
from api.nbss.personal_account_requests import PersonalAccountRequests
from common.helpers.data_generator import (
    generate_random_number,
    get_current_datetime_string,
    get_current_datetime_string_for_api,
)
from common.helpers.time_helpers import delay
from models.user import IndividualClient
from pages.base_page import BasePage
from pages.locators.nbss.finances.payments_elements import PaymentCorrectionForm, PaymentDetailsElements
from pages.locators.nbss.finances.registry_elements import RegistryDetailsElements, RegistryElements
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.finances.payments_page import PaymentsPage


@allure.suite("E2E_82 Управление небанковскими и наличными платежами")
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestPaymentsForm:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_ui_stand_login) -> None:
        self.base_page = BasePage()
        self.client_profile_page = ClientProfilePage()
        self.personal_account_api = PersonalAccountRequests()
        self.payment_api = PaymentsRequests()
        self.adjustment_api = AdjustmentRequests()
        self.registry_requests_api = RegistryRequests()
        self.payment_page = PaymentsPage()
        self.payment_details_elements = PaymentDetailsElements()
        self.payment_correction_form = PaymentCorrectionForm()
        self.registry_elements = RegistryElements()
        self.registry_details_elements = RegistryDetailsElements()

    @allure.title("Корректировка небанковского платежа")
    @allure.id(603302)
    def test_non_bank_payment_correction(self, base_url: str, create_user_with_agreement_and_account):
        with allure.step("Выполнение предусловий"):
            client_info = create_user_with_agreement_and_account
            today = get_current_datetime_string_for_api(is_full_format=False)
            payment_amount = 250
            today_user_friendly_view = get_current_datetime_string(is_full_format=False)
            doc_number = generate_random_number(4)
            correction_sum = 200

            with allure.step(f"Добавление платежа для ЛС {client_info.agreements[0].accounts[0].id}"):
                payment_data = PaymentInfo(
                    document_number=doc_number,
                    account_id=client_info.agreements[0].accounts[0].id,
                    amount=payment_amount,
                )
                self.payment_api.wait_check_create_payment(payment_data)
                self.payment_api.create_payment(payment_data)
                self.registry_requests_api.wait_last_payment_amount_in_registry(today, doc_number, payment_amount)
                self.payment_api.wait_last_payment_done(client_info.agreements[0].accounts[0].id)
                self.personal_account_api.wait_check_current_main_balance(
                    client_info.agreements[0].accounts[0].id, payment_amount
                )

        self.base_page.open(
            f"{base_url}customer-hierarchy-management/accounts/{client_info.agreements[0].accounts[0].id}/account"
        )

        self.base_page.base_elements.CONTEXT_ELEMENT.wait_for_text_in_all(["Лицевой счет"], timeout=10000)
        self.client_profile_page.locators.BURGER_MENU.select_by_value("Финансы > Платежи")

        self.payment_page.payment_elements.CHECK_NUM_FIELDS.wait_to_be_visible()
        self.payment_page.payment_elements.CHECK_NUM_FIELDS.to_contain_text(0, str(doc_number))
        self.payment_page.payment_elements.PAYMENT_DATES_FIELDS.to_contain_text(0, today_user_friendly_view)
        self.payment_page.payment_elements.REGISTRY_DATES_FIELDS.to_contain_text(0, today_user_friendly_view)
        self.payment_page.payment_elements.SUM_FIELDS.to_contain_text(0, f"{payment_data.amount}.00")
        self.payment_page.payment_elements.STATUS_FIELDS.to_contain_text(0, "Действует")

        self.payment_page.payment_elements.ADD_CORRECTION_BTN.check_attribute_by_value("disabled", "")
        self.payment_page.payment_elements.PAYMENT_DATES_FIELDS[0].click()
        delay(0.5, reason="Время на активацию кнопки")
        self.payment_page.payment_elements.ADD_CORRECTION_BTN.element_not_contain_disabled_attribute()
        self.payment_page.payment_elements.ADD_CORRECTION_BTN.click()

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
        self.payment_page.payment_elements.USER_BALANCE.wait_to_have_text(f"{payment_amount - correction_sum}.00")
        self.payment_page.payment_elements.REFRESH_PAYMENTS_BTN.click()

        self.payment_page.payment_elements.CHECK_NUM_FIELDS[0].click()
        self.payment_details_elements.FORM_TABS[1].click()
        self.payment_details_elements.PAYMENT_TYPE_BTN[1].click()
        self.payment_details_elements.PAYMENT_TYPE_BTN[1].element_have_css_color("color", "blue_button")

        self.payment_details_elements.PAYMENT_DATE_FIELDS[0].to_contain_text(today_user_friendly_view)
        self.payment_details_elements.CORRECTION_TYPE_FIELDS[0].to_contain_text("Отрицательная корректировка платежа")
        self.payment_details_elements.CORRECTION_SUM_FIELDS[0].to_contain_text(f"{correction_sum}.00")
        self.payment_details_elements.PAYMENT_TYPE_BTN[1].wait_to_have_text(f"Корректировки: -{correction_sum}.00")
        self.payment_details_elements.CORRECTION_STATUS_FIELDS[0].to_contain_text("Одобрено")
        self.payment_details_elements.CORRECTION_PURPOSE_FIELDS[0].to_contain_text("Корректировка платежа")

    @allure.title("Прием наличного платежа")
    @allure.id(600511)
    def test_non_payment_preview(
        self,
        base_url: str,
        create_user_with_agreement_and_account: IndividualClient,
    ) -> None:
        with allure.step("Выполнение предусловий"):
            client_info = create_user_with_agreement_and_account
            today = get_current_datetime_string_for_api(is_full_format=False)
            payment_amount = 250
            today_user_friendly_view = get_current_datetime_string(is_full_format=False)
            doc_number = generate_random_number(4)

            with allure.step(f"Добавление платежа для ЛС {client_info.agreements[0].accounts[0].id}"):
                payment_data = PaymentInfo(
                    document_number=doc_number,
                    account_id=client_info.agreements[0].accounts[0].id,
                    amount=payment_amount,
                )
                self.payment_api.wait_check_create_payment(payment_data)
                self.payment_api.create_payment(payment_data)
                self.registry_requests_api.wait_last_payment_amount_in_registry(today, doc_number, payment_amount)
                self.payment_api.wait_last_payment_done(client_info.agreements[0].accounts[0].id)
                self.personal_account_api.wait_check_current_main_balance(
                    client_info.agreements[0].accounts[0].id, payment_amount
                )
            self.base_page.open(
                f"{base_url}customer-hierarchy-management/accounts/{client_info.agreements[0].accounts[0].id}/account"
            )

        self.base_page.base_elements.CONTEXT_ELEMENT.wait_for_text_in_all(["Лицевой счет"], timeout=10000)
        self.client_profile_page.locators.BURGER_MENU.select_by_value("Финансы > Платежи")

        self.payment_page.payment_elements.ACCOUNT_NUM.wait_to_have_text(client_info.agreements[0].accounts[0].number)
        self.payment_page.payment_elements.USER_BALANCE.wait_to_have_text(f"{payment_amount}.00")

        self.payment_page.payment_elements.CHECK_NUM_FIELDS.wait_to_be_visible()
        self.payment_page.payment_elements.CHECK_NUM_FIELDS.to_contain_text(0, str(doc_number))
        self.payment_page.payment_elements.PAYMENT_DATES_FIELDS.to_contain_text(0, today_user_friendly_view)
        self.payment_page.payment_elements.REGISTRY_DATES_FIELDS.to_contain_text(0, today_user_friendly_view)
        self.payment_page.payment_elements.SUM_FIELDS.to_contain_text(0, f"{payment_data.amount}.00")
        self.payment_page.payment_elements.STATUS_FIELDS.to_contain_text(0, "Действует")

        self.payment_page.payment_elements.CHECK_NUM_FIELDS[0].click()

        self.payment_details_elements.FORM_TITLE.wait_to_have_text("Платёж")
        self.payment_details_elements.FORM_STATUS.wait_to_have_text("Действует")
        self.payment_details_elements.SUBTITLE.wait_to_have_text(
            re.compile(f"На сумму {payment_data.amount}.00 от {today_user_friendly_view}")
        )
        self.payment_details_elements.PAYMENT_DETAILS[0].to_contain_text(today_user_friendly_view)
        self.payment_details_elements.PAYMENT_DETAILS[1].to_contain_text(today_user_friendly_view)
        self.payment_details_elements.PAYMENT_DETAILS[2].to_contain_text(str(doc_number))
        self.payment_details_elements.PAYMENT_DETAILS[3].to_contain_text(f"{payment_data.amount}.00")
        self.payment_details_elements.PAYMENT_DETAILS[4].wait_to_have_text(re.compile(rf"{payment_data.amount}.00\sRUB"))
        self.payment_details_elements.PAYMENT_DETAILS[6].to_contain_text("PM:pm_gateway")
        self.payment_details_elements.PAYMENT_DETAILS[8].to_contain_text("PNXL1")

        self.client_profile_page.press_keyboard_button("Escape")
        self.client_profile_page.locators.BURGER_MENU.select_by_value("Платежные системы > Реестр платежей")

        self.registry_elements.CHECK_NUM_SEARCH.fill(str(doc_number))
        self.registry_elements.PAYMENT_DATES_FIELDS.wait_to_be_visible()
        self.registry_elements.PAYMENT_DATES_FIELDS.to_contain_text(0, today_user_friendly_view)
        self.registry_elements.STATUS_FIELDS.to_contain_text(0, "Действует")
        self.registry_elements.CHECK_NUM_FIELDS.to_contain_text(0, str(doc_number))
        self.registry_elements.CHECK_SUM_FIELDS[0].wait_to_have_text(re.compile(rf"{payment_data.amount}.00\sRUB"))
        self.registry_elements.PAYMENT_SUM_FIELDS[0].wait_to_have_text(re.compile(rf"{payment_data.amount}.00\sRUB"))
        self.registry_elements.CASHIER_FIELDS.to_contain_text(0, "PNXL1")
        self.registry_elements.CHECK_NUM_FIELDS[0].click()

        form_title = f"Платёж от {today_user_friendly_view}"
        self.registry_details_elements.FORM_TITLE.wait_to_have_text(re.compile(form_title))
        self.registry_details_elements.PAYMENT_DETAILS.wait_to_have_count(5)
        self.registry_details_elements.PAYMENT_DETAILS[0].to_contain_text(today_user_friendly_view)
        self.registry_details_elements.PAYMENT_DETAILS[1].wait_to_have_text(
            re.compile(rf"{payment_data.amount}.00\sRUB")
        )
        self.registry_details_elements.PAYMENT_DETAILS[2].to_contain_text(str(doc_number))
        self.registry_details_elements.PAYMENT_DETAILS[3].to_contain_text("Наличные")
        self.registry_details_elements.PAYMENT_DETAILS[4].to_contain_text("PNXL1")
