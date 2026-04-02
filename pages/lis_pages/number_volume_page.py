from dataclasses import dataclass
from pathlib import Path

import allure
import pandas as pd

from common.helpers.download_helper import CheckFile
from common.helpers.time_helpers import delay
from pages.base_page import BasePage
from pages.lis_pages.home_lis_page import HomeLisPage
from pages.locators.lis_locators.number_volume_elements import NumberVolumeLisElements


@dataclass
class NumberInfo:
    color: str = None
    status: str = None
    state: str = None
    is_block: bool = None


class NumberVolumePage(BasePage):
    def __init__(self) -> None:
        super().__init__()

        self.locators = NumberVolumeLisElements()

    @allure.step("Проверить элементы Поиск")
    def check_search_elements(self) -> None:
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
    def check_add_new_number_elements(self, num_type: str = "def") -> None:
        self.locators.START_PHONE_NUMBER.wait_to_be_visible()
        self.locators.COUNT_PHONE_NUMBER.wait_to_be_visible()
        if num_type == "8-800":
            self.locators.CHOOSE_COMMUTATOR_BLOCK.check_attribute_by_value("disabled", "disabled")
            self.locators.NUMBER_TYPE_BLOCK.check_attribute_by_value("disabled", "disabled")
        else:
            self.locators.CHOOSE_COMMUTATOR_BLOCK.element_not_contain_disabled_attribute()
            self.locators.NUMBER_TYPE_BLOCK.element_not_contain_disabled_attribute()
        if num_type == "8-800" or num_type == "abc":
            self.locators.CHOSEN_CATEGORY_BLOCK.check_attribute_by_value("disabled", "disabled")
        else:
            self.locators.CHOSEN_CATEGORY_BLOCK.element_not_contain_disabled_attribute()
            self.locators.CHOSEN_CATEGORY_FIELD.to_contain_text("Телефония")
        self.locators.CHOSEN_STATUS_FIELD.check_attribute_by_value("disabled", "disabled")
        self.locators.OPERATOR_FIELD.wait_to_be_visible()
        if num_type == "abc":
            self.locators.AVAILABLE_TO_LINK.wait_to_have_text("Недоступен")
            self.locators.LOAD_NUMBER_BUTTON.wait_to_be_visible()
        self.locators.USE_GOAL_FIELD.wait_to_be_visible()
        self.locators.COMMENT_FIELD.wait_to_be_visible()
        if num_type != "8-800":
            assert self.locators.NUMBER_TYPE_CHECKBOXES.elements_len() >= 4, "Не отразились типы номеров"

    @allure.step("Проверить элементы Группового редактирования номеров")
    def check_edit_numbers_elements(self) -> None:
        self.locators.CHOSEN_CATEGORY_BLOCK.check_attribute_by_value("disabled", "disabled")
        self.locators.NUMBER_TYPE_BLOCK.wait_to_be_enabled()
        self.locators.CHOOSE_COMMUTATOR_BLOCK.element_not_contain_disabled_attribute()
        self.locators.OPERATOR_FIELD_BLOCK.element_not_contain_disabled_attribute()
        self.locators.USE_GOAL_FIELD.wait_to_be_visible()
        self.locators.COMMENT_FIELD.wait_to_be_visible()
        assert self.locators.NUMBER_TYPE_CHECKBOXES.elements_len() >= 4, "Некорректное количество типов номеров"

    @allure.step("Проверить элементы редактирования номера")
    def check_edit_one_number_elements(self, num_zone: str = "def") -> None:
        self.locators.CHOSEN_STATUS_FIELD.check_attribute_by_value("disabled", "disabled")
        self.locators.CHOSEN_CATEGORY_BLOCK.check_attribute_by_value("disabled", "disabled")
        self.locators.NUMBER_TYPE_BLOCK.wait_to_be_enabled()
        self.locators.CHOOSE_COMMUTATOR_BLOCK.element_not_contain_disabled_attribute()
        self.locators.OPERATOR_FIELD_BLOCK.element_not_contain_disabled_attribute()
        if num_zone == "abc":
            self.locators.AVAILABLE_TO_LINK.wait_to_be_visible()
        self.locators.USE_GOAL_FIELD.wait_to_be_visible()
        self.locators.COMMENT_FIELD.wait_to_be_visible()
        self.locators.NUMBER_TYPE_CHECKBOXES.wait_not_to_be_visible()

    @allure.step("Создать файл для загрузки номеров")
    def create_csv_file_to_upload_number(self, file_name: str, num_list: list) -> Path:
        file_check = CheckFile(file_name)
        file_path = file_check.get_download_file_path()
        df = pd.DataFrame(num_list, columns=["Numbers"])
        df["Numbers"] = df["Numbers"].astype(str) + ";"
        df.to_csv(file_path, index=False, header=False)
        file_check.is_exist()
        return file_path

    @allure.step("Проверить что все чекбокс выключены")
    def check_all_checkboxes_turned_off(self) -> None:
        check_box_html = self.locators.NUMBER_TYPE_ALL_CHECKBOX.inner_html()
        assert "checkbox_checked" not in check_box_html and "n-check-checkbox_partially" not in check_box_html, (
            "Чекбокс не отключен"
        )

    @allure.step("Проверить элементы 'Изменение класса номера (MSISDN)'")
    def check_change_number_class(self) -> None:
        self.locators.MODAL.wait_elements_visible(0)
        self.locators.MODAL_TITLE[0].to_contain_text("Изменение класса номера (MSISDN)")
        self.locators.CHOOSE_CLASS_TITLE.check_attribute_by_value("on-required-label", "")
        self.locators.CONFIRM_CHANGE_CLASS_BTN.check_attribute_by_value("disabled", "disabled")
        self.locators.CANCEL_CHANGE_CLASS_BTN.wait_to_be_enabled()

    @allure.step("Проверить элементы 'Редактирование атрибутов номеров'")
    def check_edit_number_attributes_elements(self, num_zone: str = "def") -> None:
        self.locators.MODAL.wait_elements_visible(0)
        self.locators.MODAL_TITLE[0].wait_to_have_text("Редактирование атрибутов номеров зоны " + num_zone.upper())
        self.locators.CHOSEN_CATEGORY_BLOCK.check_attribute_by_value("disabled", "disabled")
        self.locators.NUMBER_TYPE_BLOCK.check_attribute_by_value("disabled", "disabled")
        self.locators.CHOOSE_COMMUTATOR_BLOCK.element_not_contain_disabled_attribute()
        self.locators.OPERATOR_FIELD_BLOCK.element_not_contain_disabled_attribute()
        if num_zone == "abc":
            self.locators.AVAILABLE_TO_LINK.wait_to_be_visible()
        self.locators.USE_GOAL_FIELD.wait_to_be_visible()
        self.locators.COMMENT_FIELD.wait_to_be_visible()
        self.locators.MASS_SAVE_BUTTON.to_contain_text("Сохранить")
        self.locators.CANCEL_BUTTON.to_contain_text("Отменить")

    @allure.step("Проверить параметры номера {number}")
    def check_number_params(self, number: str, params: NumberInfo) -> None:
        self.locators.PHONE_NUMBERS.wait_to_have_count(1)
        self.locators.PHONE_NUMBERS[0].wait_to_have_text(number)
        if params.color:
            self.locators.PHONE_NUMBERS_COLOUR[0].element_have_css_color("background-color", params.color)
        if params.status:
            self.locators.PHONE_NUMBERS_STATUS[0].wait_to_have_text(params.status)
        if params.state:
            self.locators.PHONE_NUMBERS_STATE[0].wait_to_have_text(params.state)
        if params.is_block is not None:
            if params.is_block:
                self.locators.PHONE_NUMBERS_BLOCKING[0].not_to_contain_text("Не установлена")
            else:
                self.locators.PHONE_NUMBERS_BLOCKING[0].wait_to_have_text("Не установлена")

    @allure.step("Проверка таблицы 'Шаблоны классов номеров'")
    def check_table_class_number_templates(self) -> None:
        self.locators.TEMPLATE_TABLE_LINE.wait_elements_visible(0)
        self.locators.TEMPLATE_TABLE_COLUMN_NAMES[0].wait_to_have_text("Наименование шаблонов")
        self.locators.TEMPLATE_TABLE_COLUMN_NAMES[1].wait_to_have_text("Класс")
        self.locators.TEMPLATE_TABLE_COLUMN_NAMES[2].wait_to_have_text("Приоритет")
        self.locators.TEMPLATE_TABLE_COLUMN_NAMES[3].wait_to_have_text('Используется "по умолчанию"')

    @allure.step("Проверить элементы модального окна 'Добавление шаблона класса'")
    def check_add_class_template_modal(self) -> None:
        self.locators.MODAL.wait_elements_visible(0)
        self.locators.MODAL_TITLE[0].wait_to_have_text("Добавление шаблона класса")
        self.locators.TEMPLATE_NAME_INPUT_TITLE.check_attribute_by_value("on-required-label", "")
        self.locators.TEMPLATE_NAME_INPUT.element_not_contain_disabled_attribute()
        self.locators.CHOOSE_CLASS_BLOCK_TITLE.check_attribute_by_value("on-required-label", "")
        self.locators.CHOOSE_CLASS_BLOCK.element_not_contain_disabled_attribute()
        self.locators.TEMPLATE_PRIORITY_INPUT_TITLE.check_attribute_by_value("on-required-label", "")
        self.locators.TEMPLATE_PRIORITY_INPUT.element_not_contain_disabled_attribute()
        self.locators.TEMPLATE_IS_DEFAULT_CHECKBOX.element_not_contain_disabled_attribute()
        self.locators.ADD_TEMPLATE_MODAL_BTN.wait_to_have_text("Добавить")
        self.locators.CLOSE_ADD_TEMPLATE_BTN.wait_to_have_text("Отменить")

    @allure.step("Проверить элементы модального окна 'Редактирование шаблона класса'")
    def check_edit_template(self) -> None:
        self.locators.MODAL.wait_elements_visible(0)
        self.locators.MODAL_TITLE[0].wait_to_have_text("Редактирование шаблона класса")
        self.locators.EDIT_TEMPLATE_NAME_INPUT.element_not_contain_disabled_attribute()
        self.locators.EDIT_CHOOSE_CLASS_BLOCK.element_not_contain_disabled_attribute()
        self.locators.EDIT_TEMPLATE_PRIORITY_INPUT.element_not_contain_disabled_attribute()
        self.locators.EDIT_TEMPLATE_IS_DEFAULT_CHECKBOX.element_not_contain_disabled_attribute()
        self.locators.EDIT_TEMPLATE_MODAL_BTN.wait_to_have_text("Сохранить")
        self.locators.CLOSE_EDIT_TEMPLATE_BTN.wait_to_have_text("Отменить")

    @allure.step("Проверка таблицы 'Условия шаблона'")
    def check_table_templates_rules(self) -> None:
        self.locators.RULE_TABLE_COLUMN_NAMES[0].wait_to_have_text("Наименование условия")
        self.locators.RULE_TABLE_COLUMN_NAMES[1].wait_to_have_text("Условие")
        self.locators.RULE_TABLE_COLUMN_NAMES[2].wait_to_have_text("Активность")
        self.locators.RULE_TABLE_COLUMN_NAMES[3].wait_to_have_text("Тестовый номер")

    @allure.step("Проверить элементы модального окна 'Добавление условия'")
    def check_add_rule_modal(self) -> None:
        self.locators.MODAL.wait_elements_visible(0)
        self.locators.MODAL_TITLE.wait_to_have_text("Добавление условия")
        self.locators.RULE_NAME_INPUT_TITLE.check_attribute_by_value("on-required-label", "")
        self.locators.RULE_NAME_INPUT.element_not_contain_disabled_attribute()
        self.locators.RULE_CONDITION_INPUT_TITLE.check_attribute_by_value("on-required-label", "")
        self.locators.RULE_CONDITION_INPUT.element_not_contain_disabled_attribute()
        self.locators.RULE_TEST_NUMBER_INPUT.element_not_contain_disabled_attribute()
        self.locators.RULE_IS_ACTIVE_CHECKBOX.element_not_contain_disabled_attribute()
        self.locators.ADD_RULE_MODAL_BTN.wait_to_have_text("Добавить")
        self.locators.CLOSE_ADD_RULE_BTN.wait_to_have_text("Отменить")

    @allure.step("Проверить элементы модального окна 'Редактирование условия'")
    def check_edit_rule(self) -> None:
        self.locators.MODAL.wait_elements_visible(0)
        self.locators.MODAL_TITLE[0].wait_to_have_text("Редактирование условия")
        self.locators.EDIT_RULE_NAME_INPUT.element_not_contain_disabled_attribute()
        self.locators.EDIT_RULE_CONDITION_INPUT.element_not_contain_disabled_attribute()
        self.locators.EDIT_RULE_TEST_NUMBER_INPUT.element_not_contain_disabled_attribute()
        self.locators.EDIT_RULE_IS_ACTIVE_CHECKBOX.element_not_contain_disabled_attribute()
        self.locators.EDIT_RULE_MODAL_BTN.wait_to_have_text("Сохранить")
        self.locators.CLOSE_EDIT_RULE_BTN.wait_to_have_text("Отменить")

    @allure.step("MSISDN Поиск по диапазону")
    def find_msisdn_in_range(self, start: str, end: str) -> None:
        self.locators.MSISDN_FILTER_BTN.click()
        self.locators.MSISDN_OPTION_INTERVAL.click()
        self.locators.MSISDN_OPTION_INTERVAL.wait_to_have_text("По диапазону")
        self.locators.MSISDN_FILTER_INPUT_FROM.fill(start)
        self.locators.MSISDN_FILTER_INPUT_TO.fill(end)

    @allure.step("Ввести номер в эксплуатацию")
    def set_number_in_use(self, number: int) -> None:
        home_page_lis = HomeLisPage()

        home_page_lis.locators.NUMBER_VOLUME_BTN.wait_to_be_visible()
        home_page_lis.locators.NUMBER_VOLUME_BTN.click()
        self.locators.TITLE.wait_to_be_visible()
        self.locators.TITLE.to_contain_text("Номерная ёмкость", timeout_sec=10)

        self.locators.SEARCH_BTN.wait_to_be_visible()
        self.locators.SEARCH_BTN.click()
        self.locators.MSISDN_FILTER_BTN.wait_to_be_visible()
        self.locators.MSISDN_FILTER_BTN.click()
        self.locators.MSISDN_OPTION_VALUE.wait_to_be_visible()
        self.locators.MSISDN_OPTION_VALUE.click()
        self.locators.MSISDN_FILTER_BTN.wait_to_be_visible()
        self.locators.MSISDN_FILTER_INPUT.fill(number)
        self.locators.FILTER_SEARCH_BTN.wait_to_be_visible()
        self.locators.FILTER_SEARCH_BTN.click()

        self.locators.LINE_CHECKBOXES.wait_to_be_visible()
        self.locators.LINE_CHECKBOXES.click(0)
        delay(0.3, reason="Кнопка не активна доли секунды, даже в случае enabled")
        self.locators.SET_IN_USE_BTN.wait_to_be_visible()
        self.locators.SET_IN_USE_BTN.click()
        self.locators.MODAL_FIRST_BTN.wait_to_be_visible()
        self.locators.MODAL_FIRST_BTN.click(0)
