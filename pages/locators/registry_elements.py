from playwright.sync_api import Page

from pages.locators.dynamic_form_elements import DynamicElements
from pages.ui_elements import Element, ElementsList


class RegistryElements(DynamicElements):
    """Страница Реестр Платежи /all/payment-search"""

    def __init__(self, page: Page):
        super().__init__(page)

        # КНОПКИ УПРАВЛЕНИЯ
        self.CLIENT_FIO_BTN = Element("(//*[@class='platform-link-content'])[1]", "Кнопка 'ФИО клиента'", self.page)
        self.CREATE_PAYMENT_BTN = Element(
            "div.platform-custom-table > div > div:first-child button[variant='primary']",
            "Кнопка 'Создать платеж'",
            self.page,
        )
        self.REFRESH_BTN = Element(
            "//div[contains(@class, 'platform-custom-table')]/div/div[1]/button[1]", "Кнопка 'Обновить'", self.page
        )
        self.CANCEL_PAYMENT_BTN = Element(
            "(//div[contains(@class, 'platform-custom-table')]//button)[4]", "Кнопка 'Аннулировать платёж'", self.page
        )
        self.PAYMENT_SYSTEM_TABS = ElementsList("[class*=tabs-tab-btn]", "Табы 'Платежные системы'", self.page)

        # ЗАГОЛОВКИ ТАБЛИЦЫ
        self.PAYMENT_DATES_SORT_BTN = ElementsList(
            "//thead//th[1]/div//div[contains(@class, 'ant-table-column-sorters')]", "Поля 'Дата платежа'", self.page
        )
        self.CHECK_NUM_SEARCH = ElementsList("//thead//th[3]//input", "Поле поиска 'Номер чека'", self.page)
        self.DATE_SEARCH_CROSS = Element(
            "thead th:nth-child(1) [class*=picker-clear]", "Кнопка очистки поля поиска 'Дата платежа'", self.page
        )

        # ТАБЛИЦА ПЛАТЕЖЕЙ
        self.PAYMENT_DATES_FIELDS = ElementsList("//tbody/tr/td[1]", "Поля 'Дата платежа'", self.page)
        self.STATUS_FIELDS = ElementsList("//tbody/tr/td[2]", "Поля 'Статус'", self.page)
        self.CHECK_NUM_FIELDS = ElementsList("//tbody/tr/td[3]/span", "Поля 'Номер чека'", self.page)
        self.CHECK_SUM_FIELDS = ElementsList("//tbody/tr/td[4]", "Поля 'Сумма чека'", self.page)
        self.PAYMENT_SUM_FIELDS = ElementsList("//tbody/tr/td[5]", "Поля 'Сумма платежа'", self.page)
        self.CASHIER_FIELDS = ElementsList("//tbody/tr/td[8]", "Поля 'Касса'", self.page)


class RegistryDetailsElements(DynamicElements):
    """Форма с подробной информацией о Платеже в Реестре"""

    def __init__(self, page: Page):
        super().__init__(page)

        self.FORM_TITLE = Element("div.ant-drawer-title h3", "Заголовок формы", self.page)
        self.FORM_TABS = ElementsList("[class*=drawer-body] div[class*=tabs-tab-btn]", "Табы формы", self.page)
        self.PAYMENT_DETAILS = ElementsList(
            "[class*=drawer-body] [role*='tabpanel'] > div > div > div:last-child", "Строки детали платежа", self.page
        )
        self.GOAL_TABLE_FIRST_COLUMN = ElementsList(
            "//*[contains(@class, 'drawer-body')]//div[contains(@role, 'tabpanel')]//tbody/tr/td[1]/div/p",
            "Цели элементы первого столбца",
            self.page,
        )
