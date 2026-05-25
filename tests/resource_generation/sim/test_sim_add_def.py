import allure
import pytest

from api.lis_requests.sim_cards import SimCardsRequests
from models.stand_context import stand_context


class TestSIMAdd:
    @pytest.fixture(autouse=True)
    def setup(self, sso_stand_login):
        self.sim_api = SimCardsRequests()
        self.equipment_gsm = stand_context.stand_equipment.gsm_equipments
        self.equipment_satellite = stand_context.stand_equipment.satellite_equipments

    @allure.step("Генерация SIM карт GSM")
    def test_sim_add_gsm(self):
        for equipment in self.equipment_gsm:
            self.sim_api.generate_sim(equipment=equipment, amount=stand_context.generate_sim_count)

    @allure.step("Генерация SIM карт Спутниковая связь")
    def test_sim_add_satellite(self):
        for equipment in self.equipment_satellite:
            self.sim_api.generate_sim(equipment=equipment, amount=stand_context.generate_sim_count)
