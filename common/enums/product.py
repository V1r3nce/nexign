from enum import StrEnum


class ProductCategories(StrEnum):
    fixed_phone = "FIXED_PHONE"
    mobile = "MOBILE_PHONE"


class ProductClassification(StrEnum):
    main = "main"
    additional = "additional"


class IdentificationTypeCodes(StrEnum):
    msisdn = "MSISDN"
