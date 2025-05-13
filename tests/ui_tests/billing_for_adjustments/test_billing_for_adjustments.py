import re

import allure
import pytest
from playwright.sync_api import APIRequestContext, Page

from api.requests.adjustment_requests import AdjustmentRequests
from api.requests.billing_requests import BillingRequests
from api.requests.payments_requests import PaymentsRequests
from common.helpers.data_generator import (
    get_current_datetime_string,
    get_shifted_datetime,
    get_shifted_datetime_string,
)
from pages.adjustments_page import AdjustmentsPage
from pages.billing_accounts_page import BillingAccountsPage
from pages.client_profile_page import ClientProfilePage
from pages.locators.adjustments import ChooseAdjustmentObjectForm
from pages.locators.dynamic_form_elements import CreatePaymentForm
from pages.payments_page import PaymentsPage
from tests.ui_tests.conftest import ClientInfo


@allure.epic("E2E_86 Запуск биллинга по корректировкам")
@allure.suite("Запуск биллинга по корректировкам")
class TestBillingForAdjustments:
    yesterday_date = get_shifted_datetime("-1d").strftime("%Y-%m-%d")
    yesterday_date_ddmmYYYY = get_shifted_datetime_string("-1d", False)
    yesterday_date_ddmmYYYY_HHMMSS = get_shifted_datetime_string("-1d", True)
    today_date_1_ddmmYYYY = get_current_datetime_string(False)
    today_date_2_ddmmYYYY = get_shifted_datetime_string("+1m", False)
    today_date_3_ddmmYYYY = get_shifted_datetime_string("+2m", False)

    @pytest.fixture(autouse=True)
    def setup(
        self,
        nexign_ui_stand_login: Page,
        api_request_auth_context: APIRequestContext,
        create_user_with_agreement_and_account: ClientInfo,
    ) -> None:
        self.client_profile_page = ClientProfilePage(nexign_ui_stand_login)
        self.adjustments_page = AdjustmentsPage(nexign_ui_stand_login)
        self.choose_adjustment_object_form = ChooseAdjustmentObjectForm(nexign_ui_stand_login)
        self.billing_accounts = BillingAccountsPage(nexign_ui_stand_login)
        self.client_info = create_user_with_agreement_and_account
        self.payments_page = PaymentsPage(nexign_ui_stand_login)
        self.create_payment_form = CreatePaymentForm(nexign_ui_stand_login)

        self.billing_api = BillingRequests(api_request_auth_context)
        self.adjustment_api = AdjustmentRequests(api_request_auth_context)
        self.payment_api = PaymentsRequests(api_request_auth_context)

    @allure.title("Запуск биллинга (корректировки начислений есть)")
    @allure.id(605659)
    @allure.link(
        url="allure.nexign.com/project/313/test-cases/605659",
        name="Запуск биллинга (корректировки начислений есть)",
    )
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=719302358",
        name="Запуск биллинга по корректировкам",
    )
    @allure.tag("can_auth", "success")
    @pytest.mark.smoke
    @pytest.mark.regress
    def test_billing_when_adjustment_exists(self, base_url: str) -> None:
        self.client_profile_page.open(
            f"{base_url}customer-hierarchy-management/accounts/{self.client_info.account_id}/account"
        )
        self.client_profile_page.locators.CLIENT_FIO.wait_to_be_visible()

        self.client_profile_page.locators.BURGER_MENU.click()
        self.client_profile_page.locators.BURGER_MENU_EL_BTN[9].click()
        self.adjustments_page.locators.PAGE_TITLE.wait_to_have_text("Корректировки")

        self.adjustments_page.open_add_adjustment_form()
        self.adjustments_page.fill_add_adjustment_form(
            "charge", "positive", "Абон. плата за VLAN", self.today_date_1_ddmmYYYY, "100", "Test comment 1"
        )
        self.adjustment_api.wait_adjustment_status(self.client_info.account_id)

        self.adjustments_page.locators.UPDATE_TABLE_BTN.click()
        self.adjustments_page.check_adjustment(
            0,
            "",
            self.today_date_1_ddmmYYYY,
            "Положительная корректировка детали счета в текущем периоде",
            -100.00,
            -16.67,
            "Одобрено",
            "Положительная корректировка детали счета в текущем периоде",
            "—",
            "Деталь: Абон. плата за VLAN",
            "0.00",
        )

        self.adjustments_page.locators.OPEN_BILLING_FORM.click()
        self.adjustments_page.locators.START_BILLING.wait_to_be_visible()
        self.adjustments_page.locators.START_BILLING.not_to_be_enabled()

        self.adjustments_page.locators.ADJUSTMENT_CHECKBOX.click(0)
        self.adjustments_page.locators.START_BILLING.wait_to_be_enabled()
        self.adjustments_page.locators.START_BILLING.click()
        self.adjustments_page.locators.INFO_MESSAGE.wait_to_be_visible()

        billing_profile_id = self.billing_api.get_billing_profile_id(self.client_info.account_id)
        self.billing_api.wait_billing(billing_profile_id)
        self.billing_api.wait_finish_billing(billing_profile_id, 3)
        bill_data = self.billing_api.get_list_of_bills([billing_profile_id])[0]
        bill_number = bill_data["billNumber"]

        self.adjustments_page.locators.UPDATE_TABLE_BTN.click()
        self.adjustments_page.check_adjustment(
            0,
            re.compile(bill_number + " от " + get_current_datetime_string(False) + r" \d\d:\d\d:\d\d"),
            self.today_date_1_ddmmYYYY,
            "Положительная корректировка детали счета в текущем периоде",
            -100.00,
            -16.67,
            "Одобрено",
            "Положительная корректировка детали счета в текущем периоде",
            "—",
            "Деталь: Абон. плата за VLAN",
            "0.00",
        )

        self.adjustments_page.locators.BURGER_MENU.click()
        self.adjustments_page.locators.BURGER_MENU_EL_BTN[8].click()
        self.billing_accounts.locators.PAGE_TITLE.wait_to_have_text("Биллинговые счета")

        self.billing_accounts.locators.ACCOUNT_NUMS_LIST.wait_to_have_count(1)
        self.billing_accounts.locators.ACCOUNT_NUMS_LIST.wait_to_be_visible()
        self.billing_accounts.locators.ACCOUNT_NUMS_LIST.click(0)
        self.billing_accounts.check_billing_properties_value(
            amount_due=100.00, output_balance=100.00, charged=100.00, charge_adjustments_recorded=100.00
        )

        self.billing_accounts.locators.DETAILS_TAB.click()
        self.billing_accounts.check_detail(
            detail_index=0,
            detail_name="Абон. плата за VLAN",
            charged=100.00,
            repaid=100.00,
            available_for_adjustment=100.00,
        )

        self.billing_accounts.locators.INVOICES_TAB.click()
        self.billing_accounts.check_invoice(
            invoice_index=1, invoice_type="Счет-фактура на начисления", amount=100.00, tax=16.67, balance=100.00
        )

    @allure.title("Запуск биллинга (корректировки начислений есть и учтены в счете)")
    @allure.id(611930)
    @allure.link(
        url="allure.nexign.com/project/313/test-cases/605659",
        name="Запуск биллинга (корректировки начислений есть и учтены в счете)",
    )
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=719302358",
        name="Запуск биллинга по корректировкам",
    )
    @allure.tag("can_auth", "success")
    @pytest.mark.regress
    def test_billing_when_adjustment_exists_and_included_in_bill(self, base_url: str) -> None:
        self.client_profile_page.open(
            f"{base_url}customer-hierarchy-management/accounts/{self.client_info.account_id}/account"
        )
        self.client_profile_page.locators.CLIENT_FIO.wait_to_be_visible()

        self.client_profile_page.locators.BURGER_MENU.click()
        self.client_profile_page.locators.BURGER_MENU_EL_BTN[9].click()
        self.adjustments_page.locators.PAGE_TITLE.wait_to_have_text("Корректировки")

        self.adjustments_page.open_add_adjustment_form()
        self.adjustments_page.fill_add_adjustment_form(
            "charge", "positive", "Абон. плата за VLAN", self.today_date_1_ddmmYYYY, "100", "Test comment 1"
        )

        self.adjustments_page.open_add_adjustment_form()
        self.adjustments_page.fill_add_adjustment_form(
            "charge", "positive", "Абон. плата за VLAN", self.today_date_2_ddmmYYYY, "200", "Test comment 2"
        )

        self.adjustments_page.open_add_adjustment_form()
        self.adjustments_page.fill_add_adjustment_form(
            "charge", "positive", "Абон. плата за VLAN", self.today_date_3_ddmmYYYY, "300", "Test comment 3"
        )
        self.adjustment_api.wait_all_adjustments_status(self.client_info.account_id, 3)

        self.adjustments_page.locators.ADJUSTMENT_TITLE.click(3)
        self.adjustments_page.locators.UPDATE_TABLE_BTN.click()
        self.adjustments_page.check_adjustment(
            0,
            "",
            self.today_date_1_ddmmYYYY,
            "Положительная корректировка детали счета в текущем периоде",
            -300.00,
            -50.00,
            "Одобрено",
            "Положительная корректировка детали счета в текущем периоде",
            "—",
            "Деталь: Абон. плата за VLAN",
            "0.00",
        )

        self.adjustments_page.check_adjustment(
            1,
            "",
            self.today_date_2_ddmmYYYY,
            "Положительная корректировка детали счета в текущем периоде",
            -200.00,
            -33.33,
            "Одобрено",
            "Положительная корректировка детали счета в текущем периоде",
            "—",
            "Деталь: Абон. плата за VLAN",
            "0.00",
        )

        self.adjustments_page.check_adjustment(
            2,
            "",
            self.today_date_3_ddmmYYYY,
            "Положительная корректировка детали счета в текущем периоде",
            -100.00,
            -16.67,
            "Одобрено",
            "Положительная корректировка детали счета в текущем периоде",
            "—",
            "Деталь: Абон. плата за VLAN",
            "0.00",
        )

        self.adjustments_page.locators.OPEN_BILLING_FORM.click()
        self.adjustments_page.locators.START_BILLING.wait_to_be_visible()
        self.adjustments_page.locators.START_BILLING.not_to_be_enabled()

        self.adjustments_page.locators.BILLING_ADJUSTMENTS.wait_to_have_count(3)
        self.adjustments_page.locators.BILLING_TABLE_HEADERS.click(2)

        self.adjustments_page.locators.ADJUSTMENT_CHECKBOX.click(0)
        self.adjustments_page.locators.START_BILLING.wait_to_be_enabled()
        self.adjustments_page.locators.START_BILLING.click()
        self.adjustments_page.locators.INFO_MESSAGE.wait_to_be_visible()

        billing_profile_id = self.billing_api.get_billing_profile_id(self.client_info.account_id)
        self.billing_api.wait_billing(billing_profile_id)
        self.billing_api.wait_finish_billing(billing_profile_id, 3)
        bill_data = self.billing_api.get_list_of_bills([billing_profile_id])[0]
        bill_number = bill_data["billNumber"]

        self.adjustments_page.locators.UPDATE_TABLE_BTN.click()
        self.adjustments_page.check_adjustment(
            0,
            re.compile(bill_number + " от " + get_current_datetime_string(False) + r" \d\d:\d\d:\d\d"),
            self.today_date_1_ddmmYYYY,
            "Положительная корректировка детали счета в текущем периоде",
            -300.00,
            -50.00,
            "Одобрено",
            "Положительная корректировка детали счета в текущем периоде",
            "—",
            "Деталь: Абон. плата за VLAN",
            "0.00",
        )

        self.adjustments_page.check_adjustment(
            1,
            "",
            self.today_date_2_ddmmYYYY,
            "Положительная корректировка детали счета в текущем периоде",
            -200.00,
            -33.33,
            "Одобрено",
            "Положительная корректировка детали счета в текущем периоде",
            "—",
            "Деталь: Абон. плата за VLAN",
            "0.00",
        )

        self.adjustments_page.check_adjustment(
            2,
            "",
            self.today_date_3_ddmmYYYY,
            "Положительная корректировка детали счета в текущем периоде",
            -100.00,
            -16.67,
            "Одобрено",
            "Положительная корректировка детали счета в текущем периоде",
            "—",
            "Деталь: Абон. плата за VLAN",
            "0.00",
        )

        self.adjustments_page.locators.OPEN_BILLING_FORM.click()
        self.adjustments_page.locators.START_BILLING.wait_to_be_visible()
        self.adjustments_page.locators.START_BILLING.not_to_be_enabled()

        self.adjustments_page.locators.BILLING_ADJUSTMENTS.wait_to_have_count(2)
        self.adjustments_page.check_adjustment_on_billing_form(
            0,
            "",
            "Положительная корректировка детали счета в текущем периоде",
            "-200.00",
            "-33.33",
            "Положительная корректировка детали счета в текущем периоде",
            "Деталь: Абон. плата за VLAN",
            "0.00",
        )

        self.adjustments_page.check_adjustment_on_billing_form(
            1,
            "",
            "Положительная корректировка детали счета в текущем периоде",
            "-100.00",
            "-16.67",
            "Положительная корректировка детали счета в текущем периоде",
            "Деталь: Абон. плата за VLAN",
            "0.00",
        )

        self.adjustments_page.locators.CROSS_BTN.click()
        self.adjustments_page.locators.BURGER_MENU.click()
        self.adjustments_page.locators.BURGER_MENU_EL_BTN[8].click()
        self.billing_accounts.locators.PAGE_TITLE.wait_to_have_text("Биллинговые счета")

        self.billing_accounts.locators.ACCOUNT_NUMS_LIST.wait_to_have_count(1)
        self.billing_accounts.locators.ACCOUNT_NUMS_LIST.wait_to_be_visible()
        self.billing_accounts.locators.ACCOUNT_NUMS_LIST.click(0)
        self.billing_accounts.check_billing_properties_value(
            amount_due=300.00, output_balance=300.00, charged=300.00, charge_adjustments_recorded=300.00
        )

        self.billing_accounts.locators.DETAILS_TAB.click()
        self.billing_accounts.check_detail(
            detail_index=0,
            detail_name="Абон. плата за VLAN",
            charged=300.00,
            repaid=300.00,
            available_for_adjustment=300.00,
        )

        self.billing_accounts.locators.INVOICES_TAB.click()
        self.billing_accounts.check_invoice(
            invoice_index=1, invoice_type="Счет-фактура на начисления", amount=300.00, tax=50.00, balance=300.00
        )

    @allure.title("Запуск биллинга (корректировки начислений есть, Только выбранные)")
    @allure.id(611929)
    @allure.link(
        url="allure.nexign.com/project/313/test-cases/611929",
        name="Запуск биллинга (корректировки начислений есть, Только выбранные)",
    )
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=719302358",
        name="Запуск биллинга по корректировкам",
    )
    @allure.tag("can_auth", "success")
    @pytest.mark.regress
    def test_billing_when_adjustment_exists_and_included_in_bill_only_selected(self, base_url: str) -> None:
        self.client_profile_page.open(
            f"{base_url}customer-hierarchy-management/accounts/{self.client_info.account_id}/account"
        )
        self.client_profile_page.locators.CLIENT_FIO.wait_to_be_visible()

        self.client_profile_page.locators.BURGER_MENU.click()
        self.client_profile_page.locators.BURGER_MENU_EL_BTN[9].click()
        self.adjustments_page.locators.PAGE_TITLE.wait_to_have_text("Корректировки")

        self.adjustments_page.open_add_adjustment_form()
        self.adjustments_page.fill_add_adjustment_form(
            "charge", "positive", "Абон. плата за VLAN", self.today_date_1_ddmmYYYY, "100", "Test comment 1"
        )

        self.adjustments_page.open_add_adjustment_form()
        self.adjustments_page.fill_add_adjustment_form(
            "charge", "positive", "Абон. плата за VLAN", self.today_date_2_ddmmYYYY, "200", "Test comment 2"
        )

        self.adjustments_page.open_add_adjustment_form()
        self.adjustments_page.fill_add_adjustment_form(
            "charge", "positive", "Абон. плата за VLAN", self.today_date_3_ddmmYYYY, "300", "Test comment 3"
        )
        self.adjustment_api.wait_all_adjustments_status(self.client_info.account_id, 3)

        self.adjustments_page.locators.ADJUSTMENT_TITLE.click(3)
        self.adjustments_page.locators.UPDATE_TABLE_BTN.click()
        self.adjustments_page.check_adjustment(
            0,
            "",
            self.today_date_1_ddmmYYYY,
            "Положительная корректировка детали счета в текущем периоде",
            -300.00,
            -50.00,
            "Одобрено",
            "Положительная корректировка детали счета в текущем периоде",
            "—",
            "Деталь: Абон. плата за VLAN",
            "0.00",
        )

        self.adjustments_page.check_adjustment(
            1,
            "",
            self.today_date_2_ddmmYYYY,
            "Положительная корректировка детали счета в текущем периоде",
            -200.00,
            -33.33,
            "Одобрено",
            "Положительная корректировка детали счета в текущем периоде",
            "—",
            "Деталь: Абон. плата за VLAN",
            "0.00",
        )

        self.adjustments_page.check_adjustment(
            2,
            "",
            self.today_date_3_ddmmYYYY,
            "Положительная корректировка детали счета в текущем периоде",
            -100.00,
            -16.67,
            "Одобрено",
            "Положительная корректировка детали счета в текущем периоде",
            "—",
            "Деталь: Абон. плата за VLAN",
            "0.00",
        )

        self.adjustments_page.locators.OPEN_BILLING_FORM.click()
        self.adjustments_page.locators.START_BILLING.wait_to_be_visible()
        self.adjustments_page.locators.START_BILLING.not_to_be_enabled()

        self.adjustments_page.locators.BILLING_ADJUSTMENTS.wait_to_have_count(3)
        self.adjustments_page.locators.BILLING_TABLE_HEADERS.click(2)

        self.adjustments_page.locators.SWITCH_ONLY_SELECTED_TEXT.to_contain_text("Только выбранные: 3 на сумму -600.00")
        self.adjustments_page.locators.ADJUSTMENT_CHECKBOX.click(0)
        self.adjustments_page.locators.START_BILLING.wait_to_be_enabled()
        self.adjustments_page.locators.SWITCH_ONLY_SELECTED_TEXT.wait_to_have_text(
            "Только выбранные: 1 на сумму -300.00"
        )
        self.adjustments_page.locators.SWITCH_ONLY_SELECTED.click()
        self.adjustments_page.locators.BILLING_ADJUSTMENTS.wait_to_have_count(1)

        self.adjustments_page.locators.START_BILLING.click()
        self.adjustments_page.locators.INFO_MESSAGE.wait_to_be_visible()

        billing_profile_id = self.billing_api.get_billing_profile_id(self.client_info.account_id)
        self.billing_api.wait_billing(billing_profile_id)
        self.billing_api.wait_finish_billing(billing_profile_id, 3)
        bill_data = self.billing_api.get_list_of_bills([billing_profile_id])[0]
        bill_number = bill_data["billNumber"]

        self.adjustments_page.locators.UPDATE_TABLE_BTN.click()
        self.adjustments_page.check_adjustment(
            0,
            re.compile(bill_number + " от " + get_current_datetime_string(False) + r" \d\d:\d\d:\d\d"),
            self.today_date_1_ddmmYYYY,
            "Положительная корректировка детали счета в текущем периоде",
            -300.00,
            -50.00,
            "Одобрено",
            "Положительная корректировка детали счета в текущем периоде",
            "—",
            "Деталь: Абон. плата за VLAN",
            "0.00",
        )

        self.adjustments_page.check_adjustment(
            1,
            "",
            self.today_date_2_ddmmYYYY,
            "Положительная корректировка детали счета в текущем периоде",
            -200.00,
            -33.33,
            "Одобрено",
            "Положительная корректировка детали счета в текущем периоде",
            "—",
            "Деталь: Абон. плата за VLAN",
            "0.00",
        )

        self.adjustments_page.check_adjustment(
            2,
            "",
            self.today_date_3_ddmmYYYY,
            "Положительная корректировка детали счета в текущем периоде",
            -100.00,
            -16.67,
            "Одобрено",
            "Положительная корректировка детали счета в текущем периоде",
            "—",
            "Деталь: Абон. плата за VLAN",
            "0.00",
        )

        self.adjustments_page.locators.BURGER_MENU.click()
        self.adjustments_page.locators.BURGER_MENU_EL_BTN[8].click()
        self.adjustments_page.locators.PAGE_TITLE.wait_to_have_text("Биллинговые счета")

        self.billing_accounts.locators.ACCOUNT_NUMS_LIST.wait_to_have_count(1)
        self.billing_accounts.locators.ACCOUNT_NUMS_LIST.wait_to_be_visible()
        self.billing_accounts.locators.ACCOUNT_NUMS_LIST.click(0)
        self.billing_accounts.check_billing_properties_value(
            amount_due=300.00, output_balance=300.00, charged=300.00, charge_adjustments_recorded=300.00
        )

        self.billing_accounts.locators.DETAILS_TAB.click()
        self.billing_accounts.check_detail(
            detail_index=0,
            detail_name="Абон. плата за VLAN",
            charged=300.00,
            repaid=300.00,
            available_for_adjustment=300.00,
        )

        self.billing_accounts.locators.INVOICES_TAB.click()
        self.billing_accounts.check_invoice(
            invoice_index=1, invoice_type="Счет-фактура на начисления", amount=300.00, tax=50.00, balance=300.00
        )

    @allure.title("Запуск биллинга (корректировки начислений и платажей есть)")
    @allure.id(611941)
    @allure.link(
        url="allure.nexign.com/project/313/test-cases/611941",
        name="Запуск биллинга (корректировки начислений и платажей есть)",
    )
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=719302358",
        name="Запуск биллинга по корректировкам",
    )
    @allure.tag("can_auth", "success")
    @pytest.mark.regress
    def test_billing_when_adjustment_and_payments_exist(self, base_url: str) -> None:
        self.client_profile_page.open(
            f"{base_url}customer-hierarchy-management/accounts/{self.client_info.account_id}/account"
        )
        self.client_profile_page.locators.CLIENT_FIO.wait_to_be_visible()

        self.client_profile_page.locators.BURGER_MENU.click()
        self.client_profile_page.locators.BURGER_MENU_EL_BTN[1].click()
        self.adjustments_page.locators.PAGE_TITLE.wait_to_have_text("Платежи")

        self.payments_page.locators.CREATE_PAYMENT_BTN.wait_to_be_visible()
        self.payments_page.locators.CREATE_PAYMENT_BTN.click()

        self.create_payment_form.SET_AMOUNT.fill("10000.0")
        self.create_payment_form.PAYMENT_DATE_INPUT.click()
        self.create_payment_form.PAYMENT_DATE_INPUT.fill(self.yesterday_date_ddmmYYYY_HHMMSS)
        self.create_payment_form.PAYMENT_POINT.select_by_value("PNXL1/pointNx1")
        self.create_payment_form.INNER_ACCEPT_BTN.click()
        self.payment_id = self.payments_page.locators.CHECK_NUM_FIELDS[0].text

        self.payments_page.locators.BURGER_MENU.click()
        self.payments_page.locators.BURGER_MENU_EL_BTN[9].click()
        self.adjustments_page.locators.PAGE_TITLE.wait_to_have_text("Корректировки")

        self.adjustments_page.open_add_adjustment_form()
        self.adjustments_page.fill_add_adjustment_form(
            adjustment_option="charge",
            adjustment_type="positive",
            detail_name="Абон. плата за VLAN",
            date_time=self.today_date_1_ddmmYYYY,
            sum_with_tax="100",
            comment="Test comment 1",
        )

        self.adjustments_page.open_add_payment_form()
        self.adjustments_page.fill_add_adjustment_form(
            adjustment_option="payment",
            adjustment_type="positive",
            date_time=self.today_date_2_ddmmYYYY,
            sum_with_tax="200",
            comment="Test comment 2",
        )

        self.adjustments_page.open_add_payment_form()
        self.adjustments_page.fill_add_adjustment_form(
            adjustment_option="payment",
            adjustment_type="negative",
            date_time=self.today_date_3_ddmmYYYY,
            sum_with_tax="300",
            comment="Test comment 3",
        )
        self.adjustment_api.wait_all_adjustments_status(self.client_info.account_id, 3)

        self.adjustments_page.locators.UPDATE_TABLE_BTN.click()
        self.adjustments_page.check_adjustment(
            0,
            "",
            self.today_date_1_ddmmYYYY,
            "Отрицательная корректировка платежа",
            -300.00,
            -50.00,
            "Одобрено",
            "Корректировка платежа",
            "—",
            f"Платёж: {self.payment_id} от " + self.yesterday_date_ddmmYYYY,
            "0.00",
        )

        self.adjustments_page.check_adjustment(
            1,
            "",
            self.today_date_2_ddmmYYYY,
            "Положительная корректировка платежа",
            200.00,
            33.33,
            "Одобрено",
            "Положительная корректировка платежа",
            "—",
            f"Платёж: {self.payment_id} от " + self.yesterday_date_ddmmYYYY,
            "200.00",
        )

        self.adjustments_page.check_adjustment(
            2,
            "",
            self.today_date_3_ddmmYYYY,
            "Положительная корректировка детали счета в текущем периоде",
            -100.00,
            -16.67,
            "Одобрено",
            "Положительная корректировка детали счета в текущем периоде",
            "—",
            "Деталь: Абон. плата за VLAN",
            "0.00",
        )

        self.adjustments_page.locators.OPEN_BILLING_FORM.click()
        self.adjustments_page.locators.START_BILLING.wait_to_be_visible()
        self.adjustments_page.locators.START_BILLING.not_to_be_enabled()

        self.adjustments_page.locators.ADJUSTMENT_CHECKBOX.click(0)
        self.adjustments_page.locators.START_BILLING.wait_to_be_enabled()
        self.adjustments_page.locators.START_BILLING.click()
        self.adjustments_page.locators.MODAL_BODY_TEXT[0].wait_to_have_text(
            "Корректировки с типом 'Отрицательная корректировка платежа' не доступны для биллинга по объекту"
        )
        self.adjustments_page.locators.MODAL_CLOSE_BTN.click()

        self.adjustments_page.locators.OPEN_BILLING_FORM.click()
        self.adjustments_page.locators.START_BILLING.wait_to_be_visible()

        self.adjustments_page.locators.ADJUSTMENT_CHECKBOX.click(0)
        self.adjustments_page.locators.ADJUSTMENT_CHECKBOX.click(1)
        self.adjustments_page.locators.START_BILLING.wait_to_be_enabled()
        self.adjustments_page.locators.START_BILLING.click()
        self.adjustments_page.locators.MODAL_BODY_TEXT[0].wait_to_have_text(
            "Корректировки с типом 'Положительная корректировка платежа' не доступны для биллинга по объекту"
        )
        self.adjustments_page.locators.MODAL_CLOSE_BTN.click()

        self.adjustments_page.locators.OPEN_BILLING_FORM.click()
        self.adjustments_page.locators.START_BILLING.wait_to_be_visible()

        self.adjustments_page.check_adjustment_on_billing_form(
            0,
            "",
            "Отрицательная корректировка платежа",
            "-300.00",
            "-50.00",
            "Корректировка платежа",
            f"Платёж: {self.payment_id} от " + self.yesterday_date_ddmmYYYY,
            "0.00",
        )

        self.adjustments_page.check_adjustment_on_billing_form(
            1,
            "",
            "Положительная корректировка платежа",
            "200.00",
            "33.33",
            "Положительная корректировка платежа",
            f"Платёж: {self.payment_id} от " + self.yesterday_date_ddmmYYYY,
            "200.00",
        )

        self.adjustments_page.check_adjustment_on_billing_form(
            2,
            "",
            "Положительная корректировка детали счета в текущем периоде",
            "-100.00",
            "-16.67",
            "Положительная корректировка детали счета в текущем периоде",
            "Деталь: Абон. плата за VLAN",
            "0.00",
        )

        self.adjustments_page.locators.CROSS_BTN.click()
        self.adjustments_page.locators.BURGER_MENU.click()
        self.adjustments_page.locators.BURGER_MENU_EL_BTN[8].click()
        self.billing_accounts.locators.PAGE_TITLE.wait_to_have_text("Биллинговые счета")
        self.billing_accounts.locators.ACCOUNT_EMPTY_LIST.wait_to_be_visible()

    @allure.title("Запуск биллинга (корректировки начислений и платежей отсутствуют,)")
    @allure.id(605088)
    @allure.link(
        url="allure.nexign.com/project/313/test-cases/605088",
        name="Запуск биллинга (корректировки начислений и платежей отсутствуют,)",
    )
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=719302358",
        name="Запуск биллинга по корректировкам",
    )
    @allure.tag("can_auth", "success")
    @pytest.mark.regress
    def test_billing_when_adjustment_and_payments_do_not_exist(self, base_url: str) -> None:
        self.client_profile_page.open(
            f"{base_url}customer-hierarchy-management/accounts/{self.client_info.account_id}/account"
        )
        self.client_profile_page.locators.CLIENT_FIO.wait_to_be_visible()

        self.client_profile_page.locators.BURGER_MENU.click()
        self.client_profile_page.locators.BURGER_MENU_EL_BTN[9].click()
        self.adjustments_page.locators.PAGE_TITLE.wait_to_have_text("Корректировки")

        self.adjustments_page.locators.OPEN_BILLING_FORM.wait_to_be_visible()
        self.adjustments_page.locators.OPEN_BILLING_FORM.click()
        self.adjustments_page.locators.START_BILLING.wait_to_be_visible()
        self.adjustments_page.locators.START_BILLING.not_to_be_enabled()

        self.adjustments_page.locators.UPDATE_BILLING_TABLE_BUTTON.click()
        self.adjustments_page.locators.START_BILLING.wait_to_be_visible()
        self.adjustments_page.locators.START_BILLING.not_to_be_enabled()
