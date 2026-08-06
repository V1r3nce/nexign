from dataclasses import dataclass
from pathlib import Path

import allure
import pytest

from api.base_requests import BaseRequests
from api.exceptions import (
    GetSIMShipmentsException,
    UpdateStatusException,
)
from common.helpers.checker import assert_that, wait_that
from common.helpers.data_generator import generate_english_string, generate_random_number, get_shifted_datetime_string
from common.helpers.download_helper import create_txt_file_to_upload_sim, wrap_file_and_delete_after
from common.helpers.env_helper import BASE_URL_LIS
from common.helpers.time_helpers import delay
from models.lis_resources import Equipment, SimCardData, SwitchRef
from models.playwright_bridge import GeneralResponse
from models.stand_context import stand_context


@dataclass
class ImsiPoolData:
    """Класс для данных по IMSI"""

    imsi_pools_data: dict

    def __post_init__(self) -> None:
        self.pools_id = self.imsi_pools_data["id"]
        self.imsi_end = self.imsi_pools_data["imsiEnd"]
        self.imsi_start = self.imsi_pools_data["imsiStart"]


class SimCardsRequests(BaseRequests):
    @pytest.mark.lis
    def __init__(self) -> None:
        super().__init__()
        self.macro_region_id = 999

    @allure.step("API: Получить список IMSI номеров LIS")
    def get_imsi_pools(self, imsi_sort: None | str = None, active: None | str = None) -> GeneralResponse:
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
    def get_available_for_reservation_imsis(self, count: int) -> GeneralResponse | None:
        """
        Получить доступные для резервирования IMSI номера LIS,
        либо None если такое количество недоступно (при статусе 409)
        """
        params = {"SIMCardProjectId": 0, "macroRegionId": self.macro_region_id, "count": count}
        imsi_pools = self.get(url=f"{BASE_URL_LIS}/OAPI/v1/urwin/imsiPools/reserve/availableIMSI", params=params)
        self.check_response_status(imsi_pools, [200, 409], "Не получен ожидаемый ответ для резервирования IMSI номера")
        if imsi_pools.status_code == 200:
            return imsi_pools
        else:
            return None

    @staticmethod
    def get_imsi_pool_data(imsi_pool_response: GeneralResponse) -> list[ImsiPoolData]:
        """Получить данные по IMSI в виде объектов"""
        imsi_pool = imsi_pool_response.json()["items"]
        return [ImsiPoolData(item) for item in imsi_pool]

    @allure.step("API: Добавить список IMSI номеров LIS")
    def add_imsi_pools(self, start_num: str, end_num: str) -> GeneralResponse:
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
        add_imsis = self.post(url=f"{BASE_URL_LIS}/OAPI/v1/urwin/imsiPools", json=payload)
        self.check_response_status(add_imsis, [200, 204], "Не созданы номера IMSI")
        return add_imsis

    @allure.step("API: Получить список SIM-карт LIS")
    def get_sim_card_list(
        self,
        sim_sort: None | str = None,
        status_id: None | list = None,
        state_id: None | list = None,
        equipment_id: int | None = None,
        macro_region_id: int = stand_context.stand_equipment.macro_region_id,
        is_reserved: bool | str | None = None,
        limit: int = 50,
    ) -> GeneralResponse:
        """
        Получить список SIM-карт LIS
        """
        params = {"limit": limit, "offset": 0}
        payload = {"returnCount": True, "SIMCardProjectId": None, "macroRegionIds": [macro_region_id]}
        if sim_sort:
            params["sort"] = sim_sort
        if status_id:
            payload["statusIds"] = status_id
        if state_id:
            payload["stateIds"] = state_id
        if is_reserved is not None:
            payload["isReserved"] = is_reserved
        if equipment_id:
            payload["equipmentId"] = equipment_id
        sim_cards = self.post(
            url=f"{BASE_URL_LIS}/OAPI/v1/lis/logicalResources/SIMCards/search", params=params, json=payload
        )
        self.check_response_status(sim_cards, 200, "Не получен список SIM-карт")
        return sim_cards

    @staticmethod
    def get_sim_cards_data(sim_card_response: GeneralResponse) -> list[SimCardData]:
        """Получить данные по SIM картам в виде объектов"""
        sims_list = sim_card_response.json()["items"]
        return [SimCardData.model_validate(item) for item in sims_list]

    @allure.step("API: Получить список шаблонов поиска SIM карт LIS")
    def get_sim_card_search_templates(self) -> GeneralResponse:
        payload = {"macroRegionIds": self.macro_region_id}
        params = {"limit": 0, "offset": 0}
        templates = self.post(
            url=f"{BASE_URL_LIS}/OAPI/v1/lis/logicalResources/SIMCards/filterTemplates/search",
            json=payload,
            params=params,
        )
        self.check_response_status(templates, 200, "Не получен список шаблонов SIM карт")
        return templates

    @allure.step("API: Удалить шаблон поиска SIM карт LIS")
    def delete_sim_card_search_template(self, template_id: str) -> GeneralResponse:
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
    def get_downloaded_sims(
        self, file_name: str = None, sim_sort: None | str = None, limit: int = 50
    ) -> GeneralResponse:
        """
        Получить список SIM загруженных в LIS в файле с именем file_name
        :param file_name: имя файла, в котором были загружены sim-карты
        :param sim_sort: сортировка списка sim-карт
        :param limit: количество sim-карт
        :return: uploaded_sims - список sim-карт, подходящих под условия
        """
        params = {"isError": False, "limit": limit, "macroRegionIds": self.macro_region_id, "offset": 0}
        if sim_sort:
            params["sort"] = sim_sort
        payload = {"SIMCardProjectId": None}
        if file_name:
            payload["fileName"] = file_name

        uploaded_sims = self.post(
            url=f"{BASE_URL_LIS}/OAPI/v1/lis/logicalResources/SIMCards/temporaryData/search", params=params, json=payload
        )
        self.check_response_status(uploaded_sims, [200, 204], "Не получен список загруженных SIM")
        return uploaded_sims

    @allure.step("API: Изменить проект для загруженной первой SIM")
    def change_first_uploaded_sim_project(self) -> GeneralResponse:
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
            url=f"{BASE_URL_LIS}/OAPI/v1/lis/logicalResources/SIMCards/temporaryData/SIMCardProjectBulk", json=payload
        )
        self.check_response_status(change_project, 200, "Не изменен проект для загруженной SIM")
        return change_project

    @allure.step("API: Получить список отгрузки SIM")
    def get_sims_shipments(self) -> GeneralResponse:
        """
        Получить список Отгрузка SIM-карт LIS
        """
        params = {"limit": 50, "macroRegionIds": self.macro_region_id, "offset": 0}
        payload = {"taskTypeIds": [10, 12, 13, 15, 17]}
        shipped_sims = self.post(url=f"{BASE_URL_LIS}/OAPI/v1/urwin/tasks/search", params=params, json=payload)
        self.check_response_status(shipped_sims, 200, "Не получен список отгруженных SIM")
        return shipped_sims

    @allure.step("API: Получить список создания SIM")
    def get_sims_creation(self) -> GeneralResponse:
        """
        Получить список Изготовление SIM-карт LIS
        """
        params = {"limit": 50, "macroRegionIds": self.macro_region_id, "offset": 0}
        payload = {"taskTypeIds": [1, 7]}
        created_sims = self.post(url=f"{BASE_URL_LIS}/OAPI/v1/urwin/tasks/search", params=params, json=payload)
        self.check_response_status(created_sims, 200, "Не получен список созданных SIM")
        return created_sims

    @allure.step("API: Получить список заданий Управление предсвязками")
    def get_pre_links_creation(self) -> GeneralResponse:
        params = {"limit": 50, "macroRegionIds": self.macro_region_id, "offset": 0}
        payload = {"taskTypeIds": [2, 8]}
        created_pre_links = self.post(url=f"{BASE_URL_LIS}/OAPI/v1/urwin/tasks/search", params=params, json=payload)
        self.check_response_status(created_pre_links, [200, 204], "Не получен список заданий Управление предсвязками")
        return created_pre_links

    @allure.step("API: Получить отгрузку SIM")
    def get_sims_shipment_item(self, task_id: str) -> GeneralResponse:
        """
        Получить отгрузку SIM-карт LIS
        """
        params = {"limit": 50, "showWithNullMsisdnOnly": False, "offset": 0}
        shipped_sims_item = self.get(url=f"{BASE_URL_LIS}/OAPI/v1/urwin/tasks/{task_id}/items/ranges", params=params)
        self.check_response_status(shipped_sims_item, 200, "Не получена отгрузка SIM")
        return shipped_sims_item

    @allure.step("API: Отгрузка SIM")
    def sim_shipment(self, start_imsi: int, end_imsi: int, is_test: bool = True) -> str:
        correlation_id = f"test_shipment_{generate_random_number(12)}"
        payload = {
            "IMSIRange": {"startIMSI": start_imsi, "endIMSI": end_imsi},
            "allowMoveFromDiffAgents": True,
            "correlationId": correlation_id,
            "isTest": is_test,
            "partnerId": stand_context.stand_equipment.partner_point_id,
        }
        response = self.post(
            f"{BASE_URL_LIS}/OAPI/v1/lis/logicalResources/SIMCards/logisticOperations/SIM_MOVE", json=payload
        )
        self.check_response_status(response, 200, "Ошибка отгрузки SIM")
        return correlation_id

    @allure.step("API: Ожидание выполнения операции по отгрузке SIM-карты")
    def wait_sim_shipment(self, ship_sims_file_path: str | None = None, correlation_id: str | None = None) -> None:
        if ship_sims_file_path is not None:
            file_name = Path(ship_sims_file_path).name
            correlation_id = None
        elif correlation_id is not None:
            file_name = None
        else:
            raise ValueError("Переданы некорректные параметры в функцию ожидания завершения отгрузки")

        self.wait_sim_shipment_exists(file_name=file_name, correlation_id=correlation_id)
        wait_that(
            lambda: self.get_sim_card_shipment_status(file_name=file_name, correlation_id=None) == "FINISHED",
            exception=UpdateStatusException,
            timeout=120,
            sleep_seconds=5,
            message="Статус не обновился в указанное время",
        )
        self.check_sim_shipment_successful(file_name=file_name, correlation_id=correlation_id)

    @allure.step("API: Получение SIM отгрузки по параметрам")
    def get_sim_shipment_by_file_name_or_correlation_id(
        self, file_name: str | None, correlation_id: str | None
    ) -> dict | None:
        if correlation_id is not None:
            shipment_detection_func = lambda shipment: shipment["correlationId"] == correlation_id
        else:
            shipment_detection_func = lambda shipment: shipment["params"]["simcardRangeParams"]["fileName"] == file_name

        sim_shipments = self.get_sims_shipments().json()["items"]
        sim_shipment = next(
            filter(
                shipment_detection_func,
                sim_shipments,
            ),
            None,
        )
        return sim_shipment

    @allure.step("API: Получить статус отгрузки SIM-карты")
    def get_sim_card_shipment_status(self, file_name: str | None, correlation_id: str | None) -> str | None:
        shipment = self.get_sim_shipment_by_file_name_or_correlation_id(
            file_name=file_name, correlation_id=correlation_id
        )
        return shipment["state"]["code"] if shipment is not None else None

    @allure.step("API: Дождаться появления файла отгрузки SIM-карты в ответе API")
    def wait_sim_shipment_exists(self, file_name: str | None, correlation_id: str | None) -> None:
        wait_that(
            lambda: (
                self.get_sim_shipment_by_file_name_or_correlation_id(file_name=file_name, correlation_id=correlation_id)
                is not None
            ),
            exception=GetSIMShipmentsException,
            timeout=10,
            sleep_seconds=5,
            message=f"В ответе API не найден файл с загружаемыми SIM-картами с указанным именем: {file_name}",
        )

    @allure.step("API: Проверка успешности отгрузки")
    def check_sim_shipment_successful(self, file_name: str | None, correlation_id: str | None) -> None:
        shipment = self.get_sim_shipment_by_file_name_or_correlation_id(
            file_name=file_name, correlation_id=correlation_id
        )
        assert_that(lambda: shipment is not None, "Не найдена отгрузка")
        total_sims = shipment.get("volume", -1)
        done = shipment.get("done", 0)
        assert_that(lambda: done == total_sims, "Неуспешная отгрузка SIM")

    @allure.step("API: Загрузить SIM карты по API")
    def upload_sims_by_api(self, file_path: Path, equipment: Equipment | None = None) -> str:
        """
        Загрузить SIM карты по API LIS
        """
        if equipment is None:
            equipment = stand_context.stand_equipment.gsm_equipment
        file_name = f"test_load_sim_{generate_english_string(10)}.txt"
        form_data = {
            "fileName": file_name,
            "loadSIMCardTemplateId": str(stand_context.stand_equipment.sim_template.load_sim_card_template_id),
            "SIMCardProjectId": str(stand_context.stand_equipment.sim_project_id),
            "equipmentId": str(equipment.equipment_id),
            "macroRegionId": str(equipment.macro_region.macro_region_id),
            "expirationDate": f"{get_shifted_datetime_string(shift='+365d', template='%Y-%m-%dT%H:%M:%S')}.000Z",
            "SIMCardTypeId": str(stand_context.stand_equipment.sim_type_id),
        }
        with open(file_path, "rb") as file:
            files = {"file": (file_name, file, "application/octet-stream")}
            upload_sims = self.post(
                url=f"{BASE_URL_LIS}/OAPI/v1/lis/logicalResources/SIMCards/temporaryData/loadAsync",
                data=form_data,
                files=files,
            )
        self.check_response_status(upload_sims, 204, "Не загружены SIM")
        return file_name

    @allure.step("API: Ожидание загрузки всех SIM")
    def wait_download_sims_count(self, file_name: str, amount: int) -> list:
        wait_that(
            lambda: (
                len(
                    self.get_downloaded_sims(sim_sort="-IMSI", file_name=file_name, limit=amount).json().get("items", [])
                )
                == amount
            ),
            timeout=180,
            sleep_seconds=5,
            exception=AssertionError,
            message="Добавленные SIM-карты не появились в загрузках",
        )
        downloaded_items = self.get_downloaded_sims(sim_sort="-IMSI", file_name=file_name, limit=amount).json()
        return [downloaded_items["items"][i]["loadSimId"] for i in range(amount)]

    @allure.step("API: Введение SIM в эксплуатацию")
    def put_sim_into_operation(self, load_sim_id_list: list) -> None:
        payload = {"macroRegionId": self.macro_region_id, "loadSimIds": load_sim_id_list}

        set_sims_to_use = self.post(
            url=f"{BASE_URL_LIS}/OAPI/v1/lis/logicalResources/SIMCards/temporaryData/prepareBulk",
            json=payload,
            timeout=120,
        )
        self.check_response_status(set_sims_to_use, 204, "Не введены в эксплуатацию SIM")

    @allure.step("API: Загрузить SIM карты по API и перевести в эксплуатацию")
    def upload_sims_set_to_use_by_api(self, file_path: Path, equipment: Equipment = None, amount: int = 2) -> None:
        """
        Загрузить SIM карты по API и перевести в эксплуатацию LIS
        """
        with allure.step("Загрузить SIM карты по API"):
            file_name = self.upload_sims_by_api(file_path, equipment=equipment)
            delay(10, reason="Для корректности операций по API")

        downloaded_sims = self.wait_download_sims_count(file_name, amount)
        with allure.step("Перевести в эксплуатацию"):
            self.put_sim_into_operation(downloaded_sims)

    @allure.step("API: Генерация SIM карт")
    def generate_sim(self, equipment: Equipment, amount: int) -> list[SimCardData] | None:
        available_count = (
            self.get_sim_card_list(
                equipment_id=equipment.equipment_id,
                state_id=[9],
                status_id=[1],
                is_reserved=False,
                macro_region_id=equipment.macro_region.macro_region_id,
            )
            .json()
            .get("listInfo", {})
            .get("count", 0)
        )
        if not stand_context.force_generate and available_count >= amount:
            return None
        sims = self.get_sim_card_list(sim_sort="-IMSI")
        sims_data = self.get_sim_cards_data(sims)
        imsi_template = stand_context.stand_equipment.sim_template.IMSI
        icc_template = stand_context.stand_equipment.sim_template.ICC
        if len(sims_data) == 0:
            biggest_imsi_sim = "25" + "0" * (imsi_template.max_value - imsi_template.min_value - 2)
            biggest_icc_sim = "89701" + "0" * (icc_template.max_value - icc_template.min_value - 5)
        else:
            biggest_imsi_sim = int(sims_data[0].imsi)
            biggest_icc_sim = int(sims_data[0].icc)
        imsi_list = []
        for i in range(1, amount + 1):
            imsi_list.append(biggest_imsi_sim + i)
        icc_list = []
        for i in range(1, amount + 1):
            icc_list.append(biggest_icc_sim + i)

        with wrap_file_and_delete_after(  # type: ignore
            create_txt_file_to_upload_sim(
                file_name=f"resource_generation_{generate_english_string(12)}", icc_list=icc_list, imsi_list=imsi_list
            )
        ) as new_sims_file:
            self.upload_sims_set_to_use_by_api(new_sims_file.path, equipment=equipment, amount=amount)

        correlation_id = self.sim_shipment(start_imsi=imsi_list[0], end_imsi=imsi_list[-1])
        self.wait_sim_shipment(correlation_id=correlation_id)

        return [
            SimCardData(IMSI=str(imsi), ICC=str(icc), switch=SwitchRef(equipment_id=equipment.equipment_id))
            for imsi, icc in zip(imsi_list, icc_list)
        ]
