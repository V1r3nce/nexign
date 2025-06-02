import allure
from playwright.sync_api import Page

from common.helpers.checker import wait_that
from pages.locators.dynamic_form_elements import DynamicElements, DynamicForms
from pages.ui_elements import Autocomplete, DatePicker, Dropdown, Element, ElementsList, Select


class ClientProfile(DynamicElements):
    """Страница /customer-hierarchy-management/customers/{customer_id}/overview
    'Управление клиентскими иерархиями'"""

    def __init__(self, page: Page):
        super().__init__(page)

        self.CLIENT_FIO_BTN = Element(
            "(//*[contains(@class, 'platform-text-link')])[1]", "Кнопка 'ФИО клиента'", self.page
        )

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
        self.SEGMENTS_TAB = Element("[role=tab][id$=tab-segments]", "Кнопка 'Сегменты'", self.page)
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

        # PERSONAL_DATA_TAB
        self.FIO = Element("#customer-individual-view_fio", "Поле ФИО", self.page)
        self.PERSONAL_DATA_LOADER = Element(
            "#customer-individual-view span[class*='spin-dot']", "Лоадер таблицы Персональные данные", self.page
        )

        # CLIENT_TAB
        self.EDIT_BTN = Element(".platform-button-icon-left", "Кнопка 'Редактировать'", self.page)
        self.ORG_NAME = Element("input[id*='organization-view_name']", "Наименование", self.page)
        self.FIO = Element("input[id*='view_fio']", "ФИО", self.page)
        self.NATIONALITY = Element("input[id*='nationality']", "Страна регистрации", self.page)
        self.GENDER = Element("input[id*='gender']", "Пол", self.page)
        self.DOCUMENT_TYPE = Element("input[id*='documentType']", "Тип документа", self.page)
        self.DOCUMENT_DATE = Element("input[id*='documentDateOfIssue']", "Дата выдачи", self.page)
        self.DOCUMENT_VALID_DATE = Element("input[id*='documentValidFor']", "Дата действия документа", self.page)
        self.BIRTH_DATE = Element("input[id*='birthDate']", "Дата рождения", self.page)
        self.COUNTRY = Element("#nationality_control input", "Страна регистрации", self.page)
        self.INN = Element("input[id*='taxIdentificationNumber']", "ИНН", self.page)
        self.SNILS = Element("input[id*='INILA']", "СНИЛС", self.page)
        self.PUBLIC_PERSON = Element(
            "//*[@id='publicOfficial_control']//div[contains(@class, 'content')]/label", "Публичное лицо", self.page
        )
        self.RESIDENT = Element(
            "//*[@id='isResident_control']//div[contains(@class, 'content')]/label", "Резидент", self.page
        )
        self.SPEAKING_LANGUAGE = Element("#speakingLanguage_control input", "Родной язык", self.page)
        self.BUSINESS_ACTIVITY = Element("input[id*='view_businessActivity']", "Экономическая деятельность", self.page)
        self.NOTE = Element("input[id*='view_note']", "Комментарий", self.page)
        self.TAX_SCHEME = Element("div:has(> label[for*=taxScheme]) .ant-select-selector", "Ставка налога", self.page)
        self.DOCUMENT_SERIAL_AND_NUM = Element("input[id*='documentSeriesAndNumber']", "Номер документа", self.page)
        self.OGRN = Element("input[id$='view_PSRN']", "ОГРН", self.page)

        # SEGMENTS_TAB
        self.SEGMENTS_REFRESH_BTN = Element(
            "(//div[contains(@class, 'platform-custom-table')]//button)[1]", "Кнопка 'Обновить'", self.page
        )
        self.SEGMENTS_MANAGEMENT_BTN = Element(
            "(//div[contains(@class, 'platform-custom-table')]//button)[2]", "Кнопка 'Управление сегментами'", self.page
        )
        self.TABLE_SEGMENT_TYPE = ElementsList("//tr/td[1]", "Строки Тип сегмента", self.page)
        self.TABLE_SEGMENT_VALUE = ElementsList("//tr/td[2]", "Строки Значение сегмента", self.page)
        self.TABLE_SEGMENT_VALUE_DIV = ElementsList("//tr/td[2]/div", "Наличие текста в значении сегмента", self.page)
        self.TABLE_SEGMENT_DATE = ElementsList("//tr/td[3]", "Строки Дата назначения сегмента", self.page)
        self.TABLE_SEGMENT_ASSIGNED = ElementsList("//tr/td[4]", "Строки Назначено", self.page)

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
        self.SETTING_BTN = Element("button.ant5-dropdown-trigger", "Кнопка 'Настройка колонок'", self.page)
        self.SETTING_OPTIONS = ElementsList("input.ant5-checkbox-input", "Чекбоксы 'Настройка колонок'", self.page)
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
            '.platform-custom-list-scrollable-body > div p:not([color="interface15"])', "Связанные лица", self.page
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
        self.RELATED_PERSON_TABLE_NAME = Element(
            "input[id=linked-person-general-view-individual_name]", "Поле 'Имя'", self.page
        )
        self.RELATED_PERSON_GENDER = Element(
            "input[id=linked-person-general-view-individual_gender]", "Поле 'Пол'", self.page
        )
        self.RELATED_PERSON_TYPE_OF_DOCUMENT = Element(
            "input[id=linked-person-general-view-individual_documentType]",
            "Поле 'Тип документа удостоверяющего личность'",
            self.page,
        )
        self.RELATED_PERSON_DOCUMENT_NUMBER = Element(
            "input[id=linked-person-general-view-individual_documentNumber]", "Поле 'Номер документа'", self.page
        )
        self.RELATED_PERSON_WHO_ISSUED_THE_DOCUMENT = Element(
            "input[id=linked-person-general-view-individual_documentProvidedByOrganization]",
            "Поле 'Кем выдан документ'",
            self.page,
        )
        self.RELATED_PERSON_SUBDIVISION_CODE = Element(
            "input[id=linked-person-general-view-individual_documentDivisionCode]", "Поле 'Код подразделения'", self.page
        )
        self.RELATED_PERSON_DATE_OF_ISSUE = Element(
            "input[id=linked-person-general-view-individual_documentDateOfIssue]", "Поле 'Дата выдачи'", self.page
        )
        self.RELATED_PERSON_VALID_FOR = Element(
            "input[id=linked-person-general-view-individual_documentValidFor]",
            "Поле 'Дата, до которой действует документ'",
            self.page,
        )
        self.RELATED_PERSON_BIRTH_PLACE = Element(
            "input[id=linked-person-general-view-individual_birthPlace]", "Поле 'Место рождения'", self.page
        )
        self.RELATED_PERSON_BIRTH_DATE = Element(
            "input[id=linked-person-general-view-individual_birthDate]", "Поле 'Дата рождения'", self.page
        )
        self.RELATED_PERSON_COUNTRY = Element(
            "input[id=linked-person-general-view-individual_nationality]", "Поле 'Страна регистрации'", self.page
        )
        self.RELATED_PERSON_IS_PUBLIC = Element(
            "div[id=isPublic_control] span[class*='checkbox-label']", "Поле 'Публичное лицо'", self.page
        )
        self.RELATED_PERSON_IS_RESIDENT = Element(
            "div[id=isResident_control] span[class*='checkbox-label']", "Поле 'Резидент'", self.page
        )
        self.RELATED_PERSON_INN = Element(
            "input[id=linked-person-general-view-individual_taxIdentificationNumber]", "Поле 'ИНН'", self.page
        )
        self.RELATED_PERSON_SNILS = Element(
            "input[id=linked-person-general-view-individual_inila]", "Поле 'СНИЛС'", self.page
        )
        self.RELATED_PERSON_CLIENT_FL = Element(
            ".platform-grid-container a.platform-text-link", "Поле 'Клиент (физ.лицо)'", self.page
        )
        self.RELATED_PERSON_END_USER = Element(
            ".platform-grid-item div", "Поле 'Конечный пользователь для абонентов'", self.page
        )

        self.ADDRESSES_EDIT_BTN = Element(
            "//div[@id='rc-tabs-0-panel-linked-persons']//div[contains(@class, 'ant5-collapse-item')][2]//button",
            "Редактировать 'Основные данные'",
            self.page,
        )
        self.EXPAND_RELATED_ADDRESS_BTN = Element(
            "//div[contains(@class, 'collapse-item')][2]//div[contains(@class,'collapse-expand-icon')]",
            "Кнопка открыть адреса 'Связанного лица'",
            self.page,
        )
        self.RELATED_ADDRESS = Element(
            "//div[contains(@class, 'collapse-item')][2]//div[contains(@class, 'collapse-content-box')]//div/p[2]",
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
            "(//*[contains(@class, 'collapse-borderless')])[1]/*[contains(@class, 'collapse-item')]",
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
        self.SUBSCRIBER = ElementsList("[class*=collapse-item] > [class*=collapse-header] a", "Абонент", self.page)
        self.PRODUCTS = ElementsList("[id*=panel-products] [role=tab]", "Продукты", self.page)
        self.PRODUCT_LIMIT = ElementsList("//*[contains(@class, 'ant-progress-line')]/..", "Лимиты продуктов", self.page)
        self.OPTION_LIMIT_ICON = ElementsList(
            "//*[contains(@class, 'ant-progress-line')]/.. //span", "Значок лимита опции", self.page
        )
        self.PRODUCT_NAME = ElementsList(
            "[class*=collapse-content] .platform-grid-container > div > div > a[color=accent]",
            "Названия продуктов",
            self.page,
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
            '[data-menu-id*="OpenConsuming"]', "Кнопка 'Перейти к деталям потребления'", self.page
        )
        self.PRODUCTS_STATUS_COLOR = ElementsList(
            "//*[contains(@class, 'platform-grid-container')]/div/div/p[@color='accent']/parent::div/div",
            "Цвет статуса продукта",
            self.page,
        )
        self.OPTION_STATUS_COLOR = ElementsList(
            "//*[@role='tab']/../*[@role='tabpanel'] //*[contains(@class, 'platform-grid-container')]/div/div/p[@color='accent']/../div",
            "Цвет статуса Опции",
            self.page,
        )
        self.PRODUCTS_DETAILS_OPEN_BTN = Element(
            "[id*=panel-products] .ant5-collapse-content-box button.ant5-dropdown-trigger",
            "Кнопка выпадашки для кнопки редактирования продукта",
            self.page,
        )
        self.TURN_OFF_BTN = Element(
            "(//*[contains(@class, 'ant-dropdown')]//button)[1]", "Кнопка 'Отключить'", self.page
        )
        self.PRODUCTS_OPTIONS_OPEN_BTN = ElementsList(
            "//*[contains(@class, 'ant-collapse-item')] //button[2]",
            "Кнопка выпадашки для кнопки добавления опций",
            self.page,
        )
        self.PRODUCTS_OPTIONS_ADD_BTN = Element('[data-menu-id*="ADD_OPTION"]', 'Кнопка "Добавить Опцию"', self.page)
        self.CURRENT_OPTION_PRODUCT = ElementsList(
            "[role=tablist] [role=tablist] .ant-collapse-item", "Подключенные опции у продукта", self.page
        )
        self.OPEN_OPTIONS_BTN = ElementsList(
            "[role=tablist] div[class='ant-collapse-expand-icon'] span", "Кнопка Открыть опции продукта", self.page
        )
        self.OPTION_NAME = ElementsList(
            "[role=tablist] [role=tablist] .ant-collapse-item .platform-grid-container > div > div > p[color=accent]",
            "Названия подключенных опций продукта",
            self.page,
        )

        # PRODUCTS_TAB_SIDEBAR
        self.PRODUCTS_SIDEBAR_OPEN = Element(
            "(//div[@role='tablist'] //div[contains(@class, 'platform-grid-container')]) [1] ",
            "Область клика для открытия сайдбара",
            self.page,
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
            return self.OPTION_STATUS_COLOR[0].get_color() == "rgb(0, 173, 33)"
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


class EditClientProfile(DynamicElements):
    """Страница /customer-hierarchy-management/customers/{customerId}/customer
    Вкладка 'Персональные данные', форма 'Редактирование клиента'"""

    def __init__(self, page: Page):
        super().__init__(page)

        self.EDIT_FORM_LOADER = Element(
            "#customer-individual-edit span[class*='spin-dot']", "Лоадер формы Редактирование клиента", self.page
        )
        self.SURNAME_INPUT = Element("#surname_control input", "Поле Фамилия", self.page)
        self.NAME_INPUT = Element("#firstname_control input", "Поле Имя", self.page)
        self.PATRONYMIC_INPUT = Element("#patronymic_control input", "Поле Отчество", self.page)
        self.IS_PUBLIC_CHECKBOX = Element(
            "div[role=dialog] #publicOfficial_control input", "Поле Публичное лицо", self.page
        )
        self.IS_RESIDENT_CHECKBOX = Element("div[role=dialog] #isResident_control input", "Поле Резидент", self.page)
        self.LANGUAGE_DROPDOWN = Select("#customer-individual-edit_speakingLanguage", "Поле Язык общения", self.page)
        self.COUNTRY_DROPDOWN = Select(
            "div[role=dialog] #nationality_control input", "Поле Страна регистрации", self.page
        )
        self.BIRTH_PLACE = Element("div[role=dialog] #birthPlace_control input", "Поле Место рождения", self.page)
        self.BIRTH_DATE = DatePicker("div[role=dialog] #birthDate_control input", "", self.page)
        self.GENDER = Select("#customer-individual-edit_gender", "", self.page)
        self.DOCUMENT_TYPE = Select("#customer-individual-edit_documentType", "", self.page)
        self.DOCUMENT_SERIAL = Element("div[role=dialog] #documentSeries_control input", "", self.page)
        self.DOCUMENT_NUMBER = Element("div[role=dialog] #documentNumber_control input", "", self.page)
        self.DOCUMENT_DATE = DatePicker("div[role=dialog] #documentDateOfIssue_control input", "", self.page)
        self.DOCUMENT_PROVIDE_BY = Element(
            "div[role=dialog] #documentProvidedByOrganization_control input", "", self.page
        )
        self.DOCUMENT_DIVISION_CODE = Element("div[role=dialog] #documentDivisionCode_control input", "", self.page)
        self.DOCUMENT_VALID_DATE = DatePicker("div[role=dialog] #documentValidFor_control input", "", self.page)
        self.INN = Element("div[role=dialog] #taxIdentificationNumber_control input", "", self.page)


class ClientProfileEndUser(DynamicForms):
    """Страница /customer-hierarchy-management/customers/{customerId}/products?subscription={subscriptionId}
    Вкладка 'Продукты', форма 'Абонент'"""

    def __init__(self, page: Page):
        super().__init__(page)

        self.ADD_END_USER_BUTTON = Element(
            "div[class*=drawer-body] button[variant=secondary]", "Добавить данные (Конечный пользователь)", self.page
        )
        self.DOCUMENT_TYPE_DROPDOWN = Select(
            "#end-user-add-identification_documentType", "Тип документа, удостоверяющего личность", self.page
        )
        self.DOCUMENT_SERIES = Element("#end-user-add-identification_documentSeries", "Серия", self.page)
        self.DOCUMENT_NUMBER = Element("#end-user-add-identification_documentNumber", "Номер", self.page)
        self.EXISTING_CLIENT_FOUND_TITLE = Element(
            "#end-user-add-customer-selection h4", "Найден существующий клиент", self.page
        )
        self.CLIENT = ElementsList("#end-user-add-customer-selection tbody tr", "Клиент", self.page)
        self.ADD_END_USER_NEXT_BUTTON = Element(
            "(//div[contains(@class, 'drawer-footer')]/div/div)[3]//button", "Добавить", self.page
        )
        self.DATA_TITLE = Element(
            ".platform-dynamic-form-form-body-grid div:nth-child(4) h4", "Данные конечного пользователя", self.page
        )
        self.CLOSE_END_USER_MODAL_BUTTON = Element("#_cancel-button", "Закрыть", self.page)
        self.EDIT_END_USER_BUTTON = Element(
            "(//div[contains(@class, 'platform-toolbar-item')][1]/button)[1]", "Кнопка 'Редактировать'", self.page
        )
        self.REPLACE_END_USER_BUTTON = Element(
            "(//div[contains(@class, 'platform-toolbar-item')][2]/button)[1]", "Кнопка 'Заменить'", self.page
        )

        self.ACCOUNT_ID = Element("#end-user-view_accountNumber", "Лицевой счет", self.page)
        self.BALANCE = Element("#end-user-view_balance", "Баланс", self.page)
        self.FIO = Element("#end-user-view #end-user-view_fullName", "ФИО", self.page)
        self.GENDER = Element("#end-user-view_gender", "Пол", self.page)
        self.DOCUMENT_TYPE = Element("#end-user-view_documentType", "Тип документа удостоверяющего личность", self.page)
        self.DOCUMENT_SERIES_AND_NUMBER = Element("#end-user-view_documentNumber", "Серия и номер документа", self.page)
        self.WHO_ISSUED_THE_DOCUMENT = Element(
            "#end-user-view_documentProvidedByOrganization", "Кем выдан документ", self.page
        )
        self.SUBDIVISION_CODE = Element("#end-user-view_documentDivisionCode", "Код подразделения", self.page)
        self.DATE_OF_ISSUE = Element("#end-user-view_documentDateOfIssue", "Дата выдачи", self.page)
        self.DOCUMENT_VALID_FOR = Element(
            "#end-user-view_documentValidFor", "Дата, до которой действует документ", self.page
        )
        self.PLACE_OF_BIRTH = Element("#end-user-view_birthPlace", "Место рождения", self.page)
        self.BIRTHDAY = Element("#end-user-view_birthDate", "Дата рождения", self.page)
        self.COUNTRY = Element("#end-user-view_registrationCountry", "Страна регистрации", self.page)
        self.LANGUAGE = Element("#end-user-view_speakingLanguage", "Язык", self.page)
        self.REGISTRATION_ADDRESS = Element("#end-user-view_registrationAddress", "Адрес регистрации", self.page)
        self.IS_PUBLIC = Element("#publicOfficial_control label > span:nth-child(2)", "Публичное лицо", self.page)
        self.IS_RESIDENT = Element("#isResident_control label > span:nth-child(2)", "Резидентство", self.page)

        self.SURNAME_INPUT = Element(
            "#end-user-add-fill-customer-data_surname, #end-user-edit_surname", "Поле Фамилия", self.page
        )
        self.NAME_INPUT = Element(
            "#end-user-add-fill-customer-data_firstName, #end-user-edit_firstName", "Поле Имя", self.page
        )
        self.PATRONYMIC_INPUT = Element(
            "#end-user-add-fill-customer-data_patronymic, #end-user-edit_patronymic", "Поле Отчество", self.page
        )
        self.GENDER_DROPDOWN = Select(
            "#end-user-add-fill-customer-data_gender, #end-user-edit_gender", "Дропдаун Пол", self.page
        )
        self.WHO_ISSUED_THE_DOCUMENT_INPUT = Element(
            "#end-user-add-fill-customer-data_documentProvidedByOrganization, #end-user-edit_documentProvidedByOrganization",
            " Поле Кем выдан документ",
            self.page,
        )
        self.SUBDIVISION_CODE_INPUT = Element(
            "#end-user-add-fill-customer-data_documentDivisionCode, #end-user-edit_documentDivisionCode",
            "Поле Код подразделения",
            self.page,
        )
        self.DATE_OF_ISSUE_INPUT = Element(
            "#end-user-add-fill-customer-data_documentDateOfIssue, #end-user-edit_documentDateOfIssue",
            "Поле Дата выдачи",
            self.page,
        )
        self.DOCUMENT_VALID_FOR_INPUT = Element(
            "#end-user-add-fill-customer-data_documentValidFor, #end-user-edit_documentValidFor",
            "Поле Дата, до которой действует документ",
            self.page,
        )
        self.PLACE_OF_BIRTH_INPUT = Element(
            "#end-user-add-fill-customer-data_birthPlace, #end-user-edit_birthPlace", "Поле Место рождения", self.page
        )
        self.BIRTHDAY_INPUT = Element(
            "#end-user-add-fill-customer-data_birthDate, #end-user-edit_birthDate", "Поле Дата рождения", self.page
        )
        self.COUNTRY_DROPDOWN = Dropdown(
            "#nationality_control, #end-user-edit_nationality", "Дропдаун Страна регистрации", self.page
        )
        self.LANGUAGE_DROPDOWN = Select(
            "#speakingLanguage_control, #end-user-edit_speakingLanguage", "Дропдаун Язык общения", self.page
        )
        self.REGISTRATION_ADDRESS_INPUT = Autocomplete(
            "#end-user-add-fill-customer-data_address, #end-user-edit_registrationAddress",
            "Поле Адрес регистрации",
            self.page,
        )
        self.IS_PUBLIC_CHECKBOX = Element(
            "#end-user-edit_publicOfficial",
            "Чекбокс Публичное лицо",
            self.page,
        )
        self.IS_RESIDENT_CHECKBOX = Element("#end-user-edit_isResident", "Чекбокс Резидентство", self.page)
        self.LOADER = Element("form span[class*='spin-dot']", "Лоадер на форме добавления конечного пользователя", self.page)
