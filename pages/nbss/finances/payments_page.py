import re
from dataclasses import dataclass

import allure
from playwright.sync_api import Page

from pages.base_page import BasePage
from pages.locators.nbss.finances.payments_elements import PaymentElements


@dataclass
class PaymentsPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.locators = PaymentElements(page)

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
        self.locators.ACCOUNT_DATA_BLOCKS[0].to_contain_text(account_number)
        self.locators.ACCOUNT_DATA_BLOCKS[2].to_contain_text(user_name)
        self.locators.ACCOUNT_DATA_BLOCKS[4].to_contain_text(account_type)
        self.locators.CHOSEN_DONOR_ADJUSTMENT_REASON.wait_to_have_text(chosen_reason)
        self.locators.FROM_ACCOUNT_COMMENT.wait_to_have_text(comment)
        self.locators.ACCOUNT_DATA_BLOCKS[10].wait_to_have_text(re.compile(account_sum))
        self.locators.RELOCATE_SUM_INPUT.to_have_value(relocate_sum)
        self.locators.ACCOUNT_DATA_BLOCKS[14].wait_to_have_text(re.compile(available_after_transfer))

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
        self.locators.PERSONAL_ACCOUNT_INPUT.to_have_value(account_number)
        self.locators.ACCOUNT_DATA_BLOCKS[3].wait_to_have_text(user_name)
        self.locators.ACCOUNT_DATA_BLOCKS[5].wait_to_have_text(account_type)
        self.locators.CHOSEN_RECIPIENT_ADJUSTMENT_REASON.wait_to_have_text(chosen_reason)
        self.locators.TO_ACCOUNT_COMMENT.wait_to_have_text(comment)
        self.locators.ACCOUNT_DATA_BLOCKS[11].wait_to_have_text(re.compile(current_balance))
        self.locators.ACCOUNT_DATA_BLOCKS[13].wait_to_have_text(re.compile(added_sum))
        self.locators.ACCOUNT_DATA_BLOCKS[15].wait_to_have_text(re.compile(final_balance))

    @allure.step("Заполнение параметров переноса баланса и его перенос")
    def transfer_monetary_balance(self, recipient_account_number: int, transfer_amount: int) -> None:
        with allure.step("Открытие формы"):
            self.locators.BALANCE_TRANSFER_BTN.wait_to_be_enabled()
            self.locators.BALANCE_TRANSFER_BTN.click()
        with allure.step("Заполнение параметров перевода"):
            self.locators.PERSONAL_ACCOUNT_SELECTOR.wait_to_be_visible()
            self.locators.PERSONAL_ACCOUNT_SELECTOR.click()
            self.locators.PERSONAL_ACCOUNT_TO_SEARCH.fill(recipient_account_number)
            self.locators.PERSONAL_ACCOUNT_SEARCH_BTN.click()
            self.locators.PERSONAL_ACCOUNT_CHOOSE_BTN.wait_to_be_enabled()
            self.locators.PERSONAL_ACCOUNT_CHOOSE_BTN.click()
            self.locators.DONOR_ADJUSTMENT_REASON.select_by_index(0)
            self.locators.RECIPIENT_ADJUSTMENT_REASON.select_by_index(0)
            self.locators.BALANCE_TO_TRANSFER.fill(str(transfer_amount))
        with allure.step("Перенос"):
            self.locators.TRANSFER_ACCEPT.click()
