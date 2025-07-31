from playwright.sync_api import Page

from pages.locators.base_elements import BaseElements
from pages.ui_elements import Element, ElementsList, RadioOrCheckboxBlock


class BillingAccounts(BaseElements):
    """Страница 'Биллинговые счета'"""

    def __init__(self, page: Page):
        super().__init__(page)

        # LEFT_NAV
        self.REFRESH_BTN = Element(
            "[class*=platform-custom-list-extra-tools] > div:first-child > div:first-child button [data-icon=Refresh]",
            "Кнопка 'Обновить'",
            self.page,
        )
        self.BILLING_LAUNCH_BTN = Element(
            "[class*=platform-custom-list-extra-tools] > div:first-child > div:first-child button [data-icon=Add]",
            "Кнопка 'Запуск биллинга'",
            self.page,
        )
        self.BILLING_TASKS_BTN = Element(
            "[class*=platform-custom-list-extra-tools] > div:first-child > div:first-child button [data-icon=History]",
            "Кнопка 'Список заданий биллинга'",
            self.page,
        )
        self.ACCOUNT_NUMS_LIST = ElementsList(
            ".platform-custom-list-scrollable-body>div div:first-child>p", "Список биллинговых счетов", self.page
        )
        self.ACCOUNT_EMPTY_LIST = Element(
            ".platform-custom-list-scrollable-body .platform-empty-state-container", "Записи не найдены", self.page
        )
        self.BILL_DATE = ElementsList(
            ".platform-custom-list-scrollable-body div:nth-child(2) > div:nth-child(2) p",
            "Дата биллингового счёта",
            self.page,
        )
        self.BILL_AMOUNT_DUE = ElementsList(
            ".platform-custom-list-scrollable-body div:not([class])>div>div:nth-child(2)",
            "Задолженность биллингового счёта",
            self.page,
        )
        self.BILL_STATUS = ElementsList(
            ".platform-custom-list-scrollable-body div:not([class]) div>div>div:nth-child(1)>div",
            "Статус биллингового счёта",
            self.page,
        )

        # BILLING_ACCOUNT
        self.BILLING_BTNS = ElementsList(
            "[id*=panel-bills] div:nth-child(3) div:nth-child(3)>button",
            "Список кнопок биллинга",
            self.page,
        )
        self.PROPERTIES_TAB = Element("[id*=tab-properties]", "Таб 'Свойства'", self.page)
        self.DETAILS_TAB = Element("[id*=tab-details]", "Таб 'Детали'", self.page)
        self.INVOICES_TAB = Element("[id*=tab-invoices]", "Таб 'Счета-фактуры'", self.page)
        self.DOCUMENTS_TAB = Element("[id*=tab-documents]", "Таб 'Документы'", self.page)
        self.LINKED_OPERATIONS_TAB = Element("[id*=tab-linked-accounts]", "Таб 'Связанные операции'", self.page)
        self.NON_OPERATING_INCOMES_TAB = Element(
            "[id*=panel-bills] [id*=tab-penalties]", "Таб 'Внереализационные начисления'", self.page
        )
        self.EXECUTE_BTN = ElementsList("[class*=modal-footer] button:last-child", "Кнопка 'Выполнить'", self.page)

        # PROPERTIES
        self.BILLING_PROPERTIES = ElementsList(
            "//*[@role='tabpanel'] //*[@overflow='scroll']/div/div/div[1]",
            "Список наименований свойств биллинга",
            self.page,
        )
        self.BILLING_PROPERTY_VALUES = ElementsList(
            "//*[@role='tabpanel'] //*[@overflow='scroll']/div/div/div[2]", "Список значений свойств биллинга", self.page
        )
        self.LINKED_CLAIM_LIST_BTN = Element("//*[@role='tabpanel'] //a", "Кнопка 'Список связанных заявок'", self.page)

        # DETAILS
        self.UPDATE_DETAILS_LIST_BTN = Element(
            "[id*=panel-details] [data-icon=Refresh]", "Кнопка 'Обновить детали'", self.page
        )
        self.LINKED_INQUIRES_BTN = Element(
            "[id*=panel-details] [data-icon=AddLink]", "Кнопка 'Связать с заявкой'", self.page
        )
        self.DETAIL = ElementsList("[id*=panel-details] [class*=table-tbody] tr", "Деталь биллингового счета", self.page)
        self.DETAIL_FIELDS_LIST = ElementsList(
            "[id*=panel-details] [class*=table-tbody] tr div", "Поля первой детали биллингового счета", self.page
        )
        self.DETAIL_CHECKBOX = ElementsList("[id*=panel-details] tr td:nth-child(1)", "Чекбокс выбора детали", self.page)
        self.DETAIL_NAME = ElementsList("[id*=panel-details] tr td:nth-child(2)", "Название детали", self.page)
        self.DETAIL_CHARGED = ElementsList("[id*=panel-details] tr td:nth-child(3)", "Поле 'Начислено'", self.page)
        self.DETAIL_DISCOUNT = ElementsList("[id*=panel-details] tr td:nth-child(4)", "Поле 'Скидка'", self.page)
        self.DETAIL_CHARGED_ADDITIONALLY = ElementsList(
            "[id*=panel-details] tr td:nth-child(5)", "Поле 'Доначислено'", self.page
        )
        self.DETAIL_UNIT = ElementsList("[id*=panel-details] tr td:nth-child(6)", "Поле 'Производство'", self.page)
        self.DETAIL_SUBSCRIBER = ElementsList("[id*=panel-details] tr td:nth-child(7)", "Поле 'Абонент'", self.page)
        self.DETAIL_TAX_SCHEME = ElementsList(
            "[id*=panel-details] tr td:nth-child(8)", "Поле 'Схема налогообложения'", self.page
        )
        self.DETAIL_ADJUSTED = ElementsList(
            "[id*=panel-details] tr td:nth-child(9)", "Поле 'Откорректированно'", self.page
        )
        self.DETAIL_PRODUCT = ElementsList("[id*=panel-details] tr td:nth-child(10)", "Поле 'Продукт'", self.page)
        self.DETAIL_REPAID = ElementsList("[id*=panel-details] tr td:nth-child(11)", "Поле 'Погашено'", self.page)
        self.DETAIL_AVAILABLE_ADJUSTMENT = ElementsList(
            "[id*=panel-details] tr td:nth-child(12)", "Поле 'Доступно для корректирования'", self.page
        )
        self.DETAIL_LINKED_INQUIRES = ElementsList(
            "[id*=panel-details] tr td:nth-child(13)", "Поле 'Связанные заявки'", self.page
        )
        self.LINKED_INQUIRES_LIST_BTN = ElementsList(
            "[id*=panel-details] tr td:nth-child(13) a", "Кнопка 'Список связанных заявок'", self.page
        )
        self.NO_DETAIL_BLOCK = Element(
            "[id*=panel-details] [class*=table-expanded-row-fixed]", "Блок 'Нет деталей'", self.page
        )

        # INVOICES
        self.UPDATE_INVOICE_LIST_BTN = Element(
            "[id*=panel-invoice] [data-icon=Refresh]", "Кнопка 'Обновить счета-фактуры'", self.page
        )
        self.INVOICE = ElementsList(
            "[id*=panel-invoices] [class*=table-tbody] tr", "Счета-фактуры биллингового счета", self.page
        )
        self.INVOICE_TYPE = ElementsList("[id*=panel-invoices] tr td:nth-child(1)", "Поле 'Тип'", self.page)
        self.INVOICE_NUMBER = ElementsList("[id*=panel-invoices] tr td:nth-child(2)", "Поле 'Номер'", self.page)
        self.INVOICE_DATE = ElementsList("[id*=panel-invoices] tr td:nth-child(3)", "Поле 'Дата'", self.page)
        self.INVOICE_AMOUNT = ElementsList(
            "[id*=panel-invoices] tr td:nth-child(4)", "Поле 'Сумма с налогами'", self.page
        )
        self.INVOICE_TAX = ElementsList("[id*=panel-invoices] tr td:nth-child(5)", "Поле 'Налоги'", self.page)
        self.INVOICE_UNIT = ElementsList("[id*=panel-invoices] tr td:nth-child(6)", "Поле 'Производство'", self.page)
        self.INVOICE_ADJUSTMENT_TAX_INVOICE = ElementsList(
            "[id*=panel-invoices] tr td:nth-child(7)", "Поле 'Корректируемый СФ'", self.page
        )
        self.INVOICE_ADJUSTMENT_NUMBER = ElementsList(
            "[id*=panel-invoices] tr td:nth-child(8)", "Поле 'Номер исправления'", self.page
        )
        self.INVOICE_ADJUSTMENT_DATE = ElementsList(
            "[id*=panel-invoices] tr td:nth-child(9)", "Поле 'Дата исправления'", self.page
        )
        self.INVOICE_ADJUSTED = ElementsList(
            "[id*=panel-invoices] tr td:nth-child(10)", "Поле 'Откорректированно'", self.page
        )
        self.INVOICE_BALANCE = ElementsList("[id*=panel-invoices] tr td:nth-child(11)", "Поле 'Остаток'", self.page)
        self.NO_INVOICE_BLOCK = Element(
            "[id*=panel-invoices] [class*=table-expanded-row-fixed]", "Блок 'Нет счетов-фактур'", self.page
        )

        # DOCUMENTS
        self.DOCUMENT = ElementsList("[id*='panel-documents'] [class*=table-tbody] tr", "Документ", self.page)
        self.NO_DOCUMENT_BLOCK = Element(
            "[id*='panel-documents'] .platform-empty-state-container", "Блок 'Документов пока нет'", self.page
        )

        # LINKED_OPERATIONS
        self.LINKED_OPERATIONS = RadioOrCheckboxBlock(
            "[id*='panel-linked-accounts'] div[class*=radio-group]", "Заголовки связанных операций", self.page
        )
        self.LINKED_OPERATIONS_VALUE_LOADER = ElementsList(
            "//*[contains(@id, 'panel-linked-accounts')] //*[contains(@class, '-spin-sm')]",
            "Лоадер значения связанной операции",
            self.page,
        )
        self.TABLE_ROW_LINKED_OPERATION = ElementsList(
            "[id*=panel-linked-accounts] [class*=table-tbody] [class*=table-row]",
            "Строка таблицы на вкладке 'Связанные операции'",
            self.page,
        )
        self.REPAYMENTS_OBJECT = ElementsList(
            "[id*=panel-linked-accounts] [class*=table-tbody] [class*=table-row] div:nth-child(1)",
            "Таблица 'Погашение', поле 'Объект'",
            self.page,
        )
        self.REPAYMENTS_DATE = ElementsList(
            "[id*=panel-linked-accounts] [class*=table-tbody] [class*=table-row] div:nth-child(2)",
            "Таблица 'Погашение', поле 'Дата'",
            self.page,
        )
        self.REPAYMENTS_AMOUNT = ElementsList(
            "[id*=panel-linked-accounts] [class*=table-tbody] [class*=table-row] div:nth-child(3)",
            "Таблица 'Погашение', поле 'Сумма'",
            self.page,
        )
        self.DEBITED_DATE = ElementsList(
            "[id*=panel-linked-accounts] [class*=table-tbody] [class*=table-row] div:nth-child(1)",
            "Таблица 'Списано', поле 'Дата'",
            self.page,
        )
        self.DEBITED_AMOUNT_AFTER_TAX = ElementsList(
            "[id*=panel-linked-accounts] [class*=table-tbody] [class*=table-row] div:nth-child(2)",
            "Таблица 'Списано', поле 'Сумма с налогом'",
            self.page,
        )
        self.DEBITED_TAX = ElementsList(
            "[id*=panel-linked-accounts] [class*=table-tbody] [class*=table-row] div:nth-child(3)",
            "Таблица 'Списано', поле 'Налог'",
            self.page,
        )
        self.DEBITED_DETAIL = ElementsList(
            "[id*=panel-linked-accounts] [class*=table-tbody] [class*=table-row] div:nth-child(4)",
            "Таблица 'Списано', поле 'Деталь'",
            self.page,
        )
        self.DEBITED_REASON = ElementsList(
            "[id*=panel-linked-accounts] [class*=table-tbody] [class*=table-row] div:nth-child(5)",
            "Таблица 'Списано', поле 'Причина'",
            self.page,
        )
        self.NO_RECORDS_LINKED_OPERATION_FOUND = Element(
            "[id*=panel-linked-accounts] .platform-empty-state-container",
            "Блок 'Записи не найдены' на вкладке 'Связанные операции'",
            self.page,
        )

        # NON_OPERATING_INCOMES_TAB
        self.NO_RECORDS_NON_OPERATING_INCOMES_FOUND = Element(
            "[id*=panel-penalties] .platform-empty-state-container",
            "Блок 'Записи не найдены' на вкладке 'Внереализационные начисления'",
            self.page,
        )

        # BILLING_TASKS_FORM
        self.UPDATE_BILLING_TASKS_BTN = Element(
            "[class*=drawer-open] [class*=drawer-body] [data-icon=Refresh]",
            "Кнопка 'Обновить список заданий биллинга'",
            self.page,
        )
        self.BILLING_TASK = ElementsList("[class*=-table-tbody] tr", "Задание биллинга", self.page)
        self.TASK_NUMBER_LIST = ElementsList("tr td:nth-child(1)", "Список номеров заданий", self.page)
        self.TASK_TYPE_LIST = ElementsList("tr td:nth-child(2)", "Список типов заданий", self.page)
        self.TASK_RUN_DATE_LIST = ElementsList("tr td:nth-child(3)", "Список дат запуска", self.page)
        self.TASK_STATUS_LIST = ElementsList("tr td:nth-child(4)", "Список статусов", self.page)
        self.TASK_USER_LIST = ElementsList("tr td:nth-child(5)", "Список пользователей", self.page)
        self.TASK_BILLING_TYPE_LIST = ElementsList("tr td:nth-child(6)", "Список типов биллинга", self.page)
        self.TASK_BILLING_DATE_LIST = ElementsList("tr td:nth-child(7)", "Список дат счёта", self.page)
        self.TASKS_CLOSE_BTN = Element("#_cancel-button", "Кнопка 'Закрыть'", self.page)
