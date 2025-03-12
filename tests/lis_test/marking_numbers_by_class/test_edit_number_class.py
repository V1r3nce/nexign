import re

import allure
import pytest
from playwright.sync_api import Page

from pages.lis_pages.directories_page import DirectoriesPage
from pages.lis_pages.home_lis_page import HomeLisPage
from pages.lis_pages.number_volume_page import NumberVolumePage


@allure.suite("E2E_10 Разметка номеров по классам")
@allure.sub_suite("Редактирование")
class TestEditNumberClass:
    @pytest.fixture(autouse=True)
    def setup(self, stand_login_lis: Page):
        self.home_page_lis = HomeLisPage(stand_login_lis)
        self.directories_page = DirectoriesPage(stand_login_lis)
        self.number_volume_page = NumberVolumePage(stand_login_lis)

    @allure.title("Редактирование класса номера")
    @allure.tag("can_auth", "success")
    @allure.id(585153)
    def test_edit_number_class(self, add_and_remove_class: (str, str), base_url: str):
        class_name = add_and_remove_class[0]
        new_class_name = class_name + "2"

        with allure.step("Открыть окно 'Справочники'"):
            self.home_page_lis.locators.DIRECTORIES_BTN.wait_to_be_visible()
            self.home_page_lis.locators.DIRECTORIES_BTN.click()
            self.directories_page.locators.TITLE.wait_to_have_text("Справочники")

        with allure.step("Выбрать справочник 'Классы номеров'"):
            self.directories_page.locators.DIRECTORY_NUMBER_CLASSES.click()
            self.directories_page.check_dictionary_number_classes()

        with allure.step("Выбрать элемент справочника"):
            class_index = self.directories_page.locators.DIRECTORY_ELEMENTS.text_list.index(class_name)
            self.directories_page.locators.TABLE_LINE[class_index].click()

        with allure.step("На панели управления нажмите на кнопку 'Редактировать элемент'"):
            self.directories_page.locators.EDIT_ELEMENT_BTN.element_have_css_color("background", "dark_grey_lis_button")
            self.directories_page.locators.EDIT_ELEMENT_BTN.click()
            self.directories_page.check_edit_dictionary_element()

        with allure.step("Изменить наименование элемента справочника и убрать признак активности элемента справочника"):
            self.directories_page.locators.EDIT_NAME_INPUT.fill(new_class_name)
            self.directories_page.locators.EDIT_ACTIVE_CHECKBOX.click()

        with allure.step("Нажать кнопку 'Сохранить'"):
            self.directories_page.locators.SAVE_EDIT_ELEMENT_BTN.click()
            self.directories_page.locators.MODAL[0].not_to_be_visible()
            self.directories_page.locators.DIRECTORY_ELEMENTS.wait_for_text_in_all([new_class_name])
            new_class_index = self.directories_page.locators.DIRECTORY_ELEMENTS.text_list.index(new_class_name)
            self.directories_page.locators.SECOND_COLUMN_CHECKBOXES[new_class_index].not_to_have_class(
                class_name=re.compile(r"n-check-checkbox_checked"))

    @allure.title("Редактирование шаблона класса номера")
    @allure.tag("can_auth", "success")
    @allure.id(585170)
    def test_edit_template_number_class(self, add_and_remove_template: (str, str, str), base_url: str):
        template_name = add_and_remove_template[1]
        new_template_name = template_name + "2"
        new_priority = "70"

        with allure.step("Открыть окно 'Номерная ёмкость'"):
            self.home_page_lis.locators.NUMBER_VOLUME_BTN.click()
            self.number_volume_page.locators.TITLE.to_contain_text("Номерная ёмкость")

        with allure.step("Перейти на вкладку 'Шаблоны классов номеров'"):
            self.number_volume_page.locators.PAGE_TABS.wait_to_have_count(2)
            self.number_volume_page.locators.PAGE_TABS[1].wait_to_have_text("Шаблоны классов номеров")
            self.number_volume_page.locators.PAGE_TABS[1].click()
            self.number_volume_page.check_table_class_number_templates()

        with allure.step("Выбрать элемент шаблона"):
            template_index = self.number_volume_page.locators.TEMPLATE_NAME.text_list.index(template_name)
            self.number_volume_page.locators.TEMPLATE_TABLE_LINE[template_index].click()

        with allure.step("На панели управления нажмите на кнопку 'Редактировать элемент'"):
            self.number_volume_page.locators.EDIT_TEMPLATE_BTN.element_have_css_color("background", "dark_grey_lis_button")
            self.number_volume_page.locators.EDIT_TEMPLATE_BTN.click()
            self.number_volume_page.check_edit_template()

        with allure.step("Изменить наименование элемента справочника и убрать признак активности элемента справочника"):
            self.number_volume_page.locators.EDIT_TEMPLATE_NAME_INPUT.fill(new_template_name)
            self.number_volume_page.locators.EDIT_TEMPLATE_PRIORITY_INPUT.fill(new_priority)
            self.number_volume_page.locators.EDIT_TEMPLATE_IS_DEFAULT_CHECKBOX.click()

        with allure.step("Нажать кнопку 'Сохранить'"):
            self.number_volume_page.locators.EDIT_TEMPLATE_MODAL_BTN.click()
            self.number_volume_page.locators.MODAL[0].not_to_be_visible()
            self.number_volume_page.locators.TEMPLATE_NAME.wait_for_text_in_all([new_template_name])
            new_template_index = self.number_volume_page.locators.TEMPLATE_NAME.text_list.index(new_template_name)
            self.number_volume_page.locators.TEMPLATE_PRIORITY[new_template_index].wait_to_have_text(new_priority)
            self.number_volume_page.locators.TEMPLATE_IS_DEFAULT[new_template_index].not_to_have_class(
                class_name=re.compile(r"n-check-checkbox_checked"))
