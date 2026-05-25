import allure
import pytest

from api.lis_requests.phone_numbers import PhoneNumbersRequests
from models.stand_context import stand_context


class TestNumberAddDEF:
    @pytest.fixture(autouse=True)
    def setup(self, sso_stand_login):
        self.phone_api = PhoneNumbersRequests()
        self.equipment_gsm = stand_context.stand_equipment.gsm_equipments
        self.equipment_satellite = stand_context.stand_equipment.satellite_equipments

    @allure.step("Генерация номеров GSM")
    def test_number_add_gsm(self):
        for equipment in self.equipment_gsm:
            self.phone_api.generate_numbers(equipment=equipment, count=stand_context.generate_number_count)

    @allure.step("Генерация номеров Спутниковая связь")
    def test_number_add_satellite(self):
        for equipment in self.equipment_satellite:
            self.phone_api.generate_numbers(equipment=equipment, count=stand_context.generate_number_count)
