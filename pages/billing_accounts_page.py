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

    @allure.step("Выбрать нужный счет, запомнить значения полей 'Начислено' и 'Доначислено'")
    def choose_bill_and_get_charged_charged_additionally(self, bill_index: int = 0) -> tuple[float, float]:
        self.locators.ACCOUNT_NUMS_LIST.wait_to_be_visible()
        self.locators.ACCOUNT_NUMS_LIST.click(bill_index)
        self.locators.BILLING_PROPERTIES.wait_for_text_in_all(["Начислено"])
        property_index = self.locators.BILLING_PROPERTIES.text_list.index("Начислено")
        charged = float(self.locators.BILLING_PROPERTY_VALUES[property_index].text)
        self.locators.BILLING_PROPERTIES.wait_for_text_in_all(["Доначислено"])
        property_index = self.locators.BILLING_PROPERTIES.text_list.index("Доначислено")
        charged_additionally = float(self.locators.BILLING_PROPERTY_VALUES[property_index].text)
        return charged, charged_additionally

    @allure.step("Перейти на вкладку 'Детали', запомнить значение поля 'Откорректированно'")
    def get_detail_adjusted_property(self) -> float:
        self.locators.DETAILS_TAB.click()
        self.locators.DETAIL.wait_to_be_visible()
        return float(self.locators.DETAIL_ADJUSTED[0].text)

    @allure.step("Перейти на вкладку 'Счета-фактуры', запомнить значение поля 'Откорректированно'")
    def get_tax_invoice_adjusted_property(self, tax_invoice_type: str = "Счет-фактура на начисления") -> float:
        self.locators.INVOICES_TAB.click()
        self.locators.INVOICE.wait_to_be_visible()
        self.locators.INVOICE_TYPE.wait_for_text_in_all([tax_invoice_type])
        tax_invoice_index = self.locators.INVOICE_TYPE.text_list.index(tax_invoice_type)
        return float(self.locators.INVOICE_ADJUSTED[tax_invoice_index].text)

    @allure.step("Проверить отображение суммы корректировки на вкладке 'Свойства'")
    def check_charged_additionally_property(self, amount: float) -> None:
        self.locators.BILLING_PROPERTIES.wait_for_text_in_all(["Доначислено"])
        property_index = self.locators.BILLING_PROPERTIES.text_list.index("Доначислено")
        self.locators.BILLING_PROPERTY_VALUES[property_index].wait_to_have_text(f"{amount:.2f}")

    @allure.step("Перейти на вкладку 'Детали', проверить что сумма корректировки учтена")
    def check_detail_adjusted_property(self, amount: float) -> None:
        self.locators.DETAILS_TAB.click()
        self.locators.DETAIL.wait_to_be_visible()
        self.locators.DETAIL_ADJUSTED[0].wait_to_have_text(f"{amount:.2f}")

    @allure.step("Перейти на вкладку 'Счета-фактуры', проверить что сумма корректировки учтена")
    def check_tax_invoice_adjusted_property(
        self,
        amount: float,
        tax_invoice_type: str = "Счет-фактура на начисления",
    ) -> None:
        self.locators.INVOICES_TAB.click()
        self.locators.INVOICE.wait_to_be_visible()
        self.locators.INVOICE_TYPE.wait_for_text_in_all([tax_invoice_type])
        tax_invoice_index = self.locators.INVOICE_TYPE.text_list.index(tax_invoice_type)
        self.locators.INVOICE_ADJUSTED[tax_invoice_index].wait_to_have_text(f"{amount:.2f}")
