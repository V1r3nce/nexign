import allure
from playwright.sync_api import APIRequestContext, APIResponse
from dataclasses import dataclass

from common.helpers.env_helper import BASE_URL_LIS


@dataclass
class ImsiPoolData:
    """Класс для данных по SIM"""
    sim_pools_data: dict

    def __post_init__(self):
        self.pools_id = self.sim_pools_data["id"]
        self.imsi_end = self.sim_pools_data["imsiEnd"]
        self.imsi_start = self.sim_pools_data['imsiStart']


class SimCardsRequests:
    def __init__(self, api_request_auth_context: APIRequestContext):
        self.api_request_auth_context = api_request_auth_context

    @allure.step("Получить список IMSI номеров LIS")
    def get_imsi_pools(self, sim_sort: [None, str] = None, active: [None, str] = None) -> APIResponse:
        """
        Получить список IMSI номеров LIS
        """
        params = {"limit": 50, "macroRegionId": 1, "offset": 0}
        if sim_sort:
            params["sort"] = sim_sort
        if active:
            params["active"] = active
        sim_cards = self.api_request_auth_context.get(url=f"{BASE_URL_LIS}/OAPI/v1/urwin/imsiPools", params=params)
        assert sim_cards.status in [200, 204], f"Не получен список IMSI номеров, вернулся код {sim_cards.status}"
        return sim_cards

    @staticmethod
    def get_imsi_pool_data(imsi_pool_response: APIResponse):
        """Получить данные по IMSI в виде объектов"""
        imsi_pool = imsi_pool_response.json()['items']
        return [ImsiPoolData(item) for item in imsi_pool]

    @allure.step("Добавить список IMSI номеров LIS")
    def add_imsi_pools(self, start_num: str, end_num: str) -> APIResponse:
        """
        Добавить список IMSI номеров LIS
        """
        payload = {"macroRegionId": 1, "simProjectId": 0, "imsiStart": start_num, "imsiEnd": end_num, "active": True}
        add_sim_cards = self.api_request_auth_context.post(url=f"{BASE_URL_LIS}/OAPI/v1/urwin/imsiPools", data=payload)
        assert add_sim_cards.status in [200, 204], f"Не созданы номера IMSI, вернулся код {add_sim_cards.status}"
        return add_sim_cards
