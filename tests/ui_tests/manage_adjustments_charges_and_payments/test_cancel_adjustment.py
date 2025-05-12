import re

import allure
import pytest
from playwright.sync_api import APIRequestContext, Page

from api.requests.adjustment_requests import AdjustmentRequests
from api.requests.billing_requests import BillingRequests
from api.requests.client_requests import ClientInfo
from api.requests.payments_requests import PaymentInfo, PaymentsRequests
from api.requests.personal_account_requests import PersonalAccountRequests
from common.helpers.data_generator import (
    generate_random_number,
    get_current_datetime_string,
    get_datetime_from_full_time_string,
)
from pages.adjustments_page import AdjustmentsPage
from pages.billing_accounts_page import BillingAccountsPage
from pages.client_profile_page import ClientProfilePage
from pages.locators.inquiries_page import InquiriesPage
from tests.conftest import CreatedImsis


@allure.suite("E2E_77 Управление корректировками начислений и платежей")
@allure.sub_suite("Аннулирование корректировок")
class TestCancelAdjustment:
    @pytest.fixture(autouse=True)
    def setup(
        self,
        nexign_ui_stand_login: Page,
        api_request_auth_context: APIRequestContext,
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
        self.client = create_user_with_agreement_and_account
        self.balance = 100.00
        self.adjustment_sum = generate_random_number(2)

    @allure.title("Аннулирование отрицательной корректировки платежа")
    @allure.tag("can_aurh", "success")
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=367529544",
        name="ПМИ Аннулирование корректировки к ранее выставленным счетам и СФ",
    )
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=367529056",
        name="ПМИ Создание корректировки к ранее выставленным счетам и СФ",
    )
    @allure.id(588451)
    @pytest.mark.regress
    def test_cancel_negative_payment_adjustment(self, base_url: str) -> None:
        with allure.step("Выполнение предусловий"):
            with allure.step(f"Добавление платежа для ЛС {self.client.account_id}"):
                payment_data = PaymentInfo(
                    document_number=generate_random_number(8),
                    account_id=self.client.account_id,
                    amount=self.balance,
                )
                self.payment_api.wait_check_create_payment(payment_data)
                payment_id = int(self.payment_api.create_payment(payment_data).json()["paymentId"])
                self.payment_api.wait_last_payment_successful(self.client.account_id)
                self.personal_account_api.wait_check_current_main_balance(self.client.account_id, self.balance)
                billing_payment_id = int(
                    self.payment_api.get_payments(self.client.account_id, "-paymentDate").json()["items"][0][
                        "paymentItem"
                    ]["paymentItemId"]
                )

            with allure.step("Создание отрицательной корректировки платежа"):
                self.payment_api.wait_check_add_adjustment_for_payment(payment_id)
                self.adjustment_api.create_adjustment(
                    adjustment_type_id=3,
                    adjustment_reason_id=3,
                    billing_payment_id=billing_payment_id,
                    billing_profile_id=self.billing_api.get_billing_profile_id(self.client.account_id),
                    amount=self.adjustment_sum,
                )
                self.adjustment_api.wait_adjustment_status(self.client.account_id)

            self.client_profile.open(
                f"{base_url}customer-hierarchy-management/accounts/{self.client.account_id}/account"
            )
            self.client_profile.locators.CLIENT_FIO.wait_to_be_visible()

        with allure.step("Перейти на форму 'Фин карточка' - 'Корректировки'"):
            self.client_profile.locators.BURGER_MENU.select_by_value("Корректировки")
            self.adjustments_page.locators.PAGE_TITLE.wait_to_have_text("Корректировки")
            self.adjustments_page.check_buttons()

        with allure.step("Нажать кнопу 'Обновить'"):
            self.adjustments_page.locators.UPDATE_TABLE_BTN.click()
            self.adjustments_page.locators.ADJUSTMENT.wait_elements_visible(0)
            self.adjustments_page.check_adjustment(
                idx=0,
                adjustment_type="Отрицательная корректировка платежа",
                sum_with_tax=-self.adjustment_sum,
                reason="Корректировка платежа",
                target=f"Платёж: {payment_data.document_number} от "
                f"{get_datetime_from_full_time_string(payment_data.payment_date).strftime('%d.%m.%Y')}",
            )
            self.adjustments_page.check_adjustment(0, included_in_bill="")

        with allure.step("Выбрать нужную корректировку, нажать кнопку 'Аннулировать'"):
            self.adjustments_page.locators.ADJUSTMENT_TYPE[0].click()
            self.adjustments_page.locators.CANCEL_BTN.click()
            self.adjustments_page.check_cancel_adjustment_form()

        with allure.step("Нажать кнопку 'Аннулировать'"):
            self.adjustments_page.locators.SECOND_BTN.click()
            self.adjustments_page.locators.MODAL.not_to_be_visible()
            self.adjustments_page.locators.BALANCE.wait_to_have_text(f"{(self.balance - self.adjustment_sum):.2f}")
            self.adjustments_page.check_adjustment(idx=0, status="Отмена")

        with allure.step("Дождаться выполнения запроса, обновить список корректировок"):
            self.adjustment_api.wait_adjustment_status(self.client.account_id, adjustment_status_id=4)
            self.adjustments_page.locators.UPDATE_TABLE_BTN.click()
            self.adjustments_page.check_adjustment(idx=0, status="Отменено")
            self.adjustments_page.locators.BALANCE.wait_to_have_text(f"{self.balance:.2f}")

    @allure.title("Аннулирование отрицательной корректировки платежа учтенной биллингом")
    @allure.tag("can_aurh", "success")
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=367529544",
        name="ПМИ Аннулирование корректировки к ранее выставленным счетам и СФ",
    )
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=367529056",
        name="ПМИ Создание корректировки к ранее выставленным счетам и СФ",
    )
    @allure.id(588387)
    @pytest.mark.regress
    def test_cancel_negative_payment_adjustment_invoiced(self, base_url: str) -> None:
        with allure.step("Выполнение предусловий"):
            with allure.step(f"Добавление платежа для ЛС {self.client.account_id}"):
                payment_data = PaymentInfo(
                    document_number=generate_random_number(8),
                    account_id=self.client.account_id,
                    amount=self.balance,
                )
                self.payment_api.wait_check_create_payment(payment_data)
                payment_id = int(self.payment_api.create_payment(payment_data).json()["paymentId"])
                self.payment_api.wait_last_payment_successful(self.client.account_id)
                self.personal_account_api.wait_check_current_main_balance(self.client.account_id, self.balance)
                billing_payment_id = int(
                    self.payment_api.get_payments(self.client.account_id, "-paymentDate").json()["items"][0][
                        "paymentItem"
                    ]["paymentItemId"]
                )

            with allure.step("Создание отрицательной корректировки платежа"):
                self.payment_api.wait_check_add_adjustment_for_payment(payment_id)
                billing_profile_id = self.billing_api.get_billing_profile_id(self.client.account_id)
                self.adjustment_api.create_adjustment(
                    adjustment_type_id=3,
                    adjustment_reason_id=3,
                    billing_payment_id=billing_payment_id,
                    billing_profile_id=billing_profile_id,
                    amount=self.adjustment_sum,
                )
                self.adjustment_api.wait_adjustment_status(self.client.account_id)

            with allure.step("Проведение внеочередного биллинга"):
                self.billing_api.run_unscheduled_billing(billing_profile_id)
                self.billing_api.wait_billing(billing_profile_id)
                self.billing_api.wait_finish_billing(billing_profile_id, 3)

            self.client_profile.open(
                f"{base_url}customer-hierarchy-management/accounts/{self.client.account_id}/account"
            )
            self.client_profile.locators.CLIENT_FIO.wait_to_be_visible()

        with allure.step("Перейти на форму 'Фин карточка' - 'Биллинговые счета'"):
            self.client_profile.locators.BURGER_MENU.select_by_value("Биллинговые счета")
            self.billing_accounts.locators.PAGE_TITLE.wait_to_have_text("Биллинговые счета")
            self.billing_accounts.locators.REFRESH_BTN.click()
            self.billing_accounts.locators.ACCOUNT_NUMS_LIST.wait_to_be_visible()
            bill_number = self.billing_accounts.locators.ACCOUNT_NUMS_LIST[0].text

        with allure.step("Перейти на форму 'Фин карточка' - 'Корректировки'"):
            self.client_profile.locators.BURGER_MENU.select_by_value("Корректировки")
            self.adjustments_page.locators.PAGE_TITLE.wait_to_have_text("Корректировки")
            self.adjustments_page.check_buttons()

        with allure.step("Нажать кнопу 'Обновить'"):
            self.adjustments_page.locators.UPDATE_TABLE_BTN.click()
            self.adjustments_page.check_adjustment(
                idx=0,
                included_in_bill=re.compile(
                    bill_number + " от " + get_current_datetime_string(False) + r" \d\d:\d\d:\d\d"
                ),
                adjustment_type="Отрицательная корректировка платежа",
                sum_with_tax=-self.adjustment_sum,
                reason="Корректировка платежа",
                target=f"Платёж: {payment_data.document_number} от "
                f"{get_datetime_from_full_time_string(payment_data.payment_date).strftime('%d.%m.%Y')}",
            )
            self.adjustments_page.check_adjustment(0, included_in_bill="")

        with allure.step("Выбрать нужную корректировку, кнопка 'Аннулировать' недоступна"):
            self.adjustments_page.locators.ADJUSTMENT_TYPE[0].click()
            self.adjustments_page.locators.CANCEL_BTN.not_to_be_enabled()

    @allure.title("Аннулирование корректировки счета-фактуры")
    @allure.tag("can_aurh", "success")
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=367529544",
        name="ПМИ Аннулирование корректировки к ранее выставленным счетам и СФ",
    )
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=367529056",
        name="ПМИ Создание корректировки к ранее выставленным счетам и СФ",
    )
    @allure.id(588385)
    @pytest.mark.regress
    def test_cancel_tax_invoice_adjustment(self, add_two_imsi_free_shipped: CreatedImsis, base_url: str) -> None:
        with allure.step("Выполнение предусловий"):
            tax_invoice_type = "Счет-фактура на начисления"

            self.client_profile.open(f"{base_url}customer-hierarchy-management/customers/{self.client.user_id}/overview")
            product = self.inquiries_page.sale_phone_number(self.client)
            subscription_id = self.personal_account_api.get_client_subscriptions(self.client.user_id).json()["items"][0][
                "subscriptionId"
            ]

            with allure.step(f"Добавление платежа для ЛС {self.client.account_id}"):
                payment = PaymentInfo(
                    document_number=generate_random_number(8),
                    account_id=self.client.account_id,
                    amount=product.one_time_payment + product.subscription_fee + self.balance,
                )
                self.payment_api.wait_check_create_payment(payment)
                self.payment_api.create_payment(payment)
                self.payment_api.wait_last_payment_successful(self.client.account_id)
                self.personal_account_api.wait_check_current_main_balance(self.client.account_id, self.balance)

            with allure.step(f"Проведение биллинга для ЛС: {self.client.account_id}"):
                self.personal_account_api.wait_accruals(subscription_id)
                billing_profile_id = self.billing_api.get_billing_profile_id(self.client.account_id)
                self.billing_api.run_unscheduled_billing(billing_profile_id)
                self.billing_api.wait_billing(billing_profile_id)
                self.billing_api.wait_finish_billing(billing_profile_id, 3)
                billing_run_id = self.billing_api.get_list_of_bills([billing_profile_id])[0]["billingRun"][
                    "billingProfileBillingRunId"
                ]

            with allure.step("Создание отрицательной корректировки счёта-фактуры"):
                tax_invoice_id = self.billing_api.get_tax_invoice_id(billing_run_id, tax_invoice_type)
                self.adjustment_api.create_adjustment(
                    adjustment_type_id=18,
                    adjustment_reason_id=32,
                    tax_invoice_id=tax_invoice_id,
                    billing_profile_id=billing_profile_id,
                    amount=self.adjustment_sum,
                )
                self.adjustment_api.wait_adjustment_status(self.client.account_id)

            self.client_profile.open(
                f"{base_url}customer-hierarchy-management/accounts/{self.client.account_id}/account"
            )
            self.client_profile.locators.CLIENT_FIO.wait_to_be_visible()

        with allure.step("Перейти на форму 'Фин карточка' - 'Биллинговые счета'"):
            self.client_profile.locators.BURGER_MENU.select_by_value("Биллинговые счета")
            self.billing_accounts.locators.PAGE_TITLE.wait_to_have_text("Биллинговые счета")
            self.billing_accounts.locators.REFRESH_BTN.click()

        charged, charged_additionally = self.billing_accounts.choose_bill_and_get_charged_charged_additionally()
        detail_adjusted = self.billing_accounts.get_detail_adjusted_property()
        tax_invoice_adjusted = self.billing_accounts.get_tax_invoice_adjusted_property()

        with allure.step("Перейти на форму 'Фин карточка' - 'Корректировки'"):
            self.client_profile.locators.BURGER_MENU.select_by_value("Корректировки")
            self.adjustments_page.locators.PAGE_TITLE.wait_to_have_text("Корректировки")
            self.adjustments_page.check_buttons()
            self.adjustments_page.check_adjustment(
                idx=0,
                adjustment_type="Отрицательная коррекировка счёт-фактуры",
                sum_with_tax=self.adjustment_sum,
                status="Одобрено",
                reason="Отрицательная коррекировка счёт-фактуры",
            )

        with allure.step("Выбрать необходиму корректировку счета-факуры, нажать кнопку 'Аннулировать'"):
            self.adjustments_page.locators.ADJUSTMENT_TYPE[0].click()
            self.adjustments_page.locators.CANCEL_BTN.click()
            self.adjustments_page.check_cancel_adjustment_form()

        with allure.step("Нажать кнопку 'Отменить'"):
            self.adjustments_page.locators.FIRST_BTN.click()
            self.adjustments_page.locators.MODAL.not_to_be_visible()
            self.adjustments_page.check_adjustment(idx=0, status="Одобрено")

        with allure.step("Выбрать необходиму корректировку счета-факуры, нажать кнопку 'Аннулировать'"):
            self.adjustments_page.locators.ADJUSTMENT_TYPE[0].click()
            self.adjustments_page.locators.CANCEL_BTN.click()
            self.adjustments_page.check_cancel_adjustment_form()

        with allure.step("Нажать кнопку 'Аннулировать'"):
            self.adjustments_page.locators.SECOND_BTN.click()
            self.adjustments_page.locators.MODAL.not_to_be_visible()
            self.adjustments_page.locators.BALANCE.wait_to_have_text(f"{(self.balance + self.adjustment_sum):.2f}")
            self.adjustments_page.check_adjustment(idx=0, status="Отмена")

        with allure.step("Дождаться выполнения запроса, обновить список корректировок"):
            self.adjustment_api.wait_adjustment_status(self.client.account_id, adjustment_status_id=4)
            self.adjustments_page.locators.UPDATE_TABLE_BTN.click()
            self.adjustments_page.check_adjustment(idx=0, status="Отменено")
            self.adjustments_page.locators.BALANCE.wait_to_have_text(f"{self.balance:.2f}")

        with allure.step("Перейти на форму 'Фин карточка' - 'Биллинговые счета', выбрать нужный счет"):
            self.client_profile.locators.BURGER_MENU.select_by_value("Биллинговые счета")
            self.billing_accounts.locators.PAGE_TITLE.wait_to_have_text("Биллинговые счета")
            self.billing_accounts.locators.ACCOUNT_NUMS_LIST.wait_to_be_visible()
            self.billing_accounts.locators.ACCOUNT_NUMS_LIST.click(0)

        self.billing_accounts.check_charged_additionally_property(charged_additionally - self.adjustment_sum)
        self.billing_accounts.check_detail_adjusted_property(detail_adjusted - self.adjustment_sum)
        self.billing_accounts.check_tax_invoice_adjusted_property(tax_invoice_adjusted - self.adjustment_sum)

    @allure.title("Аннулирование корректировки детали счета")
    @allure.tag("can_aurh", "success")
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=367529544",
        name="ПМИ Аннулирование корректировки к ранее выставленным счетам и СФ",
    )
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=367529056",
        name="ПМИ Создание корректировки к ранее выставленным счетам и СФ",
    )
    @allure.id(588393)
    @pytest.mark.regress
    def test_cancel_bill_detail_adjustment(self, add_two_imsi_free_shipped: CreatedImsis, base_url: str) -> None:
        with allure.step("Выполнение предусловий"):
            self.client_profile.open(f"{base_url}customer-hierarchy-management/customers/{self.client.user_id}/overview")
            product = self.inquiries_page.sale_phone_number(self.client)
            subscription_id = self.personal_account_api.get_client_subscriptions(self.client.user_id).json()["items"][0][
                "subscriptionId"
            ]

            with allure.step(f"Добавление платежа для ЛС {self.client.account_id}"):
                payment = PaymentInfo(
                    document_number=generate_random_number(8),
                    account_id=self.client.account_id,
                    amount=product.one_time_payment + product.subscription_fee + self.balance,
                )
                self.payment_api.wait_check_create_payment(payment)
                self.payment_api.create_payment(payment)
                self.payment_api.wait_last_payment_successful(self.client.account_id)
                self.personal_account_api.wait_check_current_main_balance(self.client.account_id, self.balance)

            with allure.step(f"Проведение биллинга для ЛС: {self.client.account_id}"):
                self.personal_account_api.wait_accruals(subscription_id)
                billing_profile_id = self.billing_api.get_billing_profile_id(self.client.account_id)
                self.billing_api.run_unscheduled_billing(billing_profile_id)
                self.billing_api.wait_billing(billing_profile_id)
                self.billing_api.wait_finish_billing(billing_profile_id, 3)
                bill_id = self.billing_api.get_list_of_bills([billing_profile_id])[0]["billId"]
                bill_detail_value_id = self.billing_api.get_bill_details(bill_id)[0]["billDetailValueId"]

            with allure.step("Создание отрицательной корректировки счёта-фактуры"):
                self.adjustment_api.create_adjustment(
                    adjustment_type_id=2,
                    adjustment_reason_id=2,
                    bill_id=bill_id,
                    bill_detail_value_id=bill_detail_value_id,
                    billing_profile_id=billing_profile_id,
                    amount=self.adjustment_sum,
                )
                self.adjustment_api.wait_adjustment_status(self.client.account_id)

            self.client_profile.open(
                f"{base_url}customer-hierarchy-management/accounts/{self.client.account_id}/account"
            )
            self.client_profile.locators.CLIENT_FIO.wait_to_be_visible()

        with allure.step("Перейти на форму 'Фин карточка' - 'Биллинговые счета'"):
            self.client_profile.locators.BURGER_MENU.select_by_value("Биллинговые счета")
            self.billing_accounts.locators.PAGE_TITLE.wait_to_have_text("Биллинговые счета")
            self.billing_accounts.locators.REFRESH_BTN.click()

        charged, charged_additionally = self.billing_accounts.choose_bill_and_get_charged_charged_additionally()
        detail_adjusted = self.billing_accounts.get_detail_adjusted_property()

        with allure.step("Перейти на форму 'Фин карточка' - 'Корректировки'"):
            self.client_profile.locators.BURGER_MENU.select_by_value("Корректировки")
            self.adjustments_page.locators.PAGE_TITLE.wait_to_have_text("Корректировки")
            self.adjustments_page.check_buttons()
            self.adjustments_page.check_adjustment(
                idx=0,
                adjustment_type="Отрицательная корректировка детализации счета",
                sum_with_tax=self.adjustment_sum,
                status="Одобрено",
                target_type="Основной счёт",
                reason="Отрицательная корректировка детали счета",
            )

        with allure.step("Выбрать необходиму корректировку счета-факуры, нажать кнопку 'Аннулировать'"):
            self.adjustments_page.locators.ADJUSTMENT_TYPE[0].click()
            self.adjustments_page.locators.CANCEL_BTN.click()
            self.adjustments_page.check_cancel_adjustment_form()

        with allure.step("Нажать кнопку 'Аннулировать'"):
            self.adjustments_page.locators.SECOND_BTN.click()
            self.adjustments_page.locators.MODAL.not_to_be_visible()
            self.adjustments_page.locators.BALANCE.wait_to_have_text(f"{(self.balance + self.adjustment_sum):.2f}")
            self.adjustments_page.check_adjustment(idx=0, status="Отмена")

        with allure.step("Дождаться выполнения запроса, обновить список корректировок"):
            self.adjustment_api.wait_adjustment_status(self.client.account_id, adjustment_status_id=4)
            self.adjustments_page.locators.UPDATE_TABLE_BTN.click()
            self.adjustments_page.check_adjustment(idx=0, status="Отменено")
            self.adjustments_page.locators.BALANCE.wait_to_have_text(f"{self.balance:.2f}")

        with allure.step("Перейти на форму 'Фин карточка' - 'Биллинговые счета', выбрать нужный счет"):
            self.client_profile.locators.BURGER_MENU.select_by_value("Биллинговые счета")
            self.billing_accounts.locators.PAGE_TITLE.wait_to_have_text("Биллинговые счета")
            self.billing_accounts.locators.ACCOUNT_NUMS_LIST.wait_to_be_visible()
            self.billing_accounts.locators.ACCOUNT_NUMS_LIST.click(0)

        self.billing_accounts.check_charged_additionally_property(charged_additionally - self.adjustment_sum)
        self.billing_accounts.check_detail_adjusted_property(detail_adjusted - self.adjustment_sum)
