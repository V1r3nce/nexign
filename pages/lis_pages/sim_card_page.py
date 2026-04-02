from pathlib import Path

import allure
import pandas as pd

from api.lis_requests.sim_cards import SimCardsRequests
from common.helpers.data_generator import generate_random_number
from common.helpers.download_helper import CheckFile
from common.helpers.string_helper import remove_line_breaks_and_spaces
from common.helpers.time_helpers import delay
from pages.base_page import BasePage
from pages.lis_pages.home_lis_page import HomeLisPage
from pages.locators.lis_locators.sim_cards_elements import SimCardLisElements


class SimCardsPage(BasePage):
    def __init__(self) -> None:
        super().__init__()

        self.sim_cards_elements = SimCardLisElements()

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
    def create_txt_file_to_upload_sim(file_name: str, imsi_list: list, icc_list: list, amount: int = 2) -> Path:
        file_check = CheckFile(file_name)
        file_path = file_check.get_download_file_path()
        data = {
            "Column1": imsi_list,
            "Column2": icc_list,
            "Column3": ["000"] * amount,
            "Column4": ["000"] * amount,
            "Column5": ["000"] * amount,
            "Column6": ["000"] * amount,
            "Column7": ["000"] * amount,
            "Column8": ["000"] * amount,
            "Column9": ["000"] * amount,
            "Column10": ["000"] * amount,
        }
        df = pd.DataFrame(data)
        df.to_csv(file_path, sep=" ", index=False, header=False)
        file_check.is_exist()
        return file_path

    @allure.step("Загрузить файл с SIM-картой")
    def upload_sim_file(self, new_imsi: str, new_icc: str) -> Path:
        sim_requests = SimCardsRequests()

        file_name = f"load_sim_f_{generate_random_number(6)}.txt"
        new_sims_file_path = self.create_txt_file_to_upload_sim(file_name, [new_imsi], [new_icc], amount=1)
        sim_requests.upload_sims_set_to_use_by_api(new_sims_file_path, amount=1)
        return new_sims_file_path

    @allure.step("Проверить наличие загруженной SIM-карты в списке SIM-карт")
    def check_sim_card_uploaded(self, new_imsi: str) -> None:
        home_page_lis = HomeLisPage()

        home_page_lis.locators.SIM_CARD_BTN.click()
        self.sim_cards_elements.STATE_DATE_CHANGE_HEADER.click()
        delay(1, "Время на прямую сортировку списка")
        self.sim_cards_elements.STATE_DATE_CHANGE_HEADER.click()
        delay(1, "Время на обратную сортировку списка")
        imsi = remove_line_breaks_and_spaces(self.sim_cards_elements.IMSI_NUMBERS[0].text)
        assert imsi == str(new_imsi)

    @allure.step("Выбрать комутатор SIM-карты")
    def select_sim_card_switch(self, switch_name: str) -> None:
        with allure.step("Выбрать SIM-карту"):
            self.sim_cards_elements.LINE_CHECKBOXES.wait_to_be_visible()
            self.sim_cards_elements.LINE_CHECKBOXES.click(0)
            delay(0.3, reason="Кнопка не активна доли секунды, даже в случае enabled")

        with allure.step("Выбрать коммутатор"):
            self.sim_cards_elements.CHOOSE_COMMUTATOR_BTN.wait_to_be_visible()
            self.sim_cards_elements.CHOOSE_COMMUTATOR_BTN.click()
            self.sim_cards_elements.COMMUTATOR_TYPE_NAME_SEARCH.wait_to_be_visible()
            self.sim_cards_elements.COMMUTATOR_TYPE_NAME_SEARCH.fill(switch_name)
            self.press_keyboard_button("Enter")
            self.sim_cards_elements.COMMUTATOR_TYPE_NAMES.wait_to_be_visible()
            self.sim_cards_elements.COMMUTATOR_TYPE_NAMES[0].click(click_count=2)

        with allure.step("Подтвердить выбор в модальном окне"):
            self.sim_cards_elements.MODAL_TITLE[-1].wait_to_have_text("Подтверждение операции")
            self.sim_cards_elements.MODAL_FIRST_BTN.click(-1)

    @allure.step("Получить новый вариант коммутатора для первой строки в Загрузка SIM-карт")
    def get_new_commutator_name_for_first_line_into_upload_sim(self, current_name: str) -> str:
        if current_name == "Коммутатор_DEF":
            return "Коммутатор_ABC"
        else:
            return "Коммутатор_DEF"
