from playwright.sync_api import Page

from pages.locators.base_elements import BaseElements
from pages.ui_elements import Element, ElementsList


class BillingAccounts(BaseElements):
    """Страница 'Биллинговые счета'"""

    def __init__(self, page: Page):
        super().__init__(page)

        # LEFT_NAV
        self.REFRESH_BTN = Element(
            "(//*[contains(@class, 'platform-scrollable')]/div/div[2]/div[1] //button)[1]",
            "Кнопка 'Обновить'",
            self.page,
        )
        self.BILLING_LAUNCH_BTN = Element(
            "button[variant='default']:nth-child(6)", "Кнопка 'Запуск биллинга'", self.page
        )
        self.BILLING_TASKS_BTN = Element(
            "button[title='Список заданий биллинга']", "Кнопка 'Список заданий биллинга'", self.page
        )
        self.ACCOUNT_NUMS_LIST = ElementsList(
            ".scrollable-body>div div:first-child>p", "Список биллинговых счетов", self.page
        )
        self.ACCOUNT_EMPTY_LIST = Element(
            ".scrollable-body .platform-empty-box-container", "Записи не найдены", self.page
        )
        self.BILL_DATE = ElementsList(
            ".scrollable-body div:nth-child(2) > div:nth-child(2) p", "Дата биллингового счёта", self.page
        )
        self.BILL_AMOUNT_DUE = ElementsList(
            ".scrollable-body div:nth-child(1) > div:nth-child(2) > p", "Задолженность биллингового счёта", self.page
        )
        self.BILL_STATUS = ElementsList(".scrollable-body div[size]", "Статус биллингового счёта", self.page)

        # BILLING_ACCOUNT
        self.BILLING_BTNS = ElementsList(
            ".platform-scrollable div:nth-child(1)>div>div:nth-of-type(2) [variant='default']",
            "Список кнопок биллинга",
            self.page,
        )
        self.PROPERTIES_TAB = Element("[id*=tab-properties]", "Таб 'Свойства'", self.page)
        self.DETAILS_TAB = Element("[id*=tab-details]", "Таб 'Детали'", self.page)
        self.EXECUTE_BTN = ElementsList(".ant-modal-footer button:last-child", "Кнопка 'Выполнить'", self.page)
        self.INVOICES_TAB = Element("[id*=tab-invoices]", "Таб 'Счета-фактуры'", self.page)
        self.DOCUMENTS_TAB = Element("[id*=tab-documents]", "Таб 'Документы'", self.page)
        self.LINKED_OPERATIONS_TAB = Element("[id*=tab-linked-accounts]", "Таб 'Связанные операции'", self.page)
        self.NON_OPERATING_INCOMES_TAB = Element("[id*=tab-penalties]", "Таб 'Внереализационные начисления'", self.page)

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
            "(//*[contains(@id, 'panel-details')] //button)[2]", "Кнопка 'Обновить детали'", self.page
        )
        self.LINKED_INQUIRES_BTN = Element(
            "(//*[contains(@id, 'panel-details')] //button)[4]", "Кнопка 'Связать с заявкой'", self.page
        )
        self.DETAIL = ElementsList("[id*=panel-details] tbody tr", "Деталь биллингового счета", self.page)
        self.DETAIL_CHECKBOX = ElementsList(
            "[id*=panel-details]  tr td:nth-child(1)", "Чекбокс выбора детали", self.page
        )
        self.DETAIL_FIELDS_LIST = ElementsList(
            "[id*=panel-details] tbody tr div", "Поля первой детали биллингового счета", self.page
        )
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
            "[id*=panel-details] tr td:nth-child(12)", "Поле 'Доступно для корректировки'", self.page
        )
        self.DETAIL_LINKED_INQUIRES = ElementsList(
            "[id*=panel-details] tr td:nth-child(13)", "Поле 'Связанные заявки'", self.page
        )
        self.LINKED_INQUIRES_LIST_BTN = ElementsList(
            "[id*=panel-details] tr td:nth-child(13) a", "Кнопка 'Список связанных заявок'", self.page
        )

        # INVOICES
        self.INVOICE = ElementsList("[id*=panel-invoices] tbody tr", "Счета-фактуры биллингового счета", self.page)
        self.INVOICE_TYPE = ElementsList("[id*=panel-invoices] tr td:nth-child(1)", "Поле 'Тип'", self.page)
        self.INVOICE_NUMBER = ElementsList("[id*=panel-invoices] tr td:nth-child(2)", "Поле 'Номер'", self.page)
        self.INVOICE_DATE = ElementsList("[id*=panel-invoices] tr td:nth-child(3)", "Поле 'Дата'", self.page)
        self.INVOICE_AMOUNT = ElementsList(
            "[id*=panel-invoices] tr td:nth-child(4)", "Поле 'Сумма с налогами'", self.page
        )
        self.INVOICE_TAX = ElementsList("[id*=panel-invoices] tr td:nth-child(5)", "Поле 'Налоги'", self.page)
        self.INVOICE_UNIT = ElementsList("[id*=panel-invoices] tr td:nth-child(6)", "Поле 'Производство'", self.page)
        self.INVOICE_ADJUSTMENT_TAX_INVOICE = ElementsList(
            "[id*=panel-invoices] tr td:nth-child(7)", "Поле 'Корректирующая СФ'", self.page
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

        # DOCUMENTS
        self.DOCUMENT = ElementsList("tbody tr", "Документ", self.page)
        self.NO_DOCUMENT_BLOCK = Element(
            "[id*='panel-documents'] .platform-empty-box-container", "Блок 'Документов пока нет'", self.page
        )

        # LINKED_OPERATIONS
        self.LINKED_OPERATIONS_NAME = ElementsList(
            "[id*='panel-linked-accounts'] div:not([class]) div:nth-child(2)>div>p",
            "Название связанной операции",
            self.page,
        )
        self.LINKED_OPERATIONS_VALUE = ElementsList(
            "[id*='panel-linked-accounts'] div:not([class]) div:nth-child(2)>p", "Значение связанной операции", self.page
        )
        self.LINKED_OPERATIONS_VALUE_LOADER = ElementsList(
            "[id*=panel-linked-accounts] .ant-spin-sm", "Лоадер значения связанной операции", self.page
        )
        self.TABLE_ROW_LINKED_OPERATION = ElementsList(
            "[id*=panel-linked-accounts] table tbody tr", "Строка таблицы на вкладке 'Связанные операции'", self.page
        )
        self.NO_RECORDS_LINKED_OPERATION_FOUND = Element(
            "[id*=panel-linked-accounts] .platform-empty-box-container",
            "Блок 'Записи не найдены' на вкладке 'Связанные операции'",
            self.page,
        )

        # NON_OPERATING_INCOMES_TAB
        self.NO_RECORDS_NON_OPERATING_INCOMES_FOUND = Element(
            "[id*=panel-penalties] .platform-empty-box-container",
            "Блок 'Записи не найдены' на вкладке 'Внереализационные начисления'",
            self.page,
        )

        # BILLING_TASKS_FORM
        self.UPDATE_BILLING_TASKS_BTN = Element(
            "(//*[@class='ant-drawer-body'] //button)[1]", "Кнопка 'Обновить список заданий биллинга'", self.page
        )
        self.BILLING_TASK = ElementsList("table tbody tr", "Задание биллинга", self.page)
        self.TASK_NUMBER_LIST = ElementsList("tr td:nth-child(1)", "Список номеров заданий", self.page)
        self.TASK_TYPE_LIST = ElementsList("tr td:nth-child(2) div", "Список типов заданий", self.page)
        self.TASK_RUN_DATE_LIST = ElementsList("tr td:nth-child(3)", "Список дат запуска", self.page)
        self.TASK_STATUS_LIST = ElementsList("tr td:nth-child(4) p", "Список статусов", self.page)
        self.TASK_USER_LIST = ElementsList("tr td:nth-child(5)", "Список пользователей", self.page)
        self.TASK_BILLING_TYPE_LIST = ElementsList("tr td:nth-child(6)", "Список типов биллинга", self.page)
        self.TASK_BILLING_DATE_LIST = ElementsList("tr td:nth-child(7)", "Список дат счёта", self.page)
        self.TASKS_CLOSE_BTN = Element("#_cancel-button", "Кнопка 'Закрыть'", self.page)
