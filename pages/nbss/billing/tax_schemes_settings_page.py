import allure

from pages.base_page import BasePage
from pages.locators.nbss.billing.tax_schemes_settings_elements import TaxSchemesSettingsElements


class TaxSchemesSettingsPage(BasePage):
    """Страница Схемы налогообложения"""

    def __init__(self) -> None:
        super().__init__()

        self.locators = TaxSchemesSettingsElements()

    @allure.step("Добавить исключение на новой схеме налогообложения")
    def add_exception_on_tax_scheme(self) -> None:
        with allure.step("Перейти в таб Исключения > Форму добавления исключения"):
            self.locators.TAB_EXCEPTION.click()
            self.locators.ADD_EXCEPTION_BUTTON.click()
        with allure.step("Заполнить обязательные поля на форме добавления исключения"):
            self.locators.BILLING_DETAIL.select_by_index(0)
            self.locators.REDEFINED_SCHEME.select_by_value("Схема налогообложения по умолчанию")
            self.locators.DETAIL_TAX_SCHEME_ROW.wait_to_be_visible(timeout=15000)
        with allure.step("Сохранить изменения > Перейти в форму создания новой схемы налогообложения"):
            self.locators.ACCEPT_EXCEPTION_BUTTON.click()
            self.locators.ACCEPT_EXCEPTION_BUTTON.not_to_be_visible(timeout=15000)
            self.locators.EXCEPTION_ROW.wait_to_be_visible(timeout=15000)
            self.locators.INNER_ACCEPT_BTN.wait_to_be_enabled()

    def fill_tax_form(self, name_ru: str, name_en: str) -> None:
        self.locators.ADD_TAX_BUTTON.wait_to_be_enabled(timeout=15000)
        self.locators.ADD_TAX_BUTTON.click()
        self.locators.NAME_TAX_SCHEME[0].wait_to_be_enabled(timeout=15000)
        self.locators.NAME_TAX_SCHEME[0].fill(name_ru)
        self.locators.NAME_TAX_SCHEME[1].fill(name_en)

    @allure.step("Создать налоговую схему")
    def tax_scheme_creation(self, name_ru: str, name_en: str) -> None:
        self.locators.ADD_TAX_BUTTON.wait_to_be_enabled(timeout=15000)
        self.locators.TAB_TAX_SCHEME.click()
        self.fill_tax_form(name_ru=name_ru, name_en=name_en)
        self.add_exception_on_tax_scheme()
