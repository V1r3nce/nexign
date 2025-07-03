import allure
import pytest
from playwright.sync_api import Page

from pages.lis_pages.directories_page import DirectoriesPage
from pages.lis_pages.home_lis_page import HomeLisPage
from pages.lis_pages.number_volume_page import NumberVolumePage


@allure.suite("E2E_10 Разметка номеров по классам")
@allure.sub_suite("Удаление")
@pytest.mark.regress
class TestDeleteNumberClass:
    @pytest.fixture(autouse=True)
    def setup(self, stand_login_lis: Page) -> None:
        self.home_page_lis = HomeLisPage(stand_login_lis)
        self.home_page_lis.page.context.set_extra_http_headers({"accept-language": "ru"})
        self.directories_page = DirectoriesPage(stand_login_lis)
        self.number_volume_page = NumberVolumePage(stand_login_lis)

    @allure.title("Удаление класса номера")
    @allure.id(585176)
    def test_delete_number_class(self, add_and_remove_class: tuple[str, str], base_url: str) -> None:
        class_name = add_and_remove_class[0]

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

        with allure.step("На панели управления нажмите на кнопку 'Удалить элемент'"):
            self.directories_page.locators.DELETE_ELEMENT_BTN.element_have_css_color(
                "background", "dark_grey_lis_button"
            )
            self.directories_page.locators.DELETE_ELEMENT_BTN.click()
            self.directories_page.locators.MODAL.wait_elements_visible(0)
            self.directories_page.locators.MODAL_TITLE[0].to_contain_text("Подтверждение операции")
            self.directories_page.locators.MODAL_BODY_TEXT[0].to_contain_text(
                "Количество записей: 1 "
                'Операция "Удаление элемента справочника" будет выполнена для выбранных записей (1). '
                "Выполнить операцию?"
            )

        with allure.step("Нажать кнопку 'Да' в окне подтверждения операции"):
            self.directories_page.locators.MODAL_FIRST_BTN[-1].click()
            self.directories_page.locators.DIRECTORY_ELEMENTS.wait_for_not_contain_text_in_all([class_name])

    @allure.title("Удаление шаблона класса номера")
    @allure.id(585184)
    def test_delete_template_number_class(self, add_and_remove_template: tuple[str, str, str], base_url: str) -> None:
        template_name = add_and_remove_template[1]

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

        with allure.step("На панели управления нажмите на кнопку 'Удалить элемент'"):
            self.number_volume_page.locators.DELETE_TEMPLATE_BTN.element_have_css_color(
                "background", "dark_grey_lis_button"
            )
            self.number_volume_page.locators.DELETE_TEMPLATE_BTN.click()
            self.number_volume_page.locators.MODAL.wait_elements_visible(0)
            self.number_volume_page.locators.MODAL_TITLE[0].to_contain_text("Подтверждение операции")
            self.number_volume_page.locators.MODAL_BODY_TEXT[0].to_contain_text(
                "Количество записей: 1 "
                'Операция "Удалить шаблон" будет выполнена для выбранных записей (1). Выполнить операцию?'
            )

        with allure.step("Нажать кнопку 'Да' в окне подтверждения операции"):
            self.number_volume_page.locators.MODAL_FIRST_BTN[-1].click()
            self.number_volume_page.locators.TEMPLATE_NAME.wait_for_not_contain_text_in_all([template_name])

    @allure.title("Удаление условия шаблона класса номера")
    @allure.id(586318)
    def test_delete_rule_template_number_class(self, add_and_remove_rule: tuple[str, str, str], base_url: str) -> None:
        _, template_name, rule_name = add_and_remove_rule

        with allure.step("Открыть окно 'Номерная ёмкость'"):
            self.home_page_lis.locators.NUMBER_VOLUME_BTN.click()
            self.number_volume_page.locators.TITLE.to_contain_text("Номерная ёмкость")

        with allure.step("Перейти на вкладку 'Шаблоны классов номеров'"):
            self.number_volume_page.locators.PAGE_TABS.wait_to_have_count(2)
            self.number_volume_page.locators.PAGE_TABS[1].wait_to_have_text("Шаблоны классов номеров")
            self.number_volume_page.locators.PAGE_TABS[1].click()
            self.number_volume_page.check_table_class_number_templates()

        with allure.step("Выбрать элемент шаблона, в нижней части рабочей области выбрать условие шаблона"):
            template_index = self.number_volume_page.locators.TEMPLATE_NAME.text_list.index(template_name)
            self.number_volume_page.locators.TEMPLATE_NAME[template_index].click()
            self.number_volume_page.check_table_templates_rules()
            self.number_volume_page.locators.RULE_TABLE_LINE.wait_elements_visible(0)
            rule_index = self.number_volume_page.locators.RULE_NAME.text_list.index(rule_name)
            self.number_volume_page.locators.RULE_TABLE_LINE[rule_index].click()

        with allure.step("Нажать кнопку 'Удалить условие'"):
            self.number_volume_page.locators.DELETE_RULE_BTN.element_have_css_color("background", "dark_grey_lis_button")
            self.number_volume_page.locators.DELETE_RULE_BTN.click()
            self.number_volume_page.locators.MODAL.wait_elements_visible(0)
            self.number_volume_page.locators.MODAL_TITLE[0].to_contain_text("Подтверждение операции")
            self.number_volume_page.locators.MODAL_BODY_TEXT[0].to_contain_text(
                "Количество записей: 1 "
                'Операция "Удалить условие" будет выполнена для выбранных записей (1). Выполнить операцию?'
            )

        with allure.step("Нажать кнопку 'Да' в окне подтверждения операции"):
            self.number_volume_page.locators.MODAL_FIRST_BTN[-1].click()
            self.number_volume_page.locators.RULE_NAME.wait_for_not_contain_text_in_all([rule_name])

    @allure.title("Удаление шаблона класса номера с условиями")
    @allure.id(587182)
    def test_delete_template_number_class_with_rule(
        self, add_and_remove_rule: tuple[str, str, str], base_url: str
    ) -> None:
        _, template_name, rule_name = add_and_remove_rule

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
            self.number_volume_page.locators.RULE_NAME.wait_for_text_in_all(rule_name)

        with allure.step("На панели управления нажмите на кнопку 'Удалить элемент'"):
            self.number_volume_page.locators.DELETE_TEMPLATE_BTN.element_have_css_color(
                "background", "dark_grey_lis_button"
            )
            self.number_volume_page.locators.DELETE_TEMPLATE_BTN.click()
            self.number_volume_page.locators.MODAL.wait_elements_visible(0)
            self.number_volume_page.locators.MODAL_TITLE[0].to_contain_text("Подтверждение операции")
            self.number_volume_page.locators.MODAL_BODY_TEXT[0].to_contain_text(
                "Количество записей: 1 "
                'Операция "Удалить шаблон" будет выполнена для выбранных записей (1). Выполнить операцию?'
            )

        with allure.step("Нажать кнопку 'Да' в окне подтверждения операции"):
            self.number_volume_page.locators.MODAL_FIRST_BTN[-1].click()
            self.number_volume_page.locators.MODAL.wait_elements_visible(0)
            self.number_volume_page.locators.MODAL_TITLE[0].to_contain_text("Ошибка")
            self.number_volume_page.locators.MODAL_BODY_TEXT[0].to_contain_text(
                "Удалить шаблон невозможно из-за того, что у него не удалены условия"
            )

        with allure.step("Нажать кнопку 'ОК' в окне подтверждения операции"):
            self.number_volume_page.locators.MODAL_FIRST_BTN[-1].click()
            self.number_volume_page.locators.TEMPLATE_NAME.wait_for_text_in_all([template_name])
            self.number_volume_page.locators.RULE_NAME.wait_for_text_in_all([rule_name])

    @allure.title("Удаление класса номера, для которого создан шаблон")
    @allure.id(587234)
    def test_delete_number_class_with_template(
        self, add_and_remove_template: tuple[str, str, str], base_url: str
    ) -> None:
        class_name = add_and_remove_template[0]

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

        with allure.step("На панели управления нажмите на кнопку 'Удалить элемент'"):
            self.directories_page.locators.DELETE_ELEMENT_BTN.element_have_css_color(
                "background", "dark_grey_lis_button"
            )
            self.directories_page.locators.DELETE_ELEMENT_BTN.click()
            self.directories_page.locators.MODAL.wait_elements_visible(0)
            self.directories_page.locators.MODAL_TITLE[0].to_contain_text("Подтверждение операции")
            self.directories_page.locators.MODAL_BODY_TEXT[0].to_contain_text(
                "Количество записей: 1 "
                'Операция "Удаление элемента справочника" будет выполнена для выбранных записей (1). '
                "Выполнить операцию?"
            )

        with allure.step("Нажать кнопку 'Да' в окне подтверждения операции"):
            self.directories_page.locators.MODAL_FIRST_BTN[-1].click()
            self.directories_page.locators.MODAL.wait_elements_visible(0)
            self.directories_page.locators.MODAL_TITLE[0].to_contain_text("Информация")
            self.directories_page.locators.MODAL_BODY_TEXT[0].to_contain_text(
                "Удалить элемент справочника невозможно из-за того, что на него ссылаются записи в других объектах"
            )
