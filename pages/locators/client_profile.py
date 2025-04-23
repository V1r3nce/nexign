import allure
from playwright.sync_api import Page

from common.helpers.checker import wait_that
from pages.locators.dynamic_form_elements import DynamicElements
from pages.ui_elements import Element, ElementsList, Select


class ClientProfile(DynamicElements):
    """Страница /customer-hierarchy-management/customers/{customer_id}/overview
    'Управление клиентскими иерархиями'"""

    def __init__(self, page: Page):
        super().__init__(page)

        self.CLIENT_FIO_BTN = Element("(//*[@class='platform-link-content'])[1]", "Кнопка 'ФИО клиента'", self.page)

        # HEADER
        self.CLIENT_FIO = Element("h3[display='block']", "ФИО клиента", self.page)
        self.CLIENT_STATUS = Element("//h3[@display='block']/..//p", "Статус клиента", self.page)
        self.CLIENT_TYPE = Element("//h3[@display='block']/../div/div", "Тип клиента", self.page)

        # COMMON_ELEMENTS
        self.ADD_BTN = Element("button[title='Добавить']", "Кнопка 'Добавить'", self.page)

        # HEADER_NAV_TAB
        self.OVERVIEW_TAB = Element("[role=tab][id*=tab-overview]", "Таб 'Обзор'", self.page)
        self.CLIENT_TAB = Element("[role=tab][id$=tab-customer]", "Таб 'Клиент'", self.page)
        self.RELATED_PERSONS_TAB = Element("[role=tab][id*=tab-linked-persons]", "Таб 'Связанные лица'", self.page)
        self.CONTRACTS = Element("[role=tab][id*=tab-agreements]", "Таб 'Договоры'", self.page)
        self.PERSONAL_ACCOUNTS_TAB = Element("[role=tab][id*=tab-accounts]", "Таб 'Лицевые счета'", self.page)
        self.CLIENT_GROUPS_TAB = Element("[role=tab][id$=tab-customer-groups]", "Таб 'Группы клиентов'", self.page)
        self.REQUESTS_TAB = Element("[role=tab][id*=tab-inquiries]", "Таб 'Заявки'", self.page)
        self.PRODUCTS_TAB = Element("[role=tab][id*=tab-products]", "Таб 'Продукты'", self.page)

        # LEFT_NAV_TAB
        self.PROPERTIES_TAB = Element(
            ".ant-tabs:nth-of-type(1) .ant-tabs-tab:nth-of-type(1)", "Кнопка 'Свойства'", self.page
        )
        self.ADDRESSES_TAB = Element("//div[contains(text(), 'Адреса')]/parent::div", "Кнопка 'Адреса'", self.page)
        self.TABLE_LINE = ElementsList("//tr", "Строки таблицы", self.page)
        self.TABLE_LINE_MAP_BUTTON = ElementsList("td svg", "Строки таблицы кнопка карты", self.page)
        self.DOCUMENTS_TAB = Element(
            ".ant-tabs:nth-of-type(1) .ant-tabs-tab:nth-of-type(3)", "Кнопка 'Документы'", self.page
        )

        # OVERVIEW_TAB
        self.CREATE_AGREEMENT_BTN = Element(
            ".react-grid-layout > div:nth-child(3) .platform-empty-box-container button",
            "Кнопка 'Создать договор'",
            self.page,
        )
        self.WIDGET = ElementsList(".react-grid-layout > div", "Виджет", self.page)
        self.WIDGET_LABEL = ElementsList(".react-grid-layout > div h4", "Название виджета", self.page)
        self.PERSONAL_ACCOUNT_UPDATE_BTN = Element(
            "(//*[contains(@class, 'react-grid-layout')]/div[2] //button)[2]",
            "Кнопка 'Обновить' для виджета 'Лицевые счета'",
            self.page,
        )
        self.PERSONAL_ACCOUNT_LOADER = Element(
            "//*[contains(@class, 'react-grid-layout')]/div[2]  //*[contains(@class, 'ant-spin-sm')]",
            "Лоадер при обновлении виджета 'Лицевые счета'",
            self.page,
        )
        self.BALANCE = ElementsList(
            "//*[contains(@class, 'react-grid-layout')]/div[2] //p[@color='positive' or @color='negative']",
            "Балансы ЛС",
            self.page,
        )
        self.WIDGET_PERSONAL_ACCOUNT_IDS = ElementsList(
            "//p/preceding-sibling::a[contains(@href, 'account')]", "Лицевые счета клиента", self.page
        )
        self.WIDGET_PERSONAL_ACCOUNT_SUM = ElementsList(
            "//a[contains(@href, 'account')]/parent::div/parent::div/p", "Суммы Лицевых счетов клиента", self.page
        )

        # CLIENT_TAB
        self.EDIT_BTN = Element(".platform-button-icon-left", "Кнопка 'Редактировать'", self.page)
        self.NATIONALITY = Element("input[id*='nationality']", "Страна регистрации", self.page)
        self.GENDER = Element("input[id*='gender']", "Пол", self.page)
        self.DOCUMENT_TYPE = Element("input[id*='documentType']", "Тип документа", self.page)
        self.DOCUMENT_DATE = Element("input[id*='documentDateOfIssue']", "Дата выдачи", self.page)
        self.DOCUMENT_VALID_DATE = Element("input[id*='documentValidFor']", "Дата действия документа", self.page)
        self.BIRTH_DATE = Element("input[id*='birthDate']", "Дата рождения", self.page)
        self.INN = Element("input[id*='taxIdentificationNumber']", "ИНН", self.page)
        self.SNILS = Element("input[id*='INILA']", "СНИЛС", self.page)
        self.PUBLIC_PERSON = Element("#publicOfficial_control input", "Публичное лицо", self.page)
        self.RESIDENT = Element("#isResident_control input", "Резидент", self.page)
        self.SPEAKING_LANGUAGE = Element("#speakingLanguage_control input", "Родной язык", self.page)
        self.BUSINESS_ACTIVITY = Element("input[id*='view_businessActivity']", "Экономическая деятельность", self.page)
        self.NOTE = Element("input[id*='view_note']", "Комментарий", self.page)
        self.TAX_SCHEME = Element("div:has(> label[for*=taxScheme]) .ant-select-selector", "Ставка налога", self.page)
        self.DOCUMENT_SERIAL_AND_NUM = Element("input[id*='documentSeriesAndNumber']", "Номер документа", self.page)

        # ADDRESSES_TAB
        self.REFRESH_BTN = Element("button[|title='Обновить'],[|title='Refresh']", "Кнопка 'Обновить'", self.page)
        self.CLEAR_ALL_FILTER_BTN = Element(
            "button[|title='Очистить все фильтры'],[|title='Clear all filters']",
            "Кнопка очистить все фильтры",
            self.page,
        )
        self.EDIT_ADDRESS = Element(
            "button[|title='Изменить адрес'],[|title='Edit address']", "Кнопка 'Изменить адрес'", self.page
        )
        self.DELETE_ADDRESS = Element(
            "button[|title='Удалить адрес'],[|title='Delete address']", "Кнопка 'Удалить адрес'", self.page
        )
        self.EXPORT_TO_FILE_BTN = Element(
            "button[|disabledtooltip='Export found records to XLS file'],[|disabledtooltip='Экспортировать найденные записи в XLS файл']",
            "Кнопка экспортировать файл",
            self.page,
        )
        self.TABLE_LINE = ElementsList("//tr", "Строки таблицы", self.page)
        self.TABLE_ADDRESS_TYPES = ElementsList("//tr/td[1]", "Строки Тип адреса", self.page)
        self.TABLE_ADDRESSES = ElementsList("//tr/td[2]", "Строки Адреса", self.page)
        self.TABLE_MAP_CELLS = ElementsList("//tr/td[3]", "Строки под кнопку карты", self.page)
        self.TABLE_LINE_MAP_BUTTON = ElementsList("td svg", "Строки таблицы кнопка карты", self.page)
        self.SETTING_BTN = Element("button.ant-dropdown-trigger", "Кнопка 'Настройка колонок'", self.page)
        self.SETTING_OPTIONS = ElementsList("input.ant-checkbox-input", "Чекбоксы 'Настройка колонок'", self.page)
        self.TYPE_SORT_BTN = Element(
            "//span[contains(text(), 'Тип')]/parent::div[contains(@class, 'sorters')]",
            "Кнопка сортировки 'Тип'",
            self.page,
        )
        self.TYPE_FILTER_DROPDOWN_BTN = Select("tr th .ant-select-selector", "Кнопка открыть фильтр 'Тип'", self.page)
        self.TYPE_FILTER_OPTIONS = ElementsList(
            ".rc-virtual-list .ant-select-item-option", "Опции фильтра 'Тип'", self.page
        )
        self.TYPE_FILTER_CHOOSE_ALL_BTN = Element(
            "//p[contains(text(), 'Выбрать все')]", "Кнопка 'Выбрать все' фильтр Тип", self.page
        )
        self.SEARCH_ADDRESS_INPUT = Element("//tr/th[2]//input", "Поле поиска адреса", self.page)

        # RELATED_PERSONS_TAB
        self.ADD_RELATED_PERSON_BTN = Element(
            ".linkedPerson_list .platform-button-icon-left", "Кнопка 'Добавить' связанное лицо", self.page
        )
        self.FILTER_SETTINGS = Element(
            "button[|title='Найстроки фильтра'],[|title='Filter settings']", "Кнопка 'Настройки фильтра'", self.page
        )
        self.CLEAR_FILTER_BTN = Element(
            "button[|title='Сбросить'],[|title='Clear']", "Кнопка 'Сбросить фильтр'", self.page
        )
        self.DELETE_PERSON = Element(".linkedPerson_list button:nth-of-type(3)", "Кнопка 'Удалить'", self.page)

        self.RELATED_PERSONS = ElementsList(
            '.scrollable-body > div p:not([color="interface15"])', "Связанные лица", self.page
        )

        self.MAIN_DATA_EDIT_BTN = Element(
            "(//div[contains(@class, 'platform-scrollable')])[3]/div[1]//button",
            "Редактировать 'Основные данные'",
            self.page,
        )
        self.RELATED_PERSON_NAME = Element(
            "//div[contains(@class, 'linkedPerson_list')]//div[contains(@style, 'will-change')]/div[2]//p",
            "Название 'Связанного лица'",
            self.page,
        )
        self.RELATED_PERSON_BENEFICIARY_NAME = Element(
            "[id='beneficiary-function-impersonal-view_name']",
            "Поле именования Выгодоприобретателя Связанного лица",
            self.page,
        )
        self.RELATED_SPEAKING_LANGUAGE = Element("input[id*=speakingLanguage]", "Язык общения", self.page)
        self.RELATED_POSITION = Element("input[id*=position]", "Должность", self.page)
        self.RELATED_NOTE = Element("[id*=view_note]", "Комментарий", self.page)

        self.ADDRESSES_EDIT_BTN = Element(
            "//div[@id='rc-tabs-0-panel-linked-persons']//div[contains(@class, 'ant-collapse-item')][2]//button",
            "Редактировать 'Основные данные'",
            self.page,
        )
        self.EXPAND_RELATED_ADDRESS_BTN = Element(
            "//div[contains(@class, 'ant-collapse-item')][2]//div[@class='ant-collapse-expand-icon']",
            "Кнопка открыть адреса 'Связанного лица'",
            self.page,
        )
        self.RELATED_ADDRESS = Element(
            "//div[contains(@class, 'ant-collapse-item')][2]//div[@class='ant-collapse-content-box']//div/p[2]",
            "Адреса 'Связанного лица'",
            self.page,
        )

        self.CONTACT_DATA_EDIT_BTN = Element(
            "((//div[contains(@class, 'platform-collapse')])//button)[1]", "Редактировать контакты", self.page
        )
        self.ADDRESS_EDIT_BTN = Element(
            "((//div[contains(@class, 'platform-collapse')])//button)[2]", "Редактировать адреса", self.page
        )
        self.RELATED_MOBILE_PHONE = Element(
            "//p[.='Сотовый телефон']/following-sibling::*/p", "Телефон 'Связанного лица'", self.page
        )

        self.RELATED_EMAIL = Element("a[href*='mail']", "E-mail 'Связанного лица'", self.page)
        # PERSONAL_ACCOUNTS_TAB
        self.ADD_PERSONAL_ACCOUNT_BTN = Element(
            "div[id*=panel-accounts] .platform-button-icon-left", "Кнопка 'Добавить' лицевой счет", self.page
        )
        self.EDIT_DETAILS_ACCOUNT_BTN = Element(
            ".platform-button-icon-left", "Кнопка 'Редактировать' лицевой счет", self.page
        )
        self.PAYMENT_METHOD_FLD = Element("(//div[@id='payMethod_control']//input)[1]", "Поле 'Способ оплаты", self.page)
        self.CURRENT_PERSONAL_ACCOUNT_LINK = Element(
            "[href*='accounts']", "Кнопка-ссылка на текущий Лицевой счет клиента", self.page
        )
        self.CURRENT_AGREEMENT_LINK = Element(
            "[href*='agreements']", "Кнопка-ссылка на текущий Лицевой счет клиента", self.page
        )
        self.CURRENT_CLIENT_LINK = Element("[href*='overview']", "Кнопка-ссылка на текущего клиента", self.page)
        # REQUESTS_TAB
        self.UPDATE_REQUESTS_BTN = Element("(//*[@id='inquiries-list'] //button)[1]", "Кнопка 'Обновить'", self.page)
        self.REQUESTS = ElementsList("tr[data-row-key]", "Заявки", self.page)
        self.REQUEST_NUMBER = ElementsList("tr[data-row-key] td:nth-child(1) a", "Номера заявок", self.page)
        self.REQUEST_TYPE = ElementsList("tr[data-row-key] td:nth-child(2) div", "Типы заявок", self.page)
        self.REQUEST_STATUS = ElementsList("tr[data-row-key] td:nth-child(3) p", "Статусы заявок", self.page)

        # PRODUCTS_TAB
        self.PRODUCTS_UPDATE_BTN = Element(
            "(//*[contains(@id, 'panel-products')]/div[1]/div[1] //button)[3]", "Кнопка 'Обновить'", self.page
        )
        self.PRODUCTS_LIST = ElementsList(
            "(//*[contains(@class, 'ant-collapse-borderless')])[1]/*[contains(@class, 'ant-collapse-item')]",
            "Развернутые и свернутые Продукты клиента",
            self.page,
        )
        self.PRODUCTS_HEADER_LIST = ElementsList(
            "(//*[contains(@class, 'ant-collapse-borderless')])[1]/*[contains(@class, 'ant-collapse-item')]/div[1]",
            "Заголовки продуктов клиента",
            self.page,
        )
        self.PRODUCTS_LIST_STATUS_COLOR = ElementsList(
            "//a[contains(@href,'/rm-ui/all#')]/parent::div/div", "Цвет статуса абонента", self.page
        )
        self.SUBSCRIBER = ElementsList(".ant-collapse-item-active > .ant-collapse-header a", "Абонент", self.page)
        self.PRODUCTS = ElementsList("[id*=panel-products] [role=tab]", "Продукты", self.page)
        self.PRODUCT_NAME = ElementsList(
            ".platform-grid-container > div > div > p[color=accent]", "Названия продуктов", self.page
        )
        self.PRODUCTS_CONTRACT_NUM = ElementsList(
            "(//div[contains(@id, 'panel-products')] //div[@role='tab'] //button)[1]", "Договор продукта", self.page
        )
        self.PRODUCTS_PERSONAL_ACCOUNT_NUM = ElementsList(
            "(//div[contains(@id, 'panel-products')] //div[@role='tab'] //button)[2]//p",
            "Лицевой счет продукта",
            self.page,
        )
        self.PRODUCTS_SUBSCRIPTION_FEE = ElementsList(
            "(//div[contains(@id, 'panel-products')] //div[@role='tab'] //div[contains(@class, 'platform-grid-container')])[3] /div/div",
            "Абонентская плата",
            self.page,
        )
        self.PRODUCTS_DETAILS_BTN = Element(
            '[data-menu-id*="OpenConsuming"] [type="button"]', "Кнопка редактирования продукта", self.page
        )
        self.PRODUCTS_STATUS_COLOR = ElementsList(
            "//*[contains(@class, 'platform-grid-container')]/div/div/p[@color='accent']/parent::div/div",
            "Цвет статуса продукта",
            self.page,
        )
        self.OPTION_STATUS_COLOR = ElementsList(
            "(//*[contains(@class, 'platform-grid-container')]/div/div/p[@color='accent']/parent::div/div)",
            "Цвет статуса Опции",
            self.page,
        )
        self.PRODUCTS_DETAILS_OPEN_BTN = Element(
            "(//div[@role='tablist'] //button) [4]", "Кнопка выпадашки для кнопки редактирования продукта", self.page
        )
        self.TURN_OFF_BTN = Element(
            "(//*[contains(@class, 'ant-dropdown')]//button)[1]", "Кнопка 'Отключить'", self.page
        )
        self.GO_TO_CONSUMPTION_DETAILS = Element(
            "(//*[contains(@class, 'ant-dropdown')] //button)[2]", "Кнопка 'Перейти к деталям потребления'", self.page
        )
        self.PRODUCTS_OPTIONS_OPEN_BTN = Element(
            "(//*[contains(@class, 'ant-collapse-item-active')] //button)[2]",
            "Кнопка выпадашки для кнопки добавления опций",
            self.page,
        )
        self.PRODUCTS_OPTIONS_ADD_BTN = Element('[data-menu-id*="ADD_OPTION"]', 'Кнопка "Добавить Опцию"', self.page)
        self.CURRENT_OPTION_PRODUCT = ElementsList(
            '[class="ant-collapse-item ant-collapse-item-disabled ant-collapse-no-arrow"]',
            "Подключенные опции у продукта",
            self.page,
        )
        self.OPEN_OPTIONS_BTN = Element(
            "(//div[@class='ant-collapse-expand-icon'] //span) [2]", "Кнопка Открыть опции продукта", self.page
        )

    @allure.step("Обновить список и проверить статус")
    def update_and_check_status_color(self, type_offer: str) -> bool | None:
        if type_offer == "product":
            self.PRODUCTS_UPDATE_BTN.click()
            return self.PRODUCTS_STATUS_COLOR[0].get_color() == "rgb(0, 173, 33)"
        elif type_offer == "request":
            self.UPDATE_REQUESTS_BTN.click()
            return self.REQUEST_STATUS[2].get_color() != "rgb(0, 173, 33)"
        elif type_offer == "option":
            return self.OPTION_STATUS_COLOR[1].get_color() == "rgb(0, 173, 33)"
        raise TypeError("Передан неверный тип объекта")

    @allure.step("Проверка статуса сущности")
    def wait_to_be_enabled(self, type_offer: str) -> None:
        wait_that(
            lambda: self.update_and_check_status_color(type_offer),
            message="Статус сущности не становится Активным",
            timeout=50,
            exception=TimeoutError,
            sleep_seconds=2,
        )
