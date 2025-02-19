import pytest
import allure
from playwright.sync_api import Page, APIRequestContext

from api.requests.lis_requests.sim_cards import SimCardsRequests
from common.helpers.time_helpers import delay
from pages.base_page import BasePage
from pages.locators.lis_locators.create_sim_card_elements import CreateSimCardElementsLis
from pages.locators.lis_locators.home_elements_lis import HomeElementsLis


@allure.epic("E2E_09 Подготовка SIM-карт к продаже")
@allure.suite("E2E_09 Подготовка SIM-карт к продаже")
class TestCreateImsiRange:
    @pytest.fixture(autouse=True)
    def setup(self, stand_login_lis: Page):
        self.base_page = BasePage(stand_login_lis)
        self.home_page_lis = HomeElementsLis(stand_login_lis)
        self.create_sim_card = CreateSimCardElementsLis(stand_login_lis)

    @allure.title("Формирование диапазонов IMSI (Успешное добавление, новые значения, количество)")
    @allure.id(579060)
    @allure.description("Формирование диапазонов IMSI (Успешное добавление, новые значения, количество)")
    @allure.tag("can_auth", "success")
    def test_create_imsi_range_by_quantity(self, api_request_auth_context: APIRequestContext, add_first_imsi_pool):
        imsi_requests = SimCardsRequests(api_request_auth_context)
        self.home_page_lis.SIM_CARD_CREATE_BTN.click()
        self.create_sim_card.PAGE_TABS.wait_to_have_count(3)
        self.create_sim_card.PAGE_TABS[0].wait_to_have_text("Изготовление SIM-карт")
        self.create_sim_card.PAGE_TABS[2].click()
        self.create_sim_card.PAGE_TABS[2].element_have_css_color("color", "dark_grey")

        self.create_sim_card.ADD_BLOCK_BTN.to_contain_text("Добавить блок")
        self.create_sim_card.REFRESH_BTN.wait_to_be_visible()
        self.create_sim_card.ADD_BLOCK_BTN.click()

        imsis = imsi_requests.get_imsi_pools(sim_sort="-imsiEnd")
        imsi_data = imsi_requests.get_imsi_pool_data(imsis)
        self.create_sim_card.MODAL_TITLE[0].wait_to_have_text("Добавление блока")
        self.create_sim_card.PROJECT_VALUE.wait_to_have_text("Общий проект")
        self.create_sim_card.BY_QUANTITY_BTN.element_have_css_color("background", "dark_green")
        self.create_sim_card.QUANTITY_INPUT.to_have_value("1")
        self.create_sim_card.START_RANGE_INPUT.to_have_value(str(int(imsi_data[0].imsi_end) + 1))
        self.create_sim_card.END_RANGE_INPUT.to_have_value(str(int(imsi_data[0].imsi_end) + 1))
        self.create_sim_card.START_RANGE_INPUT.fill(str(int(imsi_data[0].imsi_end) + 1))
        self.create_sim_card.ADD_RANGE_BTN.to_contain_text("Добавить")
        self.create_sim_card.CANCEL_ADD_RANGE_BTN.to_contain_text("Отменить")
        self.create_sim_card.ADD_RANGE_BTN.click()
        self.create_sim_card.CANCEL_ADD_RANGE_BTN.not_to_be_visible()

        self.create_sim_card.START_RANGE_HEADER.click()
        delay(1, "Время на прямую сортировку списка")
        self.create_sim_card.START_RANGE_HEADER.click()
        delay(1, "Время на обратную сортировку списка")
        self.create_sim_card.PROJECT_FIELDS[0].wait_to_have_text("Общий проект")
        self.create_sim_card.STATUS_FIELDS[0].wait_to_have_text("Активный")
        self.create_sim_card.START_RANGE_FIELDS[0].wait_to_have_text(str(int(imsi_data[0].imsi_end) + 1))
        self.create_sim_card.END_RANGE_FIELDS[0].wait_to_have_text(str(int(imsi_data[0].imsi_end) + 1))

    @allure.title("Формирование диапазонов IMSI (Успешное добавление, новые значения, диапазон)")
    @allure.id(579083)
    @allure.description("Формирование диапазонов IMSI (Успешное добавление, новые значения, диапазон)")
    @allure.tag("can_auth", "success")
    def test_create_imsi_range_by_range(self, api_request_auth_context: APIRequestContext):
        imsi_requests = SimCardsRequests(api_request_auth_context)
        self.home_page_lis.SIM_CARD_CREATE_BTN.click()
        self.create_sim_card.PAGE_TABS.wait_to_have_count(3)
        self.create_sim_card.PAGE_TABS[0].wait_to_have_text("Изготовление SIM-карт")
        self.create_sim_card.PAGE_TABS[2].click()
        self.create_sim_card.PAGE_TABS[2].element_have_css_color("color", "dark_grey")

        self.create_sim_card.ADD_BLOCK_BTN.to_contain_text("Добавить блок")
        self.create_sim_card.REFRESH_BTN.wait_to_be_visible()
        self.create_sim_card.ADD_BLOCK_BTN.click()

        imsis = imsi_requests.get_imsi_pools(sim_sort="-imsiEnd")
        imsi_data = imsi_requests.get_imsi_pool_data(imsis)
        self.create_sim_card.MODAL_TITLE[0].wait_to_have_text("Добавление блока")
        self.create_sim_card.PROJECT_VALUE.wait_to_have_text("Общий проект")
        self.create_sim_card.BY_RANGE_BTN.click()
        self.create_sim_card.BY_RANGE_BTN.element_have_css_color("background", "dark_green")
        self.create_sim_card.START_RANGE_INPUT.to_have_value(str(int(imsi_data[0].imsi_end) + 1))
        self.create_sim_card.END_RANGE_INPUT.to_have_value(str(int(imsi_data[0].imsi_end) + 1))

        self.create_sim_card.START_RANGE_INPUT.fill(str(int(imsi_data[0].imsi_end) + 1))
        self.create_sim_card.END_RANGE_INPUT.fill(str(int(imsi_data[0].imsi_end) + 2))
        self.create_sim_card.QUANTITY_INPUT.to_have_value("2")
        self.create_sim_card.ADD_RANGE_BTN.to_contain_text("Добавить")
        self.create_sim_card.CANCEL_ADD_RANGE_BTN.to_contain_text("Отменить")
        self.create_sim_card.ADD_RANGE_BTN.click()
        self.create_sim_card.CANCEL_ADD_RANGE_BTN.not_to_be_visible()

        self.create_sim_card.START_RANGE_HEADER.click()
        delay(1, "Время на прямую сортировку списка")
        self.create_sim_card.START_RANGE_HEADER.click()
        delay(1, "Время на обратную сортировку списка")
        self.create_sim_card.PROJECT_FIELDS[0].wait_to_have_text("Общий проект")
        self.create_sim_card.STATUS_FIELDS[0].wait_to_have_text("Активный")
        self.create_sim_card.START_RANGE_FIELDS[0].wait_to_have_text(str(int(imsi_data[0].imsi_end) + 1))
        self.create_sim_card.END_RANGE_FIELDS[0].wait_to_have_text(str(int(imsi_data[0].imsi_end) + 2))

    @allure.title("Формирование диапазонов IMSI (Неуспешное добавление, частично повторные значения)")
    @allure.id(579082)
    @allure.description("Формирование диапазонов IMSI (Неуспешное добавление, частично повторные значения)")
    @allure.tag("can_auth", "success")
    def test_create_imsi_range_wrong_number_partly(self, api_request_auth_context: APIRequestContext):
        imsi_requests = SimCardsRequests(api_request_auth_context)
        self.home_page_lis.SIM_CARD_CREATE_BTN.click()
        self.create_sim_card.PAGE_TABS.wait_to_have_count(3)
        self.create_sim_card.PAGE_TABS[2].click()
        self.create_sim_card.PAGE_TABS[2].element_have_css_color("color", "dark_grey")

        self.create_sim_card.ADD_BLOCK_BTN.to_contain_text("Добавить блок")
        self.create_sim_card.REFRESH_BTN.wait_to_be_visible()
        self.create_sim_card.ADD_BLOCK_BTN.click()

        imsis = imsi_requests.get_imsi_pools(sim_sort="-imsiEnd")
        imsi_data = imsi_requests.get_imsi_pool_data(imsis)
        self.create_sim_card.MODAL_TITLE[0].wait_to_have_text("Добавление блока")
        self.create_sim_card.PROJECT_VALUE.wait_to_have_text("Общий проект")
        self.create_sim_card.BY_QUANTITY_BTN.element_have_css_color("background", "dark_green")
        self.create_sim_card.START_RANGE_INPUT.to_have_value(str(int(imsi_data[0].imsi_end) + 1))
        self.create_sim_card.END_RANGE_INPUT.to_have_value(str(int(imsi_data[0].imsi_end) + 1))

        self.create_sim_card.START_RANGE_INPUT.fill(imsi_data[0].imsi_end)
        self.create_sim_card.QUANTITY_INPUT.fill("2")
        self.create_sim_card.QUANTITY_INPUT.to_have_value("2")
        self.create_sim_card.ADD_RANGE_BTN.click()

        self.create_sim_card.MODAL_TITLE.wait_to_have_count(3)
        self.create_sim_card.MODAL_TITLE[2].wait_to_have_text("Информация")
        self.create_sim_card.MODAL_BODY_TEXT[1].wait_to_have_text(f"Часть IMSI из диапазона {imsi_data[0].imsi_end} - "
                                                                  f"{int(imsi_data[0].imsi_end) + 1} уже используется в"
                                                                  f" существующих блоках IMSI или SIM-картах в макрорегионе: 1")
        self.create_sim_card.OK_BTN.click()

        self.create_sim_card.MODAL_TITLE[1].wait_to_have_text("Ошибка")
        self.create_sim_card.MODAL_BODY_TEXT[0].wait_to_have_text(
            f"Часть IMSI из диапазона {imsi_data[0].imsi_end} - {int(imsi_data[0].imsi_end) + 1} уже используется в существующих"
            f" блоках IMSI или SIM-картах в макрорегионе: 1")

    @allure.title("Формирование диапазонов IMSI (Неуспешное добавление, повторные значения)")
    @allure.id(579081)
    @allure.description("Формирование диапазонов IMSI (Неуспешное добавление, повторные значения)")
    @allure.tag("can_auth", "success")
    def test_create_imsi_range_wrong_number(self, api_request_auth_context: APIRequestContext):
        imsi_requests = SimCardsRequests(api_request_auth_context)
        self.home_page_lis.SIM_CARD_CREATE_BTN.click()
        self.create_sim_card.PAGE_TABS.wait_to_have_count(3)
        self.create_sim_card.PAGE_TABS[2].click()
        self.create_sim_card.PAGE_TABS[2].element_have_css_color("color", "dark_grey")

        self.create_sim_card.ADD_BLOCK_BTN.to_contain_text("Добавить блок")
        self.create_sim_card.REFRESH_BTN.wait_to_be_visible()
        self.create_sim_card.ADD_BLOCK_BTN.click()

        imsis = imsi_requests.get_imsi_pools(sim_sort="-imsiEnd")
        imsi_data = imsi_requests.get_imsi_pool_data(imsis)
        self.create_sim_card.MODAL_TITLE[0].wait_to_have_text("Добавление блока")
        self.create_sim_card.PROJECT_VALUE.wait_to_have_text("Общий проект")
        self.create_sim_card.BY_QUANTITY_BTN.element_have_css_color("background", "dark_green")
        self.create_sim_card.START_RANGE_INPUT.to_have_value(str(int(imsi_data[0].imsi_end) + 1))
        self.create_sim_card.END_RANGE_INPUT.to_have_value(str(int(imsi_data[0].imsi_end) + 1))

        self.create_sim_card.START_RANGE_INPUT.fill(imsi_data[0].imsi_end)
        self.create_sim_card.QUANTITY_INPUT.fill("1")
        self.create_sim_card.QUANTITY_INPUT.to_have_value("1")
        self.create_sim_card.ADD_RANGE_BTN.click()

        self.create_sim_card.MODAL_TITLE.wait_to_have_count(3)
        self.create_sim_card.MODAL_TITLE[2].wait_to_have_text("Информация")
        self.create_sim_card.MODAL_BODY_TEXT[1].wait_to_have_text(f"Часть IMSI из диапазона {imsi_data[0].imsi_end} - "
                                                                  f"{imsi_data[0].imsi_end} уже используется в существ"
                                                                  f"ующих блоках IMSI или SIM-картах в макрорегионе: 1")
        self.create_sim_card.OK_BTN.click()

        self.create_sim_card.MODAL_TITLE[1].wait_to_have_text("Ошибка")
        self.create_sim_card.MODAL_BODY_TEXT[0].wait_to_have_text(
            f"Часть IMSI из диапазона {imsi_data[0].imsi_end} - {imsi_data[0].imsi_end} уже используется в существующих"
            f" блоках IMSI или SIM-картах в макрорегионе: 1")

    @allure.title("Формирование диапазонов IMSI (Изменение статуса)")
    @allure.id(580280)
    @allure.description("Формирование диапазонов IMSI (Изменение статуса)")
    @allure.tag("can_auth", "success")
    def test_imsi_range_change_status(self, api_request_auth_context: APIRequestContext):
        imsi_requests = SimCardsRequests(api_request_auth_context)
        self.home_page_lis.SIM_CARD_CREATE_BTN.click()
        self.create_sim_card.PAGE_TABS.wait_to_have_count(3)
        self.create_sim_card.PAGE_TABS[2].click()
        self.create_sim_card.PAGE_TABS[2].element_have_css_color("color", "dark_grey")
        imsis = imsi_requests.get_imsi_pools(sim_sort="-imsiEnd", active="Y")
        imsi_data = imsi_requests.get_imsi_pool_data(imsis)
        self.create_sim_card.STATUS_FILTER_FIELD.click()
        self.create_sim_card.STATUS_FILTER_OPTIONS[0].click()
        self.create_sim_card.START_RANGE_HEADER.click()
        delay(1, "Время на прямую сортировку списка")
        self.create_sim_card.START_RANGE_HEADER.click()
        self.create_sim_card.START_RANGE_FIELDS.to_contain_text(0, imsi_data[0].imsi_start)
        self.create_sim_card.STATUS_FIELDS[0].wait_to_have_text("Активный")

        self.create_sim_card.LINE_CHECKBOXES[0].click()
        delay(.3, reason="Кнопка не активна доли секунды при enabled статусе")
        self.create_sim_card.CHANGE_STATUS_BTN.click()
        self.create_sim_card.STATUS_FILTER_FIELD.click()
        self.create_sim_card.STATUS_FILTER_OPTIONS[1].click()
        self.create_sim_card.STATUS_FIELDS[0].wait_to_have_text("Неактивный")
        self.create_sim_card.START_RANGE_FIELDS.to_contain_text(0, imsi_data[0].imsi_start)

        self.create_sim_card.LINE_CHECKBOXES[0].click()
        delay(.3, reason="Кнопка не активна доли секунды при enabled статусе")
        self.create_sim_card.CHANGE_STATUS_BTN.click()
        self.create_sim_card.STATUS_FILTER_FIELD.click()
        self.create_sim_card.STATUS_FILTER_OPTIONS[0].click()
        self.create_sim_card.STATUS_FIELDS[0].wait_to_have_text("Активный")
        self.create_sim_card.START_RANGE_FIELDS.to_contain_text(0, imsi_data[0].imsi_start)

    @allure.title("Формирование диапазонов IMSI (Редактирование параметров)")
    @allure.id(580277)
    @allure.description("Формирование диапазонов IMSI (Редактирование параметров)")
    @allure.tag("can_auth", "success")
    def test_edit_imsi_range(self, api_request_auth_context: APIRequestContext):
        imsi_requests = SimCardsRequests(api_request_auth_context)
        self.home_page_lis.SIM_CARD_CREATE_BTN.click()
        self.create_sim_card.PAGE_TABS.wait_to_have_count(3)
        self.create_sim_card.PAGE_TABS[2].click()
        self.create_sim_card.PAGE_TABS[2].element_have_css_color("color", "dark_grey")
        self.create_sim_card.START_RANGE_HEADER.click()
        delay(1, "Время на прямую сортировку списка")
        self.create_sim_card.START_RANGE_HEADER.click()
        delay(1, "Время на обратную сортировку списка")
        self.create_sim_card.LINE_CHECKBOXES[0].click()
        delay(.3, reason="Кнопка не активна доли секунды при enabled статусе")
        self.create_sim_card.EDIT_BLOCK_BTN.click()

        imsis = imsi_requests.get_imsi_pools(sim_sort="-imsiEnd")
        imsi_data = imsi_requests.get_imsi_pool_data(imsis)
        self.create_sim_card.MODAL_TITLE[0].wait_to_have_text("Редактирование блока")
        self.create_sim_card.PROJECT_VALUE.wait_to_have_text("Общий проект")
        self.create_sim_card.BY_QUANTITY_BTN.element_have_css_color("background", "dark_green")
        self.create_sim_card.START_RANGE_INPUT.to_have_value(imsi_data[0].imsi_start)
        self.create_sim_card.END_RANGE_INPUT.to_have_value(imsi_data[0].imsi_end)

        self.create_sim_card.QUANTITY_INPUT.fill("3")
        self.create_sim_card.QUANTITY_INPUT.to_have_value("3")
        self.create_sim_card.ADD_RANGE_BTN.click()
        self.create_sim_card.CANCEL_ADD_RANGE_BTN.not_to_be_visible()

        self.create_sim_card.PROJECT_FIELDS[0].wait_to_have_text("Общий проект")
        self.create_sim_card.STATUS_FIELDS[0].wait_to_have_text("Активный")
        self.create_sim_card.START_RANGE_FIELDS[0].wait_to_have_text(imsi_data[0].imsi_start)
        self.create_sim_card.END_RANGE_FIELDS[0].wait_to_have_text(str(int(imsi_data[0].imsi_start) + 2))
