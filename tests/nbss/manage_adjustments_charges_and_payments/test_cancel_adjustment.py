import re

import allure
import pytest

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from api.nbss.finances.adjustment_requests import AdjustmentRequests
from api.nbss.finances.billing_requests import BillingRequests
from api.nbss.finances.payments_requests import PaymentsRequests
from api.nbss.personal_account_requests import PersonalAccountRequests
from common.helpers.data_generator import (
    generate_random_number,
    get_current_datetime_string,
    get_datetime_from_full_time_string,
)
from models.client import OrganizationClient
from models.context import test_context
from models.inquiry import prepare_inquiries
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.finances.adjustments_page import AdjustmentsPage
from pages.nbss.finances.billing_accounts_page import BillingAccountsPage


@allure.suite("E2E_77 Управление корректировками начислений и платежей")
@allure.sub_suite("Аннулирование корректировок")
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestCancelAdjustment:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login, create_organization_with_agreement_and_account: OrganizationClient) -> None:
        self.personal_account_api = PersonalAccountRequests()
        self.payment_api = PaymentsRequests()
        self.client_request_api = ClientInquiriesRequests()
        self.billing_api = BillingRequests()
        self.adjustment_api = AdjustmentRequests()

        self.client_profile = ClientProfilePage()
        self.billing_accounts = BillingAccountsPage()
        self.adjustments_page = AdjustmentsPage()
        self.balance = 100.00
        self.adjustment_sum = generate_random_number(2)

    @allure.title("Аннулирование отрицательной корректировки платежа")
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=367529544",
        name="ПМИ Аннулирование корректировки к ранее выставленным счетам и СФ",
    )
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=367529056",
        name="ПМИ Создание корректировки к ранее выставленным счетам и СФ",
    )
    @allure.id(588451)
    def test_cancel_negative_payment_adjustment(self, base_url: str) -> None:
        with allure.step("Выполнение предусловий"):
            with allure.step(f"Добавление платежа для ЛС {test_context.client.agreements[0].accounts[0].id}"):
                self.payment_api.create_default_payment(test_context.client.agreements[0].accounts[0].id, self.balance)
                self.personal_account_api.wait_check_current_main_balance(
                    test_context.client.agreements[0].accounts[0].id, self.balance
                )
                payment_data = self.payment_api.get_payments(test_context.client.agreements[0].accounts[0].id).json()[
                    "items"
                ][0]
                payment_id = int(payment_data["paymentId"])
                billing_payment_id = int(payment_data["paymentItem"]["paymentItemId"])

            with allure.step("Создание отрицательной корректировки платежа"):
                self.payment_api.wait_check_add_adjustment_for_payment(payment_id)
                self.adjustment_api.create_adjustment(
                    adjustment_type_id=3,
                    adjustment_reason_id=3,
                    billing_payment_id=billing_payment_id,
                    billing_profile_id=self.billing_api.get_billing_profile_id(
                        test_context.client.agreements[0].accounts[0].id
                    ),
                    amount=self.adjustment_sum,
                )
                self.adjustment_api.wait_adjustment_status(test_context.client.agreements[0].accounts[0].id)

            self.client_profile.open(
                f"{base_url}customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
            )
            self.client_profile.locators.CLIENT_FIO.wait_to_be_visible(timeout=20000)

        with allure.step("Перейти на форму 'Финансы' - 'Корректировки'"):
            self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Корректировки")
            self.adjustments_page.locators.SELECTED_TAB_TITLE.wait_to_have_text("Корректировки")
            self.adjustments_page.check_buttons()

        with allure.step("Нажать кнопу 'Обновить'"):
            self.adjustments_page.locators.UPDATE_TABLE_BTN.click()
            self.adjustments_page.locators.ADJUSTMENTS.wait_elements_visible(0)
            self.adjustments_page.check_adjustment(
                idx=0,
                adjustment_type="Отрицательная корректировка платежа",
                sum_with_tax=-self.adjustment_sum,
                reason="Корректировка платежа",
                target=f"Платёж: {payment_data['documentNumber']} от {get_datetime_from_full_time_string(payment_data['paymentDate'][:19]).strftime('%d.%m.%Y %H:%M:%S')}",
            )
            self.adjustments_page.check_adjustment(0, included_in_bill="")

        with allure.step("Выбрать нужную корректировку, нажать кнопку 'Аннулировать'"):
            self.adjustments_page.locators.ADJUSTMENT_TYPE[0].click()
            self.adjustments_page.locators.CANCEL_BTN.wait_to_be_enabled(timeout=15000)
            self.adjustments_page.locators.CANCEL_BTN.click()
            self.adjustments_page.check_cancel_adjustment_form()

        with allure.step("Нажать кнопку 'Аннулировать'"):
            self.adjustments_page.locators.MODAL_SECOND_BTN.click()
            self.adjustments_page.locators.MODAL.wait_not_to_be_visible()
            self.adjustments_page.locators.BALANCE.wait_to_have_text(f"{(self.balance - self.adjustment_sum):.2f}")
            self.adjustments_page.check_adjustment(idx=0, status="Отмена")

        with allure.step("Дождаться выполнения запроса, обновить список корректировок"):
            self.adjustment_api.wait_adjustment_status(
                test_context.client.agreements[0].accounts[0].id, adjustment_status_id=4
            )
            self.adjustments_page.locators.UPDATE_TABLE_BTN.click()
            self.adjustments_page.check_adjustment(idx=0, status="Отменено")
            self.adjustments_page.locators.BALANCE.wait_to_have_text(f"{self.balance:.2f}")

    @allure.title("Аннулирование отрицательной корректировки платежа учтенной биллингом")
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=367529544",
        name="ПМИ Аннулирование корректировки к ранее выставленным счетам и СФ",
    )
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=367529056",
        name="ПМИ Создание корректировки к ранее выставленным счетам и СФ",
    )
    @allure.id(588387)
    def test_cancel_negative_payment_adjustment_invoiced(self, base_url: str) -> None:
        with allure.step("Выполнение предусловий"):
            with allure.step(f"Добавление платежа для ЛС {test_context.client.agreements[0].accounts[0].id}"):
                self.payment_api.create_default_payment(test_context.client.agreements[0].accounts[0].id, self.balance)
                self.personal_account_api.wait_check_current_main_balance(
                    test_context.client.agreements[0].accounts[0].id, self.balance
                )
                payment_data = self.payment_api.get_payments(test_context.client.agreements[0].accounts[0].id).json()[
                    "items"
                ][0]
                payment_id = int(payment_data["paymentId"])
                billing_payment_id = int(payment_data["paymentItem"]["paymentItemId"])

            with allure.step("Создание отрицательной корректировки платежа"):
                self.payment_api.wait_check_add_adjustment_for_payment(payment_id)
                billing_profile_id = self.billing_api.get_billing_profile_id(
                    test_context.client.agreements[0].accounts[0].id
                )
                self.adjustment_api.create_adjustment(
                    adjustment_type_id=3,
                    adjustment_reason_id=3,
                    billing_payment_id=billing_payment_id,
                    billing_profile_id=billing_profile_id,
                    amount=self.adjustment_sum,
                )
                self.adjustment_api.wait_adjustment_status(test_context.client.agreements[0].accounts[0].id)

            with allure.step("Проведение внеочередного биллинга"):
                self.billing_api.run_unscheduled_billing(billing_profile_id)
                self.billing_api.wait_billing(billing_profile_id)
                self.billing_api.wait_finish_billing(billing_profile_id, 3)

            self.client_profile.open(
                f"{base_url}customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
            )
            self.client_profile.locators.CLIENT_FIO.wait_to_be_visible(timeout=20000)

        with allure.step("Перейти на форму 'Финансы' - 'Биллинговые счета'"):
            self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Биллинговые счета")
            self.billing_accounts.locators.SELECTED_TAB_TITLE.wait_to_have_text("Биллинговые счета")
            self.billing_accounts.locators.REFRESH_BTN.click()
            self.billing_accounts.locators.ACCOUNT_NUMS_LIST.wait_to_be_visible()
            bill_number = self.billing_accounts.locators.ACCOUNT_NUMS_LIST[0].text

        with allure.step("Перейти на форму 'Финансы' - 'Корректировки'"):
            self.billing_accounts.click_tab("Корректировки")
            self.adjustments_page.locators.SELECTED_TAB_TITLE.wait_to_have_text("Корректировки")
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
                target=f"Платёж: {payment_data['documentNumber']} от {get_datetime_from_full_time_string(payment_data['paymentDate'][:19]).strftime('%d.%m.%Y %H:%M:%S')}",
            )
            self.adjustments_page.check_adjustment(0, included_in_bill="")

        with allure.step("Выбрать нужную корректировку, кнопка 'Аннулировать' недоступна"):
            self.adjustments_page.locators.ADJUSTMENT_TYPE[0].click()
            self.adjustments_page.locators.CANCEL_BTN.not_to_be_enabled()

    @allure.title("Аннулирование корректировки счета-фактуры")
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=367529544",
        name="ПМИ Аннулирование корректировки к ранее выставленным счетам и СФ",
    )
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=367529056",
        name="ПМИ Создание корректировки к ранее выставленным счетам и СФ",
    )
    @allure.id(588385)
    def test_cancel_tax_invoice_adjustment(self, base_url: str) -> None:
        with allure.step("Выполнение предусловий"):
            tax_invoice_type = "Счет-фактура на начисления"
            inquiry = self.client_request_api.product_sale(inquiry=prepare_inquiries("internet"))

            with allure.step(f"Добавление платежа для ЛС {test_context.client.agreements[0].accounts[0].id}"):
                self.payment_api.create_default_payment(
                    test_context.client.agreements[0].accounts[0].id,
                    inquiry.product.one_time_payment + inquiry.product.subscription_fee + self.balance,
                )
                self.personal_account_api.wait_check_current_main_balance(
                    test_context.client.agreements[0].accounts[0].id, self.balance
                )

            with allure.step(f"Проведение биллинга для ЛС: {test_context.client.agreements[0].accounts[0].id}"):
                self.personal_account_api.wait_accruals(test_context.client.user_id)
                billing_profile_id = self.billing_api.get_billing_profile_id(
                    test_context.client.agreements[0].accounts[0].id
                )
                self.billing_api.run_unscheduled_billing(billing_profile_id)
                self.billing_api.wait_billing(billing_profile_id)
                self.billing_api.wait_finish_billing(billing_profile_id, 3)
                billing_run_id = self.billing_api.get_list_of_bills([billing_profile_id])[0]["billingRun"][
                    "billingProfileBillingRunId"
                ]
                bill_id = self.billing_api.get_list_of_bills([billing_profile_id])[0]["billId"]

            with allure.step("Создание отрицательной корректировки счёта-фактуры"):
                tax_invoice_id = self.billing_api.get_tax_invoice_id(billing_run_id, tax_invoice_type)
                self.adjustment_api.create_adjustment(
                    adjustment_type_id=18,
                    adjustment_reason_id=32,
                    tax_invoice_id=tax_invoice_id,
                    billing_profile_id=billing_profile_id,
                    amount=self.adjustment_sum,
                )
                self.adjustment_api.wait_adjustment_status(test_context.client.agreements[0].accounts[0].id)

            self.client_profile.open(
                f"{base_url}customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
            )
            self.client_profile.locators.CLIENT_FIO.wait_to_be_visible(timeout=20000)

        with allure.step("Перейти на форму 'Финансы' - 'Биллинговые счета'"):
            self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Биллинговые счета")
            self.billing_accounts.locators.SELECTED_TAB_TITLE.wait_to_have_text("Биллинговые счета")
            self.billing_accounts.locators.REFRESH_BTN.click()

        charged, charged_additionally = self.billing_accounts.choose_bill_and_get_charged_charged_additionally()
        tax_invoice_adjusted = self.billing_accounts.get_tax_invoice_adjusted_property()

        with allure.step("Перейти на форму 'Финансы' - 'Корректировки'"):
            self.billing_accounts.click_tab("Корректировки")
            self.adjustments_page.locators.SELECTED_TAB_TITLE.wait_to_have_text("Корректировки")
            self.adjustments_page.check_buttons()
            self.adjustments_page.check_adjustment(
                idx=0,
                adjustment_type="Отрицательная корректировка счёт-фактуры",
                sum_with_tax=self.adjustment_sum,
                status="Одобрено",
                reason="Отрицательная корректировка счёт-фактуры",
            )

        with allure.step("Выбрать необходиму корректировку счета-факуры, нажать кнопку 'Аннулировать'"):
            self.adjustments_page.locators.ADJUSTMENT_TYPE[0].click()
            self.adjustments_page.locators.CANCEL_BTN.wait_to_be_enabled(timeout=15000)
            self.adjustments_page.locators.CANCEL_BTN.click()
            self.adjustments_page.check_cancel_adjustment_form()

        with allure.step("Нажать кнопку 'Отменить'"):
            self.adjustments_page.locators.MODAL_FIRST_BTN.click()
            self.adjustments_page.locators.MODAL.not_to_be_visible()
            self.adjustments_page.check_adjustment(idx=0, status="Одобрено")

        with allure.step("Выбрать необходиму корректировку счета-факуры, нажать кнопку 'Аннулировать'"):
            self.adjustments_page.locators.ADJUSTMENT_TYPE[0].click()
            self.adjustments_page.locators.CANCEL_BTN.wait_to_be_enabled(timeout=15000)
            self.adjustments_page.locators.CANCEL_BTN.click()
            self.adjustments_page.check_cancel_adjustment_form()

        with allure.step("Нажать кнопку 'Аннулировать'"):
            self.adjustments_page.locators.MODAL_SECOND_BTN.click()
            self.adjustments_page.locators.MODAL.not_to_be_visible()
            self.adjustments_page.locators.BALANCE.wait_to_have_text(f"{(self.balance + self.adjustment_sum):.2f}")
            self.adjustments_page.check_adjustment(idx=0, status="Отмена")

        with allure.step("Дождаться выполнения запроса, обновить список корректировок"):
            self.adjustment_api.wait_adjustment_status(
                test_context.client.agreements[0].accounts[0].id, adjustment_status_id=4
            )
            self.adjustments_page.locators.UPDATE_TABLE_BTN.click()
            self.adjustments_page.check_adjustment(idx=0, status="Отменено")
            self.adjustments_page.locators.BALANCE.wait_to_have_text(f"{self.balance:.2f}")

        with allure.step("Перейти на форму 'Финансы' - 'Биллинговые счета', выбрать нужный счет"):
            self.adjustments_page.click_tab("Биллинговые счета")
            self.billing_accounts.locators.SELECTED_TAB_TITLE.wait_to_have_text("Биллинговые счета")
            self.billing_accounts.locators.REFRESH_BTN.click()
            self.billing_accounts.locators.ACCOUNT_NUMS_LIST.wait_to_be_visible()
            self.billing_accounts.locators.ACCOUNT_NUMS_LIST.click(0)

        self.billing_accounts.check_charged_additionally_property(
            bill_id, charged_additionally + self.adjustment_sum, "additionalChargesAmountWithTax", acc_num=0
        )
        self.billing_accounts.check_tax_invoice_adjusted_property(
            tax_invoice_adjusted - self.adjustment_sum, tax_invoice_type="Счет-фактура на начисления"
        )

    @allure.title("Аннулирование корректировки детали счета")
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=367529544",
        name="ПМИ Аннулирование корректировки к ранее выставленным счетам и СФ",
    )
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=367529056",
        name="ПМИ Создание корректировки к ранее выставленным счетам и СФ",
    )
    @allure.id(588393)
    def test_cancel_bill_detail_adjustment(self, base_url: str) -> None:
        with allure.step("Выполнение предусловий"):
            inquiry = self.client_request_api.product_sale(test_context.client, prepare_inquiries("internet"))

            with allure.step(f"Добавление платежа для ЛС {test_context.client.agreements[0].accounts[0].id}"):
                self.payment_api.create_default_payment(
                    test_context.client.agreements[0].accounts[0].id,
                    inquiry.product.one_time_payment + inquiry.product.subscription_fee + self.balance,
                )
                self.personal_account_api.wait_check_current_main_balance(
                    test_context.client.agreements[0].accounts[0].id, self.balance
                )

            with allure.step(f"Проведение биллинга для ЛС: {test_context.client.agreements[0].accounts[0].id}"):
                self.personal_account_api.wait_accruals(test_context.client.user_id)
                billing_profile_id = self.billing_api.get_billing_profile_id(
                    test_context.client.agreements[0].accounts[0].id
                )
                self.billing_api.run_unscheduled_billing(billing_profile_id)
                self.billing_api.wait_billing(billing_profile_id)
                self.billing_api.wait_finish_billing(billing_profile_id, 3)
                bill_id = self.billing_api.get_list_of_bills([billing_profile_id])[0]["billId"]
                bill_detail_value_id = self.billing_api.get_bill_details(bill_id)[0]["billDetailValueId"]

            with allure.step("Создание отрицательной корректировки детали счета"):
                self.adjustment_api.create_adjustment(
                    adjustment_type_id=2,
                    adjustment_reason_id=2,
                    bill_id=bill_id,
                    bill_detail_value_id=bill_detail_value_id,
                    billing_profile_id=billing_profile_id,
                    amount=self.adjustment_sum,
                )
                self.adjustment_api.wait_adjustment_status(test_context.client.agreements[0].accounts[0].id)

            self.client_profile.open(
                f"{base_url}customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
            )
            self.client_profile.locators.CLIENT_FIO.wait_to_be_visible(timeout=20000)

        with allure.step("Перейти на форму 'Финансы' - 'Биллинговые счета'"):
            self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Биллинговые счета")
            self.billing_accounts.locators.SELECTED_TAB_TITLE.wait_to_have_text("Биллинговые счета")
            self.billing_accounts.locators.REFRESH_BTN.click()

        charged, charged_additionally = self.billing_accounts.choose_bill_and_get_charged_charged_additionally()
        already_adjusted = self.billing_accounts.get_detail_adjusted_property()

        with allure.step("Перейти на форму 'Финансы' - 'Корректировки'"):
            self.billing_accounts.click_tab("Корректировки")
            self.adjustments_page.locators.SELECTED_TAB_TITLE.wait_to_have_text("Корректировки")
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
            self.adjustments_page.locators.CANCEL_BTN.wait_to_be_enabled(timeout=15000)
            self.adjustments_page.locators.CANCEL_BTN.click()
            self.adjustments_page.check_cancel_adjustment_form()

        with allure.step("Нажать кнопку 'Аннулировать'"):
            self.adjustments_page.locators.MODAL_SECOND_BTN.click()
            self.adjustments_page.locators.MODAL.not_to_be_visible(timeout=15000)
            self.adjustments_page.locators.BALANCE.wait_to_have_text(f"{(self.balance + self.adjustment_sum):.2f}")
            self.adjustments_page.check_adjustment(idx=0, status="Отмена")

        with allure.step("Дождаться выполнения запроса, обновить список корректировок"):
            self.adjustment_api.wait_adjustment_status(
                test_context.client.agreements[0].accounts[0].id, adjustment_status_id=4
            )
            self.adjustments_page.locators.UPDATE_TABLE_BTN.click()
            self.adjustments_page.check_adjustment(idx=0, status="Отменено")
            self.adjustments_page.locators.BALANCE.wait_to_have_text(f"{self.balance:.2f}")

        with allure.step("Перейти на форму 'Финансы' - 'Биллинговые счета', выбрать нужный счет"):
            self.adjustments_page.click_tab("Биллинговые счета")
            self.billing_accounts.locators.SELECTED_TAB_TITLE.wait_to_have_text("Биллинговые счета")

        self.billing_accounts.check_charged_additionally_property(
            bill_id, charged_additionally + self.adjustment_sum, "additionalChargesAmountWithTax", acc_num=0
        )
        self.billing_accounts.check_detail_adjusted_property(already_adjusted - self.adjustment_sum, accrued=False)
