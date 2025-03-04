import pytest
import allure
from playwright.sync_api import Page
from pages.locators.lis_locators.sim_cards_shipment import SimCardShipmentElementsLis


@allure.epic("E2E_09 Подготовка SIM-карт к продаже")
@allure.suite("E2E_09 Подготовка SIM-карт к продаже")
class TestSimCardsPreview:
    @pytest.fixture(autouse=True)
    def setup(self, stand_login_lis: Page):
        self.sim_shipment_lis = SimCardShipmentElementsLis(stand_login_lis)

    @allure.title("Просмотр списка заданий по отгрузке SIM-карт")
    @allure.id(584936)
    @allure.description("Просмотр списка заданий по отгрузке SIM-карт")
    @allure.tag("can_auth", "success")
    def test_sim_shipment_list(self):
        self.sim_shipment_lis.SHIPMENT_BTN.to_contain_text("Отгрузить")
        self.sim_shipment_lis.SHIPMENT_BACK_BTN.to_contain_text("Вернуть на ГС")
        self.sim_shipment_lis.REFRESH_BTN.wait_to_be_visible()
        self.sim_shipment_lis.EXPORT_BTN.wait_to_be_visible()
        self.sim_shipment_lis.OPERATIONS_IDS.wait_to_be_visible()
