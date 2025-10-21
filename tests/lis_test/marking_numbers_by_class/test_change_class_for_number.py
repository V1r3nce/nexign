import re

import allure
import pytest
from playwright.sync_api import Page

from common.helpers.time_helpers import delay
from pages.lis_pages.home_lis_page import HomeLisPage
from pages.lis_pages.number_volume_page import NumberVolumePage


@allure.suite("E2E_10 Разметка номеров по классам")
@pytest.mark.regress
@pytest.mark.lis
@pytest.mark.nbss_portal
class TestChangeClassForNumber:
    @pytest.fixture(autouse=True)
    def setup(self, stand_login_lis: Page) -> None:
        self.home_page_lis = HomeLisPage(stand_login_lis)
        self.home_page_lis.page.context.set_extra_http_headers({"accept-language": "ru"})
        self.number_volume_page = NumberVolumePage(stand_login_lis)

    @allure.title("Ручная смена класса номера")
    @allure.id(585922)
    def test_manual_change_class(self, base_url: str) -> None:
        with allure.step("Открыть окно 'Номерная ёмкость'"):
            self.home_page_lis.locators.NUMBER_VOLUME_BTN.click()
            self.number_volume_page.locators.TITLE.to_contain_text("Номерная ёмкость")

        with allure.step("Выбрать номер у которого статус 'Свободен' и он не заблокирован"):
            self.number_volume_page.locators.SEARCH_BTN.click()
            self.number_volume_page.locators.STATUS_FILTER_BTN.click()
            self.number_volume_page.locators.STATUS_OPTION_FREE.click()
            self.number_volume_page.locators.BLOCKING_FILTER_BTN.click()
            self.number_volume_page.locators.NOT_BLOCKED_OPTION.click()
            self.number_volume_page.locators.FILTER_SEARCH_BTN.click()
            self.number_volume_page.locators.NO_MSISDN_OR_LOADER.not_to_be_visible()
            self.number_volume_page.locators.PHONE_NUMBERS.wait_elements_visible(0)
            phone_number = self.number_volume_page.locators.PHONE_NUMBERS[0].text
            number_class = self.number_volume_page.locators.PHONE_NUMBERS_CLASS[0].text.strip()
            self.number_volume_page.locators.LINE_CHECKBOXES[0].click()

        with allure.step("Нажать на кнопку 'Изменить класс номера'"):
            self.number_volume_page.locators.CHANGE_NUM_CLASS_BTN.element_have_css_color(
                "background", "dark_grey_lis_button"
            )
            self.number_volume_page.locators.CHANGE_NUM_CLASS_BTN.click()
            self.number_volume_page.check_change_number_class()

        with allure.step("Выбрать из выпадающего списка класс номера и нажать кнопку 'Сохранить'"):
            new_number_class = "Золотой" if number_class == "Серебряный" else "Серебряный"
            self.number_volume_page.locators.CHOOSE_CLASS_FIELD.select_by_value(new_number_class)
            self.number_volume_page.locators.CONFIRM_CHANGE_CLASS_BTN.click()
            self.number_volume_page.locators.MODAL.wait_elements_visible(1)
            self.number_volume_page.locators.MODAL_TITLE[1].to_contain_text("Подтверждение операции")
            self.number_volume_page.locators.MODAL_BODY_TEXT[0].to_contain_text(
                "Количество записей: 1 "
                'Операция "Изменить класс номера" будет выполнена для выбранных записей (1). Выполнить операцию?'
            )
            self.number_volume_page.locators.MODAL_FIRST_BTN[-1].click()

        with allure.step("В параметрах поиска очистить фильтр, заполнить поле 'MSISDN' точным значением номера"):
            self.number_volume_page.locators.CLEAR_FILTER_BTN.click()
            self.number_volume_page.locators.MSISDN_FILTER_BTN.click()
            self.number_volume_page.locators.MSISDN_OPTION_VALUE.click()
            self.number_volume_page.locators.MSISDN_FILTER_INPUT.fill(phone_number)

        with allure.step("Нажать кнопку 'Найти'"):
            self.number_volume_page.locators.FILTER_SEARCH_BTN.click()
            self.number_volume_page.locators.NO_MSISDN_OR_LOADER.not_to_be_visible()
            self.number_volume_page.locators.PHONE_NUMBERS.wait_elements_visible(0)
            self.number_volume_page.locators.PHONE_NUMBERS[0].wait_to_have_text(phone_number)
            self.number_volume_page.locators.PHONE_NUMBERS_CLASS[0].wait_to_have_text(new_number_class)

    @allure.title("Смена класса номера автоматически по шаблону классов номеров")
    @allure.id(587189)
    def test_change_class_using_template(self, base_url: str) -> None:
        with allure.step("Открыть окно 'Номерная ёмкость'"):
            self.home_page_lis.locators.NUMBER_VOLUME_BTN.click()
            self.number_volume_page.locators.TITLE.to_contain_text("Номерная ёмкость")

        with allure.step("Выбрать номер у которого статус 'Свободен', класс 'Платиновый' и он не заблокирован"):
            self.number_volume_page.locators.SEARCH_BTN.click()
            self.number_volume_page.locators.STATUS_FILTER_BTN.click()
            self.number_volume_page.locators.STATUS_OPTION_FREE.click()
            self.number_volume_page.locators.CLASS_FILTER_BTN.click()
            self.number_volume_page.locators.CLASS_FILTER_OPTIONS[3].click()
            self.number_volume_page.locators.CLASS_FILTER_BTN.click()
            self.number_volume_page.locators.BLOCKING_FILTER_BTN.click()
            self.number_volume_page.locators.NOT_BLOCKED_OPTION.click()
            self.number_volume_page.locators.FILTER_SEARCH_BTN.click()
            self.number_volume_page.locators.NO_MSISDN_OR_LOADER.not_to_be_visible()
            self.number_volume_page.locators.PHONE_NUMBERS.wait_elements_visible(0)
            phone_number = self.number_volume_page.locators.PHONE_NUMBERS[0].text
            self.number_volume_page.locators.LINE_CHECKBOXES[0].click()

        with allure.step("Нажать на кнопку 'Редактировать атрибуты номеров'"):
            self.number_volume_page.locators.GROUP_EDIT_BTN.element_have_css_color("background", "dark_grey_lis_button")
            self.number_volume_page.locators.GROUP_EDIT_BTN.click()
            self.number_volume_page.locators.GROUP_EDIT_NUM_ATTRIBUTE_BTN.click()
            self.number_volume_page.check_edit_number_attributes_elements()

        with allure.step("Выбрать из списка 'Разметка классов' только класс 'Серебряный' и нажать кнопку 'Сохранить'"):
            self.number_volume_page.locators.NUMBER_TYPE_ALL_CHECKBOX.click()
            delay(0.5, reason="Время на отключение чекбокса")
            self.number_volume_page.check_all_checkboxes_turned_off()
            class_index = self.number_volume_page.locators.NUMBER_TYPE_CLASSES.text_list.index("Серебряный")
            self.number_volume_page.locators.NUMBER_TYPE_CHECKBOXES[class_index].click()
            self.number_volume_page.locators.NUMBER_TYPE_LINE[class_index].to_have_class(
                class_name=re.compile(r"js-selected")
            )
            self.number_volume_page.locators.MASS_SAVE_BUTTON.click()

        with allure.step("Нажать кнопку 'Да'"):
            self.number_volume_page.locators.MODAL.wait_elements_visible(1)
            self.number_volume_page.locators.MODAL_TITLE[1].to_contain_text("Подтверждение операции")
            self.number_volume_page.locators.MODAL_BODY_TEXT[0].to_contain_text(
                "Количество записей: 1 "
                'Операция "Редактирование номера" будет выполнена для выбранных записей (1). Выполнить операцию?'
            )
            self.number_volume_page.locators.MODAL_FIRST_BTN[-1].click()
            self.number_volume_page.locators.PHONE_NUMBERS[0].not_to_contain_text(phone_number)

        with allure.step("В параметрах поиска очистить фильтр, заполнить поле 'MSISDN' точным значением номера"):
            self.number_volume_page.locators.CLEAR_FILTER_BTN.click()
            self.number_volume_page.locators.MSISDN_FILTER_BTN.click()
            self.number_volume_page.locators.MSISDN_OPTION_VALUE.click()
            self.number_volume_page.locators.MSISDN_FILTER_INPUT.fill(phone_number)

        with allure.step("Нажать кнопку 'Найти'"):
            self.number_volume_page.locators.FILTER_SEARCH_BTN.click()
            self.number_volume_page.locators.NO_MSISDN_OR_LOADER.not_to_be_visible()
            self.number_volume_page.locators.PHONE_NUMBERS.wait_elements_visible(0)
            self.number_volume_page.locators.PHONE_NUMBERS[0].wait_to_have_text(phone_number)
            self.number_volume_page.locators.PHONE_NUMBERS_CLASS[0].wait_to_have_text("Обычный")

    @allure.title("Ручная смена класса заблокированного номера")
    @allure.id(587325)
    def test_manual_change_class_blocked_number(self, lock_phone_number: None, base_url: str) -> None:
        with allure.step("Открыть окно 'Номерная ёмкость'"):
            self.home_page_lis.locators.NUMBER_VOLUME_BTN.click()
            self.number_volume_page.locators.TITLE.to_contain_text("Номерная ёмкость")

        with allure.step("Выбрать номер у которого установлена блокировка"):
            self.number_volume_page.locators.SEARCH_BTN.click()
            self.number_volume_page.locators.BLOCKING_FILTER_BTN.click()
            self.number_volume_page.locators.BLOCKED_OPTION.click()
            self.number_volume_page.locators.FILTER_SEARCH_BTN.click()
            self.number_volume_page.locators.NO_MSISDN_OR_LOADER.not_to_be_visible()
            self.number_volume_page.locators.PHONE_NUMBERS.wait_elements_visible(0)
            self.number_volume_page.locators.LINE_CHECKBOXES[0].click()

        with allure.step("Нажать на кнопку 'Изменить класс номера'"):
            self.number_volume_page.locators.CHANGE_NUM_CLASS_BTN.element_have_css_color(
                "background", "dark_grey_lis_button"
            )
            self.number_volume_page.locators.CHANGE_NUM_CLASS_BTN.click()
            self.number_volume_page.check_change_number_class()

        with allure.step("Выбрать из выпадающего списка класс номера и нажать кнопку 'Сохранить'"):
            self.number_volume_page.locators.CHOOSE_CLASS_FIELD.select_by_value("Золотой")
            self.number_volume_page.locators.CONFIRM_CHANGE_CLASS_BTN.click()
            self.number_volume_page.locators.MODAL.wait_elements_visible(1)
            self.number_volume_page.locators.MODAL_TITLE[1].to_contain_text("Подтверждение операции")
            self.number_volume_page.locators.MODAL_BODY_TEXT[0].to_contain_text(
                "Количество записей: 1 "
                'Операция "Изменить класс номера" будет выполнена для выбранных записей (1). Выполнить операцию?'
            )

        with allure.step("Нажать кнопку 'Да'"):
            self.number_volume_page.locators.MODAL_FIRST_BTN[-1].click()
            self.number_volume_page.locators.MODAL.wait_elements_visible(1)
            self.number_volume_page.locators.MODAL_TITLE[1].to_contain_text("Информация")
            self.number_volume_page.locators.MODAL_BODY_TEXT[0].to_contain_text(
                "Операция прервана. Не обработано 1 элементов."
            )
            self.number_volume_page.locators.MODAL_BODY_TEXT[0].to_contain_text(
                "- Ресурс (телефонный номер) заблокирован другой операцией"
            )

    @allure.title("Смена класса занятого номера")
    @allure.id(587332)
    def test_change_class_busy_number(self, base_url: str) -> None:
        with allure.step("Открыть окно 'Номерная ёмкость'"):
            self.home_page_lis.locators.NUMBER_VOLUME_BTN.click()
            self.number_volume_page.locators.TITLE.to_contain_text("Номерная ёмкость")

        with allure.step("Выбрать номер в списке номеров, у которого статус 'Занят'"):
            self.number_volume_page.locators.SEARCH_BTN.click()
            self.number_volume_page.locators.STATUS_FILTER_BTN.click()
            self.number_volume_page.locators.STATUS_OPTION_BUSY.click()
            self.number_volume_page.locators.FILTER_SEARCH_BTN.click()
            self.number_volume_page.locators.NO_MSISDN_OR_LOADER.not_to_be_visible()
            self.number_volume_page.locators.PHONE_NUMBERS.wait_elements_visible(0)
            self.number_volume_page.locators.LINE_CHECKBOXES[0].click()

        with allure.step("Кнопки 'Изменить класс номера' и 'Редактировать атрибуты номеров' недоступны"):
            self.number_volume_page.locators.CHANGE_NUM_CLASS_BTN.check_attribute_by_value("disabled", "disabled")
            self.number_volume_page.locators.GROUP_EDIT_BTN.check_attribute_by_value("disabled", "disabled")

    @allure.title("Смена класса заблокированного номера автоматически по шаблону классов номеров")
    @allure.tag("can_auth", "success")
    @allure.id(587336)
    @pytest.mark.regress
    def test_change_class_blocked_number_using_template(self, lock_phone_number: None, base_url: str) -> None:
        with allure.step("Открыть окно 'Номерная ёмкость'"):
            self.home_page_lis.locators.NUMBER_VOLUME_BTN.click()
            self.number_volume_page.locators.TITLE.to_contain_text("Номерная ёмкость")

        with allure.step("Выбрать номер у которого установлена блокировка"):
            self.number_volume_page.locators.SEARCH_BTN.click()
            self.number_volume_page.locators.BLOCKING_FILTER_BTN.click()
            self.number_volume_page.locators.BLOCKED_OPTION.click()
            self.number_volume_page.locators.FILTER_SEARCH_BTN.click()
            self.number_volume_page.locators.NO_MSISDN_OR_LOADER.not_to_be_visible()
            self.number_volume_page.locators.PHONE_NUMBERS.wait_elements_visible(0)
            self.number_volume_page.locators.LINE_CHECKBOXES[0].click()

        with allure.step("Нажать на кнопку 'Редактировать атрибуты номеров'"):
            self.number_volume_page.locators.GROUP_EDIT_BTN.element_have_css_color("background", "dark_grey_lis_button")
            self.number_volume_page.locators.GROUP_EDIT_BTN.click()
            self.number_volume_page.locators.GROUP_EDIT_NUM_ATTRIBUTE_BTN.click()
            self.number_volume_page.check_edit_number_attributes_elements()

        with allure.step("Выбрать из списка 'Разметка классов' только класс 'Серебряный'"):
            self.number_volume_page.locators.NUMBER_TYPE_ALL_CHECKBOX.click()
            delay(0.5, reason="Время на отключение чекбокса")
            self.number_volume_page.check_all_checkboxes_turned_off()
            class_index = self.number_volume_page.locators.NUMBER_TYPE_CLASSES.text_list.index("Серебряный")
            self.number_volume_page.locators.NUMBER_TYPE_CHECKBOXES[class_index].click()
            self.number_volume_page.locators.NUMBER_TYPE_LINE[class_index].to_have_class(
                class_name=re.compile(r"js-selected")
            )

        with allure.step("Нажать кнопку 'Сохранить'"):
            self.number_volume_page.locators.MASS_SAVE_BUTTON.click()
            self.number_volume_page.locators.MODAL.wait_elements_visible(1)
            self.number_volume_page.locators.MODAL_TITLE[1].to_contain_text("Подтверждение операции")
            self.number_volume_page.locators.MODAL_BODY_TEXT[0].to_contain_text(
                "Количество записей: 1 "
                'Операция "Редактирование номера" будет выполнена для выбранных записей (1). Выполнить операцию?'
            )

        with allure.step("Нажать кнопку 'Да' в окне подтверждения операции"):
            self.number_volume_page.locators.MODAL_FIRST_BTN[-1].click()
            self.number_volume_page.locators.MODAL.wait_elements_visible(1)
            self.number_volume_page.locators.MODAL_TITLE[1].to_contain_text("Информация")
            self.number_volume_page.locators.MODAL_BODY_TEXT[0].to_contain_text(
                "Операция прервана. Не обработано 1 элементов."
            )
            self.number_volume_page.locators.MODAL_BODY_TEXT[0].to_contain_text(
                "- Ресурс (телефонный номер) заблокирован другой операцией"
            )
