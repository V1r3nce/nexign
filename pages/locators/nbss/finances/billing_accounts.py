from pages.locators.base_elements import BaseElements
from pages.ui_elements import Element, ElementsList, RadioOrCheckboxBlock


class BillingAccountsElements(BaseElements):
    """Страница 'Биллинговые счета'"""

    def __init__(self) -> None:
        super().__init__()

        # LEFT_NAV
        self.REFRESH_BTN = Element(
            "[class*=platform-custom-list-extra-tools] > div:first-child > div:first-child button [data-icon=Refresh]",
            "Кнопка 'Обновить'",
        )
        self.BILLING_LAUNCH_BTN = Element(
            "[class*=platform-custom-list-extra-tools] > div:first-child > div:first-child button [data-icon=Add]",
            "Кнопка 'Запуск биллинга'",
        )
        self.BILLING_TASKS_BTN = Element(
            "[class*=platform-custom-list-extra-tools] > div:first-child > div:first-child button [data-icon=History]",
            "Кнопка 'Список заданий биллинга'",
        )
        self.ACCOUNT_NUMS_LIST = ElementsList(
            ".platform-custom-list-scrollable-body>div div:first-child>p", "Список биллинговых счетов"
        )
        self.ACCOUNT_EMPTY_LIST = Element(
            ".platform-custom-list-scrollable-body .platform-empty-state-container", "Записи не найдены"
        )
        self.BILL_DATE = ElementsList(
            ".platform-custom-list-scrollable-body div:nth-child(2) > div:nth-child(2) p",
            "Дата биллингового счёта",
        )
        self.BILL_AMOUNT_DUE = ElementsList(
            ".platform-custom-list-scrollable-body div:not([class])>div>div:nth-child(2)",
            "Задолженность биллингового счёта",
        )
        self.BILL_STATUS = ElementsList(
            ".platform-custom-list-scrollable-body div:not([class]) div>div>div:nth-child(1)>div",
            "Статус биллингового счёта",
        )

        # BILLING_ACCOUNT
        self.BILLING_BTNS = ElementsList(
            "[id*=panel-bills] div:nth-child(3) div:nth-child(3)>button",
            "Список кнопок биллинга",
        )
        self.PROPERTIES_TAB = Element("[id*=tab-properties]", "Таб 'Свойства'")
        self.DETAILS_TAB = Element("[id*=tab-details]", "Таб 'Детали'")
        self.INVOICES_TAB = Element("[id*=tab-invoices]", "Таб 'Счета-фактуры'")
        self.DOCUMENTS_TAB = Element("[id*=tab-documents]", "Таб 'Документы'")
        self.LINKED_OPERATIONS_TAB = Element("[id*=tab-linked-accounts]", "Таб 'Связанные операции'")
        self.NON_OPERATING_INCOMES_TAB = Element(
            "[id*=panel-bills] [id*=tab-penalties]", "Таб 'Внереализационные начисления'"
        )
        self.EXECUTE_BTN = ElementsList("[class*=modal-footer] button:last-child", "Кнопка 'Выполнить'")

        # PROPERTIES
        self.BILLING_PROPERTIES = ElementsList(
            "//*[@role='tabpanel'] //*[@overflow='scroll']/div/div/div[1]",
            "Список наименований свойств биллинга",
        )
        self.BILLING_PROPERTY_VALUES = ElementsList(
            "//*[@role='tabpanel'] //*[@overflow='scroll']/div/div/div[2]", "Список значений свойств биллинга"
        )
        self.LINKED_CLAIM_LIST_BTN = Element("//*[@role='tabpanel'] //a", "Кнопка 'Список связанных заявок'")

        # DETAILS
        self.UPDATE_DETAILS_LIST_BTN = Element("[id*=panel-details] [data-icon=Refresh]", "Кнопка 'Обновить детали'")
        self.LINKED_INQUIRES_BTN = Element("[id*=panel-details] [data-icon=AddLink]", "Кнопка 'Связать с заявкой'")
        self.DETAIL = ElementsList(
            "[id*=panel-details] [class*=table-tbody] tr:not([aria-hidden='true'])",
            "Деталь биллингового счета",
        )
        self.DETAIL_CHECKBOX = ElementsList(
            "[id*=panel-details] tr[data-row-key] td:nth-child(1)", "Чекбокс выбора детали"
        )
        self.DETAIL_NAME = ElementsList("[id*=panel-details] tr[data-row-key] td:nth-child(2)", "Название детали")
        self.DETAIL_CHARGED = ElementsList("[id*=panel-details] tr[data-row-key] td:nth-child(3)", "Поле 'Начислено'")
        self.DETAIL_DISCOUNT = ElementsList("[id*=panel-details] tr[data-row-key] td:nth-child(4)", "Поле 'Скидка'")
        self.DETAIL_CHARGED_ADDITIONALLY = ElementsList(
            "[id*=panel-details] tr[data-row-key] td:nth-child(5)", "Поле 'Доначислено'"
        )
        self.DETAIL_UNIT = ElementsList("[id*=panel-details] tr[data-row-key] td:nth-child(6)", "Поле 'Производство'")
        self.DETAIL_SUBSCRIBER = ElementsList("[id*=panel-details] tr[data-row-key] td:nth-child(7)", "Поле 'Абонент'")
        self.DETAIL_TAX_SCHEME = ElementsList(
            "[id*=panel-details] tr[data-row-key] td:nth-child(8)", "Поле 'Схема налогообложения'"
        )
        self.DETAIL_ADJUSTED = ElementsList(
            "[id*=panel-details] tr[data-row-key] td:nth-child(9)", "Поле 'Откорректированно'"
        )
        self.DETAIL_PRODUCT = ElementsList("[id*=panel-details] tr[data-row-key] td:nth-child(10)", "Поле 'Продукт'")
        self.DETAIL_REPAID = ElementsList("[id*=panel-details] tr[data-row-key] td:nth-child(11)", "Поле 'Погашено'")
        self.DETAIL_AVAILABLE_ADJUSTMENT = ElementsList(
            "[id*=panel-details] tr[data-row-key] td:nth-child(12)", "Поле 'Доступно для корректирования'"
        )
        self.DETAIL_LINKED_INQUIRES = ElementsList(
            "[id*=panel-details] tr[data-row-key] td:nth-child(13)", "Поле 'Связанные заявки'"
        )
        self.LINKED_INQUIRES_LIST_BTN = ElementsList(
            "[id*=panel-details] tr[data-row-key] td:nth-child(13) a", "Кнопка 'Список связанных заявок'"
        )
        self.NO_DETAIL_BLOCK = Element("[id*=panel-details] [class*=table-expanded-row-fixed]", "Блок 'Нет деталей'")

        # INVOICES
        self.UPDATE_INVOICE_LIST_BTN = Element(
            "[id*=panel-invoice] [data-icon=Refresh]", "Кнопка 'Обновить счета-фактуры'"
        )
        self.INVOICE = ElementsList(
            "[id*=panel-invoices] [class*=table-tbody] tr[data-row-key]", "Счета-фактуры биллингового счета"
        )
        self.INVOICE_TYPE = ElementsList("[id*=panel-invoices] tr[data-row-key] td:nth-child(1)", "Поле 'Тип'")
        self.INVOICE_NUMBER = ElementsList("[id*=panel-invoices] tr[data-row-key] td:nth-child(2)", "Поле 'Номер'")
        self.INVOICE_DATE = ElementsList("[id*=panel-invoices] tr[data-row-key] td:nth-child(3)", "Поле 'Дата'")
        self.INVOICE_AMOUNT = ElementsList(
            "[id*=panel-invoices] tr[data-row-key] td:nth-child(4)", "Поле 'Сумма с налогами'"
        )
        self.INVOICE_TAX = ElementsList("[id*=panel-invoices] tr[data-row-key] td:nth-child(5)", "Поле 'Налоги'")
        self.INVOICE_UNIT = ElementsList("[id*=panel-invoices] tr[data-row-key] td:nth-child(6)", "Поле 'Производство'")
        self.INVOICE_ADJUSTMENT_TAX_INVOICE = ElementsList(
            "[id*=panel-invoices] tr[data-row-key] td:nth-child(7)", "Поле 'Корректируемый СФ'"
        )
        self.INVOICE_ADJUSTMENT_NUMBER = ElementsList(
            "[id*=panel-invoices] tr[data-row-key] td:nth-child(8)", "Поле 'Номер исправления'"
        )
        self.INVOICE_ADJUSTMENT_DATE = ElementsList(
            "[id*=panel-invoices] tr[data-row-key] td:nth-child(9)", "Поле 'Дата исправления'"
        )
        self.INVOICE_ADJUSTED = ElementsList(
            "[id*=panel-invoices] tr[data-row-key] td:nth-child(10)", "Поле 'Откорректированно'"
        )
        self.INVOICE_BALANCE = ElementsList("[id*=panel-invoices] tr[data-row-key] td:nth-child(11)", "Поле 'Остаток'")
        self.NO_INVOICE_BLOCK = Element(
            "[id*=panel-invoices] [class*=table-expanded-row-fixed]", "Блок 'Нет счетов-фактур'"
        )

        # DOCUMENTS
        self.DOCUMENT = ElementsList("[id*='panel-documents'] [class*=table-tbody] tr[data-row-key]", "Документ")
        self.NO_DOCUMENT_BLOCK = Element(
            "[id*='panel-documents'] .platform-empty-state-container", "Блок 'Документов пока нет'"
        )

        # LINKED_OPERATIONS
        self.LINKED_OPERATIONS = RadioOrCheckboxBlock(
            "[id*='panel-linked-accounts'] div[class*=radio-group]", "Заголовки связанных операций"
        )
        self.LINKED_OPERATIONS_VALUE_LOADER = ElementsList(
            "//*[contains(@id, 'panel-linked-accounts')] //*[contains(@class, '-spin-sm')]",
            "Лоадер значения связанной операции",
        )
        self.TABLE_ROW_LINKED_OPERATION = ElementsList(
            "[id*=panel-linked-accounts] [class*=table-tbody] [class*=table-row]",
            "Строка таблицы на вкладке 'Связанные операции'",
        )
        self.REPAYMENTS_OBJECT = ElementsList(
            "[id*=panel-linked-accounts] [class*=table-tbody] [class*=table-row] div:nth-child(1)",
            "Таблица 'Погашение', поле 'Объект'",
        )
        self.REPAYMENTS_DATE = ElementsList(
            "[id*=panel-linked-accounts] [class*=table-tbody] [class*=table-row] div:nth-child(2)",
            "Таблица 'Погашение', поле 'Дата'",
        )
        self.REPAYMENTS_AMOUNT = ElementsList(
            "[id*=panel-linked-accounts] [class*=table-tbody] [class*=table-row] div:nth-child(3)",
            "Таблица 'Погашение', поле 'Сумма'",
        )
        self.DEBITED_DATE = ElementsList(
            "[id*=panel-linked-accounts] [class*=table-tbody] [class*=table-row] div:nth-child(1)",
            "Таблица 'Списано', поле 'Дата'",
        )
        self.DEBITED_AMOUNT_AFTER_TAX = ElementsList(
            "[id*=panel-linked-accounts] [class*=table-tbody] [class*=table-row] div:nth-child(2)",
            "Таблица 'Списано', поле 'Сумма с налогом'",
        )
        self.DEBITED_TAX = ElementsList(
            "[id*=panel-linked-accounts] [class*=table-tbody] [class*=table-row] div:nth-child(3)",
            "Таблица 'Списано', поле 'Налог'",
        )
        self.DEBITED_DETAIL = ElementsList(
            "[id*=panel-linked-accounts] [class*=table-tbody] [class*=table-row] div:nth-child(4)",
            "Таблица 'Списано', поле 'Деталь'",
        )
        self.DEBITED_REASON = ElementsList(
            "[id*=panel-linked-accounts] [class*=table-tbody] [class*=table-row] div:nth-child(5)",
            "Таблица 'Списано', поле 'Причина'",
        )
        self.NO_RECORDS_LINKED_OPERATION_FOUND = Element(
            "[id*=panel-linked-accounts] .platform-empty-state-container",
            "Блок 'Записи не найдены' на вкладке 'Связанные операции'",
        )

        # NON_OPERATING_INCOMES_TAB
        self.NO_RECORDS_NON_OPERATING_INCOMES_FOUND = Element(
            "[id*=panel-penalties] .platform-empty-state-container",
            "Блок 'Записи не найдены' на вкладке 'Внереализационные начисления'",
        )

        # BILLING_TASKS_FORM
        self.UPDATE_BILLING_TASKS_BTN = Element(
            "[class*=drawer-open] [class*=drawer-body] [data-icon=Refresh]",
            "Кнопка 'Обновить список заданий биллинга'",
        )
        self.BILLING_TASK = ElementsList("[class*=-table-tbody] tr[class*=table-row]", "Задание биллинга")
        self.TASK_NUMBER_LIST = ElementsList("tr[class*=table-row] td:nth-child(1)", "Список номеров заданий")
        self.TASK_TYPE_LIST = ElementsList("tr[class*=table-row] td:nth-child(2)", "Список типов заданий")
        self.TASK_RUN_DATE_LIST = ElementsList("tr[class*=table-row] td:nth-child(3)", "Список дат запуска")
        self.TASK_STATUS_LIST = ElementsList("tr[class*=table-row] td:nth-child(4)", "Список статусов")
        self.TASK_USER_LIST = ElementsList("tr[class*=table-row] td:nth-child(5)", "Список пользователей")
        self.TASK_BILLING_TYPE_LIST = ElementsList("tr[class*=table-row] td:nth-child(6)", "Список типов биллинга")
        self.TASK_BILLING_DATE_LIST = ElementsList("tr[class*=table-row] td:nth-child(7)", "Список дат счёта")
        self.TASKS_CLOSE_BTN = Element("#_cancel-button", "Кнопка 'Закрыть'")
