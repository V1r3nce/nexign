import re

import allure
import pytest
from playwright.sync_api import Page

from pages.lis_pages.directories_page import DirectoriesPage
from pages.lis_pages.home_lis_page import HomeLisPage
from pages.lis_pages.number_volume_page import NumberVolumePage


@allure.suite("E2E_10 Разметка номеров по классам")
@allure.sub_suite("Добавление")
@pytest.mark.regress
class TestAddNumberClass:
    @pytest.fixture(autouse=True)
    def setup(self, stand_login_lis: Page) -> None:
        self.home_page_lis = HomeLisPage(stand_login_lis)
        self.directories_page = DirectoriesPage(stand_login_lis)
        self.number_volume_page = NumberVolumePage(stand_login_lis)

    @allure.title("Добавление класса номера")
    @allure.id(585063)
    def test_add_number_class(self, remove_number_class: str, base_url: str) -> None:
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
            self.directories_page.check_add_dictionary_element()

        with allure.step("Ввести наименование нового элемента и нажать кнопку 'Добавить'"):
            self.directories_page.locators.ADD_NAME_INPUT.fill(new_class_name)
            self.directories_page.locators.ADD_ELEMENT_BTN.click()
            self.directories_page.locators.MODAL[0].not_to_be_visible()
            self.directories_page.locators.DIRECTORY_ELEMENTS.wait_for_text_in_all([new_class_name])
            new_class_index = self.directories_page.locators.DIRECTORY_ELEMENTS.text_list.index(new_class_name)
            self.directories_page.locators.SECOND_COLUMN_CHECKBOXES[new_class_index].to_have_class(
                class_name=re.compile(r"n-check-checkbox_checked")
            )

    @allure.title("Добавление шаблона класса номера")
    @allure.id(585066)
    def test_add_template_number_class(self, add_class_and_remove_template: tuple[str, str], base_url: str) -> None:
        class_name, template_name = add_class_and_remove_template
        priority = "50"

        with allure.step("Открыть окно 'Номерная ёмкость'"):
            self.home_page_lis.locators.NUMBER_VOLUME_BTN.click()
            self.number_volume_page.locators.TITLE.to_contain_text("Номерная ёмкость")

        with allure.step("Перейти на вкладку 'Шаблоны классов номеров'"):
            self.number_volume_page.locators.PAGE_TABS.wait_to_have_count(2)
            self.number_volume_page.locators.PAGE_TABS[1].wait_to_have_text("Шаблоны классов номеров")
            self.number_volume_page.locators.PAGE_TABS[1].click()
            self.number_volume_page.check_table_class_number_templates()

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
            self.number_volume_page.locators.MODAL[0].not_to_be_visible()
            self.number_volume_page.locators.TEMPLATE_NAME.wait_for_text_in_all([template_name])
            new_template_index = self.number_volume_page.locators.TEMPLATE_NAME.text_list.index(template_name)
            self.number_volume_page.locators.TEMPLATE_CLASS[new_template_index].wait_to_have_text(class_name)
            self.number_volume_page.locators.TEMPLATE_PRIORITY[new_template_index].wait_to_have_text(priority)
            self.number_volume_page.locators.TEMPLATE_IS_DEFAULT[new_template_index].wait_to_have_text("Используется")

    @allure.title("Добавление условий шаблона класса номера")
    @allure.id(585081)
    def test_add_rule_template_number_class(self, add_template_and_remove_rule: tuple[str, str], base_url: str) -> None:
        template_name, rule_name = add_template_and_remove_rule
        condition = ":1 = :2"
        test_number = "9912345678"

        with allure.step("Открыть окно 'Номерная ёмкость'"):
            self.home_page_lis.locators.NUMBER_VOLUME_BTN.click()
            self.number_volume_page.locators.TITLE.to_contain_text("Номерная ёмкость")

        with allure.step("Перейти на вкладку 'Шаблоны классов номеров'"):
            self.number_volume_page.locators.PAGE_TABS.wait_to_have_count(2)
            self.number_volume_page.locators.PAGE_TABS[1].wait_to_have_text("Шаблоны классов номеров")
            self.number_volume_page.locators.PAGE_TABS[1].click()
            self.number_volume_page.check_table_class_number_templates()

        with allure.step("Выбрать добавленный шаблон класса номера"):
            template_index = self.number_volume_page.locators.TEMPLATE_NAME.text_list.index(template_name)
            self.number_volume_page.locators.TEMPLATE_NAME[template_index].click()
            self.number_volume_page.check_table_templates_rules()

        with allure.step("Нажать кнопку 'Добавить условие'"):
            self.number_volume_page.locators.ADD_RULE_BTN.element_have_css_color("background", "dark_grey_lis_button")
            self.number_volume_page.locators.ADD_RULE_BTN.click()
            self.number_volume_page.check_add_rule_modal()

        with allure.step("Заполнить поля в окне 'Добавление условия'"):
            self.number_volume_page.locators.RULE_NAME_INPUT.fill(rule_name)
            self.number_volume_page.locators.RULE_CONDITION_INPUT.fill(condition)
            self.number_volume_page.locators.RULE_TEST_NUMBER_INPUT.fill(test_number)

        with allure.step("Нажать кнопку 'Добавить'"):
            self.number_volume_page.locators.ADD_RULE_MODAL_BTN.click()
            self.number_volume_page.locators.MODAL[0].not_to_be_visible()
            self.number_volume_page.locators.RULE_NAME.wait_for_text_in_all([rule_name])
            rule_index = self.number_volume_page.locators.RULE_NAME.text_list.index(rule_name)
            self.number_volume_page.locators.RULE_CONDITION[rule_index].wait_to_have_text(condition)
            self.number_volume_page.locators.RULE_IS_ACTIVE[rule_index].wait_to_have_text("Активен")
            self.number_volume_page.locators.RULE_TEST_NUMBER[rule_index].wait_to_have_text(test_number)

    @allure.title("Проверка условий шаблона класса номера")
    @allure.id(586321)
    def test_check_rule_template_number_class(
        self, add_template_and_remove_rule: tuple[str, str], base_url: str
    ) -> None:
        template_name, rule_name = add_template_and_remove_rule
        condition = ":1 = :2"
        test_number = "9812345678"

        with allure.step("Открыть окно 'Номерная ёмкость'"):
            self.home_page_lis.locators.NUMBER_VOLUME_BTN.click()
            self.number_volume_page.locators.TITLE.to_contain_text("Номерная ёмкость")

        with allure.step("Перейти на вкладку 'Шаблоны классов номеров'"):
            self.number_volume_page.locators.PAGE_TABS.wait_to_have_count(2)
            self.number_volume_page.locators.PAGE_TABS[1].wait_to_have_text("Шаблоны классов номеров")
            self.number_volume_page.locators.PAGE_TABS[1].click()
            self.number_volume_page.check_table_class_number_templates()

        with allure.step("Выбрать добавленный шаблон класса номера"):
            template_index = self.number_volume_page.locators.TEMPLATE_NAME.text_list.index(template_name)
            self.number_volume_page.locators.TEMPLATE_NAME[template_index].click()
            self.number_volume_page.check_table_templates_rules()

        with allure.step("Нажать кнопку 'Добавить условие'"):
            self.number_volume_page.locators.ADD_RULE_BTN.element_have_css_color("background", "dark_grey_lis_button")
            self.number_volume_page.locators.ADD_RULE_BTN.click()
            self.number_volume_page.check_add_rule_modal()

        with allure.step("Заполнить поля в окне 'Добавление условия'"):
            self.number_volume_page.locators.RULE_NAME_INPUT.fill(rule_name)
            self.number_volume_page.locators.RULE_CONDITION_INPUT.fill(condition)
            self.number_volume_page.locators.RULE_TEST_NUMBER_INPUT.fill(test_number)

        with allure.step("Нажать кнопку 'Добавить'"):
            self.number_volume_page.locators.ADD_RULE_MODAL_BTN.click()
            self.number_volume_page.locators.MODAL.wait_elements_visible(0)
            self.number_volume_page.locators.MODAL_TITLE.wait_to_have_text("Добавление условия")
            self.number_volume_page.locators.RULE_TEST_NUMBER_INPUT.to_have_class(class_name=re.compile(r"ng-invalid"))
