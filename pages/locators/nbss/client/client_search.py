from pages.locators.nbss.dynamic_form_elements import DynamicElements
from pages.ui_elements import Element, ElementsList, MultySelect


class ClientSearchElements(DynamicElements):
    def __init__(self) -> None:
        super().__init__()
        self.TITLE = Element("#root h4", "Заголовок страницы")

        self.CUSTOMER_NAME_INPUT = Element("input[class*=input][id*='customerName']", "Поле ввода Клиент")
        self.CUSTOMER_STATUSES = MultySelect("div[class*=-col]:has(input[id*=customerStatusIds])", "Статус клиента")
        self.CUSTOMER_STATUSES_CLEAR_BTN = Element(
            "div[class*=-col]:has(input[id*=customerStatusIds]) [class*=-select-clear]",
            "Кнопка очистки 'Статус клиента'",
        )
        self.ACCOUNT_STATUSES = MultySelect("div[class*=-col]:has(input[id*=accountStatusIds])", "Статус ЛС")
        self.ACCOUNT_STATUSES_CLEAR_BTN = Element(
            "div[class*=-col]:has(input[id*=accountStatusIds]) [class*=-select-clear]",
            "Кнопка очистки 'Статус ЛС'",
        )
        self.ACCOUNT_NUM = ElementsList("//input[@id='search-dynamic-form_accountNumber']", "Лицевой счет")
        self.INN_INPUT = Element("input[id*='search-dynamic-form'][id*='taxIdentificationNumber']", "Поле ввода ИНН")
        self.KPP_INPUT = Element("//input[@id='search-dynamic-form_registrationReasonCode']", "Поле ввода КПП")
        self.ID_DOCUMENT_SERIAL = Element(
            "input[id*='search-dynamic-form'][id*='identificationDocumentSeries']",
            "Поле ввода серии документа",
        )
        self.ID_DOCUMENT_NUM = Element(
            "input[id*='search-dynamic-form'][id*='identificationDocumentNumber']",
            "Поле ввода номера документа",
        )
        self.CONTRACT_STATUS = MultySelect("div[class*=-col]:has(input[id*=agreementStatusIds])", "Статус договора")
        self.CONTRACT_STATUS_CLEAR_BTN = Element(
            "div[class*=-col]:has(input[id*=agreementStatusIds]) [class*=-select-clear]",
            "Кнопка очистки 'Статус договора'",
        )
        self.IP_ADDRESS = Element("#search-dynamic-form_resourceIpAddress", "IP адрес")
        self.ACCESS_LINE_NUMBER = Element("//input[@id='search-dynamic-form_lineNumber']", "Номер Линии")
        self.SERIAL_NUM_EQUIPMENT = Element(
            "//input[@id='search-dynamic-form_equipmentSerialNumber']", "Серийный номер оборудования"
        )
        self.SUBSCRIBER = Element(
            "#search-dynamic-form_subscriptionIdentification",
            "Поле ввода номера телефона абонента",
        )

        self.RESET_BTN = Element(
            "(//div[contains(@class,'platform-toolbar-item')]//button[@type='reset'])[1]", "Очистить"
        )
        self.SEARCH_BTN = Element("//div[not(@data-item-key)]/button[@type='submit']", "Найти")

        # BODY
        self.REFRESH_BTN = Element("button[|title='Обновить'],[|title='Edit address']", "Обновить")
        self.CREATE_CLIENT = Element("#createClient", "Создать клиента")
        self.EXPORT_TO_FILE_BTN = Element(
            "button[|disabledtooltip='Export found records to XLS file'],[|disabledtooltip='Экспортировать найденные записи в XLS файл']",
            "Экспортировать",
        )

        self.FOUNDED_CLIENTS = ElementsList("[class*=-table-tbody] > [class*=-table-row]", "Найденный клиент")

        # BODY_FOUNDED_CLIENT
        self.FOUNDED_FIO = ElementsList("[class*=table-tbody] [class*=table-row] > div:nth-child(1) a", "ФИО клиента")
        self.FOUNDED_CUSTOMER_TYPE = ElementsList(
            "[class*=table-tbody] [class*=table-row] > div:nth-child(2)", "Юр. тип клиента"
        )
        self.FOUNDED_CUSTOMER_STATUS = ElementsList(
            "[class*=table-tbody] [class*=table-row] > div:nth-child(3)", "Статус клиента"
        )
        self.FOUNDED_DOCUMENT = ElementsList("[class*=table-tbody] [class*=table-row] > div:nth-child(4)", "Документ")
        self.FOUNDED_CONTRACT = ElementsList("[class*=table-tbody] [class*=table-row] > div:nth-child(5)", "Договор")
        self.FOUNDED_CONTRACT_STATUS = ElementsList(
            "[class*=table-tbody] [class*=table-row] > div:nth-child(6)", "Статус договора"
        )
        self.FOUNDED_DOCUMENT_NUM = ElementsList(
            "[class*=table-tbody] [class*=table-row] > div:nth-child(7)", "Номер документа"
        )
        self.FOUNDED_ACCOUNT_NUM = ElementsList(
            "[class*=table-tbody] [class*=table-row] > div:nth-child(8)", "Лицевой счет"
        )
        self.FOUNDED_ACCOUNT_NUM_STATUS = ElementsList(
            "[class*=table-tbody] [class*=table-row] > div:nth-child(9)", "Статус ЛС"
        )
        self.FOUNDED_ACCOUNT_NUM_TYPE = ElementsList(
            "[class*=table-tbody] [class*=table-row] > div:nth-child(10)", "Тип ЛС"
        )
        self.FOUNDED_SUBSCRIBER = ElementsList("[class*=table-tbody] [class*=table-row] > div:nth-child(11)", "Абонент")
        self.EXPORT_BTN = Element("(//span[@data-icon='Export'])[1]", "Кнопка эскпорта")
