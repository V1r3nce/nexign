import random

import allure
import pytest

from api.base_requests import BaseRequests
from common.helpers.checker import assert_that, wait_that
from common.helpers.data_generator import generate_random_ip
from common.helpers.env_helper import BASE_URL_LIS


class IpAddressRequests(BaseRequests):
    """
    Класс для управления ip адресами с помощью api запросов
    """

    @pytest.mark.lis
    @allure.step("API: Создание IP-адреса")
    def generate_ip_addresses(self, ip_count: int, access_point_id: int = 100001) -> str | list:
        """
        Создает в LIS Ip-адрес и возвращает его в виде строки

        :param ip_count: Кол-во создаваемых IP-адресов
        :param access_point_id: id точки доступа
        :return: str (если ip_count = 1) или list (если ip_count > 1)
        """
        headers = {"Content-Type": "application/json"}

        ip_base = generate_random_ip(3)
        start_knot = random.randint(0, 250)
        ip_list = [f"{ip_base}.{start_knot + i}" for i in range(ip_count)]

        payload = {
            "accessPointId": access_point_id,
            "startIPAddress": ip_list[0],
            "endIPAddress": ip_list[-1],
            "serviceProviderCode": "NEXIGN",
            "allowMixed": False,
        }

        response = self.post(
            url=f"{BASE_URL_LIS}/ps/v1/logicalResources/private/IPAddresses/generationBulkAsync",
            headers=headers,
            data=payload,
        )
        self.check_response_status(response, 204, "Не выполнен запрос на создание нового(-ых) IP-адреса в LIS.")
        return ip_list[0] if ip_count == 1 else ip_list

    @pytest.mark.lis
    @allure.step("API: Получение списка IP адресов у точки доступа")
    def get_ip_addresses(self, access_point_id: int = 100001) -> list[dict]:
        """
        Получение IP адресов для точки доступа
        :param access_point_id: id точки доступа
        :return: список с информацией по каждому IP в этой точке доступа
        """
        params = {"limit": 50, "offset": 0}
        payload = {
            "IPAddressStateIds": [1, 2, 3, 4, 5, 6],
            "accessPointFilters": {"accessPointIds": [access_point_id]},
            "returnCount": True,
            "serviceProviderCodes": ["DEFAULT"],
        }
        response = self.post(f"{BASE_URL_LIS}/ps/v1/logicalResources/IPAddresses/search", params=params, data=payload)
        self.check_response_status(response, 200, "Не получен список IP адресов")
        return response.json()["items"]

    @allure.step("API: Получение списка id IP адресов")
    def get_ip_addresses_ids(self, ip_addresses: list, access_point_id: int = 100001) -> list[int]:
        """
        Получение id IP адресов
        :param ip_addresses: список IP адресов
        :param access_point_id: id точки доступа на которой находятся IP адреса
        :return: список id IP адресов
        """
        ip_addresses_info = self.get_ip_addresses(access_point_id)
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
    def wait_ip_addresses_added(self, access_point_id: int = 100001) -> None:
        """
        Метод для ожидания появления IP адресов у точки доступа
        :param access_point_id: id точки доступа
        """
        wait_that(
            lambda: len(self.get_ip_addresses(access_point_id)) > 0,
            timeout=18,
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
            data={"IPAddressIds": ip_addresses_ids},
        )
        self.check_response_status(response, 200, "Не удалось отправить запрос на введение в эксплуатацию IP адресов")
        conflicts = response.json()["conflicts"]
        assert_that(
            lambda: len(conflicts) == 0, f"Возникла ошибка при введении в эксплуатацию IP адресов\n Ошибка: {conflicts}"
        )
