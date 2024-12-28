from playwright.sync_api import Page

from pages.locators.dynamic_form_elements import DynamicElements
from pages.ui_elements import Element, ElementsList, MultySelect


class ClientSearch(DynamicElements):
    """Страница /chm-search 'Поиск'"""
    def __init__(self, page: Page):
        super().__init__(page)
        #LEFT_BAR
        self.CUSTOMER_STATUSES = Element("#customerStatusIds_control", "Статус клиента", self.page)
        self.ACCOUNT_STATUSES = MultySelect("#accountStatusIds_control", "Статус ЛС", self.page)
        self.CONTRACT_STATUS = Element("#agreementStatusIds_control", "Статус договора", self.page)

        self.RESET_BTN = Element("button[type='reset']", "Очистить", self.page)
        self.SEARCH_BTN = Element("button[type='submit']", "Найти", self.page)

        #BODY
        self.REFRESH_BTN = Element("button[|title='Обновить'],[|title='Edit address']", "Обновить", self.page)
        self.CREATE_CLIENT = Element("#createClient", "Создать клиента", self.page)
        self.EXPORT_TO_FILE_BTN = Element("button[|disabledtooltip='Export found records to XLS file'],[|disabledtooltip='Экспортировать найденные записи в XLS файл']", "Экспортировать", self.page)

        self.FOUNDED_CLIENTS = ElementsList(".ant-table-tbody tr", "Найденный клиент", self.page)

        #BODY_FOUNDED_CLIENT
        self.FOUNDED_FIO = ElementsList(".ant-table-tbody tr td:nth-child(1)", "ФИО клиента", self.page)
        self.FOUNDED_CUSTOMER_TYPE = ElementsList(".ant-table-tbody tr td:nth-child(2)", "Юр. тип клиента", self.page)
        self.FOUNDED_CUSTOMER_STATUS = ElementsList(".ant-table-tbody tr td:nth-child(3)", "Статус клиента", self.page)
        self.FOUNDED_DOCUMENT = ElementsList(".ant-table-tbody tr td:nth-child(4)", "Документ", self.page)
        self.FOUNDED_CONTRACT = ElementsList(".ant-table-tbody tr td:nth-child(5)", "Договор", self.page)
        self.FOUNDED_CONTRACT_STATUS = ElementsList(".ant-table-tbody tr td:nth-child(6)", "Статус договора", self.page)
        self.FOUNDED_DOCUMENT_NUM = ElementsList(".ant-table-tbody tr td:nth-child(7)", "Номер документа", self.page)
        self.FOUNDED_ACCOUNT_NUM = ElementsList(".ant-table-tbody tr td:nth-child(8)", "Лицевой счет", self.page)
        self.FOUNDED_ACCOUNT_NUM_STATUS = ElementsList(".ant-table-tbody tr td:nth-child(9)", "Статус ЛС", self.page)
        self.FOUNDED_ACCOUNT_NUM_TYPE = ElementsList(".ant-table-tbody tr td:nth-child(10)", "Тип ЛС", self.page)
        self.FOUNDED_SUBSCRIBER = ElementsList(".ant-table-tbody tr td:nth-child(11)", "Абонент", self.page)