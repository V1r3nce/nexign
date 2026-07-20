import allure
import pytest
from allure_commons.types import AttachmentType

from api.lis_requests.phone_numbers import PhoneNumbersRequests
from models.lis_resources import Equipment
from models.stand_context import stand_context


class TestNumberAdd8800:
    @pytest.fixture(autouse=True)
    def setup(self, sso_stand_login):
        self.phone_api = PhoneNumbersRequests()
        self.equipment = stand_context.stand_equipment.pstn_8800_equipment

    @allure.step("Генерация номеров 8800")
    def test_number_add_8800(self):
        if stand_context.stand_equipment.pstn_8800_equipment is not None:
            for equipment in [self.equipment] if isinstance(self.equipment, Equipment) else self.equipment:
                if (
                    stand_context.stand_equipment.operator_8800 is not None
                    and stand_context.stand_equipment.operator_8800.macro_region.macro_region_id
                    == equipment.macro_region.macro_region_id
                ):
                    self.phone_api.generate_numbers(equipment=equipment, count=stand_context.generate_number_count)
        else:
            allure.attach(
                "Пропуск генерации 8800 номеров в связи с отсутствием коммутаторов",
                name="Skip 8800 numbers generation",
                attachment_type=AttachmentType.TEXT,
            )
