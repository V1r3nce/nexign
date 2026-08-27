from enum import StrEnum
from functools import lru_cache

from common.enums.base_enums import CustomEnum, ImmutableRegistry, ListableEnum


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
    satellite = "Спутниковая связь"


class PhoneNumberCategories(StrEnum):
    telephony = "Телефония"


class PhoneLinkTypes(StrEnum):
    flexible = "Гибкая"


class PhoneNumberStates(CustomEnum):
    """Состояния номеров LIS (state_id → phoneNumberStateId)."""

    closed_for_use = ("Закрыт для исп.", 1)
    open_for_use = ("Открыт для исп.", 2)
    distributed = ("Распределён", 3)
    freed = ("Освобождён", 4)
    forbidden = ("Запрещен", 5)
    booked = ("Забронирован", 6)
    linked_to_city = ("Связан с городским", 7)
    reserved = ("Зарезервирован", 8)
    processing = ("Обрабатывается", 9)
    allocated_for_replacement = ("Выд. для замены", 10)
    for_access_card = ("Для карты дост.", 11)


class SimCardStates(CustomEnum):
    """Состояния SIM-карт LIS (state_id → SIMCardStateId)."""

    entered = ("Введена", 1)
    received = ("Получена", 2)
    linked_to_phone = ("Связана с телефоном", 3)
    withdrawn = ("Выведена из обращения", 4)
    ready_for_linking = ("Готова к связыванию", 5)
    defective = ("Дефектная", 6)
    transferred_oo = ("Передана ОО", 7)
    transferred_to_dealer = ("Передана дилеру", 8)
    unlinked = ("Не связана", 9)
    sold = ("Продана", 10)
    processing = ("Обрабатывается", 11)
    reserved = ("Зарезервирована", 12)
    deleted = ("Удалена", 13)
    ready_for_packaging = ("Готова к упаковке", 14)
    transferred_for_packaging = ("Передана на упаковку", 15)
    included_in_kit = ("Входит в комплект", 16)
    part_of_product = ("В составе товара", 17)
    assigned_to_client = ("Закреплена за клиентом", 18)
    rejected_by_client = ("Отбракована клиентом", 19)


class LogicalStatuses(CustomEnum):
    """Логические статусы LIS (status_id → logicalStatusId). Общие для номеров и SIM."""

    free = ("Свободен", 1)
    busy = ("Занят", 2)
    unavailable = ("Недоступен", 3)
