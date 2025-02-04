import allure
from playwright.sync_api import Page

from common.helpers.download_helper import CheckFile
from pages.base_page import BasePage
import pandas as pd
from pages.locators.lis_locators.number_volume_elements import NumberVolumeElementsLis


class NumberVolumePage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        self.locators = NumberVolumeElementsLis(page)

    @allure.step("Проверить элементы Поиск")
    def check_search_elements(self):
        self.locators.MSISDN_FILTER_BTN.wait_to_be_visible()
        self.locators.CATEGORY_FILTER_BTN.wait_to_be_visible()
        self.locators.CLASS_FILTER_BTN.wait_to_be_visible()
        self.locators.STATUS_FILTER_BTN.wait_to_be_visible()
        self.locators.CHANGE_STATUS_DATE_BTN.wait_to_be_visible()
        self.locators.STATE_FILTER_BTN.wait_to_be_visible()
        self.locators.OPERATOR_FILTER_BTN.wait_to_be_visible()
        self.locators.USER_FILTER_FIELD.wait_to_be_visible()
        self.locators.NUMBER_TYPE_FILTER_BTN.wait_to_be_visible()
        self.locators.STANDARD_FILTER_BTN.wait_to_be_visible()
        self.locators.COMMUTATOR_FILTER_BTN.wait_to_be_visible()
        self.locators.BLOCKING_FILTER_BTN.wait_to_be_visible()
        self.locators.LINK_NUMBER_FILTER_BTN.wait_to_be_visible()
        self.locators.GOAL_FILTER_BTN.wait_to_be_visible()
        self.locators.BILLING_CONNECTION_FILTER_BTN.wait_to_be_visible()
        self.locators.COMMENT_FILTER_BTN.wait_to_be_visible()

        self.locators.FILTER_SEARCH_BTN.wait_to_be_visible()
        self.locators.CLEAR_FILTER_BTN.wait_to_be_visible()
        self.locators.CHOOSE_SEARCH_TEMPLATE_BTN.wait_to_be_visible()
        self.locators.SAVE_SEARCH_TEMPLATE_BTN.wait_to_be_visible()
        self.locators.HIDE_FILTER_BTN.wait_to_be_visible()

    @allure.step("Проверить элементы Добавление номера")
    def check_add_new_number_elements(self, num_type: str = "def"):
        self.locators.START_PHONE_NUMBER.wait_to_be_visible()
        self.locators.COUNT_PHONE_NUMBER.wait_to_be_visible()
        if num_type == "8-800":
            self.locators.CHOOSE_COMMUTATOR_BLOCK.check_attribute_by_value("disabled", "disabled")
            self.locators.NUMBER_TYPE_BLOCK.check_attribute_by_value("disabled", "disabled")
        else:
            assert self.locators.CHOOSE_COMMUTATOR_BLOCK.element_not_contain_disabled_attribute(), \
                "Блок Коммутатор не активен"
            assert self.locators.NUMBER_TYPE_BLOCK.element_not_contain_disabled_attribute(), \
                "Блок Категория не активен"
        if num_type == "8-800" or num_type == "abc":
            self.locators.CHOSEN_CATEGORY_BLOCK.check_attribute_by_value("disabled", "disabled")
        else:
            assert self.locators.CHOSEN_CATEGORY_BLOCK.element_not_contain_disabled_attribute(), \
                "Блок Категория не активен"
            self.locators.CHOSEN_CATEGORY_FIELD.to_contain_text("Телефония")
        self.locators.CHOSEN_STATUS_FIELD.check_attribute_by_value("disabled", "disabled")
        self.locators.OPERATOR_FIELD.wait_to_be_visible()
        if num_type == "abc":
            self.locators.AVAILABLE_TO_LINK.wait_to_have_text("Недоступен")
            self.locators.LOAD_NUMBER_BUTTON.wait_to_be_visible()
        self.locators.USE_GOAL_FIELD.wait_to_be_visible()
        self.locators.COMMENT_FIELD.wait_to_be_visible()
        self.locators.NUMBER_TYPE_CHECKBOXES.wait_to_have_count(4)

    @allure.step("Создать файл для загрузки номеров")
    def create_csv_file_to_upload_number(self, file_name: str, num_list: list):
        file_check = CheckFile(file_name)
        file_path = file_check.get_download_file_path()
        df = pd.DataFrame(num_list, columns=['Numbers'])
        df['Numbers'] = df['Numbers'].astype(str) + ';'
        df.to_csv(file_path, index=False, header=False)
        file_check.is_exist()
        return file_path

    @allure.step("Проверить что все чекбокс выключены")
    def check_all_checkboxes_turned_off(self):
        check_box_html = self.locators.NUMBER_TYPE_ALL_CHECKBOX.inner_html()
        assert "checkbox_checked" not in check_box_html and "n-check-checkbox_partially" not in check_box_html, \
            "Чекбокс не отключен"
