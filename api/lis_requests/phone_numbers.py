from dataclasses import dataclass

import allure
import pytest

from api.base_requests import BaseRequests
from common.helpers.checker import check_that, wait_that
from common.helpers.data_generator import generate_random_number
from common.helpers.env_helper import BASE_URL_LIS
from models.lis_resources import Equipment, Operator, PhoneNumberType, PhoneNumberTypeLink
from models.playwright_bridge import GeneralResponse
from models.stand_context import stand_context


@dataclass
class PhoneNumberData:
    """Класс для данных по номеру телефона"""

    phone_data: dict

    def __post_init__(self) -> None:
        self.MSISDN = self.phone_data["MSISDN"]
        self.class_name = self.phone_data["numberClass"]["name"]
        self.class_id = self.phone_data["numberClass"]["numberClassId"]
        self.phone_number_id = self.phone_data.get("phoneNumberId")
        self.phone_number_abc = self.phone_data.get("phoneNumberABC")
        self.phone_number_abc = self.phone_data.get("switch").get("equipmentId")


class PhoneNumbersRequests(BaseRequests):
    @pytest.mark.lis
    def __init__(self) -> None:
        super().__init__()

    @allure.step("API: Получить список телефонных номеров LIS")
    def get_phone_numbers(
        self,
        type_def: bool = True,
        status_id: list | None = None,
        state_id: list | None = None,
        num_sort: str | None = None,
        is_reserved: bool | str | None = None,
        class_ids: list | None = None,
        equipment_ids: list | None = None,
        macro_region_id: int = 999,
        limit: int = 50,
    ) -> dict:
        """
        Получить список телефонных номеров LIS
        """
        payload = {
            "returnCount": True,
            "macroRegionIds": [macro_region_id],
            "isTypeDEF": type_def,
            "includeInternalMNP": True,
        }
        if is_reserved is not None:
            payload["isReserved"] = is_reserved
        if status_id:
            payload["statusIds"] = status_id
        if state_id:
            payload["stateIds"] = state_id
        if class_ids:
            payload["numberClassIds"] = class_ids
        if equipment_ids:
            payload["equipmentIds"] = equipment_ids
        params = {"limit": limit, "offset": 0}
        if num_sort:
            params["sort"] = num_sort
        phone_numbers = self.post(
            url=f"{BASE_URL_LIS}/OAPI/v1/lis/logicalResources/phoneNumbers/search", json=payload, params=params
        )
        self.check_response_status(phone_numbers, 200, "Не получен список телефонных номеров")
        return phone_numbers.json()

    @allure.step("API: Обновить список телефонных номеров LIS")
    def update_phone_numbers(
        self,
        phone_number_ids: list,
        phone_number_purpose_id: int | None = None,
        phone_number_type_link_id: int | None = None,
        type_def: bool = True,
    ) -> None:
        """
        Обновить список телефонных номеров LIS
        """
        payload = {"macroRegionId": stand_context.stand_equipment.macro_region_id, "isTypeDEF": type_def}
        if phone_number_purpose_id:
            payload["phoneNumberPurposeId"] = phone_number_purpose_id
        if phone_number_type_link_id:
            payload["phoneNumberTypeLinkId"] = phone_number_type_link_id
        for phone_number_id in phone_number_ids:
            phone_numbers = self.put(
                url=f"{BASE_URL_LIS}/OAPI/v1/lis/logicalResources/phoneNumbers/{phone_number_id}", json=payload
            )
            self.check_response_status(phone_numbers, 204, "Не обновлен список телефонных номеров")

    @allure.step("API: Добавить список телефонных номеров LIS")
    def add_phone_numbers(
        self,
        start_number: str,
        count_number: str,
        phone_number_type: PhoneNumberType | None = None,
        operator: Operator | None = None,
        equipment: Equipment | None = None,
        phone_number_type_link: PhoneNumberTypeLink | None = None,
    ) -> GeneralResponse:
        """
        Добавить список телефонных номеров LIS
        """
        payload = {
            "startPhoneNumber": start_number,
            "countPhoneNumber": count_number,
            "phoneNumberTypeId": stand_context.stand_equipment.phone_number_federal_type.phone_number_type_id
            if phone_number_type is None
            else phone_number_type.phone_number_type_id,
            "numberCategoryId": stand_context.stand_equipment.number_category_id,
            "operatorId": stand_context.stand_equipment.operator_def.operator_id
            if operator is None
            else operator.operator_id,
            "phoneNumberClassTemplateIds": [],
            "equipmentId": stand_context.stand_equipment.gsm_equipment.equipment_id
            if equipment is None
            else equipment.equipment_id,
            "isTypeDEF": True if equipment is None else equipment.is_type_def,
            "macroRegionId": stand_context.stand_equipment.gsm_equipment.macro_region_id
            if equipment is None
            else equipment.macro_region_id,
        }
        if phone_number_type_link:
            payload["phoneNumberTypeLinkId"] = phone_number_type_link.phone_number_type_link_id
        add_phone_numbers = self.post(
            url=f"{BASE_URL_LIS}/OAPI/v1/lis/logicalResources/phoneNumbers/generationBulkAsync", json=payload
        )
        self.check_response_status(add_phone_numbers, 204, "Не добавлены номера")
        return add_phone_numbers

    @allure.step("API: Ввести в эксплуатацию список телефонных номеров LIS")
    def set_phone_numbers_in_use(
        self, phone_number_ids: list, type_def: bool = True, macro_region_id: int | None = None
    ) -> GeneralResponse:
        payload = {
            "macroRegionId": stand_context.stand_equipment.macro_region_id
            if macro_region_id is None
            else macro_region_id,
            "phoneNumberIds": phone_number_ids,
            "isTypeDEF": type_def,
        }
        add_phone_numbers = self.post(
            url=f"{BASE_URL_LIS}/OAPI/v1/lis/logicalResources/phoneNumbers/inUseBulk", json=payload, timeout=120
        )
        self.check_response_status(add_phone_numbers, 200, "Не введены в эксплуатацию номера")
        return add_phone_numbers

    @allure.step("API: Зарезервировать список телефонных номеров LIS")
    def set_phone_numbers_reserved(self, phone_number_ids: list) -> GeneralResponse:
        payload = {
            "macroRegionId": stand_context.stand_equipment.macro_region_id,
            "phoneNumberIds": phone_number_ids,
            "note": "Автотест резерв",
        }
        reserve_phone_numbers = self.post(
            url=f"{BASE_URL_LIS}/OAPI/v1/lis/logicalResources/phoneNumbers/setReservedStateBulk", json=payload
        )
        self.check_response_status(reserve_phone_numbers, 200, "Не зарезервированы телефонные номера")
        return reserve_phone_numbers

    @staticmethod
    def get_numbers_data(numbers_response: dict) -> list:
        """Получить данные по телефонам в виде объектов"""
        return [PhoneNumberData(item) for item in numbers_response["items"]]

    @staticmethod
    def get_numbers_data_without_phone_number_abc(numbers_response: dict) -> list:
        """Получить данные по телефонам в виде объектов при условии, что phoneNumberABC для номера null"""
        return [PhoneNumberData(item) for item in numbers_response["items"] if item["phoneNumberABC"] is None]

    @allure.step("API: Получить список шаблонов поиска телефонных номеров LIS")
    def get_phone_numbers_templates(self) -> GeneralResponse:
        payload = {"macroRegionIds": stand_context.stand_equipment.macro_region_id, "limit": 0, "offset": 0}
        params = {"limit": 0, "offset": 0}
        templates = self.post(
            url=f"{BASE_URL_LIS}/OAPI/v1/lis/logicalResources/phoneNumbers/filterTemplates/search",
            json=payload,
            params=params,
        )
        self.check_response_status(templates, 200, "Не получен список шаблонов телефонных номеров")
        return templates

    @allure.step("API: Удалить шаблон поиска телефонных номеров LIS")
    def delete_phone_numbers_template(self, template_id: str) -> GeneralResponse:
        delete_template = self.delete(
            url=f"{BASE_URL_LIS}/OAPI/v1/lis/logicalResources/phoneNumbers/filterTemplates/{template_id}"
        )
        self.check_response_status(delete_template, 204, "Не удален шаблон поиска телефонных номеров")
        return delete_template

    @allure.step("Блокировка телефонных номеров LIS")
    def lock_phone_numbers(
        self, phone_number_ids: list, lock_id: str = str(generate_random_number(8))
    ) -> GeneralResponse:
        payload = {"phoneNumberIds": phone_number_ids, "lockId": lock_id}
        lock_phone_numbers = self.post(
            url=f"{BASE_URL_LIS}/openapi/v1/logicalResources/phoneNumbers/reserveBulk", json=payload
        )
        self.check_response_status(lock_phone_numbers, 200, "Не заблокированы телефонные номера")
        return lock_phone_numbers

    @allure.step("API: Получение добавленных номеров")
    def get_added_phone_numbers(self, equipment: Equipment, limit: int = 50) -> list:
        return self.get_numbers_data(
            self.get_phone_numbers(
                num_sort="-MSISDN",
                type_def=equipment.is_type_def,
                macro_region_id=equipment.macro_region_id,
                status_id=[3],
                state_id=[1],
                equipment_ids=[equipment.equipment_id],
                limit=limit,
            )
        )

    @allure.step("API: Ожидание добавления номеров")
    def wait_added_phone_number(self, equipment: Equipment, start_number: int, count: int) -> list:
        number_list = [start_number + i for i in range(count)]
        expected_optimal_count = 2 * count
        wait_that(
            lambda: number_list[-1]
            in [int(number_data.MSISDN) for number_data in self.get_added_phone_numbers(equipment)],
            timeout=180,
            sleep_seconds=5,
            exception=AssertionError,
            message="Добавленные номера не появились в списке",
        )
        numbers = self.get_added_phone_numbers(equipment, limit=expected_optimal_count)
        number_ids: list[int] = []
        i = 0
        while i < len(numbers) and len(number_ids) != count:
            if int(numbers[i].MSISDN) in number_list:
                number_ids.append(numbers[i].phone_number_id)
            i += 1
        check_that(lambda: len(number_list) == len(number_ids), ValueError, "Не удалось получить список id номеров")
        return number_ids

    @allure.step("Генерация номеров")
    def generate_numbers(self, count: int, equipment: Equipment) -> None:
        """
        phones = number_requests.get_phone_numbers(num_sort="-MSISDN")
        def_data = number_requests.get_numbers_data(phones)
        new_number = int(def_data[0].MSISDN) + 1
        number_requests.add_phone_numbers(new_number, "1", equipment_id=equipment_id)
        number_volume_page.set_number_in_use(new_number)
        """
        available_count = (
            self.get_phone_numbers(
                type_def=equipment.is_type_def,
                state_id=[2],
                status_id=[1],
                equipment_ids=[equipment.equipment_id],
                macro_region_id=equipment.macro_region_id,
            )
            .get("listInfo", {})
            .get("count", 0)
        )
        if not stand_context.force_generate and available_count > count:
            return
        phone_type = stand_context.stand_equipment.get_phone_type_by_equipment(equipment=equipment)
        operator = stand_context.stand_equipment.get_operator_by_equipment(equipment)
        phones = self.get_phone_numbers(
            num_sort="-MSISDN", type_def=equipment.is_type_def, macro_region_id=equipment.macro_region_id
        )
        data = self.get_numbers_data(phones)
        if len(data) == 0:
            if equipment.is_type_def:
                start_number = 9210000000
            elif stand_context.stand_equipment.pstn_8800_equipment.equipment_id == equipment.equipment_id:
                start_number = 8000000000
            elif stand_context.stand_equipment.pstn_abc_equipment.equipment_id == equipment.equipment_id:
                start_number = 1920000000
            else:
                start_number = 0
        else:
            start_number = int(data[0].MSISDN) + 1
        self.add_phone_numbers(
            start_number=str(start_number),
            count_number=str(count),
            equipment=equipment,
            phone_number_type=phone_type,
            operator=operator,
        )

        number_ids = self.wait_added_phone_number(equipment, start_number, count)

        self.set_phone_numbers_in_use(
            phone_number_ids=number_ids, type_def=equipment.is_type_def, macro_region_id=equipment.macro_region_id
        )
