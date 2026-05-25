import allure
import pytest

from api.lis_requests.inventory_items import InventoryItemsRequests
from models.stand_context import stand_context


class TestInventoryAdd1:
    @pytest.fixture(autouse=True)
    def setup(self, sso_stand_login):
        self.inventory_api = InventoryItemsRequests()
        self.nomenclatures = stand_context.stand_equipment.nomenclatures

    @allure.step("Генерация оборудования 1 поток")
    def test_add_inventory_items_1(self):
        for i in range(0, len(self.nomenclatures), 2):
            self.inventory_api.generate_inventory_item(
                nomenclature=self.nomenclatures[i],
                count=stand_context.generate_inventory_count,
                partner_point_id=stand_context.stand_equipment.partner_point_id,
            )
