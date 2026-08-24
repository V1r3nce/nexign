import random

import allure
import pytest

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from api.nbss.finances.adjustment_requests import AdjustmentRequests
from api.nbss.finances.billing_requests import BillingRequests
from api.nbss.finances.payments_requests import PaymentsRequests
from api.nbss.personal_account_requests import PersonalAccountRequests
from common.enums.adjustment import (
    AdjustmentCorrectionObjectType,
    AdjustmentCorrectionType,
    AdjustmentOption,
    AdjustmentUIType,
)
from common.enums.billing import BillingDetail
from common.helpers.data_generator import get_datetime_from_full_time_string, get_shifted_datetime_string
from models.context import test_context
from models.inquiry import prepare_inquiries
from pages.nbss.finances.adjustments_page import AdjustmentsPage
from pages.nbss.finances.billing_accounts_page import BillingAccountsPage
from pages.nbss.finances.payments_page import PaymentsPage
from pages.nbss.personal_account_page import PersonalAccountPage


@pytest.mark.regress
@pytest.mark.nbss_portal
@allure.suite("E2E_86 Проведение внеочередного биллинга")
class TestBillingObjectsSelection:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login, create_organization_with_agreement_and_account) -> None:
        self.payment_api = PaymentsRequests()
        self.billing_api = BillingRequests()
        self.client_inquiries_api = ClientInquiriesRequests()
        self.personal_account_api = PersonalAccountRequests()
        self.adjustment_api = AdjustmentRequests()

        self.personal_account_page = PersonalAccountPage()
        self.billing_page = BillingAccountsPage()
        self.payment_page = PaymentsPage()
        self.adjustment_page = AdjustmentsPage()

        self.random_amount = random.randint(50, 500)

    @allure.title("01. Проверка учета платежей в пределах текущего биллингового периода")
    @allure.id(946234)
    def test_billing_payment_selection(self):
        client = test_context.client
        with allure.step("Продажа продукта и проведение платежа"):
            self.client_inquiries_api.product_sale(inquiry=prepare_inquiries(category="mobile"))
            self.payment_api.create_default_payment(
                client.agreement.account.id, test_context.client.inquiry.product.total_amount
            )
            self.personal_account_api.wait_check_current_main_balance(client.agreement.account.id, 0)

        with allure.step("Перейти в контекст ЛС. Перейти на форму биллинговых счетов"):
            self.personal_account_page.open_personal_account_page(client.agreement.account.id)
            self.payment_page.open_payments_page_via_burger_menu()
            self.payment_page.create_payment_and_wait_completion(amount=self.random_amount)
            self.personal_account_api.wait_check_current_main_balance(client.agreement.account.id, self.random_amount)

            self.billing_page.open_billing_page_via_burger()
            self.billing_page.run_unscheduled_billing_and_wait_completion()
            self.billing_page.open_billing()
            self.billing_page.check_billing_properties_value(
                payments_recorded=self.random_amount, output_balance=-self.random_amount
            )

    @allure.title("02. Проверка учета корректировок с датой проведения до конца текущих суток")
    @allure.id(946235)
    def test_billing_adjustment_selection(self):
        adjustment_date = get_shifted_datetime_string("+1m", False)
        client = test_context.client
        with allure.step("Продажа продукта и проведение платежа"):
            self.client_inquiries_api.product_sale(inquiry=prepare_inquiries(category="internet"))
            self.payment_api.create_default_payment(
                client.agreement.account.id, test_context.client.inquiry.product.total_amount
            )
            self.personal_account_api.wait_check_current_main_balance(client.agreement.account.id, 0)
            billing = self.billing_api.execute_unscheduled_billing_and_wait_completion(client.agreement.account.id)
            adjustment_end_date = get_datetime_from_full_time_string(
                billing.billing_run.period.get_end_date_time()
            ).strftime("%d.%m.%Y %H:%M:%S")

        with allure.step("Перейти в контекст ЛС. Перейти на форму биллинговых счетов"):
            self.personal_account_page.open_personal_account_page(client.agreement.account.id)
            self.adjustment_page.open_adjustments_page_via_burger_menu()
            self.adjustment_page.open_add_adjustment_form()
            self.adjustment_page.fill_add_adjustment_form(
                adjustment_option=AdjustmentOption.charge,
                adjustment_type=AdjustmentUIType.negative,
                correction_type=AdjustmentCorrectionType.object,
                correction_object=AdjustmentCorrectionObjectType.bill,
                detail_name=BillingDetail.fee_for_providing_access_to_network,
                bill_number=billing.bill_number,
                end_date_period=adjustment_end_date,
                date_time=adjustment_date,
                sum_with_tax=str(self.random_amount),
            )
            self.personal_account_api.wait_check_current_main_balance(client.agreement.account.id, self.random_amount)

            self.billing_page.open_billing_page_via_burger()
            self.billing_page.run_unscheduled_billing_and_wait_completion()
            self.billing_page.open_billing()
            self.billing_page.check_billing_properties_value(
                payments_recorded=self.random_amount, output_balance=-self.random_amount
            )

    @allure.title("04. Проверка неучета ранее учтенного платежа во внеочередном биллинге")
    @allure.id(946237)
    def test_billing_payment_unselection_due_to_previous_selection(self):
        client = test_context.client
        with allure.step("Проведение платежа и биллинга"):
            self.client_inquiries_api.product_sale(inquiry=prepare_inquiries(category="mobile"))
            payment_amount = test_context.client.inquiry.product.total_amount
            self.payment_api.create_default_payment(client.agreement.account.id, payment_amount)
            self.personal_account_api.wait_check_current_main_balance(client.agreement.account.id, 0)
            self.billing_api.execute_unscheduled_billing_and_wait_completion(client.agreement.account.id)

        with allure.step("Перейти в контекст ЛС. Перейти на форму биллинговых счетов"):
            self.personal_account_page.open_personal_account_page(client.agreement.account.id)
            self.payment_page.open_payments_page_via_burger_menu()
            self.payment_page.create_payment_and_wait_completion(amount=self.random_amount)
            self.personal_account_api.wait_check_current_main_balance(client.agreement.account.id, self.random_amount)

            self.billing_page.open_billing_page_via_burger()
            self.billing_page.run_unscheduled_billing_and_wait_completion()
            self.billing_page.open_billing(index=1)
            self.billing_page.check_billing_properties_value(payments_recorded=0, output_balance=0)

    @allure.title("05. Проверка неучета корректировок с датой проведения в следующих сутках")
    @allure.id(946240)
    def test_billing_adjustment_unselection_due_to_previous_selection(self):
        adjustment_date = get_shifted_datetime_string("+1d", False)
        client = test_context.client
        with allure.step("Продажа продукта и проведение платежа"):
            self.client_inquiries_api.product_sale(inquiry=prepare_inquiries(category="internet"))
            self.payment_api.create_default_payment(
                client.agreement.account.id, test_context.client.inquiry.product.total_amount
            )
            self.personal_account_api.wait_check_current_main_balance(client.agreement.account.id, 0)
            billing = self.billing_api.execute_unscheduled_billing_and_wait_completion(client.agreement.account.id)
            adjustment_end_date = get_datetime_from_full_time_string(
                billing.billing_run.period.get_end_date_time()
            ).strftime("%d.%m.%Y %H:%M:%S")

        with allure.step("Перейти в контекст ЛС. Перейти на форму биллинговых счетов"):
            self.personal_account_page.open_personal_account_page(client.agreement.account.id)
            self.adjustment_page.open_adjustments_page_via_burger_menu()
            self.adjustment_page.open_add_adjustment_form()
            self.adjustment_page.fill_add_adjustment_form(
                adjustment_option=AdjustmentOption.charge,
                adjustment_type=AdjustmentUIType.negative,
                correction_type=AdjustmentCorrectionType.object,
                correction_object=AdjustmentCorrectionObjectType.bill,
                detail_name=BillingDetail.fee_for_providing_access_to_network,
                bill_number=billing.bill_number,
                end_date_period=adjustment_end_date,
                date_time=adjustment_date,
                sum_with_tax=str(self.random_amount),
            )

            self.billing_page.open_billing_page_via_burger()
            self.billing_page.run_unscheduled_billing_and_wait_completion()
            self.billing_page.open_billing()
            self.billing_page.check_billing_properties_value(payments_recorded=0, output_balance=0)
