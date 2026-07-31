import re

import allure
import pytest

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from api.nbss.finances.billing_requests import BillingRequests
from api.nbss.finances.payments_requests import PaymentsRequests
from api.nbss.personal_account_requests import PersonalAccountRequests
from common.helpers.data_generator import (
    generate_english_string,
    generate_russian_string,
    get_current_datetime_string,
    get_datetime_from_full_time_string,
    get_shifted_datetime,
)
from common.helpers.env_helper import BASE_URL
from common.helpers.string_helper import convert_amount_to_balance_string
from models.client import IndividualClient, OrganizationClient
from models.context import test_context
from models.inquiry import prepare_inquiries
from pages.locators.nbss.dynamic_form_elements import IndividualCustomerCreate, PromisedPaymentForm
from pages.locators.nbss.finances.promised_payment import PromisedPaymentPageElements
from pages.locators.nbss.home_page_elements import HomePageElements
from pages.nbss.billing.tax_and_tax_schemes_settings_page import TaxAndTaxSchemesSettingsPage
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.finances.adjustments_page import AdjustmentsPage
from pages.nbss.finances.payments_page import PaymentsPage


@allure.epic("E2E_72 Управление налоговыми схемами")
@allure.suite("E2E_72 Управление налоговыми схемами")
@allure.link(
    url="confluence.nexign.com/pages/viewpage.action?pageId=322874371",
    name="Поддержка схем налогообложения",
)
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestTaxSchemeManagement:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login, create_organization: OrganizationClient) -> None:
        self.home_page = HomePageElements()
        self.customer_create_form = IndividualCustomerCreate()
        self.client_profile_page = ClientProfilePage()
        self.payments_request = PaymentsRequests()
        self.client_requests = ClientInquiriesRequests()
        self.personal_account_requests = PersonalAccountRequests()
        self.adjustments_page = AdjustmentsPage()
        self.billing_requests = BillingRequests()
        self.promised_payment = PromisedPaymentPageElements()
        self.promised_payment_form = PromisedPaymentForm()
        self.payments_form = PaymentsPage()
        self.tax_scheme_page = TaxAndTaxSchemesSettingsPage()

        self.today_date = get_current_datetime_string(is_full_format=False)
        self.today_datetime = get_current_datetime_string(is_full_format=True)
        self.payment_amount = 3000

    @allure.title("01. Установка схемы налогообложения")
    @allure.id(594755)
    def test_set_tax_scheme(self, individual_user_data: IndividualClient) -> None:
        user = individual_user_data

        self.home_page.CREATE_CUSTOMER_BTN.click()
        self.customer_create_form.LAST_NAME.wait_to_be_visible()
        self.customer_create_form.fill_data_for_individual_client(user)
        self.customer_create_form.CREATE_BTN.click()
        self.customer_create_form.INFO_MESSAGE.wait_to_have_text("Клиент создан", timeout=10000)

    @allure.title("02. Просмотр установленной схемы налогообложения")
    @allure.id(594757)
    def test_view_tax_scheme(self) -> None:
        self.client_profile_page.open_client_profile_page(test_context.client.user_id)
        self.client_profile_page.locators.CLIENT_TAB.wait_to_be_enabled(timeout=15000)
        self.client_profile_page.locators.CLIENT_TAB.click()
        self.client_profile_page.locators.TAX_SCHEME.wait_to_have_text(test_context.client.tax_scheme)

    @allure.title("03. Применение схемы налогообложения (Корректировка платежа)")
    @allure.id(594929)
    def test_apply_tax_scheme_payment_adjustment(
        self, create_organization_with_agreement_and_account: OrganizationClient
    ) -> None:
        document_number = self.payments_request.create_default_payment(
            test_context.client.agreements[0].accounts[0].id, self.payment_amount
        )

        self.client_profile_page.open(
            f"{BASE_URL}customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
        )
        self.client_profile_page.locators.PERSONAL_ACCOUNT_STATUS.wait_to_be_visible()
        self.client_profile_page.locators.BURGER_MENU.select_by_value("Финансы > Корректировки")
        self.adjustments_page.locators.BALANCE.wait_to_have_text(
            convert_amount_to_balance_string(self.payment_amount), timeout=10000
        )
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
            target=re.compile(f"Платёж: {document_number} от {self.today_date} " + r"\d{2}:\d{2}:\d{2}"),
            advance="1000.00",
        )

    @allure.title("04. Применение схемы налогообложения (Корректировка начисления (Объект))")
    @allure.id(595669)
    def test_apply_tax_scheme_charge_adjustment_object(self) -> None:
        self.client_requests.product_sale(inquiry=prepare_inquiries("internet"))
        self.payments_request.create_default_payment(
            test_context.client.agreements[0].accounts[0].id, self.payment_amount
        )

        self.client_profile_page.open_client_overview_page(test_context.client.user_id)

        self.client_profile_page.check_balance(
            0, self.payment_amount - test_context.client.inquiry.product.total_amount, "RUB"
        )
        self.client_profile_page.locators.WIDGET_PERSONAL_ACCOUNT_IDS.click(0)
        self.client_profile_page.locators.BURGER_MENU.select_by_value("Финансы > Корректировки")

        billing_profile_id = self.billing_requests.get_billing_profile_id(
            test_context.client.agreements[0].accounts[0].id
        )
        self.billing_requests.run_unscheduled_billing(billing_profile_id)
        self.billing_requests.wait_billing(billing_profile_id)
        self.billing_requests.wait_finish_billing(billing_profile_id, 3)
        bill_data = self.billing_requests.get_list_of_bills([billing_profile_id])[0]
        bill_number = bill_data["billNumber"]
        bill_id = bill_data["billId"]
        bill_detail_value_id = self.billing_requests.get_bill_detail_value_id(bill_id)
        detail_name = self.billing_requests.get_bill_detail_name(bill_id, bill_detail_value_id)
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
            adjustment_type="Отрицательная корректировка детализации счета",
            sum_with_tax=300.00,
            tax=50.00,
            status="Создание",
            reason="Отрицательная корректировка детали счета",
            target=f"Деталь: {detail_name}. Счёт: №{bill_number}",
            advance="300.00",
        )

    @allure.title("05. Применение схемы налогообложения (Корректировка начисления (цель))")
    @allure.id(595675)
    def test_apply_tax_scheme_charge_adjustment_target(self) -> None:
        self.client_requests.product_sale(inquiry=prepare_inquiries("internet"))
        self.payments_request.create_default_payment(
            test_context.client.agreements[0].accounts[0].id, self.payment_amount
        )
        balance = self.payment_amount - test_context.client.inquiry.product.total_amount
        self.personal_account_requests.wait_check_current_main_balance(
            test_context.client.agreements[0].accounts[0].id, balance
        )

        self.client_profile_page.open_client_overview_page(test_context.client.user_id)
        self.client_profile_page.check_balance(0, balance, "RUB")
        self.client_profile_page.locators.WIDGET_PERSONAL_ACCOUNT_IDS.click(0)
        self.client_profile_page.locators.BURGER_MENU.select_by_value("Финансы > Корректировки")

        billing_profile_id = self.billing_requests.get_billing_profile_id(
            test_context.client.agreements[0].accounts[0].id
        )
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
            target="Добавлена деталь: Абон. плата за VLAN",
            advance="0.00",
        )

        self.client_profile_page.locators.BURGER_MENU.select_by_value("Клиент > Обзор")
        self.client_profile_page.check_balance(0, balance - 300, "RUB")

    @allure.title("06. Применение схемы налогообложения (Корректировка начисления (счет-фактура))")
    @allure.id(595679)
    def test_apply_tax_scheme_charge_adjustment_invoice(self) -> None:
        self.client_requests.product_sale(inquiry=prepare_inquiries("internet"))
        self.payments_request.create_default_payment(
            test_context.client.agreements[0].accounts[0].id, self.payment_amount
        )

        self.client_profile_page.open_client_overview_page(test_context.client.user_id)
        self.client_profile_page.check_balance(
            0, self.payment_amount - test_context.client.inquiry.product.total_amount, "RUB"
        )
        self.client_profile_page.locators.WIDGET_PERSONAL_ACCOUNT_IDS.click(0)
        self.client_profile_page.locators.BURGER_MENU.select_by_value("Финансы > Корректировки")

        billing_profile_id = self.billing_requests.get_billing_profile_id(
            test_context.client.agreements[0].accounts[0].id
        )
        self.billing_requests.run_unscheduled_billing(billing_profile_id)
        self.billing_requests.wait_billing(billing_profile_id)
        self.billing_requests.wait_finish_billing(billing_profile_id, 3)
        bill_data = self.billing_requests.get_list_of_bills([billing_profile_id])[0]
        bill_number = bill_data["billNumber"]
        target = bill_data["billingRun"]["billingProfileBillingRunId"]
        tax_invoice_id = self.billing_requests.get_tax_invoice_number(target, "Счет-фактура на начисления")
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
            adjustment_type="Отрицательная корректировка счет-фактуры",
            sum_with_tax=300.00,
            tax=50.00,
            status="Создание",
            reason="Отрицательная корректировка счет-фактуры",
            target=re.compile(f"Счёт-фактура: №{tax_invoice_id}.*"),
            advance="300.00",
        )

    @allure.title("07. Применение схемы налогообложения (Обещанный платеж)")
    @allure.id(595732)
    def test_apply_tax_scheme_charge_adjustment_promised_payment(self) -> None:
        inquiry = self.client_requests.product_sale(inquiry=prepare_inquiries("internet"))

        self.client_profile_page.open(
            f"{BASE_URL}customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
        )
        self.client_profile_page.locators.BURGER_MENU.select_by_value("Финансы > Обещанные платежи")

        self.promised_payment.CONNECT_BTN.wait_to_be_visible()
        self.promised_payment.CONNECT_BTN.click()
        self.promised_payment_form.PRODUCT_OFFER_FLD.select_by_value(value="ОП на 100 на 1 день с комиссией 0")
        self.promised_payment_form.ABONENT_FLD.fill(str(inquiry.product.subs_id))
        self.promised_payment_form.INNER_ACCEPT_BTN.click()
        self.client_profile_page.locators.INFO_MESSAGE.wait_to_be_visible()
        self.client_profile_page.locators.INFO_MESSAGE_CLOSE_BTN.click()

        self.promised_payment.PRODUCT_PROMISED_PAYMENT_FLD.wait_to_be_visible()

        billing_profile_id = self.billing_requests.get_billing_profile_id(
            test_context.client.agreements[0].accounts[0].id
        )
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
        create_user_with_agreement_and_account: IndividualClient,
        create_organization_with_agreement_and_account: OrganizationClient,
    ) -> None:
        client_sender = create_user_with_agreement_and_account
        client_receiver = create_organization_with_agreement_and_account
        self.payments_request.create_default_payment(client_sender.agreements[0].accounts[0].id, self.payment_amount)

        self.client_profile_page.open(
            f"{BASE_URL}customer-hierarchy-management/customers/{client_sender.user_id}/overview"
        )

        self.client_profile_page.locators.CLIENT_FIO.wait_to_be_visible()
        self.client_profile_page.check_balance(0, self.payment_amount, "RUB")
        self.client_profile_page.locators.WIDGET_PERSONAL_ACCOUNT_IDS.click(0)
        self.client_profile_page.locators.BURGER_MENU.select_by_value("Финансы > Платежи")

        self.payments_form.payment_elements.CREATE_PAYMENT_BTN.wait_to_be_visible(timeout=10000)
        self.payments_form.payment_elements.BALANCE_TRANSFER_BTN.wait_to_be_visible()
        self.payments_form.payment_elements.BALANCE_TRANSFER_BTN.click()

        self.payments_form.payment_elements.PERSONAL_ACCOUNT_SELECTOR.wait_to_be_visible(timeout=10000)
        self.payments_form.payment_elements.PERSONAL_ACCOUNT_SELECTOR.click()
        self.payments_form.payment_elements.PERSONAL_ACCOUNT_TO_SEARCH.fill(
            client_receiver.agreements[0].accounts[0].number
        )
        self.payments_form.payment_elements.PERSONAL_ACCOUNT_SEARCH_BTN.click()
        self.payments_form.payment_elements.PERSONAL_ACCOUNT_DATA[0].wait_to_be_visible()
        self.payments_form.payment_elements.PERSONAL_ACCOUNT_DATA[1].to_contain_text(
            client_receiver.agreements[0].accounts[0].number
        )
        self.payments_form.dynamic_forms.INNER_ACCEPT_BTN.click()
        self.payments_form.payment_elements.DONOR_ADJUSTMENT_REASON.select_by_value(
            "Перенос средств по заявлению клиента"
        )
        self.payments_form.payment_elements.RECIPIENT_ADJUSTMENT_REASON.select_by_value(
            "Перенос средств по заявлению клиента."
        )
        self.payments_form.payment_elements.BALANCE_TO_TRANSFER.fill("500")
        self.payments_form.dynamic_forms.INNER_ACCEPT_BTN.click()

        self.payments_form.payment_elements.INFO_MESSAGE.wait_to_have_text("Перенос баланса выполнен")

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
            f"{BASE_URL}customer-hierarchy-management/customers/{client_receiver.user_id}/overview"
        )
        self.client_profile_page.locators.WIDGET_PERSONAL_ACCOUNT_IDS[0].wait_to_be_visible(timeout=10000)
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

    @allure.title("09. Создание схемы налогообложения")
    @allure.id(937920)
    def test_tax_scheme_creation(self, delete_taxes: list, delete_tax_schemes: list) -> None:
        tax_rate = 10
        tax_name_ru = f"Тестовый_налог_{generate_russian_string(6)}"
        tax_name_en = f"Test_tax_{generate_english_string(6)}"
        tax_scheme_name_ru = f"Тестовая_налоговая_схема_{generate_russian_string(6)}"
        tax_scheme_name_en = f"Test_tax_scheme_{generate_english_string(6)}"
        start_date = get_shifted_datetime("+1d").strftime("%d.%m.%Y")
        end_date = "31.12.2300"
        version = "Версия 1"

        delete_taxes.append(tax_name_ru)
        delete_tax_schemes.append(tax_scheme_name_ru)

        self.client_profile_page.open_client_profile_page(test_context.client.user_id)
        with allure.step("Создание налога"):
            self.client_profile_page.locators.BURGER_MENU.select_by_value("Биллинг > Схемы налогообложения")
            self.tax_scheme_page.tax_creation(tax_name_ru=tax_name_ru, tax_name_en=tax_name_en, tax_rate=tax_rate)
        with allure.step("Создание налоговой схемы"):
            self.tax_scheme_page.tax_scheme_creation(
                name_ru=tax_scheme_name_ru, name_en=tax_scheme_name_en, tax_name_ru=tax_name_ru
            )
        with allure.step("Открыть версию созданной схемы налогообложения и проверить параметры"):
            self.tax_scheme_page.open_tax_scheme_version(tax_scheme_name_ru, version)
            self.tax_scheme_page.check_tax_scheme_version(
                version,
                "Недействующая",
                start_date,
                end_date,
                tax_scheme_name_ru,
                check_charges_tab=True,
                check_copy_button=True,
            )

    @allure.title("10. Создание схемы налогообложения с некорректной датой начала действия налога")
    @allure.id(937893)
    def test_tax_scheme_with_wrong_date_creation(self, delete_taxes: list) -> None:
        tax_rate = 10
        tax_name_ru = f"Тестовый_налог_{generate_russian_string(6)}"
        tax_name_en = f"Test_tax_{generate_english_string(6)}"
        tax_scheme_name_ru = f"Тестовая_налоговая_схема_{generate_russian_string(6)}"
        tax_scheme_name_en = f"Test_tax_scheme_{generate_english_string(6)}"
        start_date = get_shifted_datetime("+900d").strftime("%d.%m.%Y")

        delete_taxes.append(tax_name_ru)

        self.client_profile_page.open_client_profile_page(test_context.client.user_id)
        with allure.step("Создание налога с датой начала в будущем"):
            self.client_profile_page.locators.BURGER_MENU.select_by_value("Биллинг > Схемы налогообложения")
            self.tax_scheme_page.tax_creation(
                tax_name_ru=tax_name_ru, tax_name_en=tax_name_en, tax_rate=tax_rate, start_date=start_date
            )
        with allure.step("Проверить, что налог с будущей датой недоступен при создании схемы"):
            self.tax_scheme_page.locators.TAX_SCHEMES_TAB.wait_to_be_enabled(timeout=15000)
            self.tax_scheme_page.locators.TAX_SCHEMES_TAB.click()
            self.tax_scheme_page.fill_tax_form(name_ru=tax_scheme_name_ru, name_en=tax_scheme_name_en)
            self.tax_scheme_page.locators.ADD_TAX_TO_SCHEME.wait_to_be_enabled(timeout=15000)
            self.tax_scheme_page.locators.ADD_TAX_TO_SCHEME.click()
            self.tax_scheme_page.locators.TAX_SELECT_FIELD.wait_to_be_enabled(timeout=15000)
            self.tax_scheme_page.locators.TAX_SELECT_FIELD.check_option_not_in_values(tax_name_ru)

    @allure.id(943354)
    @allure.title("12. Добавление исключения при создании схемы налогообложения")
    def test_add_exception_with_create_tax_scheme(self):
        self.client_profile_page.locators.BURGER_MENU.select_by_value("Биллинг > Схемы налогообложения")
        self.tax_scheme_page.tax_scheme_creation(
            f"Test-{generate_english_string(5)}", f"Test-{generate_english_string(5)}", add_exception=True
        )
