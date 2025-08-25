import re

import allure
import pytest
from playwright.sync_api import APIRequestContext, Page

from api.requests.billing_requests import BillingRequests
from api.requests.client_requests import ClientRequests
from api.requests.payments_requests import PaymentsRequests
from api.requests.personal_account_requests import PersonalAccountRequests
from common.helpers.data_generator import (
    get_current_datetime_string,
    get_datetime_from_full_time_string,
)
from models.user import IndividualClient, OrganizationClient
from pages.adjustments_page import AdjustmentsPage
from pages.client_profile_page import ClientProfilePage
from pages.locators.dynamic_form_elements import IndividualCustomerCreate, PromisedPaymentForm
from pages.locators.home_page_elements import HomePage
from pages.locators.promised_payment import PromisedPaymentPage
from pages.payments_page import PaymentsPage


@allure.epic("E2E_72 Управление налоговыми схемами")
@allure.suite("E2E_72 Управление налоговыми схемами")
@allure.link(
    url="confluence.nexign.com/pages/viewpage.action?pageId=322874371",
    name="Поддержка схем налогообложения",
)
@pytest.mark.regress
class TestTaxSchemeManagement:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_ui_stand_login: Page, api_request_auth_context: APIRequestContext) -> None:
        self.home_page = HomePage(nexign_ui_stand_login)
        self.customer_create_form = IndividualCustomerCreate(nexign_ui_stand_login)
        self.client_profile_page = ClientProfilePage(nexign_ui_stand_login)
        self.payments_request = PaymentsRequests(api_request_auth_context)
        self.client_requests = ClientRequests(api_request_auth_context)
        self.personal_account_requests = PersonalAccountRequests(api_request_auth_context)
        self.adjustments_page = AdjustmentsPage(nexign_ui_stand_login)
        self.billing_requests = BillingRequests(api_request_auth_context)
        self.promised_payment = PromisedPaymentPage(nexign_ui_stand_login)
        self.promised_payment_form = PromisedPaymentForm(nexign_ui_stand_login)
        self.payments_form = PaymentsPage(nexign_ui_stand_login)

        self.today_date = get_current_datetime_string(is_full_format=False)
        self.today_datetime = get_current_datetime_string(is_full_format=True)

    @allure.title("01. Установка схемы налогообложения")
    @allure.id(594755)
    def test_set_tax_scheme(self, base_url: str, individual_user_data: IndividualClient) -> None:
        user = individual_user_data

        self.home_page.CREATE_CUSTOMER_BTN.click()
        self.customer_create_form.LAST_NAME.wait_to_be_visible()
        self.customer_create_form.fill_data_for_individual_client(user)
        self.customer_create_form.SAVE_BTN.click()
        self.customer_create_form.INFO_MESSAGE.wait_to_have_text("Клиент создан", timeout=10000)

    @allure.title("02. Просмотр установленной схемы налогообложения")
    @allure.id(594757)
    def test_view_tax_scheme(self, individual_user_data: IndividualClient) -> None:
        user = individual_user_data

        self.home_page.CREATE_CUSTOMER_BTN.click()
        self.customer_create_form.LAST_NAME.wait_to_be_visible()
        self.customer_create_form.fill_data_for_individual_client(user)
        self.customer_create_form.SAVE_BTN.click()
        self.client_profile_page.locators.CLIENT_TAB.click()
        self.client_profile_page.locators.TAX_SCHEME.wait_to_have_text(user.tax_scheme)

    @allure.title("03. Применение схемы налогообложения (Корректировка платежа)")
    @allure.id(594929)
    def test_apply_tax_scheme_payment_adjustment(
        self, base_url: str, create_user_with_agreement_and_account: IndividualClient
    ) -> None:
        client_b2c = create_user_with_agreement_and_account
        documentNumber = self.payments_request.create_default_payment(client_b2c.agreements[0].accounts[0].id, 3000.0)

        self.client_profile_page.open(f"{base_url}customer-hierarchy-management/customers/{client_b2c.user_id}/overview")
        self.client_profile_page.locators.WIDGET_PERSONAL_ACCOUNT_IDS.click(0)
        self.client_profile_page.locators.BURGER_MENU.select_by_value("Финансы > Корректировки")

        self.adjustments_page.open_add_payment_form()
        self.adjustments_page.fill_add_adjustment_form(
            adjustment_option="payment",
            adjustment_type="positive",
            date_time=self.today_datetime,
            sum_with_tax="1000",
            comment="Автотест схема налогообложения",
        )

        self.adjustments_page.check_adjustment(
            idx=0,
            included_in_bill="",
            date=self.today_datetime,
            adjustment_type="Положительная корректировка платежа",
            sum_with_tax=1000.00,
            tax=166.67,
            status="Создание",
            reason="Положительная корректировка платежа",
            target=f"Платёж: {documentNumber} от {self.today_date}",
            advance="1000.00",
        )

    @allure.title("04. Применение схемы налогообложения (Корректировка начисления (Объект))")
    @allure.id(595669)
    def test_apply_tax_scheme_charge_adjustment_object(
        self, base_url: str, create_individual_user: IndividualClient
    ) -> None:
        client_b2c = create_individual_user
        client, product = self.client_requests.product_sale(
            user_id=client_b2c.user_id, category="internet", product_offering_id=500001
        )
        self.payments_request.create_default_payment(client.agreements[0].accounts[0].id, 3000.0)

        self.client_profile_page.open(f"{base_url}customer-hierarchy-management/customers/{client_b2c.user_id}/overview")

        self.client_profile_page.locators.CLIENT_FIO.wait_to_be_visible()
        self.client_profile_page.check_balance(0, 2350.00, "RUB")
        self.client_profile_page.locators.WIDGET_PERSONAL_ACCOUNT_IDS.click(0)
        self.client_profile_page.locators.BURGER_MENU.select_by_value("Финансы > Корректировки")

        billing_profile_id = self.billing_requests.get_billing_profile_id(client.agreements[0].accounts[0].id)
        self.billing_requests.run_unscheduled_billing(billing_profile_id)
        self.billing_requests.wait_billing(billing_profile_id)
        self.billing_requests.wait_finish_billing(billing_profile_id, 3)
        bill_data = self.billing_requests.get_list_of_bills([billing_profile_id])[0]
        bill_number = bill_data["billNumber"]
        end_date_period = get_datetime_from_full_time_string(
            bill_data["billingRun"]["period"]["endDateTime"][:19]
        ).strftime("%d.%m.%Y %H:%M:%S")

        self.adjustments_page.open_add_adjustment_form()
        self.adjustments_page.fill_add_adjustment_form(
            adjustment_option="charge",
            correction_type="object",
            correction_object="bill",
            bill_number=bill_number,
            end_date_period=end_date_period,
            adjustment_type="negative",
            date_time=self.today_datetime,
            sum_with_tax="300",
            comment="Автотест схема налогообложения",
        )

        self.adjustments_page.check_adjustment(
            idx=0,
            included_in_bill="",
            date=self.today_datetime,
            adjustment_type="Отрицательная корректировка счета",
            sum_with_tax=300.00,
            tax=50.00,
            status="Создание",
            reason="Отрицательная корректировка счета",
            target=f"Счёт: №{bill_number} от {end_date_period}",
            advance="300.00",
        )

    @allure.title("05. Применение схемы налогообложения (Корректировка начисления (цель))")
    @allure.id(595675)
    def test_apply_tax_scheme_charge_adjustment_target(
        self, base_url: str, create_individual_user: IndividualClient
    ) -> None:
        client_b2c = create_individual_user
        client, product = self.client_requests.product_sale(
            user_id=client_b2c.user_id, category="internet", product_offering_id=500001
        )
        self.payments_request.create_default_payment(client.agreements[0].accounts[0].id, 3000.0)
        self.personal_account_requests.wait_check_current_main_balance(client.agreements[0].accounts[0].id, 2350.00)

        self.client_profile_page.open(f"{base_url}customer-hierarchy-management/customers/{client_b2c.user_id}/overview")
        self.client_profile_page.locators.CLIENT_FIO.wait_to_be_visible()
        self.client_profile_page.check_balance(0, 2350.00, "RUB")
        self.client_profile_page.locators.WIDGET_PERSONAL_ACCOUNT_IDS.click(0)
        self.client_profile_page.locators.BURGER_MENU.select_by_value("Финансы > Корректировки")

        billing_profile_id = self.billing_requests.get_billing_profile_id(client.agreements[0].accounts[0].id)
        self.billing_requests.run_unscheduled_billing(billing_profile_id)
        self.billing_requests.wait_billing(billing_profile_id)
        self.billing_requests.wait_finish_billing(billing_profile_id, 3)

        self.adjustments_page.open_add_adjustment_form()
        self.adjustments_page.fill_add_adjustment_form(
            adjustment_option="charge",
            correction_type="target",
            detail_name="Абон. плата за VLAN",
            adjustment_type="positive",
            date_time=self.today_datetime,
            sum_with_tax="300",
            comment="Автотест схема налогообложения",
        )

        self.adjustments_page.check_adjustment(
            idx=0,
            included_in_bill="",
            date=self.today_datetime,
            adjustment_type="Положительная корректировка детали счета в текущем периоде",
            sum_with_tax=-300.00,
            tax=-50.00,
            status="Создание",
            reason="Положительная корректировка детали счета в текущем периоде",
            target="Деталь: Абон. плата за VLAN",
            advance="0.00",
        )

        self.client_profile_page.locators.BURGER_MENU.select_by_value("Клиент > Обзор")
        self.client_profile_page.check_balance(0, 2050.00, "RUB")

    @allure.title("06. Применение схемы налогообложения (Корректировка начисления (счет-фактура))")
    @allure.id(595679)
    def test_apply_tax_scheme_charge_adjustment_invoice(
        self, base_url: str, create_individual_user: IndividualClient
    ) -> None:
        client_b2c = create_individual_user
        client, product = self.client_requests.product_sale(
            user_id=client_b2c.user_id, category="internet", product_offering_id=500001
        )
        self.payments_request.create_default_payment(client.agreements[0].accounts[0].id, 3000.0)

        self.client_profile_page.open(f"{base_url}customer-hierarchy-management/customers/{client_b2c.user_id}/overview")
        self.client_profile_page.locators.CLIENT_FIO.wait_to_be_visible()
        self.client_profile_page.check_balance(0, 2350.00, "RUB")
        self.client_profile_page.locators.WIDGET_PERSONAL_ACCOUNT_IDS.click(0)
        self.client_profile_page.locators.BURGER_MENU.select_by_value("Финансы > Корректировки")

        billing_profile_id = self.billing_requests.get_billing_profile_id(client.agreements[0].accounts[0].id)
        self.billing_requests.run_unscheduled_billing(billing_profile_id)
        self.billing_requests.wait_billing(billing_profile_id)
        self.billing_requests.wait_finish_billing(billing_profile_id, 3)
        bill_data = self.billing_requests.get_list_of_bills([billing_profile_id])[0]
        bill_number = bill_data["billNumber"]
        target = bill_data["billingRun"]["billingProfileBillingRunId"]
        end_date_period = get_datetime_from_full_time_string(
            bill_data["billingRun"]["period"]["endDateTime"][:19]
        ).strftime("%d.%m.%Y %H:%M:%S")

        self.adjustments_page.open_add_adjustment_form()
        self.adjustments_page.fill_add_adjustment_form(
            adjustment_option="charge",
            correction_type="object",
            correction_object="invoice",
            bill_number=bill_number,
            end_date_period=end_date_period,
            adjustment_type="negative",
            date_time=self.today_datetime,
            sum_with_tax="300",
            comment="Автотест схема налогообложения",
        )

        self.adjustments_page.check_adjustment(
            idx=0,
            included_in_bill="",
            date=self.today_datetime,
            adjustment_type="Отрицательная коррекировка счёт-фактуры",
            sum_with_tax=300.00,
            tax=50.00,
            status="Создание",
            reason="Отрицательная коррекировка счёт-фактуры",
            target=re.compile(f"Счёт-фактура: №{target}.*"),
            advance="300.00",
        )

    @allure.title("07. Применение схемы налогообложения (Обещанный платеж)")
    @allure.id(595732)
    def test_apply_tax_scheme_charge_adjustment_promised_payment(
        self, base_url: str, create_individual_user: IndividualClient
    ) -> None:
        client_b2c = create_individual_user
        client, product = self.client_requests.product_sale(
            user_id=client_b2c.user_id, category="internet", product_offering_id=500001
        )

        self.client_profile_page.open(
            f"{base_url}customer-hierarchy-management/accounts/{client.agreements[0].accounts[0].id}/account"
        )
        self.client_profile_page.locators.BURGER_MENU.select_by_value("Финансы > Обещанные платежи")

        self.promised_payment.CONNECT_BTN.wait_to_be_visible()
        self.promised_payment.CONNECT_BTN.click()
        self.promised_payment_form.PRODUCT_OFFER_FLD.select_by_value(value="ОП на 100 на 1 день с комиссией 0")
        self.promised_payment_form.ABONENT_FLD.fill(str(product.subs_id))
        self.promised_payment_form.INNER_ACCEPT_BTN.click()
        self.client_profile_page.locators.INFO_MESSAGE.wait_to_be_visible()
        self.client_profile_page.locators.INFO_MESSAGE_CLOSE_BTN.click()

        self.promised_payment.PRODUCT_PROMISED_PAYMENT_FLD.wait_to_be_visible()

        billing_profile_id = self.billing_requests.get_billing_profile_id(client_b2c.agreements[0].accounts[0].id)
        self.billing_requests.run_unscheduled_billing(billing_profile_id)
        self.billing_requests.wait_billing(billing_profile_id)
        self.billing_requests.wait_finish_billing(billing_profile_id, 3)
        bill_data = self.billing_requests.get_list_of_bills([billing_profile_id])[0]
        bill_number = bill_data["billNumber"]
        end_date_period = get_datetime_from_full_time_string(
            bill_data["billingRun"]["period"]["endDateTime"][:19]
        ).strftime("%d.%m.%Y %H:%M:%S")

        self.adjustments_page.open_add_adjustment_form()
        self.adjustments_page.fill_add_adjustment_form(
            adjustment_option="charge",
            correction_type="object",
            bill_number=bill_number,
            end_date_period=end_date_period,
            adjustment_type="negative",
            date_time=self.today_datetime,
            sum_with_tax="300",
            comment="Автотест схема налогообложения",
        )

        self.adjustments_page.check_adjustment(
            idx=0,
            included_in_bill="",
            date=self.today_datetime,
            adjustment_type="Отрицательная корректировка счета",
            sum_with_tax=300.00,
            tax=50.00,
            status="Создание",
            reason="Отрицательная корректировка счета",
            target=f"Платёж: {self.documentNumber} от {self.today_date}",
            advance="300.00",
        )

    @allure.title("08. Применение схемы налогообложения (перенос монетарного баланса между клиентами)")
    @allure.id(595748)
    def test_apply_tax_scheme_balance_transfer(
        self,
        base_url: str,
        create_user_with_agreement_and_account: IndividualClient,
        create_organization_with_agreement_and_account: OrganizationClient,
        api_request_auth_context,
    ) -> None:
        client_sender = create_user_with_agreement_and_account
        client_receiver = create_organization_with_agreement_and_account
        self.payments_request.create_default_payment(client_sender.agreements[0].accounts[0].id, 3000.0)

        self.client_profile_page.open(
            f"{base_url}customer-hierarchy-management/customers/{client_sender.user_id}/overview"
        )

        self.client_profile_page.locators.CLIENT_FIO.wait_to_be_visible()
        self.client_profile_page.check_balance(0, 3000.00, "RUB")
        self.client_profile_page.locators.WIDGET_PERSONAL_ACCOUNT_IDS.click(0)
        self.client_profile_page.locators.BURGER_MENU.select_by_value("Финансы > Платежи")

        self.payments_form.locators.BALANCE_TRANSFER_BTN.click()

        self.payments_form.locators.PERSONAL_ACCOUNT_SELECTOR.click()
        self.payments_form.locators.PERSONAL_ACCOUNT_TO_SEARCH.fill(client_receiver.agreements[0].accounts[0].number)
        self.payments_form.locators.PERSONAL_ACCOUNT_SEARCH_BTN.click()
        self.payments_form.locators.PERSONAL_ACCOUNT_DATA[0].wait_to_be_visible()
        self.payments_form.locators.PERSONAL_ACCOUNT_DATA[1].to_contain_text(
            client_receiver.agreements[0].accounts[0].number
        )
        self.payments_form.locators.PERSONAL_ACCOUNT_CHOOSE_BTN.click()
        self.payments_form.locators.DONOR_ADJUSTMENT_REASON.select_by_value("Перенос средств по заявлению клиента")
        self.payments_form.locators.RECIPIENT_ADJUSTMENT_REASON.select_by_value("Перенос средств по заявлению клиента.")
        self.payments_form.locators.BALANCE_TO_TRANSFER.fill("500")
        self.payments_form.locators.TRANSFER_ACCEPT.click()

        self.payments_form.locators.INFO_MESSAGE.wait_to_have_text("Перенос баланса выполнен")

        self.client_profile_page.locators.BURGER_MENU.select_by_value("Финансы > Корректировки")
        self.adjustments_page.check_adjustment(
            idx=0,
            included_in_bill="",
            adjustment_type="Отрицательная корректировка лицевого счета",
            sum_with_tax=-500.00,
            tax=-83.33,
            status="Одобрено",
            reason="Перенос средств по заявлению клиента",
            advance="0.00",
        )

        self.client_profile_page.open(
            f"{base_url}customer-hierarchy-management/customers/{client_receiver.user_id}/overview"
        )
        self.client_profile_page.locators.WIDGET_PERSONAL_ACCOUNT_IDS.click(0)
        self.client_profile_page.locators.BURGER_MENU.select_by_value("Финансы > Корректировки")
        self.adjustments_page.check_adjustment(
            idx=0,
            included_in_bill="",
            adjustment_type="Положительная корректировка счета",
            sum_with_tax=500.00,
            tax=83.33,
            status="Одобрено",
            reason="Перенос средств по заявлению клиента.",
            advance="500.00",
        )
