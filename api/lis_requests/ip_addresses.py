import allure
import pytest

from api.base_requests import BaseRequests
from common.helpers.checker import assert_that, wait_that
from common.helpers.data_generator import generate_ip_list, generate_next_ip
from common.helpers.env_helper import BASE_URL_LIS
from models.lis_resources import APNInfo, IPInfo
from models.stand_context import stand_context


class IpAddressRequests(BaseRequests):
    """
    Класс для управления ip адресами с помощью api запросов
    """

    @pytest.mark.lis
    @allure.step("API: Создание IP-адреса")
    def generate_ip_addresses(self, ip_start: str, ip_end: str, access_point_id: int = 100001) -> None:
        """
        Создает в LIS Ip-адрес и возвращает его в виде строки

        :param ip_start: начальный IP-адрес
        :param ip_end: конечный IP-адрес
        :param access_point_id: id точки доступа
        :return: str (если ip_count = 1) или list (если ip_count > 1)
        """
        headers = {"Content-Type": "application/json"}

        payload = {
            "accessPointId": access_point_id,
            "startIPAddress": ip_start,
            "endIPAddress": ip_end,
            "serviceProviderCode": "NEXIGN",
            "allowMixed": False,
        }

        response = self.post(
            url=f"{BASE_URL_LIS}/ps/v1/logicalResources/private/IPAddresses/generationBulkAsync",
            headers=headers,
            json=payload,
        )
        self.check_response_status(response, 204, "Не выполнен запрос на создание нового(-ых) IP-адреса в LIS.")

    @pytest.mark.lis
    @allure.step("API: Получение списка IP адресов. Внутренний метод")
    def __get_ip_addresses(
        self,
        access_point_id: int | None,
        ip_states: list,
        limit: int = 50,
        is_reserved: bool | None = None,
        sort: str | None = None,
    ) -> dict:
        params = {"limit": limit, "offset": 0}
        payload = {
            "IPAddressStateIds": ip_states,
            "accessPointFilters": {},
            "returnCount": True,
            "serviceProviderCodes": ["DEFAULT"],
        }
        if access_point_id is not None:
            payload["accessPointFilters"] = {"accessPointIds": [access_point_id]}
        if is_reserved is not None:
            payload["isReserved"] = is_reserved
        if sort is not None:
            params["sort"] = sort
        response = self.post(f"{BASE_URL_LIS}/ps/v1/logicalResources/IPAddresses/search", params=params, json=payload)
        self.check_response_status(response, 200, "Не получен список IP адресов")
        return response.json()

    @allure.step("API: Получение списка IP адресов у точки доступа")
    def get_ip_addresses(self, access_point_id: int = 100001, limit: int = 50, sort: str | None = None) -> list[dict]:
        """
        Получение IP адресов для точки доступа
        :param access_point_id: id точки доступа
        :return: список с информацией по каждому IP в этой точке доступа
        """
        return self.__get_ip_addresses(
            access_point_id=access_point_id, ip_states=[1, 2, 3, 4, 5, 6], limit=limit, sort=sort
        ).get("items")

    @allure.step("API: Получение списка id IP адресов")
    def get_ip_addresses_ids(self, ip_addresses: list, access_point_id: int = 100001, count: int = 50) -> list[int]:
        """
        Получение id IP адресов
        :param ip_addresses: список IP адресов
        :param access_point_id: id точки доступа на которой находятся IP адреса
        :return: список id IP адресов
        """
        ip_addresses_info = self.get_ip_addresses(access_point_id, limit=count, sort="-IPAddress")
        result = []
        all_ip_addresses = set(ip_addresses)
        ip_addresses_set = set()
        for ip_address_info in ip_addresses_info:
            ip_address = ip_address_info["IPAddress"]
            if ip_address in ip_addresses:
                ip_addresses_set.add(ip_address)
                result.append(ip_address_info["IPAddressId"])
        missing_ip_addresses = all_ip_addresses - ip_addresses_set
        assert_that(
            lambda: len(ip_addresses) == len(result),
            f"Ошибка при формировании списка id IP адресов\nОтсутствуют id для соответствующих IP: {missing_ip_addresses}",
        )
        return result

    @allure.step("API: Ожидание появления IP адресов у точки доступа")
    def wait_ip_addresses_added(self, ip_list: list, access_point_id: int = 100001) -> None:
        """
        Метод для ожидания появления IP адресов у точки доступа
        :param ip_list: список ip адресов
        :param access_point_id: id точки доступа
        """
        wait_that(
            lambda: ip_list[-1] in self.get_biggest_ip_addresses(access_point_id),
            timeout=60,
            sleep_seconds=3,
            exception=AssertionError,
            message="IP адреса не были добавлены",
        )

    @pytest.mark.lis
    @allure.step("API: Введение IP адресов в эксплуатацию")
    def activate_ip_addresses(self, ip_addresses_ids: list) -> None:
        """
        Метод для введения IP адресов в эксплуатацию
        :param ip_addresses_ids: список id IP адресов
        """
        response = self.post(
            f"{BASE_URL_LIS}/ps/v1/logicalResources/private/IPAddresses/inUseBulk",
            json={"IPAddressIds": ip_addresses_ids},
        )
        self.check_response_status(response, 200, "Не удалось отправить запрос на введение в эксплуатацию IP адресов")
        conflicts = response.json()["conflicts"]
        assert_that(
            lambda: len(conflicts) == 0, f"Возникла ошибка при введении в эксплуатацию IP адресов\n Ошибка: {conflicts}"
        )

    @allure.step("API: Получение наибольшего IP адреса")
    def get_biggest_ip_addresses(self, access_point_id: int | None) -> list[str]:
        items = self.get_ip_addresses(access_point_id=access_point_id, sort="-IPAddress")
        result = []
        for item in items:
            result.append(item["IPAddress"])
        return result

    @allure.step("API: Генерация не активированных IP адресов")
    def generate_closed_ip_address(self, apn: APNInfo, count: int) -> list[str]:
        available_list = self.get_biggest_ip_addresses(access_point_id=None)
        if len(available_list) == 0:
            start_ip = "44.0.0.0"
        else:
            start_ip = generate_next_ip(available_list[0])
        ip_list = generate_ip_list(start_ip=start_ip, count=count)
        self.generate_ip_addresses(ip_start=ip_list[0], ip_end=ip_list[-1], access_point_id=apn.id)
        self.wait_ip_addresses_added(ip_list=ip_list, access_point_id=apn.id)
        return ip_list

    @allure.step("API: Генерация IP адресов и активация")
    def generate_ip_addresses_and_activate(self, apn: APNInfo, count: int) -> None:
        ip_list = self.generate_closed_ip_address(apn, count)
        ip_id_list = self.get_ip_addresses_ids(ip_addresses=ip_list, access_point_id=apn.id, count=2 * count)
        self.activate_ip_addresses(ip_id_list)
        apn.free_ip_list = [IPInfo(ip_list[i], ip_id_list[i]) for i in range(len(ip_list))]

    @allure.step("API: Получение списка доступных")
    def get_available_ip_addresses(self, access_point_id: int, count: int = 50) -> list[str]:
        items = self.__get_ip_addresses(
            access_point_id=access_point_id, ip_states=[2], limit=count, is_reserved=False
        ).get("items", [])
        result = []
        for item in items:
            result.append(item.get("IPAddress"))
        return result

    @allure.step("API: Получение списка доступных IP адресов в виде объектов")
    def get_available_ip_addresses_objects(self, access_point_id: int, count: int = 10) -> list[IPInfo]:
        items = self.__get_ip_addresses(
            access_point_id=access_point_id, ip_states=[2], limit=count, is_reserved=False
        ).get("items", [])
        result = []
        for item in items:
            result.append(IPInfo(item.get("IPAddress"), item.get("IPAddressId")))
        return result

    @allure.step("API: Получение количества доступных IP адресов")
    def available_ip_addresses_count(self, access_point_id: int, count: int = 50) -> int:
        return (
            self.__get_ip_addresses(access_point_id=access_point_id, ip_states=[2], limit=count, is_reserved=False)
            .get("listInfo")
            .get("count")
        )

    @allure.step("API: Генерация IP адресов для APN")
    def generate_ip_addresses_for_apn(self, apn: APNInfo, count: int) -> None:
        if (
            not stand_context.force_generate
            and self.available_ip_addresses_count(access_point_id=apn.id, count=count + 1) > count
        ):
            return
        self.generate_ip_addresses_and_activate(apn=apn, count=count)
