import allure
from playwright.sync_api import APIRequestContext, APIResponse
from dataclasses import dataclass

from common.helpers.env_helper import BASE_URL_LIS
from common.helpers.time_helpers import delay


@dataclass
class ImsiPoolData:
    """Класс для данных по IMSI"""
    imsi_pools_data: dict

    def __post_init__(self):
        self.pools_id = self.imsi_pools_data["id"]
        self.imsi_end = self.imsi_pools_data["imsiEnd"]
        self.imsi_start = self.imsi_pools_data['imsiStart']


@dataclass
class SimCardData:
    """Класс для данных по SIM"""
    sim_data: dict

    def __post_init__(self):
        self.imsi = self.sim_data["IMSI"]
        self.icc = self.sim_data["ICC"]
        self.sim_card_id = self.sim_data['SIMCardId']
        self.expiration_date = self.sim_data['expirationDate']


class SimCardsRequests:
    def __init__(self, api_request_auth_context: APIRequestContext):
        self.api_request_auth_context = api_request_auth_context

    @allure.step("Получить список IMSI номеров LIS")
    def get_imsi_pools(self, imsi_sort: [None, str] = None, active: [None, str] = None) -> APIResponse:
        """
        Получить список IMSI номеров LIS
        """
        params = {"limit": 50, "macroRegionId": 1, "offset": 0}
        if imsi_sort:
            params["sort"] = imsi_sort
        if active:
            params["active"] = active
        imsi_pools = self.api_request_auth_context.get(url=f"{BASE_URL_LIS}/OAPI/v1/urwin/imsiPools", params=params)
        assert imsi_pools.status in [200, 204], f"Не получен список IMSI номеров, вернулся код {imsi_pools.status}"
        return imsi_pools

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
        add_imsis = self.api_request_auth_context.post(url=f"{BASE_URL_LIS}/OAPI/v1/urwin/imsiPools", data=payload)
        assert add_imsis.status in [200, 204], f"Не созданы номера IMSI, вернулся код {add_imsis.status}"
        return add_imsis

    @allure.step("Получить список SIM-карт LIS")
    def get_sim_card_list(self, sim_sort: [None, str] = None, status_id: [None, list] = None,
                          state_id: [None, list] = None, is_reserved: [bool, str, None] = None) -> APIResponse:
        """
        Получить список SIM-карт LIS
        """
        params = {"limit": 50, "macroRegionId": 1, "offset": 0}
        payload = {"returnCount": True, "macroRegionIds": [1], "SIMCardProjectId": None}
        if sim_sort:
            params["sort"] = sim_sort
        if status_id:
            payload["statusIds"] = status_id
        if state_id:
            payload["stateIds"] = state_id
        if is_reserved:
            payload["isReserved"] = is_reserved
        sim_cards = self.api_request_auth_context.post(url=f"{BASE_URL_LIS}/OAPI/v1/lis/logicalResources/SIMCards/search",
                                                       params=params, data=payload)
        assert sim_cards.status == 200, f"Не получен список SIM-карт, вернулся код {sim_cards.status}"
        return sim_cards

    @staticmethod
    def get_sim_cards_data(sim_card_response: APIResponse):
        """Получить данные по SIM картам в виде объектов"""
        sims_list = sim_card_response.json()['items']
        return [SimCardData(item) for item in sims_list]

    @allure.step("Получить список шаблонов поиска SIM карт LIS")
    def get_sim_card_search_templates(self):
        payload = {"macroRegionIds": 1}
        params = {"limit": 0, "offset": 0}
        templates = self.api_request_auth_context.post(url=f"{BASE_URL_LIS}/OAPI/v1/lis/logicalResources/SIMCards/filterTemplates/search",
                                                       data=payload, params=params)
        assert templates.status == 200, f"Не получен список шаблонов SIM карт, вернулся код {templates.status} с ошибкой '{templates.text}'"
        return templates

    @allure.step("Удалить шаблон поиска SIM карт LIS")
    def delete_sim_card_search_template(self, template_id: str):
        delete_template = self.api_request_auth_context.delete(url=f"{BASE_URL_LIS}/OAPI/v1/lis/logicalResources/SIMCards/filterTemplates/{template_id}")
        assert delete_template.status == 204, (f"Не удален шаблон поиска телефонных номеров, вернулся код "
                                               f"{delete_template.status}  с ошибкой '{delete_template.text}'")
        return delete_template

    @allure.step("Удалить все шаблоны поиска SIM карт LIS")
    def remove_all_search_templates(self):
        templates = self.get_sim_card_search_templates()
        template_items = templates.json()["items"]
        if len(template_items) > 0:
            for item in template_items:
                self.delete_sim_card_search_template(item["SIMCardFilterTemplateId"])
                delay(.5, reason="Для корректной отработки запросов")
