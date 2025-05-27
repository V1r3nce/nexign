from pathlib import Path

import allure
import pandas as pd
from playwright.sync_api import Page

from common.helpers.download_helper import CheckFile
from pages.base_page import BasePage
from pages.locators.lis_locators.sim_cards_elements import SimCardElementsLis


class SimCardsPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        self.sim_cards_elements = SimCardElementsLis(page)

    @allure.step("Проверить элементы Поиск")
    def check_search_elements(self) -> None:
        self.sim_cards_elements.IMSI_FILTER_BTN.wait_to_be_visible()
        self.sim_cards_elements.ICC_FILTER_BTN.wait_to_be_visible()
        self.sim_cards_elements.MSISDN_FILTER_BTN.wait_to_be_visible()
        self.sim_cards_elements.STATE_FILTER_BTN.wait_to_be_visible()
        self.sim_cards_elements.STATUS_FILTER_BTN.wait_to_be_visible()
        self.sim_cards_elements.EXPIRATION_DATE_INPUT.wait_to_be_enabled()
        self.sim_cards_elements.CHOSEN_COMMUTATOR_INPUT.wait_to_be_enabled()
        self.sim_cards_elements.PROJECT_FILTER_BTN.wait_to_be_visible()
        self.sim_cards_elements.CHOSEN_TYPE_INPUT.wait_to_be_enabled()
        self.sim_cards_elements.LINK_POOL_INPUT.wait_to_be_enabled()
        self.sim_cards_elements.MAP_INPUT.wait_to_be_enabled()
        self.sim_cards_elements.BLOCKING_FILTER_BTN.wait_to_be_visible()
        self.sim_cards_elements.BILLING_LINK_FILTER_BTN.wait_to_be_visible()
        self.sim_cards_elements.AGENT_INPUT.wait_to_be_enabled()
        self.sim_cards_elements.TARIFF_INPUT.wait_to_be_enabled()
        self.sim_cards_elements.TECH_FILTER_BTN.wait_to_be_visible()
        self.sim_cards_elements.SEGMENT_FILTER_BTN.wait_to_be_visible()
        self.sim_cards_elements.REGISTRY_DATE_FILTER_BTN.wait_to_be_visible()
        self.sim_cards_elements.EID_INPUT.wait_to_be_enabled()
        self.sim_cards_elements.SUPPLIER_FILTER_BTN.wait_to_be_visible()
        self.sim_cards_elements.FILTER_SEARCH_BTN.wait_to_be_visible()
        self.sim_cards_elements.CLEAR_FILTER_BTN.wait_to_be_visible()
        self.sim_cards_elements.CHOOSE_SEARCH_TEMPLATE_BTN.wait_to_be_visible()
        self.sim_cards_elements.SAVE_SEARCH_TEMPLATE_BTN.wait_to_be_visible()

    @allure.step("Получить новый вариант Дилер для первой строки")
    def get_new_seller_name_for_first_line(self) -> str:
        if "NEXIGN Service Store" in self.sim_cards_elements.SELLER_FIELDS[0].text:
            return "NEXIGN технологический склад"
        else:
            return "NEXIGN Service Store"

    @allure.step("Выбрать новый вариант Дилер")
    def choose_new_seller_name(self, seller: str) -> None:
        if seller == "NEXIGN технологический склад":
            self.sim_cards_elements.SELLER_TECH_WAREHOUSE.hover()
            self.sim_cards_elements.SELLER_TECH_WAREHOUSE.click()
        elif seller == "NEXIGN Service Store":
            self.sim_cards_elements.SELLER_SERVICE_STORE.hover()
            self.sim_cards_elements.SELLER_SERVICE_STORE.click()

    @allure.step("Получить новый вариант коммутатора для первой строки")
    def get_new_commutator_name_for_first_line(self) -> str:
        self.sim_cards_elements.NUMBERS_COMMUTATOR.to_contain_text(0, "Коммутатор")
        if "Коммутатор_DEF" in self.sim_cards_elements.NUMBERS_COMMUTATOR[0].text:
            return "Коммутатор_ABC"
        else:
            return "Коммутатор_DEF"

    @staticmethod
    @allure.step("Создать файл для загрузки SIM")
    def create_txt_file_to_upload_sim(file_name: str, imsi_list: list, icc_list: list) -> Path:
        file_check = CheckFile(file_name)
        file_path = file_check.get_download_file_path()
        data = {
            "Column1": imsi_list,
            "Column2": icc_list,
            "Column3": ["000", "000"],
            "Column4": ["000", "000"],
            "Column5": ["000", "000"],
            "Column6": ["000", "000"],
            "Column7": ["000", "000"],
            "Column8": ["000", "000"],
            "Column9": ["000", "000"],
            "Column10": ["000", "000"],
        }
        df = pd.DataFrame(data)
        df.to_csv(file_path, sep=" ", index=False, header=False)
        file_check.is_exist()
        return file_path

    @allure.step("Получить новый вариант коммутатора для первой строки в Загрузка SIM-карт")
    def get_new_commutator_name_for_first_line_into_upload_sim(self, current_name: str) -> str:
        if current_name == "Коммутатор_DEF":
            return "Коммутатор_ABC"
        else:
            return "Коммутатор_DEF"
