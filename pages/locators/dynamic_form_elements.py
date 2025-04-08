import datetime
import re
from typing import Any

import allure
from playwright.sync_api import Page

from common.helpers.data_generator import faker_ru, generate_random_number, get_shifted_datetime
from models.address_info import BasicSystemAddress
from pages.locators.base_elements import BaseElements
from pages.ui_elements import Autocomplete, DatePicker, Dropdown, Element, ElementsList, Select


class DynamicElements(BaseElements):
    """На разных страницах/формах присутствуют элементы идентичные по бизнес логике.
    Например, как номер телефона. Он может присутствовать и при создании карточки клиента,
    редактировании, просмотре и т.д. аттрибут id отличается только префиксом. По этому такие элементы,
    имеют универсальный селектор для их нахождения."""

    def __init__(self, page: Page = None):
        super().__init__(page)
        self.SAVE_BTN = Element("#save", "Сохранить", self.page)

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
        self.REGISTRATION_ADDRESS_CROSS = Element(
            "//input[contains(@id, 'registrationAddress')]/parent::span/span/span",
            "Кнопка очистки 'Адрес регистрации'",
            self.page,
        )
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
        self.OPERATOR_BANK_DETAILS = Select(
            "input[id*='create_bankOperator']", "Поле оператора 'Банк и расчетный счет", self.page
        )
        self.CLIENT_BANK_DETAILS_CHBX = Element(
            "//*[@id='agreement-card-create_useExistingBankData']", "Чек-бокс 'Банковские реквизиты клиента'", self.page
        )
        self.CLIENT_BANK_CURRENT_ACCOUNT = Element(
            "input[id*='create_bankAccountNumber']", "Расчетный счет клиента", self.page
        )
        self.CLIENT_BANK = Select("#agreement-card-create_bankAccount", "Банк клиента", self.page)
        self.CREATE_BTN = Element("#create", "Кнопка 'Создать", self.page)
        self.DEADLINE = Select("#CF_DEDLINE", "Планируемый срок решения", self.page)

        self.REGISTRATION_DOCUMENT = Element("input[id*='PSRNInfo']", "Документ о регистрации", self.page)
        self.REGISTRATION_DATE = DatePicker("input[id*='registrationDate']", "Дата регистрации", self.page)
        self.REGISTRATION_NUM = Element(
            "input[id*='foreignRegistrationNumber']", "Регистрационный номер в стране регистрации", self.page
        )
        self.TAX_SCHEME = Select("input[id*='taxScheme']", "Схема налогообложения", self.page)


class DynamicForms(DynamicElements):
    def __init__(self, page: Page):
        super().__init__(page)
        """Общие элементы динамических форм."""
        self.TITLE = Element(".ant-drawer-title h3", "Заголовок формы", self.page)
        self.CROSS_BTN = Element(".ant-drawer-open  button[aria-label='Close']", "Крестик", self.page)
        self.CANCEL_BTN = Element("#cancel", "Отменить", self.page)
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

        self.CREATE_ADDRESS_LINK = Element(
            "#customer-individual-create_registrationAddress_list", "Добавить адрес", self.page
        )

        self.BIOMETRIC_CHECKBOX = Element(
            "#customer-individual-create_biometricData", "Биометрические данные", self.page
        )
        self.CONTACT_PHONE = Element("#customer-individual-create_contactPhoneNumber", "Телефон", self.page)
        self.CONTACT_EMAIL = Element("#customer-individual-create_contactEmail", "Почта", self.page)
        self.SAVE_BTN = Element("#customer-individual-create #save", "Сохранить", self.page)

    @allure.step("Заполнить данные клиента ФЛ")
    def fill_data_for_individual_client(self, only_required_fields: bool = False, **kwargs: Any) -> None:
        start_date = datetime.date(1990, 1, 1)
        end_date = datetime.date(2020, 12, 31)

        self.LAST_NAME.fill(kwargs.get("last_name") or f"автотесты-{faker_ru.last_name()}")
        self.FIRST_NAME.fill(kwargs.get("first_name") or f"автотесты-{faker_ru.first_name()}")
        self.SUR_NAME.fill(kwargs.get("sur_name") or "Автотестович")
        self.GENDER.select_by_value(kwargs.get("gender") or "Мужской")
        self.DOCUMENT_TYPE.select_by_value(kwargs.get("document_type") or "Паспорт гражданина РФ")
        self.DOCUMENT_SERIAL.fill(kwargs.get("document_serial") or str(generate_random_number(4)))
        self.DOCUMENT_NUM.fill(kwargs.get("document_num") or str(generate_random_number(6)))
        if not only_required_fields:
            self.DOCUMENT_PROVIDE_BY.fill(kwargs.get("document_provide_by") or "ГУ МВД РОССИИ")
        if not only_required_fields:
            self.DOCUMENT_DIVISION_CODE.fill(
                kwargs.get("document_division_code") or f"{generate_random_number(3)}-{generate_random_number(3)}"
            )
        if not only_required_fields:
            self.DOCUMENT_DATE.fill(
                kwargs.get("document_date") or faker_ru.date_between(start_date, end_date).strftime("%d.%m.%Y")
            )
        if not only_required_fields:
            self.DOCUMENT_VALID_DATE.fill(
                kwargs.get("document_valid_date")
                or faker_ru.date_between(datetime.datetime.today(), get_shifted_datetime("+500d")).strftime("%d.%m.%Y")
            )
        self.BIRTH_DATE.fill(kwargs.get("birth_date") or faker_ru.date_of_birth().strftime("%d.%m.%Y"))
        if not only_required_fields:
            self.BIRTH_PLACE.fill(kwargs.get("birth_place") or faker_ru.city())
        self.REGISTRATION_ADDRESS.select_by_value(kwargs.get("registration_address") or BasicSystemAddress.address)
        if not only_required_fields:
            self.INN.fill(kwargs.get("inn") or str(generate_random_number(12)))
        if not only_required_fields:
            self.SNILS.fill(kwargs.get("snils") or str(generate_random_number(11)))
        if not only_required_fields:
            self.CONTACT_PHONE.fill(kwargs.get("contact_phone") or faker_ru.phone_number())
        if not only_required_fields:
            self.CONTACT_EMAIL.fill(kwargs.get("contact_email") or faker_ru.email())
        self.TAX_SCHEME.select_by_value(kwargs.get("tax_scheme") or "Схема налогообложения по умолчанию")


class CreateEntrepreneur(IndividualCustomerCreate):
    """Форма 'Создание клиента ИП'"""

    def __init__(self, page: Page = None):
        super().__init__(page)
        self.PROPRIETARY_FORM = Select(
            "#customer-entrepreneur-create_proprietaryForm", "Организационно-правовая форма", self.page
        )

        self.PROPRIETARY_FORM_TYPE = "ИП, Индивидуальный предприниматель"

        self.LAST_NAME = Element("#customer-entrepreneur-create_surname", "Фамилия", self.page)
        self.FIRST_NAME = Element("#customer-entrepreneur-create_firstname", "Имя", self.page)
        self.SUR_NAME = Element("#customer-entrepreneur-create_patronymic", "Отчество", self.page)
        self.DOCUMENT_TYPE_DROPDOWN = Element("#customer-entrepreneur-create_documentType", "Тип документа", self.page)

        self.CREATE_ADDRESS_LINK = Element(
            "#customer-entrepreneur-create_registrationAddress_list", "Добавить адрес", self.page
        )

        self.BIOMETRIC_CHECKBOX = Element(
            "#customer-entrepreneur-create_biometricData", "Биометрические данные", self.page
        )
        self.CONTACT_PHONE = Element("#customer-entrepreneur-create_contactPhoneNumber", "Телефон", self.page)
        self.CONTACT_EMAIL = Element("#customer-entrepreneur-create_contactEmail", "Почта", self.page)

        self.SAVE_BTN = Element("#customer-entrepreneur-create #save", "Сохранить", self.page)

    @allure.step("Заполнить данные клиента ИП")
    def fill_data_for_entrepreneur_client(self, only_required_fields: bool = False, **kwargs: Any) -> None:
        start_date = datetime.date(1990, 1, 1)
        end_date = datetime.date(2020, 12, 31)

        if not only_required_fields:
            self.PROPRIETARY_FORM.select_by_value(kwargs.get("proprietary_form") or self.PROPRIETARY_FORM_TYPE)
        if not only_required_fields:
            self.REGISTRATION_DOCUMENT.fill(kwargs.get("registration_document") or str(generate_random_number(10)))
        if not only_required_fields:
            self.REGISTRATION_DATE.fill(
                kwargs.get("registration_date") or faker_ru.date_between(start_date, end_date).strftime("%d.%m.%Y")
            )
        if not only_required_fields:
            self.SNILS.fill(kwargs.get("snils") or str(generate_random_number(11)))
        if not only_required_fields:
            self.OKPO.fill(kwargs.get("okpo") or str(generate_random_number(10)))
        if not only_required_fields:
            self.OKATO.fill(kwargs.get("okato") or str(generate_random_number(10)))
        if not only_required_fields:
            self.OKVED.fill(kwargs.get("okved") or str(generate_random_number(10)))
        if not only_required_fields:
            self.OGRN.fill(kwargs.get("ogrn") or str(generate_random_number(15)))
        self.INN.fill(kwargs.get("inn") or str(generate_random_number(12)))
        self.LAST_NAME.fill(kwargs.get("last_name") or f"автотесты-{faker_ru.last_name()}")
        self.FIRST_NAME.fill(kwargs.get("first_name") or f"автотесты-{faker_ru.first_name()}")
        if not only_required_fields:
            self.SUR_NAME.fill(kwargs.get("sur_name") or "Автотестович")
        self.GENDER.select_by_value(kwargs.get("gender") or "Мужской")
        self.DOCUMENT_TYPE.select_by_value(kwargs.get("document_type") or "Паспорт гражданина РФ")
        if not only_required_fields:
            self.DOCUMENT_SERIAL.fill(kwargs.get("document_serial") or str(generate_random_number(4)))
        self.DOCUMENT_NUM.fill(kwargs.get("document_num") or str(generate_random_number(6)))
        if not only_required_fields:
            self.DOCUMENT_PROVIDE_BY.fill(kwargs.get("document_provide_by") or "ГУ МВД РОССИИ")
        if not only_required_fields:
            self.DOCUMENT_DIVISION_CODE.fill(
                kwargs.get("document_division_code") or f"{generate_random_number(3)}-{generate_random_number(3)}"
            )
        if not only_required_fields:
            self.DOCUMENT_DATE.fill(
                kwargs.get("document_date") or faker_ru.date_between(start_date, end_date).strftime("%d.%m.%Y")
            )
        if not only_required_fields:
            self.DOCUMENT_VALID_DATE.fill(
                kwargs.get("document_valid_date")
                or faker_ru.date_between(datetime.datetime.today(), get_shifted_datetime("+500d")).strftime("%d.%m.%Y")
            )
        if not only_required_fields:
            self.BIRTH_PLACE.fill(kwargs.get("birth_place") or faker_ru.city())
        self.BIRTH_DATE.fill(kwargs.get("birth_date") or faker_ru.date_of_birth().strftime("%d.%m.%Y"))
        self.NATIONALITY.select_by_value(kwargs.get("nationality") or "Россия")
        self.SPEAKING_LANGUAGE.select_by_value(kwargs.get("speaking_language") or "Русский")
        self.REGISTRATION_ADDRESS.select_by_value(kwargs.get("registration_address") or BasicSystemAddress.address)
        if not only_required_fields:
            self.REPUTATION.fill(kwargs.get("reputation") or "Автотестовая репутация")
        self.PUBLIC_PERSON_CHECKBOX.click()
        if not only_required_fields:
            self.CONTACT_PHONE.fill(kwargs.get("contact_phone") or faker_ru.phone_number())
        if not only_required_fields:
            self.CONTACT_EMAIL.fill(kwargs.get("contact_email") or faker_ru.email())
        if not only_required_fields:
            self.BUSINESS_ACTIVITY.select_by_value(kwargs.get("business_activity") or "Агент")
        if not only_required_fields:
            self.NOTE.fill(kwargs.get("note") or str(generate_random_number(10)))
        self.TAX_SCHEME.select_by_value(kwargs.get("tax_scheme") or "Схема налогообложения по умолчанию")


class CreateOrganization(DynamicForms):
    """Форма 'Создание клиента' ЮЛ."""

    def __init__(self, page: Page = None):
        super().__init__(page)
        self.PROPRIETARY_FORM = Select(
            "#customer-organization-create_proprietaryForm", "Организационно-правовая форма", self.page
        )
        self.PROPRIETARY_FORM_TYPE = "АО, Акционерное Общество"
        self.CLIENT_NAME = Element("input[id*='_customerName']", "Имя Клиента", self.page)
        self.TAX_SCHEME = Select("input[id*='taxScheme']", "Схема налогооблажения", self.page)
        self.SAVE_BTN = Element("#customer-organization-create #save", "Сохранить", self.page)

    @allure.step("Заполнить данные клиента ЮЛ")
    def fill_data_for_organization_client(self, only_required_fields: bool = False, **kwargs: Any) -> None:
        start_date = datetime.date(1990, 1, 1)
        end_date = datetime.date(2020, 12, 31)

        if not only_required_fields:
            self.INN.fill(kwargs.get("inn") or str(generate_random_number(10)))
        if not only_required_fields:
            self.PROPRIETARY_FORM.select_by_value(kwargs.get("proprietary_form") or self.PROPRIETARY_FORM_TYPE)
        self.CUSTOMER_NAME.fill(kwargs.get("customer_name") or f"Autotest_{faker_ru.pystr(min_chars=10, max_chars=10)}")
        if not only_required_fields:
            self.REGISTRATION_DOCUMENT.fill(kwargs.get("registration_document") or str(generate_random_number(10)))
        if not only_required_fields:
            self.REGISTRATION_DATE.fill(
                kwargs.get("registration_date") or faker_ru.date_between(start_date, end_date).strftime("%d.%m.%Y")
            )
        if not only_required_fields:
            self.REGISTRATION_NUM.fill(kwargs.get("registration_num") or str(generate_random_number(6)))
        if not only_required_fields:
            self.OKPO.fill(kwargs.get("okpo") or str(generate_random_number(10)))
        if not only_required_fields:
            self.OKATO.fill(kwargs.get("okato") or str(generate_random_number(10)))
        if not only_required_fields:
            self.OKVED.fill(kwargs.get("okved") or str(generate_random_number(10)))
        if not only_required_fields:
            self.OGRN.fill(kwargs.get("ogrn") or str(generate_random_number(13)))
        if not only_required_fields:
            self.KPP.fill(kwargs.get("kpp") or str(generate_random_number(9)))
        self.NATIONALITY.select_by_value(kwargs.get("nationality") or "Россия")
        self.SPEAKING_LANGUAGE.select_by_value(kwargs.get("speaking_language") or "Русский")
        if not only_required_fields:
            self.BUSINESS_ACTIVITY.select_by_value(kwargs.get("business_activity") or "Агент")
        if not only_required_fields:
            self.NOTE.fill(kwargs.get("note") or str(generate_random_number(10)))
        self.REGISTRATION_ADDRESS.select_by_value(kwargs.get("registration_address") or BasicSystemAddress.address)
        if not only_required_fields:
            self.REPUTATION.fill(kwargs.get("reputation") or "Автотестовая репутация")
        self.TAX_SCHEME.select_by_value(kwargs.get("tax_scheme") or "Схема налогообложения по умолчанию")


class AddressCreate(DynamicForms):
    """Форма 'Создание нового адреса'."""

    def __init__(self, page: Page):
        super().__init__(page)

        self.TITLE = Element("//h3[contains(text(), 'Создание нового адреса')]", "Заголовок формы", self.page)
        self.ADDED_CARD = ElementsList(
            ".ant-card", "Блоки с выбранным типом и наименованием адресного объекта", self.page
        )
        self.ADDED_CARD_EDIT_BTN = ElementsList(
            ".ant-card-extra button:nth-child(1)", "Кнопки 'Редактировать'", self.page
        )
        self.ADDED_CARD_DELETE_BTN = ElementsList(".ant-card-extra button:nth-child(2)", "Кнопки 'Удалить'", self.page)
        self.ATTRIBUTE_HEADER = ElementsList(
            "[id*='create-address-form'] .ant-collapse-item", "Панель с кнопкой 'Атрибуты'", self.page
        )
        self.ATTRIBUTE_FIELDS_BLOCK = ElementsList(
            ".ant-collapse-content .ant-form-item-control-input-content", "Блок полей атрибутов", self.page
        )
        self.ATTRIBUTE_FIELDS = ElementsList(
            ".ant-collapse-content .ant-form-item-control-input-content input", "Поля атрибутов", self.page
        )

        self.OPTION_ITEMS = ElementsList(
            "[id*='create-address-form'] .ant-select-item-option", "Варианты выбора в списке", self.page
        )
        self.OBJECT_TYPE = Select("[id*='_select-elementCode']", "Поле 'Выберите адресный объект'", self.page)
        self.OBJECT_NAME_AUTOCOMPLETE = Autocomplete(
            ".ant-row.ant-form-item-row:has(label[title='Наименование']) input[id*='rc_select']:not([readonly])",
            "Поле 'Наименование'",
            self.page,
        )
        self.OBJECT_NUM = Element(
            ".ant-row.ant-form-item-row:has(label[title='Номер']) input[id*='rc_select']:not([readonly])",
            "Поле 'Номер'",
            self.page,
        )
        self.OBJECT_ADDITIONAL_NUM = Element(
            ".ant-row.ant-form-item-row:has(label[title='Дополнительный номер']) input[id*='rc_select']",
            "Поле 'Дополнительный номер'",
            self.page,
        )
        self.OBJECT_EXTRA_NUM = Element(
            ".ant-row.ant-form-item-row:has(label[title='Добавочный номер']) input[id*='rc_select']",
            "Поле 'Добавочный номер'",
            self.page,
        )
        self.OBJECT_GAR = Element(
            ".ant-row.ant-form-item-row:has(label[title='Уникальный номер ГАР']) input[id*='rc_select']",
            "Поле 'Уникальный номер ГАР'",
            self.page,
        )
        self.OBJECT_MAIL_INDEX = Element(
            ".ant-row.ant-form-item-row:has(label[title='Почтовый индекс']) input[id*='rc_select']",
            "Поле 'Почтовый индекс'",
            self.page,
        )

        self.REGION_TYPE_DROPDOWN = Select("input[id*='regionType']", "Поле ввода 'Тип региона'", self.page)
        self.CITY_TYPE_DROPDOWN = Select("input[id*='cityType']", "Поле ввода 'Тип города'", self.page)
        self.STREET_TYPE_DROPDOWN = Autocomplete(
            "input[id*='form_street_streetType']", "Поле ввода 'Тип улицы'", self.page
        )
        self.HOUSE_TYPE_DROPDOWN = Autocomplete("input[id*='houseType']", "Поле ввода 'Тип дома'", self.page)
        self.APARTMENT_TYPE_DROPDOWN = Select(
            "input[id*='apartmentType']", "Поле ввода 'Тип жилого помещения'", self.page
        )
        self.ADDITIONAL_HOUSE_TYPE_DROPDOWN = Autocomplete(
            "input[id*='house_additionalType']", "Поле ввода 'Дополнительный тип дома'", self.page
        )
        self.EXTRA_HOUSE_TYPE_DROPDOWN = Autocomplete(
            "input[id*='house_extraType']", "Поле ввода 'Добавочный тип дома'", self.page
        )
        self.APPLY_BTN = Element("[id*='save-button']", "Кнопка 'Применить'", self.page)
        self.ADD_ADDRESS_OBJECT_BTN = Element(
            "[id*='add-address-element-button']", "Кнопка 'Добавить адресный объект'", self.page
        )
        self.CREATE_BTN = Element("[id*='create-address-modal_accept-button']", "Кнопка 'Создать'", self.page)
        self.CANCEL_BTN = Element("[id*='create-address-modal_cancel-button']", "Кнопка 'Отмена'", self.page)


class AddAddress(DynamicForms):
    """Форма 'Добавление нового адреса'."""

    def __init__(self, page: Page):
        super().__init__(page)

        self.TITLE = Element("//h3[contains(text(), 'Добавление адреса')]", "Заголовок формы", self.page)
        self.ADDRESS_TYPE_FIELD = Select("#place-add_placeType", "Поле ввода 'Тип адреса'", self.page)
        self.ADDRESS_TYPE_OPTIONS = ElementsList(".ant-select-item-option", "Выбор 'Тип адреса'", self.page)
        self.ADDRESS_INPUT = Element("#place-add_addressString", "Поле ввода 'Адреса'", self.page)
        self.ADDRESS_FIELD = Autocomplete("#place-add_addressString", "Поле 'Адрес'", self.page)
        self.ADD_ADDRESS_TO_CATALOG = Element(
            "a[href='/rm-ui/allundefined']", "Ссылка 'Добавить адрес в справочник'", self.page
        )
        self.MAPS_LINK_INPUT = Element("#place-add_addressUrl", "Поле ввода 'Ссылка на карту'", self.page)
        self.ADDRESS_OPTION = ElementsList(
            "#addressString_control .ant-select-item-option-content", "Варианты адреса", self.page
        )
        self.SAVE_BTN = Element("#save", "Кнопка 'Добавить'", self.page)
        self.CANCEL_BTN = Element("#cancel", "Кнопка 'Отмена'", self.page)


class EditAddress(DynamicForms):
    """Форма 'Редактирование адреса Клиента'"""

    def __init__(self, page: Page):
        super().__init__(page)

        self.TITLE = Element("//h3[contains(text(), 'Редактирование адреса')]", "Заголовок формы", self.page)
        self.ADDRESS_INPUT = Element("#place-edit_addressString", "Поле ввода 'Адреса'", self.page)
        self.ADD_ADDRESS_TO_CATALOG = Element(
            "a[href='/rm-ui/allundefined']", "Ссылка 'Добавить адрес в справочник'", self.page
        )
        self.MAPS_LINK_INPUT = Element("#place-edit_addressUrl", "Поле ввода 'Ссылка на карту'", self.page)
        self.ADDRESS_OPTION = ElementsList(
            "#addressString_control .ant-select-item-option-content", "Варианты адреса", self.page
        )


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
        self.TYPE_SORT_BTN = Element(
            "//span[contains(text(), 'Тип')]/parent::div[contains(@class, 'sorters')]",
            "Кнопка сортировки 'Тип'",
            self.page,
        )
        self.EDIT_ADDRESS = Element(
            "button[|title='Изменить адрес'],[|title='Edit address']", "Кнопка 'Изменить адрес'", self.page
        )
        self.DELETE_ADDRESS = Element(
            "button[|title='Удалить адрес'],[|title='Delete address']", "Кнопка 'Удалить адрес'", self.page
        )
        self.SETTING_BTN = Element("button.ant-dropdown-trigger", "Кнопка 'Настройка колонок'", self.page)
        self.SETTING_OPTIONS = ElementsList("input.ant-checkbox-input", "Чекбоксы 'Настройка колонок'", self.page)


class RequestCreate(DynamicForms):
    """Форма 'Создание заявки'."""

    def __init__(self, page: Page):
        super().__init__(page)

        self.CREATE_FORM = Element("#inquiry-create-form", "Форма создания заявки", self.page)
        self.TITLE = Element("#inquiry-create-form h3", "Заголовок форма 'Создание заявки'", self.page)
        self.CLIENT = Element("#inquiry-create-form a", "Выбранный клиент", self.page)
        self.SELECT_CLIENT_BTN = Dropdown(
            "#inquiry-create-form button:has(.platform-button-icon-right)", "Сменить клиента", self.page
        )
        self.CHOOSE_AGREEMENT_BTN = Select("input[id*='saleAddAgreement']", "Поле создание договора", self.page)
        self.CHOOSE_PRIORITY_BTN = Select("input[id*='priority']", "Поле выбора приоритета", self.page)

        self.CODE = Element("#code", "Код", self.page)
        self.TOPIC = Element("#topic", "Тема", self.page)
        self.EMAIL = Element(".ant-col:has([for='email']) input", "Предпочтительный email", self.page)
        self.PHONE = Element(".ant-col:has([for='phone']) input", "Предпочтительный телефон", self.page)
        self.DESCRIPTION = Element("#description", "Описание", self.page)
        self.FILE_INPUT = Element("input[type='file']", "Документы", self.page)
        self.FORWARD_BTN = Element("#forward", "Кнопка 'Передать'", self.page)


class ChooseRequestTopic(DynamicForms):
    """Форма 'Выбор темы заявки'"""

    def __init__(self, page: Page):
        super().__init__(page)

        self.CHOOSE_REQUEST_TOPIC_FORM = Element(".ant-drawer-title", "Форма 'Выбор темы заявки'", self.page)
        self.EXPAND_BTN = ElementsList(
            ".ant-tree-switcher_open,.ant-tree-switcher_close", "Кнопка развернуть список", self.page
        )
        self.REQUEST_TOPIC_NAME = ElementsList(".ant-tree-node-content-wrapper", "Тема заявки", self.page)
        self.ACCEPT_BTN = Element("#_accept-button", "Кнопка 'Применить'", self.page)


class ForwardInquiryForm(DynamicForms):
    """Форма 'Передача на обработку' при оформлении заявки"""

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page

        self.FORWARD_FORM = Element("#forwardInquiryForm", "Форма передачи на обработку", self.page)
        self.PROCESS_FIELD = Select("#forwardInquiryForm_process", "Поле 'Шаг'", self.page)
        self.QUEUE_FIELD = Select("#forwardInquiryForm_queue", "Поле 'Очередь'", self.page)
        self.RESPONSIBLE_FIELD = Select("#forwardInquiryForm_responsible", "Поле 'Ответственный'", self.page)
        self.DUE_DATE_FIELD = DatePicker("#forwardInquiryForm_dueDate", "Поле 'Обработать до'", self.page)
        self.COMMENT_FIELD = Element("#forwardInquiryForm_comment", "Поле 'Сопроводительная записка'", self.page)
        self.FORWARD_BTN = Element("#_accept-button", "Кнопка 'Передать'", self.page)

    def check_form_fields(self) -> None:
        self.PROCESS_FIELD.check_attribute_by_value("aria-required", "true")
        self.QUEUE_FIELD.check_attribute_by_value("aria-required", "true")
        self.RESPONSIBLE_FIELD.check_attribute_not_contain_value("aria-required", "true")
        self.DUE_DATE_FIELD.check_attribute_not_contain_value("aria-required", "true")
        self.COMMENT_FIELD.check_attribute_not_contain_value("aria-required", "true")
        self.RESPONSIBLE_FIELD.not_to_be_enabled()
        self.DUE_DATE_FIELD.not_to_be_enabled()


class CreateInquiryNotification(BaseElements):
    """Уведомление о создании заявки"""

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page

        self.INQUIRY_NOTIFICATION = Element(
            ".platform-snackbar[style*='opacity: 1']", "Уведомление о создании заявки", self.page
        )
        self.INQUIRY_TEXT = Element(".platform-snackbar[style*='opacity: 1'] p", "Текст уведомления", self.page)
        self.FORWARD_BTN = Element(
            ".platform-snackbar[style*='opacity: 1'] a[href*='inquiries']",
            "Кнопка перехода к созданной заявке",
            self.page,
        )
        self.CROSS_BTN = Element(
            ".platform-snackbar[style*='opacity: 1'] button", "Крестик для закрытия уведомления", self.page
        )


class LinkingToInquiresForm(DynamicForms):
    """Форма 'Связывание с заявкой'"""

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page

        self.LINKING_TO_INQUIRIES_FORM = Element(
            ".ant-drawer-content-wrapper:not([class*=hidden])", "Форма 'Связывание с заявкой'", self.page
        )
        self.TITLE = Element(".ant-drawer-title h4", "Заголовок формы", self.page)
        self.CLEAR_FILTER_BTN = Element(
            "(//*[contains(@class, 'ant-drawer-content')] //*[@class='ant-drawer-body'] //button)[2]",
            "Кнопка 'Очистить все фильтры'",
            self.page,
        )
        self.INQUIRY = ElementsList(".ant-drawer-content tbody tr", "Заявка", self.page)
        self.INQUIRY_NUMBER = ElementsList(".ant-drawer-content tbody td:nth-child(1) a", "Номер заявки", self.page)
        self.INQUIRY_TOPIC = ElementsList(".ant-drawer-content tbody td:nth-child(2) div", "Тема заявки", self.page)
        self.IMPROVE_BALANCE_CHECKBOX = Element(
            ".ant-drawer-content .ant-checkbox", "Чекбокс 'Улучшить баланс'", self.page
        )
        self.CANCEL_BTN = Element(
            "(//*[contains(@class, 'ant-drawer-content')] //*[@class='ant-drawer-footer'] //button)[1]",
            "Кнопка 'Отмена'",
            self.page,
        )
        self.LINKED_BTN = Element(
            "(//*[contains(@class, 'ant-drawer-content')] //*[@class='ant-drawer-footer'] //button)[2]",
            "Кнопка 'Связать'",
            self.page,
        )

    @allure.step("Выбрать заявку {inquiry_id}")
    def choice_inquiry(self, inquiry_id: int) -> None:
        self.INQUIRY_NUMBER.wait_for_text_in_all([str(inquiry_id)])
        inquiry_index = self.INQUIRY_NUMBER.text_list.index(str(inquiry_id))
        self.INQUIRY_TOPIC.click(inquiry_index)


class LinkedInquiriesForm(DynamicForms):
    """Форма 'Связанные заявки'"""

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page

        self.LINKED_INQUIRIES_FORM = Element(
            ".ant-drawer-content-wrapper:not([class*=hidden])", "Форма 'Связанные заявки'", self.page
        )
        self.TITLE = Element(".ant-drawer-content-wrapper:not([class*=hidden]) h4", "Заголовок формы", self.page)
        self.INQUIRY = ElementsList(".ant-drawer-content-wrapper:not([class*=hidden]) tbody tr", "Заявка", self.page)
        self.INQUIRY_NUMBER = ElementsList(
            ".ant-drawer-content-wrapper:not([class*=hidden]) tbody td:nth-child(1) a", "Номер заявки", self.page
        )
        self.INQUIRY_TOPIC = ElementsList(
            ".ant-drawer-content-wrapper:not([class*=hidden]) tbody td:nth-child(2) div", "Тема заявки", self.page
        )
        self.CREATE_DATE = ElementsList(
            ".ant-drawer-content-wrapper:not([class*=hidden]) tbody td:nth-child(3) div", "Дата создания", self.page
        )
        self.RESPONSIBLE = ElementsList(
            ".ant-drawer-content-wrapper:not([class*=hidden]) tbody td:nth-child(4) div", "Ответственный", self.page
        )

    def check_inquires(
        self,
        inquiry_id: int,
        topic: str = None,
        create_date: str = None,
        responsible: str = None,
        count: int = None,
        check_form: bool = True,
    ) -> None:
        if check_form:
            self.LINKED_INQUIRIES_FORM.wait_to_be_visible()
            self.TITLE.wait_to_have_text("Связанные заявки")
        if count is not None:
            self.INQUIRY.wait_to_have_count(1)
        self.INQUIRY_NUMBER.wait_for_text_in_all(str(inquiry_id))
        index = self.INQUIRY_NUMBER.text_list.index(str(inquiry_id))
        if topic:
            self.INQUIRY_TOPIC[index].to_contain_text(topic)
        if create_date:
            self.CREATE_DATE[index].to_contain_text(create_date)
        if responsible:
            self.RESPONSIBLE[index].to_contain_text(responsible)


class ContractCreate(DynamicForms):
    """Форма 'Создание договора'."""

    def __init__(self, page: Page):
        super().__init__(page)

        self.CONTRACT_CATEGORY = Select("#agreement-card-create_category", "Выбор категории договора", self.page)
        self.AGREEMENT_TYPE = Select("#agreement-card-create_agreementType", "Выбор типа договора", self.page)
        self.SECRET_KEY = Element("#agreement-card-create_secretKey", "Кодовое слово", self.page)
        self.CONTRACT_SIGN_DATE = DatePicker("#agreement-card-create_signingDate", "Дата подписания договора", self.page)
        self.INDEFINITE_CHECKBOX = Element(
            "#agreement-card-create_isIndefinitely", "Неопределенный срок действия", self.page
        )
        self.EXPIRATION_DATE = DatePicker("#expireDate_control", "Дата расторжения договора", self.page)
        self.CLIENT_SINGER = Select("#agreement-card-create_agreementSigner", "ФИО представителя клиента", self.page)
        self.OPERATOR_LAST_NAME = Element(
            "#agreement-card-create_signingUserSurname", "Фамилия представителя оператора", self.page
        )
        self.OPERATOR_FIRST_NAME = Element(
            "#agreement-card-create_signingUserFirstName", "Имя представителя оператора", self.page
        )
        self.OPERATOR_SUR_NAME = Element(
            "#agreement-card-create_signingUserPatronymic", "Отчество представителя оператора", self.page
        )
        self.SINGER_PROXY_NUM = Element(
            "#agreement-card-create_customerSignerProxyNumber", "Номер доверенности", self.page
        )
        self.PROXY_DATE = DatePicker("#customerSignerProxyStartDate_control", "Дата доверенности", self.page)
        self.USE_EXISTING_BANK_CHECKBOX = Element(
            "#useExistingBankData_control", "Выбрать существующие реквизиты", self.page
        )
        self.CLIENT_BANK_DATA = Select(
            "#agreement-card-create_existingBankData", "Банк и расчетный счет клиента", self.page
        )
        self.OPERATOR_BANK_DATA = Select(
            "#agreement-card-create_bankOperator", "Банк и расчетный счет оператора", self.page
        )


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
        self.FOUNDED_FIO = ElementsList(
            "#search-customer-table .ant-table-tbody tr td:nth-child(1)", "ФИО клиента", self.page
        )
        self.FOUNDED_CUSTOMER_TYPE = ElementsList(
            "#search-customer-table .ant-table-tbody tr td:nth-child(2)", "Тип клиента", self.page
        )
        self.FOUNDED_CUSTOMER_STATUS = ElementsList(
            "#search-customer-table .ant-table-tbody tr td:nth-child(3)", "Статус клиента", self.page
        )
        self.FOUNDED_DOCUMENT_NUM = ElementsList(
            "#search-customer-table .ant-table-tbody tr td:nth-child(4)", "Номер документа", self.page
        )
        self.FOUNDED_CONTRACT = ElementsList(
            "#search-customer-table .ant-table-tbody tr td:nth-child(5)", "Договор", self.page
        )


class CreateSalesAndServiceManagement(RequestCreate):
    """Форма 'Создание продажи и управления услугами'"""

    def __init__(self, page: Page):
        super().__init__(page)

        self.CONTACT_PERSON = Element("#inqrLinkedPerson", "Контактное лицо", self.page)
        self.SELECTED_SALE = Select("#saleAgreement", "Договор", self.page)
        self.SALE_ACCOUNT = Select("#saleAccount", "Лицевой счет", self.page)
        self.ADD_SALE_TYPE = Select("#saleAddAgreement", "Создание Договора", self.page)
        self.TITLE_CREATE_ADD_AGREEMENT = Element(
            "label[for=saleAddAgreementAdd]", "Заголовок 'Создание дополнительного соглашения'", self.page
        )
        self.CREATE_ADD_AGREEMENT = Select("#saleAddAgreementAdd", "Создание дополнительного соглашения", self.page)
        self.END_DATE = Element(
            ".ant-form-item:has(label[|title='Планируемая дата окончания'],[|title='Планируемая дата окончания']) "
            ".ant-form-item-control-input-content",
            "Планируемая дата окончания",
            self.page,
        )
        self.SAVE_BTN = Element("#inquiry-create-form #save", "Кнопка 'Сохранить'", self.page)


class CreateSystemProblem(DynamicForms):
    """Форма 'Создание системный проблемы'"""

    def __init__(self, page: Page):
        super().__init__(page)

        self.PROBLEM_NAME = Element("#name", "Поле ввода 'Наименования'", self.page)
        self.PROBLEM_TYPE_FIELD = Element("#commonFaultType", "Поле 'Тип системной проблемы'", self.page)
        self.PROBLEM_TYPE_OPTIONS = ElementsList(
            ".ant-tree-title span span", "Выбор 'Типа системной проблемы'", self.page
        )
        self.PRIMARY_ACCEPT_BTNS = ElementsList(
            "#_accept-button .platform-button__content", "Выбор кнопки 'Применить'", self.page
        )

        self.OCCURANCE_DATE = DatePicker("#raiseDate", "Дата возникновения", self.page)
        self.PLANNED_END_DATE = DatePicker("#planCloseDate", "Дата окончания (план)", self.page)

        self.CLEAR_OCCURANCE_DATE = ElementsList(".ant-picker-clear", "Очистка 'Даты возникновения'", self.page)
        self.CLEAR_END_DATE = ElementsList(".ant-picker-clear", "Очистка 'Даты окончания'", self.page)
        self.CLIENT_TYPE_FIELD = Select("#CF_CLNT_TYPE", "Поле ввода 'Тип клиента'", self.page)
        self.PROBLEM_REGION = Select("#CF_REGION", "Регион возникновения проблемы", self.page)

        self.PROBLEM_SERVICE_FIELD = Element("#TEST_1", "Поле 'Название услуги'", self.page)
        self.CLIENT_CONTACTS_AGAIN_RADIO_BTNS = ElementsList(
            "#TEST_2 .ant-radio", "Переключатели параметра 'Клиент обращается повторно?'", self.page
        )
        self.PROBLEM_OCCURANCE_DATE = DatePicker("#TEST_3", "Дата возникновения проблемы", self.page)
        self.PROBLEMATIC_SERVICE_FIELD = Select("#TEST_5", "Поле 'Проблемный сервис'", self.page)
        self.ATTEMPTS_NUM_FIELD = Element("#TEST_6", "Поле 'Количество попыток'", self.page)
        self.ADJUSTMENT_REQUIRED_RADIO_BTNS = ElementsList(
            "#TEST_4 .ant-radio", "Переключатели параметра 'Требуется корректировка?'", self.page
        )
        self.AMOUNT_OF_CHARGES_FIELD = Element("#TEST_7", "Поле 'Сумма начислений'", self.page)

        self.EXPERTS_CHECKBOX = Element("#onlyExpertLink", "Чекбокс 'Привязывают только эксперты'", self.page)
        self.INFORM_CLIENT_FIELD = Element("#messageToSubscriber", "Поле 'Сообщить клиенту'", self.page)
        self.TECHNICAL_DESCRIPTION_FIELD = Element("#description", "Поле 'Техническое описание'", self.page)
        self.OPERATOR_DESCRIPTION_FIELD = Element("#descriptionForOperator", "Поле 'Описание для оператора'", self.page)
        self.CREATE_PROBLEM_BTN = ElementsList("#_accept-button", "Кнопка 'Создать'", self.page)


class EditSystemProblem(DynamicForms):
    """Форма 'Редактирование системный проблемы'"""

    def __init__(self, page: Page):
        super().__init__(page)

        self.PROBLEM_NAME = Element("#additional_values_name", "Поле ввода 'Наименования'", self.page)
        self.PRIORITY_FIELD = Select("#additional_values_priority", "Приоритет", self.page)
        self.PROBLEM_TYPE_FIELD = Element("#additional_values_topic", "Поле 'Тип системной проблемы'", self.page)
        self.PROBLEM_TYPE_OPTIONS = ElementsList(
            ".ant-tree-title span span", "Выбор 'Типа системной проблемы'", self.page
        )
        self.PRIMARY_ACCEPT_BTNS = ElementsList(
            "#_accept-button .platform-button-content", "Выбор кнопки 'Применить'", self.page
        )
        self.REASON_TYPE_FIELD = Select("#additional_values_reasonType", "Тип причины", self.page)
        self.INFLUENCE_POTENTIAL_FIELD = Select("#additional_values_potential", "Потенциал влияния", self.page)

        self.OCCURANCE_DATE = DatePicker("#additional_values_raiseDate", "Дата возникновения", self.page)
        self.PLANNED_END_DATE = DatePicker("#additional_values_planCloseDate", "Дата окончания (план)", self.page)
        self.FACT_END_DATE = DatePicker("#additional_values_factCloseDate", "Дата окончания (факт)", self.page)

        self.CLEAR_OCCURANCE_DATE = ElementsList(".ant-picker-clear", "Очистка 'Даты возникновения'", self.page)
        self.CLEAR_END_DATE = ElementsList(".ant-picker-clear", "Очистка 'Даты окончания'", self.page)

        self.EXPERTS_CHECKBOX = Element(
            "#additional_values_onlyExpertLink", "Чекбокс 'Привязывают только эксперты'", self.page
        )
        self.INFORM_CLIENT_FIELD = Element(
            "#additional_values_messageToSubscriber", "Поле 'Сообщить клиенту'", self.page
        )
        self.TECHNICAL_DESCRIPTION_FIELD = Element(
            "#additional_values_description", "Поле 'Техническое описание'", self.page
        )
        self.OPERATOR_DESCRIPTION_FIELD = Element(
            "#additional_values_descriptionForOperator", "Поле 'Описание для оператора'", self.page
        )
        self.SAVE_PROBLEM_BTN = ElementsList("button + [variant=primary]", "Кнопка 'Сохранить'", self.page)


class SelectingReasonType(DynamicForms):
    """Форма 'Выбор типа причины'"""

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page

        self.PROBLEM_TYPE_LIST = ElementsList(".ant-tree-title span span", "Выбор типа причины", self.page)
        self.PRIMARY_ACCEPT_BTNS = ElementsList("#_accept-button", "Выбор кнопки 'Применить'", self.page)


class TransferProcessing(DynamicForms):
    """Форма 'Передача на обработку'"""

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page

        self.TRANSFER_FORM = Element("#forwardCommonFaultForm", "Форма передачи на обработку", self.page)
        self.TRANSFER_STEP_FIELD = Select("#forwardCommonFaultForm_process", "Поле 'Шаг'", self.page)
        self.QUEUE_FIELD = Select("#forwardCommonFaultForm_queue", "Поле 'Очередь'", self.page)
        self.HAND_OVER_BTN = ElementsList("#_accept-button", "Кнопка 'Передать'", self.page)
        self.COVER_NOTE_FIELD = Element("#forwardCommonFaultForm_comment", "Поле 'Сопроводительная записка'", self.page)
        self.PROCESS_UNTIL = DatePicker("#forwardCommonFaultForm_dueDate", "Поле 'Обработать до'", self.page)


class FilterSettings(DynamicForms):
    """Форма 'Фильтры'"""

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page

        self.PROBLEM_NUM_FIELD = Element("#commonFaultIds", "Поле 'Номер проблемы'", self.page)
        self.PROBLEM_NAME_FIELD = Element(
            ".ant-form.ant-form-vertical .ant-form-item:nth-child(4) input", "Поле 'Наименование проблемы'", self.page
        )
        self.PROBLEM_REASON_FIELD = Element("#commonFaultTypeCodes", "Поле 'Тип причины'", self.page)
        self.PROBLEM_TYPE_FIELD = Select("#reasons", "Выбор 'Типа проблемы'", self.page)
        self.PRIORITY_FIELD = Select("#priorityCodes", "Выбор 'Приоритета'", self.page)
        self.REGISTERED_FIELD = Select("#operatorLogins", "Выбор 'Кто зарегистрировал'", self.page)
        self.PROBLEM_TOPIC_FIELD = Element("#activityCodes", "Поле 'Шаг'", self.page)

        self.TREE_TITLE_LIST = ElementsList(".ant-tree-title span>span", "Список наименований", self.page)
        self.REASON_CHECKBOX_LIST = ElementsList(".ant-tree-checkbox-inner", "Список чекбоксов наименований", self.page)
        self.CANCEL_CHOICE = Element(".ant-drawer-body>div>div>a+a", "Отменить выбор", self.page)

        self.CHECKBOX_TITLE_LIST = ElementsList(
            ".ant-select-item-option-content .platform-filterable-component-text-to-highlight span",
            "Список напименований",
            self.page,
        )
        self.CHECKBOX_LIST = ElementsList(
            ".ant-select-item-option-content  [type='checkbox']", "Список чекбоксов наименований", self.page
        )

        self.PLUS_SQUARE = Element("[aria-label='plus-square']", "Кнопка раскрытия списка", self.page)

        self.APPLY_BTN = ElementsList(".ant-drawer-footer [variant='primary']", "Кнопка 'Применить'", self.page)
        self.PRIMARY_ACCEPT_BTNS = ElementsList(
            "#_accept-button .platform-button-content", "Выбор кнопки 'Применить'", self.page
        )
        self.RESET_BTN = ElementsList(
            ".ant-drawer-footer [variant='secondary']:nth-child(1)", "Кнопка 'Сбросить'", self.page
        )


class CreateTransition(DynamicForms):
    """Форма 'Создание перехода'"""

    def __init__(self, page: Page):
        super().__init__(page)

        self.FORM = Element(".ant-drawer-content-wrapper", "Форма 'Создание перехода'", self.page)
        self.FROM_STATUS = Select("#fromStatusId", "Исходный статус", self.page)
        self.TO_STATUS = Select("#toStatusId", "Следующий статус", self.page)
        self.PRIORITY = Element("#priority", "Приоритет", self.page)
        self.EVENT = Select("#eventId", "Событие", self.page)
        self.IS_MANUAL_CHECKBOX = Element("#isManual", "Ручной запуск перехода", self.page)
        self.CANCEL_BTN = Element("//*[@class='ant-drawer-footer']/div/button[1]", "Кнопка 'Отмена'", self.page)
        self.ACTIVE_ADD_TRANSITION_BTN = Element(
            "//*[@class='ant-drawer-footer']/div/button[2]", "Кнопка 'Добавить'", self.page
        )

    def fill_priority(self, priority: int) -> int:
        auto_priority = self.page.locator(self.PRIORITY.path).get_attribute("value")
        if auto_priority == "":
            self.PRIORITY.fill(str(priority))
        else:
            priority = int(auto_priority)
        return priority


class EditDynamicElements(BaseElements):
    """Динамические элементы в редактировании.
    (Отличается от класса DynamicElements,
    только префиксом edit_ в id элемента)."""

    def __init__(self, page: Page):
        super().__init__(page)

        self.CREATE_BTN = Element(
            "#place-edit_addressString_create-address-modal_accept-button", "Кнопка 'Создать'", self.page
        )
        self.ACCOUNT_NUM = Element("input[id*='edit_accountNumber']", "Номер ЛС", self.page)
        self.SUBSCRIPTION_ID = Element("input[id*='edit_subscriptionIdentification']", "Абонент", self.page)
        self.CONTRACT_NUM = Element("input[id*='edit_agreementNumber']", "Номер договора", self.page)
        self.INN = Element("input[id*='edit_taxIdentificationNumber']", "ИНН", self.page)
        self.KPP = Element("input[id*='edit_registrationReasonCode']", "КПП", self.page)
        self.SNILS = Element("input[id*='edit_INILA']", "СНИЛС", self.page)
        self.CUSTOMER_TYPE = Element("input[id*='edit_customerTypes']", "Тип клиента", self.page)
        self.CUSTOMER_NAME = Element("input[id*='edit_customerName']", "Имя клиента", self.page)
        self.ID_DOCUMENT_SERIAL = Element("input[id*='edit_identificationDocumentSeries']", "Серия документа", self.page)
        self.ID_DOCUMENT_NUM = Element("input[id*='edit_identificationDocumentNumber']", "Номер документа", self.page)
        self.DOCUMENT_SERIAL = Element("input[id*='edit_documentSeries']", "Серия документа", self.page)
        self.DOCUMENT_NUM = Element("input[id*='edit_documentNumber']", "Номер документа", self.page)
        self.NATIONALITY = Element("input[id*='edit_nationality']", "Гражданство", self.page)
        self.SPEAKING_LANGUAGE = Element("input[id*='edit_speakingLanguage']", "Язык общения", self.page)
        self.RESIDENT_CHECKBOX = Element("input[id*='edit_isResident']", "Флаг резидента", self.page)
        self.BUSINESS_ACTIVITY = Element("input[id*='edit_businessActivity']", "Вид деятельности", self.page)
        self.NOTE = Element("textarea[id*='edit_note']", "Примечание", self.page)
        self.REGISTRATION_ADDRESS = Element("input[id*='edit_registrationAddress']", "Адрес регистрации", self.page)
        self.REPUTATION = Element("input[id*='edit_reputation']", "Репутация", self.page)
        self.OKPO = Element("input[id*='edit_RNNBO']", "ОКПО", self.page)
        self.OKATO = Element("input[id*='edit_ARCPS']", "ОКАТО", self.page)
        self.OKVED = Element("input[id*='edit_economicActivities']", "ОКВЭД", self.page)
        self.OGRN = Element("input[id*='edit_PSRN']", "ОГРН", self.page)
        self.PUBLIC_PERSON_CHECKBOX = Element("input[id*='edit_publicOfficial']", "Флаг общественного лица", self.page)
        self.BIRTH_PLACE = Element("input[id*='edit_birthPlace']", "Место рождения", self.page)
        self.BIRTH_DATE = Element("input[id*='edit_birthDate']", "Дата рождения", self.page)
        self.GENDER_DROPDOWN = Element("input[id*='edit_gender']", "Пол", self.page)
        self.DOCUMENT_TYPE = Element("input[id*='edit_documentType']", "Тип документа", self.page)
        self.DOCUMENT_DATE = Element("input[id*='edit_documentDateOfIssue']", "Дата выдачи документа", self.page)
        self.DOCUMENT_PROVIDE_BY = Element(
            "input[id*='edit_documentProvidedByOrganization']", "Организация, выдавшая документ", self.page
        )
        self.DOCUMENT_DIVISION_CODE = Element("input[id*='edit_documentDivisionCode']", "Код подразделения", self.page)
        self.DOCUMENT_VALID_DATE = Element("input[id*='edit_documentValidFor']", "Срок действия документа", self.page)

        self.REGISTRATION_DOCUMENT = Element("input[id*='edit_PSRNInfo']", "Регистрационный документ", self.page)
        self.REGISTRATION_DATE = Element("input[id*='edit_registrationDate']", "Дата регистрации", self.page)
        self.REGISTRATION_NUM = Element("input[id*='edit_foreignRegistrationNumber']", "Номер регистрации", self.page)
        self.TAX_SCHEME = Element("input[id*='edit_taxScheme']", "Налоговая схема", self.page)


class Notifications(BaseElements):
    def __init__(self, page: Page = None):
        super().__init__(page)

        self.SUCCESS_CREATE_CLIENT = Element("#notifications p", "Уведомление 'Клиент создан'", self.page)
        self.NOTIFICATION = Element("#notifications > div > div", "Уведомление", self.page)
        self.SUCCESS_NOTIFICATIONS_CLOSE_BTN = Element(
            "#notifications > div > div > :nth-child(2)", "Кнопка 'Закрыть уведомление", self.page
        )


class AddAgreement(DynamicForms):
    """Форма 'Добавление нового договора'."""

    def __init__(self, page: Page):
        super().__init__(page)


class AddRelatedPersonForms(DynamicForms):
    """Форма 'Добавление связанного лица'"""

    def __init__(self, page: Page):
        super().__init__(page)
        self.ADD_NEW_RELATED_PERSON_BTN = Element(
            ".ant-drawer-body .platform-button-icon-left", "Кнопка 'Добавить' новое связанное лицо", self.page
        )
        self.TYPE_RELATED_PERSON = Select("input[id*='rc_select_']", "Поле выбора типа связанного лица", self.page)
        self.NAME_RELATED_PERSON = Element(
            "input[id='impersonalName']", "Поле 'Наименование связанного лица'", self.page
        )
        self.FUNCTION_RELATED_PERSON = Select(
            "input[id*='rc_select_']", "Поле выбора функции связанного лица", self.page
        )
        self.NEXT_BTN = Element(".ant-drawer-footer .platform-button-icon-right", "Кнопка 'Далее'", self.page)
        self.ADD_BTN = Element(".ant-drawer-footer button[variant='primary']", "Кнопка 'Добавить'", self.page)
        self.ADD_EMAIL_BTN = Element(
            '//*[@id="root"]/div/div[6]/div/div[3]/div/div/div[2]/div/form/div[4]/button',
            "Кнопка 'Добавить эл. почту'",
            self.page,
        )
        self.ADD_EMAIL_FORM = Element("input[id*='contactEmail_0_email']", "Поле ввода Email", self.page)

    @allure.step("Заполнить данные связанного лица")
    def fill_data_for_related_person(self, **kwargs: Any) -> None:
        self.ADD_NEW_RELATED_PERSON_BTN.click()
        self.TYPE_RELATED_PERSON.select_by_value(kwargs.get("type_related_person") or "Обезличенное")
        self.NAME_RELATED_PERSON.fill(kwargs.get("name_related_person") or "Тестовое наименование")
        self.NEXT_BTN.click()
        self.FUNCTION_RELATED_PERSON.select_by_value(kwargs.get("function") or "Выгодоприобретатель")
        self.NEXT_BTN.click()
        self.ADD_EMAIL_BTN.click()
        self.ADD_EMAIL_FORM.fill(kwargs.get("email") or "test@mail.ru")
        self.ADD_BTN.click()


class PromisedPaymentForm(DynamicForms):
    """Форма 'Подключить обещанный платёж'"""

    def __init__(self, page: Page):
        super().__init__(page)
        self.CUSTOM_PARAM_BTN = Element("#showProductOffer", "Кнопка 'Платеж с произвольными параметрами'", self.page)
        self.AMOUNT_FLD = Element("#amount", "Поле 'Сумма'", self.page)
        self.COMMISSION_FLD = Element("#commission", "Поле 'Комиссия'", self.page)
        self.DURATION_FLD = Element("#duration", "Поле 'Срок действия'", self.page)
        self.ABONENT_FLD = Element("#abonentNo", "Поле 'Абонент'", self.page)
        self.BALANCE_FLD = Element("#balanceTypeId", "Поле 'Кошелек'", self.page)
        self.PRODUCT_OFFER_FLD = Select("#selectProductOffer", "Поле 'Продуктовое предложение'", self.page)

    @allure.step("Заполнить данные обещанного платежа")
    def fill_data_for_promised_payment(
        self, only_required_fields: bool = False, commission_type: bool = False, **kwargs: Any
    ) -> None:
        if not only_required_fields:
            self.AMOUNT_FLD.fill(kwargs.get("amount") or "300")
        if not only_required_fields:
            self.COMMISSION_FLD.fill(kwargs.get("commission") or "0")
        if not only_required_fields:
            self.DURATION_FLD.fill(kwargs.get("duration") or str(generate_random_number(30)))
        if commission_type:
            if not only_required_fields:
                self.ABONENT_FLD.fill(kwargs.get("abonent") or "")


class PersonalAccountForm(DynamicForms):
    """Форма 'Добавление/Редактирование лицевого счета'"""

    def __init__(self, page: Page):
        super().__init__(page)

        self.PAYMENT_METHOD = Select(
            "(//div[@role='dialog']//div[@id='payMethod_control']//input)", "Способ оплаты", self.page
        )
        self.THRESHOLD_CONTROL_CHECKBOX = Element(
            '[id="account-card-create_thresholdControl"]', "Чекбокс 'Контроль порога'", self.page
        )
        self.THRESHOLD_CONTROL_CREATE_FLD = Element(
            "input[id='account-card-create_thresholdBreak']", "Форма ввода 'Контроль порога' при создании", self.page
        )
        self.THRESHOLD_CONTROL_EDIT_FLD = Element(
            "[id='account-card-edit_thresholdBreak']", "Форма ввода 'Контроль порога' при редактировании", self.page
        )


class ProductInfo(DynamicForms):
    """Форма Информация о товаре"""

    def __init__(self, page: Page):
        super().__init__(page)

        self.PRODUCT_NAME = Element(".ant-drawer-title h2", "Название продукта", self.page)

        # HEADER_NAV_TAB
        self.VOLUMES_TAB = Element(".ant-drawer-content [id*=tab-volumes]", "Таб 'Объемы'", self.page)
        self.CHARACTERISTICS_TAB = Element(
            ".ant-drawer-content [id*=tab-characteristics]", "Таб 'Характеристики'", self.page
        )
        self.SERVICES_TAB = Element(".ant-drawer-content [id*=tab-services]", "Таб 'Сервисы'", self.page)
        self.RESOURCES_TAB = Element(".ant-drawer-content [id*=tab-resources]", "Таб 'Ресурсы'", self.page)

        # RESOURCES_TAB
        self.RESOURCES_PANEL = Element("[id*=panel-resources]", "Панель 'Ресурсы'", self.page)
        self.SIM_CARD_BLOCK = Element(
            "//p[contains(text(), 'SIM')]/../..", "Блок 'SIM-карта'", self.page
        )  # требует дата атрибута от фронтов
        self.PHONE_NUMBER_BLOCK = Element(
            "//p[contains(text(), 'Телефонный номер')]/../../..", "Блок 'Телефонный номер (мобильный)'", self.page
        )  # требует дата атрибута от фронтов
        self.PHONE_NUMBER = Element(
            "(//p[contains(text(), 'Телефонный номер')]/../.. //p)[4]", "Номер телефона", self.page
        )
        self.MENU_PHONE_NUMBER_BTN = Element(
            "//p[contains(text(), 'Телефонный номер')]/../../.. //button", "", self.page
        )
        self.REPLACE_BTN = Element("[data-menu-id*=replace]", "Кнопка 'Заменить'", self.page)


class ReplaceResource(DynamicForms):
    """Форма Замена ресурса"""

    def __init__(self, page: Page):
        super().__init__(page)

        self.REPLACE_RESOURCE_FORM = Element(
            "(//*[@class='ant-drawer-content-wrapper'])[2]", "Форма 'Замена ресурса'", self.page
        )
        self.SUBSCRIBER = Element(
            "(//*[@class='ant-drawer-content-wrapper'])[2] //*[@class='ant-select-selection-item']", "Абонент", self.page
        )
        self.TITLE_PHONE_NUMBER = Element("label[for=phoneNumber]", "Заголовок 'Номер телефона'", self.page)
        self.PHONE_NUMBER = Element("//label[@for='phoneNumber']/../.. //input", "Номер телефона", self.page)
        self.PHONE_NUMBER_HELP = Element("#phoneNumber_help", "Подсказка для поля 'Номер телефона'", self.page)
        self.CHOICE_PHONE_NUMBER_BTN = Element(
            "//label[@for='phoneNumber']/../.. //*[@class='ant-input-suffix']",
            "Кнопка выбора номера телефона",
            self.page,
        )
        self.INFORMATION_MESSAGE = Element(
            "(//*[@class='ant-drawer-content-wrapper'])[2] //p", "Информационное сообщение", self.page
        )
        self.TITLE_CONTACT_PERSON = Element(
            "label[for=additionalInfo_contactPerson]", "Заголовок 'Контактное лицо'", self.page
        )
        self.TITLE_EMAIL = Element("label[for=additionalInfo_email]", "Заголовок 'E-mail'", self.page)
        self.TITLE_CONTACT_PHONE = Element("label[for=additionalInfo_phone]", "Заголовок 'Телефон для связи'", self.page)
        self.DO_REPLACE_BTN = Element(
            "((//*[@class='ant-drawer-content-wrapper'])[2] //button)[3]", "Кнопка 'Выполнить замену'", self.page
        )

        # CHOICE_NUMBER_FORM
        self.REPLACE_PHONE_NUMBER_FORM = Element(
            "(//*[@class='ant-drawer-content-wrapper'])[3]", "Форма замены номера телефона", self.page
        )
        self.FIND_NUMBER_INPUT = Element(
            "(//*[@class='ant-drawer-content-wrapper'])[3] //input", "Поле поиска номера телефона", self.page
        )
        self.ALLOWED_NUMBERS = ElementsList("[data-row-key]", "Доступные для замены номера", self.page)
        self.EMPTY_ALLOWED_NUMBERS_LIST = Element(
            ".platform-empty-box-container", "Пустой список доступных номеров", self.page
        )

    def check_required_fields(self) -> None:
        required_class = re.compile(r".*ant-form-item-required.*")
        self.TITLE_PHONE_NUMBER.to_have_class(required_class)
        self.TITLE_CONTACT_PERSON.not_to_have_class(required_class)
        self.TITLE_EMAIL.not_to_have_class(required_class)
        self.TITLE_CONTACT_PHONE.not_to_have_class(required_class)


class CancelPaymentForm(DynamicForms):
    """Форма Аннулирование платежа"""

    def __init__(self, page: Page):
        super().__init__(page)

        self.SUBTITLE = Element(
            "//div[contains(@class, 'ant-drawer-title')]//h3//following-sibling::p",
            "Информационный подзаголовок формы",
            self.page,
        )
        self.CANCEL_INFO_MESSAGE = Element(
            "//form/parent::div//div[2]/p", "Информационное сообщение 'Аннулирование платежа'", self.page
        )
        self.CANCEL_REASON_INPUT_FROM_REGISTRY = Element("#comment", "Причина 'Аннулирование платежа'", self.page)
        self.CANCEL_REASON_INPUT = Element("#cancellationReason", "Причина 'Аннулирование платежа'", self.page)
        self.CANCEL_OPERATION_BTN = Element("#_accept-button", "Кнопка 'Аннулировать'", self.page)
        self.CANCEL_BTN = Element("#_cancel-button", "Кнопка 'Отмена'", self.page)


class CreatePaymentForm(DynamicForms):
    """Форма Создания платежа"""

    def __init__(self, page: Page):
        super().__init__(page)

        self.SET_AMOUNT = Element("input[id='amount']", "Сумма платежа", self.page)
        self.PAYMENT_POINT = Select("input[id='paymentPointId']", "Выбор кассы", self.page)


class AddOptionsForm(DynamicForms):
    """Форма Добавления опций"""

    def __init__(self, page: Page):
        super().__init__(page)

        self.SEARCH_OPTIONS_FLD = Element('input[id="productOfferingName"]', "Поле поиска опций", self.page)
        self.SEARCH_BTN = Element(
            "(//*[contains(@class, 'ant-form-vertical')] //button)[1]", "Кнопка 'Найти'", self.page
        )
        self.SHOW_ONLY_CHOSEN_BTN = Element(
            '[class="ant-switch-handle"]', "Кнопка 'Показать только выбранные'", self.page
        )
        self.OPTIONS_NAME = ElementsList(
            "//div[contains(@class, 'ant-card-head-title')]/h4", "Доп. опции названия", self.page
        )
        self.CHOSE_OPTION_BTN = ElementsList(
            "//div[contains(@class, 'ant-card-body')]/div[2]/div[3]/button", "Кнопка выбора опции", self.page
        )
