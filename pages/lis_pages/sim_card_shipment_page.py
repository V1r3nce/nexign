from pathlib import Path

import allure
import pandas as pd

from api.lis_requests.sim_cards import SimCardsRequests
from common.helpers.data_generator import generate_random_number
from common.helpers.download_helper import CheckFile
from models.context import test_context
from pages.base_page import BasePage
from pages.locators.lis_locators.sim_cards_shipment import SimCardShipmentLisElements


class SimCardsShipmentPage(BasePage):
    def __init__(self) -> None:
        super().__init__()

        self.sims_shipment_elements = SimCardShipmentLisElements()
        self.sim_cards_requests = SimCardsRequests()

    @staticmethod
    @allure.step("Создать файл для отгрузки по списку IMSI из файла")
    def create_csv_file_to_upload_sim_shipment(file_name: str, num_list: list) -> str | Path:
        file_check = CheckFile(file_name)
        file_path = file_check.get_download_file_path()
        df = pd.DataFrame(num_list, columns=["Numbers"])
        df["Numbers"] = df["Numbers"].astype(str) + ";"
        df.to_csv(file_path, index=False, header=False)
        file_check.is_exist()
        return file_path

    @allure.step("Загрузить файл для отгрузки SIM-карты")
    def upload_sim_shipment_file(self, new_imsi: str) -> str:
        sim_shipment_lis = SimCardsShipmentPage()

        file_shipment_name = f"shipment_imsis_{generate_random_number(6)}.csv"
        ship_sims_file_path = sim_shipment_lis.create_csv_file_to_upload_sim_shipment(file_shipment_name, [new_imsi])

        return ship_sims_file_path

    @allure.step("Отгрузить SIM-карты из файла")
    def ship_sim_card_and_wait_for_completion(self, ship_sims_file_path: str) -> None:
        with allure.step("Нажать кнопку 'Отгрузить' и выбрать файл с SIM-картами"):
            self.sims_shipment_elements.SHIPMENT_BTN.to_contain_text("Отгрузить")
            self.sims_shipment_elements.SHIPMENT_BTN.click()
            with test_context.page.expect_file_chooser() as fc_info:
                self.sims_shipment_elements.SHIPMENT_BY_IMSI_FILE_BTN.click()
                file_chooser = fc_info.value
                file_chooser.set_files(ship_sims_file_path)

        with allure.step("Выбрать тип"):
            self.sims_shipment_elements.TYPE_DROP_DOWN_BTN.wait_to_be_visible()
            self.sims_shipment_elements.TYPE_DROP_DOWN_BTN.click()
            self.sims_shipment_elements.TEST_TYPE_OPTION.wait_to_be_visible()
            self.sims_shipment_elements.TEST_TYPE_OPTION.click()
            self.sims_shipment_elements.PARTNER_NAME_BLOCK.check_attribute_by_value("disabled", "disabled")
            self.sims_shipment_elements.MOVE_BTN.click()

        with allure.step("Дождаться перехода операции в статус 'Задание выполнено'"):
            self.sims_shipment_elements.OPERATIONS_TYPES.to_contain_text(0, "Перемещение на дилера")
            self.sims_shipment_elements.STATUS_FIELDS.to_contain_text(0, "Задание создано")
            self.sim_cards_requests.wait_sim_shipment(ship_sims_file_path)

            self.sims_shipment_elements.REFRESH_BTN.click()
            self.sims_shipment_elements.STATUS_FIELDS.to_contain_text(0, "Задание выполнено")
