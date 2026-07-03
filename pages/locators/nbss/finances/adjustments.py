from pages.locators.nbss.dynamic_form_elements import DynamicForms
from pages.ui_elements import (
    CheckboxBlock,
    DatePicker,
    DropdownWithId,
    Element,
    ElementsList,
    RadioOrCheckboxBlock,
    Select,
)


class AdjustmentsElements(DynamicForms):
    """Страница 'Корректировки'"""

    def __init__(self) -> None:
        super().__init__()

        # Основная форма
        self.CURRENCY = Element("//h3[text() = 'RUB']", "RUB")
        self.BALANCE = Element(
            "//*[contains(@class, 'platform-scrollable')] //div[2] //h3[@color='positive' or @color='negative']",
            "Баланс лицевого счета",
        )

        # BUTTONS
        self.ADD_ADJUSTMENT_BTN = DropdownWithId(
            "adjustment",
            "Добавить корректировку",
        )
        self.UPDATE_TABLE_BTN = Element("[id*=panel-adjustments] button:has([data-icon=Refresh])", "Кнопка 'Обновить'")
        self.CANCEL_BTN = Element(
            "(//*[contains(@class, 'platform-table')] //button)[4]",
            "Кнопка 'Аннулировать'",
        )
        self.OPEN_BILLING_FORM = Element(
            ".platform-table > div:not([class*=table-wrapper]) div:not([class*=btn]) button[class*=btn-color-default]:not([title]) span:not([data-icon])",
            "Кнопка 'Провести биллинг'",
        )
        self.EXPORT_TO_XLS_BTN = Element(
            "(//*[contains(@class, 'platform-table')] //button)[7]",
            "Кнопка 'Экспортировать найденные записи в XLS файл'",
        )
        self.SETTING_BTN = Element("[id*=panel-adjustments] button:has([data-icon=Settings])", "Кнопка 'Настройка'")
        self.COLUMN_LIST = CheckboxBlock("[class*=dropdown-placement-bottomRight]", "Список колонок таблицы")

        # ADJUSTMENTS
        self.ADJUSTMENT_TITLE = ElementsList(
            "table tr>th[class*=react-resizable]>div:first-child", "Заголовки таблицы 'Корректировки'"
        )
        self.ADJUSTMENTS = ElementsList("[class*=table-tbody] [data-row-key]", "Корректировка")
        self.ADJUSTMENT_ID = ElementsList("[class*=table-tbody] [data-row-key] > [class*=table-cell]:nth-child(1)", "ID")
        self.INCLUDED_IN_BILL = ElementsList(
            "[class*=table-tbody] [data-row-key] > [class*=table-cell]:nth-child(2)", "Учтено в счете"
        )
        self.ADJUSTMENT_TYPE = ElementsList(
            "[class*=table-tbody] [data-row-key] > [class*=table-cell]:nth-child(3)", "Тип"
        )
        self.ADJUSTMENT_DATE = ElementsList(
            "[class*=table-tbody] [data-row-key] > [class*=table-cell]:nth-child(4) > a", "Дата"
        )
        self.SUM_WITH_TAX = ElementsList(
            "[class*=table-tbody] [data-row-key] > [class*=table-cell]:nth-child(5)", "Сумма с учётом налога"
        )
        self.TAX = ElementsList("[class*=table-tbody] [data-row-key] > [class*=table-cell]:nth-child(6)", "Налог")
        self.STATUS = ElementsList(
            "[class*=table-tbody] [data-row-key] > [class*=table-cell]:nth-child(7) div", "Статус"
        )
        self.REASON = ElementsList("[class*=table-tbody] [data-row-key] > [class*=table-cell]:nth-child(8)", "Причина")
        self.TARGET_TYPE = ElementsList(
            "[class*=table-tbody] [data-row-key] > [class*=table-cell]:nth-child(9)", "Целевой тип счёта"
        )
        self.TARGET = ElementsList("[class*=table-tbody] [data-row-key] > [class*=table-cell]:nth-child(10)", "Цель")
        self.DOCUMENT_NUMBER = ElementsList(
            "[class*=table-tbody] [data-row-key] > [class*=table-cell]:nth-child(11)", "Номер документа основания"
        )
        self.DOCUMENT_DATE = ElementsList(
            "[class*=table-tbody] [data-row-key] > [class*=table-cell]:nth-child(12)", "Дата докумнта основания"
        )
        self.TRANSFERRED = ElementsList(
            "[class*=table-tbody] [data-row-key] > [class*=table-cell]:nth-child(13)", "Перенесено"
        )
        self.ADVANCE = ElementsList("[class*=table-tbody] [data-row-key] > [class*=table-cell]:nth-child(14)", "Аванс")

        self.LOADER_SPIN = Element("(//div[contains(@class, '-spin-spinning')]/span)[1]", "Загрузка")

        # Форма Биллинг по корректировкам
        self.BILLING_TITLE = Element(".ant-drawer-header-title h3", "Биллинг по корректировкам")
        self.START_BILLING = Element("[class*=-drawer-footer] button[class*=btn-primary]", "Провести биллинг")
        self.UPDATE_BILLING_TABLE_BUTTON = Element("[class*=drawer-body] [data-icon=Refresh]", "Обновить")
        self.SWITCH_ONLY_SELECTED = Element("button[role='switch']", "Только выбранные")
        self.SWITCH_ONLY_SELECTED_TEXT = Element(
            "(//div[contains(@class, '-drawer-body')]//div[contains(@class, 'platform-table')]//p)[1]",
            "Только выбранные",
        )
        self.BILLING_TABLE_HEADERS = ElementsList(
            "[class*=-drawer-body] th div[class*=column-title]",
            "Заголовки таблицы 'Биллинг по корректировкам'",
        )
        self.ADJUSTMENT_CHECKBOX = ElementsList(
            "[class*=drawer-content] [class*=table-tbody] [class*=table-cell] input[type=checkbox]",
            "Чекбокс для выбора корректировки",
        )
        self.BILLING_ADJUSTMENTS = ElementsList(
            "div[class*=drawer-content][role=dialog] [class*=table-tbody] [class*=table-row]",
            "Корректировки на форме Биллинг по корректировкам",
        )

        # Таблица
        self.ROWS_BILLING = ElementsList(
            "[class*='drawer-body'] tr[class*=table-row]", "Строки таблицы 'Биллинг по корректировкам'"
        )
        self.INCLUDED_IN_BILL_BILLING = ElementsList("//div[contains(@class, '-drawer-body')]//td[3]", "Учтено в счете")
        self.ADJUSTMENT_TYPE_BILLING = ElementsList("//div[contains(@class, '-drawer-body')]//td[4]", "Тип")
        self.SUM_WITH_TAX_BILLING = ElementsList(
            "//div[contains(@class, '-drawer-body')]//td[6]", "Сумма с учетом налога"
        )
        self.TAX_BILLING = ElementsList("//div[contains(@class, '-drawer-body')]//td[7]", "Налог")
        self.REASON_BILLING = ElementsList("//div[contains(@class, '-drawer-body')]//td[8]", "Причина")
        self.TARGET_BILLING = ElementsList("//div[contains(@class, '-drawer-body')]//td[10]", "Цель")
        self.TRANSFERRED_BILLING = ElementsList("//div[contains(@class, '-drawer-body')]//td[13]", "Перенесено")
        self.ADVANCE_BILLING = ElementsList("//div[contains(@class, '-drawer-body')]//td[14]", "Аванс")


class CreateAdjustmentForm(DynamicForms):
    """Форма Ввод корректировки платежа/начисления"""

    def __init__(self) -> None:
        super().__init__()

        # Ввод корректировки платежа
        self.PAYMENT_INPUT = Element("#payments", "Поле ввода платежа")

        # Ввод корректировки начисления
        self.ADJUSTMENT_TARGET = RadioOrCheckboxBlock("#target", "Поле 'Корректировать'")
        self.ADJUSTMENT_OBJECT = Select("#adjustmentObject", "Тип объекта корректировки")
        self.ADJUSTMENT_OBJECT_VALUE = Element("#adjustmentObjectValue", "Объект корректировки")
        self.DETAILS = Element("#details, #billsDetailsList", "Поле ввода 'Детали'")
        self.TAX_INVOICE_LINE = Element("#adjustmentLineInvoice", "Поле ввода 'Строка СФ'")

        # Общие элементы форм
        self.ADJUSTMENT_TYPE_RADIOBUTTONS = RadioOrCheckboxBlock(
            "#adjustmentTypeRange", "Радио-баттон 'Тип корректировки'"
        )
        self.ADJUSTMENT_DATE_INPUT = DatePicker("#adjustmentData", "Дата корректировки")
        self.SUM_WITH_TAX_INPUT = Element("#amountWithTax", "Сумма с учетом налога")
        self.TAX_INPUT = Element("#adjustmentInBalanceTax", "Налог")
        self.REASON_SELECT = Select("//input[@id='adjustmentReason']", "Причина")
        self.COMMENT_INPUT = Element("#comment", "Комментарий")
        self.ADD_ADJUSTMENT_BUTTON = Element("//*[contains(@class, 'drawer-footer')] //button[2]", "Добавить")


class ChooseAdjustmentObjectForm(DynamicForms):
    """Форма Выбора объекта корректировки (платеж, счет, счет-фактура, деталь)"""

    def __init__(self) -> None:
        super().__init__()

        self.TITLE = Element("(//*[contains(@class, '-drawer-title')]/h3)[2]", "Заголовок формы")
        self.PAYMENT = ElementsList("[class*=drawer-content] [class*=table-tbody] [class*=table-row]", "Платеж")
        self.BILL = ElementsList("[class*=drawer-content] [class*=table-tbody] [class*=table-row]", "Счет")
        self.DETAIL = ElementsList("[class*=drawer-content] [class*=table-tbody] [class*=table-row]", "Деталь")
        self.TAX_INVOICE = ElementsList(
            "[class*=drawer-content] [class*=table-tbody] [class*=table-row]", "Счет-фактура"
        )

        self.DETAIL_NAME = ElementsList(
            "[class*=drawer-content] [class*=table-tbody] [class*=table-cell]:nth-child(1)", "Название Детали"
        )

        self.TAX_INVOICE_TYPE = ElementsList(
            "[class*=table-row] [class*=table-cell]:nth-child(1)", "Поле 'Тип' счета-фактуры"
        )
        self.TAX_INVOICE_NUMBER = ElementsList(
            "[class*=table-row] [class*=table-cell]:nth-child(2)", "Поле 'Номер' счета-фактуры"
        )
        self.TAX_INVOICE_DATE = ElementsList(
            "[class*=table-row] [class*=table-cell]:nth-child(3)", "Поле 'Дата' счета-фактуры"
        )

        self.NEXT_PAGE_BTN = Element(
            "(//*[contains(@class, '-table-pagination')] //button)[2]", "Кнопка 'Следующая страница'"
        )
        self.CHOOSE_BTN = Element("(//*[contains(@class, 'drawer-footer')])[2] //button[2]", "Кнопка 'Выбрать'")


class AdjustmentDetails(DynamicForms):
    """
    Этот класс описывает локаторы находящиеся в сайдбаре Детали корректировки.
    Он появляется после нажатия на дату у конкретной корректировки.
    """

    def __init__(self) -> None:
        super().__init__()

        self.PROPERTIES_TAB = Element("//div[@data-node-key='properties'] /div", "Таб Свойства")
        self.RELATED_TAB = Element("//div[@data-node-key='related'] /div", "Таб Связанные операции")
        self.REPAYMENTS_ROW = ElementsList(
            "[id$=related] [class*=table-tbody] [class*=table-row][data-row-key]",
            "Строки в таблице Погашения",
        )
        self.REPAYMENTS_SUM = ElementsList(
            "[id$=related] [class*=table-tbody] [class*=table-row][data-row-key] [class*=table-cell]:nth-child(2)",
            "Столбец Сумма погашения",
        )
        self.REFRESH_BTN = Element(
            "//div[contains(@id,'panel-related')] //span[@data-icon='Refresh']", "Кнопка обновить"
        )
        self.CLOSE_BTN = Element("//button[.//span[normalize-space()='Закрыть']]", "Кнопка закрыть")
