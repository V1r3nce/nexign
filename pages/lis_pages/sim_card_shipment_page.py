import allure
from playwright.sync_api import Page
import pandas as pd
from common.helpers.download_helper import CheckFile
from pages.base_page import BasePage
from pages.locators.lis_locators.sim_cards_shipment import SimCardShipmentElementsLis


class SimCardsShipmentPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        self.sims_shipment_elements = SimCardShipmentElementsLis(page)

    @staticmethod
    @allure.step("Создать файл для отгрузки по списку IMSI из файла")
    def create_csv_file_to_upload_sim_shipment(file_name: str, num_list: list):
        file_check = CheckFile(file_name)
        file_path = file_check.get_download_file_path()
        df = pd.DataFrame(num_list, columns=['Numbers'])
        df['Numbers'] = df['Numbers'].astype(str) + ';'
        df.to_csv(file_path, index=False, header=False)
        file_check.is_exist()
        return file_path
