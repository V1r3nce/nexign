from playwright.sync_api import Page

from pages.locators.dynamic_form_elements import DynamicForms
from pages.ui_elements import CheckboxBlock, DatePicker, Dropdown, Element, ElementsList, RadioOrCheckboxBlock, Select


class Adjustments(DynamicForms):
    """Страница 'Корректировки'"""

    def __init__(self, page: Page):
        super().__init__(page)

        # Основная форма
        self.CURRENCY = Element("//h3[text() = 'RUB']", "RUB", self.page)
        self.BALANCE = Element(
            "//*[contains(@class, 'platform-scrollable')] //div[2] //h3[@color='positive' or @color='negative']",
            "Баланс лицевого счета",
            self.page,
        )

        # BUTTONS
        self.ADD_ADJUSTMENT_BTN = Dropdown(
            "[id*=panel-adjustments] button[class*=dropdown-trigger]:has([data-icon=ArrowDropDown])",
            "Добавить корректировку",
            self.page,
        )
        self.UPDATE_TABLE_BTN = Element(
            "[id*=panel-adjustments] button:has([data-icon=Refresh])", "Кнопка 'Обновить'", self.page
        )
        self.CANCEL_BTN = Element(
            "(//*[contains(@class, 'platform-table')] //button)[4]",
            "Кнопка 'Аннулировать'",
            self.page,
        )
        self.OPEN_BILLING_FORM = Element(
            "(//div[contains(@class, 'platform-table')] //button)[6]", "Кнопка 'Провести биллинг'", self.page
        )
        self.EXPORT_TO_XLS_BTN = Element(
            "(//*[contains(@class, 'platform-table')] //button)[7]",
            "Кнопка 'Экспортировать найденные записи в XLS файл'",
            self.page,
        )
        self.SETTING_BTN = Element(
            "[id*=panel-adjustments] button:has([data-icon=Settings])", "Кнопка 'Настройка'", self.page
        )
        self.COLUMN_LIST = CheckboxBlock("[class*=dropdown-placement-bottomRight]", "Список колонок таблицы", self.page)

        # ADJUSTMENTS
        self.ADJUSTMENT_TITLE = ElementsList(
            "table tr>th>div:first-child", "Заголовки таблицы 'Корректировки'", self.page
        )
        self.ADJUSTMENTS = ElementsList("//*[contains(@class, 'table-tbody')] //tr", "Корректировка", self.page)
        self.ADJUSTMENT_ID = ElementsList("//*[contains(@class, 'table-tbody')] //td[1]", "ID", self.page)
        self.INCLUDED_IN_BILL = ElementsList("//*[contains(@class, 'table-tbody')] //td[2]", "Учтено в счете", self.page)
        self.ADJUSTMENT_TYPE = ElementsList("//*[contains(@class, 'table-tbody')] //td[3]", "Тип", self.page)
        self.ADJUSTMENT_DATE = ElementsList("//td //a", "Дата", self.page)
        self.SUM_WITH_TAX = ElementsList(
            "//*[contains(@class, 'table-tbody')] //td[5]", "Сумма с учётом налога", self.page
        )
        self.TAX = ElementsList("//*[contains(@class, 'table-tbody')] //td[6]", "Налог", self.page)
        self.STATUS = ElementsList("//*[contains(@class, 'table-tbody')] //td[7]", "Статус", self.page)
        self.REASON = ElementsList("//*[contains(@class, 'table-tbody')] //td[8]", "Причина", self.page)
        self.TARGET_TYPE = ElementsList("//*[contains(@class, 'table-tbody')] //td[9]", "Целевой тип счёта", self.page)
        self.TARGET = ElementsList("//*[contains(@class, 'table-tbody')] //td[10]", "Цель", self.page)
        self.DOCUMENT_NUMBER = ElementsList(
            "//*[contains(@class, 'table-tbody')] //td[11]", "Номер документа основания", self.page
        )
        self.DOCUMENT_DATE = ElementsList(
            "//*[contains(@class, 'table-tbody')] //td[12]", "Дата докумнта основания", self.page
        )
        self.TRANSFERRED = ElementsList("//*[contains(@class, 'table-tbody')] //td[13]", "Перенесено", self.page)
        self.ADVANCE = ElementsList("//*[contains(@class, 'table-tbody')] //td[14]", "Аванс", self.page)

        self.LOADER_SPIN = Element("(//div[contains(@class, '-spin-spinning')]/span)[1]", "Загрузка", self.page)

        # Форма Биллинг по корректировкам
        self.BILLING_TITLE = Element(".ant-drawer-header-title h3", "Биллинг по корректировкам", self.page)
        self.START_BILLING = Element("[class*=-drawer-footer] button[class*=btn-primary]", "Провести биллинг", self.page)
        self.UPDATE_BILLING_TABLE_BUTTON = Element("[class*=drawer-body] [data-icon=Refresh]", "Обновить", self.page)
        self.SWITCH_ONLY_SELECTED = Element("button[role='switch']", "Только выбранные", self.page)
        self.SWITCH_ONLY_SELECTED_TEXT = Element(
            "(//div[contains(@class, '-drawer-body')]//div[contains(@class, 'platform-table')]//p)[1]",
            "Только выбранные",
            self.page,
        )
        self.BILLING_TABLE_HEADERS = ElementsList(
            "[class*=-drawer-body] th div[class*=column-title]",
            "Заголовки таблицы 'Биллинг по корректировкам'",
            self.page,
        )
        self.ADJUSTMENT_CHECKBOX = ElementsList(
            "//div[contains(@class, '-drawer-body')]//tr/td[1]", "Чекбокс для выбора корректировки", self.page
        )
        self.BILLING_ADJUSTMENTS = ElementsList(
            "//div[contains(@class, '-drawer-body')]//div[contains(@class, 'table-tbody')]/tr",
            "Корректировки на форме Биллинг по корректировкам",
            self.page,
        )

        # Таблица
        self.ROWS_BILLING = ElementsList(
            "[class*='drawer-body'] tr[class*=table-row]", "Строки таблицы 'Биллинг по корректировкам'", self.page
        )
        self.INCLUDED_IN_BILL_BILLING = ElementsList(
            "//div[contains(@class, '-drawer-body')]//td[3]", "Учтено в счете", self.page
        )
        self.ADJUSTMENT_TYPE_BILLING = ElementsList("//div[contains(@class, '-drawer-body')]//td[4]", "Тип", self.page)
        self.SUM_WITH_TAX_BILLING = ElementsList(
            "//div[contains(@class, '-drawer-body')]//td[6]", "Сумма с учетом налога", self.page
        )
        self.TAX_BILLING = ElementsList("//div[contains(@class, '-drawer-body')]//td[7]", "Налог", self.page)
        self.REASON_BILLING = ElementsList("//div[contains(@class, '-drawer-body')]//td[8]", "Причина", self.page)
        self.TARGET_BILLING = ElementsList("//div[contains(@class, '-drawer-body')]//td[10]", "Цель", self.page)
        self.TRANSFERRED = ElementsList("//div[contains(@class, '-drawer-body')]//td[13]", "Перенесено", self.page)
        self.ADVANCE_BILLING = ElementsList("//div[contains(@class, '-drawer-body')]//td[14]", "Аванс", self.page)


class CreateAdjustmentForm(DynamicForms):
    """Форма Ввод корректировки платежа/начисления"""

    def __init__(self, page: Page):
        super().__init__(page)

        # Ввод корректировки платежа
        self.PAYMENT_INPUT = Element("#payments", "Поле ввода платежа", self.page)

        # Ввод корректировки начисления
        self.ADJUSTMENT_TARGET = RadioOrCheckboxBlock("#target", "Поле 'Корректировать'", self.page)
        self.ADJUSTMENT_OBJECT = Select("#adjustmentObject", "Тип объекта корректировки", self.page)
        self.ADJUSTMENT_OBJECT_VALUE = Element("#adjustmentObjectValue", "Объект корректировки", self.page)
        self.DETAILS = Element("#details, #billsDetailsList", "Поле ввода 'Детали'", self.page)
        self.TAX_INVOICE_LINE = Element("#adjustmentLineInvoice", "Поле ввода 'Строка СФ'", self.page)

        # Общие элементы форм
        self.ADJUSTMENT_TYPE_RADIOBUTTONS = RadioOrCheckboxBlock(
            "#adjustmentTypeRange", "Радио-баттон 'Тип корректировки'", self.page
        )
        self.ADJUSTMENT_DATE_INPUT = DatePicker("#adjustmentData", "Дата корректировки", self.page)
        self.SUM_WITH_TAX_INPUT = Element("#amountWithTax", "Сумма с учетом налога", self.page)
        self.TAX_INPUT = Element("#adjustmentInBalanceTax", "Налог", self.page)
        self.REASON_SELECT = Select("#adjustmentReason", "Причина", self.page)
        self.COMMENT_INPUT = Element("#comment", "Комментарий", self.page)
        self.ADD_ADJUSTMENT_BUTTON = Element("//*[contains(@class, 'drawer-footer')] //button[2]", "Добавить", self.page)


class ChooseAdjustmentObjectForm(DynamicForms):
    """Форма Выбора объекта корректировки (платеж, счет, счет-фактура, деталь)"""

    def __init__(self, page: Page):
        super().__init__(page)

        self.TITLE = Element("(//*[contains(@class, '-drawer-title')]/h3)[2]", "Заголовок формы", self.page)
        self.PAYMENT = ElementsList(
            "[class*=drawer-content] [class*=table-tbody] [class*=table-row]", "Платеж", self.page
        )
        self.BILL = ElementsList("[class*=drawer-content] [class*=table-tbody] [class*=table-row]", "Счет", self.page)
        self.DETAIL = ElementsList(
            "[class*=drawer-content] [class*=table-tbody] [class*=table-row]", "Деталь", self.page
        )
        self.TAX_INVOICE = ElementsList(
            "[class*=drawer-content] [class*=table-tbody] [class*=table-row]", "Счет-фактура", self.page
        )

        self.DETAIL_NAME = ElementsList(
            "[class*=drawer-content] [class*=table-tbody] td:nth-child(1)", "Название Детали", self.page
        )

        self.TAX_INVOICE_TYPE = ElementsList(
            "[class*=table-row] [class*=table-cell]:nth-child(1)", "Поле 'Тип' счета-фактуры", self.page
        )
        self.TAX_INVOICE_NUMBER = ElementsList(
            "[class*=table-row] [class*=table-cell]:nth-child(2)", "Поле 'Номер' счета-фактуры", self.page
        )
        self.TAX_INVOICE_DATE = ElementsList(
            "[class*=table-row] [class*=table-cell]:nth-child(3)", "Поле 'Дата' счета-фактуры", self.page
        )

        self.NEXT_PAGE_BTN = Element(
            "(//*[contains(@class, '-table-pagination')] //button)[2]", "Кнопка 'Следующая страница'", self.page
        )
        self.CHOOSE_BTN = Element(
            "(//*[contains(@class, 'drawer-footer')])[2] //button[2]", "Кнопка 'Выбрать'", self.page
        )


class AdjustmentDetails(DynamicForms):
    """
    Этот класс описывает локаторы находящиеся в сайдбаре Детали корректировки.
    Он появляется после нажатия на дату у конкретной корректировки.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        self.PROPERTIES_TAB = Element("//div[@data-node-key='properties'] /div", "Таб Свойства", self.page)
        self.RELATED_TAB = Element("//div[@data-node-key='related'] /div", "Таб Связанные операции", self.page)
        self.REPAYMENTS_ROW = ElementsList(
            "//div[contains(@id,'panel-related')] //tr[contains(@class, 'table-row')]",
            "Строки в таблице Погашения",
            self.page,
        )
        self.REPAYMENTS_SUM = ElementsList(
            "//div[contains(@id,'panel-related')] //td[2]", "Столбец Сумма погашения", self.page
        )
        self.REFRESH_BTN = Element(
            "//div[contains(@id,'panel-related')] //span[@data-icon='Refresh']", "Кнопка обновить", self.page
        )
        self.CLOSE_BTN = Element("//button[@aria-label='Close']", "Кнопка закрыть", self.page)
