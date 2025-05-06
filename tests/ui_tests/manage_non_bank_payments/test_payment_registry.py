import re

import allure
import pytest
from playwright.sync_api import APIRequestContext, Page

from api.requests.payments_requests import PaymentInfo, PaymentsRequests
from api.requests.personal_account_requests import PersonalAccountRequests
from api.requests.registry_requests import RegistryRequests
from common.helpers.data_generator import (
    generate_random_number,
    get_current_datetime_string,
    get_current_datetime_string_for_api,
)
from common.helpers.time_helpers import delay
from pages.base_page import BasePage
from pages.client_profile_page import ClientProfilePage
from pages.locators.payments_elements import PaymentDetailsElements
from pages.locators.registry_elements import RegistryDetailsElements, RegistryElements
from pages.payments_page import PaymentsPage
from tests.ui_tests.conftest import ClientInfo


@allure.suite("E2E_82 Управление небанковскими и наличными платежами")
class TestManageNonBankPayments:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_ui_stand_login: Page, api_request_auth_context: APIRequestContext):
        self.base_page = BasePage(nexign_ui_stand_login)
        self.client_profile_page = ClientProfilePage(nexign_ui_stand_login)
        self.registry_elements = RegistryElements(nexign_ui_stand_login)
        self.personal_account_api = PersonalAccountRequests(api_request_auth_context)
        self.payment_api = PaymentsRequests(api_request_auth_context)
        self.registry_requests_api = RegistryRequests(api_request_auth_context)
        self.registry_details_elements = RegistryDetailsElements(nexign_ui_stand_login)
        self.payment_page = PaymentsPage(nexign_ui_stand_login)
        self.payment_details_elements = PaymentDetailsElements(nexign_ui_stand_login)

    @allure.title("Отображение небанковского платежа в реестре платежей")
    @allure.id(603836)
    @pytest.mark.regress
    def test_check_non_bank_payment_preview_in_payment_registry(
        self,
        base_url: str,
        api_request_auth_context: APIRequestContext,
        create_user_with_agreement_and_account: ClientInfo,
    ):
        with allure.step("Выполнение предусловий"):
            client_info = create_user_with_agreement_and_account
            today = get_current_datetime_string_for_api(is_full_format=False)
            payment_amount = generate_random_number(3)
            today_user_friendly_view = get_current_datetime_string(is_full_format=False)
            doc_number = generate_random_number(4)

            with allure.step(f"Добавление платежа для ЛС {client_info.account_id}"):
                payment_data = PaymentInfo(
                    document_number=doc_number,
                    item_type="CUSTOMER_ACCOUNT",
                    account_id=client_info.account_id,
                    payment_method_type="CASH",
                    currency_code="RUB",
                    amount=payment_amount,
                )
                self.payment_api.wait_check_create_payment(payment_data)
                self.payment_api.create_payment(payment_data)
                self.registry_requests_api.wait_last_payment_amount_in_registry(today, doc_number, payment_amount)
                self.payment_api.wait_last_payment_successful(client_info.account_id)
                self.personal_account_api.wait_check_current_main_balance(client_info.account_id, payment_amount)

        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{client_info.user_id}/overview")
        delay(1, reason="Время для смены контекста и содержания меню")
        self.client_profile_page.locators.BURGER_MENU_BTN.click()
        self.client_profile_page.locators.BURGER_MENU_EL_BTN[3].click()

        self.registry_elements.CHECK_NUM_SEARCH.fill(str(doc_number))
        self.registry_elements.CHECK_NUM_FIELDS.wait_to_have_count(1)

        self.registry_elements.PAYMENT_DATES_FIELDS.wait_to_be_visible()
        self.registry_elements.PAYMENT_DATES_FIELDS.to_contain_text(0, today_user_friendly_view)
        self.registry_elements.STATUS_FIELDS.to_contain_text(0, "Действует")
        self.registry_elements.CHECK_NUM_FIELDS.to_contain_text(0, str(doc_number))
        self.registry_elements.CHECK_SUM_FIELDS.to_contain_text(0, str(payment_data.amount))
        self.registry_elements.PAYMENT_SUM_FIELDS.to_contain_text(0, str(payment_data.amount))
        self.registry_elements.CASHIER_FIELDS.to_contain_text(0, "PNXL1/pointNx1")

        self.registry_elements.CHECK_NUM_FIELDS[0].click()
        form_title = f"Платёж от {today_user_friendly_view}"
        self.registry_details_elements.FORM_TITLE.wait_to_have_text(re.compile(form_title))
        self.registry_details_elements.PAYMENT_DETAILS.wait_to_have_count(5)
        self.registry_details_elements.PAYMENT_DETAILS[0].to_contain_text(today_user_friendly_view)
        self.registry_details_elements.PAYMENT_DETAILS[1].to_contain_text(str(payment_amount))
        self.registry_details_elements.PAYMENT_DETAILS[2].to_contain_text(str(doc_number))
        self.registry_details_elements.PAYMENT_DETAILS[3].to_contain_text("Наличные")
        self.registry_details_elements.PAYMENT_DETAILS[4].to_contain_text("PNXL1/pointNx1")
        self.registry_details_elements.FORM_TABS[1].click()

        self.registry_details_elements.FORM_TABS[1].to_have_class("ant-tabs-tab ant-tabs-tab-active")
        self.registry_details_elements.GOAL_TABLE_FIRST_COLUMN[0].wait_to_have_text(
            f"Лицевой счет {client_info.account_id}"
        )
        self.registry_details_elements.GOAL_TABLE_FIRST_COLUMN[1].wait_to_have_text("Исходная сумма:")
        self.registry_details_elements.GOAL_TABLE_FIRST_COLUMN[2].wait_to_have_text(f"{payment_amount}.00 RUB.")

    @allure.title("Отображение небанковского платежа в списке платежей клиента")
    @allure.id(603837)
    @pytest.mark.regress
    def test_check_non_bank_payment_preview_in_client_payments(
        self, base_url: str, api_request_auth_context: APIRequestContext, create_user_with_agreement_and_account
    ):
        with allure.step("Выполнение предусловий"):
            client_info = create_user_with_agreement_and_account
            today = get_current_datetime_string_for_api(is_full_format=False)
            payment_amount = generate_random_number(3)
            today_user_friendly_view = get_current_datetime_string(is_full_format=False)
            doc_number = generate_random_number(4)

            with allure.step(f"Добавление платежа для ЛС {client_info.account_id}"):
                payment_data = PaymentInfo(
                    document_number=doc_number,
                    item_type="CUSTOMER_ACCOUNT",
                    account_id=client_info.account_id,
                    payment_method_type="CASH",
                    currency_code="RUB",
                    amount=payment_amount,
                )
                self.payment_api.wait_check_create_payment(payment_data)
                self.payment_api.create_payment(payment_data)
                self.registry_requests_api.wait_last_payment_amount_in_registry(today, doc_number, payment_amount)
                self.payment_api.wait_last_payment_successful(client_info.account_id)
                self.personal_account_api.wait_check_current_main_balance(client_info.account_id, payment_amount)

        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{client_info.user_id}/overview")

        self.client_profile_page.locators.CURRENT_PERSONAL_ACCOUNT_LINK.click()
        delay(1, reason="Время для смены контекста и содержания меню")
        self.client_profile_page.locators.BURGER_MENU_BTN.click()
        self.client_profile_page.locators.BURGER_MENU_EL_BTN[1].click()

        self.payment_page.locators.CHECK_NUM_FIELDS.wait_to_be_visible()
        self.payment_page.locators.CHECK_NUM_FIELDS.to_contain_text(0, str(doc_number))
        self.payment_page.locators.PAYMENT_DATES_FIELDS.to_contain_text(0, today_user_friendly_view)
        self.payment_page.locators.REGISTRY_DATES_FIELDS.to_contain_text(0, today_user_friendly_view)
        self.payment_page.locators.SUM_FIELDS.to_contain_text(0, f"{payment_data.amount}.00")
        self.payment_page.locators.STATUS_FIELDS.to_contain_text(0, "Действует")

        self.payment_page.locators.CHECK_NUM_FIELDS[0].click()

        self.payment_details_elements.FORM_TITLE.wait_to_have_text("Платёж")
        self.payment_details_elements.FORM_STATUS.wait_to_have_text("Действует")
        (
            self.payment_details_elements.SUBTITLE.wait_to_have_text(
                re.compile(f"На сумму {payment_data.amount}.00 от {today_user_friendly_view}")
            )
        )
        self.payment_details_elements.PAYMENT_DETAILS[0].to_contain_text(today_user_friendly_view)
        self.payment_details_elements.PAYMENT_DETAILS[1].to_contain_text(today_user_friendly_view)
        self.payment_details_elements.PAYMENT_DETAILS[2].to_contain_text(str(doc_number))
        self.payment_details_elements.PAYMENT_DETAILS[3].to_contain_text(f"{payment_data.amount}.00")
        self.payment_details_elements.PAYMENT_DETAILS[4].wait_to_have_text(re.compile(rf"{payment_data.amount}.00\sRUB"))
        self.payment_details_elements.PAYMENT_DETAILS[6].to_contain_text("PM:pm_gateway")
        self.payment_details_elements.PAYMENT_DETAILS[8].to_contain_text("PNXL1")
        self.payment_details_elements.FORM_TABS[1].click()

        self.payment_details_elements.FORM_TABS[1].to_have_class("ant-tabs-tab ant-tabs-tab-active")
        self.payment_details_elements.PAYMENT_TYPE_BTN[0].wait_to_have_text("Погашения: 0.00")
        self.payment_details_elements.PAYMENT_TYPE_BTN[1].wait_to_have_text("Корректировки: 0.00")
        self.payment_details_elements.PAYMENT_TYPE_BTN[0].element_have_css_color("color", "deep_blue")
        self.payment_details_elements.PAYMENT_DATE_FIELDS.wait_not_to_be_visible()
        self.payment_details_elements.PAYMENT_TYPE_BTN[1].click()
        self.payment_details_elements.PAYMENT_TYPE_BTN[1].element_have_css_color("color", "deep_blue")
        self.payment_details_elements.PAYMENT_DATE_FIELDS.wait_not_to_be_visible()
