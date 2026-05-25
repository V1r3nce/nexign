import allure

from api.base_requests import BaseRequests
from common.helpers.checker import assert_that
from common.helpers.data_generator import generate_english_string, random_numbers_except
from common.helpers.env_helper import BASE_URL_LIS
from models.lis_resources import APNInfo


class APNRequests(BaseRequests):
    @allure.step("API: Получение списка APN")
    def get_apn(self) -> dict:
        """
        Метод для получения информации по APN
        :return: json с информацией по APN
        """
        params = {"limit": 100, "offset": 0}
        payload = {"macroRegionIds": [0, 999], "serviceProviderCodes": ["DEFAULT"], "isActive": True}
        response = self.post(f"{BASE_URL_LIS}/ps/v1/logicalResources/accessPoints/search", json=payload, params=params)
        self.check_response_status(response, 200, "Не получен список с APN")
        return response.json()

    @allure.step("API: Получение последнего HLR Id")
    def generate_hlr_id(self) -> int:
        """
        Метод для получения нового HLR id
        :return: HLR id
        """
        apns = self.get_apn()["items"]
        hlr_ids = []
        for apn in apns:
            hlr_ids.append(apn["HLRAccessPointId"])
        return random_numbers_except(1000000, 9000000, hlr_ids)

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
    def add_apn(self, point_purpose_id: int = 2, point_type_id: int = 1) -> APNInfo:
        """
        Метод для добавления APN(точки доступа).
        :param point_purpose_id: id назначения точки доступа
        :param point_type_id: id типа точки доступа
        :return: AccessPointId идентификатор точки доступа
        """
        hlr_id = self.generate_hlr_id()
        new_apn_name = f"default.{generate_english_string(7)}.test"
        payload = {
            "name": new_apn_name,
            "HLRAccessPointId": f"{hlr_id}",
            "accessPointPurposeId": point_purpose_id,
            "accessPointTypeId": point_type_id,
            "macroRegionId": 0,
            "note": None,
            "serviceProviderCode": "DEFAULT",
            "isActive": True,
            "isConfiguredOnNetwork": False,
        }
        response = self.post(f"{BASE_URL_LIS}/ps/v1/logicalResources/private/accessPoints", json=payload)
        self.check_response_status(response, 201, "Не удалось добавить APN")
        new_id = response.json().get("accessPointId", None)
        assert_that(lambda: new_id is not None, "Id точки доступа не получен")
        return APNInfo(new_apn_name, new_id, hlr_id)
