import allure
import pytest

from api.base_requests import BaseRequests
from common.helpers.checker import assert_that
from common.helpers.env_helper import BASE_URL_LIS
from models.lis_resources import SIMCardType, SIMTemplate


class SimCardsReferenceInfoRequests(BaseRequests):
    @pytest.mark.lis
    def __init__(self) -> None:
        super().__init__()

    @allure.step("API: Получение шаблонов SIM-карт")
    def get_sims_template(self, macro_region_ids: list[int]) -> SIMTemplate:
        payload = {"macroRegionIds": macro_region_ids}
        response = self.post(f"{BASE_URL_LIS}/OAPI/v1/lis/logicalResources/SIMCards/fileTemplates/search", json=payload)
        self.check_response_status(response, 200, "Не получены шаблоны SIM-карт")
        items_list = response.json().get("items", [])
        assert_that(lambda: len(items_list) != 0, "Отсутствуют шаблоны для SIM-карт")
        return SIMTemplate.model_validate(items_list[0])

    @allure.step("API: Получение типов SIM-карт")
    def get_sims_types(self, macro_region_ids: list[int]) -> list[SIMCardType]:
        payload = {"macroRegionIds": macro_region_ids}
        response = self.post(f"{BASE_URL_LIS}/ps/v1/logicalResources/SIMCardTypes/search", json=payload)
        self.check_response_status(response, 200, "Не получены типы SIM-карт")
        result = []
        for item in response.json().get("items", []):
            result.append(SIMCardType.model_validate(item))
        return result
