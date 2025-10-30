from playwright.sync_api import Page

from pages.locators.nbss.dynamic_form_elements import DynamicElements
from pages.ui_elements import Element, ElementsList, MultySelect


class ClientSearch(DynamicElements):
    def __init__(self, page: Page):
        super().__init__(page)
        self.TITLE = Element("#root h4", "Заголовок страницы", self.page)

        self.CUSTOMER_NAME_INPUT = Element(
            "input[id*='search-dynamic-form'][id*='customerName']", "Поле ввода Клиент", self.page
        )
        self.CUSTOMER_STATUSES = MultySelect(
            "div[class*=-col]:has(input[id*=customerStatusIds])", "Статус клиента", self.page
        )
        self.CUSTOMER_STATUSES_CLEAR_BTN = Element(
            "div[class*=-col]:has(input[id*=customerStatusIds]) [class*=-select-clear]",
            "Кнопка очистки 'Статус клиента'",
            self.page,
        )
        self.ACCOUNT_STATUSES = MultySelect("div[class*=-col]:has(input[id*=accountStatusIds])", "Статус ЛС", self.page)
        self.ACCOUNT_STATUSES_CLEAR_BTN = Element(
            "div[class*=-col]:has(input[id*=accountStatusIds]) [class*=-select-clear]",
            "Кнопка очистки 'Статус ЛС'",
            self.page,
        )
        self.INN_INPUT = Element(
            "input[id*='search-dynamic-form'][id*='taxIdentificationNumber']", "Поле ввода ИНН", self.page
        )
        self.ID_DOCUMENT_SERIAL = Element(
            "input[id*='search-dynamic-form'][id*='identificationDocumentSeries']",
            "Поле ввода серии документа",
            self.page,
        )
        self.ID_DOCUMENT_NUM = Element(
            "input[id*='search-dynamic-form'][id*='identificationDocumentNumber']",
            "Поле ввода номера документа",
            self.page,
        )
        self.CONTRACT_STATUS = MultySelect(
            "div[class*=-col]:has(input[id*=agreementStatusIds])", "Статус договора", self.page
        )
        self.CONTRACT_STATUS_CLEAR_BTN = Element(
            "div[class*=-col]:has(input[id*=agreementStatusIds]) [class*=-select-clear]",
            "Кнопка очистки 'Статус договора'",
            self.page,
        )

        self.RESET_BTN = Element("button[type='reset']", "Очистить", self.page)
        self.SEARCH_BTN = Element("//div[not(@data-item-key)]/button[@type='submit']", "Найти", self.page)

        # BODY
        self.REFRESH_BTN = Element("button[|title='Обновить'],[|title='Edit address']", "Обновить", self.page)
        self.CREATE_CLIENT = Element("#createClient", "Создать клиента", self.page)
        self.EXPORT_TO_FILE_BTN = Element(
            "button[|disabledtooltip='Export found records to XLS file'],[|disabledtooltip='Экспортировать найденные записи в XLS файл']",
            "Экспортировать",
            self.page,
        )

        self.FOUNDED_CLIENTS = ElementsList("[class*=-table-tbody] > [class*=-table-row]", "Найденный клиент", self.page)

        # BODY_FOUNDED_CLIENT
        self.FOUNDED_FIO = ElementsList(
            "[class*=table-tbody] [class*=table-row] > div:nth-child(1) a", "ФИО клиента", self.page
        )
        self.FOUNDED_CUSTOMER_TYPE = ElementsList(
            "[class*=table-tbody] [class*=table-row] > div:nth-child(2)", "Юр. тип клиента", self.page
        )
        self.FOUNDED_CUSTOMER_STATUS = ElementsList(
            "[class*=table-tbody] [class*=table-row] > div:nth-child(3)", "Статус клиента", self.page
        )
        self.FOUNDED_DOCUMENT = ElementsList(
            "[class*=table-tbody] [class*=table-row] > div:nth-child(4)", "Документ", self.page
        )
        self.FOUNDED_CONTRACT = ElementsList(
            "[class*=table-tbody] [class*=table-row] > div:nth-child(5)", "Договор", self.page
        )
        self.FOUNDED_CONTRACT_STATUS = ElementsList(
            "[class*=table-tbody] [class*=table-row] > div:nth-child(6)", "Статус договора", self.page
        )
        self.FOUNDED_DOCUMENT_NUM = ElementsList(
            "[class*=table-tbody] [class*=table-row] > div:nth-child(7)", "Номер документа", self.page
        )
        self.FOUNDED_ACCOUNT_NUM = ElementsList(
            "[class*=table-tbody] [class*=table-row] > div:nth-child(8)", "Лицевой счет", self.page
        )
        self.FOUNDED_ACCOUNT_NUM_STATUS = ElementsList(
            "[class*=table-tbody] [class*=table-row] > div:nth-child(9)", "Статус ЛС", self.page
        )
        self.FOUNDED_ACCOUNT_NUM_TYPE = ElementsList(
            "[class*=table-tbody] [class*=table-row] > div:nth-child(10)", "Тип ЛС", self.page
        )
        self.FOUNDED_SUBSCRIBER = ElementsList(
            "[class*=table-tbody] [class*=table-row] > div:nth-child(11)", "Абонент", self.page
        )
