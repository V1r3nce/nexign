from dataclasses import dataclass
from pathlib import Path

import allure
from playwright.sync_api import APIResponse

from api.base_requests import BaseRequests
from api.exceptions import SimCardListIsEmptyException
from common.helpers.checker import check_that
from common.helpers.data_generator import generate_english_string
from common.helpers.env_helper import BASE_URL_LIS
from common.helpers.time_helpers import delay


@dataclass
class ImsiPoolData:
    """Класс для данных по IMSI"""

    imsi_pools_data: dict

    def __post_init__(self) -> None:
        self.pools_id = self.imsi_pools_data["id"]
        self.imsi_end = self.imsi_pools_data["imsiEnd"]
        self.imsi_start = self.imsi_pools_data["imsiStart"]


@dataclass
class SimCardData:
    """Класс для данных по SIM"""

    sim_data: dict

    def __post_init__(self) -> None:
        self.imsi = self.sim_data["IMSI"]
        self.icc = self.sim_data["ICC"]
        self.expiration_date = self.sim_data["expirationDate"]
        self.switchId = self.sim_data.get("switch").get("equipmentId")
        self.sim_card_id = self.sim_data.get("SIMCardId")


class SimCardsRequests(BaseRequests):
    def __init__(self) -> None:
        super().__init__()
        self.macro_region_id = 999

    @allure.step("API: Получить список IMSI номеров LIS")
    def get_imsi_pools(self, imsi_sort: None | str = None, active: None | str = None) -> APIResponse:
        """
        Получить список IMSI номеров LIS
        """
        params = {"limit": 50, "macroRegionId": self.macro_region_id, "offset": 0}
        if imsi_sort:
            params["sort"] = imsi_sort
        if active:
            params["active"] = active
        imsi_pools = self.get(url=f"{BASE_URL_LIS}/OAPI/v1/urwin/imsiPools", params=params)
        self.check_response_status(imsi_pools, [200, 204], "Не получен список IMSI номеров")
        return imsi_pools

    @allure.step("API: Получить доступные для резервирования IMSI номера LIS")
    def get_available_for_reservation_imsis(self, count: int) -> APIResponse | None:
        """
        Получить доступные для резервирования IMSI номера LIS,
        либо None если такое количество недоступно (при статусе 409)
        """
        params = {"SIMCardProjectId": 0, "macroRegionId": self.macro_region_id, "count": count}
        imsi_pools = self.get(url=f"{BASE_URL_LIS}/OAPI/v1/urwin/imsiPools/reserve/availableIMSI", params=params)
        self.check_response_status(imsi_pools, [200, 409], "Не получен ожидаемый ответ для резервирования IMSI номера")
        if imsi_pools.status == 200:
            return imsi_pools
        else:
            return None

    @staticmethod
    def get_imsi_pool_data(imsi_pool_response: APIResponse) -> list[ImsiPoolData]:
        """Получить данные по IMSI в виде объектов"""
        imsi_pool = imsi_pool_response.json()["items"]
        return [ImsiPoolData(item) for item in imsi_pool]

    @allure.step("API: Добавить список IMSI номеров LIS")
    def add_imsi_pools(self, start_num: str, end_num: str) -> APIResponse:
        """
        Добавить список IMSI номеров LIS
        """
        payload = {
            "macroRegionId": self.macro_region_id,
            "simProjectId": 0,
            "imsiStart": start_num,
            "imsiEnd": end_num,
            "active": True,
        }
        add_imsis = self.post(url=f"{BASE_URL_LIS}/OAPI/v1/urwin/imsiPools", data=payload)
        self.check_response_status(add_imsis, [200, 204], "Не созданы номера IMSI")
        return add_imsis

    @allure.step("API: Получить список SIM-карт LIS")
    def get_sim_card_list(
        self,
        sim_sort: None | str = None,
        status_id: None | list = None,
        state_id: None | list = None,
        is_reserved: bool | str | None = None,
    ) -> APIResponse:
        """
        Получить список SIM-карт LIS
        """
        params = {"limit": 50, "macroRegionId": self.macro_region_id, "offset": 0}
        payload = {"returnCount": True, "macroRegionIds": [self.macro_region_id], "SIMCardProjectId": None}
        if sim_sort:
            params["sort"] = sim_sort
        if status_id:
            payload["statusIds"] = status_id
        if state_id:
            payload["stateIds"] = state_id
        if is_reserved is not None:
            payload["isReserved"] = is_reserved
        sim_cards = self.post(
            url=f"{BASE_URL_LIS}/OAPI/v1/lis/logicalResources/SIMCards/search", params=params, data=payload
        )
        self.check_response_status(sim_cards, 200, "Не получен список SIM-карт")
        return sim_cards

    @staticmethod
    def get_sim_cards_data(sim_card_response: APIResponse) -> list[SimCardData]:
        """Получить данные по SIM картам в виде объектов"""
        sims_list = sim_card_response.json()["items"]
        check_that(lambda: len(sims_list) > 0, SimCardListIsEmptyException, "Список SIM карт пуст")
        return [SimCardData(item) for item in sims_list]

    @allure.step("API: Получить список шаблонов поиска SIM карт LIS")
    def get_sim_card_search_templates(self) -> APIResponse:
        payload = {"macroRegionIds": self.macro_region_id}
        params = {"limit": 0, "offset": 0}
        templates = self.post(
            url=f"{BASE_URL_LIS}/OAPI/v1/lis/logicalResources/SIMCards/filterTemplates/search",
            data=payload,
            params=params,
        )
        self.check_response_status(templates, 200, "Не получен список шаблонов SIM карт")
        return templates

    @allure.step("API: Удалить шаблон поиска SIM карт LIS")
    def delete_sim_card_search_template(self, template_id: str) -> APIResponse:
        delete_template = self.delete(
            url=f"{BASE_URL_LIS}/OAPI/v1/lis/logicalResources/SIMCards/filterTemplates/{template_id}"
        )
        self.check_response_status(delete_template, 204, "Не удален шаблон поиска телефонных номеров")
        return delete_template

    @allure.step("API: Удалить все шаблоны поиска SIM карт LIS")
    def remove_all_search_templates(self) -> None:
        templates = self.get_sim_card_search_templates()
        template_items = templates.json()["items"]
        if len(template_items) > 0:
            for item in template_items:
                self.delete_sim_card_search_template(item["SIMCardFilterTemplateId"])
                delay(0.5, reason="Для корректной отработки запросов")

    @allure.step("API: Получить список загруженных SIM")
    def get_downloaded_sims(self, sim_sort: None | str = None) -> APIResponse:
        """
        Получить список загруженных SIM LIS
        """
        params = {"isError": False, "limit": 50, "macroRegionIds": self.macro_region_id, "offset": 0}
        if sim_sort:
            params["sort"] = sim_sort
        payload = {"SIMCardProjectId": None}
        uploaded_sims = self.post(
            url=f"{BASE_URL_LIS}/OAPI/v1/lis/logicalResources/SIMCards/temporaryData/search", params=params, data=payload
        )
        self.check_response_status(uploaded_sims, [200, 204], "Не получен список загруженных SIM, вернулся код")
        return uploaded_sims

    @allure.step("API: Изменить проект для загруженной первой SIM")
    def change_first_uploaded_sim_project(self) -> APIResponse:
        """
        Изменить проект для загруженной первой SIM, для предусловия
        """
        uploaded_sims = self.get_downloaded_sims(sim_sort="-IMSI")
        payload = {
            "loadSimIds": [uploaded_sims.json()["items"][0]["loadSimId"]],
            "macroRegionId": self.macro_region_id,
            "SIMCardProjectId": 0,
        }
        change_project = self.post(
            url=f"{BASE_URL_LIS}/OAPI/v1/lis/logicalResources/SIMCards/temporaryData/SIMCardProjectBulk", data=payload
        )
        self.check_response_status(change_project, 200, "Не изменен проект для загруженной SIM")
        return change_project

    @allure.step("API: Получить список отгрузки SIM")
    def get_sims_shipments(self) -> APIResponse:
        """
        Получить список Отгрузка SIM-карт LIS
        """
        params = {"limit": 50, "macroRegionIds": self.macro_region_id, "offset": 0}
        payload = {"taskTypeIds": [10, 12, 13, 15, 17]}
        shipped_sims = self.post(url=f"{BASE_URL_LIS}/OAPI/v1/urwin/tasks/search", params=params, data=payload)
        self.check_response_status(shipped_sims, 200, "Не получен список отгруженных SIM")
        return shipped_sims

    @allure.step("API: Получить список создания SIM")
    def get_sims_creation(self) -> APIResponse:
        """
        Получить список Изготовление SIM-карт LIS
        """
        params = {"limit": 50, "macroRegionIds": self.macro_region_id, "offset": 0}
        payload = {"taskTypeIds": [1, 7]}
        created_sims = self.post(url=f"{BASE_URL_LIS}/OAPI/v1/urwin/tasks/search", params=params, data=payload)
        self.check_response_status(created_sims, 200, "Не получен список созданных SIM")
        return created_sims

    @allure.step("API: Получить список заданий Управление предсвязками")
    def get_pre_links_creation(self) -> APIResponse:
        params = {"limit": 50, "macroRegionIds": self.macro_region_id, "offset": 0}
        payload = {"taskTypeIds": [2, 8]}
        created_pre_links = self.post(url=f"{BASE_URL_LIS}/OAPI/v1/urwin/tasks/search", params=params, data=payload)
        self.check_response_status(created_pre_links, 200, "Не получен список заданий Управление предсвязками")
        return created_pre_links

    @allure.step("API: Получить отгрузку SIM")
    def get_sims_shipment_item(self, task_id: str) -> APIResponse:
        """
        Получить отгрузку SIM-карт LIS
        """
        params = {"limit": 50, "showWithNullMsisdnOnly": False, "offset": 0}
        shipped_sims_item = self.get(url=f"{BASE_URL_LIS}/OAPI/v1/urwin/tasks/{task_id}/items/ranges", params=params)
        self.check_response_status(shipped_sims_item, 200, "Не получена отгрузка SIM")
        return shipped_sims_item

    @allure.step("API: Загрузить SIM карты по API")
    def upload_sims_by_api(self, file_path: Path) -> APIResponse:
        """
        Загрузить SIM карты по API LIS
        """
        with open(file_path, "rb") as file:
            file_content = file.read()
        file_name = f"test_load_sim_f_{generate_english_string(5)}.txt"
        form_data = {
            "file": {"name": file_name, "mimeType": "application/octet-stream", "buffer": file_content},
            "fileName": file_name,
            "loadSIMCardTemplateId": "100001",
            "SIMCardProjectId": "0",
            "equipmentId": "100001",
            "macroRegionId": f"{self.macro_region_id}",
            "expirationDate": "2027-03-08T20:00:00.000Z",
            "SIMCardTypeId": "100003",
        }
        upload_sims = self.post(
            url=f"{BASE_URL_LIS}/OAPI/v1/lis/logicalResources/SIMCards/temporaryData/loadAsync", multipart=form_data
        )
        self.check_response_status(upload_sims, 204, "Не загружены SIM")
        return upload_sims

    @allure.step("API: Загрузить 2е SIM карты по API и перевести в эксплуатацию")
    def upload_sims_set_to_use_by_api(self, file_path: Path) -> APIResponse:
        """
        Загрузить две SIM карты по API и перевести в эксплуатацию LIS
        """
        self.upload_sims_by_api(file_path)
        delay(1, reason="Для корректности операций по API")
        downloaded_sims = self.get_downloaded_sims(sim_sort="-IMSI")
        payload = {
            "loadSimIds": [
                downloaded_sims.json()["items"][0]["loadSimId"],
                downloaded_sims.json()["items"][1]["loadSimId"],
            ],
            "macroRegionId": self.macro_region_id,
        }
        set_sims_to_use = self.post(
            url=f"{BASE_URL_LIS}/OAPI/v1/lis/logicalResources/SIMCards/temporaryData/prepareBulk", data=payload
        )
        self.check_response_status(set_sims_to_use, 204, "Не введены в эксплуатацию SIM")
        return set_sims_to_use
