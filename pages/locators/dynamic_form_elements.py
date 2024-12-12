from base_elements import BaseElements

class DynamicElements(BaseElements):
    ACCOUNT_NUM = "input[id*='accountNumber']"
    SUBSCRIPTION_ID = "input[id*='subscriptionIdentification']"
    CONTRACT_NUM = "input[id*='agreementNumber']"
    INN = "input[id*='taxIdentificationNumber']"
    KPP = "input[id*='registrationReasonCode']"
    SNILS = "input[id*='INILA']"
    CUSTOMER_TYPE = "input[id*='customerTypes']"
    CUSTOMER_NAME = "input[id*='customerName']"
    ID_DOCUMENT_SERIAL = "input[id*='identificationDocumentSeries']"
    ID_DOCUMENT_NUM = "input[id*='identificationDocumentNumber']"
    DOCUMENT_SERIAL = "input[id*='documentSeries']"
    DOCUMENT_NUM = "input[id*='documentNumber']"
    NATIONALITY = "input[id*='nationality']"
    SPEAKING_LANGUAGE = "input[id*='speakingLanguage']"
    RESIDENT_CHECKBOX = "input[id*='isResident']"
    BUSINESS_ACTIVITY = "input[id*='businessActivity']"
    NOTE = "textarea[id*='note']"
    REGISTRATION_ADDRESS = "input[id*='registrationAddress']"
    REPUTATION = "input[id*='reputation']"
    OKPO = "input[id*='RNNBO']"
    OKATO = "input[id*='ARCPS']"
    OKVED = "input[id*='economicActivities']"
    OGRN = "input[id*='PSRN']"
    PUBLIC_PERSON_CHECKBOX = "input[id*='publicOfficial']"
    BIRTH_PLACE = "input[id*='birthPlace']"
    BIRTH_DATE = "input[id*='birthDate']"
    GENDER_DROPDOWN = "input[id*='gender']"
    DOCUMENT_TYPE = "input[id*='documentType']"
    DOCUMENT_DATE = "input[id*='documentDateOfIssue']"
    DOCUMENT_PROVIDE_BY = "input[id*='documentProvidedByOrganization''"
    DOCUMENT_DIVISION_CODE = "input[id*='documentDivisionCode']"
    DOCUMENT_VALID_DATE = "input[id*='documentValidFor']"

    REGISTRATION_DOCUMENT = "input[id*='PSRNInfo']"
    REGISTRATION_DATE = "input[id*='registrationDate']"
    REGISTRATION_NUM = "input[id*='foreignRegistrationNumber']"
    TAX_SCHEME = "input[id*='taxScheme']"

class DynamicForms(DynamicElements):
    TITLE = ".ant-drawer-title h3"
    CROSS_BTN = ".ant-drawer-open  button[aria-label='Close']"
    CANCEL_BTN = "#cancel"
    SAVE_BTN = "#save"
    CLOSE_BTN = "#close"
    FORWARD_BTN = "#forward"

    INNER_CANCEL_BTN = "#_cancel-button"
    INNER_SAVE_BTN = "#_save-button"

class FlCustomerCreate(DynamicForms):
    LAST_NAME = "#customer-individual-create_surname"
    FIRST_NAME = "#customer-individual-create_firstname"
    SUR_NAME = "#customer-individual-create_patronymic"
    DOCUMENT_TYPE_DROPDOWN = "#customer-individual-create_documentType"

    CREATE_ADDRESS_LINK = "#customer-individual-create_registrationAddress_list"

    BIOMETRIC_CHECKBOX = "#customer-individual-create_biometricData"
    CONTACT_PHONE = "#customer-individual-create_contactPhoneNumber"
    CONTACT_EMAIL = "#customer-individual-create_contactEmail"

class CreateOrganization(DynamicForms):
    PROPRIETARY_FORM = "#customer-organization-create_proprietaryForm"


class AddressCreate(DynamicForms):
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

class RequestCreate(DynamicForms):
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

class EditCustomerAttributes(EditDynamicElements):
    pass