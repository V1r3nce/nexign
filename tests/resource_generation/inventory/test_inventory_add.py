import allure
import pytest

from api.lis_requests.inventory_items import InventoryItemsRequests
from api.lis_requests.sim_cards import SimCardsRequests
from common.helpers.checker import assert_that
from models.stand_context import stand_context


class TestInventoryAdd:
    @pytest.fixture(autouse=True)
    def setup(self, sso_stand_login):
        self.inventory_api = InventoryItemsRequests()
        self.sim_api = SimCardsRequests()
        self.nomenclatures = stand_context.stand_equipment.nomenclatures
        self.linked_nomenclatures = stand_context.stand_equipment.default_linked_nomenclature
        self.equipment_satellite = stand_context.stand_equipment.satellite_equipments
        self.default_satellite = stand_context.stand_equipment.default_satellite_equipment

    @allure.step("Генерация оборудования")
    def test_add_inventory_items(self):
        for nomenclature in self.nomenclatures:
            self.inventory_api.generate_inventory_item(
                nomenclature=nomenclature,
                count=stand_context.generate_inventory_count,
                partner_point_id=stand_context.stand_equipment.partner_point_id,
            )

    @allure.step("Генерация оборудования")
    def test_add_linked_inventory_items(self):
        for nomenclature in self.linked_nomenclatures:
            inventory_items = self.inventory_api.generate_inventory_item(
                nomenclature=nomenclature,
                count=stand_context.generate_linked_resources_count,
                partner_point_id=stand_context.stand_equipment.partner_point_id,
                force=True,
            )
            assert_that(lambda: inventory_items is not None, "Ошибка генерации оборудования")
            sims = self.sim_api.generate_sim(
                equipment=self.default_satellite, amount=stand_context.generate_linked_resources_count
            )
            assert_that(lambda: sims is not None, "Ошибка генерации SIM карт для связывания")
            self.inventory_api.inventory_items_link(inventory_items, sims)
