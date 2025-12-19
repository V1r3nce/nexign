import re

import allure
import pytest

from api.nbss.finances.adjustment_requests import AdjustmentRequests
from api.nbss.finances.billing_requests import BillingRequests
from api.nbss.finances.payments_requests import PaymentsRequests
from common.helpers.data_generator import get_current_datetime_string, get_shifted_datetime_string
from common.helpers.time_helpers import delay, get_shifted_datetime
from models.client import IndividualClient
from pages.locators.nbss.dynamic_form_elements import CreatePaymentForm
from pages.locators.nbss.finances.adjustments import ChooseAdjustmentObjectForm
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.finances.adjustments_page import AdjustmentsPage
from pages.nbss.finances.billing_accounts_page import BillingAccountsPage
from pages.nbss.finances.payments_page import PaymentsPage


@pytest.mark.udb
@pytest.mark.nbss_portal
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
    def setup(self, nexign_stand_login, create_user_with_agreement_and_account: IndividualClient) -> None:
        self.client_profile_page = ClientProfilePage()
        self.adjustments_page = AdjustmentsPage()
        self.choose_adjustment_object_form = ChooseAdjustmentObjectForm()
        self.billing_accounts = BillingAccountsPage()
        self.client_info = create_user_with_agreement_and_account
        self.payments_page = PaymentsPage()
        self.create_payment_form = CreatePaymentForm()

        self.billing_api = BillingRequests()
        self.adjustment_api = AdjustmentRequests()
        self.payment_api = PaymentsRequests()

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
            f"{base_url}customer-hierarchy-management/accounts/{self.client_info.agreements[0].accounts[0].id}/account"
        )
        self.client_profile_page.locators.CLIENT_FIO.wait_to_be_visible()

        self.client_profile_page.locators.BURGER_MENU.select_by_value("Финансы > Корректировки")
        self.adjustments_page.locators.SELECTED_TAB_TITLE.wait_to_have_text("Корректировки")

        self.adjustments_page.open_add_adjustment_form()
        self.adjustments_page.fill_add_adjustment_form(
            adjustment_option="charge",
            adjustment_type="positive",
            detail_name="Абон. плата за VLAN",
            date_time=self.today_date_1_ddmmYYYY,
            sum_with_tax="100",
            comment="Test comment 1",
        )
        self.adjustment_api.wait_adjustment_status(self.client_info.agreements[0].accounts[0].id)

        self.adjustments_page.locators.UPDATE_TABLE_BTN.click()
        self.adjustments_page.check_adjustment(
            idx=0,
            included_in_bill="",
            date=self.today_date_1_ddmmYYYY,
            adjustment_type="Положительная корректировка детали счета в текущем периоде",
            sum_with_tax=-100.00,
            tax=-16.67,
            status="Одобрено",
            reason="Положительная корректировка детали счета в текущем периоде",
            target_type="—",
            target="Добавлена деталь: Абон. плата за VLAN",
            advance="0.00",
        )

        self.adjustments_page.locators.OPEN_BILLING_FORM.click()
        self.adjustments_page.locators.START_BILLING.wait_to_be_visible()
        self.adjustments_page.locators.START_BILLING.not_to_be_enabled()

        self.adjustments_page.locators.ADJUSTMENT_CHECKBOX.click(0)
        self.adjustments_page.locators.START_BILLING.wait_to_be_enabled()
        self.adjustments_page.locators.START_BILLING.click()
        self.adjustments_page.locators.INFO_MESSAGE.wait_to_be_visible()

        billing_profile_id = self.billing_api.get_billing_profile_id(self.client_info.agreements[0].accounts[0].id)
        self.billing_api.wait_billing(billing_profile_id)
        self.billing_api.wait_finish_billing(billing_profile_id, 3)
        bill_data = self.billing_api.get_list_of_bills([billing_profile_id])[0]
        bill_number = bill_data["billNumber"]

        self.adjustments_page.locators.UPDATE_TABLE_BTN.click()
        self.adjustments_page.check_adjustment(
            idx=0,
            included_in_bill=re.compile(bill_number + " от " + get_current_datetime_string(False) + r" \d\d:\d\d:\d\d"),
            date=self.today_date_1_ddmmYYYY,
            adjustment_type="Положительная корректировка детали счета в текущем периоде",
            sum_with_tax=-100.00,
            tax=-16.67,
            status="Одобрено",
            reason="Положительная корректировка детали счета в текущем периоде",
            target_type="—",
            target="Добавлена деталь: Абон. плата за VLAN",
            advance="0.00",
        )

        self.adjustments_page.locators.BURGER_MENU.select_by_value("Финансы > Биллинговые счета")
        self.billing_accounts.locators.SELECTED_TAB_TITLE.wait_to_have_text("Биллинговые счета")

        self.billing_accounts.locators.ACCOUNT_NUMS_LIST.wait_to_have_count(1)
        self.billing_accounts.locators.ACCOUNT_NUMS_LIST.wait_to_be_visible()
        self.billing_accounts.locators.ACCOUNT_NUMS_LIST.click(0)
        self.billing_accounts.check_billing_properties_value(
            amount_due=100.00, output_balance=100.00, charge_adjustments_recorded=100.00
        )

        self.billing_accounts.locators.DETAILS_TAB.click()
        self.billing_accounts.check_detail(
            detail_index=0,
            detail_name="Абон. плата за VLAN",
            charged=100.00,
            repaid=0.00,
            available_for_adjustment=100.00,
            adjusted=-100.00,
        )

        self.billing_accounts.locators.INVOICES_TAB.click()
        self.billing_accounts.check_invoice(
            invoice_index=0,
            invoice_type="Счет-фактура на начисления",
            amount=100.00,
            tax=16.67,
            balance=100.00,
            adjusted=0.00,
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
            f"{base_url}customer-hierarchy-management/accounts/{self.client_info.agreements[0].accounts[0].id}/account"
        )
        self.client_profile_page.locators.CLIENT_FIO.wait_to_be_visible()

        self.client_profile_page.locators.BURGER_MENU.select_by_value("Финансы > Корректировки")
        self.adjustments_page.locators.SELECTED_TAB_TITLE.wait_to_have_text("Корректировки")

        self.adjustments_page.open_add_adjustment_form()
        self.adjustments_page.fill_add_adjustment_form(
            adjustment_option="charge",
            adjustment_type="positive",
            detail_name="Абон. плата за VLAN",
            date_time=self.today_date_1_ddmmYYYY,
            sum_with_tax="100",
            comment="Test comment 1",
        )

        self.adjustments_page.open_add_adjustment_form()
        self.adjustments_page.fill_add_adjustment_form(
            adjustment_option="charge",
            adjustment_type="positive",
            detail_name="Абон. плата за VLAN",
            date_time=self.today_date_2_ddmmYYYY,
            sum_with_tax="200",
            comment="Test comment 2",
        )

        self.adjustments_page.open_add_adjustment_form()
        self.adjustments_page.fill_add_adjustment_form(
            adjustment_option="charge",
            adjustment_type="positive",
            detail_name="Абон. плата за VLAN",
            date_time=self.today_date_3_ddmmYYYY,
            sum_with_tax="300",
            comment="Test comment 3",
        )
        self.adjustment_api.wait_all_adjustments_status(self.client_info.agreements[0].accounts[0].id, 3)

        self.adjustments_page.locators.ADJUSTMENT_TITLE.click(3)
        self.adjustments_page.locators.UPDATE_TABLE_BTN.click()
        self.adjustments_page.check_adjustment(
            idx=0,
            included_in_bill="",
            date=self.today_date_1_ddmmYYYY,
            adjustment_type="Положительная корректировка детали счета в текущем периоде",
            sum_with_tax=-300.00,
            tax=-50.00,
            status="Одобрено",
            reason="Положительная корректировка детали счета в текущем периоде",
            target_type="—",
            target="Добавлена деталь: Абон. плата за VLAN",
            advance="0.00",
        )

        self.adjustments_page.check_adjustment(
            idx=1,
            included_in_bill="",
            date=self.today_date_2_ddmmYYYY,
            adjustment_type="Положительная корректировка детали счета в текущем периоде",
            sum_with_tax=-200.00,
            tax=-33.33,
            status="Одобрено",
            reason="Положительная корректировка детали счета в текущем периоде",
            target_type="—",
            target="Добавлена деталь: Абон. плата за VLAN",
            advance="0.00",
        )

        self.adjustments_page.check_adjustment(
            idx=2,
            included_in_bill="",
            date=self.today_date_3_ddmmYYYY,
            adjustment_type="Положительная корректировка детали счета в текущем периоде",
            sum_with_tax=-100.00,
            tax=-16.67,
            status="Одобрено",
            reason="Положительная корректировка детали счета в текущем периоде",
            target_type="—",
            target="Добавлена деталь: Абон. плата за VLAN",
            advance="0.00",
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

        billing_profile_id = self.billing_api.get_billing_profile_id(self.client_info.agreements[0].accounts[0].id)
        self.billing_api.wait_billing(billing_profile_id)
        self.billing_api.wait_finish_billing(billing_profile_id, 3)
        bill_data = self.billing_api.get_list_of_bills([billing_profile_id])[0]
        bill_number = bill_data["billNumber"]

        self.adjustments_page.locators.UPDATE_TABLE_BTN.click()
        self.adjustments_page.check_adjustment(
            idx=0,
            included_in_bill=re.compile(bill_number + " от " + get_current_datetime_string(False) + r" \d\d:\d\d:\d\d"),
            date=self.today_date_1_ddmmYYYY,
            adjustment_type="Положительная корректировка детали счета в текущем периоде",
            sum_with_tax=-300.00,
            tax=-50.00,
            status="Одобрено",
            reason="Положительная корректировка детали счета в текущем периоде",
            target_type="—",
            target="Добавлена деталь: Абон. плата за VLAN",
            advance="0.00",
        )

        self.adjustments_page.check_adjustment(
            idx=1,
            included_in_bill="",
            date=self.today_date_2_ddmmYYYY,
            adjustment_type="Положительная корректировка детали счета в текущем периоде",
            sum_with_tax=-200.00,
            tax=-33.33,
            status="Одобрено",
            reason="Положительная корректировка детали счета в текущем периоде",
            target_type="—",
            target="Добавлена деталь: Абон. плата за VLAN",
            advance="0.00",
        )

        self.adjustments_page.check_adjustment(
            idx=2,
            included_in_bill="",
            date=self.today_date_3_ddmmYYYY,
            adjustment_type="Положительная корректировка детали счета в текущем периоде",
            sum_with_tax=-100.00,
            tax=-16.67,
            status="Одобрено",
            reason="Положительная корректировка детали счета в текущем периоде",
            target_type="—",
            target="Добавлена деталь: Абон. плата за VLAN",
            advance="0.00",
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
            "Добавлена деталь: Абон. плата за VLAN",
            "0.00",
        )

        self.adjustments_page.check_adjustment_on_billing_form(
            1,
            "",
            "Положительная корректировка детали счета в текущем периоде",
            "-100.00",
            "-16.67",
            "Положительная корректировка детали счета в текущем периоде",
            "Добавлена деталь: Абон. плата за VLAN",
            "0.00",
        )

        self.adjustments_page.locators.CROSS_BTN.click()
        self.adjustments_page.locators.BURGER_MENU.select_by_value("Финансы > Биллинговые счета")
        self.billing_accounts.locators.SELECTED_TAB_TITLE.wait_to_have_text("Биллинговые счета")

        self.billing_accounts.locators.ACCOUNT_NUMS_LIST.wait_to_have_count(1)
        self.billing_accounts.locators.ACCOUNT_NUMS_LIST.wait_to_be_visible()
        self.billing_accounts.locators.ACCOUNT_NUMS_LIST.click(0)
        self.billing_accounts.check_billing_properties_value(
            amount_due=300.00, output_balance=300.00, charge_adjustments_recorded=300.00
        )

        self.billing_accounts.locators.DETAILS_TAB.click()
        self.billing_accounts.check_detail(
            detail_index=0,
            detail_name="Абон. плата за VLAN",
            charged=300.00,
            available_for_adjustment=300.00,
            adjusted=-300.00,
        )

        self.billing_accounts.locators.INVOICES_TAB.click()
        self.billing_accounts.check_invoice(
            invoice_index=0,
            invoice_type="Счет-фактура на начисления",
            amount=300.00,
            tax=50.00,
            balance=300.00,
            adjusted=0.00,
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
            f"{base_url}customer-hierarchy-management/accounts/{self.client_info.agreements[0].accounts[0].id}/account"
        )
        self.client_profile_page.locators.CLIENT_FIO.wait_to_be_visible()

        self.client_profile_page.locators.BURGER_MENU.select_by_value("Финансы > Корректировки")
        self.adjustments_page.locators.SELECTED_TAB_TITLE.wait_to_have_text("Корректировки")

        self.adjustments_page.open_add_adjustment_form()
        self.adjustments_page.fill_add_adjustment_form(
            adjustment_option="charge",
            adjustment_type="positive",
            detail_name="Абон. плата за VLAN",
            date_time=self.today_date_1_ddmmYYYY,
            sum_with_tax="100",
            comment="Test comment 1",
        )

        self.adjustments_page.open_add_adjustment_form()
        self.adjustments_page.fill_add_adjustment_form(
            adjustment_option="charge",
            adjustment_type="positive",
            detail_name="Абон. плата за VLAN",
            date_time=self.today_date_2_ddmmYYYY,
            sum_with_tax="200",
            comment="Test comment 2",
        )

        self.adjustments_page.open_add_adjustment_form()
        self.adjustments_page.fill_add_adjustment_form(
            adjustment_option="charge",
            adjustment_type="positive",
            detail_name="Абон. плата за VLAN",
            date_time=self.today_date_3_ddmmYYYY,
            sum_with_tax="300",
            comment="Test comment 3",
        )
        self.adjustment_api.wait_all_adjustments_status(self.client_info.agreements[0].accounts[0].id, 3)

        self.adjustments_page.locators.ADJUSTMENT_TITLE.click(3)
        self.adjustments_page.locators.UPDATE_TABLE_BTN.click()
        self.adjustments_page.check_adjustment(
            idx=0,
            included_in_bill="",
            date=self.today_date_1_ddmmYYYY,
            adjustment_type="Положительная корректировка детали счета в текущем периоде",
            sum_with_tax=-300.00,
            tax=-50.00,
            status="Одобрено",
            reason="Положительная корректировка детали счета в текущем периоде",
            target_type="—",
            target="Добавлена деталь: Абон. плата за VLAN",
            advance="0.00",
        )

        self.adjustments_page.check_adjustment(
            idx=1,
            included_in_bill="",
            date=self.today_date_2_ddmmYYYY,
            adjustment_type="Положительная корректировка детали счета в текущем периоде",
            sum_with_tax=-200.00,
            tax=-33.33,
            status="Одобрено",
            reason="Положительная корректировка детали счета в текущем периоде",
            target_type="—",
            target="Добавлена деталь: Абон. плата за VLAN",
            advance="0.00",
        )

        self.adjustments_page.check_adjustment(
            idx=2,
            included_in_bill="",
            date=self.today_date_3_ddmmYYYY,
            adjustment_type="Положительная корректировка детали счета в текущем периоде",
            sum_with_tax=-100.00,
            tax=-16.67,
            status="Одобрено",
            reason="Положительная корректировка детали счета в текущем периоде",
            target_type="—",
            target="Добавлена деталь: Абон. плата за VLAN",
            advance="0.00",
        )

        self.adjustments_page.locators.OPEN_BILLING_FORM.click()
        self.adjustments_page.locators.START_BILLING.wait_to_be_visible()
        self.adjustments_page.locators.START_BILLING.not_to_be_enabled()

        self.adjustments_page.locators.BILLING_ADJUSTMENTS.wait_to_have_count(3)
        self.adjustments_page.locators.BILLING_TABLE_HEADERS.click(2)

        self.adjustments_page.locators.SWITCH_ONLY_SELECTED_TEXT.to_contain_text("Только выбранные: 0 на сумму 0.00")
        self.adjustments_page.locators.ADJUSTMENT_CHECKBOX.click(0)
        self.adjustments_page.locators.START_BILLING.wait_to_be_enabled()
        self.adjustments_page.locators.SWITCH_ONLY_SELECTED_TEXT.wait_to_have_text(
            "Только выбранные: 1 на сумму -300.00"
        )
        self.adjustments_page.locators.SWITCH_ONLY_SELECTED.click()
        self.adjustments_page.locators.BILLING_ADJUSTMENTS.wait_to_have_count(1)

        self.adjustments_page.locators.START_BILLING.click()
        self.adjustments_page.locators.INFO_MESSAGE.wait_to_be_visible()

        billing_profile_id = self.billing_api.get_billing_profile_id(self.client_info.agreements[0].accounts[0].id)
        self.billing_api.wait_billing(billing_profile_id)
        self.billing_api.wait_finish_billing(billing_profile_id, 3)
        bill_data = self.billing_api.get_list_of_bills([billing_profile_id])[0]
        bill_number = bill_data["billNumber"]

        self.adjustments_page.locators.UPDATE_TABLE_BTN.click()
        self.adjustments_page.check_adjustment(
            idx=0,
            included_in_bill=re.compile(bill_number + " от " + get_current_datetime_string(False) + r" \d\d:\d\d:\d\d"),
            date=self.today_date_1_ddmmYYYY,
            adjustment_type="Положительная корректировка детали счета в текущем периоде",
            sum_with_tax=-300.00,
            tax=-50.00,
            status="Одобрено",
            reason="Положительная корректировка детали счета в текущем периоде",
            target_type="—",
            target="Добавлена деталь: Абон. плата за VLAN",
            advance="0.00",
        )

        self.adjustments_page.check_adjustment(
            idx=1,
            included_in_bill="",
            date=self.today_date_2_ddmmYYYY,
            adjustment_type="Положительная корректировка детали счета в текущем периоде",
            sum_with_tax=-200.00,
            tax=-33.33,
            status="Одобрено",
            reason="Положительная корректировка детали счета в текущем периоде",
            target_type="—",
            target="Добавлена деталь: Абон. плата за VLAN",
            advance="0.00",
        )

        self.adjustments_page.check_adjustment(
            idx=2,
            included_in_bill="",
            date=self.today_date_3_ddmmYYYY,
            adjustment_type="Положительная корректировка детали счета в текущем периоде",
            sum_with_tax=-100.00,
            tax=-16.67,
            status="Одобрено",
            reason="Положительная корректировка детали счета в текущем периоде",
            target_type="—",
            target="Добавлена деталь: Абон. плата за VLAN",
            advance="0.00",
        )

        self.adjustments_page.locators.BURGER_MENU.select_by_value("Финансы > Биллинговые счета")
        self.adjustments_page.locators.SELECTED_TAB_TITLE.wait_to_have_text("Биллинговые счета")

        self.billing_accounts.locators.ACCOUNT_NUMS_LIST.wait_to_have_count(1)
        self.billing_accounts.locators.ACCOUNT_NUMS_LIST.wait_to_be_visible()
        self.billing_accounts.locators.ACCOUNT_NUMS_LIST.click(0)
        self.billing_accounts.check_billing_properties_value(
            amount_due=300.00, output_balance=300.00, charge_adjustments_recorded=300.00
        )

        self.billing_accounts.locators.DETAILS_TAB.click()
        self.billing_accounts.check_detail(
            detail_index=0,
            detail_name="Абон. плата за VLAN",
            charged=300.00,
            adjusted=-300.00,
            repaid=0.00,
            available_for_adjustment=300.00,
        )

        self.billing_accounts.locators.INVOICES_TAB.click()
        self.billing_accounts.check_invoice(
            invoice_index=0,
            invoice_type="Счет-фактура на начисления",
            amount=300.00,
            tax=50.00,
            balance=300.00,
            adjusted=0.00,
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
            f"{base_url}customer-hierarchy-management/accounts/{self.client_info.agreements[0].accounts[0].id}/account"
        )
        self.client_profile_page.locators.CLIENT_FIO.wait_to_be_visible()

        self.client_profile_page.locators.BURGER_MENU.select_by_value("Финансы > Платежи")
        self.adjustments_page.locators.SELECTED_TAB_TITLE.wait_to_have_text("Платежи")

        self.payments_page.payment_elements.CREATE_PAYMENT_BTN.wait_to_be_visible()
        self.payments_page.payment_elements.CREATE_PAYMENT_BTN.click()

        self.create_payment_form.SET_AMOUNT.fill("10000.0")
        self.create_payment_form.PAYMENT_DATE_INPUT.click()
        self.create_payment_form.PAYMENT_DATE_INPUT.fill(self.yesterday_date_ddmmYYYY_HHMMSS)
        self.create_payment_form.PAYMENT_POINT.select_by_value("PNXL1/pointNx1")
        self.create_payment_form.INNER_ACCEPT_BTN.click()
        self.payment_id = self.payments_page.payment_elements.CHECK_NUM_FIELDS[0].text

        self.payments_page.payment_elements.BURGER_MENU.select_by_value("Финансы > Корректировки")
        self.adjustments_page.locators.SELECTED_TAB_TITLE.wait_to_have_text("Корректировки")

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
        self.adjustment_api.wait_all_adjustments_status(self.client_info.agreements[0].accounts[0].id, 3)

        self.adjustments_page.locators.UPDATE_TABLE_BTN.click()
        self.adjustments_page.check_adjustment(
            idx=0,
            included_in_bill="",
            date=self.today_date_1_ddmmYYYY,
            adjustment_type="Отрицательная корректировка платежа",
            sum_with_tax=-300.00,
            tax=-50.00,
            status="Одобрено",
            reason="Корректировка платежа",
            target_type="—",
            target=f"Платёж: {self.payment_id} от " + self.yesterday_date_ddmmYYYY,
            advance="0.00",
        )

        self.adjustments_page.check_adjustment(
            idx=1,
            included_in_bill="",
            date=self.today_date_2_ddmmYYYY,
            adjustment_type="Положительная корректировка платежа",
            sum_with_tax=200.00,
            tax=33.33,
            status="Одобрено",
            reason="Положительная корректировка платежа",
            target_type="—",
            target=f"Платёж: {self.payment_id} от " + self.yesterday_date_ddmmYYYY,
            advance="200.00",
        )

        self.adjustments_page.check_adjustment(
            idx=2,
            included_in_bill="",
            date=self.today_date_3_ddmmYYYY,
            adjustment_type="Положительная корректировка детали счета в текущем периоде",
            sum_with_tax=-100.00,
            tax=-16.67,
            status="Одобрено",
            reason="Положительная корректировка детали счета в текущем периоде",
            target_type="—",
            target="Добавлена деталь: Абон. плата за VLAN",
            advance="0.00",
        )

        self.adjustments_page.locators.OPEN_BILLING_FORM.click()
        self.adjustments_page.locators.START_BILLING.wait_to_be_visible()
        self.adjustments_page.locators.START_BILLING.not_to_be_enabled()

        self.adjustments_page.locators.ROWS_BILLING.wait_to_have_count(1)
        self.adjustments_page.check_adjustment_on_billing_form(
            0,
            "",
            "Положительная корректировка детали счета в текущем периоде",
            "-100.00",
            "-16.67",
            "Положительная корректировка детали счета в текущем периоде",
            "Добавлена деталь: Абон. плата за VLAN",
            "0.00",
        )

        self.adjustments_page.locators.CROSS_BTN.click()
        self.adjustments_page.locators.BURGER_MENU.select_by_value("Биллинговые счета")
        self.billing_accounts.locators.SELECTED_TAB_TITLE.wait_to_have_text("Биллинговые счета")
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
            f"{base_url}customer-hierarchy-management/accounts/{self.client_info.agreements[0].accounts[0].id}/account"
        )
        self.client_profile_page.locators.CLIENT_FIO.wait_to_be_visible()

        self.client_profile_page.locators.BURGER_MENU.select_by_value("Финансы > Корректировки")
        self.adjustments_page.locators.SELECTED_TAB_TITLE.wait_to_have_text("Корректировки")

        delay(1, "Нестабильно кликает на 'Провести биллинг'")
        self.adjustments_page.locators.OPEN_BILLING_FORM.wait_to_be_visible()
        self.adjustments_page.locators.OPEN_BILLING_FORM.click()
        self.adjustments_page.locators.START_BILLING.wait_to_be_visible()
        self.adjustments_page.locators.START_BILLING.not_to_be_enabled()

        self.adjustments_page.locators.UPDATE_BILLING_TABLE_BUTTON.click()
        self.adjustments_page.locators.START_BILLING.wait_to_be_visible()
        self.adjustments_page.locators.START_BILLING.not_to_be_enabled()
