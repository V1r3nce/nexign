from pages.locators.dynamic_form_elements import (
    CreateEntrepreneur,
    CreateOrganization,
    DynamicElements,
    IndividualCustomerCreate,
)

fl_customer = IndividualCustomerCreate()
dynamic_elements = DynamicElements()
fl_entrepreneur = CreateEntrepreneur()
fl_organization = CreateOrganization()

data_client = {
    "individual": {
        fl_customer.LAST_NAME.path: "Петров",
        fl_customer.FIRST_NAME.path: "Иван",
        fl_customer.SUR_NAME.path: "Тестович",
        dynamic_elements.GENDER.path: "Мужской",
        dynamic_elements.DOCUMENT_TYPE.path: "Паспорт гражданина РФ",
        dynamic_elements.DOCUMENT_SERIAL.path: "2219",
        dynamic_elements.DOCUMENT_NUM.path: "917343",
        dynamic_elements.DOCUMENT_PROVIDE_BY.path: "ГУ МВД РОССИИ",
        dynamic_elements.DOCUMENT_DIVISION_CODE.path: "520-003",
        dynamic_elements.DOCUMENT_DATE.path: "25.10.2002",
        dynamic_elements.DOCUMENT_VALID_DATE.path: "25.10.2027",
        dynamic_elements.BIRTH_DATE.path: "21.12.1991",
        dynamic_elements.BIRTH_PLACE.path: "г. Москва",
        dynamic_elements.REGISTRATION_ADDRESS.path: "Россия",
        dynamic_elements.INN.path: "123123123123",
        dynamic_elements.SNILS.path: "12312312312",
        fl_customer.CONTACT_PHONE.path: "+79200456745",
        fl_customer.CONTACT_EMAIL.path: "test123@mail.ru",
    },
    "entrepreneur": {
        dynamic_elements.GENDER.path: "Мужской",
        fl_entrepreneur.LAST_NAME.path: "Петров",
        fl_entrepreneur.FIRST_NAME.path: "Иван",
        fl_entrepreneur.SUR_NAME.path: "Тестович",
        dynamic_elements.DOCUMENT_TYPE.path: "Паспорт гражданина РФ",
        dynamic_elements.DOCUMENT_SERIAL.path: "2219",
        dynamic_elements.DOCUMENT_NUM.path: "917343",
        dynamic_elements.DOCUMENT_VALID_DATE.path: "25.10.2027",
        dynamic_elements.BIRTH_DATE.path: "21.12.1991",
        dynamic_elements.REGISTRATION_ADDRESS.path: "Россия",
        dynamic_elements.INN.path: "123123123123",
        fl_entrepreneur.CONTACT_PHONE.path: "+79200456745",
    },
    "organization": {
        fl_organization.CLIENT_NAME.path: "Петров Иван",
        dynamic_elements.REGISTRATION_ADDRESS.path: "Россия",
        fl_organization.TAX_SCHEME.path: "Схема налогообложения по умолчанию",
    },
}

dropdown_fields = [dynamic_elements.GENDER.path, dynamic_elements.DOCUMENT_TYPE.path]
