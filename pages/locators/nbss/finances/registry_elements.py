from pages.locators.nbss.dynamic_form_elements import DynamicElements
from pages.ui_elements import DatePicker, Element, ElementsList


class RegistryElements(DynamicElements):
    """Страница Реестр Платежи /all/payment-search"""

    def __init__(self) -> None:
        super().__init__()

        # КНОПКИ УПРАВЛЕНИЯ
        self.CLIENT_FIO_BTN = Element("(//*[@class='platform-link-content'])[1]", "Кнопка 'ФИО клиента'")
        self.CREATE_PAYMENT_BTN = Element(
            "div.platform-custom-table > div > div:first-child button[variant='primary']",
            "Кнопка 'Создать платеж'",
        )
        self.REFRESH_BTN = Element("//div[contains(@class, 'platform-table')]/div/div[1]/button[1]", "Кнопка 'Обновить'")
        self.CANCEL_PAYMENT_BTN = Element(
            "(//div[contains(@class, 'platform-table')]//button)[4]", "Кнопка 'Аннулировать платёж'"
        )
        self.PAYMENT_SYSTEM_TABS = ElementsList("[class*=tabs-tab-btn]", "Табы 'Платежные системы'")

        # ЗАГОЛОВКИ ТАБЛИЦЫ
        self.PAYMENT_DATES_SORT_BTN = ElementsList(
            "//thead//th[1]/div//div[contains(@class, 'ant-table-column-sorters')]", "Поля 'Дата платежа'"
        )
        self.CHECK_NUM_SEARCH = ElementsList("//thead//th[3]//input", "Поле поиска 'Номер чека'")
        self.DATE_SEARCH_CROSS = Element(
            "thead th:nth-child(1) [class*=picker-clear]", "Кнопка очистки поля поиска 'Дата платежа'"
        )

        # ТАБЛИЦА ПЛАТЕЖЕЙ
        self.PAYMENT_DATES_FIELDS = ElementsList(
            "[class*=table-tbody] [class*=table-row] > div:nth-child(1)", "Поля 'Дата платежа'"
        )
        self.STATUS_FIELDS = ElementsList("[class*=table-tbody] [class*=table-row] > div:nth-child(2)", "Поля 'Статус'")
        self.CHECK_NUM_FIELDS = ElementsList(
            "[class*=table-tbody] [class*=table-row] > div:nth-child(3) span", "Поля 'Номер чека'"
        )
        self.CHECK_SUM_FIELDS = ElementsList(
            "[class*=table-tbody] [class*=table-row] > div:nth-child(4)", "Поля 'Сумма чека'"
        )
        self.PAYMENT_SUM_FIELDS = ElementsList(
            "[class*=table-tbody] [class*=table-row] > div:nth-child(5)", "Поля 'Сумма платежа'"
        )
        self.CASHIER_FIELDS = ElementsList("[class*=table-tbody] [class*=table-row] > div:nth-child(8)", "Поля 'Касса'")
        self.CALENDAR_FIELD = DatePicker("//span[@data-icon='SortDown']/../following-sibling::div", "Поле 'Календарь'")


class RegistryDetailsElements(DynamicElements):
    """Форма с подробной информацией о Платеже в Реестре"""

    def __init__(self) -> None:
        super().__init__()

        self.FORM_TITLE = Element("div[class*=drawer-title] h3", "Заголовок формы")
        self.FORM_TABS = ElementsList("[class*=drawer-body] div[class*=tabs-tab-btn]", "Табы формы")
        self.PAYMENT_DETAILS = ElementsList(
            "[class*=drawer-body] [role*='tabpanel'] > div > div > div:last-child", "Строки детали платежа"
        )
        self.GOAL_TABLE_FIRST_COLUMN = ElementsList(
            "//div[contains(@role, 'tabpanel')]//div[contains(@class, 'table-row')]/div[1]/div/p",
            "Цели элементы первого столбца",
        )
