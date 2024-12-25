from playwright.sync_api import Page
from pages.locators.ui_elements import Element, ElementsList
from pages.locators.base_elements import BaseElements
import allure


class DynamicElements(BaseElements):
    """На разных страницах/формах присутствуют элементы идентичные по бизнес логике.
    Например, как номер телефона. Он может присутствовать и при создании карточки клиента,
    редактировании, просмотре и т.д. аттрибут id отличается только префиксом. По этому такие элементы,
    имеют универсальный селектор для их нахождения."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.ACCOUNT_NUM = "input[id*='accountNumber']"
        self.SUBSCRIPTION_ID = "input[id*='subscriptionIdentification']"
        self.CONTRACT_NUM = "input[id*='agreementNumber']"
        self.INN = Element("input[id*='create_taxIdentificationNumber']", "ИНН", self.page)
        self.KPP = Element("input[id*='registrationReasonCode']", "КПП", self.page)
        self.SNILS = Element("input[id*='create_INILA']", "СНИЛС", self.page)
        self.CUSTOMER_TYPE = "input[id*='customerTypes']"
        self.CUSTOMER_NAME = "input[id*='customerName']"
        self.ID_DOCUMENT_SERIAL = "input[id*='identificationDocumentSeries']"
        self.ID_DOCUMENT_NUM = "input[id*='identificationDocumentNumber']"
        self.DOCUMENT_SERIAL = Element("input[id*='documentSeries']", "Серия документа", self.page)
        self.DOCUMENT_NUM = Element("input[id*='documentNumber']", "Номер документа", self.page)
        self.NATIONALITY = "input[id*='nationality']"
        self.SPEAKING_LANGUAGE = Select("input[id*='speakingLanguage']", "Язык общения", self.page)
        self.RESIDENT_CHECKBOX = "input[id*='isResident']"
        self.BUSINESS_ACTIVITY = "input[id*='businessActivity']"
        self.NOTE = "textarea[id*='note']"
        self.REGISTRATION_ADDRESS = Autocomplete("input[id*='registrationAddress']", "Адрес регистрации", self.page)
        self.REPUTATION = "input[id*='reputation']"
        self.OKPO = "input[id*='RNNBO']"
        self.OKATO = "input[id*='ARCPS']"
        self.OKVED = "input[id*='economicActivities']"
        self.OGRN = "input[id*='PSRN']"
        self.PUBLIC_PERSON_CHECKBOX = "input[id*='publicOfficial']"
        self.BIRTH_PLACE = Element("input[id*='birthPlace']", "Место рождения", self.page)
        self.BIRTH_DATE = DatePicker("input[id*='birthDate']", "Дата рождения", self.page)
        self.GENDER = Select("input[id*='gender']", "Пол", self.page)
        self.DOCUMENT_TYPE = Select("input[id*='documentType']", "Тип документа", self.page)
        self.DOCUMENT_DATE = DatePicker("input[id*='documentDateOfIssue']", "Дата выдачи", self.page)
        self.DOCUMENT_PROVIDE_BY = Element("input[id*='documentProvidedByOrganization']", "Кем выдан", self.page)
        self.DOCUMENT_DIVISION_CODE = Element("input[id*='documentDivisionCode']", "Код подразделения", self.page)
        self.DOCUMENT_VALID_DATE = DatePicker("input[id*='documentValidFor']", "Дата действия документа", self.page)
        self.REASON_TYPE = Select("input[id*='reasonType']", "Тип причины", self.page)
        self.PRIORITY = Select("#priority", "Приоритет", self.page)
        self.POTENTIAL = Select("#potential", "Потенциал", self.page)

        self.DEADLINE = Select("#CF_DEDLINE", "Планируемый срок решения", self.page)

        self.REGISTRATION_DOCUMENT = "input[id*='PSRNInfo']"
        self.REGISTRATION_DATE = "input[id*='registrationDate']"
        self.REGISTRATION_NUM = "input[id*='foreignRegistrationNumber']"
        self.TAX_SCHEME = "input[id*='taxScheme']"


class DynamicForms(DynamicElements):
    def __init__(self, page: Page):
        super().__init__(page)
        """Общие элементы динамических форм."""
        self.TITLE = Element(".ant-drawer-title h3", "Заголовок формы", self.page)
        self.CROSS_BTN = Element(".ant-drawer-open  button[aria-label='Close']", "Крестик", self.page)
        self.CANCEL_BTN = Element("#cancel", "Отменить", self.page)
        self.SAVE_BTN = Element("#save", "Сохранить", self.page)
        self.CLOSE_BTN = Element("#close", "Закрыть", self.page)
        self.FORWARD_BTN = Element("#forward", "Перейти", self.page)

        self.INNER_CANCEL_BTN = Element("#_cancel-button", "Внутренняя кнопка закрытия", self.page)
        self.INNER_SAVE_BTN = Element("#_save-button", "Внутренняя кнопка сохранения", self.page)
        self.INNER_ACCEPT_BTN = Element("#_accept-button", "Внутренняя кнопка 'Выбрать'", self.page)


class FlCustomerCreate(DynamicForms):
    """Форма 'Создание клиента ФЛ'"""
    def __init__(self, page: Page):
        super().__init__(page)

        self.LAST_NAME = Element("#customer-individual-create_surname", "Фамилия", self.page)
        self.FIRST_NAME = Element("#customer-individual-create_firstname", "Имя", self.page)
        self.SUR_NAME = Element("#customer-individual-create_patronymic", "Отчество", self.page)
        self.DOCUMENT_TYPE_DROPDOWN = Element("#customer-individual-create_documentType", "Тип документа", self.page)

        self.CREATE_ADDRESS_LINK = Element("#customer-individual-create_registrationAddress_list", "Добавить адрес", self.page)

        self.BIOMETRIC_CHECKBOX = Element("#customer-individual-create_biometricData", "Биометрические данные", self.page)
        self.CONTACT_PHONE = Element("#customer-individual-create_contactPhoneNumber", "Телефон", self.page)
        self.CONTACT_EMAIL = Element("#customer-individual-create_contactEmail", "Почта", self.page)

    @allure.step("Заполнить данные клиента ФЛ")
    def fill_data_for_individual_client(self, **kwargs):
        start_date = datetime.date(1990, 1, 1)
        end_date = datetime.date(2020, 12, 31)

        self.LAST_NAME.fill(kwargs.get('last_name') or f'автотесты-{faker_ru.last_name()}')
        self.FIRST_NAME.fill(kwargs.get('first_name') or f'автотесты-{faker_ru.first_name()}')
        self.SUR_NAME.fill(kwargs.get('sur_name') or 'Автотестович')
        self.GENDER.select_by_value(kwargs.get('gender') or 'Мужской')
        self.DOCUMENT_TYPE.select_by_value(kwargs.get('document_type') or 'Паспорт гражданина РФ')
        self.DOCUMENT_SERIAL.fill(kwargs.get('document_serial') or str(generate_random_number(4)), check=False)
        self.DOCUMENT_NUM.fill(kwargs.get('document_num') or str(generate_random_number(6)))
        self.DOCUMENT_PROVIDE_BY.fill(kwargs.get('document_provide_by') or 'ГУ МВД РОССИИ')
        self.DOCUMENT_DIVISION_CODE.fill(kwargs.get('document_division_code') or f"{generate_random_number(3)}-{generate_random_number(3)}")
        self.DOCUMENT_DATE.fill(kwargs.get('document_date') or faker_ru.date_between(start_date, end_date).strftime('%d.%m.%Y'))
        self.DOCUMENT_VALID_DATE.fill(kwargs.get('document_valid_date') or faker_ru.date_between(datetime.datetime.today(),
                                                                   get_shifted_datetime("+500d")).strftime('%d.%m.%Y'))
        self.BIRTH_DATE.fill(kwargs.get('birth_date') or faker_ru.date_of_birth().strftime('%d.%m.%Y'))
        self.BIRTH_PLACE.fill(kwargs.get('birth_place') or faker_ru.city())
        self.REGISTRATION_ADDRESS.select_by_value(kwargs.get('registration_address') or BasicSystemAddress.address)
        self.INN.fill(kwargs.get('inn') or str(generate_random_number(12)))
        self.SNILS.fill(kwargs.get('snils') or str(generate_random_number(11)))
        self.CONTACT_PHONE.fill(kwargs.get('contact_phone') or faker_ru.phone_number())
        self.CONTACT_EMAIL.fill(kwargs.get('contact_email') or faker_ru.email())


class CreateOrganization(DynamicForms):
    """Форма 'Создание клиента'."""
    PROPRIETARY_FORM = "#customer-organization-create_proprietaryForm"


class AddressCreate(DynamicForms):
    """Форма 'Создание нового адреса'."""
    def __init__(self, page: Page):
        super().__init__(page)

        self.TITLE = Element("//h3[contains(text(), 'Создание нового адреса')]", "Заголовок формы", self.page)
        self.ADDED_CARD = ElementsList(".ant-card",
                                       "Блоки с выбранным типом и наименованием адресного объекта", self.page)
        self.ADDED_CARD_EDIT_BTN = ElementsList(".ant-card-extra button:nth-child(1)",
                                                "Кнопки 'Редактировать'", self.page)
        self.ADDED_CARD_DELETE_BTN = ElementsList(".ant-card-extra button:nth-child(2)",
                                                  "Кнопки 'Удалить'", self.page)
        self.ATTRIBUTE_HEADER = ElementsList(".ant-collapse-item", "Панель с кнопкой 'Атрибуты'", self.page)

        self.OPTION_ITEMS = ElementsList("[id*='create-address-form'] .ant-select-item-option",
                                         "Варианты выбора в списке", self.page)
        self.OBJECT_TYPE = Select("[id*='_select-elementCode']", "Поле 'Выберите адресный объект'", self.page)
        self.OBJECT_NAME_AUTOCOMPLETE = Autocomplete(".ant-row.ant-form-item-row:has(label[title='Наименование']) input[id*='rc_select']", "Поле 'Наименование'", self.page)
        self.OBJECT_NUM = Element(".ant-row.ant-form-item-row:has(label[title='Номер']) input[id*='rc_select']",
                                  "Поле 'Номер'", self.page)
        self.OBJECT_ADDITIONAL_NUM = Element(".ant-row.ant-form-item-row:has(label[title='Дополнительный номер'])"
                                             " input[id*='rc_select']", "Поле 'Дополнительный номер'", self.page)
        self.OBJECT_EXTRA_NUM = Element(".ant-row.ant-form-item-row:has(label[title='Добавочный номер'])"
                                        " input[id*='rc_select']", "Поле 'Добавочный номер'", self.page)
        self.OBJECT_GAR = Element(".ant-row.ant-form-item-row:has(label[title='Уникальный номер ГАР'])"
                                  " input[id*='rc_select']", "Поле 'Уникальный номер ГАР'", self.page)
        self.OBJECT_MAIL_INDEX = Element(".ant-row.ant-form-item-row:has(label[title='Почтовый индекс'])"
                                         " input[id*='rc_select']", "Поле 'Почтовый индекс'", self.page)

        self.REGION_TYPE_DROPDOWN = Select("input[id*='regionType']",
                                            "Поле ввода 'Тип региона'", self.page)
        self.CITY_TYPE_DROPDOWN = Select("input[id*='cityType']",
                                          "Поле ввода 'Тип города'", self.page)
        self.STREET_TYPE_DROPDOWN = Autocomplete("input[id*='form_street_streetType']",
                                            "Поле ввода 'Тип улицы'", self.page)
        self.HOUSE_TYPE_DROPDOWN = Autocomplete("input[id*='houseType']",
                                           "Поле ввода 'Тип дома'", self.page)
        self.APARTMENT_TYPE_DROPDOWN = Select("input[id*='apartmentType']",
                                               "Поле ввода 'Тип жилого помещения'", self.page)
        self.ADDITIONAL_HOUSE_TYPE_DROPDOWN = Element("input[id*='house_additionalType']",
                                                      "Поле ввода 'Дополнительный тип дома'", self.page)
        self.EXTRA_HOUSE_TYPE_DROPDOWN = Element("input[id*='house_extraType']",
                                                 "Поле ввода 'Добавочный тип дома'", self.page)
        self.APPLY_BTN = Element("[id*='save-button']",
                                 "Кнопка 'Применить'", self.page)
        self.ADD_ADDRESS_OBJECT_BTN = Element("[id*='add-address-element-button']",
                                              "Кнопка 'Добавить адресный объект'", self.page)
        self.CREATE_BTN = Element("[id*='create-address-modal_accept-button']", "Кнопка 'Создать'",
                                  self.page)


class AddAddress(DynamicForms):
    """Форма 'Добавление нового адреса'."""
    def __init__(self, page: Page):
        super().__init__(page)

        self.TITLE = Element("//h3[contains(text(), 'Добавление адреса')]", "Заголовок формы", self.page)
        self.ADDRESS_TYPE_FIELD = Select("#place-add_placeType", "Поле ввода 'Тип адреса'", self.page)
        self.ADDRESS_TYPE_OPTIONS = ElementsList(".ant-select-item-option", "Выбор 'Тип адреса'", self.page)
        self.ADDRESS_INPUT = Element("#place-add_addressString", "Поле ввода 'Адреса'", self.page)
        self.ADD_ADDRESS_TO_CATALOG = Element("a[href='/rm-ui/allundefined']",
                                              "Ссылка 'Добавить адрес в справочник'", self.page)
        self.MAPS_LINK_INPUT = Element("#place-add_addressUrl", "Поле ввода 'Ссылка на карту'", self.page)
        self.ADDRESS_OPTION = ElementsList("#addressString_control .ant-select-item-option-content",
                                           "Выделенное всплывающее адрес", self.page)
        self.SAVE_BTN = Element("#save", "Кнопка 'Добавить'", self.page)
        self.CANCEL_BTN = Element("#cancel", "Кнопка 'Отмена'", self.page)


class EditAddressInfo(DynamicForms):
    """Форма 'Редактирование адресной информации'"""
    def __init__(self, page: Page):
        super().__init__(page)

        self.ADD_BUTTON = Element("button[title='Добавить']", "Кнопка 'Добавить'", self.page)
        self.TABLE_LINE = ElementsList("//tr", "Строки таблицы", self.page)
        self.TABLE_LINE_MAP_BUTTON = ElementsList("td svg", "Строки таблицы кнопка карты", self.page)
        self.CANCEL_BTN = Element("#_cancel-button", "Кнопка 'Закрыть'", self.page)


class RequestCreate(DynamicForms):
    """Форма 'Создание заявки'."""
    def __init__(self, page: Page):
        super().__init__(page)

        self.CLIENT = Element("#inquiry-create-form a", "Выбранный клиент", self.page)
        self.SELECT_CLIENT_BTN = Dropdown("#inquiry-create-form button:has(.platform-button__icon_right)", "Сменить клиента", self.page)
        CODE = "#code"
        TOPIC = "#topic"
        EMAIL = "#email"
        PHONE = "#phone"
        DESCRIPTION = "#description"
        FILE_INPUT = "input[type='file']"



class ClientChoice(DynamicForms):
    """Форма 'Выбор клиента'."""
    def __init__(self, page: Page):
        super().__init__(page)

        self.INN = Element("#search-customer_taxIdentificationNumber", "ИНН", self.page)
        self.RESET_BTN = Element("#resetButton", "Кнопка 'Сбросить'", self.page)
        self.FIND_BTN = Element("#findButton", "Кнопка 'Найти'", self.page)

        self.FOUNDED_CUSTOMER = ElementsList("#search-customer-table .ant-table-tbody tr", "Клиенты", self.page)

        # FOUNDED_CUSTOMER
        self.FOUNDED_FIO = ElementsList("#search-customer-table .ant-table-tbody tr td:nth-child(1)", "ФИО клиента", self.page)
        self.FOUNDED_CUSTOMER_TYPE = ElementsList("#search-customer-table .ant-table-tbody tr td:nth-child(2)", "Тип клиента", self.page)
        self.FOUNDED_CUSTOMER_STATUS = ElementsList("#search-customer-table .ant-table-tbody tr td:nth-child(3)", "Статус клиента", self.page)
        self.FOUNDED_DOCUMENT_NUM = ElementsList("#search-customer-table .ant-table-tbody tr td:nth-child(4)", "Номер документа", self.page)
        self.FOUNDED_CONTRACT = ElementsList("#search-customer-table .ant-table-tbody tr td:nth-child(5)", "Договор", self.page)


class CreateSalesAndServiceManagement(RequestCreate):
    """Форма 'Создание продажи и управления услугами'"""
    def __init__(self, page: Page):
        super().__init__(page)

        self.CONTACT_PERSON = Element("#inqrLinkedPerson", "Контактное лицо", self.page)
        self.EMAIL = Element(".ant-col:has([for='email']) input", "Предпочтительный email", self.page)
        self.PHONE = Element(".ant-col:has([for='phone']) input", "Предпочтительный телефон", self.page)
        self.SELECTED_SALE = Element("#saleAgreement", "Договор", self.page)
        self.ADD_SALE_TYPE = Element("#saleAddAgreement", "Создание Договора", self.page)
        self.DESCRIPTION = Element("#description", "Описание", self.page)
        self.FILE_INPUT = Element("input[type='file']", "Документы", self.page)
        self.END_DATE = Element(".ant-form-item:has(label[|title='Планируемая дата окончания'],[|title='Планируемая дата окончания']) "
                    ".ant-form-item-control-input-content", "Планируемая дата окончания", self.page)


class EditDynamicElements(BaseElements):
    """Динамические элементы в редактировании.
    (Отличается от класса DynamicElements,
    только префиксом edit_ в id элемента)."""
    ACCOUNT_NUM = "input[id*='edit_accountNumber']"
    SUBSCRIPTION_ID = "input[id*='edit_subscriptionIdentification']"
    CONTRACT_NUM = "input[id*='edit_agreementNumber']"
    INN = "input[id*='edit_taxIdentificationNumber']"
    KPP = "input[id*='edit_registrationReasonCode']"
    SNILS = "input[id*='edit_INILA']"
    CUSTOMER_TYPE = "input[id*='edit_customerTypes']"
    CUSTOMER_NAME = "input[id*='edit_customerName']"
    ID_DOCUMENT_SERIAL = "input[id*='edit_identificationDocumentSeries']"
    ID_DOCUMENT_NUM = "input[id*='edit_identificationDocumentNumber']"
    DOCUMENT_SERIAL = "input[id*='edit_documentSeries']"
    DOCUMENT_NUM = "input[id*='edit_documentNumber']"
    NATIONALITY = "input[id*='edit_nationality']"
    SPEAKING_LANGUAGE = "input[id*='edit_speakingLanguage']"
    RESIDENT_CHECKBOX = "input[id*='edit_isResident']"
    BUSINESS_ACTIVITY = "input[id*='edit_businessActivity']"
    NOTE = "textarea[id*='edit_note']"
    REGISTRATION_ADDRESS = "input[id*='edit_registrationAddress']"
    REPUTATION = "input[id*='edit_reputation']"
    OKPO = "input[id*='edit_RNNBO']"
    OKATO = "input[id*='edit_ARCPS']"
    OKVED = "input[id*='edit_economicActivities']"
    OGRN = "input[id*='edit_PSRN']"
    PUBLIC_PERSON_CHECKBOX = "input[id*='edit_publicOfficial']"
    BIRTH_PLACE = "input[id*='edit_birthPlace']"
    BIRTH_DATE = "input[id*='edit_birthDate']"
    GENDER_DROPDOWN = "input[id*='edit_gender']"
    DOCUMENT_TYPE = "input[id*='edit_documentType']"
    DOCUMENT_DATE = "input[id*='edit_documentDateOfIssue']"
    DOCUMENT_PROVIDE_BY = "input[id*='edit_documentProvidedByOrganization']"
    DOCUMENT_DIVISION_CODE = "input[id*='edit_documentDivisionCode']"
    DOCUMENT_VALID_DATE = "input[id*='edit_documentValidFor']"

    REGISTRATION_DOCUMENT = "input[id*='edit_PSRNInfo']"
    REGISTRATION_DATE = "input[id*='edit_registrationDate']"
    REGISTRATION_NUM = "input[id*='edit_foreignRegistrationNumber']"
    TAX_SCHEME = "input[id*='edit_taxScheme']"


class Notifications(BaseElements):
    def __init__(self, page: Page = None):
        super().__init__(page)

        self.SUCCESS_CREATE_CLIENT = Element("#notifications p",
                                             "Уведомление 'Клиент создан'",
                                             self.page)
        self.SUCCESS_NOTIFICATIONS_CLOSE_BTN = Element("#notifications > div > div > :nth-child(2)",
                                                       "Кнопка 'Закрыть уведомление",
                                                       self.page)



class AddAgreement(DynamicForms):
    """Форма 'Добавление нового договора'."""
    def __init__(self, page: Page):
        super().__init__(page)

class EditCustomerAttributes(EditDynamicElements):
    pass
