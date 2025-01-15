from playwright.sync_api import Page

from pages.locators.dynamic_form_elements import DynamicElements
from pages.ui_elements import Element, ElementsList, Select


class ClientProfile(DynamicElements):
    """Страница /customer-hierarchy-management/customers/{customer_id}/overview
    'Управление клиентскими иерархиями'"""
    def __init__(self, page: Page):
        super().__init__(page)

        #HEADER
        self.CLIENT_FIO = Element("h3[display='block']", "ФИО клиента", self.page)
        self.CLIENT_STATUS = Element("//h3[@display='block']/..//p", "Статус клиента", self.page)
        self.CLIENT_TYPE = Element("//h3[@display='block']/../div/div", "Тип клиента", self.page)

        #COMMON_ELEMENTS
        self.ADD_BTN = Element("button[title='Добавить']", "Кнопка 'Добавить'", self.page)

        #HEADER_NAV_TAB
        self.OVERVIEW_TAB = Element("(//div[@role='tablist'])[1] //div[contains(@class, 'ant-tabs-tab')][1]", "Таб 'Обзор'", self.page)
        self.CLIENT_TAB = Element("(//div[@role='tablist'])[1] //div[contains(@class, 'ant-tabs-tab')][2]", "Таб 'Клиент'", self.page)
        self.RELATED_PERSONS_TAB = Element("(//div[@role='tablist'])[1] //div[contains(@class, 'ant-tabs-tab')][3]",
                                           "Таб 'Связанные лица'", self.page)
        self.CONTRACTS = Element("(//div[@role='tablist'])[1] //div[contains(@class, 'ant-tabs-tab')][4]", "Таб 'Договоры'", self.page)
        self.PERSONAL_ACCOUNTS_TAB = Element("(//div[@role='tablist'])[1] //div[contains(@class, 'ant-tabs-tab')][5]", "Таб 'Лицевые счета'", self.page)
        self.REQUESTS_TAB = Element("(//div[@role='tablist'])[1] //div[contains(@class, 'ant-tabs-tab')][6]", "Таб 'Заявки'", self.page)
        self.PRODUCTS_TAB = Element("(//div[@role='tablist'])[1] //div[contains(@class, 'ant-tabs-tab')][7]", "Таб 'Продукты'", self.page)

        #LEFT_NAV_TAB
        self.PROPERTIES_TAB = Element(".ant-tabs:nth-of-type(1) .ant-tabs-tab:nth-of-type(1)", "Кнопка 'Свойства'", self.page)
        self.ADDRESSES_TAB = Element("//div[contains(text(), 'Адреса')]/parent::div",
                                     "Кнопка 'Адреса'", self.page)
        self.TABLE_LINE = ElementsList("//tr", "Строки таблицы", self.page)
        self.TABLE_LINE_MAP_BUTTON = ElementsList("td svg", "Строки таблицы кнопка карты", self.page)
        self.DOCUMENTS_TAB = Element(".ant-tabs:nth-of-type(1) .ant-tabs-tab:nth-of-type(3)", "Кнопка 'Документы'", self.page)

        #OVERVIEW_TAB
        WIDGET = ".react-grid-layout > div:nth-child({widget_num})"
        WIDGET_LABEL = ".react-grid-layout > div:nth-child({widget_num}) h4"

        #CLIENT_TAB
        EDIT_BTN = ".platform-button__icon_left"
        self.GENDER = Element("input[id*='gender']", "Пол", self.page)
        self.DOCUMENT_TYPE = Element("input[id*='documentType']", "Тип документа", self.page)
        self.DOCUMENT_DATE = Element("input[id*='documentDateOfIssue']", "Дата выдачи", self.page)
        self.DOCUMENT_VALID_DATE = Element("input[id*='documentValidFor']", "Дата действия документа", self.page)
        self.BIRTH_DATE = Element("input[id*='birthDate']", "Дата рождения", self.page)
        self.REGISTRATION_ADDRESS = Element("input[id*='registrationAddress']", "Адрес регистрации", self.page)
        self.INN = Element("input[id*='taxIdentificationNumber']", "ИНН", self.page)
        self.SNILS = Element("input[id*='INILA']", "СНИЛС", self.page)
        self.PUBLIC_PERSON = Element("#publicOfficial_control input", "Публичное лицо", self.page)
        self.RESIDENT = Element("#isResident_control input", "Резидент", self.page)
        self.SPEAKING_LANGUAGE = Element("#speakingLanguage_control input", "Родной язык", self.page)
        self.BUSINESS_ACTIVITY = Element("input[id*='view_businessActivity']", "Экономическая деятельность", self.page)
        self.NOTE = Element("input[id*='view_note']", "Комментарий", self.page)
        self.TAX_SCHEME = Element("input[id*='taxScheme']", "Ставка налога", self.page)

        #ADDRESSES_TAB
        REFRESH_BTN = "button[|title='Обновить'],[|title='Refresh']"
        CLEAR_ALL_FILTER_BTN = "button[|title='Очистить все фильтры'],[|title='Clear all filters']"
        self.EDIT_ADDRESS = Element("button[|title='Изменить адрес'],[|title='Edit address']",
                                    "Кнопка 'Изменить адрес'", self.page)
        DELETE_ADDRESS = "button[|title='Удалить адрес'],[|title='Delete address']"
        EXPORT_TO_FILE_BTN = "button[|disabledtooltip='Export found records to XLS file'],[|disabledtooltip='Экспортировать найденные записи в XLS файл']"
        self.TABLE_LINE = ElementsList("//tr", "Строки таблицы", self.page)
        self.TABLE_ADDRESS_TYPES = ElementsList("//tr/td[1]", "Строки Тип адреса", self.page)
        self.TABLE_ADDRESSES = ElementsList("//tr/td[2]", "Строки Адреса", self.page)
        self.TABLE_MAP_CELLS = ElementsList("//tr/td[3]", "Строки под кнопку карты", self.page)
        self.TABLE_LINE_MAP_BUTTON = ElementsList("td svg", "Строки таблицы кнопка карты", self.page)
        self.SETTING_BTN = Element("button.ant-dropdown-trigger", "Кнопка 'Настройка колонок'", self.page)
        self.SETTING_OPTIONS = ElementsList("input.ant-checkbox-input", "Чекбоксы 'Настройка колонок'", self.page)
        self.TYPE_SORT_BTN = Element("//span[contains(text(), 'Тип')]/parent::div[contains(@class, 'sorters')]",
                                     "Кнопка сортировки 'Тип'", self.page)
        self.TYPE_FILTER_DROPDOWN_BTN = Select("tr th .ant-select-selector", "Кнопка открыть фильтр 'Тип'", self.page)
        self.TYPE_FILTER_OPTIONS = ElementsList(".rc-virtual-list .ant-select-item-option", "Опции фильтра 'Тип'",
                                                self.page)
        self.TYPE_FILTER_CHOOSE_ALL_BTN = Element("//p[contains(text(), 'Выбрать все')]",
                                                  "Кнопка 'Выбрать все' фильтр Тип", self.page)
        self.SEARCH_ADDRESS_INPUT = Element("//tr/th[2]//input", "Поле поиска адреса", self.page)

        #RELATED_PERSONS_TAB
        FILTER_SETTINGS = "button[|title='Найстроки фильтра'],[|title='Filter settings']"
        CLEAR_FILTER_BTN = "button[|title='Сбросить'],[|title='Clear']"
        DELETE_PERSON = ".linkedPerson_list button:nth-of-type(3)"

        self.RELATED_PERSONS = ElementsList('.scrollable-body > div p:not([color="interface15"])', 'Связанные лица',
                                            self.page)

        self.MAIN_DATA_EDIT_BTN = Element("(//div[contains(@class, 'platform-scrollable')])[3]/div[1]//button",
                                          "Редактировать 'Основные данные'", self.page)
        self.RELATED_PERSON_NAME = Element("#contact-person-function-impersonal-view_name",
                                           "Название 'Связанного лица'", self.page)
        RELATED_SPEAKING_LANGUAGE = "#contact-person-function-impersonal-view_speakingLanguage"
        RELATED_SPECIALIZATIONS = ".ant-select-selection-overflow"
        RELATED_NOTE = "#contact-person-function-impersonal-view_note"

        self.ADDRESSES_EDIT_BTN = Element("(//div[contains(@class, 'platform-scrollable')])[3]/div[2]//button",
                                          "Редактировать 'Основные данные'", self.page)
        self.RELATED_ADDRESS = Element(".platform-grid__item > [color='interface15'] + p",
                                       "Адреса 'Связанного лица'", self.page)

        CONTACT_DATA_EDIT_BTN = "(//div[contains(@class, 'platform-scrollable')])[3]/div[3]//button" # XPATH
        self.RELATED_MOBILE_PHONE = Element("article", "Телефон 'Связанного лица'", self.page)
        self.RELATED_EMAIL = Element("a[href*='mail']", "E-mail 'Связанного лица'", self.page)
