import re

import allure
import pytest

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from api.nbss.finances.adjustment_requests import AdjustmentRequests
from api.nbss.finances.billing_requests import BillingRequests
from api.nbss.finances.payments_requests import PaymentsRequests
from api.nbss.personal_account_requests import PersonalAccountRequests
from common.helpers.data_generator import calc_tax, get_current_datetime_string
from common.helpers.env_helper import BASE_URL, UserData
from common.helpers.time_helpers import delay, get_current_moscow_datetime
from models.client import OrganizationClient
from models.context import test_context
from models.inquiry import prepare_inquiries
from pages.locators.nbss.finances.adjustments import CreateAdjustmentForm
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.finances.adjustments_page import AdjustmentsPage
from pages.nbss.finances.billing_accounts_page import BillingAccountsPage
from tests.conftest import CreatedImsis


@allure.suite("E2E_83 Выставление счетов-фактур")
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestMakeInvoice:
    @pytest.fixture(autouse=True)
    def setup(
        self, nexign_stand_login, add_two_imsi_free_shipped: CreatedImsis, create_organization: OrganizationClient
    ) -> None:
        self.client_request_api = ClientInquiriesRequests()
        self.payment_api = PaymentsRequests()
        self.billing_api = BillingRequests()
        self.adjustment_api = AdjustmentRequests()
        self.personal_account_api = PersonalAccountRequests()

        self.client_profile = ClientProfilePage()
        self.adjustments_page = AdjustmentsPage()
        self.billing_accounts = BillingAccountsPage()
        self.create_adjustment_form = CreateAdjustmentForm()
        self.inquiry = self.client_request_api.product_sale(inquiry=prepare_inquiries("internet"))
        self.balance = 100.00
        self.payment_api.create_default_payment(
            test_context.client.agreements[0].accounts[0].id,
            self.inquiry.product.one_time_payment + self.inquiry.product.subscription_fee + self.balance,
        )
        self.personal_account_api.wait_check_current_main_balance(
            test_context.client.agreements[0].accounts[0].id, self.balance
        )
        self.personal_account_api.wait_accruals(test_context.client.user_id)
        billing_profile_id = self.billing_api.get_billing_profile_id(test_context.client.agreements[0].accounts[0].id)
        self.billing_api.run_unscheduled_billing(billing_profile_id)
        self.billing_api.wait_billing(billing_profile_id)
        self.billing_api.wait_finish_billing(billing_profile_id, 3)

    @allure.title("01. Выставление счета-фактуры")
    @allure.id(586019)
    def test_create_payment_invoice(self) -> None:
        self.client_profile.open(
            f"{BASE_URL}customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
        )
        self.client_profile.locators.CLIENT_FIO.wait_to_be_visible()

        with allure.step("Перейти на форму 'Фин карточка' - 'Биллинговые счета'"):
            self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Биллинговые счета")
            self.billing_accounts.locators.SELECTED_TAB_TITLE.wait_to_have_text("Биллинговые счета")

        self.billing_accounts.locators.ACCOUNT_NUMS_LIST.wait_to_have_count(1)
        self.billing_accounts.locators.ACCOUNT_NUMS_LIST.click(0)
        self.billing_accounts.locators.INVOICES_TAB.click()
        invoice_index = self.billing_accounts.get_invoice_index("Счет-фактура на начисления")
        self.billing_accounts.check_invoice(
            invoice_index=invoice_index,
            invoice_type="Счет-фактура на начисления",
            amount=self.inquiry.product.one_time_payment + self.inquiry.product.subscription_fee,
            tax=calc_tax(self.inquiry.product.one_time_payment + self.inquiry.product.subscription_fee),
            adjusted=0,
            balance=self.inquiry.product.one_time_payment + self.inquiry.product.subscription_fee,
        )

    @allure.title("02. Выставление исправленного счета-фактуры")
    @allure.id(585549)
    def test_create_edited_payment_invoice(self) -> None:
        self.client_profile.open(
            f"{BASE_URL}customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
        )
        self.client_profile.locators.CLIENT_FIO.wait_to_be_visible()

        with allure.step("Добавить корректировку"):
            self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Корректировки")
            self.adjustments_page.locators.SELECTED_TAB_TITLE.wait_to_have_text("Корректировки")
            self.adjustments_page.locators.ADD_ADJUSTMENT_BTN.select_by_value("Ввод корректировки начисления")
            tax_invoice_type = "Счет-фактура на начисления"
            self.adjustments_page.fill_tax_invoice_input_create_adjustment_form(tax_invoice_type)
            self.create_adjustment_form.ADJUSTMENT_TYPE_RADIOBUTTONS.select_by_value("Отрицательная корректировка")
            adjustment_sum = self.balance - 1
            tax = self.adjustments_page.fill_other_required_input_create_adjustment_form(
                adjustment_sum=adjustment_sum,
                reason="Отрицательная корректировка счёт-фактуры",
            )
            adjustment_date = get_current_datetime_string(is_full_format=False)
            self.create_adjustment_form.TITLE.not_to_be_visible()
            self.adjustments_page.check_adjustment(
                idx=0,
                adjustment_type="Отрицательная корректировка счёт-фактуры",
                date=adjustment_date,
                sum_with_tax=adjustment_sum,
                tax=tax,
                status="Создание",
                reason="Отрицательная корректировка счёт-фактуры",
            )
            self.adjustment_api.wait_adjustment_status(test_context.client.agreements[0].accounts[0].id)
            self.adjustments_page.locators.UPDATE_TABLE_BTN.click()
            self.adjustments_page.check_adjustment(idx=0, status="Одобрено")

        billing_profile_id = self.billing_api.get_billing_profile_id(test_context.client.agreements[0].accounts[0].id)
        self.billing_api.run_unscheduled_billing(billing_profile_id)
        self.billing_api.wait_billing(billing_profile_id, 2)
        self.billing_api.wait_finish_billing(billing_profile_id, 3)

        with allure.step("Перейти на форму 'Фин карточка' - 'Биллинговые счета'"):
            self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Биллинговые счета")
            self.billing_accounts.locators.SELECTED_TAB_TITLE.wait_to_have_text("Биллинговые счета")

        delay(2, reason="Время на загрузку второго биллинга")
        self.billing_accounts.locators.REFRESH_BTN.click()
        self.billing_accounts.locators.ACCOUNT_NUMS_LIST.wait_to_have_count(2)
        self.billing_accounts.locators.ACCOUNT_NUMS_LIST.click(1)
        self.billing_accounts.locators.INVOICES_TAB.click()
        invoice_index = self.billing_accounts.get_invoice_index("Исправленный счет-фактура на начисления")
        self.billing_accounts.check_invoice(
            invoice_index=invoice_index,
            invoice_type="Исправленный счет-фактура на начисления",
            amount=self.inquiry.product.subscription_fee + self.inquiry.product.one_time_payment - adjustment_sum,
            tax=calc_tax(self.inquiry.product.one_time_payment + self.inquiry.product.subscription_fee - adjustment_sum),
            adjustment_tax_invoice=re.compile(r"\d{4}-\d{2}-\d{2}"),
            adjustment_number=1,
            adjusted=adjustment_sum,
            balance=self.inquiry.product.subscription_fee + self.inquiry.product.one_time_payment - adjustment_sum,
        )


@allure.suite("E2E_83 Выставление счетов-фактур")
@pytest.mark.regress
class TestMakePreInvoice:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login, create_organization_with_agreement_and_account: OrganizationClient) -> None:
        self.payment_api = PaymentsRequests()
        self.billing_api = BillingRequests()
        self.personal_account_api = PersonalAccountRequests()

        self.client_profile = ClientProfilePage()
        self.billing_accounts = BillingAccountsPage()
        self.billing_accounts_page = BillingAccountsPage()
        self.balance = 100.00
        self.payment_api.create_default_payment(test_context.client.agreements[0].accounts[0].id, self.balance)
        self.personal_account_api.wait_check_current_main_balance(
            test_context.client.agreements[0].accounts[0].id, self.balance
        )

    @allure.title("04. Выставление авансового счета-фактуры")
    @allure.id(618615)
    def test_create_prepayment_invoice(self) -> None:
        self.client_profile.open(
            f"{BASE_URL}customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
        )
        self.client_profile.locators.CLIENT_FIO.wait_to_be_visible()

        with allure.step("Перейти на форму 'Фин карточка' - 'Биллинговые счета'"):
            self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Биллинговые счета")
            self.billing_accounts.locators.SELECTED_TAB_TITLE.wait_to_have_text("Биллинговые счета")

        with allure.step("На форме биллинговые счета нажимаем на кнопку 'Запуск биллинга' (+)"):
            delay(4, reason="Время на загрузку нового договора и счета")
            billing_date = get_current_moscow_datetime()
            billing_task = self.billing_accounts_page.run_unscheduled_billing()

        with allure.step("Нажимаем на кнопку 'Список заданий биллинга'"):
            self.billing_accounts_page.locators.BILLING_TASKS_BTN.click()
            self.billing_accounts_page.locators.BILLING_TASK.wait_to_have_count(1)
            self.billing_accounts_page.check_billing_task(billing_type="Внеочередной биллинг", status="Выполняется")
            self.billing_api.wait_finish_billing(
                self.billing_api.get_billing_profile_id(test_context.client.agreements[0].accounts[0].id)
            )

        self.billing_accounts_page.locators.UPDATE_BILLING_TASKS_BTN.click()
        self.billing_accounts_page.check_billing_task(
            task=billing_task,
            task_type="Биллинг",
            status="Завершено",
            user=UserData.login,
            billing_type="Внеочередной биллинг",
            bill_date=billing_date,
        )
        self.billing_accounts_page.locators.TASKS_CLOSE_BTN.click()

        self.billing_accounts.locators.REFRESH_BTN.click()
        self.billing_accounts.locators.ACCOUNT_NUMS_LIST.wait_to_have_count(1)
        self.billing_accounts.locators.ACCOUNT_NUMS_LIST.click(0)
        self.billing_accounts.locators.INVOICES_TAB.click()
        self.billing_accounts.check_invoice(
            invoice_index=0,
            invoice_type="Авансовый счет-фактура",
            amount=self.balance,
            tax=calc_tax(self.balance),
        )
