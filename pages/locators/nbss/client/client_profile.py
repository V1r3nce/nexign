import allure

from common.helpers.checker import wait_that
from pages.locators.nbss.dynamic_form_elements import DynamicElements, DynamicForms
from pages.ui_elements import Autocomplete, DatePicker, Element, ElementsList, Select


class ClientProfileElements(DynamicElements):
    """Страница /customer-hierarchy-management/customers/{customer_id}/overview
    'Управление клиентскими иерархиями'"""

    def __init__(self) -> None:
        super().__init__()

        self.CLIENT_FIO_BTN = Element("(//*[contains(@class, 'platform-text-link')])[1]", "Кнопка 'ФИО клиента'")

        # HEADER
        self.CLIENT_FIO = Element("h3[class*=title]", "ФИО клиента")
        self.CLIENT_STATUS = Element(
            "header[class*=platform-summary-header] div[class*=platform-summary-title] span[class*=tag]",
            "Статус клиента",
        )
        self.CLIENT_TYPE = Element("[class*=summary-subtitle]", "Тип клиента")

        # COMMON_ELEMENTS
        self.ADD_BTN = Element("(//button[@title='Добавить'])[1]", "Кнопка 'Добавить'")
        self.CANCEL_BTN = ElementsList("#_cancel-button", "Внутренняя кнопка закрытия")

        # HEADER_NAV_TAB
        self.OVERVIEW_TAB = Element("[role=tab][id*=tab-overview]", "Таб 'Обзор'")
        self.CLIENT_TAB = Element("[role=tab][id$=tab-customer]", "Таб 'Клиент'")
        self.RELATED_PERSONS_TAB = Element("[role=tab][id*=tab-linked-persons]", "Таб 'Связанные лица'")
        self.SUBDIVISIONS_TAB = Element("[role=tab][id*=tab-subdivisions]", "Таб 'Подразделения'")
        self.AGREEMENTS_TAB = Element("[role=tab][id*=tab-agreements]", "Таб 'Договоры'")
        self.PERSONAL_ACCOUNTS_TAB = Element("[role=tab][id*=tab-accounts]", "Таб 'Лицевые счета'")
        self.CLIENT_GROUPS_TAB = Element("[role=tab][id$=tab-customer-groups]", "Таб 'Группы клиентов'")
        self.REQUESTS_TAB = Element("[role=tab][id*=tab-inquiries]", "Таб 'Заявки'")
        self.PRODUCTS_TAB = Element("[role=tab][id*=tab-products]", "Таб 'Продукты'")

        # LEFT_NAV_TAB
        self.PROPERTIES_TAB = Element("[data-node-key=attributes]", "Кнопка 'Свойства'")
        self.SEGMENTS_TAB = Element("[role=tab][id$=tab-segments]", "Кнопка 'Сегменты'")
        self.ADDRESSES_TAB = Element("[data-node-key=addresses]", "Кнопка 'Адреса'")
        self.TABLE_LINE = ElementsList("//tr", "Строки таблицы")
        self.DOCUMENTS_TAB = Element(".ant-tabs:nth-of-type(1) .ant-tabs-tab:nth-of-type(3)", "Кнопка 'Документы'")

        # OVERVIEW_TAB
        self.WIDGET = ElementsList(".react-grid-layout > div", "Виджет")
        self.WIDGET_LABEL = ElementsList(".react-grid-layout > div h4", "Название виджета")
        self.PERSONAL_ACCOUNT_UPDATE_BTN = Element(
            "(//*[contains(@class, 'react-grid-layout')]/div[2] //button)[2]",
            "Кнопка 'Обновить' для виджета 'Лицевые счета'",
        )
        self.PERSONAL_ACCOUNT_LOADER = Element(
            "//*[contains(@class, 'react-grid-layout')]/div[2]  //*[contains(@class, 'ant-spin-sm')]",
            "Лоадер при обновлении виджета 'Лицевые счета'",
        )
        self.BALANCE = ElementsList(
            "//*[contains(@class, 'react-grid-layout')]/div[2] //p[@color='positive' or @color='negative']",
            "Балансы ЛС",
        )
        self.WIDGET_PERSONAL_ACCOUNT_IDS = ElementsList(
            "//p/preceding-sibling::a[contains(@href, 'account')]", "Лицевые счета клиента"
        )
        self.WIDGET_PERSONAL_ACCOUNT_SUM = ElementsList(
            "//a[contains(@href, 'account')]/parent::div/parent::div/p", "Суммы Лицевых счетов клиента"
        )
        self.CUSTOMER_NAME = ElementsList(
            "//label[@for='customer-info_customerName']",
            "Лейбл: Наименование клиента",
        )

        # PERSONAL_DATA_TAB
        self.FIO = Element("#customer-individual-view_fio", "Поле ФИО")
        self.PERSONAL_DATA_LOADER = Element(
            "#customer-individual-view span[class*='spin-dot']", "Лоадер таблицы Персональные данные"
        )

        # CLIENT_TAB
        self.EDIT_BTN = Element("button:has([data-icon=Edit])", "Кнопка 'Редактировать'")
        self.ORG_NAME = Element("input[id*='organization-view_name']", "Наименование")
        self.FIO = Element("input[id*='view_fio']", "ФИО")
        self.NATIONALITY = Element("input[id*='nationality']", "Страна регистрации")
        self.GENDER = Element("input[id*='gender']", "Пол")
        self.DOCUMENT_TYPE = Element("input[id*='documentType']", "Тип документа")
        self.DOCUMENT_DATE = Element("input[id*='documentDateOfIssue']", "Дата выдачи")
        self.DOCUMENT_VALID_DATE = Element("input[id*='documentValidFor']", "Дата действия документа")
        self.BIRTH_DATE = Element("input[id*='birthDate']", "Дата рождения")
        self.COUNTRY = Element("#nationality_control input", "Страна регистрации")
        self.INN = Element("input[id*='taxIdentificationNumber']", "ИНН")
        self.SNILS = Element("input[id*='INILA']", "СНИЛС")
        self.PUBLIC_PERSON = Element("div:has(> label > span > input[id*=publicOfficial])", "Публичное лицо")
        self.RESIDENT = Element("label:has(input[id*=isResident])", "Резидент")
        self.SPEAKING_LANGUAGE = Element("input[id*='view_speakingLanguage']", "Родной язык")
        self.BUSINESS_ACTIVITY = Element("input[id*='view_businessActivity']", "Экономическая деятельность")
        self.NOTE = Element("input[id*='view_note']", "Комментарий")
        self.TAX_SCHEME = Element("div[class*=select-selector]:has([id*=taxScheme])", "Схема налогообложения")
        self.DOCUMENT_SERIAL_AND_NUM = Element("input[id*='documentSeriesAndNumber']", "Номер документа")
        self.OGRN = Element("input[id$='view_PSRN']", "ОГРН")
        self.AUTHORIZATION_CODE = Element("[id*=AuthorizationCode]", "Код авторизации")

        # SEGMENTS_TAB
        self.SEGMENTS_REFRESH_BTN = Element(
            "(//div[contains(@class, 'platform-table')]//button)[1]", "Кнопка 'Обновить'"
        )
        self.SEGMENTS_MANAGEMENT_BTN = Element(
            "(//div[contains(@class, 'platform-table')]//button)[2]", "Кнопка 'Управление сегментами'"
        )
        self.TABLE_SEGMENT_TYPE = ElementsList("(//div[contains(@class, '-table-row')]/div)[1]", "Тип сегмента")
        self.TABLE_SEGMENT_VALUE = ElementsList("(//div[contains(@class, '-table-row')]/div)[2]", "Значение сегмента")
        self.TABLE_SEGMENT_DATE = ElementsList(
            "(//div[contains(@class, '-table-row')]/div)[3]", "Дата назначения сегмента"
        )
        self.TABLE_SEGMENT_ASSIGNED = ElementsList("(//div[contains(@class, '-table-row')]/div)[4]", "Назначено")

        # ADDRESSES_TAB
        self.REFRESH_BTN = Element("button[|title='Обновить'],[|title='Refresh']", "Кнопка 'Обновить'")
        self.CLEAR_ALL_FILTER_BTN = Element(
            "button[|title='Очистить все фильтры'],[|title='Clear all filters']",
            "Кнопка очистить все фильтры",
        )
        self.EDIT_ADDRESS = Element("button[|title='Изменить адрес'],[|title='Edit address']", "Кнопка 'Изменить адрес'")
        self.DELETE_ADDRESS = Element(
            "button[|title='Удалить адрес'],[|title='Delete address']", "Кнопка 'Удалить адрес'"
        )
        self.EXPORT_TO_FILE_BTN = Element(
            "button[|disabledtooltip='Export found records to XLS file'],[|disabledtooltip='Экспортировать найденные записи в XLS файл']",
            "Кнопка экспортировать файл",
        )
        # TODO: Актуализировать локатор после исправления https://jira.nexign.com/browse/RMBSS-13179, задача: https://jira.nexign.com/browse/TUDS-3756
        self.TOOLTIP_MESSAGE = Element(
            "[class*=tooltip]:not([class*=hidden]) p[data-name]", "Сообщение в видимой подсказке"
        )
        self.TABLE_LINE = ElementsList("//tr[@data-row-key]", "Строки таблицы")
        self.TABLE_ADDRESS_LINES = ElementsList(
            "[id*=panel-addresses] [class$=table-tbody] div[data-row-key]", "Строки таблицы"
        )
        self.TABLE_ADDRESS_TYPES = ElementsList(
            "[id*=panel-addresses] [class$=table-tbody] div[data-row-key] > div:nth-child(1)", "Строки Тип адреса"
        )
        self.TABLE_ADDRESSES = ElementsList(
            "[id*=panel-addresses] [class$=table-tbody] div[data-row-key] > div:nth-child(2)", "Строки Адреса"
        )
        self.TABLE_MAP_CELLS = ElementsList(
            "[id*=panel-addresses] [class$=table-tbody] div[data-row-key]:has(button)", "Строки под кнопку карты"
        )
        self.TABLE_LINE_MAP_BUTTON = ElementsList(
            "[id*=panel-addresses] [class$=table-tbody] div[data-row-key] button:has(span)",
            "Строки таблицы кнопка карты",
        )
        self.SETTING_BTN = Element(
            "//div[contains(@id, 'panel-addresses')]//button[contains(@class, 'dropdown-trigger')]",
            "Кнопка 'Настройка колонок'",
        )
        self.SETTING_OPTIONS = ElementsList("input[class*=checkbox-input]", "Чекбоксы 'Настройка колонок'")
        self.TYPE_SORT_BTN = Element(
            "//span[contains(text(), 'Тип')]/../..//*[contains(@data-icon, 'Sort')]",
            "Кнопка сортировки 'Тип'",
        )
        self.TYPE_FILTER_DROPDOWN_BTN = Select("tr th [class*=select-selector]", "Кнопка открыть фильтр 'Тип'")
        self.TYPE_FILTER_OPTIONS = ElementsList(
            "//div[contains(@class, 'select-item-option') and @title]/div/div/div[2]", "Опции фильтра 'Тип'"
        )
        self.TYPE_FILTER_CHOOSE_ALL_BTN = Element(
            "//a[contains(text(), 'Выбрать все')]", "Кнопка 'Выбрать все' фильтр Тип"
        )
        self.SEARCH_ADDRESS_INPUT = Element("//tr/th[2]//input", "Поле поиска адреса")

        # RELATED_PERSONS_TAB
        self.ADD_RELATED_PERSON_BTN = Element(
            "[class*='linkedPerson_list'] [class*='platform-toolbar'] > div:not([style]) button:has([data-icon=Add])",
            "Кнопка 'Добавить' связанное лицо",
        )
        self.FILTER_SETTINGS = Element(
            "button[|title='Найстроки фильтра'],[|title='Filter settings']", "Кнопка 'Настройки фильтра'"
        )
        self.CLEAR_FILTER_BTN = Element("button[|title='Сбросить'],[|title='Clear']", "Кнопка 'Сбросить фильтр'")
        self.DELETE_PERSON = Element(".linkedPerson_list button:nth-of-type(3)", "Кнопка 'Удалить'")

        self.RELATED_PERSONS = ElementsList(
            ".platform-custom-list-scrollable-body > div p:not([color])", "Связанные лица"
        )
        self.EMPTY_RELATED_PERSONS = Element(
            ".platform-custom-list-scrollable-body > div p", "Пустой список связанных лиц"
        )

        self.MAIN_DATA_EDIT_BTN = Element(
            "(//div[contains(@class, 'platform-scrollable')])[3]/div[1]//button",
            "Редактировать 'Основные данные'",
        )
        self.RELATED_PERSON_BENEFICIARY_NAME = Element(
            "#linked-person-general-view-impersonal_name",
            "Поле именования Выгодоприобретателя Связанного лица",
        )
        self.RELATED_SPEAKING_LANGUAGE = Element(
            "input[id*=linked-person][id*=speakingLanguage]:not([style])", "Язык общения"
        )
        self.RELATED_POSITION = Element("input[id*=position]", "Должность")
        self.RELATED_NOTE = Element("[id*=view_note]", "Комментарий")
        self.RELATED_NOTE_ADDITIONAL_ATTRIBUTE = ElementsList(
            "[class*=platform-scrollable][data-testid*=LinkedPersons] div:has(>[id*=linked-person]) + div p[data-name=paragraph]",
            "Комментарий (Дополнительные атрибуты)",
        )
        self.RELATED_PERSON_TABLE_NAME = Element("input[id=linked-person-general-view-individual_name]", "Поле 'Имя'")
        self.RELATED_PERSON_GENDER = Element("input[id=linked-person-general-view-individual_gender]", "Поле 'Пол'")
        self.RELATED_PERSON_TYPE_OF_DOCUMENT = Element(
            "input[id=linked-person-general-view-individual_documentType]",
            "Поле 'Тип документа удостоверяющего личность'",
        )
        self.RELATED_PERSON_DOCUMENT_NUMBER = Element(
            "input[id=linked-person-general-view-individual_documentNumber]", "Поле 'Номер документа'"
        )
        self.RELATED_PERSON_DOCUMENT_PROVIDE_BY = Element(
            "input[id=linked-person-general-view-individual_documentProvidedByOrganization]",
            "Поле 'Кем выдан документ'",
        )
        self.RELATED_PERSON_SUBDIVISION_CODE = Element(
            "input[id=linked-person-general-view-individual_documentDivisionCode]", "Поле 'Код подразделения'"
        )
        self.RELATED_PERSON_DATE_OF_ISSUE = Element(
            "input[id=linked-person-general-view-individual_documentDateOfIssue]", "Поле 'Дата выдачи'"
        )
        self.RELATED_PERSON_VALID_FOR = Element(
            "input[id=linked-person-general-view-individual_documentValidFor]",
            "Поле 'Дата, до которой действует документ'",
        )
        self.RELATED_PERSON_BIRTH_PLACE = Element(
            "input[id=linked-person-general-view-individual_birthPlace]", "Поле 'Место рождения'"
        )
        self.RELATED_PERSON_BIRTH_DATE = Element(
            "input[id=linked-person-general-view-individual_birthDate]", "Поле 'Дата рождения'"
        )
        self.RELATED_PERSON_COUNTRY = Element(
            "input[id=linked-person-general-view-individual_nationality]", "Поле 'Страна регистрации'"
        )
        self.RELATED_PERSON_IS_PUBLIC = Element(
            "label:has(#linked-person-general-view-individual_isPublic) span[class*='checkbox-label']",
            "Поле 'Публичное лицо'",
        )
        self.RELATED_PERSON_IS_RESIDENT = Element(
            "label:has(#linked-person-general-view-individual_isResident) span[class*='checkbox-label']",
            "Поле 'Резидент'",
        )
        self.RELATED_PERSON_INN = Element(
            "input[id=linked-person-general-view-individual_taxIdentificationNumber]", "Поле 'ИНН'"
        )
        self.RELATED_PERSON_SNILS = Element("input[id=linked-person-general-view-individual_inila]", "Поле 'СНИЛС'")
        self.RELATED_PERSON_CLIENT_FL = Element(
            ".platform-grid-container a.platform-text-link", "Поле 'Клиент (физ.лицо)'"
        )

        self.ADDRESSES_EDIT_BTN = Element(
            "//div[@id='rc-tabs-0-panel-linked-persons']//div[contains(@class, 'collapse-item')][2]//button",
            "Редактировать 'Основные данные'",
        )
        self.EXPAND_RELATED_ADDRESS_BTN = Element(
            "//div[contains(@class, 'collapse-item')][2]//div[contains(@class,'collapse-expand-icon')]",
            "Кнопка открыть адреса 'Связанного лица'",
        )
        self.RELATED_ADDRESS = Element(
            "//div[contains(@class, 'collapse-item')][2]//div[contains(@class, 'collapse-content-box')]//div/p[2]",
            "Адреса 'Связанного лица'",
        )

        self.CONTACT_DATA_EDIT_BTN = Element(
            "[class*=collapse-item]:nth-child(1) [data-testid*=LinkedPersons][data-testid*=Edit]",
            "Редактировать контакты",
        )
        self.CONTACT_PHONE_EDIT_INFO = Element(
            "[id*=contactPhones][id*=help]", "Информационное сообщение при редактировании Номера"
        )
        self.CONTACT_PHONE_CLEAR = Element(
            "[class*=select]:has([id*=contactPhones][id$=base]) button[class*=clear]", "Кнопка удалить у Номера"
        )
        self.ADDRESS_EDIT_BTN = Element("[class*=collapse-item]:nth-child(2) [data-icon=Edit]", "Редактировать адреса")
        self.RELATED_MOBILE_PHONE = Element(
            "[class*=collapse-content-box] [class*=grid-item] > div p:not([color])", "Телефон 'Связанного лица'"
        )
        self.RELATED_EMAIL = Element("[class*=collapse-content-box] [class*=grid-item] a", "Email 'Связанного лица'")

        self.RELATED_EMAIL = Element("a[href*='mail']", "E-mail 'Связанного лица'")
        self.AUTHORIZE_BTN = Element("[class*=toolbar-item]:not([data-item-key]) [data-icon=Visibility]", "Авторизовать")

        # SUBDIVISION TAB
        self.SUBDIVISIONS_NAMES = ElementsList("a[href*=subdivision]", "Названия Подразделений")
        self.SUBDIVISION_ADDRESS = ElementsList("input[id*=registrationAddress]", "Адрес регистрации Подразделения")
        self.SUBDIVISION_TITLE_NAME = Element(
            ".platform-root-scrollable-container h3", "Заголовок название Подразделения"
        )
        self.SUBDIVISIONS_INN = ElementsList("input[id*=subdivision-card-view_INN]", "ИНН Подразделения")
        self.SUBDIVISIONS_KPP = ElementsList("input[id*=subdivision-card-view_KPP]", "КПП Подразделения")
        self.SUBDIVISIONS_OGRN = ElementsList("input[id*=subdivision-card-view_OGRN]", "ОГРН Подразделения")

        # AGREEMENTS_TAB
        self.PERSONAL_AGREEMENT_LINK = Element(
            "[role=tabpanel][id$=panel-agreements] [class*=table-row][data-row-key] > [class*=table-cell] a",
            "Кнопка-ссылка по номеру договора",
        )
        self.ADD_AGREEMENT_BTN = Element(
            "[data-testid=chm-ChmAgreementCreation-btn-agreements-buttons-addButtonTitle]",
            "Кнопка 'Добавить' договор",
        )
        self.SIGN_AGREEMENT_BTN = Element(
            "[data-testid=chm-AgreementSigningModal-btn-signingButton]",
            "Кнопка 'Подписать договор'",
        )
        self.EDIT_AGREEMENT_BTN = Element(
            "[id*=panel-attributes] button:has([data-icon=Edit])", "Кнопка 'Редактировать' договор"
        )
        self.AGREEMENT_EXPIRATION_DATE = Element(
            "[role=tabpanel][id$=panel-agreements] [class*=table-row][data-row-key] :nth-child(4)",
            "Дата расторжения договора",
        )
        self.AGREEMENT_TYPE = Element(
            "[role=tabpanel][id$=panel-agreements] [class*=table-row][data-row-key] > [class*=table-cell] > div",
            "Категория договора",
        )
        self.AGREEMENT_STATUS = Element(
            "[class*=summary-title] [class*=tag]",
            "Статус договора",
        )
        self.DOCUMENTS_LINE = ElementsList(
            "[role=tabpanel][id$=panel-agreements] [class*=table-row][data-row-key]",
            "Строки в таблице Договоров",
        )
        self.CURRENT_CONTRACT_LINK = ElementsList(
            "//a[starts-with(@href, '/nbss/customer-hierarchy-management/agreements/') and contains(@href, '/agreement')]",
            "Кликабельный 'Номер Договора'",
        )

        # PERSONAL_ACCOUNTS_TAB
        self.PERSONAL_ACCOUNT_STATUS = Element(".platform-scrollable [class*=tag]", "Статус лицевого счета")
        self.ADD_PERSONAL_ACCOUNT_BTN = Element(
            "[id*=panel-accounts] button:has([data-icon=Add])", "Кнопка 'Добавить' лицевой счет"
        )
        self.NO_PERSONAL_ACCOUNTS_BLOCK = Element(
            "[id*=panel-accounts] .platform-empty-state-container",
            "Блок отсутствия записей на вкладку 'Лицевые  счета'",
        )
        self.EDIT_DETAILS_ACCOUNT_BTN = Element(
            "[id*=panel-account] button:has([data-icon=Edit])", "Кнопка 'Редактировать' лицевой счет"
        )
        self.CLOSE_PERSONAL_ACCOUNT_BTN = Element(
            "[id*=panel-account] button[data-testid*=ObjectCardDf]", "Кнопка 'Закрыть лицевой счёт'"
        )
        self.PAYMENT_METHOD_FLD = Element("[class*=select-selector]:has([id*=ratingType])", "Поле 'Способ оплаты")
        self.THRESHOLD_CONTROL = Element(
            "[class*=checkbox-wrapper]:has(#account-card-view_thresholdControl)", "Поле 'Контроль порога'"
        )
        self.THRESHOLD_BREAK = Element("#account-card-view_thresholdBreak", "Поле 'Порог отключения'")
        self.CURRENT_PERSONAL_ACCOUNT_LINK = Element(
            "[href*=accounts][href$=account]", "Кнопка-ссылка на текущий Лицевой счет клиента"
        )
        self.PERSONAL_ACCOUNT_LINKS = ElementsList("[href*='accounts']", "Кнопки-ссылки для Лицевых счетов клиента")
        self.CURRENT_AGREEMENT_LINK = Element("[href*='agreements']", "Кнопка-ссылка на текущий Лицевой счет клиента")
        self.CURRENT_CLIENT_LINK = Element(
            "//p//following-sibling::a[contains(@href, 'overview')]", "Кнопка-ссылка на текущего клиента"
        )

        # CLIENT_GROUPS_TAB
        self.ADD_CLIENT_GROUP_BTN = Element(
            "[class$=platform-toolbar] > div:not([style]) [data-testid*=AddCustomerToGroup]",
            "Кнопка '+ Добавить'",
        )
        self.DELETE_CLIENT_FROM_GROUP_BTN = Element(
            "[class$=platform-toolbar] > div:not([style]) [data-testid*=AccountRemoveOutline]",
            "Кнопка 'Удалить клиента из группы'",
        )
        self.CLIENT_GROUP_LIST = ElementsList("[class*=scrollable-body] p:not([color])", "Список групп клиентов")
        self.CLIENT_GROUPS_SEARCH = Element(
            "div[class*='table-header'] input[class*='input ']", "Поле поиска 'Имя группы'"
        )
        self.CLIENT_GROUPS = ElementsList(
            "[class*='table-row'] [class*='table-cell']:nth-child(1)",
            "Список групп клиентов на форме 'Добавление клиента в группу'",
        )
        self.CLIENT_ROLE_DROPDOWN = Select("#role", "Дропдаун 'Роль назначаемая клиенту'")
        self.ADD_BTN = Element("div[id*=panel-addresses] span[data-icon=Add]", "Кнопка 'Добавить'")

        # REQUESTS_TAB
        self.UPDATE_REQUESTS_BTN = Element("(//*[@id='inquiries-list'] //button)[1]", "Кнопка 'Обновить'")
        self.REQUESTS = ElementsList("div[data-row-key]", "Заявки")
        self.REQUEST_NUMBER = ElementsList("div[data-row-key] [class*=table-cell]:nth-child(1) a", "Номера заявок")
        self.REQUEST_TYPE = ElementsList("div[data-row-key] [class*=table-cell]:nth-child(2)", "Типы заявок")
        self.REQUEST_STATUS = ElementsList("div[data-row-key] [class*=table-cell]:nth-child(3)", "Статусы заявок")
        self.REQUEST_STEP = ElementsList("div[data-row-key] [class*=table-cell]:nth-child(4)", "Шаги заявок")
        self.REQUEST_RESPONSIBLE = ElementsList(
            "div[data-row-key] [class*=table-cell]:nth-child(5)", "Ответственные заявок"
        )
        self.REQUEST_CREATE_DATE = ElementsList(
            "div[data-row-key] [class*=table-cell]:nth-child(6)", "Дата создания заявок"
        )

        # PRODUCTS_TAB
        self.PRODUCTS_UPDATE_BTN = Element(
            "[id*=panel-products] [class*=toolbar] > div:not([style]) button:has([data-icon=Refresh])",
            "Кнопка 'Обновить'",
        )
        self.PRODUCTS_STATUS_COLOR = ElementsList(
            "[class*=product][data-subscription-id] [class*=header-status]",
            "Цвет статуса продукта",
        )
        self.OPTION_STATUS_COLOR = ElementsList(
            "//*[contains(@class, 'collapse-content-box')]//*[contains(@class, 'collapse-content-box')]//a[@color='accent']/../div",
            "Цвет статуса Опции",
        )
        self.PROPERTIES_TAB = Element("[role=tab][id*=attributes]", "Таб 'Свойства'")

    @allure.step("Обновить список и проверить статус")
    def update_and_check_status_color(self, type_offer: str) -> bool | None:
        if type_offer == "product":
            self.PRODUCTS_UPDATE_BTN.click()
            return self.PRODUCTS_STATUS_COLOR[0].get_css_property("background-color") == "rgb(0, 173, 33)"
        elif type_offer == "request":
            self.UPDATE_REQUESTS_BTN.click()
            return self.REQUEST_STATUS[2].get_css_property("background-color") != "rgb(0, 173, 33)"
        elif type_offer == "option":
            return self.OPTION_STATUS_COLOR[0].get_css_property("background-color") == "rgb(0, 173, 33)"
        raise TypeError("Передан неверный тип объекта")

    @allure.step("Проверка статуса сущности")
    def wait_to_be_enabled(self, type_offer: str) -> None:
        wait_that(
            lambda: self.update_and_check_status_color(type_offer),
            message=f"Статус сущности {type_offer} не стал Активным",
            timeout=50,
            exception=TimeoutError,
            sleep_seconds=2,
        )


class ClientRelatedPersons(DynamicElements):
    def __init__(self) -> None:
        super().__init__()

        self.RELATED_PERSON_NAMES = ElementsList(
            "[class*=linkedPerson_list] [class*=list-scrollable] p:not([color])",
            "Название 'Связанного лица'",
        )
        self.EDIT_RELATED_PERSONS_BTN = Element(
            "[class$=platform-toolbar] > div:not([style]) [data-testid*=linkedPerson][data-testid*=EditButton]",
            "Кнопка Редактировать",
        )
        self.HISTORY_RELATED_PERSONS_BTN = Element(
            "[class$=platform-toolbar] > div:not([style]) [data-testid*=historyButton]", "Кнопка История изменений"
        )


class ClientProfileAttributes(DynamicElements):
    """Страница /customer-hierarchy-management/customers/{customerId}/customer
    Вкладка 'Персональные данные', форма 'Редактирование клиента'"""

    def __init__(self) -> None:
        super().__init__()

        self.EDIT_ATTRIBUTES_BTN = Element("[id*=panel-attributes] button:has([data-icon=Edit])", "Кнопка Редактировать")
        self.EDIT_FORM_LOADER = Element(
            "#customer-individual-edit span[class*='spin-dot']", "Лоадер формы Редактирование клиента"
        )
        self.SURNAME_INPUT = Element("#customer-individual-edit_surname", "Поле Фамилия")
        self.NAME_INPUT = Element("#customer-individual-edit_firstname", "Поле Имя")
        self.PATRONYMIC_INPUT = Element("#patronymic_control input", "Поле Отчество")
        self.IS_PUBLIC_CHECKBOX = Element("div[role=dialog] #publicOfficial_control input", "Поле Публичное лицо")
        self.IS_RESIDENT_CHECKBOX = Element("div[role=dialog] #isResident_control input", "Поле Резидент")
        self.LANGUAGE_DROPDOWN = Select("#customer-individual-edit_speakingLanguage", "Поле Язык общения")
        self.COUNTRY_DROPDOWN = Select("div[role=dialog] #nationality_control input", "Поле Страна регистрации")
        self.BIRTH_PLACE = Element("#customer-individual-edit_birthPlace", "Поле Место рождения")
        self.BIRTH_DATE = DatePicker("div[role=dialog] #birthDate_control input", "Дата рождения")
        self.GENDER = Select("#customer-individual-edit_gender", "Пол")
        self.DOCUMENT_TYPE = Select("#customer-individual-edit_documentType", "Тип документа")
        self.DOCUMENT_SERIAL = Element("div[role=dialog] #documentSeries_control input", "Серия документа")
        self.DOCUMENT_NUMBER = Element("div[role=dialog] #documentNumber_control input", "Номер документа")
        self.DOCUMENT_DATE = DatePicker("div[role=dialog] #documentDateOfIssue_control input", "Дата выдачи")
        self.DOCUMENT_PROVIDE_BY = Element("#customer-individual-edit_documentProvidedByOrganization", "Кем выдан")
        self.DOCUMENT_DIVISION_CODE = Element("div[role=dialog] #documentDivisionCode_control input", "")
        self.DOCUMENT_VALID_DATE = DatePicker(
            "div[role=dialog] #documentValidFor_control input", "Дата, до которой действует документ"
        )
        self.INN = Element("div[role=dialog] #taxIdentificationNumber_control input", "ИНН")

        self.HISTORY_BTN = Element("button:has([data-icon=History])", "Кнопка 'История изменений'")
        self.HISTORY_SIDEBAR_TITLE = Element(
            "[class*=drawer-open] [class*=drawer-title] h3",
            "Заголовок сайдбара истории",
        )
        self.HISTORY_SIDEBAR_CLOSE_BTN = Element(
            "[data-testid=chm-HistorySidebar-drw-1-cancel-btn]",
            "Кнопка закрытия сайдбара истории изменений",
        )

        self.REFRESH_BTN = Element(
            "//button[.//span[@data-icon='Refresh']]",
            "Кнопка обновления истории изменений",
        )

        self.HISTORY_TABLE_ROWS = ElementsList(
            "[class*=drawer-open] [class*=table-tbody] [class*=table-row][data-row-key]",
            "Строки таблицы истории изменений",
        )

        self.HISTORY_TABLE_ROW_ATTRIBUTE = ElementsList(
            "[class*=drawer-open] [class*=table-tbody] [class*=table-row][data-row-key] [class*=table-cell]:nth-child(3)",
            "Атрибуты строк таблицы",
        )

        self.HISTORY_TABLE_ROW_OPERATIONS = ElementsList(
            "[class*=drawer-open] [class*=table-tbody] [class*=table-row][data-row-key] [class*=table-cell]:nth-child(4)",
            "Старые значения строк таблицы",
        )

        self.HISTORY_TABLE_ROW_OLD_VALUES = ElementsList(
            "[class*=drawer-open] [class*=table-tbody] [class*=table-row][data-row-key] [class*=table-cell]:nth-child(5)",
            "Старые значения строк таблицы",
        )

        self.HISTORY_TABLE_ROW_NEW_VALUES = ElementsList(
            "[class*=drawer-open] [class*=table-tbody] [class*=table-row][data-row-key] [class*=table-cell]:nth-child(6)",
            "Новые значения строк таблицы",
        )


class ClientProfileEndUser(DynamicForms):
    """Страница /customer-hierarchy-management/customers/{customerId}/products?subscription={subscriptionId}
    Вкладка 'Продукты', форма 'Абонент'"""

    def __init__(self) -> None:
        super().__init__()

        self.ADD_END_USER_BUTTON = Element(
            " div[id*=user-view] div[class*=platform-empty-state-container] button",
            "Добавить данные (Конечный пользователь)",
        )
        self.DOCUMENT_TYPE_DROPDOWN = Select(
            "#end-user-add-identification_documentType", "Тип документа, удостоверяющего личность"
        )
        self.DOCUMENT_SERIES = Element("#end-user-add-identification_documentSeries", "Серия")
        self.DOCUMENT_NUMBER = Element("#end-user-add-identification_documentNumber", "Номер")
        self.EXISTING_CLIENT_FOUND_TITLE = Element("#end-user-add-customer-selection h4", "Найден существующий клиент")
        self.LINKED_CLIENT_FOUND_TITLE = Element("#end-user-add-linked-person-selection h4", "Найдены связанные лица")
        self.CLIENT = ElementsList("#end-user-add-customer-selection", "Клиент")
        self.LINKED_CLIENT = ElementsList("#end-user-add-linked-person-selection", "Связанное лицо")
        self.ADD_END_USER_NEXT_BUTTON = Element(
            "(//div[contains(@class, 'drawer-footer')]/div/div)[3]//button", "Добавить"
        )
        self.ADD_LINKED_END_USER_NEXT_BUTTON = Element("[class*='drawer-footer'] div:nth-child(3) button", "Добавить")
        self.DATA_TITLE = Element("(//*[@id='end-user-view'] //h4)[last()]", "Данные конечного пользователя")
        self.CLOSE_END_USER_MODAL_BUTTON = Element("#_cancel-button", "Закрыть")
        self.EDIT_END_USER_BUTTON = Element(
            "[class$=platform-toolbar] > div:not([style]) [data-testid*=editEndUser]", "Кнопка 'Редактировать'"
        )
        self.REPLACE_END_USER_BUTTON = Element(
            "[class$=platform-toolbar] > div:not([style]) [data-testid*=replaceEndUser]", "Кнопка 'Заменить'"
        )

        self.ACCOUNT_ID = Element("#end-user-view_accountNumber", "Лицевой счет")
        self.BALANCE = Element("#end-user-view_balance", "Баланс")
        self.FIO = Element("#end-user-view #end-user-view_fullName", "ФИО")
        self.GENDER = Element("#end-user-view_gender", "Пол")
        self.DOCUMENT_TYPE = Element("#end-user-view_documentType", "Тип документа удостоверяющего личность")
        self.DOCUMENT_SERIES_AND_NUMBER = Element("#end-user-view_documentNumber", "Серия и номер документа")
        self.DOCUMENT_PROVIDE_BY = Element("#end-user-view_documentProvidedByOrganization", "Кем выдан документ")
        self.SUBDIVISION_CODE = Element("#end-user-view_documentDivisionCode", "Код подразделения")
        self.DATE_OF_ISSUE = Element("#end-user-view_documentDateOfIssue", "Дата выдачи")
        self.DOCUMENT_VALID_FOR = Element("#end-user-view_documentValidFor", "Дата, до которой действует документ")
        self.PLACE_OF_BIRTH = Element("#end-user-view_birthPlace", "Место рождения")
        self.BIRTHDAY = Element("#end-user-view_birthDate", "Дата рождения")
        self.COUNTRY = Element("#end-user-view_registrationCountry", "Страна регистрации")
        self.LANGUAGE = Element("#end-user-view_speakingLanguage", "Язык")
        self.REGISTRATION_ADDRESS = Element("#end-user-view_registrationAddress", "Адрес регистрации")
        self.IS_PUBLIC = Element("label:has(#end-user-view_publicOfficial)", "Публичное лицо")
        self.IS_RESIDENT = Element("label:has(#end-user-view_isResident)", "Резидентство")

        self.SURNAME_INPUT = Element("#end-user-add-fill-customer-data_surname, #end-user-edit_surname", "Поле Фамилия")
        self.NAME_INPUT = Element("#end-user-add-fill-customer-data_firstName, #end-user-edit_firstName", "Поле Имя")
        self.PATRONYMIC_INPUT = Element(
            "#end-user-add-fill-customer-data_patronymic, #end-user-edit_patronymic", "Поле Отчество"
        )
        self.GENDER_DROPDOWN = Select("#end-user-add-fill-customer-data_gender, #end-user-edit_gender", "Дропдаун Пол")
        self.WHO_ISSUED_THE_DOCUMENT_INPUT = Element(
            "#end-user-add-fill-customer-data_documentProvidedByOrganization, #end-user-edit_documentProvidedByOrganization",
            " Поле Кем выдан документ",
        )
        self.SUBDIVISION_CODE_INPUT = Element(
            "#end-user-add-fill-customer-data_documentDivisionCode, #end-user-edit_documentDivisionCode",
            "Поле Код подразделения",
        )
        self.DATE_OF_ISSUE_INPUT = Element(
            "#end-user-add-fill-customer-data_documentDateOfIssue, #end-user-edit_documentDateOfIssue",
            "Поле Дата выдачи",
        )
        self.DOCUMENT_VALID_FOR_INPUT = DatePicker(
            "#end-user-add-fill-customer-data_documentValidFor, #end-user-edit_documentValidFor",
            "Поле Дата, до которой действует документ",
        )
        self.PLACE_OF_BIRTH_INPUT = Element(
            "#end-user-add-fill-customer-data_birthPlace, #end-user-edit_birthPlace", "Поле Место рождения"
        )
        self.BIRTHDAY_INPUT = Element(
            "#end-user-add-fill-customer-data_birthDate, #end-user-edit_birthDate", "Поле Дата рождения"
        )
        self.COUNTRY_DROPDOWN = Select("#nationality_control, #end-user-edit_nationality", "Дропдаун Страна регистрации")
        self.LANGUAGE_DROPDOWN = Select(
            "#speakingLanguage_control, #end-user-edit_speakingLanguage", "Дропдаун Язык общения"
        )
        self.REGISTRATION_ADDRESS_INPUT = Autocomplete(
            "#end-user-add-fill-customer-data_address, #end-user-edit_registrationAddress",
            "Поле Адрес регистрации",
        )
        self.IS_PUBLIC_CHECKBOX = Element(
            "#end-user-edit_publicOfficial",
            "Чекбокс Публичное лицо",
        )
        self.IS_RESIDENT_CHECKBOX = Element("#end-user-edit_isResident", "Чекбокс Резидентство")
        self.LOADER = Element("form span[class*='spin-dot']", "Лоадер на форме добавления конечного пользователя")


class PersonalAccountForm(DynamicForms):
    """Страница /customer-hierarchy-management/accounts/{accountId}/account
    Вкладка 'Лицевой счет', Форма 'Лицевой счет'"""

    def __init__(self) -> None:
        super().__init__()

        self.ACCOUNT_PRIORITY = Element(
            "#priorityAccountForPayment_control span[class*=checkbox-label]",
            "Приоритетный ЛС для приёма платежа по Абоненту",
        )
        self.ACCOUNT_PRIORITY_INPUT = Element(
            "#account-card-edit_priorityAccountForPayment",
            "Чекбокс 'Приоритетный ЛС для приёма платежа по Абоненту'",
        )
