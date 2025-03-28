from pathlib import Path

import allure
import pandas as pd
from playwright.sync_api import APIRequestContext, Page

from api.exceptions import UpdateStatusException
from api.requests.lis_requests.sim_cards import SimCardsRequests
from common.helpers.checker import wait_that
from common.helpers.data_generator import get_current_datetime_string
from common.helpers.download_helper import CheckFile
from common.helpers.time_helpers import delay
from pages.base_page import BasePage
from pages.locators.lis_locators.manage_pre_links import ManagePreLinksLis


class ManagePreLinksPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        self.elements = ManagePreLinksLis(page)

    @allure.step("Создать файл для создания предсвязки для IMSI–MSISDN")
    def create_csv_file_to_upload_imsi_msisdn(self, file_name: str, imsi_list: list, msisdn_list: list) -> str | Path:
        file_check = CheckFile(file_name)
        file_path = file_check.get_download_file_path()
        df = pd.DataFrame({"first_column": imsi_list, "second_column": msisdn_list})
        df.to_csv(file_path, sep=";", index=False, header=False)
        file_check.is_exist()
        return file_path

    @allure.step("Проверить классы номеров, нажать 'Далее'")
    def check_nums_classes_press_next(self) -> None:
        assert self.elements.NUMBER_TYPE_CLASSES.elements_len() >= 4, "Не отражаются классы номеров"
        self.elements.NEXT_BTN.click()

    @allure.step("Добавить комментарий, нажать 'Сформировать'")
    def add_comment_press_form_button(self) -> None:
        self.elements.MODAL_BODY_INPUT.fill("Autotest")
        self.elements.FORM_BTN.wait_to_have_text("Сформировать")
        self.elements.FORM_BTN.click()

    @allure.step("Проверить выполнение операции")
    def check_task_done(self, api_request_auth_context: APIRequestContext, task_name: str) -> None:
        sim_requests = SimCardsRequests(api_request_auth_context)
        self.elements.OPERATIONS_TYPES.to_contain_text(0, task_name)
        self.elements.STATUS_FIELDS.to_contain_text(0, "Задание создано")
        delay(1, reason="Время для обработки задания")
        wait_that(
            lambda: sim_requests.get_pre_links_creation().json()["items"][0]["state"]["name"] == "Задание выполнено",
            exception=UpdateStatusException,
            timeout=25,
            sleep_seconds=0.5,
            message="Статус не обновился в указанное время",
        )
        self.elements.REFRESH_BTN_CREATE_SIM.click()
        self.elements.STATUS_FIELDS.to_contain_text(0, "Задание выполнено")
        today_date = get_current_datetime_string(is_full_format=False)
        self.elements.PROCES_START_FIELDS.to_contain_text(0, today_date)
        self.elements.PROCES_END_FIELDS.to_contain_text(0, today_date)

    @allure.step("Проверить детали операции")
    def check_done_operation_details(self, imsi_num1: str, imsi_num_2: str) -> None:
        self.elements.OPERATIONS_IDS[0].click()
        self.elements.OPERATION_DETAIL_TITLE.to_contain_text("Подробности операции")
        self.elements.COMPLETE_PERCENT.to_contain_text("Задание выполнено (100% выполнено)")
        self.elements.DETAILS_COMMUTATOR.wait_to_have_text("Коммутатор_DEF")
        self.elements.DETAILS_NUMS_TYPE.wait_to_have_text("Федеральная")
        self.elements.DETAILS_GOAL.wait_to_have_text("Общий пул")
        self.elements.OPERATION_DETAIL_IMSI_LIST[0].wait_to_have_text(imsi_num1)
        self.elements.OPERATION_DETAIL_IMSI_LIST[1].wait_to_have_text(imsi_num_2)
        self.elements.OPERATION_DETAIL_STATUS_LIST[0].wait_to_have_text("Выполнена")
        self.elements.OPERATION_DETAIL_STATUS_LIST[1].wait_to_have_text("Выполнена")
