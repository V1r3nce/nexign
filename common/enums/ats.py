from enum import StrEnum
from typing import Self


class DirectAttributeMeta(type):
    """Данный класс предназначен для использования классов с атрибутами типа str и int(не в tuple)"""

    def __getattribute__(cls, name: str) -> type:
        if name.startswith("__") and name.endswith("__"):
            return super().__getattribute__(name)

        value = super().__getattribute__(name)
        return value


class CustomEnum(StrEnum):
    def __new__(cls, name: str, obj_id: int) -> Self:
        obj = str.__new__(cls, name)
        obj._value_ = name
        obj.id = obj_id
        return obj


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
