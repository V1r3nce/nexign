import allure

from common.helpers.time_helpers import delay
from models.context import test_context
from pages.base_page import BasePage
from pages.locators.uniblp_locators.statements_elements import StatementsUniblpElements


class StatementsUniblpPage(BasePage):
    def __init__(self) -> None:
        super().__init__()

        self.locators = StatementsUniblpElements()

    @allure.step("Переход в форму 'Поиск плательщика' и поиск клиента по лицевому счету")
    def search_and_select_payer(self, account_number: int) -> None:
        self.locators.SEARCH_PAYER_BTN.click()
        self.locators.SEARCH_PAYER_TITLE.wait_to_be_visible()
        self.locators.SEARCH_PAYER_TITLE.to_contain_text("Поиск плательщика")

        self.locators.SEARCH_PAYER_ATTR_PERSONAL_ACCOUNT.fill(str(account_number))

        self.locators.SEARCH_PAYER_FIND_BTN.wait_to_be_enabled()
        self.locators.SEARCH_PAYER_FIND_BTN.click()

        self.locators.SEARCH_PAYER_CLIENTS_LIST_ROWS[0].wait_to_be_visible()
        self.locators.SEARCH_PAYER_CLIENTS_LIST_ROWS[0].click()

        delay(2, "Время на прогрузку кнопки")
        self.locators.SEARCH_PAYER_SELECT_CLIENT_BTN.wait_to_be_enabled()
        self.locators.SEARCH_PAYER_SELECT_CLIENT_BTN.click()

    @allure.step("Ручное разнесение счета")
    def manual_post_payment(self, row_index: int, amount: float, remainder_amount: float) -> float:
        self.locators.TARGET_PAYS_TABLE_ROWS[row_index].dblclick()
        self.locators.POST_PAY_AMOUNT_DIALOG_TITLE.wait_to_be_visible()
        self.locators.POST_PAY_AMOUNT_DIALOG_TITLE.to_contain_text("Сумма ручного разнесения")
        self.locators.POST_PAY_AMOUNT_INPUT.fill(str(amount))
        self.locators.POST_PAY_AMOUNT_SAVE_BTN.click()

        self.locators.TARGET_PAYS_REDEMPTION_AMOUNT[row_index].to_contain_text(f"{amount:.2f}")

        new_remainder = remainder_amount - amount
        remainder_str = "0" if new_remainder == 0 else f"{new_remainder:.2f}"
        self.locators.TARGET_PAYS_REMAINDER_AMOUNT.to_contain_text(
            f"Остаток платежа, подлежащий авторазнесению: {remainder_str}"
        )
        return new_remainder

    @allure.step("Проверка параметров клиента после выбора клиента")
    def verify_client_info_after_selection(self) -> None:
        self.locators.PAYMENT_PERSONAL_ACCOUNT[0].to_contain_text(
            f"{test_context.client.agreements[0].accounts[0].number}"
        )
        self.locators.PAYMENT_CLIENT_NAME[0].to_contain_text(f"{test_context.client.customer_name}")
        self.locators.CLIENT_HEADER.to_contain_text("Клиент")
        self.locators.CLIENT_NAME.to_contain_text(f"{test_context.client.customer_name}")
        self.locators.PERSONAL_ACCOUNT.to_contain_text(f"{test_context.client.agreements[0].accounts[0].number}")
        self.locators.CONTRACT_NUMBER.to_contain_text(f"{test_context.client.agreements[0].number}")
        self.locators.INN.to_contain_text(f"{test_context.client.inn}")
        self.locators.KPP.to_contain_text(f"{test_context.client.kpp}")
        self.locators.SETTLEMENT_ACCOUNT.to_contain_text(f"{test_context.client.bank_account}")
        self.locators.CLIENT_TYPE.to_contain_text("Биллинговый")

    @allure.step("Сохранение платежа и проверка полей")
    def save_payment_and_verify_fields(self) -> None:
        self.locators.PAYMENTS_SAVE_BTN.click()
        self.locators.STATEMENT_DOCUMENTS_TITLE.wait_to_be_visible()
        self.locators.STATEMENT_DOCUMENTS_TABLE[0].wait_to_be_visible()
        self.locators.PAYMENTS_COLUMN_BILLING_SYSTEM[0].to_contain_text("Nexign")
        self.locators.PAYMENTS_COLUMN_CLIENT_NAME[0].to_contain_text(test_context.client.customer_name)
        self.locators.PAYMENTS_COLUMN_PERSONAL_ACCOUNT[0].to_contain_text(
            f"{test_context.client.agreements[0].accounts[0].number}"
        )
        self.locators.PAYMENTS_COLUMN_INN[0].to_contain_text(f"{test_context.client.inn}")

    @allure.step("Сохранение целеуказаний по разнесению платежа")
    def save_target_pays(self) -> None:
        self.locators.TARGET_PAYS_SAVE_BTN.click()
        self.locators.TARGET_PAYS_MESSAGE.wait_to_be_visible()
        self.locators.TARGET_PAYS_MESSAGE.to_contain_text("Целеуказания по разнесению платежа сохранены!")
        self.locators.TARGET_PAYS_CLOSE_BTN.click()

    @allure.step("Сохранение документа в биллинг")
    def save_document_to_billing(self) -> None:
        self.locators.STATEMENT_DOCUMENTS_CHECKBOX[0].click()
        delay(2, "Время на прогрузку кнопки")
        self.locators.SAVE_TO_BILLING_BTN.click()
        self.locators.SAVE_TO_BILLING_DIALOG_TITLE.wait_to_be_visible()
        self.locators.SAVE_TO_BILLING_DIALOG_TITLE.to_contain_text("Подготовлено к сохранению в биллинг")
        self.locators.SAVE_TO_BILLING_DOCUMENTS_COUNT.to_contain_text("Количество документов:  1")
        self.locators.SAVE_TO_BILLING_ERRORS_COUNT.to_contain_text("Количество ошибок:  0")
        self.locators.SAVE_TO_BILLING_CLOSE_BTN.click()
