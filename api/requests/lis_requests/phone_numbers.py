import allure
from playwright.sync_api import APIRequestContext, APIResponse
from dataclasses import dataclass

from common.helpers.data_generator import generate_random_number
from common.helpers.env_helper import BASE_URL_LIS


@dataclass
class PhoneNumberData:
    """Класс для данных по номеру телефона"""
    phone_data: dict

    def __post_init__(self):
        self.MSISDN = self.phone_data["MSISDN"]
        self.phone_number_id = self.phone_data["phoneNumberId"]
        self.class_name = self.phone_data['numberClass']['name']
        self.phone_number_abc = self.phone_data['phoneNumberABC']


class PhoneNumbersRequests:
    def __init__(self, api_request_auth_context: APIRequestContext):
        self.api_request_auth_context = api_request_auth_context

    @allure.step("Получить список телефонных номеров LIS")
    def get_phone_numbers(self, type_def: bool = True, status_id: [None, list] = None,
                          state_id: [None, list] = None, num_sort: [None, str] = None,
                          is_reserved: [bool, str, None] = None, class_ids: [None, list] = None) -> APIResponse:
        """
        Получить список телефонных номеров LIS
        """
        payload = {"returnCount": True, "macroRegionIds": [1], "isTypeDEF": type_def, "includeInternalMNP": True}
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
        phone_numbers = self.api_request_auth_context.post(url=f"{BASE_URL_LIS}/OAPI/v1/lis/logicalResources/phoneNumbers/search",
                                                           data=payload, params=params)
        assert phone_numbers.status == 200, "Не получен список телефонных номеров"
        return phone_numbers

    @allure.step("Обновить список телефонных номеров LIS")
    def update_phone_numbers(self, phone_number_ids: list, phone_number_purpose_id: [int, None] = None,
                             phone_number_type_link_id: [int, None] = None):
        """
        Обновить список телефонных номеров LIS
        """
        payload = {"macroRegionId": 1, "phoneNumberIds": phone_number_ids, "phoneNumberPurposeId": 1}
        if phone_number_purpose_id:
            payload["phoneNumberPurposeId"] = phone_number_purpose_id
        if phone_number_type_link_id:
            payload["phoneNumberTypeLinkId"] = phone_number_type_link_id
        phone_numbers = self.api_request_auth_context.post(url=f"{BASE_URL_LIS}/OAPI/v1/lis/logicalResources/phoneNumbers/updateBulk",
                                                           data=payload)
        assert phone_numbers.status == 200, "Не обновлен список телефонных номеров"
        return phone_numbers

    @allure.step("Добавить список телефонных номеров LIS")
    def add_phone_numbers(self, start_number: str, count_number: str, type_def: bool = True):
        """
        Добавить список телефонных номеров LIS
        """
        payload = {"startPhoneNumber": start_number,
                   "countPhoneNumber": count_number,
                   "phoneNumberTypeId": 1,
                   "numberCategoryId": 1,
                   "operatorId": 1,
                   "phoneNumberClassTemplateIds": [],
                   "equipmentId": 2,
                   "isTypeDEF": type_def,
                   "macroRegionId": 1}
        add_phone_numbers = self.api_request_auth_context.post(
            url=f"{BASE_URL_LIS}/OAPI/v1/lis/logicalResources/phoneNumbers/generationBulkAsync",
            data=payload)
        assert add_phone_numbers.status == 204, (f"Не добавлены номера, вернулся статус {add_phone_numbers.status} "
                                                 f"и ответ {add_phone_numbers.text()}")
        return add_phone_numbers

    @allure.step("Ввести в эксплуатацию список телефонных номеров LIS")
    def set_phone_numbers_in_use(self, phone_number_ids: list, type_def: bool = True):
        payload = {"macroRegionId": 1, "phoneNumberIds": phone_number_ids, "isTypeDEF": type_def}
        add_phone_numbers = self.api_request_auth_context.post(
            url=f"{BASE_URL_LIS}/OAPI/v1/lis/logicalResources/phoneNumbers/inUseBulk",
            data=payload)
        assert add_phone_numbers.status == 200, (f"Не введены в эксплуатацию номера, вернулся статус"
                                                 f" {add_phone_numbers.status} и ответ {add_phone_numbers.text()}")
        return add_phone_numbers

    @allure.step("Зарезервировать список телефонных номеров LIS")
    def set_phone_numbers_reserved(self, phone_number_ids: list):
        payload = {"macroRegionId": 1, "phoneNumberIds": phone_number_ids, "note": "Автотест резерв"}
        reserve_phone_numbers = self.api_request_auth_context.post(
            url=f"{BASE_URL_LIS}/OAPI/v1/lis/logicalResources/phoneNumbers/setReservedStateBulk",
            data=payload)
        assert reserve_phone_numbers.status == 200, \
            (f"Не зарезервированы телефонные номера, вернулся статус {reserve_phone_numbers.status} "
             f"и ответ {reserve_phone_numbers.text()}")
        return reserve_phone_numbers

    @staticmethod
    def get_numbers_data(numbers_response: APIResponse):
        """Получить данные по телефонам в виде объектов"""
        return [PhoneNumberData(item) for item in numbers_response.json()['items']]

    @staticmethod
    def get_numbers_data_without_phone_number_abc(numbers_response: APIResponse):
        """Получить данные по телефонам в виде объектов при условии, что phoneNumberABC для номера null"""
        return [PhoneNumberData(item) for item in numbers_response.json()['items'] if item['phoneNumberABC'] is None]

    @allure.step("Получить список шаблонов поиска телефонных номеров LIS")
    def get_phone_numbers_templates(self):
        payload = {"macroRegionIds": 1, "limit": 0, "offset": 0}
        params = {"limit": 0, "offset": 0}
        templates = self.api_request_auth_context.post(url=f"{BASE_URL_LIS}/OAPI/v1/lis/logicalResources/phoneNumbers/filterTemplates/search",
                                                       data=payload, params=params)
        assert templates.status == 200, "Не получен список шаблонов телефонных номеров"
        return templates

    @allure.step("Удалить шаблон поиска телефонных номеров LIS")
    def delete_phone_numbers_template(self, template_id: str):
        delete_template = self.api_request_auth_context.delete(url=f"{BASE_URL_LIS}/OAPI/v1/lis/logicalResources/phoneNumbers/filterTemplates/{template_id}")
        assert delete_template.status == 204, "Не удален шаблон поиска телефонных номеров"
        return delete_template

    @allure.step("Блокировка телефонных номеров LIS")
    def lock_phone_numbers(self, phone_number_ids: list, lock_id: str = str(generate_random_number(8))):
        payload = {"phoneNumberIds": phone_number_ids, "lockId": lock_id}
        lock_phone_numbers = self.api_request_auth_context.post(
            url=f"{BASE_URL_LIS}/openapi/v1/logicalResources/phoneNumbers/reserveBulk",
            data=payload)
        assert lock_phone_numbers.status == 200, \
            (f"Не заблокированы телефонные номера, вернулся статус {lock_phone_numbers.status} "
             f"и ответ {lock_phone_numbers.text()}")
        return lock_phone_numbers
