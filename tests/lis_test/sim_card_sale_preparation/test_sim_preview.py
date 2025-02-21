import re
import pytest
import allure
from playwright.sync_api import Page, APIRequestContext
from common.helpers.data_generator import get_shifted_datetime_string
from api.requests.lis_requests.sim_cards import SimCardsRequests
from common.helpers.download_helper import CheckFile
from common.helpers.time_helpers import delay
from pages.base_page import BasePage
from pages.locators.lis_locators.home_elements_lis import HomeElementsLis
from pages.locators.lis_locators.sim_cards_elements import SimCardElementsLis


@allure.epic("E2E_09 Подготовка SIM-карт к продаже")
@allure.suite("E2E_09 Подготовка SIM-карт к продаже")
class TestSimCardsPreview:
    @pytest.fixture(autouse=True)
    def setup(self, stand_login_lis: Page):
        self.base_page = BasePage(stand_login_lis)
        self.home_page_lis = HomeElementsLis(stand_login_lis)
        self.sim_cards_elements = SimCardElementsLis(stand_login_lis)

    @allure.title("Просмотр списка SIM-карт")
    @allure.id(578445)
    @allure.description("Просмотр списка SIM-карт")
    @allure.tag("can_auth", "success")
    def test_sim_card_preview(self, api_request_auth_context: APIRequestContext):
        sim_requests = SimCardsRequests(api_request_auth_context)
        sims = sim_requests.get_sim_card_list()
        sims_data = sim_requests.get_sim_cards_data(sims)
        self.home_page_lis.SIM_CARD_BTN.click()

        self.sim_cards_elements.PAGE_TABS.wait_to_have_count(3)
        self.sim_cards_elements.PAGE_TABS[0].element_have_css_color("color", "dark_grey")
        self.sim_cards_elements.REFRESH_BTN.wait_to_be_visible()
        self.sim_cards_elements.SEARCH_BTN.wait_to_be_visible()
        self.sim_cards_elements.REFRESH_BTN.click()

        self.sim_cards_elements.LINE_CHECKBOXES.wait_to_be_visible(3)
        self.sim_cards_elements.LINE_CHECKBOXES.click(0)
        self.sim_cards_elements.LINE_CHECKBOXES.click(3)
        self.sim_cards_elements.TABLE_LINE[0].to_have_class(class_name=re.compile(r"js-selected"))
        self.sim_cards_elements.TABLE_LINE[3].to_have_class(class_name=re.compile(r"js-selected"))
        self.sim_cards_elements.IMSI_NUMBERS[0].wait_to_have_text(sims_data[0].imsi)
        self.sim_cards_elements.NUMBERS_COUNTER.to_contain_text("Всего*")
        self.sim_cards_elements.NUMBERS_COUNTER.to_contain_text(str(sims.json()['listInfo']['count']))
        self.sim_cards_elements.REFRESH_BTN.wait_to_be_visible()
        self.sim_cards_elements.SEARCH_BTN.wait_to_be_visible()

    @allure.title("Просмотр списка SIM-карт (Выгрузка в файл)")
    @allure.id(578468)
    @allure.description("Просмотр списка SIM-карт (Выгрузка в файл)")
    @allure.tag("can_auth", "success")
    def test_sim_card_preview_download_file(self, api_request_auth_context: APIRequestContext,
                                            remove_file_from_download_folder):
        sim_requests = SimCardsRequests(api_request_auth_context)
        sims = sim_requests.get_sim_card_list()
        self.home_page_lis.SIM_CARD_BTN.wait_to_be_visible()
        self.home_page_lis.SIM_CARD_BTN.click()

        self.sim_cards_elements.PAGE_TABS.wait_to_have_count(3)
        self.sim_cards_elements.PAGE_TABS[0].element_have_css_color("color", "dark_grey")
        self.sim_cards_elements.REFRESH_BTN.click()
        self.sim_cards_elements.CHECK_ALL_BTN.click()
        delay(.3, reason="Кнопка не активна доли секунды, даже в случае enabled")
        self.sim_cards_elements.DOWNLOAD_BTN.hover()
        self.sim_cards_elements.DOWNLOAD_BTN.click()
        self.sim_cards_elements.MODAL[0].wait_to_be_visible()
        self.sim_cards_elements.MODAL_TITLE[0].to_contain_text("Подтверждение операции")
        with self.sim_cards_elements.page.expect_download(timeout=20000) as download_info:
            self.sim_cards_elements.FIRST_BTN[0].click()
        download = download_info.value
        file_name = download.suggested_filename
        self.file_check = CheckFile(file_name)
        download.save_as(self.file_check.path)
        remove_file_from_download_folder.append(file_name)
        self.file_check.check_excel_file_group_of_fields_contains([[0, 0], [0, 1], [0, 2]],
                                                                  ["IMSI", "ICC", "MSISDN"])
        self.file_check.check_excel_file_contain_filled_rows(sims.json()['listInfo']['count'] + 1)

    @allure.title("Просмотр списка SIM-карт (Изменение срока действия SIM-карты)")
    @allure.id(580313)
    @allure.description("Просмотр списка SIM-карт (Изменение срока действия SIM-карты)")
    @allure.tag("can_auth", "success")
    def test_sim_card_preview_change_expiration_date(self):
        self.home_page_lis.SIM_CARD_BTN.wait_to_be_visible()
        self.home_page_lis.SIM_CARD_BTN.click()

        self.sim_cards_elements.PAGE_TABS.wait_to_have_count(3)
        self.sim_cards_elements.PAGE_TABS[0].element_have_css_color("color", "dark_grey")
        self.sim_cards_elements.REFRESH_BTN.click()
        self.sim_cards_elements.LINE_CHECKBOXES.wait_to_be_visible(3)
        self.sim_cards_elements.LINE_CHECKBOXES.click(0)
        delay(.3, reason="Кнопка не активна доли секунды, даже в случае enabled")
        self.sim_cards_elements.EDIT_EXPIRATION_DATE_BTN.click()
        self.sim_cards_elements.MODAL_TITLE[-1].wait_to_have_text("Изменение срока действия")
        new_date = get_shifted_datetime_string("+500d", is_full_format=False)
        self.sim_cards_elements.CONFIRM_CHANGE_EXPIRATION_DATE_BTN.wait_to_be_visible()
        self.sim_cards_elements.SECOND_BTN[-1].wait_to_be_visible()
        self.sim_cards_elements.MODAL_EXPIRATION_DATE_INPUT.type(new_date)
        self.sim_cards_elements.CONFIRM_CHANGE_EXPIRATION_DATE_BTN.click()
        self.sim_cards_elements.MODAL_TITLE[-1].to_contain_text("Подтверждение операции")
        self.sim_cards_elements.FIRST_BTN[-1].click()
        self.sim_cards_elements.EXPIRATIONS_DATES.to_contain_text(0, new_date)

    @allure.title("Просмотр списка SIM-карт (История SIM-карты)")
    @allure.id(578868)
    @allure.description("Просмотр списка SIM-карт (История SIM-карты)")
    @allure.tag("can_auth", "success")
    def test_sim_card_history(self, api_request_auth_context: APIRequestContext):
        sim_requests = SimCardsRequests(api_request_auth_context)
        sims = sim_requests.get_sim_card_list()
        sims_data = sim_requests.get_sim_cards_data(sims)
        self.home_page_lis.SIM_CARD_BTN.wait_to_be_visible()
        self.home_page_lis.SIM_CARD_BTN.click()

        self.sim_cards_elements.PAGE_TABS.wait_to_have_count(3)
        self.sim_cards_elements.PAGE_TABS[0].element_have_css_color("color", "dark_grey")
        self.sim_cards_elements.REFRESH_BTN.click()
        self.sim_cards_elements.LINE_CHECKBOXES.wait_to_be_visible(3)
        self.sim_cards_elements.LINE_CHECKBOXES.click(0)
        delay(.3, reason="Кнопка не активна доли секунды, даже в случае enabled")
        self.sim_cards_elements.HISTORY_BTN.click()

        self.sim_cards_elements.MODAL_TITLE[-1].wait_to_have_text(f"История по IMSI {sims_data[0].imsi}")
        self.sim_cards_elements.HISTORY_TYPE_BTN.wait_to_have_count(3)
        self.sim_cards_elements.REFRESH_MODAL_TABLE_BTN.wait_to_be_visible()
        self.sim_cards_elements.HISTORY_TYPE_BTN[0].to_contain_text("LIS")
        self.sim_cards_elements.HISTORY_TYPE_BTN[1].to_contain_text("Greenfield")
        self.sim_cards_elements.HISTORY_TYPE_BTN[2].to_contain_text("Операций")

        self.sim_cards_elements.HISTORY_TYPE_BTN[0].element_have_css_color("background", "dark_green")
        assert self.sim_cards_elements.TABLE_FIRST_COLUMN_ELEMENTS.elements_len() > 0, "Не отображаются строки вкладки LIS Истории изменений"
        assert re.search(r"Занят|Свободен|Недоступен", self.sim_cards_elements.TABLE_FIRST_COLUMN_ELEMENTS[0].text),\
            "Некорректное отображение статуса"
        self.sim_cards_elements.HISTORY_TYPE_BTN[2].click()
        self.sim_cards_elements.HISTORY_TYPE_BTN[2].element_have_css_color("background", "dark_green")
        assert self.sim_cards_elements.TABLE_FIRST_COLUMN_ELEMENTS.elements_len() > 0, "Не отображаются строки вкладки Операций Истории изменений"
        delay(.5, reason="Ожидание для обновления строки")
        assert re.search(r"\d{1,5}", self.sim_cards_elements.TABLE_FIRST_COLUMN_ELEMENTS[0].text), "Некорректное отображение ID операции"

    @allure.title("Просмотр списка SIM-карт (История SIM-карты, Несколько карт)")
    @allure.id(578872)
    @allure.description("Просмотр списка SIM-карт (История SIM-карты, Несколько карт)")
    @allure.tag("can_auth", "success")
    def test_sim_cards_history_btn(self):
        self.home_page_lis.SIM_CARD_BTN.wait_to_be_visible()
        self.home_page_lis.SIM_CARD_BTN.click()

        self.sim_cards_elements.PAGE_TABS.wait_to_have_count(3)
        self.sim_cards_elements.PAGE_TABS[0].element_have_css_color("color", "dark_grey")
        self.sim_cards_elements.REFRESH_BTN.click()
        self.sim_cards_elements.LINE_CHECKBOXES.wait_to_be_visible(3)
        self.sim_cards_elements.LINE_CHECKBOXES.click(0)
        self.sim_cards_elements.LINE_CHECKBOXES.click(1)
        delay(.3, reason="Кнопка не активна доли секунды, даже в случае enabled")
        self.sim_cards_elements.HISTORY_BTN.check_attribute_by_value("disabled", "disabled")
        self.sim_cards_elements.HISTORY_BTN.click()
        delay(1, reason="Чтобы наверняка убедиться, что окно истории не открылась")
        self.sim_cards_elements.MODAL.wait_not_to_be_visible()
