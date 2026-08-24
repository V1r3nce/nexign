import random

import allure
import pytest

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from api.nbss.finances.adjustment_requests import AdjustmentRequests
from api.nbss.finances.billing_requests import BillingRequests
from api.nbss.finances.payments_requests import PaymentsRequests
from api.nbss.personal_account_requests import PersonalAccountRequests
from common.enums.adjustment import AdjustmentReason, AdjustmentType
from common.helpers.checker import assert_that
from models.context import test_context
from models.inquiry import prepare_inquiries


@pytest.mark.regress
@pytest.mark.nbss_portal
@allure.suite("E2E_86 Проведение внеочередного биллинга")
class TestBEBillingObjectsSelection:
    @pytest.fixture(autouse=True)
    def setup(self, sso_stand_login, create_organization_with_agreement_and_account) -> None:
        self.payment_api = PaymentsRequests()
        self.billing_api = BillingRequests()
        self.client_inquiries_api = ClientInquiriesRequests()
        self.personal_account_api = PersonalAccountRequests()
        self.adjustment_api = AdjustmentRequests()

        self.random_amount = random.randint(50, 500)

    @allure.title("01. Проверка учета платежей в пределах текущего биллингового периода")
    @allure.id(946234)
    def test_be_billing_payment_selection(self):
        client = test_context.client
        with allure.step("Продажа продукта и проведение платежа"):
            self.client_inquiries_api.product_sale(inquiry=prepare_inquiries(category="mobile"))
            self.payment_api.create_default_payment(
                client.agreement.account.id, test_context.client.inquiry.product.total_amount
            )
            self.personal_account_api.wait_check_current_main_balance(client.agreement.account.id, 0)

        with allure.step("Проведение платежа"):
            self.payment_api.create_default_payment(client.agreement.account.id, self.random_amount)
            self.personal_account_api.wait_check_current_main_balance(client.agreement.account.id, self.random_amount)

        with allure.step("Проведение биллинга и проверка"):
            billing = self.billing_api.execute_unscheduled_billing_and_wait_completion()
            payments_recorded = billing.result_sum_info.payments_amount_with_tax
            assert_that(
                lambda: payments_recorded == self.random_amount,
                lambda: f"Значение учтенных платежей ожидалось: {self.random_amount}\nПолучено: {payments_recorded}",
            )

    @allure.title("02. Проверка учета корректировок с датой проведения до конца текущих суток")
    @allure.id(946235)
    def test_be_billing_adjustment_selection(self):
        client = test_context.client
        with allure.step("Проведение платежа и биллинга"):
            self.client_inquiries_api.product_sale(inquiry=prepare_inquiries(category="internet"))
            payment_amount = test_context.client.inquiry.product.total_amount + self.random_amount
            self.payment_api.create_default_payment(client.agreement.account.id, payment_amount)
            self.personal_account_api.wait_check_current_main_balance(client.agreement.account.id, self.random_amount)
            billing_1 = self.billing_api.execute_unscheduled_billing_and_wait_completion(client.agreement.account.id)
            self.adjustment_api.create_adjustment(
                adjustment_type=AdjustmentType.negative_bill_detail_included,
                adjustment_reason=AdjustmentReason.negative_detail,
                amount=2000,
                bill_detail_id=100088,
                account_financial_profile_id=test_context.client.agreement.account.id,
            )
            billing_2 = self.billing_api.execute_unscheduled_billing_and_wait_completion(client.agreement.account.id)

        with allure.step("Проверить"):
            print(billing_1)
            print(billing_2)

    @allure.title("04. Проверка неучета ранее учтенного платежа во внеочередном биллинге")
    @allure.id(946237)
    def test_be_billing_payment_unselection_due_to_previous_selection(self):
        client = test_context.client
        with allure.step("Проведение платежа и биллинга"):
            self.client_inquiries_api.product_sale(inquiry=prepare_inquiries(category="mobile"))
            payment_amount = test_context.client.inquiry.product.total_amount + self.random_amount
            billing_1 = self.billing_api.execute_unscheduled_billing_and_wait_completion(client.agreement.account.id)
            self.payment_api.create_default_payment(client.agreement.account.id, payment_amount)
            self.personal_account_api.wait_check_current_main_balance(client.agreement.account.id, self.random_amount)
            billing_2 = self.billing_api.execute_unscheduled_billing_and_wait_completion(client.agreement.account.id)

        with allure.step("Проверить"):
            print(billing_1)
            print(billing_2)

    @allure.title("05. Проверка неучета корректировок с датой проведения в следующих сутках")
    @allure.id(946240)
    def test_be_billing_adjustment_unselection_due_to_previous_selection(self):
        client = test_context.client
        with allure.step("Проведение платежа и биллинга"):
            self.client_inquiries_api.product_sale(inquiry=prepare_inquiries(category="internet"))
            payment_amount = test_context.client.inquiry.product.total_amount + self.random_amount
            self.payment_api.create_default_payment(client.agreement.account.id, payment_amount)
            self.personal_account_api.wait_check_current_main_balance(client.agreement.account.id, self.random_amount)
            billing_1 = self.billing_api.execute_unscheduled_billing_and_wait_completion(client.agreement.account.id)
            self.adjustment_api.create_adjustment(
                adjustment_type=AdjustmentType.negative_bill_detail_included,
                adjustment_reason=AdjustmentReason.negative_detail,
                amount=2000,
                bill_detail_id=100088,
                account_financial_profile_id=test_context.client.agreement.account.id,
            )
            billing_2 = self.billing_api.execute_unscheduled_billing_and_wait_completion(client.agreement.account.id)

        with allure.step("Проверить"):
            print(billing_1)
            print(billing_2)
