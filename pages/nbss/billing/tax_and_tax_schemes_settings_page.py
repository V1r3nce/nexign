import allure

from pages.base_page import BasePage
from pages.locators.nbss.billing.tax_and_tax_schemes_settings_elements import TaxAndTaxSchemesSettingsElements


class TaxAndTaxSchemesSettingsPage(BasePage):
    """Страница Схемы налогообложения"""

    def __init__(self) -> None:
        super().__init__()

        self.locators = TaxAndTaxSchemesSettingsElements()

    @allure.step("Добавить исключение на новой схеме налогообложения")
    def add_exception_on_tax_scheme(self) -> None:
        with allure.step("Перейти в таб Исключения > Форму добавления исключения"):
            self.locators.TAB_EXCEPTION.click()
            self.locators.ADD_EXCEPTION_BUTTON.wait_to_be_visible()
            self.locators.ADD_EXCEPTION_BUTTON.click()
        with allure.step("Заполнить обязательные поля на форме добавления исключения"):
            self.locators.BILLING_DETAIL.wait_to_be_visible()
            self.locators.BILLING_DETAIL.select_by_index(0)
            self.locators.REDEFINED_SCHEME.select_by_value("Схема налогообложения по умолчанию")
            self.locators.DETAIL_TAX_SCHEME_ROW.wait_to_be_visible(timeout=15000)
        with allure.step("Сохранить изменения > Перейти в форму создания новой схемы налогообложения"):
            self.locators.INNER_ACCEPT_BTN.wait_to_be_visible()
            self.locators.INNER_ACCEPT_BTN.click()
            self.locators.EXCEPTION_ROW.wait_to_be_visible(timeout=20000)
            self.locators.INNER_ACCEPT_BTN.wait_to_be_enabled()

    @allure.step("Заполнить форму создания налога")
    def fill_tax_form(self, name_ru: str, name_en: str, tax_rate: int | None = None) -> None:
        """
        Заполняет поля наименования (ru / en) на форме создания налога или схемы налогообложения.
        На форме создания налога также заполняет ставку налога.

        :param name_ru: Наименование на русском языке
        :param name_en: Наименование на английском языке
        :param tax_rate: Ставка налога (для формы создания налога)
        """
        self.locators.ADD_TAX_BUTTON.wait_to_be_enabled(timeout=15000)
        self.locators.ADD_TAX_BUTTON.click()
        self.locators.TAX_NAME[0].wait_to_be_enabled(timeout=15000)
        self.locators.TAX_NAME[0].fill(name_ru)
        self.locators.TAX_NAME[1].fill(name_en)
        if tax_rate:
            self.locators.TAX_RATE.fill(str(tax_rate))

    @allure.step("Создать налоговую схему")
    def tax_scheme_creation(
        self, name_ru: str, name_en: str, tax_name_ru: str | None = None, add_exception: bool = False
    ) -> None:
        self.locators.ADD_TAX_BUTTON.wait_to_be_enabled(timeout=15000)
        self.locators.TAX_SCHEMES_TAB.click()
        self.fill_tax_form(name_ru=name_ru, name_en=name_en)
        if tax_name_ru:
            self.add_tax_to_scheme(tax_name_ru)
            self.locators.TAX_SCHEMES_ADVANCES_TAB.wait_to_be_enabled(timeout=15000)
            self.locators.TAX_SCHEMES_ADVANCES_TAB.click()
            self.add_tax_to_scheme(tax_name_ru)
            self.locators.MAKE_TAX_SCHEME_INVISIBLE.wait_to_be_visible(timeout=15000)
            self.locators.MAKE_TAX_SCHEME_INVISIBLE.click()
            self.locators.ACCEPT_BTN.click()
        if add_exception:
            self.add_exception_on_tax_scheme()

    @allure.step("Создать налог")
    def tax_creation(self, tax_name_ru: str, tax_name_en: str, tax_rate: int, start_date: str | None = None) -> None:
        self.fill_tax_form(name_ru=tax_name_ru, name_en=tax_name_en, tax_rate=tax_rate)
        if start_date:
            self.locators.START_DATE_SELECTION.fill(start_date)
        self.locators.INNER_ACCEPT_BTN.click()
        self.locators.TAX_CREATION_TITLE.not_to_be_visible(timeout=15000)

    @allure.step("Добавить налог {0} в налоговую схему")
    def add_tax_to_scheme(self, name: str) -> None:
        self.locators.ADD_TAX_TO_SCHEME.wait_to_be_enabled(timeout=15000)
        self.locators.ADD_TAX_TO_SCHEME.click()
        self.locators.TAX_SELECT_FIELD.wait_to_be_enabled(timeout=15000)
        self.locators.TAX_SELECT_FIELD.select_by_value(name)
        self.locators.ADD_TAX_ACCEPT_BTN[1].click()
        self.locators.TAX_SELECT_FIELD.not_to_be_visible(timeout=15000)

    def open_tax_scheme_version(self, scheme_name: str, version: str) -> None:
        self.locators.REFRESH_BTN.click()
        self.locators.TAX_SCHEMES.wait_to_be_visible(timeout=10000)
        self.locators.TAX_SCHEMES.select_by_value(scheme_name)
        self.locators.TAX_SCHEME_VERSIONS.click_by_text(version)

    def check_tax_scheme_version(
        self,
        version: str | None = None,
        status: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        scheme_name: str | None = None,
        check_charges_tab: bool = False,
        check_copy_button: bool = False,
    ) -> None:
        if version:
            self.locators.VERSION_NAME.to_contain_text_in_any(version)
        if status:
            self.locators.VERSION_STATUS.to_contain_text_in_any(status)
        if start_date:
            self.locators.TAX_DATES.to_contain_text_in_any(start_date)
        if end_date:
            self.locators.TAX_DATES.to_contain_text_in_any(end_date)
        if scheme_name:
            self.locators.VERSION_NAME.to_contain_text_in_any(scheme_name)
        if check_charges_tab:
            self.locators.TAX_SCHEMES_CHARGES_TAB.click()
            self.locators.TAX_SCHEMES_ADVANCES_TAB.wait_to_be_visible()
        if check_copy_button:
            self.locators.COPY_BUTTON.wait_to_be_visible()
