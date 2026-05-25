from dataclasses import dataclass
from functools import cached_property
from random import choice
from typing import Any, List, overload


@dataclass
class DefaultStandardNames:
    @cached_property
    def gsm_standard_name(self) -> str:
        return "GSM"

    @cached_property
    def satellite_standard_name(self) -> str:
        return "Спутниковая связь"

    @cached_property
    def pstn_standard_name(self) -> str:
        return "PSTN"


default_standard_names = DefaultStandardNames()


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


@dataclass
class EquipmentType:
    equipment_type_id: int
    name: str
    macro_region_id: int

    def __init__(self, item: dict) -> None:
        self.equipment_type_id = item.get("equipmentTypeId")
        self.name = item.get("name")
        self.macro_region_id = item.get("macroRegion").get("macroRegionId")


@dataclass
class EquipmentStandard:
    standard_id: int
    name: str
    macro_region_id: int

    def __init__(self, item: dict) -> None:
        self.standard_id = item.get("standardId")
        self.name = item.get("name")
        self.macro_region_id = item.get("macroRegion").get("macroRegionId")


@dataclass
class Equipment:
    equipment_id: int
    name: str
    standard: EquipmentStandard
    type: EquipmentType
    macro_region_id: int

    def __init__(self, item: dict) -> None:
        self.equipment_id = item.get("equipmentId")
        self.name = item.get("name")
        self.standard = EquipmentStandard(item.get("standard"))
        self.type = EquipmentType(item.get("type"))
        self.macro_region_id = item.get("macroRegion").get("macroRegionId")

    @cached_property
    def is_type_def(self) -> bool:
        return self.standard.name in [
            default_standard_names.gsm_standard_name,
            default_standard_names.satellite_standard_name,
        ]


@dataclass
class PhoneNumberType:
    phone_number_type_id: int
    macro_region_id: int
    name: str
    standard: EquipmentStandard | None = None

    def __init__(self, item: dict) -> None:
        self.phone_number_type_id = item.get("phoneNumberTypeId")
        self.name = item.get("name")
        standard_item = item.get("standard")
        if standard_item is not None:
            self.standard = EquipmentStandard(standard_item)
        self.macro_region_id = item.get("macroRegion").get("macroRegionId")


@dataclass
class Operator:
    operator_id: int
    name: str
    macro_region_id: int

    def __init__(self, item: dict) -> None:
        self.operator_id = item.get("operatorId")
        self.name = item.get("name")
        self.macro_region_id = item.get("macroRegion").get("macroRegionId")


@dataclass
class PhoneNumberTypeLink:
    phone_number_type_link_id: int
    name: str

    def __init__(self, item: dict) -> None:
        self.operator_id = item.get("phoneNumberTypeLinkId")
        self.name = item.get("name")


@dataclass
class StockSystem:
    stock_system_id: int
    name: str
    code: str

    def __init__(self, item: dict) -> None:
        self.stock_system_id = item.get("stockSystemId")
        self.name = item.get("name")
        self.code = item.get("code")


@dataclass
class Nomenclature:
    code: str
    nomenclature_id: int
    name: str
    stock_system: StockSystem
    is_serial: bool

    def __init__(self, item: dict) -> None:
        self.code = item.get("code")
        self.nomenclature_id = item.get("nomenclatureId")
        self.name = item.get("name")
        self.stock_system = StockSystem(item.get("stockSystem"))
        self.is_serial = item.get("isSerial")


@dataclass
class InventoryItem:
    serial_number: str
    inventory_item_id: int
    reserved_code: str | None

    def __init__(self, item: dict) -> None:
        self.serial_number = item.get("serialNumber")
        self.inventory_item_id = item.get("inventoryItemId")
        self.reserved_code = item.get("reservedCode")
