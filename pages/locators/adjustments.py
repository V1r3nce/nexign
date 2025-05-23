from playwright.sync_api import Page

from pages.locators.dynamic_form_elements import DynamicForms
from pages.ui_elements import DatePicker, Dropdown, Element, ElementsList, RadioOrCheckboxBlock, Select


class Adjustments(DynamicForms):
    """Страница 'Корректировки'"""

    def __init__(self, page: Page):
        super().__init__(page)

        # Основная форма
        self.CURRENCY = Element("//h3[text() = 'RUB']", "RUB", self.page)
        self.BALANCE = Element(
            "//*[contains(@class, 'platform-scrollable')] //div[2] //h3[1]", "Баланс лицевого счета", self.page
        )

        # BUTTONS
        self.ADD_ADJUSTMENT_BTN = Dropdown(
            ".platform-dropdown-button-wrapper button[variant=primary]", "Добавить корректировку", self.page
        )
        self.UPDATE_TABLE_BTN = Element(
            "(//*[contains(@class, 'platform-custom-table')] //button)[2]", "Кнопка 'Обновить'", self.page
        )
        self.CANCEL_BTN = Element(
            "(//*[contains(@class, 'platform-custom-table')] //button)[4]",
            "Кнопка 'Аннулировать'",
            self.page,
        )
        self.OPEN_BILLING_FORM = Element(
            "(//div[contains(@class, 'platform-custom-table')] //button)[6]", "Кнопка 'Провести биллинг'", self.page
        )
        self.EXPORT_TO_XLS_BTN = Element(
            "(//*[contains(@class, 'platform-custom-table')] //button)[7]",
            "Кнопка 'Экспортировать найденные записи в XLS файл'",
            self.page,
        )

        # ADJUSTMENTS
        self.ADJUSTMENT_TITLE = ElementsList(
            "table tr>th>div:first-child", "Заголовки таблицы 'Корректировки'", self.page
        )
        self.ADJUSTMENTS = ElementsList(".ant-table-tbody tr", "Корректировка", self.page)
        self.INCLUDED_IN_BILL = ElementsList(".ant-table-tbody td:nth-child(1) div", "Учтено в счете", self.page)
        self.ADJUSTMENT_TYPE = ElementsList(".ant-table-tbody td:nth-child(2)", "Тип", self.page)
        self.ADJUSTMENT_DATE = ElementsList(".ant-table-tbody td:nth-child(3)", "Дата", self.page)
        self.SUM_WITH_TAX = ElementsList(".ant-table-tbody td:nth-child(4)", "Сумма с учётом налога", self.page)
        self.TAX = ElementsList(".ant-table-tbody td:nth-child(5)", "Налог", self.page)
        self.STATUS = ElementsList(".ant-table-tbody td:nth-child(6)", "Статус", self.page)
        self.REASON = ElementsList(".ant-table-tbody td:nth-child(7)", "Причина", self.page)
        self.TARGET_TYPE = ElementsList(".ant-table-tbody td:nth-child(8)", "Целевой тип счёта", self.page)
        self.TARGET = ElementsList(".ant-table-tbody td:nth-child(9)", "Цель", self.page)
        self.ADVANCE = ElementsList(".ant-table-tbody td:nth-child(11)", "Аванс", self.page)

        self.LOADER_SPIN = Element("(//div[contains(@class, 'ant-spin-spinning')]/span)[1]", "Загрузка", self.page)

        # Форма Биллинг по корректировкам
        self.BILLING_TITLE = Element(".ant-drawer-header-title h3", "Биллинг по корректировкам", self.page)
        self.START_BILLING = Element(".ant-drawer-footer button[variant='primary']", "Провести биллинг", self.page)
        self.UPDATE_BILLING_TABLE_BUTTON = Element(
            "(//div[@class = 'ant-drawer-body']//button)[1]", "Обновить", self.page
        )
        self.SWITCH_ONLY_SELECTED = Element("button[role='switch']", "Только выбранные", self.page)
        self.SWITCH_ONLY_SELECTED_TEXT = Element(
            "(//div[@class = 'ant-drawer-body']//div[contains(@class, 'platform-custom-table')]//p)[1]",
            "Только выбранные",
            self.page,
        )
        self.BILLING_TABLE_HEADERS = ElementsList(
            ".ant-drawer-body th div.ant-table-column-sorters",
            "Заголовки таблицы 'Биллинг по корректировкам'",
            self.page,
        )
        self.ADJUSTMENT_CHECKBOX = ElementsList(
            "//div[@class='ant-drawer-body']//tr/td[1]", "Чекбокс для выбора корректировки", self.page
        )
        self.BILLING_ADJUSTMENTS = ElementsList(
            "//div[@class = 'ant-drawer-body']//tbody/tr", "Корректировки на форме Биллинг по корректировкам", self.page
        )
        self.INCLUDED_IN_BILL_BILLING = ElementsList(
            "//div[@class = 'ant-drawer-body']//td[2]/div", "Учтено в счете", self.page
        )
        self.ADJUSTMENT_TYPE_BILLING = ElementsList("//div[@class = 'ant-drawer-body']//td[3]/div", "Тип", self.page)
        self.SUM_WITH_TAX_BILLING = ElementsList(
            "//div[@class = 'ant-drawer-body']//td[5]/div", "Сумма с учетом налога", self.page
        )
        self.TAX_BILLING = ElementsList("//div[@class = 'ant-drawer-body']//td[6]/div", "Налог", self.page)
        self.REASON_BILLING = ElementsList("//div[@class = 'ant-drawer-body']//td[7]/div", "Причина", self.page)
        self.TARGET_BILLING = ElementsList("//div[@class = 'ant-drawer-body']//td[9]/div", "Цель", self.page)
        self.ADVANCE_BILLING = ElementsList("//div[@class = 'ant-drawer-body']//td[11]/div", "Аванс", self.page)
        self.TRANSFERRED = ElementsList(".ant-table-tbody td:nth-child(10)", "Перенесено", self.page)
        self.ADVANCED = ElementsList(".ant-table-tbody td:nth-child(11)", "Аванс", self.page)


class CreateAdjustmentForm(DynamicForms):
    """Форма Ввод корректировки платежа/начисления"""

    def __init__(self, page: Page):
        super().__init__(page)

        # Ввод корректировки платежа
        self.PAYMENT_INPUT = Element("#payments", "Поле ввода платежа", self.page)

        # Ввод корректировки начисления
        self.ADJUSTMENT_TARGET = RadioOrCheckboxBlock("#target", "Поле 'Корректировать'", self.page)
        self.ADJUSTMENT_OBJECT = Select("//*[@id='adjustmentObject']/../../..", "Тип объекта корректировки", self.page)
        self.ADJUSTMENT_OBJECT_VALUE = Element("#adjustmentObjectValue", "Объект корректировки", self.page)
        self.DETAILS = Element("#details, #billsDetailsList", "Поле ввода 'Детали'", self.page)
        self.DETAILS_SELECTION_BUTTON = Element(
            "//input[@id = 'billsDetailsList']/ancestor::span/span", "Детали", self.page
        )
        self.TAX_INVOICE_LINE = Element("#adjustmentLineInvoice", "Поле ввода 'Строка СФ'", self.page)

        # Общие элементы форм
        self.ADJUSTMENT_TYPE_RADIOBUTTONS = RadioOrCheckboxBlock(
            "#adjustmentTypeRange", "Радио-баттон 'Тип корректировки'", self.page
        )
        self.ADJUSTMENT_TYPE = ElementsList(".ant-radio-wrapper", "Тип корректировки", self.page)
        self.ADJUSTMENT_DATE_INPUT = DatePicker("#adjustmentData", "Дата корректировки", self.page)
        self.SUM_WITH_TAX_INPUT = Element("#amountWithTax", "Сумма с учетом налога", self.page)
        self.TAX_INPUT = Element("#adjustmentInBalanceTax", "Налог", self.page)
        self.REASON_SELECT = Select("#adjustmentReason", "Причина", self.page)
        self.COMMENT_INPUT = Element("#comment", "Комментарий", self.page)
        self.ADD_ADJUSTMENT_BUTTON = Element(".ant-drawer-footer button:nth-child(2)", "Добавить", self.page)


class ChooseAdjustmentObjectForm(DynamicForms):
    """Форма Выбора объекта корректировки (платеж, счет, счет-фактура, деталь)"""

    def __init__(self, page: Page):
        super().__init__(page)

        self.TITLE = Element("(//*[@class='ant-drawer-title']/h3)[2]", "Заголовок формы", self.page)
        self.PAYMENT = ElementsList(".ant-drawer-content tbody tr", "Платеж", self.page)
        self.BILL = ElementsList(".ant-drawer-content tbody tr", "Счет", self.page)
        self.DETAIL = ElementsList(".ant-drawer-content tbody tr", "Деталь", self.page)
        self.TAX_INVOICE = ElementsList(".ant-drawer-content tbody tr", "Счет-фактура", self.page)

        self.DETAIL_NAME = ElementsList(".ant-drawer-content tr td:nth-child(1)", "Название Детали", self.page)

        self.TAX_INVOICE_TYPE = ElementsList(
            ".ant-drawer-content tr td:nth-child(1)", "Поле 'Тип' счета-фактуры", self.page
        )
        self.TAX_INVOICE_NUMBER = ElementsList(
            ".ant-drawer-content tr td:nth-child(2)", "Поле 'Номер' счета-фактуры", self.page
        )
        self.TAX_INVOICE_DATE = ElementsList(
            ".ant-drawer-content tr td:nth-child(3)", "Поле 'Дата' счета-фактуры", self.page
        )

        self.NEXT_PAGE_BTN = Element(
            "(//*[contains(@class, 'ant-table-pagination')] //button)[2]", "Кнопка 'Следующая страница'", self.page
        )
        self.CHOOSE_BTN = Element("(//*[@class = 'ant-drawer-footer'])[2] //button[2]", "Кнопка 'Выбрать'", self.page)
