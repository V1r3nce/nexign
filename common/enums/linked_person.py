from enum import Enum, StrEnum


class Specialization(Enum):
    PaymentQuestions = 1
    AgreementQuestions = 2
    TechnicalQuestions = 3
    RequestsProcessing = 4
    SecondAuthorization = 5


class LinkedPersonFunction(StrEnum):
    leader = "Руководитель"
    subdivision_leader = "Руководитель подразделения"
    contact_person = "Контактное лицо"
    trustee = "Доверенное лицо"
    beneficiary = "Выгодоприобретатель"
    beneficial_owner = "Бенефициарный владелец"
    agreement_signer = "Подписант договора"
    end_user = "Конечный пользователь"


class LinkedPersonType(StrEnum):
    individual = "Физическое лицо"
    impersonal = "Обезличенное"
