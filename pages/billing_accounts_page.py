import allure
from playwright.sync_api import Page

from pages.base_page import BasePage
from pages.locators.billing_accounts import BillingAccounts


class BillingAccountsPage(BasePage):
    """Страница /bills/{account_num}/properties Биллинговые счета"""

    def __init__(self, page: Page):
        super().__init__(page)
        self.locators = BillingAccounts(page)

    @allure.step("Проверка свойств биллинга")
    def check_billing_properties(self) -> None:
        self.locators.BILLING_PROPERTIES.wait_elements_visible(17)
        self.locators.BILLING_PROPERTIES[0].to_contain_text("Срок оплаты")
        self.locators.BILLING_PROPERTIES[1].to_contain_text("Период")
        self.locators.BILLING_PROPERTIES[2].to_contain_text("Задолженность")
        self.locators.BILLING_PROPERTIES[3].to_contain_text("Связанные заявки")
        self.locators.BILLING_PROPERTIES[4].to_contain_text("Реструктуризация")
        self.locators.BILLING_PROPERTIES[5].to_contain_text("Входной баланс")
        self.locators.BILLING_PROPERTIES[6].to_contain_text("Выходной баланс")
        self.locators.BILLING_PROPERTIES[7].to_contain_text("Начислено")
        self.locators.BILLING_PROPERTIES[8].to_contain_text("Оплачено")
        self.locators.BILLING_PROPERTIES[9].to_contain_text("Доначислено")
        self.locators.BILLING_PROPERTIES[10].to_contain_text("Учтено начислений")
        self.locators.BILLING_PROPERTIES[11].to_contain_text("Учтено корректировок платежей")
        self.locators.BILLING_PROPERTIES[12].to_contain_text("Учтено корректировок начислений")
        self.locators.BILLING_PROPERTIES[13].to_contain_text("Сумма биллинговой скидки")
        self.locators.BILLING_PROPERTIES[14].to_contain_text("Авансовый платеж")
        self.locators.BILLING_PROPERTIES[15].to_contain_text("Списано")
        self.locators.BILLING_PROPERTIES[16].to_contain_text("Комплект документов")
        self.locators.BILLING_PROPERTIES[17].to_contain_text("Дата генерации")
