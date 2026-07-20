from enum import StrEnum

from common.enums.base_enums import CustomEnum


class AtsAttributes(StrEnum):
    tax_scheme = "Схема налогообложения"
    full_name = "Полное имя лица"
    surname = "Фамилия"
    payment_method = "Способ оплаты"
    ogrn = "ОГРН/ОГРНИП"
    organization_type = "Наименование организационно-правовой формы"
    short_organization_type = "Краткое наименование организационно-правовой формы"


class AtsOperations(StrEnum):
    add = "Добавление"
    change = "Изменение"


class TaxScheme(StrEnum):
    default_scheme = "Схема налогообложения по умолчанию"
    non_operational = "Внереализационная схема налогообложения"


class OrganizationType(StrEnum):
    jsc = "АО, Акционерное Общество"
    public_jsc = "ПАО, Публичное Акционерное Общество"
    non_public_jsc = "НАО, Непубличное Акционерное Общество"


class PersonalAccountPaymentMethod(CustomEnum):
    postpaid = ("Постоплатный", 2)
    prepaid = ("Предоплатный", 1)
