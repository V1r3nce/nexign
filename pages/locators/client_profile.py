from playwright.sync_api import Page

from pages.locators.dynamic_form_elements import DynamicElements
from pages.locators.ui_elements import Element, ElementsList


class ClientProfile(DynamicElements):
    """Страница /customer-hierarchy-management/customers/{customer_id}/overview
    'Управление клиентскими иерархиями'"""
    def __init__(self, page: Page):
        super().__init__(page)

        #HEADER
        CLIENT_FIO = "h3[display='block']"
        CLIENT_STATUS = "//h3[@display='block']/..//p" #XPATH
        CLIENT_TYPE = "//h3[@display='block']/../div/div" #XPATH

        #COMMON_ELEMENTS
        self.ADD_BTN = Element("button:has(.platform-button__icon_left)", "Кнопка 'Добавить'", self.page)

        #HEADER_NAV_TAB
        OVERVIEW_TAB = ".ant-tabs:nth-of-type(2) .ant-tabs-tab:nth-of-type(1)"
        self.CLIENT_TAB = Element(".ant-tabs:nth-of-type(2) .ant-tabs-tab:nth-of-type(2)", "Таб 'Клиент'", self.page)
        self.RELATED_PERSONS_TAB = Element(".ant-tabs:nth-of-type(2) .ant-tabs-tab:nth-of-type(3)",
                                           "Таб 'Связанные лица'", self.page)
        CONTRACTS = ".ant-tabs:nth-of-type(2) .ant-tabs-tab:nth-of-type(4)"
        PERSONAL_ACCOUNTS_TAB = ".ant-tabs:nth-of-type(2) .ant-tabs-tab:nth-of-type(5)"
        REQUESTS_TAB = ".ant-tabs:nth-of-type(2) .ant-tabs-tab:nth-of-type(6)"
        PRODUCTS_TAB = ".ant-tabs:nth-of-type(2) .ant-tabs-tab:nth-of-type(7)"

        #LEFT_NAV_TAB
        PROPERTIES_TAB = ".ant-tabs:nth-of-type(1) .ant-tabs-tab:nth-of-type(1)"
        self.ADDRESSES_TAB = Element(".ant-tabs:nth-of-type(1) .ant-tabs-tab:nth-of-type(2)",
                                     "Кнопка 'Адреса'", self.page)
        DOCUMENTS_TAB = ".ant-tabs:nth-of-type(1) .ant-tabs-tab:nth-of-type(3)"

        #OVERVIEW_TAB
        WIDGET = ".react-grid-layout > div:nth-child({widget_num})"
        WIDGET_LABEL = ".react-grid-layout > div:nth-child({widget_num}) h4"

        #CLIENT_TAB
        EDIT_BTN = ".platform-button__icon_left"

        #ADDRESSES_TAB
        REFRESH_BTN = "button[|title='Обновить'],[|title='Refresh']"
        CLEAR_ALL_FILTER_BTN = "button[|title='Очистить все фильтры'],[|title='Clear all filters']"
        EDIT_ADDRESS = "button[|title='Изменить адрес'],[|title='Edit address']"
        DELETE_ADDRESS = "button[|title='Удалить адрес'],[|title='Delete address']"
        EXPORT_TO_FILE_BTN = "button[|disabledtooltip='Export found records to XLS file'],[|disabledtooltip='Экспортировать найденные записи в XLS файл']"
        self.TABLE_LINE = ElementsList("//tr", "Строки таблицы", self.page)
        self.TABLE_LINE_MAP_BUTTON = ElementsList("td svg", "Строки таблицы кнопка карты", self.page)
        self.SETTING_BTN = Element("button.ant-dropdown-trigger", "Кнопка 'Настройка колонок'", self.page)
        self.SETTING_OPTIONS = ElementsList("input.ant-checkbox-input", "Чекбоксы 'Настройка колонок'", self.page)

        COLUMN_SETTINGS = "button[|title='Настройка колонок'],[|title='Column settings']"

        ADDED_ADDRESSES = ".ant-table-tbody tr:nth-child({address_num})"

        #RELATED_PERSONS_TAB
        FILTER_SETTINGS = "button[|title='Найстроки фильтра'],[|title='Filter settings']"
        CLEAR_FILTER_BTN = "button[|title='Сбросить'],[|title='Clear']"
        DELETE_PERSON = ".linkedPerson_list button:nth-of-type(3)"

        RELATED_PERSONS = ".scrollable-body > div:nth-child({person_num})"

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
        RELATED_MOBILE_PHONE = "article"
        RELATED_EMAIL = "a[href*='mail']"
