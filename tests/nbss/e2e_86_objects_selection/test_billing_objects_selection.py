import random

import allure
import pytest

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from api.nbss.finances.billing_requests import BillingRequests
from api.nbss.finances.payments_requests import PaymentsRequests
from api.nbss.personal_account_requests import PersonalAccountRequests
from models.context import test_context
from models.inquiry import prepare_inquiries
from pages.nbss.finances.billing_accounts_page import BillingAccountsPage
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

        self.personal_account_page = PersonalAccountPage()
        self.billing_page = BillingAccountsPage()

    @allure.title("01. Проверка учета платежей в пределах текущего биллингового периода")
    @allure.id(946234)
    def test_billing_payment_selection(self):
        random_amount = random.randint(50, 500)
        client = test_context.client
        print(client.user_id)
        with allure.step("Проведение платежа и биллинга"):
            self.client_inquiries_api.product_sale(inquiry=prepare_inquiries(category="mobile"))
            payment_amount = test_context.client.inquiry.product.total_amount + random_amount
            self.billing_api.execute_unscheduled_billing_and_wait_completion()
            self.payment_api.create_default_payment(client.agreement.account.id, payment_amount)
            self.personal_account_api.wait_check_current_main_balance(client.agreement.account.id, random_amount)
            self.billing_api.execute_unscheduled_billing_and_wait_completion()

        with allure.step("Перейти в контекст ЛС. Перейти на форму биллинговых счетов"):
            self.personal_account_page.open_personal_account_page(client.agreement.account.id)
            self.billing_page.open_billing_page_via_burger()
            self.billing_page.open_billing()
            self.billing_page.check_billing_properties_value(payments_recorded=payment_amount)
