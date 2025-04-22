from playwright.sync_api import Page

from pages.locators.base_elements import BaseElements
from pages.locators.dynamic_form_elements import DynamicForms
from pages.ui_elements import DatePicker, Dropdown, Element, ElementsList, RadioOrCheckboxBlock, Select


class Adjustments(BaseElements):
    """Страница 'Корректировки'"""

    def __init__(self, page: Page):
        super().__init__(page)

        self.BALANCE = Element(
            "//*[contains(@class, 'platform-scrollable')] //div[2] //h3[1]", "Баланс лицевого счета", self.page
        )

        # BUTTONS
        self.ADD_ADJUSTMENT_BTN = Dropdown(
            "(//*[contains(@class, 'platform-custom-table')]/div[1]/div[1] //button)[1]",
            "Кнопка 'Добавить корректировку'",
            self.page,
        )
        self.UPDATE_TABLE_BTN = Element(
            "(//*[contains(@class, 'platform-custom-table')]/div[1]/div[1] //button)[2]",
            "Кнопка 'Обновить'",
            self.page,
        )
        self.CANCEL_BTN = Element(
            "(//*[contains(@class, 'platform-custom-table')]/div[1]/div[1] //button)[4]",
            "Кнопка 'Аннулировать'",
            self.page,
        )
        self.OPEN_BILLING_FORM_BTN = Element(
            "(//*[contains(@class, 'platform-custom-table')]/div[1]/div[1] //button)[6]",
            "Кнопка 'Провести биллинг'",
            self.page,
        )
        self.EXPORT_TO_XLS_BTN = Element(
            "(//*[contains(@class, 'platform-custom-table')]/div[1]/div[1] //button)[7]",
            "Кнопка 'Экспортировать найденные записи в XLS файл'",
            self.page,
        )

        # ADJUSTMENTS
        self.ADJUSTMENT_TITLE = ElementsList(
            "table tr>th>div:first-child", "Заголовки таблицы 'Корректировки'", self.page
        )
        self.ADJUSTMENT = ElementsList(".ant-table-tbody tr", "Корректировка", self.page)
        self.INCLUDED_IN_BILL = ElementsList(".ant-table-tbody td:nth-child(1)", "Учтено в счете", self.page)
        self.ADJUSTMENT_TYPE = ElementsList(".ant-table-tbody td:nth-child(2)", "Тип", self.page)
        self.ADJUSTMENT_DATE = ElementsList(".ant-table-tbody td:nth-child(3)", "Дата", self.page)
        self.SUM_WITH_TAX = ElementsList(".ant-table-tbody td:nth-child(4)", "Сумма с учётом налога", self.page)
        self.TAX = ElementsList(".ant-table-tbody td:nth-child(5)", "Налог", self.page)
        self.STATUS = ElementsList(".ant-table-tbody td:nth-child(6)", "Статус", self.page)
        self.REASON = ElementsList(".ant-table-tbody td:nth-child(7)", "Причина", self.page)
        self.TARGET_TYPE = ElementsList(".ant-table-tbody td:nth-child(8)", "Целевой тип счёта", self.page)
        self.TARGET = ElementsList(".ant-table-tbody td:nth-child(9)", "Цель", self.page)
        self.TRANSFERRED = ElementsList(".ant-table-tbody td:nth-child(10)", "Перенесено", self.page)
        self.ADVANCED = ElementsList(".ant-table-tbody td:nth-child(11)", "Аванс", self.page)


class CreateAdjustmentForm(DynamicForms):
    """Форма Ввод корректировки платежа/начисления"""

    def __init__(self, page: Page):
        super().__init__(page)

        self.PAYMENT_INPUT = Element("#payments", "Поле ввода платежа", self.page)
        self.ADJUSTMENT_TARGET = RadioOrCheckboxBlock("#target", "Поле 'Корректировать'", self.page)
        self.ADJUSTMENT_OBJECT = Select("//*[@id='adjustmentObject']/../../..", "Тип объекта корректировки", self.page)
        self.ADJUSTMENT_OBJECT_VALUE = Element("#adjustmentObjectValue", "Объект корректировки", self.page)
        self.DETAILS = Element("#details, #billsDetailsList", "Поле ввода 'Детали'", self.page)
        self.TAX_INVOICE_LINE = Element("#adjustmentLineInvoice", "Поле ввода 'Строка СФ'", self.page)

        self.ADJUSTMENT_TYPE_RADIOBUTTONS = RadioOrCheckboxBlock(
            "#adjustmentTypeRange", "Радио-баттон 'Тип корректировки'", self.page
        )
        self.POSITIVE_ADJUSTMENT = Element(
            "#adjustmentTypeRange label:nth-child(1)", "Положительная корректировка", self.page
        )
        self.ADJUSTMENT_DATE_INPUT = DatePicker("#adjustmentData", "Поле ввода 'Дата корректировки'", self.page)
        self.SUM_WITH_TAX_INPUT = Element("#amountWithTax", "Поле ввода 'Сумма с учётом налога'", self.page)
        self.TAX_INPUT = Element("#adjustmentInBalanceTax", "Поле ввода 'Налог'", self.page)
        self.REASON_SELECT = Select("#adjustmentReason", "Поле 'Причина'", self.page)
        self.COMMENT_INPUT = Element("#comment", "Поле ввода 'Комментарий'", self.page)
        self.ADD_ADJUSTMENT_BTN = Element(".ant-drawer-footer button:nth-child(2)", "Кнопка 'Добавить'", self.page)


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
