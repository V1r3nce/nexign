from pages.locators.dynamic_form_elements import FlCustomerCreate, DynamicElements, EditDynamicElements

data_individual = {
    FlCustomerCreate.LAST_NAME: 'Петров',
    FlCustomerCreate.FIRST_NAME: 'Иван',
    FlCustomerCreate.SUR_NAME: 'Тестович',
    DynamicElements.GENDER_DROPDOWN: 'Мужской',
    DynamicElements.DOCUMENT_TYPE: 'Паспорт гражданина РФ',
    DynamicElements.DOCUMENT_SERIAL: '2219',
    DynamicElements.DOCUMENT_NUM: '917343',
    DynamicElements.DOCUMENT_PROVIDE_BY: 'ГУ МВД РОССИИ',
    DynamicElements.DOCUMENT_DIVISION_CODE: '520-003',
    DynamicElements.DOCUMENT_DATE: '25.10.2002',
    DynamicElements.DOCUMENT_VALID_DATE: '25.10.2027',
    DynamicElements.BIRTH_DATE: '21.12.1991',
    DynamicElements.BIRTH_PLACE: 'г. Москва',
    DynamicElements.REGISTRATION_ADDRESS: 'Россия',
    DynamicElements.INN: '123123123123',
    DynamicElements.SNILS: '12312312312',
    FlCustomerCreate.CONTACT_PHONE: '+79200456745',
    FlCustomerCreate.CONTACT_EMAIL: 'test123@mail.ru'
}

dropdown_fields = [DynamicElements.GENDER_DROPDOWN, DynamicElements.DOCUMENT_TYPE
                   ]