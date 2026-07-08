import allure
import pytest

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from api.nbss.finances.adjustment_requests import AdjustmentRequests
from api.nbss.finances.billing_requests import BillingRequests
from api.nbss.finances.payments_requests import PaymentsRequests
from api.nbss.personal_account_requests import PersonalAccountRequests
from common.helpers.data_generator import generate_english_string
from common.helpers.env_helper import BASE_URL
from models.context import test_context
from models.inquiry import prepare_inquiries
from pages.locators.nbss.finances.payments_elements import PaymentElements
from pages.nbss.finances.billing_accounts_page import BillingAccountsPage


@allure.suite("E2E_86 Проведение внеочередного биллинга")
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestBillingDocumentsFormation:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login):
        self.client_inquiry_api = ClientInquiriesRequests()
        self.billing_api = BillingRequests()
        self.billing_account = BillingAccountsPage()
        self.personal_account_api = PersonalAccountRequests()
        self.payment_api = PaymentsRequests()
        self.adjustment_api = AdjustmentRequests()
        self.payments_elements = PaymentElements()

        self.document_name = generate_english_string(8)
        self.document_type_bill = "Биллинговый счет"
        self.document_type_invoice = "Счёт-фактура"
        self.document_type_payment_request = "Платежное требование"
        self.account_balance = 100
        self.adjustment_sum = 100

    @allure.title("Выгрузка Счет-фактуры внеочередного биллинга, начисления не оплачены")
    @allure.id(842520)
    def test_creating_invoice_document_unpaid_accruals(self, create_organization_with_postpaid_account):
        with allure.step("Проводим продажу, ожидаем начисления, проводим биллинг"):
            self.client_inquiry_api.product_sale(inquiry=prepare_inquiries(category="satellite_rent"))
            self.personal_account_api.wait_accruals(test_context.client.user_id)
            self.billing_api.execute_unscheduled_billing_and_wait_completion()
        with allure.step("Переходим в контекст ЛС"):
            self.billing_account.open(
                f"{BASE_URL}customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
            )
            self.payments_elements.USER_BALANCE.wait_to_be_visible(timeout=15000)
        with allure.step("Переходим в биллинговые счета и открываем нужный"):
            self.billing_account.locators.BURGER_MENU.select_by_value("Финансы > Биллинговые счета")
            self.billing_account.open_billing()
            self.billing_account.locators.BILL_AMOUNT_DUE[0].to_contain_text(
                test_context.client.inquiry.product.total_amount, separated=True
            )
        with allure.step("Переходим в таб с документами, заказываем документ и его проверяем"):
            self.billing_account.open_documents_tab()
            self.billing_account.order_document(
                document_type=self.document_type_invoice, document_name=self.document_name
            )
            self.billing_api.wait_document_done(document_name=self.document_name)
            self.billing_account.check_document(
                document_type=self.document_type_invoice, document_name=self.document_name
            )

    @allure.title("Выгрузка Счет-фактуры внеочередного биллинга")
    @allure.id(576297)
    def test_creating_invoice_document(self, create_organization):
        with allure.step("Проводим продажу, создаем платеж, ожидаем начисления, проводим биллинг"):
            self.client_inquiry_api.product_sale(inquiry=prepare_inquiries(category="internet"))
            self.payment_api.create_default_payment(
                test_context.client.agreements[0].accounts[0].id,
                test_context.client.inquiry.product.total_amount + self.account_balance,
            )
            self.personal_account_api.wait_check_current_main_balance(
                test_context.client.agreements[0].accounts[0].id, self.account_balance
            )
            self.personal_account_api.wait_accruals(test_context.client.user_id)
            self.billing_api.execute_unscheduled_billing_and_wait_completion()
        with allure.step("Переходим в контекст ЛС"):
            self.billing_account.open(
                f"{BASE_URL}customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
            )
            self.payments_elements.USER_BALANCE.wait_to_be_visible(timeout=15000)
        with allure.step("Переходим в биллинговые счета и открываем нужный"):
            self.billing_account.locators.BURGER_MENU.select_by_value("Финансы > Биллинговые счета")
            self.billing_account.open_billing()
        with allure.step("Переходим в таб с документами, заказываем документ и его проверяем"):
            self.billing_account.open_documents_tab()
            self.billing_account.order_document(
                document_type=self.document_type_invoice, document_name=self.document_name
            )
            self.billing_api.wait_document_done(document_name=self.document_name)
            self.billing_account.check_document(
                document_type=self.document_type_invoice, document_name=self.document_name
            )

    @allure.title("Выгрузка Биллингового счета внеочередного биллинга, начисления не оплачены")
    @allure.id(576025)
    def test_creating_bill_document_unpaid_accruals(self, create_organization_with_postpaid_account):
        with allure.step("Проводим продажу, ожидаем начисления, проводим биллинг"):
            self.client_inquiry_api.product_sale(inquiry=prepare_inquiries(category="satellite_rent"))
            self.personal_account_api.wait_accruals(test_context.client.user_id)
            self.billing_api.execute_unscheduled_billing_and_wait_completion()
        with allure.step("Переходим в контекст ЛС"):
            self.billing_account.open(
                f"{BASE_URL}customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
            )
            self.payments_elements.USER_BALANCE.wait_to_be_visible(timeout=15000)
        with allure.step("Переходим в биллинговые счета и открываем нужный"):
            self.billing_account.locators.BURGER_MENU.select_by_value("Финансы > Биллинговые счета")
            self.billing_account.open_billing()
            self.billing_account.locators.BILL_AMOUNT_DUE[0].to_contain_text(
                test_context.client.inquiry.product.total_amount, separated=True
            )
        with allure.step("Переходим в таб с документами, заказываем документ и его проверяем"):
            self.billing_account.open_documents_tab()
            self.billing_account.order_document(document_type=self.document_type_bill, document_name=self.document_name)
            self.billing_api.wait_document_done(document_name=self.document_name)
            self.billing_account.check_document(document_type=self.document_type_bill, document_name=self.document_name)

    @allure.title("Выгрузка Биллингового счета внеочередного биллинга")
    @allure.id(575712)
    def test_creating_bill_document(self, create_organization):
        with allure.step("Проводим продажу, создаем платеж, ожидаем начисления, проводим биллинг"):
            self.client_inquiry_api.product_sale(inquiry=prepare_inquiries(category="internet"))
            self.payment_api.create_default_payment(
                test_context.client.agreements[0].accounts[0].id,
                test_context.client.inquiry.product.total_amount + self.account_balance,
            )
            self.personal_account_api.wait_check_current_main_balance(
                test_context.client.agreements[0].accounts[0].id, self.account_balance
            )
            self.personal_account_api.wait_accruals(test_context.client.user_id)
            self.billing_api.execute_unscheduled_billing_and_wait_completion()
        with allure.step("Переходим в контекст ЛС"):
            self.billing_account.open(
                f"{BASE_URL}customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
            )
            self.payments_elements.USER_BALANCE.wait_to_be_visible(timeout=15000)
        with allure.step("Переходим в биллинговые счета и открываем нужный"):
            self.billing_account.locators.BURGER_MENU.select_by_value("Финансы > Биллинговые счета")
            self.billing_account.open_billing()
        with allure.step("Переходим в таб с документами, заказываем документ и его проверяем"):
            self.billing_account.open_documents_tab()
            self.billing_account.order_document(document_type=self.document_type_bill, document_name=self.document_name)
            self.billing_api.wait_document_done(document_name=self.document_name)
            self.billing_account.check_document(document_type=self.document_type_bill, document_name=self.document_name)

    @allure.title("Выгрузка Биллингового счета внеочередного биллинга, с корректировкой платежа")
    @allure.id(576171)
    def test_creating_bill_document_with_adjustment(self, create_organization):
        with allure.step(
            "Проводим продажу, создаем платеж, ожидаем начисления, создаем корректировку, проводим биллинг"
        ):
            self.client_inquiry_api.product_sale(inquiry=prepare_inquiries(category="internet"))
            self.payment_api.create_default_payment(
                test_context.client.agreements[0].accounts[0].id,
                test_context.client.inquiry.product.total_amount + self.account_balance,
            )
            self.personal_account_api.wait_check_current_main_balance(
                test_context.client.agreements[0].accounts[0].id, self.account_balance
            )
            self.personal_account_api.wait_accruals(test_context.client.user_id)
            billing_payment_id = int(
                self.payment_api.get_payments(test_context.client.agreements[0].accounts[0].id).json()["items"][0][
                    "paymentItem"
                ]["paymentItemId"]
            )
            self.adjustment_api.create_adjustment(
                adjustment_type_id=10,
                adjustment_reason_id=13,
                billing_payment_id=billing_payment_id,
                billing_profile_id=self.billing_api.get_billing_profile_id(
                    test_context.client.agreements[0].accounts[0].id
                ),
                amount=self.adjustment_sum,
            )
            self.billing_api.execute_unscheduled_billing_and_wait_completion()
        with allure.step("Переходим в контекст ЛС"):
            self.billing_account.open(
                f"{BASE_URL}customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
            )
            self.payments_elements.USER_BALANCE.wait_to_be_visible(timeout=15000)
        with allure.step("Переходим в биллинговые счета и открываем нужный"):
            self.billing_account.locators.BURGER_MENU.select_by_value("Финансы > Биллинговые счета")
            self.billing_account.open_billing()
        with allure.step("Переходим в таб с документами, заказываем документ и его проверяем"):
            self.billing_account.open_documents_tab()
            self.billing_account.order_document(document_type=self.document_type_bill, document_name=self.document_name)
            self.billing_api.wait_document_done(document_name=self.document_name)
            self.billing_account.check_document(document_type=self.document_type_bill, document_name=self.document_name)

    @allure.title("Выгрузка Платежного требования внеочередного биллинга")
    @allure.id(576307)
    def test_creating_payment_request_document(self, create_organization):
        with allure.step("Проводим продажу, создаем платеж, ожидаем начисления, проводим биллинг"):
            self.client_inquiry_api.product_sale(inquiry=prepare_inquiries(category="internet"))
            self.payment_api.create_default_payment(
                test_context.client.agreements[0].accounts[0].id,
                test_context.client.inquiry.product.total_amount + self.account_balance,
            )
            self.personal_account_api.wait_check_current_main_balance(
                test_context.client.agreements[0].accounts[0].id, self.account_balance
            )
            self.personal_account_api.wait_accruals(test_context.client.user_id)
            self.billing_api.execute_unscheduled_billing_and_wait_completion()
        with allure.step("Переходим в контекст ЛС"):
            self.billing_account.open(
                f"{BASE_URL}customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
            )
            self.payments_elements.USER_BALANCE.wait_to_be_visible(timeout=15000)
        with allure.step("Переходим в биллинговые счета и открываем нужный"):
            self.billing_account.locators.BURGER_MENU.select_by_value("Финансы > Биллинговые счета")
            self.billing_account.open_billing()
        with allure.step("Переходим в таб с документами, заказываем документ и его проверяем"):
            self.billing_account.open_documents_tab()
            self.billing_account.order_document(
                document_type=self.document_type_payment_request, document_name=self.document_name
            )
            self.billing_api.wait_document_done(document_name=self.document_name)
            self.billing_account.check_document(
                document_type=self.document_type_payment_request, document_name=self.document_name
            )

    @allure.title("Выгрузка Платежного требования внеочередного биллинга, начисления не оплачены")
    @allure.id(842752)
    def test_creating_payment_request_document_unpaid_accruals(self, create_organization_with_postpaid_account):
        with allure.step("Проводим продажу, ожидаем начисления, проводим биллинг"):
            self.client_inquiry_api.product_sale(inquiry=prepare_inquiries(category="satellite_rent"))
            self.personal_account_api.wait_accruals(test_context.client.user_id)
            self.billing_api.execute_unscheduled_billing_and_wait_completion()
        with allure.step("Переходим в контекст ЛС"):
            self.billing_account.open(
                f"{BASE_URL}customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
            )
            self.payments_elements.USER_BALANCE.wait_to_be_visible(timeout=15000)
        with allure.step("Переходим в биллинговые счета и открываем нужный"):
            self.billing_account.locators.BURGER_MENU.select_by_value("Финансы > Биллинговые счета")
            self.billing_account.open_billing()
            self.billing_account.locators.BILL_AMOUNT_DUE[0].to_contain_text(
                test_context.client.inquiry.product.total_amount, separated=True
            )
        with allure.step("Переходим в таб с документами, заказываем документ и его проверяем"):
            self.billing_account.open_documents_tab()
            self.billing_account.order_document(
                document_type=self.document_type_payment_request, document_name=self.document_name
            )
            self.billing_api.wait_document_done(document_name=self.document_name)
            self.billing_account.check_document(
                document_type=self.document_type_payment_request, document_name=self.document_name
            )
