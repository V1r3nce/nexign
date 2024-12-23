from playwright.sync_api import Page
from pages.locators.ui_elements import Element, ElementsList
from pages.locators.base_elements import BaseElements


class DynamicElements(BaseElements):
    def __init__(self, page: Page = None):
        super().__init__(page)
        """На разных страницах/формах присутствуют элементы идентичные по бизнес логике.
        Например, как номер телефона. Он может присутствовать и при создании карточки клиента,
        редактировании, просмотре и т.д. аттрибут id отличается только префиксом. По этому такие элементы,
        имеют универсальный селектор для их нахождения."""

        ACCOUNT_NUM = "input[id*='accountNumber']"
        SUBSCRIPTION_ID = "input[id*='subscriptionIdentification']"
        self.CONTRACT_NUM = Element("input[id*='agreementNumber']",
                                    "Поле 'Номер контракта'",
                                    self.page)
        self.INN = Element("input[id*='create_taxIdentificationNumber']",
                           "Поле ИНН", self.page)
        self.KPP = Element("input[id*='registrationReasonCode']",
                           "Поле КПП", self.page)
        #self.OPERATOR_BANK = Element("input[id*=create_bankOperator]",)
        self.OPERATOR_BANK_DETAILS = Element("input[id*='create_bankOperator']",
                                             "Поле оператора 'Банк и расчетный счет",
                                             self.page)
        self.SNILS = Element("input[id*='create_INILA']",
                             "Поле СНИЛС", self.page)
        CUSTOMER_TYPE = "input[id*='customerTypes']"
        CUSTOMER_NAME = "input[id*='customerName']"
        ID_DOCUMENT_SERIAL = "input[id*='identificationDocumentSeries']"
        ID_DOCUMENT_NUM = "input[id*='identificationDocumentNumber']"
        self.DOCUMENT_SERIAL = Element("input[id*='documentSeries']",
                                       "Поле Серия", self.page)
        self.DOCUMENT_NUM = Element("input[id*='documentNumber']",
                                    "Поле Номер", self.page)
        NATIONALITY = "input[id*='nationality']"
        SPEAKING_LANGUAGE = "input[id*='speakingLanguage']"
        RESIDENT_CHECKBOX = "input[id*='isResident']"
        BUSINESS_ACTIVITY = "input[id*='businessActivity']"
        NOTE = "textarea[id*='note']"
        self.REGISTRATION_ADDRESS = Element("input[id*='registrationAddress']",
                                            "Поле Адрес регистрации", self.page)
        REPUTATION = "input[id*='reputation']"
        OKPO = "input[id*='RNNBO']"
        OKATO = "input[id*='ARCPS']"
        OKVED = "input[id*='economicActivities']"
        OGRN = "input[id*='PSRN']"
        PUBLIC_PERSON_CHECKBOX = "input[id*='publicOfficial']"
        self.BIRTH_PLACE = Element("input[id*='birthPlace']",
                                   "Поле Местро рождения", self.page)
        self.BIRTH_DATE = Element("input[id*='birthDate']",
                                  "Поле Дата рождения", self.page)
        self.GENDER_DROPDOWN = Element("input[id*='gender']",
                                       "Поле выбора пола", self.page)
        self.DOCUMENT_TYPE = Element("input[id*='documentType']",
                                     "Поле Документ", self.page)
        self.DOCUMENT_DATE = Element("input[id*='documentDateOfIssue']",
                                     "Поле Дата выдачи", self.page)
        self.DOCUMENT_PROVIDE_BY = Element("input[id*='documentProvidedByOrganization']",
                                           "Поле 'Кем выдан'", self.page)
        self.DOCUMENT_DIVISION_CODE = Element("input[id*='documentDivisionCode']",
                                              "Поле Код подразделения", self.page)
        self.DOCUMENT_VALID_DATE = Element("input[id*='documentValidFor']",
                                           "Поле Дата действия", self.page)

        REGISTRATION_DOCUMENT = "input[id*='PSRNInfo']"
        REGISTRATION_DATE = "input[id*='registrationDate']"
        REGISTRATION_NUM = "input[id*='foreignRegistrationNumber']"
        TAX_SCHEME = "input[id*='taxScheme']"


class DynamicForms(DynamicElements):
    def __init__(self, page: Page):
        super().__init__(page)

        """Общие элементы динамических форм."""
        TITLE = ".ant-drawer-title h3"
        CROSS_BTN = ".ant-drawer-open  button[aria-label='Close']"
        CANCEL_BTN = "#cancel"
        self.SAVE_BTN = Element("#save",
                                "Кнопка 'Сохранить'", self.page)
        CLOSE_BTN = "#close"
        FORWARD_BTN = "#forward"

        INNER_CANCEL_BTN = "#_cancel-button"
        INNER_SAVE_BTN = "#_save-button"
        self.CREATE_BTN = Element("#create",
                                  "Кнопка 'Создать",
                                  self.page)


class FlCustomerCreate(DynamicForms):
    def __init__(self, page: Page = None):
        super().__init__(page)

        """Форма 'Создание клиента ФЛ'"""
        self.LAST_NAME = Element("#customer-individual-create_surname",
                            "Поле ввода Фамилии", self.page)
        self.FIRST_NAME = Element("#customer-individual-create_firstname",
                                  "Поле ввода Имени", self.page)
        self.SUR_NAME = Element("#customer-individual-create_patronymic",
                                "Поле ввода Отчества", self.page)
        DOCUMENT_TYPE_DROPDOWN = "#customer-individual-create_documentType"

        CREATE_ADDRESS_LINK = "#customer-individual-create_registrationAddress_list"

        BIOMETRIC_CHECKBOX = "#customer-individual-create_biometricData"
        self.CONTACT_PHONE = Element("#customer-individual-create_contactPhoneNumber",
                                     "Поле Контактный телефон", self.page)
        self.CONTACT_EMAIL = Element("#customer-individual-create_contactEmail",
                                     "Поле Контактный email", self.page)



class CreateOrganization(DynamicForms):
    """Форма 'Создание клиента'."""
    PROPRIETARY_FORM = "#customer-organization-create_proprietaryForm"


class AddressCreate(DynamicForms):
    """Форма 'Создание нового адреса'."""
    ADDED_CARD = ".ant-card"
    ADDED_CARD_EDIT_BTN = ".ant-card-extra button:nth-child(1)"
    ADDED_CARD_DELETE_BTN = ".ant-card-extra button:nth-child(2)"

    OBJECT_TYPE = "#_select-elementCode"
    OBJECT_NAME_AUTOCOMPLETE = ".ant-row.ant-form-item-row:has(label[title='Наименование']) input[id*='rc_select']"
    OBJECT_NUM = ".ant-row.ant-form-item-row:has(label[title='Номер']) input[id*='rc_select']"
    OBJECT_ADDITIONAL_NUM = ".ant-row.ant-form-item-row:has(label[title='Дополнительный номер']) input[id*='rc_select']"
    OBJECT_EXTRA_NUM = ".ant-row.ant-form-item-row:has(label[title='Добавочный номер']) input[id*='rc_select']"
    OBJECT_GAR = ".ant-row.ant-form-item-row:has(label[title='Уникальный номер ГАР']) input[id*='rc_select']"
    OBJECT_MAIL_INDEX = ".ant-row.ant-form-item-row:has(label[title='Почтовый индекс']) input[id*='rc_select']"

    REGION_TYPE_DROPDOWN = "#customer-individual-create_registrationAddress_create-address-form_region_regionType"
    HOUSE_TYPE_DROPDOWN = "#customer-individual-create_registrationAddress_create-address-form_house_houseType"
    ADDITIONAL_HOUSE_TYPE_DROPDOWN = "#customer-individual-create_registrationAddress_create-address-form_house_additionalType"
    EXTRA_HOUSE_TYPE_DROPDOWN = "#customer-individual-create_registrationAddress_create-address-form_house_extraType"

    APARTMENT_TYPE = "#customer-individual-create_registrationAddress_create-address-form_apartment_apartmentType"

    ADD_ADDRESS_OBJECT_BTN = "#customer-individual-create_registrationAddress_add-address-element-button"


class AddAddress(DynamicForms):
    """Форма 'Добавление нового адреса'."""
    def __init__(self, page: Page):
        super().__init__(page)

        self.TITLE = Element("//h3[contains(text(), 'Добавление адреса')]", "Заголовок формы", self.page)
        self.ADDRESS_TYPE_FIELD = Element("#place-add_placeType", "Поле ввода 'Тип адреса'", self.page)
        self.ADDRESS_TYPE_OPTIONS = ElementsList(".ant-select-item-option", "Выбор 'Тип адреса'", self.page)
        self.ADDRESS_INPUT = Element("#place-add_addressString", "Поле ввода 'Адреса'", self.page)
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
    CLIENT = "#inquiry-create-form p:nth-child(2)"
    SELECT_CLIENT_BTN = "#inquiry-create-form button:has(.platform-button__icon_right)"
    CODE = "#code"
    TOPIC = "#topic"
    EMAIL = "#email"
    PHONE = "#phone"
    DESCRIPTION = "#description"
    FILE_INPUT = "input[type='file']"
    PRIORITY = "#priority"


class ClientChoice(DynamicForms):
    """Форма 'Выбор клиента'."""
    RESET_BTN = "#resetButton"
    FIND_BTN = "#findButton"

    FOUNDED_CUSTOMER = ".ant-table-tbody tr:nth-child({client_num})"

    #FOUNDED_CUSTOMER
    FOUNDED_FIO = ".ant-table-tbody tr:nth-child({client_num}) td:nth-child(1)"
    FOUNDED_CUSTOMER_TYPE = ".ant-table-tbody tr:nth-child({client_num}) td:nth-child(2)"
    FOUNDED_CUSTOMER_STATUS = ".ant-table-tbody tr:nth-child({client_num}) td:nth-child(3)"
    FOUNDED_DOCUMENT_NUM = ".ant-table-tbody tr:nth-child({client_num}) td:nth-child(4)"
    FOUNDED_CONTRACT = ".ant-table-tbody tr:nth-child({client_num}) td:nth-child(5)"


class CreateSalesAndServiceManagement(DynamicForms):
    """Форма 'Создание продажи и управления услугами'"""
    CONTACT_PERSON = "#inqrLinkedPerson"
    EMAIL = ".ant-col:has([for='email']) input"
    PHONE = ".ant-col:has([for='phone']) input"
    SELECTED_SALE = "#saleAgreement"
    ADD_SALE_TYPE = "#saleAddAgreement"
    DESCRIPTION = "#description"
    FILE_INPUT = "input[type='file']"
    PRIORITY = "#priority"
    END_DATE = ".ant-form-item:has(label[|title='Планируемая дата окончания'],[|title='Планируемая дата окончания']) .ant-form-item-control-input-content"


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
