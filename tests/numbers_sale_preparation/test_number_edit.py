import re
import pytest
import allure
from playwright.sync_api import Page, APIRequestContext
from api.requests.lis_requests.phone_numbers import PhoneNumbersRequests
from common.helpers.data_generator import generate_russian_string
from common.helpers.env_helper import BASE_URL_LIS
from common.helpers.time_helpers import delay
from pages.base_page import BasePage
from pages.lis_pages.number_volume_page import NumberVolumePage
from pages.locators.lis_locators.home_elements_lis import HomeElementsLis


@allure.epic("E2E_11 Подготовка номеров к продаже")
@allure.suite("E2E_11 Подготовка номеров к продаже")
class TestSaleNumbersEdit:
    @pytest.fixture(autouse=True)
    def setup(self, stand_login_lis: Page):
        self.base_page = BasePage(stand_login_lis)
        self.home_page_lis = HomeElementsLis(stand_login_lis)
        self.number_volume_page = NumberVolumePage(stand_login_lis)
        self.random_str = generate_russian_string(11)

    @allure.title("Связка номеров DEF и ABC")
    @allure.id(581496)
    @allure.tag("can_auth", "success")
    def test_link_numbers_def_and_abc(self, api_request_auth_context: APIRequestContext):
        phone_numbers = PhoneNumbersRequests(api_request_auth_context)
        phones_def = phone_numbers.get_phone_numbers(BASE_URL_LIS, status_id=[1], state_id=[2], num_sort="MSISDN",
                                                     is_reserved="false")
        phones_abc = phone_numbers.get_phone_numbers(BASE_URL_LIS, type_def=False, status_id=[1], state_id=[2],
                                                     num_sort="MSISDN", is_reserved="false")
        def_data = phone_numbers.get_numbers_data(phones_def)
        abc_data = phone_numbers.get_numbers_data_without_phone_number_abc(phones_abc)
        phone_numbers.update_phone_numbers(BASE_URL_LIS, [def_data[0].phone_number_id,
                                                          def_data[1].phone_number_id], 1)
        phone_numbers.update_phone_numbers(BASE_URL_LIS, [abc_data[0].phone_number_id,
                                                          abc_data[1].phone_number_id], 1, 2)
        self.home_page_lis.NUMBER_VOLUME_BTN.wait_to_be_visible()
        self.home_page_lis.NUMBER_VOLUME_BTN.click()
        self.number_volume_page.locators.TITLE.to_contain_text("Номерная ёмкость")
        self.number_volume_page.locators.ZONE_TYPE[0].to_have_css("background", re.compile(r'rgb\(69, 166, 0\)'))

        self.number_volume_page.locators.SEARCH_BTN.click()
        self.number_volume_page.locators.STATUS_FILTER_BTN.click()
        self.number_volume_page.locators.STATUS_OPTION_FREE.click()
        self.number_volume_page.locators.STATE_FILTER_BTN.click()
        self.number_volume_page.locators.STATE_FILTER_OPTIONS.wait_to_be_visible()
        self.number_volume_page.locators.STATE_FILTER_OPTIONS.wait_to_have_count(11)
        self.number_volume_page.locators.STATE_FILTER_OPTIONS[8].click()
        self.number_volume_page.locators.STATE_FILTER_BTN.click()
        self.number_volume_page.locators.BLOCKING_FILTER_BTN.click()
        self.number_volume_page.locators.NOT_BLOCKED_OPTION.click()
        self.number_volume_page.locators.FILTER_SEARCH_BTN.click()
        self.number_volume_page.locators.MSISDN_HEADER.click()
        delay(1, "Время на прямую сортировку списка")
        self.number_volume_page.locators.PHONE_NUMBERS[0].wait_to_have_text(def_data[0].MSISDN)

        self.number_volume_page.locators.LINE_CHECKBOXES[0].click()
        self.number_volume_page.locators.LINE_CHECKBOXES[1].click()
        self.number_volume_page.locators.LINK_DEF_TO_ABC_BTN.click()
        self.number_volume_page.locators.MODAL_TITLE[0].wait_to_have_text("Связывание номеров")
        self.number_volume_page.locators.TEMPLATE_INPUT.to_have_value("")
        self.number_volume_page.locators.ABC_START_INPUT.fill(abc_data[0].MSISDN)
        self.number_volume_page.locators.ABC_END_INPUT.fill(abc_data[1].MSISDN)
        self.number_volume_page.locators.DEF_START_INPUT.fill(def_data[0].MSISDN)
        self.number_volume_page.locators.DEF_END_INPUT.fill(def_data[1].MSISDN)
        self.number_volume_page.locators.FIRST_BTN[0].to_contain_text("Связать")
        self.number_volume_page.locators.SECOND_BTN[0].to_contain_text("Отменить")
        self.number_volume_page.locators.FIRST_BTN[0].click()
        self.number_volume_page.locators.MODAL_TITLE.wait_elements_visible(1)
        self.number_volume_page.locators.OK_BTN.click()

        self.number_volume_page.locators.CLEAR_FILTER_BTN.click()
        self.number_volume_page.locators.STATE_FILTER_BTN.click()
        self.number_volume_page.locators.STATE_FILTER_OPTIONS.wait_to_be_visible()
        self.number_volume_page.locators.STATE_FILTER_OPTIONS.wait_to_have_count(11)
        self.number_volume_page.locators.STATE_FILTER_OPTIONS[10].click()
        self.number_volume_page.locators.FILTER_SEARCH_BTN.click()
        delay(1, reason="Время на обновление списка")
        linked_phone_numbers = [item.text for item in self.number_volume_page.locators.PHONE_NUMBERS]
        assert (f"\n  {def_data[0].MSISDN}\n" in linked_phone_numbers and f"\n  {def_data[1].MSISDN}\n"
                in linked_phone_numbers), "Номера не появились в связанных с городским"
        (self.number_volume_page.locators.PHONE_NUMBERS_STATE[linked_phone_numbers.index(f"\n  {def_data[0].MSISDN}\n")]
         .wait_to_have_text("Связан с городским"))
        (self.number_volume_page.locators.PHONE_NUMBERS_STATE[linked_phone_numbers.index(f"\n  {def_data[1].MSISDN}\n")]
         .wait_to_have_text("Связан с городским"))
        (self.number_volume_page.locators.PHONE_NUMBERS_CLASS[linked_phone_numbers.index(f"\n  {def_data[0].MSISDN}\n")]
         .wait_to_have_text(abc_data[0].class_name))
        (self.number_volume_page.locators.PHONE_NUMBERS_CLASS[linked_phone_numbers.index(f"\n  {def_data[1].MSISDN}\n")]
         .wait_to_have_text(abc_data[1].class_name))

    @allure.title("Редактирование атрибутов номера (Несколько номеров)")
    @allure.id(580673)
    @allure.tag("can_auth", "success")
    def test_edit_numbers_attribute(self):
        self.home_page_lis.NUMBER_VOLUME_BTN.wait_to_be_visible()
        self.home_page_lis.NUMBER_VOLUME_BTN.click()
        self.number_volume_page.locators.TITLE.to_contain_text("Номерная ёмкость")
        self.number_volume_page.locators.REFRESH_BTN.click()

        self.number_volume_page.locators.SEARCH_BTN.click()
        self.number_volume_page.locators.STATE_FILTER_BTN.click()
        self.number_volume_page.locators.STATE_FILTER_OPTIONS.wait_to_be_visible()
        self.number_volume_page.locators.STATE_FILTER_OPTIONS.wait_to_have_count(11)
        self.number_volume_page.locators.STATE_FILTER_OPTIONS[8].click()
        self.number_volume_page.locators.STATE_FILTER_BTN.click()
        self.number_volume_page.locators.BLOCKING_FILTER_BTN.click()
        self.number_volume_page.locators.NOT_BLOCKED_OPTION.click()
        self.number_volume_page.locators.FILTER_SEARCH_BTN.click()
        self.number_volume_page.locators.MSISDN_HEADER.click()
        delay(1, "Время на обратную сортировку списка")
        self.number_volume_page.locators.PHONE_NUMBERS_STATE[0].wait_to_have_text("Открыт для исп.")
        self.number_volume_page.locators.PHONE_NUMBERS_STATE[1].wait_to_have_text("Открыт для исп.")

        self.number_volume_page.locators.LINE_CHECKBOXES.click(0)
        self.number_volume_page.locators.LINE_CHECKBOXES.click(1)
        delay(.3, reason="Кнопка не активна доли секунды, даже в случае enabled")
        self.number_volume_page.locators.GROUP_EDIT_BTN.click()
        self.number_volume_page.locators.GROUP_EDIT_NUM_ATTRIBUTE_BTN.click()
        self.number_volume_page.locators.MODAL_TITLE.wait_to_have_text("Редактирование атрибутов номеров зоны DEF")
        self.number_volume_page.check_edit_numbers_elements()
        self.number_volume_page.locators.MASS_SAVE_BUTTON.to_contain_text("Сохранить")
        self.number_volume_page.locators.CANCEL_BUTTON.to_contain_text("Отменить")
        self.number_volume_page.locators.COMMENT_FIELD.fill(self.random_str)
        self.number_volume_page.locators.NUMBER_TYPE_ALL_CHECKBOX.click()
        delay(0.5, reason="Время на отключение чекбокса")
        self.number_volume_page.check_all_checkboxes_turned_off()
        self.number_volume_page.locators.MASS_SAVE_BUTTON.click()

        self.number_volume_page.locators.MODAL.wait_elements_visible(1)
        self.number_volume_page.locators.MODAL_TITLE[1].to_contain_text("Подтверждение операции")
        (self.number_volume_page.locators.MODAL_BODY_TEXT.
         to_contain_text(' Операция "Редактирование номера" будет выполнена для выбранных записей (2). Выполнить операцию?'))
        self.number_volume_page.locators.FIRST_BTN[-1].click()
        self.number_volume_page.locators.COMMENTS[0].wait_to_have_text(self.random_str)
        self.number_volume_page.locators.COMMENTS[1].wait_to_have_text(self.random_str)

    @allure.title("Редактирование атрибутов номера (Один номер)")
    @allure.id(580676)
    @allure.tag("can_auth", "success")
    def test_edit_number_attribute(self):
        self.home_page_lis.NUMBER_VOLUME_BTN.wait_to_be_visible()
        self.home_page_lis.NUMBER_VOLUME_BTN.click()
        self.number_volume_page.locators.TITLE.to_contain_text("Номерная ёмкость")
        self.number_volume_page.locators.REFRESH_BTN.click()

        self.number_volume_page.locators.SEARCH_BTN.click()
        self.number_volume_page.locators.STATE_FILTER_BTN.click()
        self.number_volume_page.locators.STATE_FILTER_OPTIONS.wait_to_be_visible()
        self.number_volume_page.locators.STATE_FILTER_OPTIONS.wait_to_have_count(11)
        self.number_volume_page.locators.STATE_FILTER_OPTIONS[8].click()
        self.number_volume_page.locators.FILTER_SEARCH_BTN.click()
        self.number_volume_page.locators.MSISDN_HEADER.click()
        delay(1, "Время на обратную сортировку списка")
        self.number_volume_page.locators.PHONE_NUMBERS_STATE[0].wait_to_have_text("Открыт для исп.")

        self.number_volume_page.locators.LINE_CHECKBOXES.click(0)
        delay(.3, reason="Кнопка не активна доли секунды, даже в случае enabled")
        self.number_volume_page.locators.EDIT_NUM_BTN.click()
        self.number_volume_page.locators.MODAL_TITLE.wait_to_have_text("Редактирование номера зоны DEF")
        self.number_volume_page.check_edit_one_number_elements()
        self.number_volume_page.locators.SAVE_BUTTON.to_contain_text("Сохранить")
        self.number_volume_page.locators.CANCEL_BUTTON.to_contain_text("Отменить")
        self.number_volume_page.locators.COMMENT_FIELD.fill(self.random_str)
        self.number_volume_page.locators.SAVE_BUTTON.click()

        self.number_volume_page.locators.COMMENTS[0].wait_to_have_text(self.random_str)

    @allure.title("Редактирование атрибутов номера (Один номер, Занятый номер)")
    @allure.id(580678)
    @allure.tag("can_auth", "success")
    def test_edit_busy_number_attribute(self):
        self.home_page_lis.NUMBER_VOLUME_BTN.wait_to_be_visible()
        self.home_page_lis.NUMBER_VOLUME_BTN.click()
        self.number_volume_page.locators.TITLE.to_contain_text("Номерная ёмкость")
        self.number_volume_page.locators.REFRESH_BTN.click()

        self.number_volume_page.locators.SEARCH_BTN.click()
        self.number_volume_page.locators.STATE_FILTER_BTN.click()
        self.number_volume_page.locators.STATE_FILTER_OPTIONS.wait_to_be_visible()
        self.number_volume_page.locators.STATE_FILTER_OPTIONS.wait_to_have_count(11)
        self.number_volume_page.locators.STATE_FILTER_OPTIONS[9].click()
        self.number_volume_page.locators.FILTER_SEARCH_BTN.click()
        self.number_volume_page.locators.MSISDN_HEADER.click()
        delay(1, "Время на обратную сортировку списка")
        self.number_volume_page.locators.PHONE_NUMBERS_STATE[0].wait_to_have_text("Распределён")

        self.number_volume_page.locators.LINE_CHECKBOXES.click(0)
        delay(.3, reason="Кнопка не активна доли секунды, даже в случае enabled")
        self.number_volume_page.locators.GROUP_EDIT_BTN.click()
        self.number_volume_page.locators.GROUP_EDIT_BUSY_NUM_ATTRIBUTE_BTN.click()
        self.number_volume_page.locators.MODAL_TITLE.wait_to_have_text("Редактирование атрибутов номеров зоны DEF")

        self.number_volume_page.locators.CHOSEN_STATUS_FIELD.not_to_be_visible()
        self.number_volume_page.locators.CHOSEN_CATEGORY_BLOCK.not_to_be_visible()
        self.number_volume_page.locators.NUMBER_TYPE_BLOCK.not_to_be_visible()
        self.number_volume_page.locators.CHOOSE_COMMUTATOR_BLOCK.not_to_be_visible()
        self.number_volume_page.locators.OPERATOR_FIELD_BLOCK.not_to_be_visible()
        self.number_volume_page.locators.USE_GOAL_FIELD.wait_to_be_visible()
        self.number_volume_page.locators.COMMENT_FIELD.wait_to_be_visible()
        self.number_volume_page.locators.NUMBER_TYPE_CHECKBOXES.wait_not_to_be_visible()
        self.number_volume_page.locators.MASS_SAVE_BUTTON.to_contain_text("Сохранить")
        self.number_volume_page.locators.CANCEL_BUTTON.to_contain_text("Отменить")
        self.number_volume_page.locators.COMMENT_FIELD.fill(self.random_str)
        self.number_volume_page.locators.MASS_SAVE_BUTTON.click()

        self.number_volume_page.locators.MODAL.wait_elements_visible(1)
        self.number_volume_page.locators.MODAL_TITLE[1].to_contain_text("Подтверждение операции")
        (self.number_volume_page.locators.MODAL_BODY_TEXT.
         to_contain_text(' Операция "Редактирование номера" будет выполнена для выбранных записей (1). Выполнить операцию?'))
        self.number_volume_page.locators.FIRST_BTN[-1].click()

        self.number_volume_page.locators.COMMENTS[0].wait_to_have_text(self.random_str)

    @allure.title("Связка номеров DEF и ABC (Разные цели использования)")
    @allure.id(582581)
    @allure.tag("can_auth", "success")
    def test_link_numbers_def_and_abc_different_goals(self, api_request_auth_context: APIRequestContext):
        phone_numbers = PhoneNumbersRequests(api_request_auth_context)
        phones_def = phone_numbers.get_phone_numbers(BASE_URL_LIS, status_id=[1], state_id=[2], num_sort="MSISDN",
                                                     is_reserved=False)
        phones_abc = phone_numbers.get_phone_numbers(BASE_URL_LIS, type_def=False, status_id=[1], state_id=[2],
                                                     num_sort="-MSISDN", is_reserved=False)
        def_data = phone_numbers.get_numbers_data(phones_def)
        abc_data = phone_numbers.get_numbers_data_without_phone_number_abc(phones_abc)
        phone_numbers.update_phone_numbers(BASE_URL_LIS, [def_data[0].phone_number_id,
                                                          def_data[1].phone_number_id], 1)
        phone_numbers.update_phone_numbers(BASE_URL_LIS, [abc_data[0].phone_number_id,
                                                          abc_data[1].phone_number_id], 3, 2)
        self.home_page_lis.NUMBER_VOLUME_BTN.wait_to_be_visible()
        self.home_page_lis.NUMBER_VOLUME_BTN.click()
        self.number_volume_page.locators.TITLE.to_contain_text("Номерная ёмкость")
        self.number_volume_page.locators.ZONE_TYPE[0].to_have_css("background", re.compile(r'rgb\(69, 166, 0\)'))

        self.number_volume_page.locators.SEARCH_BTN.click()
        self.number_volume_page.locators.STATUS_FILTER_BTN.click()
        self.number_volume_page.locators.STATUS_OPTION_FREE.click()
        self.number_volume_page.locators.STATE_FILTER_BTN.click()
        self.number_volume_page.locators.STATE_FILTER_OPTIONS.wait_to_be_visible()
        self.number_volume_page.locators.STATE_FILTER_OPTIONS.wait_to_have_count(11)
        self.number_volume_page.locators.STATE_FILTER_OPTIONS[8].click()
        self.number_volume_page.locators.STATE_FILTER_BTN.click()
        self.number_volume_page.locators.BLOCKING_FILTER_BTN.click()
        self.number_volume_page.locators.NOT_BLOCKED_OPTION.click()
        self.number_volume_page.locators.FILTER_SEARCH_BTN.click()
        self.number_volume_page.locators.MSISDN_HEADER.click()
        delay(1, "Время на прямую сортировку списка")
        self.number_volume_page.locators.PHONE_NUMBERS[0].wait_to_have_text(def_data[0].MSISDN)

        self.number_volume_page.locators.LINE_CHECKBOXES[0].click()
        self.number_volume_page.locators.LINE_CHECKBOXES[1].click()
        self.number_volume_page.locators.LINK_DEF_TO_ABC_BTN.click()
        self.number_volume_page.locators.MODAL_TITLE[0].wait_to_have_text("Связывание номеров")
        self.number_volume_page.locators.TEMPLATE_INPUT.to_have_value("")
        self.number_volume_page.locators.ABC_START_INPUT.fill(abc_data[0].MSISDN)
        self.number_volume_page.locators.ABC_END_INPUT.fill(abc_data[1].MSISDN)
        self.number_volume_page.locators.DEF_START_INPUT.fill(def_data[0].MSISDN)
        self.number_volume_page.locators.DEF_END_INPUT.fill(def_data[1].MSISDN)
        self.number_volume_page.locators.FIRST_BTN[0].to_contain_text("Связать")
        self.number_volume_page.locators.SECOND_BTN[0].to_contain_text("Отменить")
        self.number_volume_page.locators.FIRST_BTN[0].click()

        self.number_volume_page.locators.ABC_START_INPUT.to_have_css("color", re.compile(r'rgb\(192, 75, 49\)'))
        self.number_volume_page.locators.ABC_END_INPUT.to_have_css("color", re.compile(r'rgb\(192, 75, 49\)'))

    @allure.title("Удаление связки номеров DEF и ABC")
    @allure.id(582292)
    @allure.tag("can_auth", "success")
    def test_remove_numbers_links(self, api_request_auth_context: APIRequestContext):
        phone_numbers = PhoneNumbersRequests(api_request_auth_context)
        linked_phones = phone_numbers.get_phone_numbers(BASE_URL_LIS, state_id=[7], num_sort="MSISDN")
        linked_phones_data = phone_numbers.get_numbers_data(linked_phones)
        self.home_page_lis.NUMBER_VOLUME_BTN.wait_to_be_visible()
        self.home_page_lis.NUMBER_VOLUME_BTN.click()
        self.number_volume_page.locators.TITLE.to_contain_text("Номерная ёмкость")
        self.number_volume_page.locators.ZONE_TYPE[0].to_have_css("background", re.compile(r'rgb\(69, 166, 0\)'))

        self.number_volume_page.locators.SEARCH_BTN.click()
        self.number_volume_page.locators.STATE_FILTER_BTN.click()
        self.number_volume_page.locators.STATE_FILTER_OPTIONS.wait_to_be_visible()
        self.number_volume_page.locators.STATE_FILTER_OPTIONS.wait_to_have_count(11)
        self.number_volume_page.locators.STATE_FILTER_OPTIONS[10].click()
        self.number_volume_page.locators.FILTER_SEARCH_BTN.click()
        self.number_volume_page.locators.PHONE_NUMBERS.wait_to_be_visible()
        self.number_volume_page.locators.MSISDN_HEADER.click()
        delay(1, "Время на прямую сортировку списка")
        self.number_volume_page.locators.PHONE_NUMBERS[0].wait_to_have_text(linked_phones_data[0].MSISDN)
        self.number_volume_page.locators.LINE_CHECKBOXES[0].click()
        self.number_volume_page.locators.LINE_CHECKBOXES[1].click()
        delay(.3, reason="Кнопка не активна доли секунды, даже в случае enabled")
        self.number_volume_page.locators.UNLINK_BTN.click()

        self.number_volume_page.locators.MODAL.wait_elements_visible(0)
        self.number_volume_page.locators.MODAL_TITLE[0].to_contain_text("Подтверждение операции")
        (self.number_volume_page.locators.MODAL_BODY_TEXT.
         to_contain_text(' Операция "Развязать" будет выполнена для выбранных записей (2). Выполнить операцию?'))
        self.number_volume_page.locators.FIRST_BTN[-1].click()

        self.number_volume_page.locators.CLEAR_FILTER_BTN.click()
        self.number_volume_page.locators.MSISDN_FILTER_BTN.click()
        self.number_volume_page.locators.MSISDN_OPTION_INTERVAL.click()
        self.number_volume_page.locators.MSISDN_FILTER_INPUT_FROM.fill(linked_phones_data[0].MSISDN)
        self.number_volume_page.locators.MSISDN_FILTER_INPUT_TO.fill(linked_phones_data[1].MSISDN)
        self.number_volume_page.locators.FILTER_SEARCH_BTN.click()
        self.number_volume_page.locators.PHONE_NUMBERS.wait_to_have_count(2)
        self.number_volume_page.locators.PHONE_NUMBERS[0].wait_to_have_text(linked_phones_data[0].MSISDN)
        self.number_volume_page.locators.PHONE_NUMBERS[1].wait_to_have_text(linked_phones_data[1].MSISDN)
        self.number_volume_page.locators.PHONE_NUMBERS_STATE[0].wait_to_have_text("Открыт для исп.")
        self.number_volume_page.locators.PHONE_NUMBERS_STATE[1].wait_to_have_text("Открыт для исп.")

    @allure.title("Смена класса номера")
    @allure.id(580674)
    @allure.tag("can_auth", "success")
    def test_change_number_class(self, api_request_auth_context: APIRequestContext):
        phone_numbers = PhoneNumbersRequests(api_request_auth_context)
        phones = phone_numbers.get_phone_numbers(BASE_URL_LIS, status_id=[1], state_id=[2], num_sort="MSISDN",
                                                 is_reserved="false", class_ids=[1])
        phones_data = phones.json()['items']
        self.home_page_lis.NUMBER_VOLUME_BTN.wait_to_be_visible()
        self.home_page_lis.NUMBER_VOLUME_BTN.click()
        self.number_volume_page.locators.TITLE.to_contain_text("Номерная ёмкость")
        self.number_volume_page.locators.REFRESH_BTN.click()

        self.number_volume_page.locators.SEARCH_BTN.click()
        self.number_volume_page.locators.MSISDN_FILTER_BTN.click()
        self.number_volume_page.locators.MSISDN_OPTION_VALUE.click()
        self.number_volume_page.locators.MSISDN_FILTER_INPUT.fill(phones_data[0]['MSISDN'])
        self.number_volume_page.locators.FILTER_SEARCH_BTN.click()
        self.number_volume_page.locators.PHONE_NUMBERS.wait_to_have_count(1)
        self.number_volume_page.locators.PHONE_NUMBERS[0].wait_to_have_text(phones_data[0]['MSISDN'])
        self.number_volume_page.locators.PHONE_NUMBERS_CLASS[0].wait_to_have_text("Обычный")

        self.number_volume_page.locators.LINE_CHECKBOXES[0].click()
        delay(.3, reason="Кнопка не активна доли секунды, даже в случае enabled")
        self.number_volume_page.locators.CHANGE_NUM_CLASS_BTN.click()

        self.number_volume_page.locators.MODAL.wait_elements_visible(0)
        self.number_volume_page.locators.MODAL_TITLE[0].to_contain_text("Изменение класса номера (MSISDN)")
        self.number_volume_page.locators.CHOOSE_CLASS_FIELD.click()
        self.number_volume_page.locators.CLASS_OPTIONS[0].click()
        self.number_volume_page.locators.CHOOSE_CLASS_FIELD.wait_to_have_text(" Бронзовый ")
        self.number_volume_page.locators.CONFIRM_CHANGE_CLASS_BTN.wait_to_have_text("Сохранить")
        self.number_volume_page.locators.CANCEL_CHANGE_CLASS_BTN.wait_to_have_text("Отменить")
        self.number_volume_page.locators.CONFIRM_CHANGE_CLASS_BTN.click()

        self.number_volume_page.locators.MODAL.wait_elements_visible(1)
        self.number_volume_page.locators.MODAL_TITLE[1].to_contain_text("Подтверждение операции")
        (self.number_volume_page.locators.MODAL_BODY_TEXT.
         to_contain_text(' Операция "Изменить класс номера" будет выполнена для выбранных записей (1). Выполнить операцию?'))
        self.number_volume_page.locators.FIRST_BTN[-1].click()
        self.number_volume_page.locators.PHONE_NUMBERS_CLASS[0].wait_to_have_text("Бронзовый")
        self.number_volume_page.locators.PHONE_NUMBERS[0].wait_to_have_text(phones_data[0]['MSISDN'])
