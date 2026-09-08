import allure

from pages.base_page import BasePage
from pages.locators.nbss.dynamic_form_elements import CreateSalesAndServiceManagement


class CreateSalesFormPage(BasePage):
    """Форма 'Создание продажи и управление услугами'"""

    def __init__(self) -> None:
        super().__init__()

        self.locators = CreateSalesAndServiceManagement()

    @allure.step(
        "Проверить, что форма продажи содержит данные абонента: договор {agreement_number}, ЛС {account_number}"
    )
    def check_context(self, agreement_number: str, account_number: str) -> None:
        self.locators.TITLE.wait_to_be_visible(timeout=10000)
        self.locators.SELECTED_AGREEMENT.to_contain_text(agreement_number, timeout_sec=20)
        self.locators.SALE_ACCOUNT.to_contain_text(account_number, timeout_sec=20)

    @allure.step("Закрыть форму создания продажи без сохранения")
    def close_without_saving(self) -> None:
        self.locators.CANCEL_BTN.wait_to_be_visible()
        self.locators.CANCEL_BTN.click()
        self.locators.MODAL_SECOND_BTN.wait_to_be_visible()
        self.locators.MODAL_SECOND_BTN.click()
        self.locators.TITLE.not_to_be_visible()
