import re

import allure
import pytest
from playwright.sync_api import APIRequestContext, Page

from api.requests.lis_requests.sim_cards import SimCardsRequests
from pages.base_page import BasePage
from pages.lis_pages.manage_pre_links_page import ManagePreLinksPage
from pages.lis_pages.sim_card_page import SimCardsPage
from pages.lis_pages.sim_card_shipment_page import SimCardsShipmentPage
from pages.locators.lis_locators.home_elements_lis import HomeElementsLis
from tests.lis_test.conftest import CreatedImsis


@allure.epic("E2E_09 Подготовка SIM-карт к продаже")
@allure.suite("E2E_09 Подготовка SIM-карт к продаже")
class TestCreatePreLinks:
    @pytest.fixture(autouse=True)
    def setup(self, stand_login_lis: Page) -> None:
        self.base_page = BasePage(stand_login_lis)
        self.home_page_lis = HomeElementsLis(stand_login_lis)
        self.manage_pre_links = ManagePreLinksPage(stand_login_lis)
        self.sim_cards_page = SimCardsPage(stand_login_lis)
        self.sim_shipment_lis = SimCardsShipmentPage(stand_login_lis)

    @allure.title("Создание предсвязок (по диапазону IMSI)")
    @allure.id(583283)
    @allure.description("Создание предсвязок (по диапазону IMSI)")
    @allure.tag("can_auth", "success")
    @pytest.mark.regress
    def test_create_pre_link_by_imsi(
        self,
        api_request_auth_context: APIRequestContext,
        add_two_msisdn_free_and_open_for_use: tuple,
        add_two_imsi_free_shipped: CreatedImsis,
        remove_file_from_download_folder: list,
    ) -> None:
        remove_file_from_download_folder.append(add_two_imsi_free_shipped.new_sims_file_path)
        remove_file_from_download_folder.append(add_two_imsi_free_shipped.ship_sims_file_path)

        imsi_1, imsi_2 = add_two_imsi_free_shipped.imsi_1, add_two_imsi_free_shipped.imsi_2
        new_number, new_number_2 = add_two_msisdn_free_and_open_for_use

        self.home_page_lis.MANAGE_LINK_BTN.click()
        self.manage_pre_links.elements.PAGE_TITLE.wait_to_have_text("Управление предсвязками")
        self.manage_pre_links.elements.CREATE_BTN.click()
        self.manage_pre_links.elements.BY_IMSI_RANGE_BTN.click()

        self.manage_pre_links.elements.MODAL_TITLE[0].wait_to_have_text("Создание предсвязок")
        self.manage_pre_links.elements.QUANTITY_INPUT_CREATE_SIM.wait_to_be_enabled()
        self.manage_pre_links.elements.QUANTITY_INPUT_CREATE_SIM.fill("2")
        self.manage_pre_links.elements.CHOOSE_COMMUTATOR_BTN.click()
        self.manage_pre_links.elements.COMMUTATOR_TYPE_NAME_SEARCH.fill("Коммутатор_DEF")
        self.base_page.press_keyboard_button("Enter")
        self.manage_pre_links.elements.COMMUTATOR_TYPE_NAMES.wait_to_have_count(1)
        self.manage_pre_links.elements.COMMUTATOR_TYPE_NAMES[0].click(click_count=2)
        self.manage_pre_links.elements.START_RANGE_INPUT_CREATE_SIM.fill(imsi_1)
        self.manage_pre_links.elements.END_RANGE_INPUT_CREATE_SIM.fill(imsi_2)
        self.manage_pre_links.elements.NUMBER_TYPE_FIELD.click()
        self.manage_pre_links.elements.NUMBER_TYPE_OPTIONS[3].to_contain_text("Федеральная")
        self.manage_pre_links.elements.NUMBER_TYPE_OPTIONS[3].click()
        self.manage_pre_links.elements.USE_GOAL_FIELD.to_contain_text("Общий пул")
        self.manage_pre_links.elements.TAKE_FREE_AFTER_INPUT.fill("0")
        self.manage_pre_links.elements.TAKE_CITY_LINKED_ONLY_CHECKBOX.not_to_have_class(
            re.compile("n-check-checkbox_checked")
        )
        self.manage_pre_links.elements.TEMPLATE_INPUT.to_have_value("")
        self.manage_pre_links.elements.START_MSISDN_INPUT.fill(new_number)
        self.manage_pre_links.elements.END_MSISDN_INPUT.fill(new_number_2)
        self.manage_pre_links.elements.CANCEL_BTN.wait_to_be_visible()
        self.manage_pre_links.elements.NEXT_BTN.click()

        self.manage_pre_links.check_nums_classes_press_next()
        self.manage_pre_links.add_comment_press_form_button()

        self.manage_pre_links.check_task_done(api_request_auth_context, "Формирование предсвязок")
        self.manage_pre_links.check_done_operation_details(imsi_1, imsi_2)

    @allure.title("Аннулирование предсвязок (по диапазону IMSI)")
    @allure.id(583719)
    @allure.description("Аннулирование предсвязок (по диапазону IMSI)")
    @allure.tag("can_auth", "success")
    @pytest.mark.regress
    def test_cancel_pre_link_by_imsi_range(
        self, api_request_auth_context: APIRequestContext, remove_file_from_download_folder: list
    ) -> None:
        sim_requests = SimCardsRequests(api_request_auth_context)
        pre_links_items = sim_requests.get_pre_links_creation().json()["items"]
        assert pre_links_items[0]["state"]["name"] == "Задание выполнено", "Статус не 'Задание выполнено'"

        self.home_page_lis.MANAGE_LINK_BTN.click()
        self.manage_pre_links.elements.PAGE_TITLE.wait_to_have_text("Управление предсвязками")
        self.manage_pre_links.elements.CANCEL_TASK_BTN.click()
        self.manage_pre_links.elements.CANCEL_BY_IMSI_RANGE_BTN.click()
        self.manage_pre_links.elements.MODAL_TITLE[0].wait_to_have_text("Аннулирование предсвязок")
        self.manage_pre_links.elements.QUANTITY_INPUT_CREATE_SIM.fill("2")
        self.manage_pre_links.elements.START_RANGE_INPUT_CREATE_SIM.fill(
            pre_links_items[0]["params"]["simcardRangeParams"]["startIMSI"]
        )
        self.manage_pre_links.elements.END_RANGE_INPUT_CREATE_SIM.fill(
            pre_links_items[0]["params"]["simcardRangeParams"]["endIMSI"]
        )
        self.manage_pre_links.elements.MODAL_BODY_INPUT.fill("Автотест аннулирование")
        self.manage_pre_links.elements.CANCEL_BTN.wait_to_be_visible()
        self.manage_pre_links.elements.FORM_BTN.to_contain_text("Аннулировать")
        self.manage_pre_links.elements.FORM_BTN.click()

        self.manage_pre_links.check_task_done(api_request_auth_context, "Аннулирование предсвязок")

    @allure.title("Создание предсвязок (по списку IMSI из файла)")
    @allure.id(583877)
    @allure.description("Создание предсвязок (по списку IMSI из файла)")
    @allure.tag("can_auth", "success")
    @pytest.mark.regress
    def test_create_pre_link_by_imsi_from_file(
        self,
        api_request_auth_context: APIRequestContext,
        add_two_msisdn_free_and_open_for_use: tuple,
        add_two_imsi_free_shipped: CreatedImsis,
        remove_file_from_download_folder: list,
    ) -> None:
        remove_file_from_download_folder.append(add_two_imsi_free_shipped.new_sims_file_path)
        remove_file_from_download_folder.append(add_two_imsi_free_shipped.ship_sims_file_path)

        imsi_1, imsi_2 = add_two_imsi_free_shipped.imsi_1, add_two_imsi_free_shipped.imsi_2
        new_number, new_number_2 = add_two_msisdn_free_and_open_for_use

        self.home_page_lis.MANAGE_LINK_BTN.click()
        self.manage_pre_links.elements.PAGE_TITLE.wait_to_have_text("Управление предсвязками")
        self.manage_pre_links.elements.CREATE_BTN.click()
        with self.manage_pre_links.page.expect_file_chooser() as fc_info:
            self.manage_pre_links.elements.BY_IMSI_RANGE_FROM_FILE_BTN.click()
        file_chooser = fc_info.value
        file_chooser.set_files(add_two_imsi_free_shipped.ship_sims_file_path)

        self.manage_pre_links.elements.MODAL_TITLE[0].wait_to_have_text("Создание предсвязок")
        self.manage_pre_links.elements.QUANTITY_INPUT_CREATE_SIM.to_have_value("2")
        self.manage_pre_links.elements.QUANTITY_INPUT_CREATE_SIM.check_attribute_by_value("disabled", "disabled")
        self.manage_pre_links.elements.CHOOSE_COMMUTATOR_BTN.click()
        self.manage_pre_links.elements.COMMUTATOR_TYPE_NAME_SEARCH.fill("Коммутатор_DEF")
        self.base_page.press_keyboard_button("Enter")
        self.manage_pre_links.elements.COMMUTATOR_TYPE_NAMES.wait_to_have_count(1)
        self.manage_pre_links.elements.COMMUTATOR_TYPE_NAMES[0].click(click_count=2)
        self.manage_pre_links.elements.START_RANGE_INPUT_CREATE_SIM.check_attribute_by_value("placeholder", "из файла")
        self.manage_pre_links.elements.START_RANGE_INPUT_CREATE_SIM.check_attribute_by_value("disabled", "disabled")
        self.manage_pre_links.elements.END_RANGE_INPUT_CREATE_SIM.check_attribute_by_value("placeholder", "из файла")
        self.manage_pre_links.elements.END_RANGE_INPUT_CREATE_SIM.check_attribute_by_value("disabled", "disabled")
        self.manage_pre_links.elements.NUMBER_TYPE_FIELD.click()
        self.manage_pre_links.elements.NUMBER_TYPE_OPTIONS[3].to_contain_text("Федеральная")
        self.manage_pre_links.elements.NUMBER_TYPE_OPTIONS[3].click()
        self.manage_pre_links.elements.USE_GOAL_FIELD.to_contain_text("Общий пул")
        self.manage_pre_links.elements.TAKE_FREE_AFTER_INPUT.fill("0")
        self.manage_pre_links.elements.TAKE_CITY_LINKED_ONLY_CHECKBOX.not_to_have_class(
            re.compile("n-check-checkbox_checked")
        )
        self.manage_pre_links.elements.TEMPLATE_INPUT.to_have_value("")
        self.manage_pre_links.elements.START_MSISDN_INPUT.fill(new_number)
        self.manage_pre_links.elements.END_MSISDN_INPUT.fill(new_number_2)
        self.manage_pre_links.elements.CANCEL_BTN.wait_to_be_visible()
        self.manage_pre_links.elements.NEXT_BTN.click()

        self.manage_pre_links.check_nums_classes_press_next()
        self.manage_pre_links.add_comment_press_form_button()

        self.manage_pre_links.check_task_done(api_request_auth_context, "Формирование предсвязок")
        self.manage_pre_links.check_done_operation_details(imsi_1, imsi_2)

    @allure.title("Создание предсвязок (по списку IMSI из файла. Неверный файл)")
    @allure.id(585171)
    @allure.description("Создание предсвязок (по списку IMSI из файла. Неверный файл)")
    @allure.tag("can_auth", "success")
    @pytest.mark.regress
    def test_create_pre_link_by_imsi_from_wrong_file(self, remove_file_from_download_folder: list) -> None:
        file_name = "wrong_file_link_sims.csv"
        new_sims_file_path = self.sim_cards_page.create_txt_file_to_upload_sim(
            file_name, ["1" * 15, "2" * 15], ["1" * 17, "2" * 17]
        )
        remove_file_from_download_folder.append(new_sims_file_path)

        self.home_page_lis.MANAGE_LINK_BTN.click()
        self.manage_pre_links.elements.PAGE_TITLE.wait_to_have_text("Управление предсвязками")
        self.manage_pre_links.elements.CREATE_BTN.click()
        with self.manage_pre_links.page.expect_file_chooser() as fc_info:
            self.manage_pre_links.elements.BY_IMSI_RANGE_FROM_FILE_BTN.click()
        file_chooser = fc_info.value
        file_chooser.set_files(new_sims_file_path)

        self.manage_pre_links.elements.MODAL_TITLE.wait_to_be_visible()
        self.manage_pre_links.elements.MODAL_TITLE.to_contain_text(0, "Ошибка")
        (
            self.manage_pre_links.elements.MODAL_BODY_TEXT.to_contain_text(
                0, "Файл wrong_file_link_sims.csv содержит некорректные данные в строках: 1"
            )
        )

    @allure.title("Создание предсвязок (по списку IMSI–MSISDN из файла)")
    @allure.id(584120)
    @allure.description("Создание предсвязок (по списку IMSI–MSISDN из файла)")
    @allure.tag("can_auth", "success")
    @pytest.mark.regress
    def test_create_pre_link_by_imsi_msisdn_from_file(
        self,
        api_request_auth_context: APIRequestContext,
        add_two_msisdn_free_and_open_for_use: tuple,
        add_two_imsi_free_shipped: CreatedImsis,
        remove_file_from_download_folder: list,
    ) -> None:
        remove_file_from_download_folder.append(add_two_imsi_free_shipped.new_sims_file_path)
        remove_file_from_download_folder.append(add_two_imsi_free_shipped.ship_sims_file_path)

        imsi_1, imsi_2 = add_two_imsi_free_shipped.imsi_1, add_two_imsi_free_shipped.imsi_2
        new_number, new_number_2 = add_two_msisdn_free_and_open_for_use
        pre_links_file = self.manage_pre_links.create_csv_file_to_upload_imsi_msisdn(
            "pre_link_imsi_msisdn.csv", [imsi_1, imsi_2], [new_number, new_number_2]
        )
        remove_file_from_download_folder.append(pre_links_file)

        self.home_page_lis.MANAGE_LINK_BTN.click()
        self.manage_pre_links.elements.PAGE_TITLE.wait_to_have_text("Управление предсвязками")
        self.manage_pre_links.elements.CREATE_BTN.click()
        with self.manage_pre_links.page.expect_file_chooser() as fc_info:
            self.manage_pre_links.elements.BY_IMSI_MSISDN_FROM_FILE_BTN.click()
        file_chooser = fc_info.value
        file_chooser.set_files(pre_links_file)

        self.manage_pre_links.elements.MODAL_TITLE[0].wait_to_have_text("Создание предсвязок")
        self.manage_pre_links.elements.QUANTITY_INPUT_CREATE_SIM.to_have_value("2")
        self.manage_pre_links.elements.QUANTITY_INPUT_CREATE_SIM.check_attribute_by_value("disabled", "disabled")
        self.manage_pre_links.elements.CHOOSE_COMMUTATOR_BTN.click()
        self.manage_pre_links.elements.COMMUTATOR_TYPE_NAME_SEARCH.fill("Коммутатор_DEF")
        self.base_page.press_keyboard_button("Enter")
        self.manage_pre_links.elements.COMMUTATOR_TYPE_NAMES.wait_to_have_count(1)
        self.manage_pre_links.elements.COMMUTATOR_TYPE_NAMES[0].click(click_count=2)
        self.manage_pre_links.elements.START_RANGE_INPUT_CREATE_SIM.check_attribute_by_value("placeholder", "из файла")
        self.manage_pre_links.elements.START_RANGE_INPUT_CREATE_SIM.check_attribute_by_value("disabled", "disabled")
        self.manage_pre_links.elements.END_RANGE_INPUT_CREATE_SIM.check_attribute_by_value("placeholder", "из файла")
        self.manage_pre_links.elements.END_RANGE_INPUT_CREATE_SIM.check_attribute_by_value("disabled", "disabled")
        self.manage_pre_links.elements.NUMBER_TYPE_FIELD.click()
        self.manage_pre_links.elements.NUMBER_TYPE_OPTIONS[3].to_contain_text("Федеральная")
        self.manage_pre_links.elements.NUMBER_TYPE_OPTIONS[3].click()
        self.manage_pre_links.elements.USE_GOAL_FIELD.to_contain_text("Общий пул")
        self.manage_pre_links.elements.TAKE_FREE_AFTER_INPUT.check_attribute_by_value("disabled", "disabled")
        self.manage_pre_links.elements.TAKE_CITY_LINKED_ONLY_CHECKBOX.not_to_have_class(
            re.compile("n-check-checkbox_checked")
        )
        self.manage_pre_links.elements.TEMPLATE_INPUT.check_attribute_by_value("disabled", "disabled")
        self.manage_pre_links.elements.START_MSISDN_INPUT.check_attribute_by_value("placeholder", "из файла")
        self.manage_pre_links.elements.START_MSISDN_INPUT.check_attribute_by_value("disabled", "disabled")
        self.manage_pre_links.elements.END_MSISDN_INPUT.check_attribute_by_value("placeholder", "из файла")
        self.manage_pre_links.elements.END_MSISDN_INPUT.check_attribute_by_value("disabled", "disabled")
        self.manage_pre_links.elements.CANCEL_BTN.wait_to_be_visible()
        self.manage_pre_links.elements.NEXT_BTN.click()

        self.manage_pre_links.check_nums_classes_press_next()
        self.manage_pre_links.add_comment_press_form_button()

        self.manage_pre_links.check_task_done(api_request_auth_context, "Формирование предсвязок")
        self.manage_pre_links.check_done_operation_details(imsi_1, imsi_2)
