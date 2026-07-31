import re
from dataclasses import dataclass

import allure

from pages.base_page import BasePage
from pages.locators.nbss.dynamic_form_elements import CancelPaymentForm, DynamicForms
from pages.locators.nbss.finances.payments_elements import PaymentElements
from pages.locators.nbss.finances.registry_elements import RegistryElements


@dataclass
class PaymentsPage(BasePage):
    def __init__(self) -> None:
        super().__init__()
        self.base_page = BasePage()
        self.registry_elements = RegistryElements()
        self.payment_elements = PaymentElements()
        self.dynamic_forms = DynamicForms()
        self.payments_annul_form = CancelPaymentForm()

    @allure.step("Проверить, поля 'Со счёта'")
    def check_from_account_fields(
        self,
        account_number: str,
        user_name: str,
        account_type: str,
        chosen_reason: str,
        comment: str,
        account_sum: str,
        relocate_sum: str,
        available_after_transfer: str,
    ) -> None:
        self.payment_elements.ACCOUNT_DATA_BLOCKS[0].to_contain_text(account_number)
        self.payment_elements.ACCOUNT_DATA_BLOCKS[2].to_contain_text(user_name)
        self.payment_elements.ACCOUNT_DATA_BLOCKS[4].to_contain_text(account_type)
        self.payment_elements.CHOSEN_DONOR_ADJUSTMENT_REASON.wait_to_have_text(chosen_reason)
        self.payment_elements.FROM_ACCOUNT_COMMENT.wait_to_have_text(comment)
        self.payment_elements.ACCOUNT_DATA_BLOCKS[10].wait_to_have_text(re.compile(account_sum))
        self.payment_elements.RELOCATE_SUM_INPUT.to_have_value(relocate_sum)
        self.payment_elements.ACCOUNT_DATA_BLOCKS[14].wait_to_have_text(re.compile(available_after_transfer))

    @allure.step("Проверить, поля 'На счёт'")
    def check_to_account_fields(
        self,
        account_number: str,
        user_name: str,
        account_type: str,
        chosen_reason: str,
        comment: str,
        current_balance: str,
        added_sum: str,
        final_balance: str,
    ) -> None:
        self.payment_elements.PERSONAL_ACCOUNT_INPUT.to_have_value(account_number)
        self.payment_elements.ACCOUNT_DATA_BLOCKS[3].wait_to_have_text(user_name)
        self.payment_elements.ACCOUNT_DATA_BLOCKS[5].wait_to_have_text(account_type)
        self.payment_elements.CHOSEN_RECIPIENT_ADJUSTMENT_REASON.wait_to_have_text(chosen_reason)
        self.payment_elements.TO_ACCOUNT_COMMENT.wait_to_have_text(comment)
        self.payment_elements.ACCOUNT_DATA_BLOCKS[11].wait_to_have_text(re.compile(current_balance))
        self.payment_elements.ACCOUNT_DATA_BLOCKS[13].wait_to_have_text(re.compile(added_sum))
        self.payment_elements.ACCOUNT_DATA_BLOCKS[15].wait_to_have_text(re.compile(final_balance))

    @allure.step("Заполнение параметров переноса баланса и его перенос")
    def transfer_monetary_balance(self, recipient_account_number: int, transfer_amount: int) -> None:
        with allure.step("Открытие формы"):
            self.payment_elements.BALANCE_TRANSFER_BTN.wait_to_be_enabled()
            self.payment_elements.BALANCE_TRANSFER_BTN.click()
        with allure.step("Заполнение параметров перевода"):
            self.payment_elements.PERSONAL_ACCOUNT_SELECTOR.wait_to_be_visible()
            self.payment_elements.PERSONAL_ACCOUNT_SELECTOR.click()
            self.payment_elements.PERSONAL_ACCOUNT_TO_SEARCH.fill(recipient_account_number)
            self.payment_elements.PERSONAL_ACCOUNT_SEARCH_BTN.click()
            self.dynamic_forms.INNER_ACCEPT_BTN.wait_to_be_enabled()
            self.dynamic_forms.INNER_ACCEPT_BTN.click()
            self.payment_elements.DONOR_ADJUSTMENT_REASON.select_by_index(0)
            self.payment_elements.RECIPIENT_ADJUSTMENT_REASON.select_by_index(0)
            self.payment_elements.BALANCE_TO_TRANSFER.fill(str(transfer_amount))
        with allure.step("Перенос"):
            self.payment_elements.BALANCE_TRANSFER_ACCEPT_BTN.wait_to_be_enabled(timeout=15000)
            self.payment_elements.BALANCE_TRANSFER_ACCEPT_BTN.click()

    @allure.step("Заполнение периода дат в календаре на странице реестра платежей")
    def fill_registry_date(self, start_date: str, end_date: str) -> None:
        self.registry_elements.CALENDAR_FIELD.fill_calendar_dates_period(start_date, end_date)

    @allure.step("Заполнение формы 'Аннулирование платежа'")
    def fill_annul_form(self) -> None:
        self.payment_elements.CANCEL_PAYMENT_BTN.click()
        self.payments_annul_form.CANCEL_REASON_INPUT.wait_to_be_visible()
        self.payments_annul_form.CANCEL_REASON_INPUT.fill("test")
        self.payments_annul_form.INNER_ACCEPT_BTN.wait_to_be_enabled()
        self.payments_annul_form.INNER_ACCEPT_BTN.click()
