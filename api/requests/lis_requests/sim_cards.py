from pathlib import Path
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

    @allure.step("Получить доступные для резервирования IMSI номера LIS")
    def get_available_for_reservation_imsis(self, count: int) -> APIResponse | None:
        """
        Получить доступные для резервирования IMSI номера LIS,
        либо None если такое количество недоступно (при статусе 409)
        """
        params = {"SIMCardProjectId": 0, "macroRegionId": 1, "count": count}
        imsi_pools = (self.api_request_auth_context.
                      get(url=f"{BASE_URL_LIS}/OAPI/v1/urwin/imsiPools/reserve/availableIMSI", params=params))
        assert imsi_pools.status in [200, 409], (f"Не получен ожидаемый ответ для резервирования IMSI номера,"
                                                 f" вернулся код {imsi_pools.status} и ответ {imsi_pools.text()}")
        if imsi_pools.status == 200:
            return imsi_pools
        elif imsi_pools.status == 409:
            return None

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
        if is_reserved is not None:
            payload["isReserved"] = is_reserved
        sim_cards = (self.api_request_auth_context.
                     post(url=f"{BASE_URL_LIS}/OAPI/v1/lis/logicalResources/SIMCards/search",
                          params=params, data=payload))
        assert sim_cards.status == 200, (f"Не получен список SIM-карт, вернулся код {sim_cards.status} "
                                         f"и ответ {sim_cards.text()}")
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
        templates = (self.api_request_auth_context.
                     post(url=f"{BASE_URL_LIS}/OAPI/v1/lis/logicalResources/SIMCards/filterTemplates/search",
                          data=payload, params=params))
        assert templates.status == 200, (f"Не получен список шаблонов SIM карт, "
                                         f"вернулся код {templates.status} с ошибкой '{templates.text}'")
        return templates

    @allure.step("Удалить шаблон поиска SIM карт LIS")
    def delete_sim_card_search_template(self, template_id: str):
        delete_template = (self.api_request_auth_context.
                           delete(url=f"{BASE_URL_LIS}/OAPI/v1/lis/logicalResources/SIMCards/filterTemplates/{template_id}"))
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

    @allure.step("Получить список загруженных SIM")
    def get_downloaded_sims(self, sim_sort: [None, str] = None) -> APIResponse:
        """
        Получить список загруженных SIM LIS
        """
        params = {"isError": False, "limit": 50, "macroRegionIds": 1, "offset": 0}
        if sim_sort:
            params["sort"] = sim_sort
        payload = {"SIMCardProjectId": None}
        uploaded_sims = (self.api_request_auth_context.
                         post(url=f"{BASE_URL_LIS}/OAPI/v1/lis/logicalResources/SIMCards/temporaryData/search",
                              params=params, data=payload))
        assert uploaded_sims.status in [200, 204], (f"Не получен список загруженных SIM, вернулся код "
                                                    f"{uploaded_sims.status} и ответ {uploaded_sims.text()}")
        return uploaded_sims

    @allure.step("Изменить проект для загруженной первой SIM")
    def change_first_uploaded_sim_project(self) -> APIResponse:
        """
        Изменить проект для загруженной первой SIM, для предусловия
        """
        uploaded_sims = self.get_downloaded_sims(sim_sort="-IMSI")
        payload = {"loadSimIds": [uploaded_sims.json()["items"][0]["loadSimId"]],
                   "macroRegionId": 1,
                   "SIMCardProjectId": 0}
        change_project = (self.api_request_auth_context.post(
            url=f"{BASE_URL_LIS}/OAPI/v1/lis/logicalResources/SIMCards/temporaryData/SIMCardProjectBulk", data=payload))
        assert change_project.status == 200, (f"Не изменен проект для загруженной SIM, вернулся код "
                                              f"{change_project.status} и ответ {change_project.text()}")
        return change_project

    @allure.step("Получить список отгрузки SIM")
    def get_sims_shipments(self) -> APIResponse:
        """
        Получить список Отгрузка SIM-карт LIS
        """
        params = {"limit": 50, "macroRegionIds": 1, "offset": 0}
        payload = {"taskTypeIds": [10, 12, 13, 15, 17]}
        shipped_sims = (self.api_request_auth_context.post(url=f"{BASE_URL_LIS}/OAPI/v1/urwin/tasks/search",
                        params=params, data=payload))
        assert shipped_sims.status == 200, (f"Не получен список отгруженных SIM, вернулся код "
                                            f"{shipped_sims.status} и ответ {shipped_sims.text()}")
        return shipped_sims

    @allure.step("Получить список создания SIM")
    def get_sims_creation(self) -> APIResponse:
        """
        Получить список Изготовление SIM-карт LIS
        """
        params = {"limit": 50, "macroRegionIds": 1, "offset": 0}
        payload = {"taskTypeIds": [1, 7]}
        created_sims = (self.api_request_auth_context.post(url=f"{BASE_URL_LIS}/OAPI/v1/urwin/tasks/search",
                        params=params, data=payload))
        assert created_sims.status == 200, (f"Не получен список созданных SIM, вернулся код "
                                            f"{created_sims.status} и ответ {created_sims.text()}")
        return created_sims

    @allure.step("Получить список заданий Управление предсвязками")
    def get_pre_links_creation(self) -> APIResponse:
        params = {"limit": 50, "macroRegionIds": 1, "offset": 0}
        payload = {"taskTypeIds": [2, 8]}
        created_pre_links = (self.api_request_auth_context.post(url=f"{BASE_URL_LIS}/OAPI/v1/urwin/tasks/search",
                             params=params, data=payload))
        assert created_pre_links.status == 200, (f"Не получен список заданий Управление предсвязками, вернулся код "
                                                 f"{created_pre_links.status} и ответ {created_pre_links.text()}")
        return created_pre_links

    @allure.step("Получить отгрузку SIM")
    def get_sims_shipment_item(self, task_id: str) -> APIResponse:
        """
        Получить отгрузку SIM-карт LIS
        """
        params = {"limit": 50, "showWithNullMsisdnOnly": False, "offset": 0}
        shipped_sims_item = (self.api_request_auth_context.
                             get(url=f"{BASE_URL_LIS}/OAPI/v1/urwin/tasks/{task_id}/items/ranges", params=params))
        assert shipped_sims_item.status == 200, (f"Не получена отгрузка SIM, вернулся код "
                                                 f"{shipped_sims_item.status} и ответ {shipped_sims_item.text()}")
        return shipped_sims_item

    @allure.step("Загрузить SIM карты по API")
    def upload_sims_by_api(self, file_path) -> APIResponse:
        """
        Загрузить SIM карты по API LIS
        """
        with open(file_path, 'rb') as file:
            file_content = file.read()
        form_data = {
            'file': {
                'name': 'load_sim_f.txt',
                'mimeType': 'application/octet-stream',
                'buffer': file_content
            },
            'fileName': 'load_sim_f.txt',
            'loadSIMCardTemplateId': '1',
            'SIMCardProjectId': '0',
            'equipmentId': '2',
            'macroRegionId': '1',
            'expirationDate': '2027-03-08T20:00:00.000Z',
            'SIMCardTypeId': '100000'
        }
        upload_sims = (self.api_request_auth_context.post(url=f"{BASE_URL_LIS}/OAPI/v1/lis/logicalResources/SIMCards/"
                                                              f"temporaryData/loadAsync", multipart=form_data))
        assert upload_sims.status == 204, (f"Не загружены SIM, вернулся код {upload_sims.status} "
                                           f"и ответ {upload_sims.text()}")
        return upload_sims

    @allure.step("Загрузить 2е SIM карты по API и перевести в эксплуатацию")
    def upload_sims_set_to_use_by_api(self, file_path: Path) -> APIResponse:
        """
        Загрузить две SIM карты по API и перевести в эксплуатацию LIS
        """
        self.upload_sims_by_api(file_path)
        delay(1, reason="Для корректности операций по API")
        downloaded_sims = self.get_downloaded_sims(sim_sort="-IMSI")
        payload = {"loadSimIds": [downloaded_sims.json()["items"][0]["loadSimId"],
                                  downloaded_sims.json()["items"][1]["loadSimId"]],
                   "macroRegionId": 1}
        set_sims_to_use = self.api_request_auth_context.post(url=f"{BASE_URL_LIS}/OAPI/v1/lis/logicalResources/SIMCards"
                                                                 f"/temporaryData/prepareBulk", data=payload)
        assert set_sims_to_use.status == 204, (f"Не введены в эксплуатацию SIM, вернулся код "
                                               f"{set_sims_to_use.status} и ответ {set_sims_to_use.text()}")
        return set_sims_to_use
