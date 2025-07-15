import random

import allure
from playwright.sync_api import APIRequestContext

from api.requests.base_requests import BaseRequests
from common.helpers.data_generator import generate_random_ip
from common.helpers.env_helper import BASE_URL_LIS


class IpAddressRequests(BaseRequests):
    """
    Класс для управления ip адресами с помощью api запросов
    """

    def __init__(self, api_request_auth_context: APIRequestContext, macro_region_id: int = 999):
        super().__init__(api_request_auth_context)

    @allure.step("API: Создание IP-адреса")
    def generate_ip_addresses(self, ip_count: int) -> str | list:
        """
        Создает в LIS Ip-адрес и возвращает его в виде строки

        :param ip_count: Кол-во создаваемых IP-адресов
        :return: str (если ip_count = 1) или list (если ip_count > 1)
        """
        headers = {"Content-Type": "application/json"}

        ip_base = generate_random_ip(3)
        start_knot = random.randint(0, 250)
        ip_list = [f"{ip_base}.{start_knot + i}" for i in range(ip_count)]

        payload = {
            "accessPointId": 100001,
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
