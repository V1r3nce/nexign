import allure
from playwright.sync_api import APIRequestContext

from api.base_requests import BaseRequests
from common.helpers.data_generator import generate_english_string
from common.helpers.env_helper import BASE_URL_LIS


class APNRequests(BaseRequests):
    def __init__(self, api_request_auth_context: APIRequestContext):
        super().__init__(api_request_auth_context)

    @allure.step("API: Получение списка APN")
    def get_apn(self) -> dict:
        """
        Метод для получения информации по APN
        :return: json с информацией по APN
        """
        payload = {"macroRegionIds": [0, 999], "serviceProviderCodes": ["DEFAULT"], "isActive": True}
        response = self.post(f"{BASE_URL_LIS}/ps/v1/logicalResources/accessPoints/search", data=payload)
        self.check_response_status(response, 200, "Не получен список с APN")
        return response.json()

    @allure.step("API: Получение последнего HLR Id")
    def get_apn_last_hlr_id(self) -> int:
        """
        Метод для получения наибольшего(последнего) HLR id
        :return: HLR id
        """
        apns = self.get_apn()["items"]
        hlr_ids = []
        for apn in apns:
            hlr_ids.append(apn["HLRAccessPointId"])
        hlr_ids.sort()
        return hlr_ids[-1]

    @allure.step("API: Получить AccessPointId по названию APN")
    def get_apn_access_point_id_by_name(self, apn_name: str) -> int | None:
        """
        Метод для получения id точки доступа по ее названию
        :param apn_name: имя точки доступа
        :return: id точки доступа
        """
        apns = self.get_apn()["items"]
        for apn in apns:
            if apn["name"] == apn_name:
                return apn["accessPointId"]
        return None

    @allure.step("API: Добавить APN")
    def add_apn(self, point_purpose_id: int = 2, point_type_id: int = 1) -> int | None:
        """
        Метод для добавления APN(точки доступа).
        :param point_purpose_id: id назначения точки доступа
        :param point_type_id: id типа точки доступа
        :return: AccessPointId идентификатор точки доступа
        """
        last_hlr_id = self.get_apn_last_hlr_id()
        new_apn_name = f"default.{generate_english_string(7)}.test"
        payload = {
            "name": new_apn_name,
            "HLRAccessPointId": f"{last_hlr_id + 1}",
            "accessPointPurposeId": point_purpose_id,
            "accessPointTypeId": point_type_id,
            "macroRegionId": 0,
            "note": None,
            "serviceProviderCode": "DEFAULT",
            "isActive": True,
            "isConfiguredOnNetwork": False,
        }
        response = self.post(f"{BASE_URL_LIS}/ps/v1/logicalResources/private/accessPoints", data=payload)
        self.check_response_status(response, 201, "Не удалось добавить APN")
        return self.get_apn_access_point_id_by_name(new_apn_name)
