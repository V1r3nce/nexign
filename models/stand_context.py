from functools import cached_property

from api.lis_requests.apn import APNRequests
from api.lis_requests.equipment import EquipmentRequests
from api.lis_requests.nomenclatures import NomenclatureRequests
from api.lis_requests.phone_numbers_reference_info import PhoneNumbersReferenceInfoRequests
from api.lis_requests.sim_cards_reference_info import SimCardsReferenceInfoRequests
from api.rfd_requests.refdata_requests import RefDataRequests
from common.enums.lis import (
    APNNames,
    DefaultNomenclatures,
    DefaultStandardNames,
    LisOperators,
    NomenclatureTemplates,
    PhoneLinkTypes,
    PhoneNumberCategories,
    PhoneNumberTypes,
    PhoneZoneCodes,
    SimTypes,
)
from common.helpers.checker import assert_that
from common.helpers.env_helper import GENERATE_RESOURCES
from models.lis_resources import (
    APNInfo,
    Equipment,
    EquipmentStandard,
    EquipmentType,
    Nomenclature,
    NumberCategory,
    Operator,
    PhoneNumberType,
    PhoneNumberTypeLink,
    SIMCardType,
    SIMTemplate,
)


class StandEquipment:
    __equipment_api: EquipmentRequests = EquipmentRequests()
    __phone_api: PhoneNumbersReferenceInfoRequests = PhoneNumbersReferenceInfoRequests()
    __sim_api: SimCardsReferenceInfoRequests = SimCardsReferenceInfoRequests()
    __nomenclature_api: NomenclatureRequests = NomenclatureRequests()
    __refdata_api: RefDataRequests = RefDataRequests()
    __apn_api: APNRequests = APNRequests()
    sim_project_id: int = 0
    macro_region_id: int = 999
    macro_region_ids: list = [0, 999]

    # common
    @cached_property
    def types(self) -> list[EquipmentType]:
        items = self.__equipment_api.get_equipments_types()
        equipment_types = []
        for item in items:
            equipment_types.append(EquipmentType.model_validate(item))
        return equipment_types

    @cached_property
    def standards(self) -> list[EquipmentStandard]:
        items = self.__equipment_api.get_equipment_standards()
        equipment_standard = []
        for item in items:
            equipment_standard.append(EquipmentStandard.model_validate(item))
        return equipment_standard

    @cached_property
    def equipment_list(self) -> list[Equipment]:
        items = self.__equipment_api.get_equipment()
        equipment = []
        for item in items:
            if item.get("isActive"):
                equipment.append(Equipment.model_validate(item))
        return equipment

    @cached_property
    def nomenclatures(self) -> list[Nomenclature]:
        nomenclatures: list[Nomenclature] = []

        def update_list() -> None:
            all_nomenclatures = self.__nomenclature_api.get_nomenclatures()
            for item in all_nomenclatures:
                if item.get("isActive") and any(
                    [pattern in item.get("code") for pattern in NomenclatureTemplates.as_list()]
                ):
                    if item.get("code") not in [nomenclature.code for nomenclature in nomenclatures]:
                        nomenclatures.append(Nomenclature.model_validate(item))

        update_list()
        existing_codes = [nomenclature.code for nomenclature in nomenclatures]
        flag_if_set_exists = False
        for nomenclatures_set in DefaultNomenclatures.nomenclatures_list:
            flag_if_set_exists = True
            for nomenclature in nomenclatures_set:
                nomenclature_hit = False
                for existing_nomenclature in existing_codes:
                    if nomenclature in existing_nomenclature:
                        nomenclature_hit = True
                        break
                if not nomenclature_hit:
                    flag_if_set_exists = False
                    break
            if flag_if_set_exists:
                break
        if not flag_if_set_exists:
            for nomenclature in DefaultNomenclatures.invest_nomenclatures:
                if nomenclature not in existing_codes:
                    self.__nomenclature_api.add_nomenclature(
                        stock_system_id=self.partner_point_id, code=nomenclature, is_serial=True
                    )
        update_list()
        return nomenclatures

    @cached_property
    def partner_point_id(self) -> int:
        points = self.__refdata_api.get_partner_points_list(add_address_string=False, show_actual_only=True)
        return points[0].get("referenceItemCode")

    @cached_property
    def phone_numbers_types(self) -> list[PhoneNumberType]:
        all_types = self.__phone_api.get_phone_numbers_types(self.macro_region_ids)
        types = []
        for phone_type in all_types:
            if phone_type.get("isActive"):
                types.append(PhoneNumberType.model_validate(phone_type))
        return types

    @cached_property
    def operators(self) -> list[Operator]:
        all_operators = self.__phone_api.get_operators(self.macro_region_ids)
        operators = []
        for operator in all_operators:
            if operator.get("isActive"):
                operators.append(Operator.model_validate(operator))
        return operators

    @cached_property
    def phone_number_type_links(self) -> list[PhoneNumberTypeLink]:
        all_links = self.__phone_api.get_phone_numbers_type_links(self.macro_region_ids)
        phone_links = []
        for link in all_links:
            phone_links.append(PhoneNumberTypeLink.model_validate(link))
        return phone_links

    @cached_property
    def numbers_categories(self) -> list[NumberCategory]:
        result = []
        for number_category in self.__phone_api.get_numbers_categories(self.macro_region_ids):
            if number_category.get("isActive"):
                result.append(NumberCategory.model_validate(number_category))
        return result

    @cached_property
    def apns(self) -> list[APNInfo]:
        all_info = self.__apn_api.get_apn()
        apns = []
        for apn in all_info.get("items", []):
            apns.append(APNInfo(apn))
        return apns

    @cached_property
    def sim_template(self) -> SIMTemplate:
        return self.__sim_api.get_sims_template(self.macro_region_ids)

    @cached_property
    def sim_type_id(self) -> int:
        return self.default_sim_type.sim_card_type_id

    # common default
    @cached_property
    def default_apn(self) -> APNInfo | None:
        all_apns = self.apns
        for apn in all_apns:
            if APNNames.nexign_default in apn.name:
                return apn
        return None

    @cached_property
    def phone_number_federal_type(self) -> PhoneNumberType:
        all_types = self.phone_numbers_types
        for item in all_types:
            if item.name == PhoneNumberTypes.federal:
                return item
        raise AssertionError("Не найдено обычного типа нумерации Федеральный")

    @cached_property
    def default_number_category(self) -> NumberCategory:
        all_categories = self.numbers_categories
        for category in all_categories:
            if PhoneNumberCategories.telephony in category.name:
                return category
        raise AssertionError("Не найдено обычной категории номеров")

    @cached_property
    def operator_def(self) -> Operator:
        for operator in self.operators:
            if operator.name in LisOperators.def_operators():
                return operator
        raise AssertionError("Не найдено обычного DEF оператора")

    @cached_property
    def operator_8800(self) -> Operator | None:
        for operator in self.operators:
            if operator.name == LisOperators.dbl_eight_dbl_zero:
                return operator
        return None

    @cached_property
    def phone_def_type_link(self) -> PhoneNumberTypeLink:
        for type_link in self.phone_number_type_links:
            if PhoneLinkTypes.flexible in type_link.name:
                return type_link
        raise AssertionError("Не найдено обычной DEF связки")

    @cached_property
    def default_sim_type(self) -> SIMCardType:
        types = self.__sim_api.get_sims_types(self.macro_region_ids)
        for sim_type in types:
            if sim_type.name == SimTypes.standard:
                return sim_type
        raise AssertionError("Не найдено обычного типа SIM-карты")

    # def(gsm + satellite)
    @cached_property
    def gsm_equipments(self) -> list[Equipment]:
        all_equipment = self.equipment_list
        gsm_equipment = []
        for item in all_equipment:
            if item.standard.name == DefaultStandardNames.gsm_standard_name:
                gsm_equipment.append(item)
        return gsm_equipment

    @cached_property
    def gsm_equipment(self) -> Equipment:
        return self.gsm_equipments[0]

    @cached_property
    def satellite_equipments(self) -> list[Equipment]:
        all_equipment = self.equipment_list
        satellite_equipment = []
        for item in all_equipment:
            if item.standard.name in DefaultStandardNames.satellite_standard_names:
                satellite_equipment.append(item)
        return satellite_equipment

    @cached_property
    def default_satellite_equipment(self) -> Equipment:
        satellite_equipment = self.satellite_equipments
        assert_that(lambda: len(satellite_equipment) != 0, "Отсутствуют коммутаторы стандарта Спутниковая связь")
        return satellite_equipment[0]

    # pstn
    @cached_property
    def pstn_equipments(self) -> list[Equipment]:
        all_equipment = self.equipment_list
        pstn_equipment = []
        for item in all_equipment:
            if item.standard.name == DefaultStandardNames.pstn_standard_name:
                pstn_equipment.append(item)
        return pstn_equipment

    @cached_property
    def pstn_abc_equipment(self) -> Equipment | None:
        all_equipment = self.equipment_list
        for item in all_equipment:
            if item.standard.name == DefaultStandardNames.pstn_standard_name and PhoneZoneCodes.abc in item.name:
                return item
        return None

    @cached_property
    def pstn_8800_equipment(self) -> Equipment | None:
        all_equipment = self.equipment_list
        for item in all_equipment:
            if (
                item.standard.name == DefaultStandardNames.pstn_standard_name
                and PhoneZoneCodes.dbl_eight_dbl_zero in item.name
            ):
                return item
        return None

    # evaluate functions
    def get_phone_type_by_equipment(self, equipment: Equipment) -> PhoneNumberType:
        phone_type_to_equipment_map: dict = {PhoneNumberTypes.fixed: PhoneZoneCodes.abc}
        if equipment.standard.name in DefaultStandardNames.def_standard_names:
            return self.phone_number_federal_type
        for phone_type in self.phone_numbers_types:
            current_standard = getattr(phone_type.standard, "standard_id", -1)
            if current_standard == -1 or current_standard == equipment.standard.standard_id:
                if phone_type.name in equipment.name or (
                    phone_type_to_equipment_map.get(phone_type.name, "unknown_type") in equipment.name
                ):
                    return phone_type
        raise ValueError("Невозможно определить тип нумерации по коммутатору")

    def get_operator_by_equipment(self, equipment: Equipment) -> Operator:
        if self.operator_8800 is not None and self.operator_8800.name in equipment.name.replace("-", ""):
            return self.operator_8800
        else:
            return self.operator_def

    def get_standard_by_enum(self, standard: DefaultStandardNames) -> EquipmentStandard:
        standard_list = self.standards
        for item in standard_list:
            if item.name in standard:
                return item
        raise ValueError("Невозможно получить стандарт связи")


class StandContext:
    stand_equipment: StandEquipment = StandEquipment()
    generate_inventory_count: int = 500
    generate_sim_count: int = 1000
    generate_number_count: int = 1000
    generate_ips_count: int = 100
    generate_apns_count: int = 3
    force_generate: bool = GENERATE_RESOURCES


stand_context = StandContext()
