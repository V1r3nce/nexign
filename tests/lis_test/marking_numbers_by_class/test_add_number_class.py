import re

import allure
import pytest
from playwright.sync_api import Page

from pages.lis_pages.directories_page import DirectoriesPage
from pages.lis_pages.home_lis_page import HomeLisPage
from pages.lis_pages.number_volume_page import NumberVolumePage


@allure.suite("E2E_10 Разметка номеров по классам")
@allure.sub_suite("Добавление")
class TestAddNumberClass:
    @pytest.fixture(autouse=True)
    def setup(self, stand_login_lis: Page):
        self.home_page_lis = HomeLisPage(stand_login_lis)
        self.directories_page = DirectoriesPage(stand_login_lis)
        self.number_volume_page = NumberVolumePage(stand_login_lis)

    @allure.title("Добавление класса номера")
    @allure.tag("can_auth", "success")
    @allure.id(585063)
    def test_add_number_class(self, remove_number_class: str, base_url: str):
        new_class_name = remove_number_class

        with allure.step("Открыть окно 'Справочники'"):
            self.home_page_lis.locators.DIRECTORIES_BTN.wait_to_be_visible()
            self.home_page_lis.locators.DIRECTORIES_BTN.click()
            self.directories_page.locators.TITLE.wait_to_have_text("Справочники")

        with allure.step("Выбрать справочник 'Классы номеров'"):
            self.directories_page.locators.DIRECTORY_NUMBER_CLASSES.click()
            self.directories_page.check_dictionary_number_classes()

        with allure.step("На панели управления нажмите на кнопку 'Добавить элемент'"):
            self.directories_page.locators.ADD_NEW_ELEMENT_BTN.click()
            self.directories_page.locators.MODAL.wait_elements_visible(0)
            self.directories_page.check_add_dictionary_element()

        with allure.step("Ввести наименование нового элемента и нажать кнопку 'Добавить'"):
            self.directories_page.locators.NAME_INPUT.fill(new_class_name)
            self.directories_page.locators.ADD_ELEMENT_BTN.click()
            self.directories_page.locators.LOADER.not_to_be_visible()
            new_class_index = self.directories_page.locators.DIRECTORY_ELEMENTS.text_list.index(new_class_name)
            self.directories_page.locators.SECOND_COLUMN_CHECKBOXES[new_class_index].to_have_class(
                class_name=re.compile(r"n-check-checkbox_checked"))

    @allure.title("Добавление шаблона класса номера")
    @allure.tag("can_auth", "success")
    @allure.id(585066)
    def test_add_template_number_class(self, add_class_and_remove_template_and_number: (str, str), base_url: str):
        class_name, template_name = add_class_and_remove_template_and_number
        priority = "50"

        with allure.step("Открыть окно 'Номерная ёмкость'"):
            self.home_page_lis.locators.NUMBER_VOLUME_BTN.click()
            self.number_volume_page.locators.TITLE.to_contain_text("Номерная ёмкость")

        with allure.step("Перейти на вкладку 'Шаблоны классов номеров'"):
            self.number_volume_page.locators.PAGE_TABS.wait_to_have_count(2)
            self.number_volume_page.locators.PAGE_TABS[1].wait_to_have_text("Шаблоны классов номеров")
            self.number_volume_page.locators.PAGE_TABS[1].click()
            self.number_volume_page.check_table_class_number_templates()
            template_count = self.number_volume_page.locators.TEMPLATE_TABLE_LINE.elements_len()

        with allure.step("Нажать кнопку 'Добавить шаблон'"):
            self.number_volume_page.locators.ADD_TEMPLATE_BTN.click()
            self.number_volume_page.check_add_class_template_modal()

        with allure.step("Заполнить поля формы 'Добавление шаблона класса'"):
            self.number_volume_page.locators.TEMPLATE_NAME_INPUT.fill(template_name)
            self.number_volume_page.locators.CHOOSE_CLASS_BLOCK.select_by_value(class_name)
            self.number_volume_page.locators.TEMPLATE_PRIORITY_INPUT.fill(priority)
            self.number_volume_page.locators.TEMPLATE_IS_DEFAULT_CHECKBOX.click()

        with allure.step("Нажать кнопку 'Добавить'"):
            self.number_volume_page.locators.ADD_TEMPLATE_MODAL_BTN.click()
            self.number_volume_page.locators.TEMPLATE_TABLE_LINE.wait_to_have_count(template_count + 1)
            new_template_index = self.number_volume_page.locators.TEMPLATE_NAME.text_list.index(template_name)
            self.number_volume_page.locators.TEMPLATE_CLASS[new_template_index].wait_to_have_text(class_name)
            self.number_volume_page.locators.TEMPLATE_PRIORITY[new_template_index].wait_to_have_text(priority)
            self.number_volume_page.locators.TEMPLATE_IS_DEFAULT[new_template_index].wait_to_have_text("Используется")
