from dataclasses import dataclass
from functools import cached_property
from random import choice
from typing import Any, List, overload

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from common.enums.lis import DefaultStandardNames


@dataclass
class IPInfo:
    address: str
    id: int


@dataclass
class APNInfo:
    name: str
    id: int
    hlr_id: int
    free_ip_list: List[IPInfo]

    @overload
    def __init__(self, name: str, id: int, hlr_id: int): ...

    @overload
    def __init__(self, item: dict): ...

    def __init__(self, *args: Any) -> None:
        if len(args) == 1:
            item = args[0]
            self.id = item.get("accessPointId")
            self.name = item.get("name")
            self.hlr_id = item.get("HLRAccessPointId")
        elif len(args) == 3:
            self.name = args[0]
            self.id = args[1]
            self.hlr_id = args[2]
        else:
            ValueError("Некорректная инициализация")
        self.free_ip_list = []

    def pop_random(self) -> IPInfo:
        index = choice(range(len(self.free_ip_list)))
        return self.free_ip_list.pop(index)


class MacroRegion(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    macro_region_id: int
    name: str


class EquipmentType(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    equipment_type_id: int
    name: str
    macro_region: MacroRegion


class EquipmentStandard(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    standard_id: int
    name: str
    macro_region: MacroRegion


class Equipment(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    equipment_id: int
    name: str
    standard: EquipmentStandard
    type: EquipmentType
    macro_region: MacroRegion

    @cached_property
    def is_type_def(self) -> bool:
        return self.standard.name in DefaultStandardNames.def_standard_names


class PhoneNumberType(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    phone_number_type_id: int
    macro_region: MacroRegion
    name: str
    standard: EquipmentStandard | None = None


class NumberCategory(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    number_category_id: int
    name: str
    macro_region: MacroRegion


class Operator(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    operator_id: int
    name: str
    macro_region: MacroRegion


class PhoneNumberTypeLink(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    phone_number_type_link_id: int
    name: str


class StockSystem(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    stock_system_id: int
    name: str
    code: str


class Nomenclature(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    code: str
    nomenclature_id: int
    name: str
    stock_system: StockSystem
    is_serial: bool


class InventoryItem(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    serial_number: str
    inventory_item_id: int
    reserved_code: str | None


class RangeValue(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    min_value: int
    max_value: int


class SIMTemplate(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    load_sim_card_template_id: int = Field(alias="loadSIMCardTemplateId")
    IMSI: RangeValue
    ICC: RangeValue
    PUK1: RangeValue
    PUK2: RangeValue | None
    PIN1: RangeValue | None
    PIN2: RangeValue | None
    activation_key: RangeValue | None


class SIMCardType(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    sim_card_type_id: int = Field(alias="SIMCardTypeId")
    name: str
    macro_region: MacroRegion


class NumberClass(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    number_class_id: int
    name: str


class SwitchRef(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    equipment_id: int


class BaseNumberData(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    MSISDN: str
    number_class: NumberClass
    phone_number_id: int | None = None
    switch: SwitchRef | None = None


class PhoneNumberData(BaseNumberData):
    """Класс для данных по номеру телефона"""

    phone_number_abc: BaseNumberData | None = Field(default=None, alias="phoneNumberABC")

    @property
    def class_name(self) -> str:
        return self.number_class.name

    @property
    def class_id(self) -> int:
        return self.number_class.number_class_id

    @property
    def switch_id(self) -> int | None:
        return self.switch.equipment_id if self.switch is not None else None


class SimCardData(BaseModel):
    """Класс для данных по SIM"""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    imsi: str = Field(alias="IMSI")
    icc: str = Field(alias="ICC")
    expiration_date: str | None = None
    switch: SwitchRef | None = None
    sim_card_id: int | None = Field(default=None, alias="SIMCardId")

    @property
    def switchId(self) -> int | None:
        return self.switch.equipment_id if self.switch is not None else None
