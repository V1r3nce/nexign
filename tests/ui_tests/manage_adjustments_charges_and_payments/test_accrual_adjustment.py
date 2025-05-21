import re

import allure
import pytest
from playwright.sync_api import APIRequestContext, Page

from api.requests.adjustment_requests import AdjustmentRequests
from api.requests.billing_requests import BillingRequests
from api.requests.client_requests import ClientInfo
from api.requests.payments_requests import PaymentInfo, PaymentsRequests
from api.requests.personal_account_requests import PersonalAccountRequests
from common.helpers.checker import assert_that
from common.helpers.data_generator import (
    generate_random_number,
    get_current_datetime_string,
    get_datetime_from_full_time_string,
)
from pages.adjustments_page import AdjustmentsPage
from pages.billing_accounts_page import BillingAccountsPage
from pages.client_profile_page import ClientProfilePage
from pages.locators.adjustments import CreateAdjustmentForm
from pages.locators.inquiries_page import InquiriesPage
from tests.conftest import CreatedImsis


@allure.suite("E2E_77 Управление корректировками начислений и платежей")
@allure.sub_suite("Коректировки начислений")
class TestAccrualAdjustment:
    @pytest.fixture(autouse=True)
    def setup(
        self,
        nexign_ui_stand_login: Page,
        api_request_auth_context: APIRequestContext,
        add_two_imsi_free_shipped: CreatedImsis,
        create_user_with_agreement_and_account: ClientInfo,
    ) -> None:
        self.personal_account_api = PersonalAccountRequests(api_request_auth_context)
        self.payment_api = PaymentsRequests(api_request_auth_context)
        self.billing_api = BillingRequests(api_request_auth_context)
        self.adjustment_api = AdjustmentRequests(api_request_auth_context)

        self.client_profile = ClientProfilePage(nexign_ui_stand_login)
        self.inquiries_page = InquiriesPage(nexign_ui_stand_login)
        self.billing_accounts = BillingAccountsPage(nexign_ui_stand_login)
        self.adjustments_page = AdjustmentsPage(nexign_ui_stand_login)
        self.create_adjustment_form = CreateAdjustmentForm(nexign_ui_stand_login)
        self.client = create_user_with_agreement_and_account

    @allure.title("Создание отрицательной корректировки счёта")
    @allure.tag("can_aurh", "success")
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=367529056",
        name="ПМИ Создание корректировки к ранее выставленным счетам и СФ",
    )
    @allure.id(585713)
    @pytest.mark.regress
    def test_create_negative_adjustment_bill(self, base_url: str) -> None:
        with allure.step("Выполнение предусловий"):
            self.client_profile.open(f"{base_url}customer-hierarchy-management/customers/{self.client.user_id}/overview")
            product = self.inquiries_page.sale_phone_number(self.client)
            subscription_id = self.personal_account_api.get_client_subscriptions(self.client.user_id).json()["items"][0][
                "subscriptionId"
            ]

            with allure.step(f"Добавление платежа для ЛС {self.client.account_id}"):
                balance = 100.00
                payment = PaymentInfo(
                    document_number=generate_random_number(8),
                    item_type="CUSTOMER_ACCOUNT",
                    account_id=self.client.account_id,
                    payment_method_type="CASH",
                    currency_code="RUB",
                    amount=product.one_time_payment + product.subscription_fee + balance,
                )
                self.payment_api.wait_check_create_payment(payment)
                self.payment_api.create_payment(payment)
                self.payment_api.wait_last_payment_successful(self.client.account_id)
                self.personal_account_api.wait_check_current_main_balance(self.client.account_id, balance)

            self.client_profile.locators.CLIENT_FIO_BTN.click()
            self.client_profile.locators.BALANCE.wait_to_be_visible()
            self.client_profile.locators.BALANCE[0].to_contain_text(f"{balance:.2f}")

            with allure.step(f"Проведение биллинга для ЛС: {self.client.account_id}"):
                self.personal_account_api.wait_accruals(subscription_id)
                billing_profile_id = self.billing_api.get_billing_profile_id(self.client.account_id)
                self.billing_api.run_unscheduled_billing(billing_profile_id)
                self.billing_api.wait_billing(billing_profile_id)
                self.billing_api.wait_finish_billing(billing_profile_id, 3)
                bill_data = self.billing_api.get_list_of_bills([billing_profile_id])[0]
                bill_number = bill_data["billNumber"]
                end_date_period = get_datetime_from_full_time_string(
                    bill_data["billingRun"]["period"]["endDateTime"][:19]
                ).strftime("%d.%m.%Y %H:%M:%S")

            self.client_profile.open(
                f"{base_url}customer-hierarchy-management/accounts/{self.client.account_id}/account"
            )
            self.client_profile.locators.CLIENT_FIO.wait_to_be_visible()

        with allure.step("Перейти на форму 'Фин карточка' - 'Биллинговые счета'"):
            self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Биллинговые счета")
            self.adjustments_page.locators.SELECTED_TAB_TITLE.wait_to_have_text("Биллинговые счета")

        charged, charged_additionally = self.billing_accounts.choose_bill_and_get_charged_charged_additionally()
        adjusted = self.billing_accounts.get_detail_adjusted_property()

        with allure.step("Перейти на форму 'Фин карточка' - 'Корректировки'"):
            self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Корректировки")
            self.adjustments_page.locators.SELECTED_TAB_TITLE.wait_to_have_text("Корректировки")
            self.adjustments_page.check_buttons()

        with allure.step("Нажать кнопку 'Добавить корректировку' - 'Ввод корректировки начисления'"):
            self.adjustments_page.locators.ADD_ADJUSTMENT_BTN.select_by_value("Ввод корректировки начисления")
            self.adjustments_page.check_create_charge_adjustment_form()

        self.adjustments_page.fill_bill_input_create_adjustment_form(
            bill_number=bill_number, end_date_period=end_date_period
        )

        with allure.step("Продолжить заполнение полей"):
            assert_that(
                lambda: self.create_adjustment_form.ADJUSTMENT_TYPE_RADIOBUTTONS.checked_value
                == "Отрицательная корректировка",
                "По умолчанию не выбрано 'Отрицательная корректировка'",
            )
            self.create_adjustment_form.ADJUSTMENT_TYPE_RADIOBUTTONS.all_elements_to_have_class(re.compile(r"disabled"))
            adjustment_sum = generate_random_number(len(str(charged).split(".")[0]) - 1)
            tax = self.adjustments_page.fill_other_required_input_create_adjustment_form(
                adjustment_sum=adjustment_sum,
                reason="Отрицательная корректировка счета",
            )
            adjustment_date = get_current_datetime_string(is_full_format=False)
            self.create_adjustment_form.TITLE.not_to_be_visible()
            self.adjustments_page.locators.BALANCE.wait_to_have_text(f"{balance:.2f}")
            self.adjustments_page.check_adjustment(
                idx=0,
                adjustment_type="Отрицательная корректировка счета",
                date=adjustment_date,
                sum_with_tax=adjustment_sum,
                tax=tax,
                status="Создание",
                reason="Отрицательная корректировка счета",
                target_type="Основной счёт",
                target=f"Счёт: №{bill_number} от {end_date_period}",
            )

        with allure.step("Дождаться выполнения запроса, обновить список корректировок"):
            self.adjustment_api.wait_adjustment_status(self.client.account_id)
            self.adjustments_page.locators.UPDATE_TABLE_BTN.click()
            self.adjustments_page.check_adjustment(idx=0, status="Одобрено")
            self.adjustments_page.locators.BALANCE.wait_to_have_text(f"{(balance + adjustment_sum):.2f}", timeout=15000)

        with allure.step("Перейти на форму 'Фин карточка' - 'Биллинговые счета'"):
            self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Биллинговые счета")
            self.adjustments_page.locators.SELECTED_TAB_TITLE.wait_to_have_text("Биллинговые счета")
            self.billing_accounts.locators.ACCOUNT_NUMS_LIST.wait_to_be_visible()
            self.billing_accounts.locators.ACCOUNT_NUMS_LIST.click(0)

        self.billing_accounts.check_charged_additionally_property(charged_additionally + adjustment_sum)
        self.billing_accounts.check_detail_adjusted_property(adjusted + adjustment_sum)

    @allure.title("Создание отрицательной корректировки счёта (Сумма корректировки превышает сумму счета)")
    @allure.tag("can_aurh", "success")
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=367529056",
        name="ПМИ Создание корректировки к ранее выставленным счетам и СФ",
    )
    @allure.id(587316)
    @pytest.mark.regress
    def test_create_negative_adjustment_bill_with_summ_more_then_accrual(self, base_url: str) -> None:
        with allure.step("Выполнение предусловий"):
            self.client_profile.open(f"{base_url}customer-hierarchy-management/customers/{self.client.user_id}/overview")
            product = self.inquiries_page.sale_phone_number(self.client)
            subscription_id = self.personal_account_api.get_client_subscriptions(self.client.user_id).json()["items"][0][
                "subscriptionId"
            ]

            with allure.step(f"Добавление платежа для ЛС {self.client.account_id}"):
                balance = 100.00
                payment = PaymentInfo(
                    document_number=generate_random_number(8),
                    item_type="CUSTOMER_ACCOUNT",
                    account_id=self.client.account_id,
                    payment_method_type="CASH",
                    currency_code="RUB",
                    amount=product.one_time_payment + product.subscription_fee + balance,
                )
                self.payment_api.wait_check_create_payment(payment)
                self.payment_api.create_payment(payment)
                self.payment_api.wait_last_payment_successful(self.client.account_id)
                self.personal_account_api.wait_check_current_main_balance(self.client.account_id, balance)

            self.client_profile.locators.CLIENT_FIO_BTN.click()
            self.client_profile.locators.BALANCE.wait_to_be_visible()
            self.client_profile.locators.BALANCE[0].to_contain_text(f"{balance:.2f}")

            with allure.step(f"Проведение биллинга для ЛС: {self.client.account_id}"):
                self.personal_account_api.wait_accruals(subscription_id)
                billing_profile_id = self.billing_api.get_billing_profile_id(self.client.account_id)
                self.billing_api.run_unscheduled_billing(billing_profile_id)
                self.billing_api.wait_billing(billing_profile_id)
                self.billing_api.wait_finish_billing(billing_profile_id, 3)
                bill_data = self.billing_api.get_list_of_bills([billing_profile_id])[0]
                bill_number = bill_data["billNumber"]
                end_date_period = get_datetime_from_full_time_string(
                    bill_data["billingRun"]["period"]["endDateTime"][:19]
                ).strftime("%d.%m.%Y %H:%M:%S")

            self.client_profile.open(
                f"{base_url}customer-hierarchy-management/accounts/{self.client.account_id}/account"
            )
            self.client_profile.locators.CLIENT_FIO.wait_to_be_visible()

        with allure.step("Перейти на форму 'Фин карточка' - 'Биллинговые счета'"):
            self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Биллинговые счета")
            self.adjustments_page.locators.SELECTED_TAB_TITLE.wait_to_have_text("Биллинговые счета")

        charged, _ = self.billing_accounts.choose_bill_and_get_charged_charged_additionally()

        with allure.step("Перейти на форму 'Фин карточка' - 'Корректировки'"):
            self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Корректировки")
            self.adjustments_page.locators.SELECTED_TAB_TITLE.wait_to_have_text("Корректировки")
            self.adjustments_page.check_buttons()

        with allure.step("Нажать кнопку 'Добавить корректировку' - 'Ввод корректировки начисления'"):
            self.adjustments_page.locators.ADD_ADJUSTMENT_BTN.select_by_value("Ввод корректировки начисления")
            self.adjustments_page.check_create_charge_adjustment_form()

        self.adjustments_page.fill_bill_input_create_adjustment_form(
            bill_number=bill_number, end_date_period=end_date_period
        )

        with allure.step("Продолжить заполнение полей"):
            assert_that(
                lambda: self.create_adjustment_form.ADJUSTMENT_TYPE_RADIOBUTTONS.checked_value
                == "Отрицательная корректировка",
                "По умолчанию не выбрано 'Отрицательная корректировка'",
            )
            self.create_adjustment_form.ADJUSTMENT_TYPE_RADIOBUTTONS.all_elements_to_have_class(re.compile(r"disabled"))
            adjustment_sum = generate_random_number(len(str(charged).split(".")[0]) + 1)
            self.adjustments_page.fill_other_required_input_create_adjustment_form(
                adjustment_sum=adjustment_sum,
                reason="Отрицательная корректировка счета",
            )
            self.create_adjustment_form.TITLE.not_to_be_visible()
            self.adjustments_page.base_elements.MODAL_TITLE[0].to_contain_text("Ошибка")
            self.adjustments_page.base_elements.MODAL_BODY_TEXT[0].to_contain_text(
                "Сумма больше чем доступная для исправления для счёта с идентификатором"
            )

    @allure.title("Создание отрицательной корректировки счёта-фактуры")
    @allure.tag("can_aurh", "success")
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=367529056",
        name="ПМИ Создание корректировки к ранее выставленным счетам и СФ",
    )
    @allure.id(588111)
    @pytest.mark.regress
    def test_create_negative_adjustment_tax_invoice(self, base_url: str) -> None:
        with allure.step("Выполнение предусловий"):
            self.client_profile.open(f"{base_url}customer-hierarchy-management/customers/{self.client.user_id}/overview")
            product = self.inquiries_page.sale_phone_number(self.client)
            subscription_id = self.personal_account_api.get_client_subscriptions(self.client.user_id).json()["items"][0][
                "subscriptionId"
            ]

            with allure.step(f"Добавление платежа для ЛС {self.client.account_id}"):
                balance = 100.00
                payment = PaymentInfo(
                    document_number=generate_random_number(8),
                    item_type="CUSTOMER_ACCOUNT",
                    account_id=self.client.account_id,
                    payment_method_type="CASH",
                    currency_code="RUB",
                    amount=product.one_time_payment + product.subscription_fee + balance,
                )
                self.payment_api.wait_check_create_payment(payment)
                self.payment_api.create_payment(payment)
                self.payment_api.wait_last_payment_successful(self.client.account_id)
                self.personal_account_api.wait_check_current_main_balance(self.client.account_id, balance)

            self.client_profile.locators.CLIENT_FIO_BTN.click()
            self.client_profile.locators.BALANCE.wait_to_be_visible()
            self.client_profile.locators.BALANCE[0].to_contain_text(f"{balance:.2f}")

            with allure.step(f"Проведение биллинга для ЛС: {self.client.account_id}"):
                self.personal_account_api.wait_accruals(subscription_id)
                billing_profile_id = self.billing_api.get_billing_profile_id(self.client.account_id)
                self.billing_api.run_unscheduled_billing(billing_profile_id)
                self.billing_api.wait_billing(billing_profile_id)
                self.billing_api.wait_finish_billing(billing_profile_id, 3)

            self.client_profile.open(
                f"{base_url}customer-hierarchy-management/accounts/{self.client.account_id}/account"
            )
            self.client_profile.locators.CLIENT_FIO.wait_to_be_visible()

        with allure.step("Перейти на форму 'Фин карточка' - 'Биллинговые счета'"):
            self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Биллинговые счета")
            self.adjustments_page.locators.SELECTED_TAB_TITLE.wait_to_have_text("Биллинговые счета")

        charged, charged_additionally = self.billing_accounts.choose_bill_and_get_charged_charged_additionally()
        detail_adjusted = self.billing_accounts.get_detail_adjusted_property()
        tax_invoice_type = "Счет-фактура на начисления"
        tax_invoice_adjusted = self.billing_accounts.get_tax_invoice_adjusted_property()

        with allure.step("Перейти на форму 'Фин карточка' - 'Корректировки'"):
            self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Корректировки")
            self.adjustments_page.locators.SELECTED_TAB_TITLE.wait_to_have_text("Корректировки")
            self.adjustments_page.check_buttons()

        with allure.step("Нажать кнопку 'Добавить корректировку' - 'Ввод корректировки начисления'"):
            self.adjustments_page.locators.ADD_ADJUSTMENT_BTN.select_by_value("Ввод корректировки начисления")
            self.adjustments_page.check_create_charge_adjustment_form()

        tax_invoice = self.adjustments_page.fill_tax_invoice_input_create_adjustment_form(tax_invoice_type)

        with allure.step("Продолжить заполнение полей"):
            assert_that(
                lambda: self.create_adjustment_form.ADJUSTMENT_TYPE_RADIOBUTTONS.checked_value
                == "Отрицательная корректировка",
                "По умолчанию не выбрано 'Отрицательная корректировка'",
            )
            self.create_adjustment_form.ADJUSTMENT_TYPE_RADIOBUTTONS.all_elements_to_have_class(re.compile(r"disabled"))
            adjustment_sum = generate_random_number(len(str(charged).split(".")[0]) - 1)
            tax = self.adjustments_page.fill_other_required_input_create_adjustment_form(
                adjustment_sum=adjustment_sum,
                reason="Отрицательная коррекировка счёт-фактуры",
            )
            adjustment_date = get_current_datetime_string(is_full_format=False)
            self.create_adjustment_form.TITLE.not_to_be_visible()
            self.adjustments_page.locators.BALANCE.wait_to_have_text(f"{balance:.2f}")
            self.adjustments_page.check_adjustment(
                idx=0,
                adjustment_type="Отрицательная коррекировка счёт-фактуры",
                date=adjustment_date,
                sum_with_tax=adjustment_sum,
                tax=tax,
                status="Создание",
                target=tax_invoice,
                reason="Отрицательная коррекировка счёт-фактуры",
            )

        with allure.step("Дождаться выполнения запроса, обновить список корректировок"):
            self.adjustment_api.wait_adjustment_status(self.client.account_id)
            self.adjustments_page.locators.UPDATE_TABLE_BTN.click()
            self.adjustments_page.check_adjustment(idx=0, status="Одобрено")
            self.adjustments_page.locators.BALANCE.wait_to_have_text(f"{(balance + adjustment_sum):.2f}", timeout=15000)

        with allure.step("Перейти на форму 'Фин карточка' - 'Биллинговые счета'"):
            self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Биллинговые счета")
            self.adjustments_page.locators.SELECTED_TAB_TITLE.wait_to_have_text("Биллинговые счета")
            self.billing_accounts.locators.ACCOUNT_NUMS_LIST.wait_to_be_visible()
            self.billing_accounts.locators.ACCOUNT_NUMS_LIST.click(0)

        self.billing_accounts.check_charged_additionally_property(charged_additionally + adjustment_sum)
        self.billing_accounts.check_detail_adjusted_property(detail_adjusted + adjustment_sum)
        self.billing_accounts.check_tax_invoice_adjusted_property(tax_invoice_adjusted + adjustment_sum)
