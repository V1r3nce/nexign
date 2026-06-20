import re
from datetime import datetime
from typing import Any, Union

import allure

from common.helpers.data_generator import generate_random_number
from common.helpers.string_helper import check_that_date_later
from common.helpers.time_helpers import delay
from models.client import EntrepreneurClient, IndividualClient, OrganizationClient
from pages.locators.base_elements import BaseElements
from pages.ui_elements import (
    Autocomplete,
    DatePicker,
    Dropdown,
    Element,
    ElementsList,
    RadioOrCheckboxBlock,
    Select,
    SelectDifferentItemTextPath,
    SelectDifferentRoot,
    VirtualSelect,
)


class DynamicElements(BaseElements):
    """На разных страницах/формах присутствуют элементы идентичные по бизнес логике.
    Например, как номер телефона. Он может присутствовать и при создании карточки клиента,
    редактировании, просмотре и т.д. атрибут id отличается только префиксом. По этому такие элементы,
    имеют универсальный селектор для их нахождения."""

    def __init__(self) -> None:
        super().__init__()
        self.SAVE_BTN = Element(
            "(//button[@id='save'] | //div[contains(@class, 'bottom-toolbar')]//div[not(@data-item-key)]/button[@type='submit'])[last()]",
            "Сохранить",
        )
        self.ACCOUNT_NUM = Element("input[id*='accountNumber']", "Номер ЛС")
        self.PAYMENT_TYPE = Select("input[id*='ratingType']", "Тип оплаты ЛС")
        self.SUBSCRIPTION_ID = Element("input[id*='subscriptionIdentification']", "Абонент")
        self.CONTRACT_NUM = Element("input[id*='agreementNumber']", "Номер договора")
        self.PROPRIETARY_FORM = Select("input[id*='proprietaryForm']", "Организационно-правовая форма")
        self.INN = Element("input[id*='create'][id*='taxIdentificationNumber']", "ИНН")
        self.KPP = Element("input[id*='registrationReasonCode']", "КПП")
        self.SNILS = Element("input[id*='create_INILA']", "СНИЛС")
        self.CUSTOMER_TYPE = "input[id*='customerTypes']"
        self.CUSTOMER_NAME = Element("input[id*='create_customerName']", "Имя клиента")
        self.ID_DOCUMENT_SERIAL = "input[id*='identificationDocumentSeries']"
        self.ID_DOCUMENT_NUM = "input[id*='identificationDocumentNumber']"
        self.DOCUMENT_SERIAL = Element("input[id*='documentSeries']", "Серия документа")
        self.DOCUMENT_NUM = Element("input[id*='documentNumber']", "Номер документа")
        self.NATIONALITY = Select("input[id*='nationality']", "Страна регистрации")
        self.SPEAKING_LANGUAGE = Select("input[id*='speakingLanguage']", "Язык общения")
        self.RESIDENT = Element("input[id*='isResident']", "Резидент")
        self.BUSINESS_ACTIVITY = Select("input[id*='businessActivity']", "Экономическая деятельность")
        self.NOTE = Element("[id*=create][id$=note]", "Комментарий")
        self.REGISTRATION_ADDRESS = Autocomplete("input[id*='registrationAddress']", "Адрес регистрации")
        self.REGISTRATION_ADDRESS_CROSS = Element(
            "//input[contains(@id, 'registrationAddress')]/parent::span//input[contains(@id, 'registrationAddress')]/parent::span/span/button",
            "Кнопка очистки 'Адрес регистрации'",
        )
        self.REPUTATION = Element("input[id*='reputation']", "Деловая репутация")
        self.OKPO = Element("input[id*='RNNBO']", "ОКПО")
        self.OKATO = Element("input[id*='ARCPS']", "ОКАТО")
        self.OKVED = Element("input[id*='economicActivities']", "ОКВЭД")
        self.OGRN = Element("input[id*=create][id$=PSRN]", "ОГРН")
        self.PUBLIC_PERSON_CHECKBOX = Element("input[id*='publicOfficial']", "Публичное лицо")
        self.BIRTH_PLACE = Element("input[id*='birthPlace']", "Место рождения")
        self.BIRTH_DATE = DatePicker("input[id*='birthDate']", "Дата рождения")
        self.GENDER = Select("input[id*='gender']", "Пол")
        self.DOCUMENT_TYPE = Select("input[id*='documentType']", "Тип документа")
        self.DOCUMENT_DATE = DatePicker("input[id*='documentDateOfIssue']", "Дата выдачи")
        self.DOCUMENT_PROVIDE_BY = Element("input[id*='documentProvidedByOrganization']", "Кем выдан")
        self.DOCUMENT_DIVISION_CODE = Element("input[id*='documentDivisionCode']", "Код подразделения")
        self.DOCUMENT_VALID_DATE = DatePicker("input[id*='documentValidFor']", "Дата действия документа")
        self.REASON_TYPE = Select("input[id*='reasonType']", "Тип причины")
        self.PRIORITY = Select("#priority", "Приоритет")
        self.POTENTIAL = Select("#potential", "Потенциал")
        self.OPERATOR_AGENT_FIO = Select("#agreement-card-create_signingUser", "Поле 'ФИО' представителя оператора")
        self.OPERATOR_BANK_DETAILS = Select("input[id*='create_bankOperator']", "Поле оператора 'Банк и расчетный счет")
        self.CLIENT_BANK_DETAILS_CHBX = Element(
            "//*[@id='agreement-card-create_useExistingBankData']", "Чек-бокс 'Банковские реквизиты клиента'"
        )
        self.CLIENT_BANK_CURRENT_ACCOUNT = Element("input[id*='create_bankAccountNumber']", "Расчетный счет клиента")
        self.CLIENT_BANK = Select("#agreement-card-create_bankAccount", "Банк клиента")
        self.CREATE_BTN = Element("#create", "Кнопка 'Создать")
        self.DEADLINE = Select("#CF_DEDLINE", "Планируемый срок решения")

        self.REGISTRATION_DOCUMENT = Element("input[id*=PSRN]", "Документ о регистрации")
        self.REGISTRATION_DATE = DatePicker("input[id*='registrationDate']", "Дата регистрации")
        self.REGISTRATION_NUM = Element(
            "input[id*='foreignRegistrationNumber']", "Регистрационный номер в стране регистрации"
        )
        self.CONTACT_PHONE = Element(
            "(//*[contains(@class, 'platform-phone-input')] //*[contains(@class, 'input-base')] //input)[last()]",
            "Номер телефона",
        )
        self.CONTACT_PHONE_CODE = Element(
            "[class$=platform-phone-input] [class*=input-code] input", "Код номера телефона"
        )
        self.PHONE_TYPE = VirtualSelect("div[class*=select-selector]:has(input[id*=Phone][id$=Type])", "Тип телефона")
        self.CONTACT_PERSON = Element("#contactPersonName", "Имя Контактного Лица")
        self.EMAIL_ADD_BTN = Element(
            "//div[contains(@class,'drawer-open')] //span[contains(text(), 'Email')]",
            "Кнопка Добавить Email",
        )
        self.EMAIL_INPUT = Element("input[id*=contactEmail]", "Почта")
        self.TAX_SCHEME = Select("input[id*='taxScheme']", "Схема налогообложения")
        self.NEXT_BTN = Element("div[class*='drawer-footer'] [data-icon=KeyboardArrowRight]", "Кнопка 'Далее'")
        self.ADDRESS_INPUT = Element("#address", "Поле 'Адрес'")
        self.PERSONAL_ACCOUNT_BALANCE = Element(
            "//*[contains(@class, 'platform-scrollable')] //div[2] //h3[@color='positive' or @color='negative']",
            "Баланс ЛС",
        )


class DynamicForms(DynamicElements):
    def __init__(self) -> None:
        super().__init__()
        """Общие элементы динамических форм."""
        self.ATTENTION_TEXT = Element("[class*=platform-attention-label] p", "Текст предупреждения")
        self.TITLE = Element("[class*=drawer-open] [class*=drawer-title] h3", "Заголовок формы")
        self.CROSS_BTN = Element("[class*=drawer-open]  button[aria-label='Close']", "Крестик")
        self.CANCEL_BTN = Element("#cancel", "Отменить")
        self.CLOSE_BTN = Element("#close", "Закрыть")
        self.FORWARD_BTN = Element("#forward", "Перейти")
        self.INNER_CANCEL_BTN = Element("#_cancel-button", "Внутренняя кнопка закрытия")
        self.INNER_SAVE_BTN = Element("#_save-button", "Внутренняя кнопка сохранения")
        self.INNER_ACCEPT_BTN = Element("#_accept-button", "Внутренняя кнопка 'Выбрать'")
        self.NOW_BTN = Element("a[class*=now-btn]", "Кнопка 'Сегодня'")
        self.CREATE_BTN = Element(
            "[class*=drawer-open] [class*=drawer-footer] button:not(:has(span[class*=icon]))", "Кнопка 'Создать"
        )

    @allure.step("Заполнение второй страницы создания клиента")
    def fill_second_client_creation_page(
        self,
        user_data: Union[OrganizationClient, IndividualClient, EntrepreneurClient],
        only_required_fields: bool = False,
    ) -> None:
        self.NEXT_BTN.wait_to_be_visible()
        self.NEXT_BTN.click()
        self.CONTACT_PERSON.wait_to_be_visible()
        self.CONTACT_PERSON.fill(user_data.contact_person)
        self.PHONE_TYPE.select_by_value(user_data.contact_phone_type)
        self.CONTACT_PHONE.fill(user_data.contact_phone)
        if not only_required_fields:
            self.EMAIL_ADD_BTN.wait_to_be_visible()
            self.EMAIL_ADD_BTN.click()
            self.EMAIL_INPUT.wait_to_be_visible()
            self.EMAIL_INPUT.fill(user_data.contact_email)


class IndividualCustomerCreate(DynamicForms):
    """Форма 'Создание клиента ФЛ'"""

    def __init__(self) -> None:
        super().__init__()

        self.LAST_NAME = Element("#customer-individual-create_surname", "Фамилия")
        self.FIRST_NAME = Element("#customer-individual-create_firstname", "Имя")
        self.SUR_NAME = Element("#customer-individual-create_patronymic", "Отчество")
        self.DOCUMENT_TYPE_DROPDOWN = Element("#customer-individual-create_documentType", "Тип документа")

        self.CREATE_ADDRESS_LINK = Element("#customer-individual-create_registrationAddress_list", "Добавить адрес")

        self.BIOMETRIC_CHECKBOX = Element("#customer-individual-create_biometricData", "Биометрические данные")

    @allure.step("Заполнить данные клиента ФЛ")
    def fill_data_for_individual_client(
        self,
        user_data: IndividualClient,
        only_required_fields: bool = False,
        need_second_page: bool = True,
    ) -> None:
        self.LAST_NAME.wait_to_be_visible()
        delay(1, "Поля видны но идет подгрузка, данные не вводятся. Требуется ожидание")
        self.LAST_NAME.fill(user_data.sur_name)
        self.FIRST_NAME.fill(user_data.first_name)
        self.SUR_NAME.fill(user_data.patronymic)
        self.GENDER.select_by_value(user_data.gender)
        self.DOCUMENT_TYPE.select_by_value(user_data.document_type)
        delay(1, "Пропадает информация по документам")
        self.DOCUMENT_SERIAL.click()
        self.DOCUMENT_SERIAL.fill(user_data.document_serial)
        self.DOCUMENT_NUM.fill(user_data.document_num)
        if not only_required_fields:
            self.DOCUMENT_PROVIDE_BY.fill(user_data.document_provide_by)
            self.DOCUMENT_DIVISION_CODE.fill(user_data.document_division_code)
            self.DOCUMENT_DATE.type(user_data.document_date, delay=100)
            self.DOCUMENT_VALID_DATE.type(user_data.document_valid_date, delay=100)
        self.BIRTH_DATE.fill(user_data.birth_date, delay=100)
        delay(1.5, reason="Без ожидания не сохраняется дата рождения")
        if not only_required_fields:
            self.BIRTH_PLACE.fill(user_data.birth_place)
        self.REGISTRATION_ADDRESS.select_by_value(user_data.registration_address, include_last_symbol=True)
        if not only_required_fields:
            self.INN.fill(user_data.inn)
            self.SNILS.fill(user_data.snils)

        self.TAX_SCHEME.select_by_value(user_data.tax_scheme)
        if need_second_page:
            self.fill_second_client_creation_page(user_data)


class CreateEntrepreneur(IndividualCustomerCreate):
    """Форма 'Создание клиента ИП'"""

    def __init__(self) -> None:
        super().__init__()

        self.LAST_NAME = Element("#customer-entrepreneur-create_surname", "Фамилия")
        self.FIRST_NAME = Element("#customer-entrepreneur-create_firstname", "Имя")
        self.SUR_NAME = Element("#customer-entrepreneur-create_patronymic", "Отчество")
        self.DOCUMENT_TYPE_DROPDOWN = Element("#customer-entrepreneur-create_documentType", "Тип документа")

        self.CREATE_ADDRESS_LINK = Element("#customer-entrepreneur-create_registrationAddress_list", "Добавить адрес")

        self.BIOMETRIC_CHECKBOX = Element("#customer-entrepreneur-create_biometricData", "Биометрические данные")
        self.CONTACT_EMAIL = Element("#customer-entrepreneur-create_contactEmail", "Почта")

        self.SAVE_BTN = Element(
            "//form[@id='customer-entrepreneur-create']//div[not(@data-item-key)]/button[@type='submit']",
            "Сохранить",
        )

    @allure.step("Заполнить данные клиента ИП")
    def fill_data_for_entrepreneur_client(
        self, user_data: EntrepreneurClient, only_required_fields: bool = False, need_second_page: bool = True
    ) -> None:
        self.INN.wait_to_be_visible()
        delay(1, "Поля видны но идет подгрузка, данные не вводятся. Требуется ожидание")
        if not only_required_fields:
            self.PROPRIETARY_FORM.select_by_value(user_data.proprietary_form)
        if not only_required_fields:
            self.REGISTRATION_DOCUMENT.fill(user_data.registration_document)
        if not only_required_fields:
            self.REGISTRATION_DATE.type(user_data.registration_date)
        if not only_required_fields:
            self.SNILS.fill(user_data.snils)
        if not only_required_fields:
            self.OKPO.fill(user_data.okpo)
        if not only_required_fields:
            self.OKATO.fill(user_data.okato)
        if not only_required_fields:
            self.OKVED.fill(user_data.okved)
        if not only_required_fields:
            self.OGRN.fill(user_data.ogrn)
        self.INN.fill(user_data.inn)
        self.LAST_NAME.fill(user_data.sur_name)
        self.FIRST_NAME.fill(user_data.first_name)
        if not only_required_fields:
            self.SUR_NAME.fill(user_data.patronymic)
        self.GENDER.select_by_value(user_data.gender)
        self.DOCUMENT_TYPE.select_by_value(user_data.document_type)
        if not only_required_fields:
            self.DOCUMENT_SERIAL.fill(user_data.document_serial)
        self.DOCUMENT_NUM.fill(user_data.document_num)
        if not only_required_fields:
            self.DOCUMENT_PROVIDE_BY.fill(user_data.document_provide_by)
        if not only_required_fields:
            self.DOCUMENT_DIVISION_CODE.fill(user_data.document_division_code)
        if not only_required_fields:
            self.DOCUMENT_DATE.type(user_data.document_date, delay=100)
        if not only_required_fields:
            self.DOCUMENT_VALID_DATE.fill(user_data.document_valid_date)
            delay(0.5, reason="Без ожидания не сохраняется дата, до которой действует документ")
        self.BIRTH_DATE.type(user_data.birth_date, delay=100)
        if not only_required_fields:
            self.BIRTH_PLACE.fill(user_data.birth_place)
        delay(0.5, reason="Без ожидания не сохраняется дата рождения")
        self.NATIONALITY.select_by_value(user_data.nationality)
        self.SPEAKING_LANGUAGE.select_by_value(user_data.speaking_language)
        self.REGISTRATION_ADDRESS.select_by_value(user_data.registration_address, include_last_symbol=True)
        if not only_required_fields:
            self.REPUTATION.fill(user_data.reputation)
        if user_data.is_public_bool or user_data.is_public == "Да":
            self.PUBLIC_PERSON_CHECKBOX.click()
        if not only_required_fields:
            self.BUSINESS_ACTIVITY.select_by_value(user_data.business_activity)
        if not only_required_fields:
            self.NOTE.fill(user_data.note)
        self.TAX_SCHEME.select_by_value(user_data.tax_scheme)
        if need_second_page:
            self.fill_second_client_creation_page(user_data)


class CreateOrganization(DynamicForms):
    """Форма 'Создание клиента' ЮЛ."""

    def __init__(self) -> None:
        super().__init__()
        self.CLIENT_NAME = Element("input[id*='_customerName']", "Имя Клиента")
        self.AUTHORIZATION_CODE = Element("input[id*=AuthorizationCode]", "Код авторизации")
        self.TAX_SCHEME = Select("input[id*='taxScheme']", "Схема налогооблажения")
        self.SAVE_BTN = Element(
            "(//*[contains(@class, 'drawer-open')]//div[contains(@class, 'drawer-footer')]//button)[2]",
            "Сохранить",
        )

    @allure.step("Заполнить данные клиента ЮЛ")
    def fill_data_for_organization_client(
        self,
        user_data: OrganizationClient,
        only_required_fields: bool = False,
        need_second_page: bool = True,
    ) -> None:
        self.INN.wait_to_be_visible()
        delay(1, "Поля видны но идет подгрузка, данные не вводятся. Требуется ожидание")
        self.PROPRIETARY_FORM.select_by_value(user_data.proprietary_form)
        if not only_required_fields:
            self.INN.fill(user_data.inn)
            self.KPP.fill(user_data.kpp)
        self.CLIENT_NAME.fill(user_data.customer_name)
        self.OGRN.fill(user_data.ogrn)
        self.REGISTRATION_ADDRESS.select_by_value(user_data.registration_address, include_last_symbol=True)
        self.AUTHORIZATION_CODE.fill(str(user_data.auth_code))
        self.SPEAKING_LANGUAGE.select_by_value(user_data.speaking_language)
        self.TAX_SCHEME.select_by_value(user_data.tax_scheme)
        if not only_required_fields:
            self.NOTE.fill(user_data.note)
        if need_second_page:
            self.fill_second_client_creation_page(user_data)


class AddressCreate(DynamicForms):
    """Форма 'Создание нового адреса'."""

    def __init__(self) -> None:
        super().__init__()

        self.TITLE = Element("//h3[contains(text(), 'Создание нового адреса')]", "Заголовок формы")
        self.ADDED_CARD = ElementsList(
            "form [class*=card-head-title]", "Блоки с выбранным типом и наименованием адресного объекта"
        )
        self.ADDED_CARD_EDIT_BTN = ElementsList("[class*=card-extra] button:nth-child(1)", "Кнопки 'Редактировать'")
        self.ADDED_CARD_DELETE_BTN = ElementsList("[class*=card-extra] button:nth-child(2)", "Кнопки 'Удалить'")
        self.ATTRIBUTE_HEADER = ElementsList(
            "[id*='create-address-form'] [class*=collapse-item]", "Панель с кнопкой 'Атрибуты'"
        )
        self.ATTRIBUTE_FIELDS_BLOCK = ElementsList(
            "//div[contains(@class, 'collapse-content')]//div[contains(@class, 'form-item-control-input-content')]",
            "Блок полей атрибутов",
        )
        self.ATTRIBUTE_FIELDS = ElementsList(
            "//div[contains(@class, 'collapse-content')]//div[contains(@class, 'form-item-control-input-content')]//input",
            "Поля атрибутов",
        )

        self.OPTION_ITEMS = ElementsList(
            "[id*='create-address-form'] .ant-select-item-option", "Варианты выбора в списке"
        )
        self.OBJECT_TYPE = Select("[id*='_select-elementCode']", "Поле 'Выберите адресный объект'")
        self.OBJECT_NAME_AUTOCOMPLETE = Autocomplete(
            "[class*=form-item-row]:has(label[title='Наименование']) input[id*='rc_select']:not([readonly])",
            "Поле 'Наименование'",
        )
        self.OBJECT_NUM = Element(
            "[class*=form-item-row]:has(label[title='Номер']) input[id*='rc_select']:not([readonly])",
            "Поле 'Номер'",
        )
        self.OBJECT_ADDITIONAL_NUM = Element(
            "[class*=form-item-row]:has(label[title='Дополнительный номер']) input[id*='rc_select']",
            "Поле 'Дополнительный номер'",
        )
        self.OBJECT_EXTRA_NUM = Element(
            "[class*=form-item-row]:has(label[title='Добавочный номер']) input[id*='rc_select']",
            "Поле 'Добавочный номер'",
        )
        self.OBJECT_GAR = ElementsList(
            "[class*=form-item-row]:has(label[title='Уникальный номер ГАР']) input[id*='rc_select']",
            "Поле 'Уникальный номер ГАР'",
        )
        self.OBJECT_MAIL_INDEX = Element(
            "[class*=form-item-row]:has(label[title='Почтовый индекс']) input[id*='rc_select']",
            "Поле 'Почтовый индекс'",
        )

        self.REGION_TYPE_DROPDOWN = Select("input[id*='regionType']", "Поле ввода 'Тип региона'")
        self.CITY_TYPE_DROPDOWN = Select("input[id*='cityType']", "Поле ввода 'Тип города'")
        self.STREET_TYPE_DROPDOWN = Autocomplete("input[id*='form_street_streetType']", "Поле ввода 'Тип улицы'")
        self.HOUSE_TYPE_DROPDOWN = Autocomplete("input[id*='houseType']", "Поле ввода 'Тип дома'")
        self.APARTMENT_TYPE_DROPDOWN = Select("input[id*='apartmentType']", "Поле ввода 'Тип жилого помещения'")
        self.ADDITIONAL_HOUSE_TYPE_DROPDOWN = Autocomplete(
            "input[id*='house_additionalType']", "Поле ввода 'Дополнительный тип дома'"
        )
        self.EXTRA_HOUSE_TYPE_DROPDOWN = Autocomplete("input[id*='house_extraType']", "Поле ввода 'Добавочный тип дома'")
        self.APPLY_BTN = Element("[id*='save-button']", "Кнопка 'Применить'")
        self.ADD_ADDRESS_OBJECT_BTN = Element("[id*='add-address-element-button']", "Кнопка 'Добавить адресный объект'")
        self.CREATE_BTN = Element("[id*='create-address-modal_accept-button']", "Кнопка 'Создать'")
        self.CANCEL_BTN = Element("[id*='create-address-modal_cancel-button']", "Кнопка 'Отмена'")


class AddressForm(DynamicForms):
    def __init__(self) -> None:
        super().__init__()

        self.TITLE = Element(
            "(//h3[contains(text(), 'Добавление адреса') or contains(text(), 'Редактирование адреса') or contains(text(), 'Редактирование адресной информации')])[last()]",
            "Заголовок формы",
        )
        self.ADDRESS_TYPE_FIELD = Select("input[id*=placeType]", "Поле ввода 'Тип адреса'")
        self.ADDRESS_INPUT = Element("input[id*=addressString]", "Поле ввода 'Адреса'")
        self.LATITUDE_INPUT = Element("input[id*=latitude]", "Поле 'Широта'")
        self.LONGITUDE_INPUT = Element("input[id*=longitude]", "Поле 'Долгота'")
        self.MAPS_LINK_INPUT = Element("input[id*=addressUrl]", "Поле ввода 'Ссылка на карту'")
        self.ADD_ADDRESS_TO_CATALOG = Element("a[href='/nbss#']", "Ссылка 'Добавить адрес в справочник'")
        self.ADDRESS_OPTION = ElementsList(
            "(//div[contains(@id, 'addressString_list')]/parent::div//div[contains(@class, 'select-item-option-content')]) [1]",
            "Варианты адреса",
        )
        self.CANCEL_BTN = Element(
            "//div[contains(@class, 'bottom-toolbar-area')]//div[contains(@class, 'platform-toolbar-item') and not(@data-item-key)][1]/button",
            "Кнопка 'Отмена'",
        )


class AddAddress(AddressForm):
    """Форма 'Добавление нового адреса'."""

    def __init__(self) -> None:
        super().__init__()

        self.TITLE = Element("//h3[contains(text(), 'Добавление адреса')]", "Заголовок формы")
        self.ADDRESS_TYPE_OPTIONS = ElementsList(".ant-select-item-option", "Выбор 'Тип адреса'")
        self.ERROR_MESSAGE = Element("[class*=attention-label] p[data-name=paragraphInfo]", "Информационное поле")
        self.ADDRESS_FIELD = Autocomplete("#place-add_addressString", "Поле 'Адрес'")
        self.ADDRESS_OPTION = ElementsList(
            "(//div[contains(@id, 'addressString_list')]/parent::div//div[contains(@class, 'select-item-option-content')]) [1]",
            "Варианты адреса",
        )
        self.CANCEL_BTN = Element(
            "//div[contains(@class, 'bottom-toolbar-area')]//div[contains(@class, 'platform-toolbar-item') and not(@data-item-key)][1]/button",
            "Кнопка 'Отмена'",
        )

    @allure.step("Добавление связанного адреса")
    def add_new_related_address(self, new_address: str) -> None:
        """Добавляет новый адрес через форму создания связанного адреса.

        :param new_address: Полный адрес для добавления в формате "страна, город, улица, дом"
        """
        self.TITLE.to_contain_text("Добавление адреса")
        self.ADDRESS_INPUT.fill(new_address)
        self.ADDRESS_OPTION.wait_elements_visible(0)
        self.ADDRESS_OPTION[0].to_contain_text(new_address)
        self.ADDRESS_OPTION[0].click()
        self.SAVE_BTN.wait_to_be_enabled(timeout=15000)
        self.SAVE_BTN.click()


class EditAddress(AddressForm):
    """Форма 'Редактирование адреса Клиента'"""

    def __init__(self) -> None:
        super().__init__()

        self.TITLE = Element("//h3[contains(text(), 'Редактирование адреса')]", "Заголовок формы")


class EditAddressInfo(DynamicForms):
    """Форма 'Редактирование адресной информации'"""

    def __init__(self) -> None:
        super().__init__()

        self.ADD_BUTTON = Element(
            "//*[contains(@class, 'drawer-content')]//div[not(@data-item-key)]/button[@title='Добавить']",
            "Кнопка 'Добавить'",
        )
        self.TABLE_LINE = ElementsList(
            "[class*=drawer-content][role=dialog] [class$=table-tbody] div[data-row-key]", "Строки таблицы"
        )
        self.TABLE_ADDRESS_TYPES = ElementsList(
            "[class*=drawer-content][role=dialog] [class$=table-tbody] div[data-row-key] > div:nth-child(1)",
            "Строки Тип адреса",
        )
        self.TABLE_ADDRESSES = ElementsList(
            "[class*=drawer-content][role=dialog] [class$=table-tbody] div[data-row-key] > div:nth-child(2)",
            "Строки Адреса",
        )
        self.TABLE_MAP_CELLS = ElementsList(
            "[class*=drawer-content][role=dialog] [class$=table-tbody] div[data-row-key]:has(button)",
            "Строки под кнопку карты",
        )
        self.TABLE_LINE_MAP_BUTTON = ElementsList(
            "[data-row-key][class*=table-row] button:has(span)",
            "Строки таблицы кнопка карты",
        )
        self.CANCEL_BTN = Element("#_cancel-button", "Кнопка 'Закрыть'")
        self.TYPE_SORT_BTN = Element(
            "//span[contains(text(), 'Тип')]/parent::div[contains(@class, 'sorters')]",
            "Кнопка сортировки 'Тип'",
        )
        self.EDIT_ADDRESS = Element("button[|title='Изменить адрес'],[|title='Edit address']", "Кнопка 'Изменить адрес'")
        self.DELETE_ADDRESS = Element(
            "button[|title='Удалить адрес'],[|title='Delete address']", "Кнопка 'Удалить адрес'"
        )
        self.SETTING_BTN = Element("[class*=drawer-right] button[class*=dropdown-trigger]", "Кнопка 'Настройка колонок'")
        self.SETTING_OPTIONS = ElementsList("input[class*=checkbox-input]", "Чекбоксы 'Настройка колонок'")


class RequestCreate(DynamicForms):
    """Форма 'Создание заявки'."""

    def __init__(self) -> None:
        super().__init__()

        self.CREATE_FORM = Element(".side-panel-content", "Форма создания заявки")
        self.TITLE = Element(".side-panel-content h3", "Заголовок форма 'Создание заявки'")
        self.CLIENT = Element(".side-panel-content a", "Выбранный клиент")
        self.SELECT_CLIENT_BTN = Dropdown(
            ".side-panel-content button:has(span[data-icon='ArrowDropDown'])", "Сменить клиента"
        )
        self.CHOOSE_AGREEMENT_BTN = Select("input[id*='saleAddAgreement']", "Поле создание договора")
        self.AGREEMENT = Select("#drAgreement", "Договор")
        self.ACCOUNT = Select("#drAgreementAccount", "Лицевой счет")
        self.CHOOSE_PRIORITY_BTN = Select("input[id*='priority']", "Поле выбора приоритета")

        self.CODE = Element("#code", "Код")
        self.TOPIC = Element("#topic", "Тема")
        self.CHOOSE_TOPIC_TITLE = Element(".ant-drawer-header-title", "Заголовок 'Выбор темы заявки'")
        self.EMAIL = Element("[class*=-col]:has([for='email']) input", "Предпочтительный email")
        self.PHONE = Element("div[class*=phone-input-base-input] input", "Предпочтительный телефон")
        self.DESCRIPTION = Element("#description", "Описание")
        self.FILE_INPUT = Element("input[type='file']", "Документы")
        self.FORWARD_BTN = Element("#forward", "Кнопка 'Передать'")

        self.ACCOUNT_FIELD = Select("#rfdAcc", "Поле 'Лицевой счет'")
        self.SUBSCRIBER_FIELD = Select("#tedSubscriber", "Поле 'Абонент'")
        self.SERVICE_FIELD = Select("#tedServiceType", "Поле 'Сервис'")
        self.AMOUNT_MIN_FIELD = Element("#tedAmountMin", "Поле 'Объем в секундах'")
        self.AMOUNT_SMS_FIELD = Element("#tedAmountSms", "Поле 'объем в штуках'")
        self.AMOUNT_MB_FIELD = Element("#tedAmountMb", "Поле 'Объем в Мб'")
        self.QUEUE_FIELD = Element("#forwardInquiryForm_queue", "Поле 'Очередь'")
        self.REFUND_BALANCE = Element("#rfdRefundBalance", "Поле 'Планируемая сумма возврата'")
        self.RETURN_TYPE_FIELD = Select("#rfdReturnType", "Поле 'Цель возврата'")
        self.RETURN_PAYMENT_FIELD = Select("#rfdPayment", "Поле 'Платеж для возврата'")
        self.RETURN_PAYMENT_ELEMENT_FIELD = Element(
            "//div[contains(@class, 'platform-grid-item')][5] //*[@class='platform-filterable-component-text-to-highlight']",
            "Платеж для возврата",
        )
        self.WARNING_REFUND_FIELD = Element("#rfdWarnExceed", "Предупреждение 'Внимание'")


class ChooseRequestTopic(DynamicForms):
    """Форма 'Выбор темы заявки'"""

    def __init__(self) -> None:
        super().__init__()

        self.AGREEMENT_BTN = Element("#tpAgreementSource", "Поле Договор источник")
        self.AGREEMENT = ElementsList("//div[@title]", "Выбор договора из выпадающего списка")
        self.AGREEMENT_SELECT = Select("//input[@id='tpAgreementSource']/../..", "Селект Договор источник")

        self.CHOOSE_REQUEST_TOPIC_FORM = Element(".ant-drawer-open .ant-drawer-title", "Форма 'Выбор темы заявки'")
        self.EXPAND_BTN = ElementsList(".ant-tree-switcher_open,.ant-tree-switcher_close", "Кнопка развернуть список")
        self.REQUEST_TOPIC_NAME = ElementsList(".ant-tree-node-content-wrapper", "Тема заявки")
        self.ACCEPT_BTN = Element("#_accept-button", "Кнопка 'Применить'")

    def choose_topic(self, topics: list) -> None:
        for index in range(len(topics)):
            self.REQUEST_TOPIC_NAME.wait_for_text_in_all([topics[index]])
            topic_index = self.REQUEST_TOPIC_NAME.text_list.index(topics[index])
            if index == len(topics) - 1:
                self.REQUEST_TOPIC_NAME.click(topic_index)
            else:
                self.EXPAND_BTN.click(topic_index)
        self.ACCEPT_BTN.click()


class ForwardInquiryForm(DynamicForms):
    """Форма 'Передача на обработку' при оформлении заявки"""

    def __init__(self) -> None:
        super().__init__()

        self.FORWARD_FORM = Element("#forwardInquiryForm", "Форма передачи на обработку")
        self.PROCESS_FIELD = Select("#forwardInquiryForm_process", "Поле 'Шаг'")
        self.QUEUE_FIELD = Select("#forwardInquiryForm_queue", "Поле 'Очередь'")
        self.RESPONSIBLE_FIELD = Select("#forwardInquiryForm_responsible", "Поле 'Ответственный'")
        self.DUE_DATE_FIELD = DatePicker("#forwardInquiryForm_dueDate", "Поле 'Обработать до'")
        self.COMMENT_FIELD = Element("#forwardInquiryForm_comment", "Поле 'Сопроводительная записка'")
        self.FORWARD_BTN = Element("[class*=drawer-open] #_accept-button", "Кнопка 'Передать'")
        self.ERROR_FIELD = Element("//div[contains(@class, '-form-item-explain-error')]", "Сообщение об ошибке")
        self.REASON_TERMINATE_FIELD = Select(
            "//input[@id='agtrmTermReason']/ancestor::span[1]", "Поле 'Причина расторжения'"
        )
        self.TERMINATE_CONTRACT_FIELD = Select(
            "//input[@id='agtrmTermAgreement']/ancestor::span[1]", "Поле 'Расторгаемый договор'"
        )
        self.SAVE_BTN = Element("#save", "Кнопка 'Сохранить'")

    def check_form_fields(self) -> None:
        self.PROCESS_FIELD.check_attribute_by_value("aria-required", "true")
        self.QUEUE_FIELD.check_attribute_by_value("aria-required", "true")
        self.RESPONSIBLE_FIELD.check_attribute_not_contain_value("aria-required", "true")
        self.DUE_DATE_FIELD.check_attribute_not_contain_value("aria-required", "true")
        self.COMMENT_FIELD.check_attribute_not_contain_value("aria-required", "true")
        self.RESPONSIBLE_FIELD.not_to_be_enabled()
        self.DUE_DATE_FIELD.wait_to_be_enabled()


class LinkingToInquiresForm(DynamicForms):
    """Форма 'Связывание с заявкой'"""

    def __init__(self) -> None:
        super().__init__()

        self.LINKING_TO_INQUIRIES_FORM = Element(
            "[class*=-drawer-content-wrapper]:not([class*=hidden])", "Форма 'Связывание с заявкой'"
        )
        self.TITLE = Element("[class*=-drawer-title] h4", "Заголовок формы")
        self.CLEAR_FILTER_BTN = Element(
            "(//*[contains(@class, '-drawer-content')] //*[contains(@class, '-drawer-body')] //button)[2]",
            "Кнопка 'Очистить все фильтры'",
        )
        self.INQUIRY = ElementsList("[class*=-drawer-content] [class*=table-tbody] tr", "Заявка")
        self.INQUIRY_NUMBER = ElementsList(
            "[class*=-drawer-content] [class*=table-tbody] td:nth-child(1) a", "Номер заявки"
        )
        self.INQUIRY_TOPIC = ElementsList("[class*=-drawer-content] [class*=table-tbody] td:nth-child(2)", "Тема заявки")
        self.IMPROVE_BALANCE_CHECKBOX = Element(
            "[class*=-drawer-content] [class*='-checkbox ']", "Чекбокс 'Улучшить баланс'"
        )
        self.CANCEL_BTN = Element(
            "(//*[contains(@class, '-drawer-content')] //*[contains(@class, '-drawer-footer')] //button)[1]",
            "Кнопка 'Отмена'",
        )
        self.LINKED_BTN = Element(
            "(//*[contains(@class, '-drawer-content')] //*[contains(@class, '-drawer-footer')] //button)[2]",
            "Кнопка 'Связать'",
        )

    @allure.step("Выбрать заявку {inquiry_id}")
    def choice_inquiry(self, inquiry_id: int) -> None:
        self.INQUIRY_NUMBER.wait_for_text_in_all([str(inquiry_id)])
        inquiry_index = self.INQUIRY_NUMBER.text_list.index(str(inquiry_id))
        self.INQUIRY_TOPIC.click(inquiry_index)


class LinkedInquiriesForm(DynamicForms):
    """Форма 'Связанные заявки'"""

    def __init__(self) -> None:
        super().__init__()

        self.LINKED_INQUIRIES_FORM = Element(
            "[class*=-drawer-content-wrapper]:not([class*=hidden])", "Форма 'Связанные заявки'"
        )
        self.TITLE = Element("[class*=-drawer-content-wrapper]:not([class*=hidden]) h4", "Заголовок формы")
        self.INQUIRY = ElementsList(
            "[class*=-drawer-content-wrapper]:not([class*=hidden]) [class*=table-tbody] tr", "Заявка"
        )
        self.INQUIRY_NUMBER = ElementsList(
            "[class*=-drawer-content-wrapper]:not([class*=hidden]) [class*=table-tbody] td:nth-child(1) a",
            "Номер заявки",
        )
        self.INQUIRY_TOPIC = ElementsList(
            "[class*=-drawer-content-wrapper]:not([class*=hidden]) [class*=table-tbody] td:nth-child(2)",
            "Тема заявки",
        )
        self.CREATE_DATE = ElementsList(
            "[class*=-drawer-content-wrapper]:not([class*=hidden]) [class*=table-tbody] td:nth-child(3)",
            "Дата создания",
        )
        self.RESPONSIBLE = ElementsList(
            "[class*=-drawer-content-wrapper]:not([class*=hidden]) [class*=table-tbody] td:nth-child(4)",
            "Ответственный",
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

    def __init__(self) -> None:
        super().__init__()

        self.CONTRACT_CATEGORY = Select("#agreement-card-create_category", "Выбор категории договора")
        self.AGREEMENT_TYPE = Select("#agreement-card-create_agreementType", "Выбор типа договора")
        self.SECRET_KEY = Element("#agreement-card-create_secretKey", "Кодовое слово")
        self.CONTRACT_SIGN_DATE = DatePicker("#agreement-card-create_signingDate", "Дата подписания договора")
        self.INDEFINITE_CHECKBOX = Element("#agreement-card-create_isIndefinitely", "Неопределенный срок действия")
        self.EXPIRATION_DATE = DatePicker("#expireDate_control", "Дата расторжения договора")
        self.CLIENT_SINGER = Select("#agreement-card-create_agreementSigner", "ФИО представителя клиента")
        self.OPERATOR_FIO = Select("#agreement-card-create_signingUser", "ФИО представителя оператора")
        self.SINGER_PROXY_NUM = Element("#agreement-card-create_customerSignerProxyNumber", "Номер доверенности")
        self.PROXY_DATE = DatePicker("#customerSignerProxyStartDate_control", "Дата доверенности")
        self.USE_EXISTING_BANK_CHECKBOX = Element("[id*='useExistingBankData']", "Выбрать существующие реквизиты")
        self.CLIENT_BANK_DATA = Select("#agreement-card-create_existingBankData", "Банк и расчетный счет клиента")
        self.OPERATOR_BANK_DATA = Select("#agreement-card-create_bankOperator", "Банк и расчетный счет оператора")


class ClientChoice(DynamicForms):
    """Форма 'Выбор клиента'."""

    def __init__(self) -> None:
        super().__init__()

        self.ACCOUNT_NUM = Element("#search-customer_accountNumber", "Номер ЛС")
        self.SUBSCRIPTION_ID = Element("#search-customer_subscriptionIdentification", "Абонент")
        self.CONTRACT_NUM = Element("#search-customer_agreementNumber", "Номер договора")
        self.KPP = Element("#search-customer_registrationReasonCode", "КПП")
        self.INN = Element("#search-customer_taxIdentificationNumber", "ИНН")
        self.CUSTOMER_NAME = Element("#search-customer_customerName", "Наименование клиента")
        self.RESET_BTN = Element("#resetButton", "Кнопка 'Сбросить'")
        self.FIND_BTN = Element(
            "//form[@id='search-customer']//div[not(@data-item-key)]/button[@type='submit']", "Кнопка 'Найти'"
        )

        self.FOUNDED_CUSTOMER = ElementsList(
            "#search-customer-table [class*=-table-tbody] > [class*=-table-row]", "Клиенты"
        )

        # FOUNDED_CUSTOMER
        self.FOUNDED_FIO = ElementsList(
            "#search-customer-table [class*=-table-tbody] > [class*=-table-row] div[class*=table-cell]:nth-child(1)",
            "ФИО клиента",
        )
        self.FOUNDED_CUSTOMER_TYPE = ElementsList(
            "#search-customer-table [class*=-table-tbody] > [class*=-table-row] div[class*=table-cell]:nth-child(2)",
            "Тип клиента",
        )
        self.FOUNDED_CUSTOMER_STATUS = ElementsList(
            "#search-customer-table [class*=-table-tbody] > [class*=-table-row] div[class*=table-cell]:nth-child(3)",
            "Статус клиента",
        )
        self.FOUNDED_DOCUMENT_NUM = ElementsList(
            "#search-customer-table [class*=-table-tbody] > [class*=-table-row] div[class*=table-cell]:nth-child(4)",
            "Номер документа",
        )
        self.FOUNDED_CONTRACT = ElementsList(
            "#search-customer-table [class*=-table-tbody] > [class*=-table-row] div[class*=table-cell]:nth-child(5)",
            "Договор",
        )

        # на случай, если открытых форм несколько и кнопки дублируются (например сохранить или закрыть)
        self.INNER_ACCEPT_BTN = ElementsList("#_accept-button", "Внутренняя кнопка 'Выбрать'")
        self.INNER_CANCEL_BTN = ElementsList("#_cancel-button", "Внутренняя кнопка закрытия")


class CreateSalesAndServiceManagement(RequestCreate):
    """Форма 'Создание продажи и управления услугами'"""

    def __init__(self) -> None:
        super().__init__()

        self.CONTACT_PERSON = Element("#inqrLinkedPerson", "Контактное лицо")
        self.SELECTED_AGREEMENT = Select("#saleAgreement", "Поле 'Договор'")
        self.FILL_AGREEMENT_INPUT = Element("#saleAgreement", "Заполненное поле 'Договор'")
        self.SALE_ACCOUNT = Select("#saleAccount", "Поле 'Лицевой счет'")
        self.ADD_SALE_TYPE = Select("#saleAddAgreement,#saleAddAgreementAdd", "Создание Договора")
        self.NEED_SPD = Select("#needSPD", "Поле 'Заказ на комплекты РПД'")
        self.DELIVERY_TYPE = Select("[id*=deliveryTypeSPD]", "Поле 'Способ доставки РПД'")
        self.EMAIL_FOR_DELIVERY = Element("#emailForSendSPD", "Поле 'Email для доставки РПД'")
        self.COURIER = Select("#couriersTypeSPD", "Поле 'Курьер'")
        self.ADDRESS_FOR_DELIVERY = Element("#addressForSendSPD", "Поле 'Адрес для доставки РПД'")
        self.ADD_KP = Select("#saleAddKp", "Поле 'Создание Коммерческого предложения'")
        self.CREATE_ADD_AGREEMENT = Select("#saleAddAgreementAdd", "Поле 'Формирование договора/ДС'")
        self.ADD_ACCOUNT = Select("#saleAddAccount", "Создание Лицевого счета")
        self.EQUIPMENT_RETURNED_ACTION = Select("#equipmentRentStateAction", "Действие с возвращаемым оборудованием")

        self.SUBSCRIBER = Element("subscription", "Абонент")
        self.CURRENT_PRODUCT = Element("#subscriptionCurrentProduct", "Текущий продукт")

        self.SAVE_BTN = Element("#inquiry-create-form #save", "Кнопка 'Сохранить'")


class CommentsForm(DynamicForms):
    """Форма 'Комментарии'."""

    def __init__(self) -> None:
        super().__init__()

        self.TITLE = Element("[class$=side-panel-title] h3", "Заголовок формы 'Комментарии'")
        self.FORM = Element("[class*=panel-toolbar] + div:has([class*=panel-content])", "Форма 'Комментарии'")
        self.OPEN_FULL_BTN = Element("[data-icon=OpenInFull]", "Кнопка 'Развернуть'")
        self.CLOSE_FULL_BTN = Element("[data-icon=CloseFullscreen]", "Кнопка 'Свернуть'")
        self.COMMENTS_TYPE = SelectDifferentItemTextPath(
            "[class*=panel-content-body] [class*=select-show]",
            "Объект для которого отображаются комментарии",
        )
        self.NO_COMMENTS_BLOCK = Element(
            "[class$=side-panel-content] .platform-empty-state-container",
            "Блок 'Комментарии отсутствуют'",
        )
        self.COMMENT_INPUT = Element("[class$=side-panel-content] textarea[class*=input]", "Поле ввода комментария")
        self.SEND_COMMENT_BTN = Element("[class$=side-panel-content] [data-icon=Send]", "Кнопка 'Отправить комментарий'")

        # COMMENTS
        self.COMMENT = ElementsList("[class*=card-body]", "Комментарий")
        self.COMMENT_AUTHOR = ElementsList("[class*=card-body] p:nth-child(1)", "Автор комментария")
        self.COMMENT_DATE = ElementsList("[class*=card-body] p[color]", "Дата создания комментария")
        self.COMMENT_TEXT = ElementsList("[class*=card-body] p:nth-child(2):not([color])", "Текст комментария")
        self.MORE_ACTIONS_BTN = ElementsList("[data-icon=MoreVert]", "Кнопка выбора действий")
        self.EDIT_BTN = Element("[data-menu-id*=-edit]", "Кнопка 'Редактировать'")
        self.DELETE_BTN = Element("[data-menu-id*=-delete]", "Кнопка 'Удалить'")

        # EDIT COMMENT FORM
        self.EDIT_FORM_TITLE = Element("[class*=drawer-title] h3", "Заголовок формы 'Редактирование комментария'")
        self.EDIT_COMMENT_INPUT = Element(
            "[class*=drawer-body] textarea[id=text]", "Поле ввода для редактирования комментария"
        )

    @allure.step("Проверить комментарий")
    def check_comment(
        self,
        comment_index: int = 0,
        author: str | None = None,
        date: datetime | None = None,
        comment_text: str | None = None,
        time_for_save_comment: int = 5,
    ) -> None:
        self.COMMENT.wait_elements_visible(comment_index)
        if author:
            self.COMMENT_AUTHOR[comment_index].wait_to_have_text(author)
        if date:
            check_that_date_later(self.COMMENT_DATE[comment_index], date, time_for_save_comment)
        if comment_text:
            self.COMMENT_TEXT[comment_index].wait_to_have_text(comment_text)


class TechConnectCheckForm(DynamicForms):
    """Окно 'Проверка технической возможности подключения'."""

    def __init__(self) -> None:
        super().__init__()

        self.TITLE = Element("h3", "Заголовок 'Проверка технической возможности подключения'")
        self.ADDRESS_OPTIONS = Autocomplete("#address", "Варианты адресов")
        self.SELECT_PRODUCTS_BTN = Element(
            "[class*=spin-container] [class*=spin-container] button[type=button][class*=btn-primary][class*=btn-variant-solid]",
            "Кнопка 'Выбрать продукты'",
        )


class CreateSystemProblem(DynamicForms):
    """Форма 'Создание системный проблемы'"""

    def __init__(self) -> None:
        super().__init__()

        self.PROBLEM_NAME = Element("#name", "Поле ввода 'Наименования'")
        self.PROBLEM_TYPE_FIELD = Element("#commonFaultType", "Поле 'Тип системной проблемы'")
        self.PROBLEM_TYPE_OPTIONS = ElementsList(
            "(//*[contains(@class, 'tree-title')]//span//span)", "Выбор 'Типа системной проблемы'"
        )
        self.PRIMARY_ACCEPT_BTNS = ElementsList("#_accept-button .platform-button__content", "Выбор кнопки 'Применить'")

        self.OCCURANCE_DATE = DatePicker("#raiseDate", "Дата возникновения")
        self.PLANNED_END_DATE = DatePicker("#planCloseDate", "Дата окончания (план)")

        self.CLEAR_DATE = ElementsList("(//*[contains(@class, 'picker-clear')])", "Очистка 'Даты возникновения'")
        self.CLIENT_TYPE_FIELD = Select("#CF_CLNT_TYPE", "Поле ввода 'Тип клиента'")
        self.PROBLEM_REGION = Select("#CF_REGION", "Регион возникновения проблемы")

        self.PROBLEM_SERVICE_FIELD = Element("#TEST_1", "Поле 'Название услуги'")
        self.CLIENT_CONTACTS_AGAIN_RADIO_BTNS = ElementsList(
            "#TEST_2 .ant-radio", "Переключатели параметра 'Клиент обращается повторно?'"
        )
        self.PROBLEM_OCCURANCE_DATE = DatePicker("#TEST_3", "Дата возникновения проблемы")
        self.PROBLEMATIC_SERVICE_FIELD = Select("#TEST_5", "Поле 'Проблемный сервис'")
        self.ATTEMPTS_NUM_FIELD = Element("#TEST_6", "Поле 'Количество попыток'")
        self.ADJUSTMENT_REQUIRED_RADIO_BTNS = ElementsList(
            "#TEST_4 .ant-radio", "Переключатели параметра 'Требуется корректировка?'"
        )
        self.AMOUNT_OF_CHARGES_FIELD = Element("#TEST_7", "Поле 'Сумма начислений'")

        self.EXPERTS_CHECKBOX = Element("#onlyExpertLink", "Чекбокс 'Привязывают только эксперты'")
        self.INFORM_CLIENT_FIELD = Element("#messageToSubscriber", "Поле 'Сообщить клиенту'")
        self.TECHNICAL_DESCRIPTION_FIELD = Element("#description", "Поле 'Техническое описание'")
        self.OPERATOR_DESCRIPTION_FIELD = Element("#descriptionForOperator", "Поле 'Описание для оператора'")
        self.CREATE_PROBLEM_BTN = ElementsList("[role='dialog'] #_accept-button", "Кнопка 'Создать'")


class EditSystemProblem(DynamicForms):
    """Форма 'Редактирование системный проблемы'"""

    def __init__(self) -> None:
        super().__init__()

        self.PROBLEM_NAME = Element("#additional_values_name", "Поле ввода 'Наименования'")
        self.PRIORITY_FIELD = Select("#additional_values_priority", "Приоритет")
        self.PROBLEM_TYPE_FIELD = Element("#additional_values_topic", "Поле 'Тип системной проблемы'")
        self.PROBLEM_TYPE_OPTIONS = ElementsList(
            "(//*[contains(@class, 'tree-title')]//span//span)", "Выбор 'Типа системной проблемы'"
        )
        self.PRIMARY_ACCEPT_BTNS = ElementsList(
            "(//*[contains(@class, 'drawer')][last()]//*[@id='_accept-button'])", "Выбор кнопки 'Применить'"
        )
        self.REASON_TYPE_FIELD = Select("#additional_values_reasonType", "Тип причины")
        self.INFLUENCE_POTENTIAL_FIELD = Select("#additional_values_potential", "Потенциал влияния")

        self.OCCURANCE_DATE = DatePicker("#additional_values_raiseDate", "Дата возникновения")
        self.PLANNED_END_DATE = DatePicker("#additional_values_planCloseDate", "Дата окончания (план)")
        self.FACT_END_DATE = DatePicker("#additional_values_factCloseDate", "Дата окончания (факт)")

        self.CLEAR_DATE = ElementsList("(//*[contains(@class, 'picker-clear')])", "Очистка 'Даты возникновения'")

        self.EXPERTS_CHECKBOX = Element("#additional_values_onlyExpertLink", "Чекбокс 'Привязывают только эксперты'")
        self.INFORM_CLIENT_FIELD = Element("#additional_values_messageToSubscriber", "Поле 'Сообщить клиенту'")
        self.TECHNICAL_DESCRIPTION_FIELD = Element("#additional_values_description", "Поле 'Техническое описание'")
        self.OPERATOR_DESCRIPTION_FIELD = Element(
            "#additional_values_descriptionForOperator", "Поле 'Описание для оператора'"
        )
        self.SAVE_PROBLEM_BTN = ElementsList("button + .ant-btn-primary", "Кнопка 'Сохранить'")


class SelectingReasonType(DynamicForms):
    """Форма 'Выбор типа причины'"""

    def __init__(self) -> None:
        super().__init__()

        self.PROBLEM_TYPE_LIST = ElementsList(".ant-tree-title span span", "Выбор типа причины")
        self.PRIMARY_ACCEPT_BTNS = ElementsList("#_accept-button", "Выбор кнопки 'Применить'")


class TransferProcessing(DynamicForms):
    """Форма 'Передача на обработку'"""

    def __init__(self) -> None:
        super().__init__()

        self.TRANSFER_FORM = Element("#forwardCommonFaultForm", "Форма передачи на обработку")
        self.TRANSFER_STEP_FIELD = Select("#forwardCommonFaultForm_process", "Поле 'Шаг'")
        self.QUEUE_FIELD = Select("#forwardCommonFaultForm_queue", "Поле 'Очередь'")
        self.HAND_OVER_BTN = ElementsList("#_accept-button", "Кнопка 'Передать'")
        self.COVER_NOTE_FIELD = Element("#forwardCommonFaultForm_comment", "Поле 'Сопроводительная записка'")
        self.PROCESS_UNTIL = DatePicker("#forwardCommonFaultForm_dueDate", "Поле 'Обработать до'")


class FilterSettings(DynamicForms):
    """Форма 'Фильтры'"""

    def __init__(self) -> None:
        super().__init__()

        self.PROBLEM_NUM_FIELD = Element("#commonFaultIds", "Поле 'Номер проблемы'")
        self.PROBLEM_NAME_FIELD = Element(
            ".ant-form.ant-form-vertical .ant-form-item:nth-child(4) input", "Поле 'Наименование проблемы'"
        )
        self.PROBLEM_REASON_FIELD = Element("#commonFaultTypeCodes", "Поле 'Тип причины'")
        self.PROBLEM_TYPE_FIELD = Select("#reasons", "Выбор 'Типа проблемы'")
        self.PRIORITY_FIELD = Select("#priorityCodes", "Выбор 'Приоритета'")
        self.REGISTERED_FIELD = Select("#operatorLogins", "Выбор 'Кто зарегистрировал'")
        self.PROBLEM_TOPIC_FIELD = Element("#activityCodes", "Поле 'Шаг'")

        self.TREE_TITLE_LIST = ElementsList(".ant-tree-title span>span", "Список наименований")
        self.REASON_CHECKBOX_LIST = ElementsList(".ant-tree-checkbox-inner", "Список чекбоксов наименований")
        self.CANCEL_CHOICE = Element("a+a", "Отменить выбор")

        self.CHECKBOX_TITLE_LIST = ElementsList(
            ".ant-select-item-option-content .platform-filterable-component-text-to-highlight span",
            "Список напименований",
        )
        self.CHECKBOX_LIST = ElementsList(
            ".ant-select-item-option-content  [type='checkbox']", "Список чекбоксов наименований"
        )

        self.PLUS_SQUARE = Element("[data-icon='SmallUncollapse']", "Кнопка раскрытия списка")

        self.APPLY_BTN = ElementsList(".ant-drawer-footer .ant-btn-primary", "Кнопка 'Применить'")
        self.PRIMARY_ACCEPT_BTNS = ElementsList("#_accept-button", "Выбор кнопки 'Применить'")
        self.RESET_BTN = ElementsList(".ant-drawer-footer .ant-btn-text:nth-child(1)", "Кнопка 'Сбросить'")


class CreateTransition(DynamicForms):
    """Форма 'Создание перехода'"""

    def __init__(self) -> None:
        super().__init__()

        self.FORM = Element(".ant-drawer-content-wrapper", "Форма 'Создание перехода'")
        self.FROM_STATUS = Select("#fromStatusId", "Исходный статус")
        self.TO_STATUS = Select("#toStatusId", "Следующий статус")
        self.PRIORITY = Element("#priority", "Приоритет")
        self.EVENT = Select("#eventId", "Событие")
        self.IS_MANUAL_CHECKBOX = Element("#isManual", "Ручной запуск перехода")
        self.CANCEL_BTN = Element("//*[@class='ant-drawer-footer']/div/button[1]", "Кнопка 'Отмена'")
        self.ACTIVE_ADD_TRANSITION_BTN = Element("//*[@class='ant-drawer-footer']/div/button[2]", "Кнопка 'Добавить'")


class EditDynamicElements(BaseElements):
    """Динамические элементы в редактировании.
    (Отличается от класса DynamicElements,
    только префиксом edit_ в id элемента)."""

    def __init__(self) -> None:
        super().__init__()

        self.CREATE_BTN = Element("#place-edit_addressString_create-address-modal_accept-button", "Кнопка 'Создать'")
        self.ACCOUNT_NUM = Element("input[id*='edit_accountNumber']", "Номер ЛС")
        self.SUBSCRIPTION_ID = Element("input[id*='edit_subscriptionIdentification']", "Абонент")
        self.CONTRACT_NUM = Element("input[id*='edit_agreementNumber']", "Номер договора")
        self.INN = Element("input[id*='edit_taxIdentificationNumber']", "ИНН")
        self.KPP = Element("input[id*='edit_registrationReasonCode']", "КПП")
        self.SNILS = Element("input[id*='edit_INILA']", "СНИЛС")
        self.CUSTOMER_TYPE = Element("input[id*='edit_customerTypes']", "Тип клиента")
        self.CUSTOMER_NAME = Element("input[id*='edit_customerName']", "Имя клиента")
        self.ID_DOCUMENT_SERIAL = Element("input[id*='edit_identificationDocumentSeries']", "Серия документа")
        self.ID_DOCUMENT_NUM = Element("input[id*='edit_identificationDocumentNumber']", "Номер документа")
        self.DOCUMENT_SERIAL = Element("input[id*='edit_documentSeries']", "Серия документа")
        self.DOCUMENT_NUM = Element("input[id*='edit_documentNumber']", "Номер документа")
        self.NATIONALITY = Element("input[id*='edit_nationality']", "Гражданство")
        self.SPEAKING_LANGUAGE = Element("input[id*='edit_speakingLanguage']", "Язык общения")
        self.RESIDENT_CHECKBOX = Element("input[id*='edit_isResident']", "Флаг резидента")
        self.BUSINESS_ACTIVITY = Element("input[id*='edit_businessActivity']", "Вид деятельности")
        self.NOTE = Element("textarea[id*='edit_note']", "Примечание")
        self.REGISTRATION_ADDRESS = Element("input[id*='edit_registrationAddress']", "Адрес регистрации")
        self.REPUTATION = Element("input[id*='edit_reputation']", "Репутация")
        self.OKPO = Element("input[id*='edit_RNNBO']", "ОКПО")
        self.OKATO = Element("input[id*='edit_ARCPS']", "ОКАТО")
        self.OKVED = Element("input[id*='edit_economicActivities']", "ОКВЭД")
        self.OGRN = Element("input[id*='edit_PSRN']", "ОГРН")
        self.PUBLIC_PERSON_CHECKBOX = Element("input[id*='edit_publicOfficial']", "Флаг общественного лица")
        self.BIRTH_PLACE = Element("input[id*='edit_birthPlace']", "Место рождения")
        self.BIRTH_DATE = Element("input[id*='edit_birthDate']", "Дата рождения")
        self.GENDER_DROPDOWN = Element("input[id*='edit_gender']", "Пол")
        self.DOCUMENT_TYPE = Element("input[id*='edit_documentType']", "Тип документа")
        self.DOCUMENT_DATE = Element("input[id*='edit_documentDateOfIssue']", "Дата выдачи документа")
        self.DOCUMENT_PROVIDE_BY = Element(
            "input[id*='edit_documentProvidedByOrganization']", "Организация, выдавшая документ"
        )
        self.DOCUMENT_DIVISION_CODE = Element("input[id*='edit_documentDivisionCode']", "Код подразделения")
        self.DOCUMENT_VALID_DATE = Element("input[id*='edit_documentValidFor']", "Срок действия документа")

        self.REGISTRATION_DOCUMENT = Element("input[id*='edit_PSRNInfo']", "Регистрационный документ")
        self.REGISTRATION_DATE = Element("input[id*='edit_registrationDate']", "Дата регистрации")
        self.REGISTRATION_NUM = Element("input[id*='edit_foreignRegistrationNumber']", "Номер регистрации")
        self.TAX_SCHEME = Element("input[id*='edit_taxScheme']", "Налоговая схема")


class AddAgreement(DynamicForms):
    """Форма 'Добавление нового договора'."""

    def __init__(self) -> None:
        super().__init__()


class AddRelatedPersonForms(DynamicForms):
    """Форма 'Добавление связанного лица'"""

    def __init__(self) -> None:
        super().__init__()
        self.TITLE = Element("[class*='drawer-title'] h4", "Заголовок формы")
        self.ADD_NEW_RELATED_PERSON_BTN = Element(
            "[class*='drawer-body'] [class*='platform-toolbar'] > div:nth-child(1) [data-icon*='Add']",
            "Кнопка 'Добавить' новое связанное лицо",
        )
        self.TYPE_RELATED_PERSON = Select("#add-linked-person_linkedPersonType", "Поле выбора типа связанного лица")
        self.NAME_RELATED_PERSON = Element("#add-linked-person_impersonalName", "Поле 'Наименование связанного лица'")
        self.FUNCTION_RELATED_PERSON = Select(
            "#add-linked-person-function_functionType", "Поле выбора функции связанного лица"
        )
        self.ADD_BTN = Element("[class*='drawer-footer'] > div > button[class*='btn-primary']", "Кнопка 'Добавить'")

    @allure.step("Заполнить данные связанного лица")
    def fill_data_for_related_person(self, **kwargs: Any) -> None:
        self.ADD_NEW_RELATED_PERSON_BTN.click()
        self.TYPE_RELATED_PERSON.select_by_value(kwargs.get("type_related_person") or "Обезличенное")
        self.NAME_RELATED_PERSON.fill(kwargs.get("name_related_person") or "Тестовое наименование")
        self.NEXT_BTN.click()
        self.FUNCTION_RELATED_PERSON.select_by_value(kwargs.get("function") or "Выгодоприобретатель")
        self.NEXT_BTN.click()
        self.EMAIL_ADD_BTN.click()
        self.EMAIL_INPUT.fill(kwargs.get("email") or "test@mail.ru")
        self.ADD_BTN.click()


class PromisedPaymentForm(DynamicForms):
    """Форма 'Подключить обещанный платёж'"""

    def __init__(self) -> None:
        super().__init__()
        self.CUSTOM_PARAM_BTN = Element("#showProductOffer", "Кнопка 'Платеж с произвольными параметрами'")
        self.AMOUNT_FLD = Element("#amount", "Поле 'Сумма'")
        self.COMMISSION_FLD = Element("#commission", "Поле 'Комиссия'")
        self.DURATION_FLD = Element("#duration", "Поле 'Срок действия'")
        self.ABONENT_FLD = Element("#abonentNo", "Поле 'Абонент'")
        self.BALANCE_FLD = Element("#balanceTypeId", "Поле 'Кошелек'")
        self.PRODUCT_OFFER_FLD = Select("#selectProductOffer", "Поле 'Продуктовое предложение'")
        self.CASH_FLD = Select("#paymentPointId", "Поле 'Касса'")

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
                self.ABONENT_FLD.fill(str(kwargs.get("abonent")) or "")


class PersonalAccountForm(DynamicForms):
    """Форма 'Добавление/Редактирование лицевого счета'"""

    def __init__(self) -> None:
        super().__init__()

        self.ACCOUNT_NUMBER = Element("#account-card-create_accountNumber", "Поле ввода 'Номер лицевого счета'")
        self.PAYMENT_METHOD = SelectDifferentRoot(
            "form:is(#account-card-edit, #account-card-create) [class*=select-selector]:has([id*=ratingType])",
            "Способ оплаты",
        )
        self.THRESHOLD_CONTROL_CHECKBOX = Element(
            "[class*=checkbox-wrapper]:has(#account-card-create_thresholdControl, #account-card-edit_thresholdControl)",
            "Чекбокс 'Контроль порога'",
        )
        self.THRESHOLD_CONTROL_FLD = Element(
            "#account-card-create_thresholdBreak, #account-card-edit_thresholdBreak",
            "Форма ввода 'Контроль порога'",
        )
        self.CANCEL_BTN = Element("(//*[contains(@class, 'platform-toolbar')]/div[1] //button)[1]", "Кнопка 'Отмена'")

    def check_personal_account_form(self) -> int:
        self.TITLE.wait_to_have_text("Создание лицевого счёта")
        self.ACCOUNT_NUMBER.check_attribute_by_value("value", re.compile(r"\d+"))
        self.ACCOUNT_NUMBER.check_attribute_by_value("disabled", "")
        return int(self.ACCOUNT_NUMBER.text)


class ProductInfoForm(DynamicForms):
    """Форма Информация о товаре"""

    def __init__(self) -> None:
        super().__init__()

        self.PRODUCT_NAME = Element("[class*=drawer-title] h2", "Название продукта")
        self.REGION = Element(
            "[class*=drawer-header] p:last-child",
            "Значение поля 'Регион'",
        )
        self.SUBSCRIPTION_FEE = Element(
            "[class*=-drawer-content] [class*=-drawer-body] div:nth-child(3) h4", "Абонентская плата"
        )

        # HEADER_NAV_TAB
        self.VOLUMES_TAB = Element("[class*=drawer-content] [id*=tab-volumes]", "Таб 'Объемы'")
        self.PRICE_TAB = Element("[class*=drawer-content] [id*=tab-price]", "Таб 'Цены'")
        self.CHARACTERISTICS_TAB = Element("[class*=drawer-content] [id*=tab-characteristics]", "Таб 'Характеристики'")
        self.SERVICES_TAB = Element("[class*=drawer-content] [id*=tab-services]", "Таб 'Сервисы'")
        self.RESOURCES_TAB = Element("[class*=drawer-content] [id*=tab-resources]", "Таб 'Ресурсы'")

        # Характеристики
        self.SPECIFICATION = ElementsList(
            "[class*=-drawer-content][role=dialog] div[id*='panel-characteristics']", "Характеристики"
        )
        self.ADDRESS = Element("[data-testid=address-value] p", "Значение поля 'Адрес'")
        self.ACTIVATION_TYPE = Element("[data-testid=attribute-undefined]:first-child p:last-child", "Тип активации")
        self.COMMUNICATION_STANDARD = Element(
            "[data-testid=attribute-undefined]:nth-child(2) p:last-child", "Стандарт связи"
        )
        self.SPEED = Element("[data-testid=attribute-undefined]:nth-child(3) p:last-child", "Скорость")

        # RESOURCES_TAB
        self.RESOURCES_PANEL = Element("[id*=panel-resources]", "Панель 'Ресурсы'")
        self.SIM_CARD_BLOCK = Element(
            "//p[contains(text(), 'SIM')]/../..", "Блок 'SIM-карта'"
        )  # требует дата атрибута от фронтов
        self.PHONE_NUMBER_BLOCK = Element(
            "//p[contains(text(), 'Телефонный номер')]/../../..", "Блок 'Телефонный номер (мобильный)'"
        )  # требует дата атрибута от фронтов
        self.CODE_NOMENCLATURE = Element(
            "//p[contains(text(), 'Код номенклатуры')]/../../p", "Код номенклатуры оборудования"
        )
        self.NUMBER_EQUIPMENT = Element(
            "//p[contains(text(), 'Серийный номер')]/../../p", "Серийный номер оборудования"
        )  # Требуется дата айди от фронтов, зацепиться по другому нереально
        self.PHONE_NUMBER = Element("(//p[contains(text(), 'Телефонный номер')]/../.. //p)[4]", "Номер телефона")
        self.MENU_PHONE_NUMBER_BTN = Element("//p[contains(text(), 'Телефонный номер')]/../../.. //button", "")
        self.REPLACE_BTN = Element("[data-menu-id*=replace]", "Кнопка 'Заменить'")
        self.PRODUCT_SIDEBAR_RESOURCES_SIM_MORE_BTN = Element(
            "//p[contains(text(), 'SIM')] /parent::div /parent::div /parent::div //button",
            "Три точки у ресурса сим карта в сайдбаре продукта",
        )
        self.RESOURCE_SIM_ICC = Element(
            "(//p[contains(text(),'SIM')] /parent::div /parent::div //p )[4]",
            "ICC SIM карты в разделе Ресурсы",
        )

    @allure.step("Проверка адреса продукта в форме информации")
    def verify_product_addresses(self, expected_region: str, expected_address: str) -> None:
        """Проверяет отображение региона и адреса в форме информации о продукте.

        :param expected_region: Ожидаемый регион продукта
        :param expected_address: ожидаемый адрес продукта
        """
        self.REGION.to_contain_text(expected_region, timeout_sec=2)
        self.CHARACTERISTICS_TAB.click()
        self.ADDRESS.to_contain_text(expected_address)
        self.INNER_CANCEL_BTN.click()


class ReplaceResource(DynamicForms):
    """Форма Замена ресурса"""

    def __init__(self) -> None:
        super().__init__()

        self.TITLE = Element("(//div[contains(@class, 'side-panel-content')]//h4)[1]", "Заголовок 'Заменяемый ресурс'")
        self.REPLACE_RESOURCE_FORM = Element(
            "(//*[contains(@class, 'drawer-open')] //*[contains(@class, 'drawer-content-wrapper')])[2]",
            "Форма 'Замена ресурса'",
        )
        self.RESOURCE_TYPE = Select(
            "input[id=resourceType]",
            "Поле 'Тип ресурса'",
        )
        self.SUBSCRIBER = Element(
            "(//*[contains(@class, 'drawer-open')] //*[contains(@class, 'drawer-content-wrapper')])[2] //*[contains(@class,'select-borderless')]",
            "Абонент",
        )
        self.TITLE_PHONE_NUMBER = Element("label[for=phoneNumber]", "Заголовок 'Номер телефона'")
        self.PHONE_NUMBER = Element("//label[@for='phoneNumber']/../.. //input", "Номер телефона")
        self.PHONE_NUMBER_HELP = Element("#phoneNumber_help", "Подсказка для поля 'Номер телефона'")
        self.CHOICE_PHONE_NUMBER_BTN = Element(
            "//label[@for='phoneNumber']/../.. //*[@class='ant-input-suffix']",
            "Кнопка выбора номера телефона",
        )
        self.REPLACE_SUM = Element("input[id=baseAmount]", "Базовая стоимость замены")
        self.DISCOUNT_INPUT = Element("input[id=percent]", "Поле 'Скидка'")
        self.REPLACE_SUM_AFTER_DISCOUNT = Element("input[id=cost]", "Поле 'Итоговая цена без налога'")
        self.TITLE_CONTACT_PERSON = Element("label[for=additionalInfo_contactPerson]", "Заголовок 'Контактное лицо'")
        self.TITLE_EMAIL = Element("label[for=additionalInfo_email]", "Заголовок 'E-mail'")
        self.TITLE_CONTACT_PHONE = Element("label[for=additionalInfo_phone]", "Заголовок 'Телефон для связи'")
        self.DO_REPLACE_BTN = Element("button[class*=btn-primary]", "Кнопка 'Выполнить замену'")

        # CHOICE_NUMBER_FORM
        self.REPLACE_PHONE_NUMBER_FORM = Element(
            "(//*[@class='ant-drawer-content-wrapper'])[3]", "Форма замены номера телефона"
        )
        self.FIND_NUMBER_INPUT = Element(
            "(//*[@class='ant-drawer-content-wrapper'])[3] //input", "Поле поиска номера телефона"
        )
        self.ALLOWED_NUMBERS = ElementsList("[data-row-key]", "Доступные для замены номера")
        self.EMPTY_ALLOWED_NUMBERS_LIST = Element(".platform-empty-state-container", "Пустой список доступных номеров")
        self.SUBSCRIBER_SELECT = Select("input[id='subscriber']", "Форма для выбора номера")
        self.ICC_INPUT = Element("//div[@id='newIcc'] //input", "Окно для ввода ICC")
        self.ICC_CHECK_BTN = Element("//div[@id='newIcc'] //button", "Кнопка проверить ICC")
        self.ICC_SUCCESS_WINDOW = Element(
            "//div[@id='newIcc'] //../../../../../..  //p[@color='interface15']",
            "Окно с информацией о замене SIM-карты",
        )
        self.ICC_INFO_WINDOW = Element(
            "//div[@id='newIcc_help'] //p",
            "Окно с информацией о замене",
        )
        self.ICC_NOT_ENOUGH_FUNDS = Element(
            "//div[@class='ant-form-item-explain-error']",
            "Уведомление о нехвадтке средств для замены SIM-карты",
        )
        self.APPLY_BTN = Element("//button[@variant='primary']", "Кнопка Выполнить замену")

        # REPLACEABLE_RESOURCE
        self.REPLACEABLE_RESOURCE_IDENTIFIER = Autocomplete(
            "input[id=resourceIdentifier]", "Поле 'Идентификатор ресурса'"
        )
        self.REPLACEABLE_RESOURCE_PRODUCT_NAME = Element(
            "div[class*=platform-grid-container] > div[data-testid*=attribute]:nth-child(1) p[data-name=paragraph]",
            "Поле 'Продукт' в блоке Заменяемый ресурс",
        )
        self.REPLACEABLE_RESOURCE_SUBSCRIBER = Element(
            "div[class*=platform-grid-container] > div[data-testid*=attribute]:nth-child(2) p[data-name=paragraph]",
            "Поле 'Абонент' в блоке Заменяемый ресурс",
        )
        self.REPLACEABLE_RESOURCE_NOMENCLATURE_CODE = Element("p[id=itemCode]", "Поле 'Код номенклатуры'")
        self.REPLACEABLE_RESOURCE_TYPE_OF_SALE = Element("p[id=typeOfSale]", "Поле 'Тип передачи'")

        # RESOURCE_FOR_REPLACE
        self.FOR_REPLACE_FROM_EARLIER_PURCHASED = Element(
            "[class*=side-panel-content-body] div[class*=spin-container] > div:nth-child(2) input[class*=checkbox-input]",
            "Чекбокс 'Из ранее приобретенных'",
        )
        self.FOR_REPLACE_RESOURCE_IDENTIFIER = Select(
            "input[id=newSerialNumber]", "Поле 'Идентификатор ресурса' в блоке Ресурс на замену"
        )
        self.ADD_AGREEMENT_CHECKBOX = Element("input[id=isAdditionalAgreement]", "Чекбокс 'Дополнительное соглашение'")
        self.ACCEPTANCE_CERTIFICATE_CHECKBOX = Element(
            "input[id=isAcceptanceCertificate]", "Чекбокс 'Акт приема-передачи'"
        )

    def check_required_fields(self) -> None:
        required_class = re.compile(r".*-form-item-required .*")
        self.TITLE_PHONE_NUMBER.to_have_class(required_class)
        self.TITLE_CONTACT_PERSON.not_to_have_class(required_class)
        self.TITLE_EMAIL.not_to_have_class(required_class)
        self.TITLE_CONTACT_PHONE.not_to_have_class(required_class)


class CancelPaymentForm(DynamicForms):
    """Форма Аннулирование платежа"""

    def __init__(self) -> None:
        super().__init__()

        self.SUBTITLE = Element(
            "//div[contains(@class, 'drawer-title')]//h3//following-sibling::p",
            "Информационный подзаголовок формы",
        )
        self.CANCEL_INFO_MESSAGE = Element(
            "[role=dialog] .platform-attention-label p", "Информационное сообщение 'Аннулирование платежа'"
        )
        self.CANCEL_REASON_INPUT_FROM_REGISTRY = Element("#comment", "Причина 'Аннулирование платежа'")
        self.CANCEL_REASON_INPUT = Element("#cancellationReason", "Причина 'Аннулирование платежа'")
        self.CANCEL_OPERATION_BTN = Element("#_accept-button", "Кнопка 'Аннулировать'")
        self.CANCEL_BTN = Element("#_cancel-button", "Кнопка 'Отмена'")


class CreatePaymentForm(DynamicForms):
    """Форма Создания платежа"""

    def __init__(self) -> None:
        super().__init__()

        self.SET_AMOUNT = Element("input[id='amount']", "Сумма платежа")
        self.PAYMENT_POINT = Select("input[id='paymentPointId']", "Выбор кассы")
        self.PAYMENT_DATE_INPUT = DatePicker("input[id='paymentDate']", "Дата платежа")
        self.PAYMENT_DATE_APPLY_BUTTON = Element("li.ant-picker-ok span", "Применить")


class AddOptionsForm(DynamicForms):
    """Форма Добавления опций"""

    def __init__(self) -> None:
        super().__init__()

        self.PERSONAL_ACCOUNT_CHARGING_TEXT = Element("p[color='interface1']", "Текст о списании с персонального счета")
        self.SEARCH_OPTIONS_FLD = Element('input[id="productOfferingName"]', "Поле поиска опций")
        self.SEARCH_BTN = Element("form[class*='form-vertical'] button[class*=btn-default]", "Кнопка 'Найти'")
        self.SHOW_ONLY_CHOSEN_BTN = Element('[class*="switch-handle"]', "Кнопка 'Показать только выбранные'")
        self.OPTION_CARD = ElementsList("//div[contains(@class, 'card-body')]", "Карточка опции")
        self.OPTIONS_NAME = ElementsList("//div[contains(@class, 'card-head-title')]/h4", "Доп. опции названия")
        self.CHOSE_OPTION_BTN = ElementsList("#card_buttons button[class*=primary]", "Кнопка выбора опции")
        self.PERSONAL_ACCOUNT_CHECKBOX = ElementsList("input[type=checkbox]", "Чекбокс Персональный счет")
        self.PERSONAL_ACCOUNT_MODAL_FIELDS = ElementsList(
            "div[class*='modal-body'] .platform-grid-container div p:nth-child(2)",
            "Поля окна Использовать персональный счет",
        )


class ChangeMainProductForm(DynamicForms):
    """Форма смены основного продукта"""

    def __init__(self) -> None:
        super().__init__()

        self.ADD_PRODUCT_BTN = Element("#_accept-button", "Кнопка 'Добавить'")
        self.SEARCH_BTN = Element(
            "[class*=spin-container] [class*=scrollable] + div button[class*=outlined]", "Кнопка 'Найти'"
        )
        self.CHOSE_PRODUCT_BTN = ElementsList("//*[@id='card_buttons']/div/button[1]", "Кнопка 'Выбрать' у 1 продукта")
        self.LOTTIE_TEXT = Element("(//span[@display='inline-block'])[1]", "Текстовка Лотти")


class EditSegmentsForm(DynamicForms):
    """Форма 'Редактирование сегментов Клиента'"""

    def __init__(self) -> None:
        super().__init__()

        self.TITLE = Element("//div[contains(@class, 'ant-drawer-title')]/h3", "Заголовок формы")
        self.SEARCH_SEGMENTS_VALUE_FLD = Select(
            'input[id="segmentsControlForm_entitySegments_0_segmentValueId"]', "Выбор Значения"
        )
        self.MANAGEMENT_TYPE_RADIO_BTN = RadioOrCheckboxBlock(
            '[id="segmentsControlForm_excludeFromSegmentation"]', "Радио кнопка 'Тип назначения'"
        )
        self.SAVE_SEGMENT_BTN = Element("#_accept-button", "Кнопка 'Сохранить' сегмент")


class ClientAuthorizationForm(DynamicForms):
    """Форма 'Авторизация клиента'"""

    def __init__(self) -> None:
        super().__init__()

        self.BY_DOCUMENT_BTN = Element("label:has(input[value=external])", "По документу")
        self.BY_PHONE_BTN = Element("label:has(input[value=sms])", "По телефону")

        self.AUTHORIZATION_PHONE_NUMBER = Element("#authorize-form_phoneNumber", "Номер телефона")
        self.SEND_CODE = Element("#authorize-form button[class*=btn-primary] span", "Отправить код")

        self.FOUR_DIGITS_CODE = Element("#authorize-form_code", "Последние 4 цифры номера документа или СМС-код")
        self.ERROR_TEXT = Element("#authorize-form_code_help", "Текст ошибки")
        self.ATTEMPTS_NUMBER = Element(
            "#authorize-form span[class*=input-borderless] input[readonly][type=text]", "Количество попыток"
        )

        self.CANCEL_BTN = Element("//*[@id='authorize-form'] /../following-sibling::div[2]/button[1]", "Кнопка 'Отмена'")
        self.AUTHORIZE_BTN = Element(
            "//*[@id='authorize-form'] /../following-sibling::div[2]/button[2]", "Кнопка 'Авторизовать'"
        )
