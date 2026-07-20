from enum import StrEnum
from functools import lru_cache

from common.enums.base_enums import ImmutableRegistry, ListableEnum


class LisOperators(StrEnum):
    buro = "BURO"
    nexign = "NEXIGN"
    dbl_eight_dbl_zero = "8800"

    @classmethod
    @lru_cache(maxsize=1)
    def def_operators(cls) -> list[str]:
        return [cls.buro, cls.nexign]


class PhoneZoneCodes(StrEnum):
    default = "DEF"
    abc = "ABC"
    dbl_eight_dbl_zero = "8-800"


class DefaultStandardNames(ImmutableRegistry):
    gsm_standard_name: str = "GSM"
    satellite_standard_names: list = ["Спутниковая связь", "Спутниковая связь BURO"]
    pstn_standard_name: str = "PSTN"
    def_standard_names: list = [gsm_standard_name] + satellite_standard_names


class DefaultNomenclatures(ImmutableRegistry):
    invest_nomenclatures = ["at_L_001", "at_XL_001"]
    buro_nomenclatures = ["РБЛТ", "AT"]
    nomenclatures_list: list[str] = invest_nomenclatures + buro_nomenclatures


class NomenclatureTemplates(ListableEnum, StrEnum):
    buro_terminal = "AT."
    invest_satellite = "at_"
    buro_satellite = "РБЛТ."


class SimTypes(StrEnum):
    standard = "STANDARD"


class APNNames(StrEnum):
    nexign_default = "ip.stat.external.nx"


class PhoneNumberTypes(StrEnum):
    federal = "Федеральная"
    fixed = "Фиксированная"


class PhoneNumberCategories(StrEnum):
    telephony = "Телефония"


class PhoneLinkTypes(StrEnum):
    flexible = "Гибкая"
