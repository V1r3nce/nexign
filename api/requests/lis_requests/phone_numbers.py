from dataclasses import dataclass

import allure
from playwright.sync_api import APIRequestContext, APIResponse

from api.requests.base_requests import BaseRequests
from common.helpers.data_generator import generate_random_number
from common.helpers.env_helper import BASE_URL_LIS


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
    def __init__(self, api_request_auth_context: APIRequestContext, macro_region_id: int = 999):
        super().__init__(api_request_auth_context)
        self.macro_region_id = macro_region_id

    @allure.step("API: Получить список телефонных номеров LIS")
    def get_phone_numbers(
        self,
        type_def: bool = True,
        status_id: list | None = None,
        state_id: list | None = None,
        num_sort: str | None = None,
        is_reserved: bool | str | None = None,
        class_ids: list | None = None,
    ) -> APIResponse:
        """
        Получить список телефонных номеров LIS
        """
        payload = {
            "returnCount": True,
            "macroRegionIds": [self.macro_region_id],
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
        params = {"limit": 50, "offset": 0}
        if num_sort:
            params["sort"] = num_sort
        phone_numbers = self.post(
            url=f"{BASE_URL_LIS}/OAPI/v1/lis/logicalResources/phoneNumbers/search", data=payload, params=params
        )
        self.check_response_status(phone_numbers, 200, "Не получен список телефонных номеров")
        return phone_numbers

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
        payload = {"macroRegionId": self.macro_region_id, "isTypeDEF": type_def}
        if phone_number_purpose_id:
            payload["phoneNumberPurposeId"] = phone_number_purpose_id
        if phone_number_type_link_id:
            payload["phoneNumberTypeLinkId"] = phone_number_type_link_id
        for phone_number_id in phone_number_ids:
            phone_numbers = self.put(
                url=f"{BASE_URL_LIS}/OAPI/v1/lis/logicalResources/phoneNumbers/{phone_number_id}", data=payload
            )
            self.check_response_status(phone_numbers, 204, "Не обновлен список телефонных номеров")

    @allure.step("API: Добавить список телефонных номеров LIS")
    def add_phone_numbers(
        self,
        start_number: str,
        count_number: str,
        type_def: bool = True,
        phone_number_type_id: int = 1,
        operator_id: int = 100001,
        equipment_id: int = 100001,
        phone_number_type_link_id: int | None = None,
    ) -> APIResponse:
        """
        Добавить список телефонных номеров LIS
        """
        payload = {
            "startPhoneNumber": start_number,
            "countPhoneNumber": count_number,
            "phoneNumberTypeId": phone_number_type_id,
            "numberCategoryId": 1,
            "operatorId": operator_id,
            "phoneNumberClassTemplateIds": [],
            "equipmentId": equipment_id,
            "isTypeDEF": type_def,
            "macroRegionId": self.macro_region_id,
        }
        if phone_number_type_link_id:
            payload["phoneNumberTypeLinkId"] = phone_number_type_link_id
        add_phone_numbers = self.post(
            url=f"{BASE_URL_LIS}/OAPI/v1/lis/logicalResources/phoneNumbers/generationBulkAsync", data=payload
        )
        self.check_response_status(add_phone_numbers, 204, "Не добавлены номера")
        return add_phone_numbers

    @allure.step("API: Ввести в эксплуатацию список телефонных номеров LIS")
    def set_phone_numbers_in_use(self, phone_number_ids: list, type_def: bool = True) -> APIResponse:
        payload = {"macroRegionId": self.macro_region_id, "phoneNumberIds": phone_number_ids, "isTypeDEF": type_def}
        add_phone_numbers = self.post(
            url=f"{BASE_URL_LIS}/OAPI/v1/lis/logicalResources/phoneNumbers/inUseBulk", data=payload
        )
        self.check_response_status(add_phone_numbers, 200, "Не введены в эксплуатацию номера")
        return add_phone_numbers

    @allure.step("API: Зарезервировать список телефонных номеров LIS")
    def set_phone_numbers_reserved(self, phone_number_ids: list) -> APIResponse:
        payload = {"macroRegionId": self.macro_region_id, "phoneNumberIds": phone_number_ids, "note": "Автотест резерв"}
        reserve_phone_numbers = self.post(
            url=f"{BASE_URL_LIS}/OAPI/v1/lis/logicalResources/phoneNumbers/setReservedStateBulk", data=payload
        )
        self.check_response_status(reserve_phone_numbers, 200, "Не зарезервированы телефонные номера")
        return reserve_phone_numbers

    @staticmethod
    def get_numbers_data(numbers_response: APIResponse) -> list:
        """Получить данные по телефонам в виде объектов"""
        return [PhoneNumberData(item) for item in numbers_response.json()["items"]]

    @staticmethod
    def get_numbers_data_without_phone_number_abc(numbers_response: APIResponse) -> list:
        """Получить данные по телефонам в виде объектов при условии, что phoneNumberABC для номера null"""
        return [PhoneNumberData(item) for item in numbers_response.json()["items"] if item["phoneNumberABC"] is None]

    @allure.step("API: Получить список шаблонов поиска телефонных номеров LIS")
    def get_phone_numbers_templates(self) -> APIResponse:
        payload = {"macroRegionIds": self.macro_region_id, "limit": 0, "offset": 0}
        params = {"limit": 0, "offset": 0}
        templates = self.post(
            url=f"{BASE_URL_LIS}/OAPI/v1/lis/logicalResources/phoneNumbers/filterTemplates/search",
            data=payload,
            params=params,
        )
        self.check_response_status(templates, 200, "Не получен список шаблонов телефонных номеров")
        return templates

    @allure.step("API: Удалить шаблон поиска телефонных номеров LIS")
    def delete_phone_numbers_template(self, template_id: str) -> APIResponse:
        delete_template = self.delete(
            url=f"{BASE_URL_LIS}/OAPI/v1/lis/logicalResources/phoneNumbers/filterTemplates/{template_id}"
        )
        self.check_response_status(delete_template, 204, "Не удален шаблон поиска телефонных номеров")
        return delete_template

    @allure.step("Блокировка телефонных номеров LIS")
    def lock_phone_numbers(self, phone_number_ids: list, lock_id: str = str(generate_random_number(8))) -> APIResponse:
        payload = {"phoneNumberIds": phone_number_ids, "lockId": lock_id}
        lock_phone_numbers = self.post(
            url=f"{BASE_URL_LIS}/openapi/v1/logicalResources/phoneNumbers/reserveBulk", data=payload
        )
        self.check_response_status(lock_phone_numbers, 200, "Не заблокированы телефонные номера")
        return lock_phone_numbers
