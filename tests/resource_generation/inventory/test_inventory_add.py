import allure
import pytest

from api.lis_requests.inventory_items import InventoryItemsRequests
from models.stand_context import stand_context


class TestInventoryAdd:
    @pytest.fixture(autouse=True)
    def setup(self, sso_stand_login):
        self.inventory_api = InventoryItemsRequests()
        self.nomenclatures = stand_context.stand_equipment.nomenclatures

    @allure.step("Генерация оборудования")
    def test_add_inventory_items(self):
        for nomenclature in self.nomenclatures:
            self.inventory_api.generate_inventory_item(
                nomenclature=nomenclature,
                count=stand_context.generate_inventory_count,
                partner_point_id=stand_context.stand_equipment.partner_point_id,
            )
