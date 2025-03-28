import re

import allure
import pytest
from playwright.sync_api import APIRequestContext, Page

from api.exceptions import UpdateStatusException
from api.requests.lis_requests.sim_cards import SimCardsRequests
from common.helpers.checker import wait_that
from common.helpers.data_generator import get_current_datetime_string
from common.helpers.time_helpers import delay
from pages.lis_pages.sim_card_page import SimCardsPage
from pages.lis_pages.sim_card_shipment_page import SimCardsShipmentPage
from pages.locators.lis_locators.home_elements_lis import HomeElementsLis


@allure.epic("E2E_09 Подготовка SIM-карт к продаже")
@allure.suite("E2E_09 Подготовка SIM-карт к продаже")
class TestSimCardsShipments:
    @pytest.fixture(autouse=True)
    def setup(self, stand_login_lis: Page) -> None:
        self.sim_shipment_lis = SimCardsShipmentPage(stand_login_lis)
        self.home_page_lis = HomeElementsLis(stand_login_lis)
        self.sim_cards_page = SimCardsPage(stand_login_lis)

    @allure.title("Просмотр списка заданий по отгрузке SIM-карт")
    @allure.id(584936)
    @allure.description("Просмотр списка заданий по отгрузке SIM-карт")
    @allure.tag("can_auth", "success")
    def test_sim_shipment_list(self) -> None:
        self.sim_shipment_lis.sims_shipment_elements.SHIPMENT_BTN.to_contain_text("Отгрузить")
        self.sim_shipment_lis.sims_shipment_elements.SHIPMENT_BACK_BTN.to_contain_text("Вернуть на ГС")
        self.sim_shipment_lis.sims_shipment_elements.REFRESH_BTN.wait_to_be_visible()
        self.sim_shipment_lis.sims_shipment_elements.EXPORT_BTN.wait_to_be_visible()
        self.sim_shipment_lis.sims_shipment_elements.OPERATIONS_IDS.wait_to_be_visible()

    @allure.title("Перемещение SIM-карт в Отдел обслуживания и тестовому дилеру (По списку IMSI из файла)")
    @allure.id(584803)
    @allure.description("Перемещение SIM-карт в Отдел обслуживания и тестовому дилеру (По списку IMSI из файла)")
    @allure.tag("can_auth", "success")
    def test_sim_shipment_to_test_seller_by_imsi_from_file(
        self, api_request_auth_context: APIRequestContext, remove_file_from_download_folder: list
    ) -> None:
        sim_requests = SimCardsRequests(api_request_auth_context)
        sims = sim_requests.get_sim_card_list(sim_sort="-IMSI")
        sims_data = sim_requests.get_sim_cards_data(sims)
        last_sims_imsi, last_sims_icc = (int(sims_data[0].imsi), int(sims_data[0].icc))
        file_name = "load_sim_f_584803.txt"
        new_sims_file_path = self.sim_cards_page.create_txt_file_to_upload_sim(
            file_name,
            [str(last_sims_imsi + 1), str(last_sims_imsi + 2)],
            [str(last_sims_icc + 1), str(last_sims_icc + 2)],
        )
        sim_requests.upload_sims_set_to_use_by_api(new_sims_file_path)
        remove_file_from_download_folder.append(new_sims_file_path)
        file_shipment_name = "shipment_imsis.csv"
        ship_sims_file_path = self.sim_shipment_lis.create_csv_file_to_upload_sim_shipment(
            file_shipment_name, [str(last_sims_imsi + 1), str(last_sims_imsi + 2)]
        )
        remove_file_from_download_folder.append(ship_sims_file_path)

        self.sim_shipment_lis.sims_shipment_elements.SHIPMENT_BTN.to_contain_text("Отгрузить")
        self.sim_shipment_lis.sims_shipment_elements.SHIPMENT_BTN.click()
        with self.sim_shipment_lis.page.expect_file_chooser() as fc_info:
            self.sim_shipment_lis.sims_shipment_elements.SHIPMENT_BY_IMSI_FILE_BTN.click()
        file_chooser = fc_info.value
        file_chooser.set_files(ship_sims_file_path)

        self.sim_shipment_lis.sims_shipment_elements.MODAL_TITLE.wait_to_be_visible()
        self.sim_shipment_lis.sims_shipment_elements.MODAL_TITLE.to_contain_text(0, "Отгрузка SIM")
        self.sim_shipment_lis.sims_shipment_elements.QUANTITY_INPUT.check_attribute_by_value("disabled", "disabled")
        self.sim_shipment_lis.sims_shipment_elements.QUANTITY_INPUT.to_have_value("2")
        self.sim_shipment_lis.sims_shipment_elements.IMSI_START_INPUT.check_attribute_by_value("disabled", "disabled")
        (
            self.sim_shipment_lis.sims_shipment_elements.IMSI_START_INPUT.check_attribute_by_value(
                "placeholder", "из файла"
            )
        )
        self.sim_shipment_lis.sims_shipment_elements.IMSI_END_INPUT.check_attribute_by_value("disabled", "disabled")
        self.sim_shipment_lis.sims_shipment_elements.IMSI_END_INPUT.check_attribute_by_value("placeholder", "из файла")
        self.sim_shipment_lis.sims_shipment_elements.TYPE_DROP_DOWN_BTN.wait_to_be_enabled()
        self.sim_shipment_lis.sims_shipment_elements.PARTNER_NAME_DROP_DOWN_BTN.wait_to_be_enabled()
        self.sim_shipment_lis.sims_shipment_elements.MOVE_BTN.wait_to_be_visible()
        self.sim_shipment_lis.sims_shipment_elements.CANCEL_BTN.wait_to_be_visible()

        self.sim_shipment_lis.sims_shipment_elements.TYPE_DROP_DOWN_BTN.click()
        self.sim_shipment_lis.sims_shipment_elements.TEST_TYPE_OPTION.click()
        self.sim_shipment_lis.sims_shipment_elements.PARTNER_NAME_DROP_DOWN_BTN.click()
        self.sim_shipment_lis.sims_shipment_elements.PARTNER_NAMES_OPTIONS.wait_to_have_count(3)
        self.sim_shipment_lis.sims_shipment_elements.PARTNER_NAMES_OPTIONS[0].click()
        self.sim_shipment_lis.sims_shipment_elements.MOVE_BTN.click()

        self.sim_shipment_lis.sims_shipment_elements.OPERATIONS_TYPES.to_contain_text(0, "Перемещение на дилера")
        self.sim_shipment_lis.sims_shipment_elements.STATUS_FIELDS.to_contain_text(0, "Задание создано")
        delay(1, reason="Время для обработки задания")
        wait_that(
            lambda: sim_requests.get_sims_shipments().json()["items"][0]["state"]["name"] == "Задание выполнено",
            exception=UpdateStatusException,
            timeout=12,
            sleep_seconds=0.5,
            message="Статус не обновился в указанное время",
        )
        self.sim_shipment_lis.sims_shipment_elements.REFRESH_BTN.click()
        self.sim_shipment_lis.sims_shipment_elements.STATUS_FIELDS.to_contain_text(0, "Задание выполнено")
        today_date = get_current_datetime_string(is_full_format=False)
        self.sim_shipment_lis.sims_shipment_elements.PROCES_START_FIELDS.to_contain_text(0, today_date)
        self.sim_shipment_lis.sims_shipment_elements.PROCES_END_FIELDS.to_contain_text(0, today_date)

        self.sim_shipment_lis.sims_shipment_elements.OPERATIONS_IDS[0].click()
        self.sim_shipment_lis.sims_shipment_elements.OPERATION_DETAIL_TITLE.to_contain_text("Подробности операции")
        (
            self.sim_shipment_lis.sims_shipment_elements.COMPLETE_PERCENT.to_contain_text(
                "Задание выполнено (100% выполнено)"
            )
        )
        self.sim_shipment_lis.sims_shipment_elements.OPERATION_DETAIL_TYPE.wait_to_have_text("Перемещение на дилера")
        self.sim_shipment_lis.sims_shipment_elements.OPERATION_DETAIL_PARTNER.wait_to_have_text("NEXIGN Main Store")
        (
            self.sim_shipment_lis.sims_shipment_elements.OPERATION_DETAIL_IMSI_LIST[0].wait_to_have_text(
                str(last_sims_imsi + 1)
            )
        )
        (
            self.sim_shipment_lis.sims_shipment_elements.OPERATION_DETAIL_IMSI_LIST[1].wait_to_have_text(
                str(last_sims_imsi + 2)
            )
        )
        self.sim_shipment_lis.sims_shipment_elements.OPERATION_DETAIL_STATUS_LIST[0].wait_to_have_text("Выполнена")
        self.sim_shipment_lis.sims_shipment_elements.OPERATION_DETAIL_STATUS_LIST[1].wait_to_have_text("Выполнена")

        self.home_page_lis.SIM_CARD_BTN.click()
        self.sim_cards_page.sim_cards_elements.STATE_DATE_CHANGE_HEADER.click()
        delay(1, "Время на прямую сортировку списка")
        self.sim_cards_page.sim_cards_elements.STATE_DATE_CHANGE_HEADER.click()
        delay(1, "Время на обратную сортировку списка")
        first_imsi, second_imsi = (
            self.sim_cards_page.sim_cards_elements.IMSI_NUMBERS[0].text.replace("\n", "").replace(" ", ""),
            self.sim_cards_page.sim_cards_elements.IMSI_NUMBERS[1].text.replace("\n", "").replace(" ", ""),
        )
        assert sorted([str(last_sims_imsi + 1), str(last_sims_imsi + 2)]) == sorted([first_imsi, second_imsi]), (
            "Не отобразились номера переданные дилеру в SIM-карты"
        )
        self.sim_cards_page.sim_cards_elements.NUMBERS_STATES[0].wait_to_have_text("Не связана")
        self.sim_cards_page.sim_cards_elements.NUMBERS_STATES[1].wait_to_have_text("Не связана")

    @allure.title("Просмотр списка SIM-карт (Передача SIM-карт дилеру без фильтрации)")
    @allure.id(584969)
    @allure.description("Просмотр списка SIM-карт (Передача SIM-карт дилеру без фильтрации)")
    @allure.tag("can_auth", "success")
    def test_sim_cards_send_to_seller_without_filter(self) -> None:
        self.home_page_lis.SIM_CARD_BTN.click()
        self.sim_cards_page.sim_cards_elements.PAGE_TABS.wait_to_have_count(3)
        self.sim_cards_page.sim_cards_elements.PAGE_TABS[0].element_have_css_color("color", "dark_grey")
        self.sim_cards_page.sim_cards_elements.MSISDN_HEADER.click()
        delay(1, "Время на прямую сортировку списка")
        self.sim_cards_page.sim_cards_elements.MSISDN_HEADER.click()
        delay(1, "Время на обратную сортировку списка")
        self.sim_cards_page.sim_cards_elements.NUMBERS_STATUSES[0].wait_to_have_text("Свободен")
        self.sim_cards_page.sim_cards_elements.NUMBERS_STATES[0].wait_to_have_text("Не связана")
        self.sim_cards_page.sim_cards_elements.LINE_CHECKBOXES[0].click()
        self.sim_cards_page.sim_cards_elements.SEND_TO_SELLER_BTN.check_attribute_by_value("disabled", "disabled")
        self.sim_cards_page.sim_cards_elements.SEND_TO_SELLER_BTN.click()
        delay(1, reason="Чтобы наверняка убедиться, что окно истории не открылась")
        self.sim_cards_page.sim_cards_elements.MODAL.wait_not_to_be_visible()

    @allure.title("Перемещение SIM-карт на Главный склад (По списку IMSI из файла)")
    @allure.id(584967)
    @allure.description("Перемещение SIM-карт на Главный склад (По списку IMSI из файла)")
    @allure.tag("can_auth", "success")
    def test_sim_shipment_to_main_warehouse_by_imsi_from_file(
        self,
        api_request_auth_context: APIRequestContext,
        remove_file_from_download_folder: list,
    ) -> None:
        sim_requests = SimCardsRequests(api_request_auth_context)
        sims = sim_requests.get_sims_shipments()
        shipment = sim_requests.get_sims_shipment_item(sims.json()["items"][0]["taskId"])
        start_imsi = shipment.json()["items"][0]["startIMSI"]
        end_imsi = shipment.json()["items"][0]["finishIMSI"]
        self.sim_shipment_lis.sims_shipment_elements.SHIPMENT_BTN.to_contain_text("Отгрузить")
        self.sim_shipment_lis.sims_shipment_elements.SHIPMENT_BACK_BTN.click()

        file_shipment_name = "shipment_imsis_584967.csv"
        ship_sims_file_path = self.sim_shipment_lis.create_csv_file_to_upload_sim_shipment(
            file_shipment_name, [start_imsi, end_imsi]
        )
        remove_file_from_download_folder.append(ship_sims_file_path)

        with self.sim_shipment_lis.page.expect_file_chooser() as fc_info:
            self.sim_shipment_lis.sims_shipment_elements.SHIPMENT_BY_IMSI_FILE_BTN.click()
        file_chooser = fc_info.value
        file_chooser.set_files(ship_sims_file_path)

        self.sim_shipment_lis.sims_shipment_elements.MODAL_TITLE.wait_to_be_visible()
        self.sim_shipment_lis.sims_shipment_elements.MODAL_TITLE.to_contain_text(0, "Возврат на ГС")
        self.sim_shipment_lis.sims_shipment_elements.QUANTITY_INPUT.check_attribute_by_value("disabled", "disabled")
        self.sim_shipment_lis.sims_shipment_elements.QUANTITY_INPUT.to_have_value("2")
        self.sim_shipment_lis.sims_shipment_elements.IMSI_START_INPUT.check_attribute_by_value("disabled", "disabled")
        (
            self.sim_shipment_lis.sims_shipment_elements.IMSI_START_INPUT.check_attribute_by_value(
                "placeholder", "из файла"
            )
        )
        self.sim_shipment_lis.sims_shipment_elements.IMSI_END_INPUT.check_attribute_by_value("disabled", "disabled")
        self.sim_shipment_lis.sims_shipment_elements.IMSI_END_INPUT.check_attribute_by_value("placeholder", "из файла")
        self.sim_shipment_lis.sims_shipment_elements.TYPE_DROP_DOWN_BTN.wait_to_be_enabled()
        self.sim_shipment_lis.sims_shipment_elements.PARTNER_NAME_DROP_DOWN_BTN.wait_to_be_enabled()
        self.sim_shipment_lis.sims_shipment_elements.MOVE_BTN.wait_to_be_visible()
        self.sim_shipment_lis.sims_shipment_elements.CANCEL_BTN.wait_to_be_visible()

        self.sim_shipment_lis.sims_shipment_elements.TYPE_DROP_DOWN_BTN.click()
        self.sim_shipment_lis.sims_shipment_elements.TEST_TYPE_OPTION.click()
        self.sim_shipment_lis.sims_shipment_elements.PARTNER_NAME_BLOCK.check_attribute_by_value("disabled", "disabled")
        self.sim_shipment_lis.sims_shipment_elements.PARTNER_NAME_DROP_DOWN_BTN.wait_to_be_visible()
        delay(0.3, reason="Кнопка не активна доли секунды, даже в случае enabled")
        self.sim_shipment_lis.sims_shipment_elements.MOVE_BTN.click()

        self.sim_shipment_lis.sims_shipment_elements.OPERATIONS_TYPES.to_contain_text(0, "Возврат с дилера на ГС")
        self.sim_shipment_lis.sims_shipment_elements.STATUS_FIELDS.to_contain_text(0, "Задание создано")
        delay(1, reason="Время для обработки задания")
        wait_that(
            lambda: sim_requests.get_sims_shipments().json()["items"][0]["state"]["name"] == "Задание выполнено",
            timeout=15,
            sleep_seconds=0.5,
            exception=UpdateStatusException,
            message="Статус не обновился в указанное время",
        )
        self.sim_shipment_lis.sims_shipment_elements.REFRESH_BTN.click()
        self.sim_shipment_lis.sims_shipment_elements.STATUS_FIELDS.to_contain_text(0, "Задание выполнено")
        today_date = get_current_datetime_string(is_full_format=False)
        self.sim_shipment_lis.sims_shipment_elements.PROCES_START_FIELDS.to_contain_text(0, today_date)
        self.sim_shipment_lis.sims_shipment_elements.PROCES_END_FIELDS.to_contain_text(0, today_date)

        self.sim_shipment_lis.sims_shipment_elements.OPERATIONS_IDS[0].click()
        self.sim_shipment_lis.sims_shipment_elements.OPERATION_DETAIL_TITLE.to_contain_text("Подробности операции")
        (
            self.sim_shipment_lis.sims_shipment_elements.COMPLETE_PERCENT.to_contain_text(
                "Задание выполнено (100% выполнено)"
            )
        )
        self.sim_shipment_lis.sims_shipment_elements.OPERATION_DETAIL_TYPE.wait_to_have_text("Возврат с дилера на ГС")
        self.sim_shipment_lis.sims_shipment_elements.OPERATION_DETAIL_PARTNER.wait_to_have_text("NEXIGN Main Store")
        self.sim_shipment_lis.sims_shipment_elements.OPERATION_DETAIL_IMSI_LIST[0].wait_to_have_text(start_imsi)
        self.sim_shipment_lis.sims_shipment_elements.OPERATION_DETAIL_IMSI_LIST[1].wait_to_have_text(end_imsi)
        self.sim_shipment_lis.sims_shipment_elements.OPERATION_DETAIL_STATUS_LIST[0].wait_to_have_text("Выполнена")
        self.sim_shipment_lis.sims_shipment_elements.OPERATION_DETAIL_STATUS_LIST[1].wait_to_have_text("Выполнена")

        self.home_page_lis.SIM_CARD_BTN.click()
        self.sim_cards_page.sim_cards_elements.STATE_DATE_CHANGE_HEADER.click()
        delay(1, "Время на прямую сортировку списка")
        self.sim_cards_page.sim_cards_elements.STATE_DATE_CHANGE_HEADER.click()
        delay(1, "Время на обратную сортировку списка")
        self.sim_cards_page.sim_cards_elements.IMSI_NUMBERS.to_contain_text(0, re.compile(f"{start_imsi}|{end_imsi}"))
        first_imsi, second_imsi = (
            self.sim_cards_page.sim_cards_elements.IMSI_NUMBERS[0].text.replace("\n", "").replace(" ", ""),
            self.sim_cards_page.sim_cards_elements.IMSI_NUMBERS[1].text.replace("\n", "").replace(" ", ""),
        )
        assert sorted([start_imsi, end_imsi]) == sorted([first_imsi, second_imsi]), (
            "Не отобразились номера переданные дилеру в SIM-карты"
        )
        self.sim_cards_page.sim_cards_elements.NUMBERS_STATES[0].wait_to_have_text("Получена")
        self.sim_cards_page.sim_cards_elements.NUMBERS_STATES[1].wait_to_have_text("Получена")

    @allure.title(
        "Перемещение SIM-карт в Отдел обслуживания и тестовому дилеру (По списку IMSI из файла. Неверный файл)"
    )
    @allure.id(585193)
    @allure.description(
        "Перемещение SIM-карт в Отдел обслуживания и тестовому дилеру (По списку IMSI из файла. Неверный файл)"
    )
    @allure.tag("can_auth", "success")
    def test_sim_shipment_to_test_seller_by_imsi_from_wrong_file(
        self, api_request_auth_context: APIRequestContext, remove_file_from_download_folder: list
    ) -> None:
        file_name = "wrong_file_ship_sims.csv"
        wrong_file_path = self.sim_cards_page.create_txt_file_to_upload_sim(
            file_name, ["1" * 15, "2" * 15], ["1" * 17, "2" * 17]
        )
        remove_file_from_download_folder.append(wrong_file_path)

        self.sim_shipment_lis.sims_shipment_elements.SHIPMENT_BTN.to_contain_text("Отгрузить")
        self.sim_shipment_lis.sims_shipment_elements.SHIPMENT_BTN.click()
        with self.sim_shipment_lis.page.expect_file_chooser() as fc_info:
            self.sim_shipment_lis.sims_shipment_elements.SHIPMENT_BY_IMSI_FILE_BTN.click()
        file_chooser = fc_info.value
        file_chooser.set_files(wrong_file_path)

        self.sim_shipment_lis.sims_shipment_elements.MODAL_TITLE.wait_to_be_visible()
        self.sim_shipment_lis.sims_shipment_elements.MODAL_TITLE.to_contain_text(0, "Ошибка")
        (
            self.sim_shipment_lis.sims_shipment_elements.MODAL_BODY_TEXT.to_contain_text(
                0, "Файл wrong_file_ship_sims.csv содержит некорректные данные в строках: 1"
            )
        )

    @allure.title("Перемещение SIM-карт на Главный склад (По списку IMSI из файла. Неверный файл)")
    @allure.id(585188)
    @allure.description("Перемещение SIM-карт на Главный склад (По списку IMSI из файла. Неверный файл)")
    @allure.tag("can_auth", "success")
    def test_sim_shipment_to_main_warehouse_by_imsi_from_wrong_file(
        self, api_request_auth_context: APIRequestContext, remove_file_from_download_folder: list
    ) -> None:
        file_name = "wrong_file_ship_sims.csv"
        wrong_file_path = self.sim_cards_page.create_txt_file_to_upload_sim(
            file_name, ["1" * 15, "2" * 15], ["1" * 17, "2" * 17]
        )
        remove_file_from_download_folder.append(wrong_file_path)

        self.sim_shipment_lis.sims_shipment_elements.SHIPMENT_BTN.to_contain_text("Отгрузить")
        self.sim_shipment_lis.sims_shipment_elements.SHIPMENT_BACK_BTN.click()
        with self.sim_shipment_lis.page.expect_file_chooser() as fc_info:
            self.sim_shipment_lis.sims_shipment_elements.SHIPMENT_BY_IMSI_FILE_BTN.click()
        file_chooser = fc_info.value
        file_chooser.set_files(wrong_file_path)

        self.sim_shipment_lis.sims_shipment_elements.MODAL_TITLE.wait_to_be_visible()
        self.sim_shipment_lis.sims_shipment_elements.MODAL_TITLE.to_contain_text(0, "Ошибка")
        (
            self.sim_shipment_lis.sims_shipment_elements.MODAL_BODY_TEXT.to_contain_text(
                0, "Файл wrong_file_ship_sims.csv содержит некорректные данные в строках: 1"
            )
        )

    @allure.title("Перемещение SIM-карт в Отдел обслуживания и тестовому дилеру (По диапазону IMSI)")
    @allure.id(584603)
    @allure.description("Перемещение SIM-карт в Отдел обслуживания и тестовому дилеру (По диапазону IMSI)")
    @allure.tag("can_auth", "success")
    def test_sim_shipment_to_test_seller_by_imsi_range(self, api_request_auth_context: APIRequestContext) -> None:
        sim_requests = SimCardsRequests(api_request_auth_context)
        sims = sim_requests.get_sim_card_list(sim_sort="-IMSI", status_id=[1], state_id=[2], is_reserved=False)
        sims_data = sim_requests.get_sim_cards_data(sims)
        self.sim_shipment_lis.sims_shipment_elements.SHIPMENT_BTN.to_contain_text("Отгрузить")
        self.sim_shipment_lis.sims_shipment_elements.SHIPMENT_BTN.click()
        self.sim_shipment_lis.sims_shipment_elements.SHIPMENT_BY_IMSI_RANGE_BTN.click()

        self.sim_shipment_lis.sims_shipment_elements.MODAL_TITLE[-1].to_contain_text("Отгрузка SIM")
        self.sim_shipment_lis.sims_shipment_elements.QUANTITY_INPUT.wait_to_be_enabled()
        self.sim_shipment_lis.sims_shipment_elements.IMSI_START_INPUT.wait_to_be_enabled()
        self.sim_shipment_lis.sims_shipment_elements.IMSI_END_INPUT.wait_to_be_enabled()
        self.sim_shipment_lis.sims_shipment_elements.TYPE_DROP_DOWN_BTN.wait_to_be_enabled()
        self.sim_shipment_lis.sims_shipment_elements.PARTNER_NAME_DROP_DOWN_BTN.wait_to_be_enabled()
        self.sim_shipment_lis.sims_shipment_elements.MOVE_BTN.wait_to_be_visible()
        self.sim_shipment_lis.sims_shipment_elements.CANCEL_BTN.wait_to_be_visible()

        self.sim_shipment_lis.sims_shipment_elements.QUANTITY_INPUT.fill("1")
        self.sim_shipment_lis.sims_shipment_elements.IMSI_START_INPUT.fill(sims_data[0].imsi)
        self.sim_shipment_lis.sims_shipment_elements.IMSI_END_INPUT.to_have_value(sims_data[0].imsi)
        self.sim_shipment_lis.sims_shipment_elements.TYPE_DROP_DOWN_BTN.click()
        self.sim_shipment_lis.sims_shipment_elements.TEST_TYPE_OPTION.click()
        self.sim_shipment_lis.sims_shipment_elements.PARTNER_NAME_DROP_DOWN_BTN.click()
        self.sim_shipment_lis.sims_shipment_elements.PARTNER_NAMES_OPTIONS.wait_to_have_count(3)
        self.sim_shipment_lis.sims_shipment_elements.PARTNER_NAMES_OPTIONS[0].click()
        self.sim_shipment_lis.sims_shipment_elements.MOVE_BTN.click()

        self.sim_shipment_lis.sims_shipment_elements.OPERATIONS_TYPES.to_contain_text(0, "Перемещение на дилера")
        self.sim_shipment_lis.sims_shipment_elements.STATUS_FIELDS.to_contain_text(0, "Задание создано")
        delay(1, reason="Время для обработки задания")
        wait_that(
            lambda: sim_requests.get_sims_shipments().json()["items"][0]["state"]["name"] == "Задание выполнено",
            exception=UpdateStatusException,
            timeout=40,
            sleep_seconds=0.5,
            message="Статус не обновился в указанное время",
        )
        self.sim_shipment_lis.sims_shipment_elements.REFRESH_BTN.click()
        self.sim_shipment_lis.sims_shipment_elements.STATUS_FIELDS.to_contain_text(0, "Задание выполнено")
        today_date = get_current_datetime_string(is_full_format=False)
        self.sim_shipment_lis.sims_shipment_elements.PROCES_START_FIELDS.to_contain_text(0, today_date)
        self.sim_shipment_lis.sims_shipment_elements.PROCES_END_FIELDS.to_contain_text(0, today_date)

        self.sim_shipment_lis.sims_shipment_elements.OPERATIONS_IDS[0].click()
        self.sim_shipment_lis.sims_shipment_elements.OPERATION_DETAIL_TITLE.to_contain_text("Подробности операции")
        (
            self.sim_shipment_lis.sims_shipment_elements.COMPLETE_PERCENT.to_contain_text(
                "Задание выполнено (100% выполнено)"
            )
        )
        self.sim_shipment_lis.sims_shipment_elements.OPERATION_DETAIL_TYPE.wait_to_have_text("Перемещение на дилера")
        self.sim_shipment_lis.sims_shipment_elements.OPERATION_DETAIL_PARTNER.wait_to_have_text("NEXIGN Main Store")
        self.sim_shipment_lis.sims_shipment_elements.OPERATION_DETAIL_IMSI_LIST[0].wait_to_have_text(sims_data[0].imsi)
        self.sim_shipment_lis.sims_shipment_elements.OPERATION_DETAIL_STATUS_LIST[0].wait_to_have_text("Выполнена")

        self.home_page_lis.SIM_CARD_BTN.click()
        self.sim_cards_page.sim_cards_elements.STATE_DATE_CHANGE_HEADER.click()
        delay(1, "Время на прямую сортировку списка")
        self.sim_cards_page.sim_cards_elements.STATE_DATE_CHANGE_HEADER.click()
        self.sim_cards_page.sim_cards_elements.IMSI_NUMBERS[0].wait_to_have_text(sims_data[0].imsi)
        self.sim_cards_page.sim_cards_elements.NUMBERS_STATES[0].wait_to_have_text("Не связана")

    @allure.title("Перемещение SIM-карт на Главный склад (По диапазону IMSI)")
    @allure.id(584966)
    @allure.description("Перемещение SIM-карт на Главный склад (По диапазону IMSI)")
    @allure.tag("can_auth", "success")
    def test_sim_shipment_to_main_warehouse_by_imsi_range(self, api_request_auth_context: APIRequestContext) -> None:
        sim_requests = SimCardsRequests(api_request_auth_context)
        sims = sim_requests.get_sims_shipments()
        sims_imsis = [
            item["params"]["simcardRangeParams"]["endIMSI"]
            for item in sims.json()["items"]
            if item["type"]["name"] == "Перемещение на дилера"
        ]
        self.sim_shipment_lis.sims_shipment_elements.SHIPMENT_BTN.to_contain_text("Отгрузить")
        self.sim_shipment_lis.sims_shipment_elements.SHIPMENT_BACK_BTN.click()
        self.sim_shipment_lis.sims_shipment_elements.SHIPMENT_BY_IMSI_RANGE_BTN.click()

        self.sim_shipment_lis.sims_shipment_elements.MODAL_TITLE[-1].to_contain_text("Возврат на ГС")
        self.sim_shipment_lis.sims_shipment_elements.QUANTITY_INPUT.wait_to_be_enabled()
        self.sim_shipment_lis.sims_shipment_elements.IMSI_START_INPUT.wait_to_be_enabled()
        self.sim_shipment_lis.sims_shipment_elements.IMSI_END_INPUT.wait_to_be_enabled()
        self.sim_shipment_lis.sims_shipment_elements.TYPE_DROP_DOWN_BTN.wait_to_be_enabled()
        self.sim_shipment_lis.sims_shipment_elements.PARTNER_NAME_BLOCK.check_attribute_by_value("disabled", "disabled")
        self.sim_shipment_lis.sims_shipment_elements.PARTNER_NAME_DROP_DOWN_BTN.wait_to_be_visible()
        self.sim_shipment_lis.sims_shipment_elements.MOVE_BTN.wait_to_be_visible()
        self.sim_shipment_lis.sims_shipment_elements.CANCEL_BTN.wait_to_be_visible()

        self.sim_shipment_lis.sims_shipment_elements.QUANTITY_INPUT.fill("1")
        self.sim_shipment_lis.sims_shipment_elements.IMSI_START_INPUT.fill(sims_imsis[0])
        self.sim_shipment_lis.sims_shipment_elements.IMSI_END_INPUT.to_have_value(sims_imsis[0])
        self.sim_shipment_lis.sims_shipment_elements.TYPE_DROP_DOWN_BTN.click()
        self.sim_shipment_lis.sims_shipment_elements.TEST_TYPE_OPTION.click()
        delay(0.3, reason="Кнопка не активна доли секунды, даже в случае enabled")
        self.sim_shipment_lis.sims_shipment_elements.MOVE_BTN.click()

        self.sim_shipment_lis.sims_shipment_elements.OPERATIONS_TYPES.to_contain_text(0, "Возврат с дилера на ГС")
        self.sim_shipment_lis.sims_shipment_elements.STATUS_FIELDS.to_contain_text(0, "Задание создано")
        delay(1, reason="Время для обработки задания")
        wait_that(
            lambda: sim_requests.get_sims_shipments().json()["items"][0]["state"]["name"] == "Задание выполнено",
            exception=UpdateStatusException,
            timeout=25,
            sleep_seconds=0.5,
            message="Статус не обновился в указанное время",
        )
        self.sim_shipment_lis.sims_shipment_elements.REFRESH_BTN.click()
        self.sim_shipment_lis.sims_shipment_elements.STATUS_FIELDS.to_contain_text(0, "Задание выполнено")
        today_date = get_current_datetime_string(is_full_format=False)
        self.sim_shipment_lis.sims_shipment_elements.PROCES_START_FIELDS.to_contain_text(0, today_date)
        self.sim_shipment_lis.sims_shipment_elements.PROCES_END_FIELDS.to_contain_text(0, today_date)

        self.sim_shipment_lis.sims_shipment_elements.OPERATIONS_IDS[0].click()
        self.sim_shipment_lis.sims_shipment_elements.OPERATION_DETAIL_TITLE.to_contain_text("Подробности операции")
        (
            self.sim_shipment_lis.sims_shipment_elements.COMPLETE_PERCENT.to_contain_text(
                "Задание выполнено (100% выполнено)"
            )
        )
        self.sim_shipment_lis.sims_shipment_elements.OPERATION_DETAIL_TYPE.wait_to_have_text("Возврат с дилера на ГС")
        self.sim_shipment_lis.sims_shipment_elements.OPERATION_DETAIL_PARTNER.wait_to_have_text("NEXIGN Main Store")
        self.sim_shipment_lis.sims_shipment_elements.OPERATION_DETAIL_IMSI_LIST[0].wait_to_have_text(sims_imsis[0])
        self.sim_shipment_lis.sims_shipment_elements.OPERATION_DETAIL_STATUS_LIST[0].wait_to_have_text("Выполнена")

        self.home_page_lis.SIM_CARD_BTN.click()
        self.sim_cards_page.sim_cards_elements.STATE_DATE_CHANGE_HEADER.click()
        delay(1, "Время на прямую сортировку списка")
        self.sim_cards_page.sim_cards_elements.STATE_DATE_CHANGE_HEADER.click()
        self.sim_cards_page.sim_cards_elements.IMSI_NUMBERS[0].wait_to_have_text(sims_imsis[0])
        self.sim_cards_page.sim_cards_elements.NUMBERS_STATES[0].wait_to_have_text("Получена")
