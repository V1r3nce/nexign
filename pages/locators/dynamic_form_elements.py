import datetime

from playwright.sync_api import Page

from common.helpers.data_generator import faker_ru, generate_random_number, get_shifted_datetime
from models.address_info import BasicSystemAddress
from pages.ui_elements import Element, ElementsList, Select, Autocomplete, DatePicker, Dropdown
from pages.locators.base_elements import BaseElements
import allure


class DynamicElements(BaseElements):
    """На разных страницах/формах присутствуют элементы идентичные по бизнес логике.
    Например, как номер телефона. Он может присутствовать и при создании карточки клиента,
    редактировании, просмотре и т.д. аттрибут id отличается только префиксом. По этому такие элементы,
    имеют универсальный селектор для их нахождения."""

    def __init__(self, page: Page = None):
        super().__init__(page)
        self.ACCOUNT_NUM = Element("input[id*='accountNumber']", "Номер ЛС", self.page)
        self.SUBSCRIPTION_ID = "input[id*='subscriptionIdentification']"
        self.CONTRACT_NUM = Element("input[id*='agreementNumber']", "Номер договора", self.page)
        self.INN = Element("input[id*='create_taxIdentificationNumber']", "ИНН", self.page)
        self.KPP = Element("input[id*='registrationReasonCode']", "КПП", self.page)
        self.SNILS = Element("input[id*='create_INILA']", "СНИЛС", self.page)
        self.CUSTOMER_TYPE = "input[id*='customerTypes']"
        self.CUSTOMER_NAME = Element("input[id*='create_customerName']", "Имя клиента", self.page)
        self.ID_DOCUMENT_SERIAL = "input[id*='identificationDocumentSeries']"
        self.ID_DOCUMENT_NUM = "input[id*='identificationDocumentNumber']"
        self.DOCUMENT_SERIAL = Element("input[id*='documentSeries']", "Серия документа", self.page)
        self.DOCUMENT_NUM = Element("input[id*='documentNumber']", "Номер документа", self.page)
        self.NATIONALITY = Select("input[id*='nationality']", "Страна регистрации", self.page)
        self.SPEAKING_LANGUAGE = Select("input[id*='speakingLanguage']", "Язык общения", self.page)
        self.RESIDENT = Element("input[id*='isResident']", "Резидент", self.page)
        self.BUSINESS_ACTIVITY = Select("input[id*='businessActivity']", "Экономическая деятельность", self.page)
        self.NOTE = Element("[id*='create_note']", "Комментарий", self.page)
        self.REGISTRATION_ADDRESS = Autocomplete("input[id*='registrationAddress']", "Адрес регистрации", self.page)
        self.REPUTATION = Element("input[id*='reputation']", "Деловая репутация", self.page)
        self.OKPO = Element("input[id*='RNNBO']", "ОКПО", self.page)
        self.OKATO = Element("input[id*='ARCPS']", "ОКАТО", self.page)
        self.OKVED = Element("input[id*='economicActivities']", "ОКВЭД", self.page)
        self.OGRN = Element("input[id$='create_PSRN']", "ОГРН", self.page)
        self.PUBLIC_PERSON_CHECKBOX = Element("input[id*='publicOfficial']", "Публичное лицо", self.page)
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
        self.OPERATOR_BANK_DETAILS = Select("input[id*='create_bankOperator']",
                                            "Поле оператора 'Банк и расчетный счет",
                                            self.page)
        self.CLIENT_BANK_DETAILS_CHBX = Element("//*[@id='agreement-card-create_useExistingBankData']",
                                                "Чек-бокс 'Банковские реквизиты клиента'",
                                                self.page)
        self.CLIENT_BANK_CURRENT_ACCOUNT = Element("input[id*='create_bankAccountNumber']", "Расчетный счет клиента",
                                                   self.page)
        self.CLIENT_BANK = Select("#agreement-card-create_bankAccount", "Банк клиента", self.page)
        self.CREATE_BTN = Element("#create",
                                  "Кнопка 'Создать", self.page)
        self.DEADLINE = Select("#CF_DEDLINE", "Планируемый срок решения", self.page)

        self.REGISTRATION_DOCUMENT = Element("input[id*='PSRNInfo']", "Документ о регистрации", self.page)
        self.REGISTRATION_DATE = DatePicker("input[id*='registrationDate']", "Дата регистрации", self.page)
        self.REGISTRATION_NUM = Element("input[id*='foreignRegistrationNumber']",
                                        "Регистрационный номер в стране регистрации", self.page)
        self.TAX_SCHEME = Select("input[id*='taxScheme']", "Схема налогообложения", self.page)


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


class IndividualCustomerCreate(DynamicForms):
    """Форма 'Создание клиента ФЛ'"""

    def __init__(self, page: Page = None):
        super().__init__(page)

        self.LAST_NAME = Element("#customer-individual-create_surname", "Фамилия", self.page)
        self.FIRST_NAME = Element("#customer-individual-create_firstname", "Имя", self.page)
        self.SUR_NAME = Element("#customer-individual-create_patronymic", "Отчество", self.page)
        self.DOCUMENT_TYPE_DROPDOWN = Element("#customer-individual-create_documentType", "Тип документа", self.page)

        self.CREATE_ADDRESS_LINK = Element("#customer-individual-create_registrationAddress_list", "Добавить адрес",
                                           self.page)

        self.BIOMETRIC_CHECKBOX = Element("#customer-individual-create_biometricData", "Биометрические данные",
                                          self.page)
        self.CONTACT_PHONE = Element("#customer-individual-create_contactPhoneNumber", "Телефон", self.page)
        self.CONTACT_EMAIL = Element("#customer-individual-create_contactEmail", "Почта", self.page)
        self.SAVE_BTN = Element("#customer-individual-create #save", "Сохранить", self.page)

    @allure.step("Заполнить данные клиента ФЛ")
    def fill_data_for_individual_client(self, only_required_fields: bool = False, **kwargs):
        start_date = datetime.date(1990, 1, 1)
        end_date = datetime.date(2020, 12, 31)

        self.LAST_NAME.fill(kwargs.get('last_name') or f'автотесты-{faker_ru.last_name()}')
        self.FIRST_NAME.fill(kwargs.get('first_name') or f'автотесты-{faker_ru.first_name()}')
        self.SUR_NAME.fill(kwargs.get('sur_name') or 'Автотестович')
        self.GENDER.select_by_value(kwargs.get('gender') or 'Мужской')
        self.DOCUMENT_TYPE.select_by_value(kwargs.get('document_type') or 'Паспорт гражданина РФ')
        self.DOCUMENT_SERIAL.fill(kwargs.get('document_serial') or str(generate_random_number(4)))
        self.DOCUMENT_NUM.fill(kwargs.get('document_num') or str(generate_random_number(6)))
        if not  only_required_fields: self.DOCUMENT_PROVIDE_BY.fill(kwargs.get('document_provide_by') or 'ГУ МВД РОССИИ')
        if not  only_required_fields: self.DOCUMENT_DIVISION_CODE.fill(kwargs.get('document_division_code') or f"{generate_random_number(3)}-{generate_random_number(3)}")
        if not  only_required_fields: self.DOCUMENT_DATE.fill(kwargs.get('document_date') or faker_ru.date_between(start_date, end_date).strftime('%d.%m.%Y'))
        if not  only_required_fields: self.DOCUMENT_VALID_DATE.fill(kwargs.get('document_valid_date') or faker_ru.date_between(datetime.datetime.today(),
                                                                   get_shifted_datetime("+500d")).strftime('%d.%m.%Y'))
        self.BIRTH_DATE.fill(kwargs.get('birth_date') or faker_ru.date_of_birth().strftime('%d.%m.%Y'))
        if not  only_required_fields: self.BIRTH_PLACE.fill(kwargs.get('birth_place') or faker_ru.city())
        self.REGISTRATION_ADDRESS.select_by_value(kwargs.get('registration_address') or BasicSystemAddress.address)
        if not  only_required_fields: self.INN.fill(kwargs.get('inn') or str(generate_random_number(12)))
        if not  only_required_fields: self.SNILS.fill(kwargs.get('snils') or str(generate_random_number(11)))
        if not  only_required_fields: self.CONTACT_PHONE.fill(kwargs.get('contact_phone') or faker_ru.phone_number())
        if not  only_required_fields: self.CONTACT_EMAIL.fill(kwargs.get('contact_email') or faker_ru.email())
        self.TAX_SCHEME.select_by_value(kwargs.get('tax_scheme') or 'Схема налогообложения по умолчанию')

class CreateEntrepreneur(IndividualCustomerCreate):
    """Форма 'Создание клиента ИП'"""

    def __init__(self, page: Page = None):
        super().__init__(page)
        self.PROPRIETARY_FORM = Select("#customer-entrepreneur-create_proprietaryForm", "Организационно-правовая форма",
                                       self.page)

        self.PROPRIETARY_FORM_TYPE = 'ИП, Индивидуальный предприниматель'

        self.LAST_NAME = Element("#customer-entrepreneur-create_surname", "Фамилия", self.page)
        self.FIRST_NAME = Element("#customer-entrepreneur-create_firstname", "Имя", self.page)
        self.SUR_NAME = Element("#customer-entrepreneur-create_patronymic", "Отчество", self.page)
        self.DOCUMENT_TYPE_DROPDOWN = Element("#customer-entrepreneur-create_documentType", "Тип документа", self.page)

        self.CREATE_ADDRESS_LINK = Element("#customer-entrepreneur-create_registrationAddress_list", "Добавить адрес",
                                           self.page)

        self.BIOMETRIC_CHECKBOX = Element("#customer-entrepreneur-create_biometricData", "Биометрические данные",
                                          self.page)
        self.CONTACT_PHONE = Element("#customer-entrepreneur-create_contactPhoneNumber", "Телефон", self.page)
        self.CONTACT_EMAIL = Element("#customer-entrepreneur-create_contactEmail", "Почта", self.page)

        self.SAVE_BTN = Element("#customer-entrepreneur-create #save", "Сохранить", self.page)

    @allure.step("Заполнить данные клиента ИП")
    def fill_data_for_entrepreneur_client(self, only_required_fields: bool = False, **kwargs):
        start_date = datetime.date(1990, 1, 1)
        end_date = datetime.date(2020, 12, 31)

        if not only_required_fields: self.PROPRIETARY_FORM.select_by_value(kwargs.get('proprietary_form') or self.PROPRIETARY_FORM_TYPE)
        if not only_required_fields: self.REGISTRATION_DOCUMENT.fill(kwargs.get('registration_document') or str(generate_random_number(10)))
        if not only_required_fields: self.REGISTRATION_DATE.fill(
            kwargs.get('registration_date') or faker_ru.date_between(start_date, end_date).strftime('%d.%m.%Y'))
        if not only_required_fields: self.SNILS.fill(kwargs.get('snils') or str(generate_random_number(11)))
        if not only_required_fields: self.OKPO.fill(kwargs.get('okpo') or str(generate_random_number(10)))
        if not only_required_fields: self.OKATO.fill(kwargs.get('okato') or str(generate_random_number(10)))
        if not only_required_fields: self.OKVED.fill(kwargs.get('okved') or str(generate_random_number(10)))
        if not only_required_fields: self.OGRN.fill(kwargs.get('ogrn') or str(generate_random_number(15)))
        self.INN.fill(kwargs.get('inn') or str(generate_random_number(12)))
        self.LAST_NAME.fill(kwargs.get('last_name') or f'автотесты-{faker_ru.last_name()}')
        self.FIRST_NAME.fill(kwargs.get('first_name') or f'автотесты-{faker_ru.first_name()}')
        if not only_required_fields: self.SUR_NAME.fill(kwargs.get('sur_name') or 'Автотестович')
        self.GENDER.select_by_value(kwargs.get('gender') or 'Мужской')
        self.DOCUMENT_TYPE.select_by_value(kwargs.get('document_type') or 'Паспорт гражданина РФ')
        if not only_required_fields: self.DOCUMENT_SERIAL.fill(kwargs.get('document_serial') or str(generate_random_number(4)))
        self.DOCUMENT_NUM.fill(kwargs.get('document_num') or str(generate_random_number(6)))
        if not only_required_fields: self.DOCUMENT_PROVIDE_BY.fill(kwargs.get('document_provide_by') or 'ГУ МВД РОССИИ')
        if not only_required_fields: self.DOCUMENT_DIVISION_CODE.fill(
            kwargs.get('document_division_code') or f"{generate_random_number(3)}-{generate_random_number(3)}")
        if not only_required_fields: self.DOCUMENT_DATE.fill(
            kwargs.get('document_date') or faker_ru.date_between(start_date, end_date).strftime('%d.%m.%Y'))
        if not only_required_fields: self.DOCUMENT_VALID_DATE.fill(
            kwargs.get('document_valid_date') or faker_ru.date_between(datetime.datetime.today(),
                                                                       get_shifted_datetime("+500d")).strftime(
                '%d.%m.%Y'))
        if not only_required_fields: self.BIRTH_PLACE.fill(kwargs.get('birth_place') or faker_ru.city())
        self.BIRTH_DATE.fill(kwargs.get('birth_date') or faker_ru.date_of_birth().strftime('%d.%m.%Y'))
        self.NATIONALITY.select_by_value(kwargs.get('nationality') or 'Россия')
        self.SPEAKING_LANGUAGE.select_by_value(kwargs.get('speaking_language') or 'Русский')
        self.REGISTRATION_ADDRESS.select_by_value(kwargs.get('registration_address') or BasicSystemAddress.address)
        if not only_required_fields: self.REPUTATION.fill(kwargs.get('reputation') or "Автотестовая репутация")
        self.PUBLIC_PERSON_CHECKBOX.click()
        if not only_required_fields: self.CONTACT_PHONE.fill(kwargs.get('contact_phone') or faker_ru.phone_number())
        if not only_required_fields: self.CONTACT_EMAIL.fill(kwargs.get('contact_email') or faker_ru.email())
        if not only_required_fields: self.BUSINESS_ACTIVITY.select_by_value(kwargs.get('business_activity') or 'Агент')
        if not only_required_fields: self.NOTE.fill(kwargs.get('note') or str(generate_random_number(10)))
        self.TAX_SCHEME.select_by_value(kwargs.get('tax_scheme') or 'Схема налогообложения по умолчанию')


class CreateOrganization(DynamicForms):
    """Форма 'Создание клиента' ЮЛ."""

    def __init__(self, page: Page = None):
        super().__init__(page)
        self.PROPRIETARY_FORM = Select("#customer-organization-create_proprietaryForm", "Организационно-правовая форма",
                                       self.page)
        self.PROPRIETARY_FORM_TYPE = 'АО, Акционерное Общество'
        self.CLIENT_NAME = Element("input[id*='_customerName']", "Имя Клиента", self.page)
        self.TAX_SCHEME = Select("input[id*='taxScheme']", "Схема налогооблажения", self.page)
        self.SAVE_BTN = Element("#customer-organization-create #save", "Сохранить", self.page)
    @allure.step("Заполнить данные клиента ЮЛ")
    def fill_data_for_organization_client(self, only_required_fields: bool = False, **kwargs):
        start_date = datetime.date(1990, 1, 1)
        end_date = datetime.date(2020, 12, 31)

        if not only_required_fields: self.INN.fill(kwargs.get('inn') or str(generate_random_number(10)))
        if not only_required_fields: self.PROPRIETARY_FORM.select_by_value(kwargs.get('proprietary_form') or self.PROPRIETARY_FORM_TYPE)
        self.CUSTOMER_NAME.fill(kwargs.get('customer_name') or f"Autotest_{faker_ru.pystr(min_chars=10, max_chars=10)}")
        if not only_required_fields: self.REGISTRATION_DOCUMENT.fill(kwargs.get('registration_document') or str(generate_random_number(10)))
        if not only_required_fields: self.REGISTRATION_DATE.fill(
            kwargs.get('registration_date') or faker_ru.date_between(start_date, end_date).strftime('%d.%m.%Y'))
        if not only_required_fields: self.REGISTRATION_NUM.fill(kwargs.get('registration_num') or str(generate_random_number(6)))
        if not only_required_fields: self.OKPO.fill(kwargs.get('okpo') or str(generate_random_number(10)))
        if not only_required_fields: self.OKATO.fill(kwargs.get('okato') or str(generate_random_number(10)))
        if not only_required_fields: self.OKVED.fill(kwargs.get('okved') or str(generate_random_number(10)))
        if not only_required_fields: self.OGRN.fill(kwargs.get('ogrn') or str(generate_random_number(13)))
        if not only_required_fields: self.KPP.fill(kwargs.get('kpp') or str(generate_random_number(9)))
        self.NATIONALITY.select_by_value(kwargs.get('nationality') or 'Россия')
        self.SPEAKING_LANGUAGE.select_by_value(kwargs.get('speaking_language') or 'Русский')
        if not only_required_fields: self.BUSINESS_ACTIVITY.select_by_value(kwargs.get('business_activity') or 'Агент')
        if not only_required_fields: self.NOTE.fill(kwargs.get('note') or str(generate_random_number(10)))
        self.REGISTRATION_ADDRESS.select_by_value(kwargs.get('registration_address') or BasicSystemAddress.address)
        if not only_required_fields: self.REPUTATION.fill(kwargs.get('reputation') or "Автотестовая репутация")
        self.TAX_SCHEME.select_by_value(kwargs.get('tax_scheme') or 'Схема налогообложения по умолчанию')


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
        self.ATTRIBUTE_HEADER = ElementsList("[id*='create-address-form'] .ant-collapse-item",
                                             "Панель с кнопкой 'Атрибуты'", self.page)
        self.ATTRIBUTE_FIELDS_BLOCK = ElementsList(".ant-collapse-content .ant-form-item-control-input-content",
                                                   "Блок полей атрибутов", self.page)
        self.ATTRIBUTE_FIELDS = ElementsList(".ant-collapse-content .ant-form-item-control-input-content input",
                                             "Поля атрибутов", self.page)

        self.OPTION_ITEMS = ElementsList("[id*='create-address-form'] .ant-select-item-option",
                                         "Варианты выбора в списке", self.page)
        self.OBJECT_TYPE = Select("[id*='_select-elementCode']", "Поле 'Выберите адресный объект'", self.page)
        self.OBJECT_NAME_AUTOCOMPLETE = Autocomplete(".ant-row.ant-form-item-row:has(label[title='Наименование']) "
                                                     "input[id*='rc_select']", "Поле 'Наименование'", self.page)
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
        self.ADDITIONAL_HOUSE_TYPE_DROPDOWN = Autocomplete("input[id*='house_additionalType']",
                                                           "Поле ввода 'Дополнительный тип дома'", self.page)
        self.EXTRA_HOUSE_TYPE_DROPDOWN = Autocomplete("input[id*='house_extraType']",
                                                      "Поле ввода 'Добавочный тип дома'", self.page)
        self.APPLY_BTN = Element("[id*='save-button']",
                                 "Кнопка 'Применить'", self.page)
        self.ADD_ADDRESS_OBJECT_BTN = Element("[id*='add-address-element-button']",
                                              "Кнопка 'Добавить адресный объект'", self.page)
        self.CREATE_BTN = Element("[id*='create-address-modal_accept-button']", "Кнопка 'Создать'",
                                  self.page)
        self.CANCEL_BTN = Element("[id*='create-address-modal_cancel-button']", "Кнопка 'Отмена'",
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
                                           "Варианты адреса", self.page)
        self.SAVE_BTN = Element("#save", "Кнопка 'Добавить'", self.page)
        self.CANCEL_BTN = Element("#cancel", "Кнопка 'Отмена'", self.page)


class EditAddress(DynamicForms):
    """Форма 'Редактирование адреса Клиента'"""

    def __init__(self, page: Page):
        super().__init__(page)

        self.TITLE = Element("//h3[contains(text(), 'Редактирование адреса')]", "Заголовок формы", self.page)
        self.ADDRESS_INPUT = Element("#place-edit_addressString", "Поле ввода 'Адреса'", self.page)
        self.ADD_ADDRESS_TO_CATALOG = Element("a[href='/rm-ui/allundefined']",
                                              "Ссылка 'Добавить адрес в справочник'", self.page)
        self.MAPS_LINK_INPUT = Element("#place-edit_addressUrl", "Поле ввода 'Ссылка на карту'", self.page)
        self.ADDRESS_OPTION = ElementsList("#addressString_control .ant-select-item-option-content",
                                           "Варианты адреса", self.page)


class EditAddressInfo(DynamicForms):
    """Форма 'Редактирование адресной информации'"""

    def __init__(self, page: Page):
        super().__init__(page)

        self.ADD_BUTTON = Element("button[title='Добавить']", "Кнопка 'Добавить'", self.page)
        self.TABLE_LINE = ElementsList("//tr", "Строки таблицы", self.page)
        self.TABLE_ADDRESS_TYPES = ElementsList("//tr/td[1]", "Строки Тип адреса", self.page)
        self.TABLE_ADDRESSES = ElementsList("//tr/td[2]", "Строки Адреса", self.page)
        self.TABLE_MAP_CELLS = ElementsList("//tr/td[3]", "Строки под кнопку карты", self.page)
        self.TABLE_LINE_MAP_BUTTON = ElementsList("td svg", "Строки таблицы кнопка карты", self.page)
        self.CANCEL_BTN = Element("#_cancel-button", "Кнопка 'Закрыть'", self.page)
        self.TYPE_SORT_BTN = Element("//span[contains(text(), 'Тип')]/parent::div[contains(@class, 'sorters')]",
                                     "Кнопка сортировки 'Тип'", self.page)
        self.EDIT_ADDRESS = Element("button[|title='Изменить адрес'],[|title='Edit address']",
                                    "Кнопка 'Изменить адрес'", self.page)
        self.DELETE_ADDRESS = Element("button[|title='Удалить адрес'],[|title='Delete address']",
                                      "Кнопка 'Удалить адрес'", self.page)
        self.SETTING_BTN = Element("button.ant-dropdown-trigger", "Кнопка 'Настройка колонок'", self.page)
        self.SETTING_OPTIONS = ElementsList("input.ant-checkbox-input", "Чекбоксы 'Настройка колонок'", self.page)


class RequestCreate(DynamicForms):
    """Форма 'Создание заявки'."""

    def __init__(self, page: Page):
        super().__init__(page)

        self.CLIENT = Element("#inquiry-create-form a", "Выбранный клиент", self.page)
        self.SELECT_CLIENT_BTN = Dropdown("#inquiry-create-form button:has(.platform-button__icon_right)",
                                          "Сменить клиента", self.page)
        self.CHOOSE_AGREEMENT_BTN = Select("input[id*='saleAddAgreement']", "Поле создание договора",
                                           self.page)
        self.CHOOSE_PRIORITY_BTN = Select("input[id*='priority']", "Поле выбора приоритета",
                                          self.page)


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

        self.ACCOUNT_NUM = Element("#search-customer_accountNumber", "Номер ЛС", self.page)
        self.SUBSCRIPTION_ID = Element("#search-customer_subscriptionIdentification", "Абонент", self.page)
        self.CONTRACT_NUM = Element("#search-customer_agreementNumber", "Номер договора", self.page)
        self.KPP = Element("#search-customer_registrationReasonCode", "КПП", self.page)
        self.INN = Element("#search-customer_taxIdentificationNumber", "ИНН", self.page)
        self.CUSTOMER_NAME = Element("#search-customer_customerName", "Наименование клиента", self.page)
        self.RESET_BTN = Element("#resetButton", "Кнопка 'Сбросить'", self.page)
        self.FIND_BTN = Element("#findButton", "Кнопка 'Найти'", self.page)

        self.FOUNDED_CUSTOMER = ElementsList("#search-customer-table .ant-table-tbody tr", "Клиенты", self.page)

        # FOUNDED_CUSTOMER
        self.FOUNDED_FIO = ElementsList("#search-customer-table .ant-table-tbody tr td:nth-child(1)", "ФИО клиента",
                                        self.page)
        self.FOUNDED_CUSTOMER_TYPE = ElementsList("#search-customer-table .ant-table-tbody tr td:nth-child(2)",
                                                  "Тип клиента", self.page)
        self.FOUNDED_CUSTOMER_STATUS = ElementsList("#search-customer-table .ant-table-tbody tr td:nth-child(3)",
                                                    "Статус клиента", self.page)
        self.FOUNDED_DOCUMENT_NUM = ElementsList("#search-customer-table .ant-table-tbody tr td:nth-child(4)",
                                                 "Номер документа", self.page)
        self.FOUNDED_CONTRACT = ElementsList("#search-customer-table .ant-table-tbody tr td:nth-child(5)", "Договор",
                                             self.page)


class CreateSalesAndServiceManagement(RequestCreate):
    """Форма 'Создание продажи и управления услугами'"""

    def __init__(self, page: Page):
        super().__init__(page)

        self.CONTACT_PERSON = Element("#inqrLinkedPerson", "Контактное лицо", self.page)
        self.EMAIL = Element(".ant-col:has([for='email']) input", "Предпочтительный email", self.page)
        self.PHONE = Element(".ant-col:has([for='phone']) input", "Предпочтительный телефон", self.page)
        self.SELECTED_SALE = Element("#saleAgreement", "Договор", self.page)
        self.ADD_SALE_TYPE = Select("#saleAddAgreement", "Создание Договора", self.page)
        self.DESCRIPTION = Element("#description", "Описание", self.page)
        self.FILE_INPUT = Element("input[type='file']", "Документы", self.page)
        self.END_DATE = Element(
            ".ant-form-item:has(label[|title='Планируемая дата окончания'],[|title='Планируемая дата окончания']) "
            ".ant-form-item-control-input-content", "Планируемая дата окончания", self.page)
        self.SAVE_BTN = Element("#inquiry-create-form #save", "Кнопка 'Сохранить'", self.page)

class EditDynamicElements(BaseElements):
    """Динамические элементы в редактировании.
    (Отличается от класса DynamicElements,
    только префиксом edit_ в id элемента)."""

    def __init__(self, page: Page):
        super().__init__(page)

        self.CREATE_BTN = Element("#place-edit_addressString_create-address-modal_accept-button", "Кнопка 'Создать'",
                                  self.page)
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


class AddRelatedPersonForms(DynamicForms):
    """Форма 'Добавление связанного лица'"""
    def __init__(self, page: Page):
        super().__init__(page)
        self.ADD_NEW_RELATED_PERSON_BTN = Element(".ant-drawer-body .platform-button__icon_left",
                                                  "Кнопка 'Добавить' новое связанное лицо",
                                                  self.page)
        self.TYPE_RELATED_PERSON = Select("input[id*='rc_select_']", "Поле выбора типа связанного лица",
                                          self.page)
        self.NAME_RELATED_PERSON = Element("input[id='impersonalName']", "Поле 'Наименование связанного лица'",
                                           self.page)
        self.FUNCTION_RELATED_PERSON = Select("input[id*='rc_select_']", "Поле выбора функции связанного лица",
                                              self.page)
        self.NEXT_BTN = Element(".ant-drawer-footer .platform-button__icon_right", "Кнопка 'Далее'",
                                self.page)
        self.ADD_BTN = Element(".ant-drawer-footer button[variant='primary']", "Кнопка 'Добавить'",
                               self.page)
        self.ADD_EMAIL_BTN = Element('//*[@id="root"]/div/div[6]/div/div[3]/div/div/div[2]/div/form/div[4]/button', "Кнопка 'Добавить эл. почту'",
                                     self.page)
        self.ADD_EMAIL_FORM = Element("input[id*='contactEmail_0_email']", "Поле ввода Email",
                                      self.page)

    @allure.step("Заполнить данные связанного лица")
    def fill_data_for_related_person(self, **kwargs):
        self.ADD_NEW_RELATED_PERSON_BTN.click()
        self.TYPE_RELATED_PERSON.select_by_value(kwargs.get('type_related_person') or 'Обезличенное')
        self.NAME_RELATED_PERSON.fill(kwargs.get('name_related_person') or 'Тестовое наименование')
        self.NEXT_BTN.click()
        self.FUNCTION_RELATED_PERSON.select_by_value(kwargs.get('function') or 'Выгодоприобретатель')
        self.NEXT_BTN.click()
        self.ADD_EMAIL_BTN.click()
        self.ADD_EMAIL_FORM.fill(kwargs.get('email') or 'test@mail.ru')
        self.ADD_BTN.click()


class ProductOffer(DynamicForms):
    """Форма 'Выбор продуктовых предложений'"""
    def __init__(self, page: Page):
        super().__init__(page)

        self.TYPE_PACKAGE_OFFER = Element("#productType > div > :nth-child(1)", "Тип 'Пакетное предложение'",
                              self.page)
        self.TYPE_MONO_PRODUCT = Element("#productType > div > :nth-child(2)", "Тип 'Монопродукт'",
                              self.page)
        self.CATEGORY_BLOCK = Element("#productOfferingCategoryCodes > div > :nth-child(1)", "Категория 'Блокировка'",
                                 self.page)
        self.CATEGORY_ETHERNET = Element("#productOfferingCategoryCodes > div > :nth-child(2)", "Категория 'Интернет'",
                                 self.page)
        self.CATEGORY_MOBILE = Element("#productOfferingCategoryCodes > div > :nth-child(3)", "Категория 'Мобильная связь'",
                                 self.page)
        self.CATEGORY_EQUIPMENT = Element("#productOfferingCategoryCodes > div > :nth-child(4)", "Категория 'Оборудование'",
                                 self.page)
        self.CATEGORY_LANDLINE_TELEPHONE = Element("#productOfferingCategoryCodes > div > :nth-child(5)", "Категория 'Стационарная телефония'",
                                 self.page)
        self.CATEGORY_TECHNICAL_SERVICES = Element("#productOfferingCategoryCodes > div > :nth-child(6)", "Категория 'Технические услуги'",
                                 self.page)
        self.CATEGORY_GOODS = Element("#productOfferingCategoryCodes > div > :nth-child(7)", "Категория 'Товары'",
                                 self.page)
        self.CATEGORY_SPECIALIST_SERVICES = Element("#productOfferingCategoryCodes > div > :nth-child(8)", "Категория 'Услуги специалиста'",
                                 self.page)
        self.FOUND_BTN = Element('.ant-form-vertical > :nth-child(5) > :nth-child(1)',
                                 "Кнопка 'Найти'",
                                 self.page)
        self.CHOOSE_PACKAGE_BTN = Element('.ant-spin-container > div > :nth-child(1) > :nth-child(2) > :nth-child(2) > :nth-child(3)',
                                "Кнопка 'Выбрать'",
                                self.page)
        self.CHOOSE_MONO_BTN = Element(
            "(//div[contains(@class, 'platform-button')])[16]",
            "Кнопка 'Выбрать'",
            self.page)
        self.ADD_BTN = Element("[id='_accept-button']",
                                "Кнопка 'Добавить'",
                                self.page)




class EditCustomerAttributes(EditDynamicElements):
    pass
