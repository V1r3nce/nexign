import re

import allure
import pytest
from playwright.sync_api import APIRequestContext, Page

from api.requests.lis_requests.phone_numbers import PhoneNumbersRequests
from common.helpers.download_helper import CheckFile
from common.helpers.time_helpers import delay
from pages.base_page import BasePage
from pages.lis_pages.number_volume_page import NumberVolumePage
from pages.locators.lis_locators.home_elements_lis import HomeElementsLis


@allure.epic("E2E_11 Подготовка номеров к продаже")
@allure.suite("E2E_11 Подготовка номеров к продаже")
class TestSaleNumbersPreview:
    @pytest.fixture(autouse=True)
    def setup(self, stand_login_lis: Page) -> None:
        self.base_page = BasePage(stand_login_lis)
        self.home_page_lis = HomeElementsLis(stand_login_lis)
        self.number_volume_page = NumberVolumePage(stand_login_lis)

    @allure.title("Просмотр номеров")
    @allure.id(580593)
    @allure.description("Проверка отображения номеров и элементов страницы Номерная емкость")
    @allure.tag("can_auth", "success")
    @pytest.mark.regress
    def test_numbers_preview(self, api_request_auth_context: APIRequestContext) -> None:
        self.home_page_lis.NUMBER_VOLUME_BTN.click()
        self.number_volume_page.locators.TITLE.to_contain_text("Номерная ёмкость")
        self.number_volume_page.locators.PAGE_TABS[0].wait_to_have_text("Список MSISDN")
        self.number_volume_page.locators.RESERVE_BTN.wait_to_be_visible()
        self.number_volume_page.locators.LINK_NUMBER_BTN.wait_to_be_visible()
        self.number_volume_page.locators.REFRESH_BTN.wait_to_be_visible()
        self.number_volume_page.locators.SEARCH_BTN.wait_to_be_visible()

        self.number_volume_page.locators.REFRESH_BTN.click()
        self.number_volume_page.locators.PHONE_NUMBERS[0].wait_to_be_visible()
        self.number_volume_page.locators.PHONE_NUMBERS[10].wait_to_be_visible()
        self.number_volume_page.locators.NUMBERS_COUNTER.wait_to_be_visible()
        phone_numbers = PhoneNumbersRequests(api_request_auth_context)
        phones = phone_numbers.get_phone_numbers()
        self.number_volume_page.locators.NUMBERS_COUNTER.to_contain_text("Всего*")
        self.number_volume_page.locators.NUMBERS_COUNTER.to_contain_text(str(phones.json()["listInfo"]["count"]))
        self.number_volume_page.locators.LINE_CHECKBOXES[0].click()
        self.number_volume_page.locators.LINE_CHECKBOXES[10].click()
        self.number_volume_page.locators.TABLE_LINE[0].to_have_class(class_name=re.compile(r"js-selected"))
        self.number_volume_page.locators.TABLE_LINE[10].to_have_class(class_name=re.compile(r"js-selected"))

    @allure.title("Просмотр номеров (Выбор зоны нумерации)")
    @allure.id(580669)
    @allure.description("Проверка отображения номеров для разных зон нумерации")
    @allure.tag("can_auth", "success")
    @pytest.mark.regress
    def test_numbers_zone_preview(self, api_request_auth_context: APIRequestContext) -> None:
        self.home_page_lis.NUMBER_VOLUME_BTN.click()
        self.number_volume_page.locators.TITLE.to_contain_text("Номерная ёмкость")
        self.number_volume_page.locators.ZONE_TYPE[0].click()
        self.number_volume_page.locators.REFRESH_BTN.click()

        phone_numbers = PhoneNumbersRequests(api_request_auth_context)
        phones_1 = phone_numbers.get_phone_numbers()
        phones_data_1 = phones_1.json()["items"]
        self.number_volume_page.locators.PHONE_NUMBERS[0].wait_to_be_visible()
        self.number_volume_page.locators.PHONE_NUMBERS[0].to_contain_text(phones_data_1[0]["MSISDN"])
        self.number_volume_page.locators.PHONE_NUMBERS[10].to_contain_text(phones_data_1[10]["MSISDN"])

        self.number_volume_page.locators.ZONE_TYPE[1].click()
        self.number_volume_page.locators.REFRESH_BTN.click()

        phones_2 = phone_numbers.get_phone_numbers(type_def=False)
        phones_data_2 = phones_2.json()["items"]
        self.number_volume_page.locators.PHONE_NUMBERS[0].wait_to_have_text(phones_data_2[0]["MSISDN"])
        self.number_volume_page.locators.PHONE_NUMBERS[10].wait_to_have_text(phones_data_2[10]["MSISDN"])

        self.number_volume_page.locators.LINK_NUMBER_BTN.wait_to_be_visible()
        self.number_volume_page.locators.REFRESH_BTN.wait_to_be_visible()
        self.number_volume_page.locators.SEARCH_BTN.wait_to_be_visible()

        self.number_volume_page.locators.NUMBERS_COUNTER.to_contain_text("Всего*")
        self.number_volume_page.locators.NUMBERS_COUNTER.to_contain_text(str(phones_2.json()["listInfo"]["count"]))

        self.number_volume_page.locators.LINE_CHECKBOXES[0].click()
        self.number_volume_page.locators.LINE_CHECKBOXES[10].click()
        self.number_volume_page.locators.TABLE_LINE[0].to_have_class(class_name=re.compile(r"js-selected"))
        self.number_volume_page.locators.TABLE_LINE[10].to_have_class(class_name=re.compile(r"js-selected"))

    @allure.title("Просмотр номеров (Выгрузка в файл)")
    @allure.id(580927)
    @allure.description("Проверка сохранения данных по номерам в Excel")
    @allure.tag("can_auth", "success")
    @pytest.mark.regress
    def test_numbers_download(
        self, api_request_auth_context: APIRequestContext, remove_file_from_download_folder: list
    ) -> None:
        phone_numbers = PhoneNumbersRequests(api_request_auth_context)
        phones = phone_numbers.get_phone_numbers()
        phones_data = phones.json()["items"]
        self.home_page_lis.NUMBER_VOLUME_BTN.click()
        self.number_volume_page.locators.TITLE.to_contain_text("Номерная ёмкость")
        self.number_volume_page.locators.REFRESH_BTN.click()

        self.number_volume_page.locators.CHECK_ALL_BTN.click()
        delay(0.3, reason="Кнопка не активна доли секунды, даже в случае enabled")
        self.number_volume_page.locators.DOWNLOAD_BTN.hover()
        self.number_volume_page.locators.DOWNLOAD_BTN.click()
        self.number_volume_page.locators.MODAL[0].wait_to_be_visible()
        self.number_volume_page.locators.MODAL_TITLE[0].to_contain_text("Подтверждение операции")
        with self.number_volume_page.page.expect_download(timeout=20000) as download_info:
            self.number_volume_page.locators.FIRST_BTN[0].click()
        download = download_info.value
        file_name = download.suggested_filename
        self.file_check = CheckFile(file_name)
        download.save_as(self.file_check.path)
        remove_file_from_download_folder.append(file_name)
        self.file_check.check_excel_file_group_of_fields_contains([[0, 0], [0, 1]], ["Number type", "MSISDN"])
        self.file_check.check_excel_file_contain_filled_rows(phones.json()["listInfo"]["count"] + 1)
        self.file_check.check_excel_file_contain_value_in_column(phones_data[0]["MSISDN"], 1)

    @allure.title("Просмотр номеров (История номера)")
    @allure.id(580670)
    @allure.tag("can_auth", "success")
    @pytest.mark.regress
    def test_numbers_history(self, api_request_auth_context: APIRequestContext) -> None:
        phone_numbers = PhoneNumbersRequests(api_request_auth_context)
        phones = phone_numbers.get_phone_numbers()
        phones_data = phones.json()["items"]
        self.home_page_lis.NUMBER_VOLUME_BTN.click()
        self.number_volume_page.locators.TITLE.to_contain_text("Номерная ёмкость")
        self.number_volume_page.locators.REFRESH_BTN.click()

        self.number_volume_page.locators.TABLE_LINE.wait_elements_visible(10)
        self.number_volume_page.locators.LINE_CHECKBOXES.click(0)
        self.number_volume_page.locators.HISTORY_BTN.wait_to_be_enabled()
        delay(0.3, reason="Кнопка не активна доли секунды, даже в случае enabled")
        self.number_volume_page.locators.HISTORY_BTN.click()

        self.number_volume_page.locators.MODAL[0].wait_to_be_visible()
        self.number_volume_page.locators.MODAL_TITLE[0].to_contain_text(f"История по MSISDN {phones_data[0]['MSISDN']}")
        self.number_volume_page.locators.REFRESH_HISTORY_BTN.wait_to_be_visible()
        self.number_volume_page.locators.HISTORY_TYPE_BTN[0].to_contain_text("LIS")
        self.number_volume_page.locators.HISTORY_TYPE_BTN[1].to_contain_text("Greenfield")
        self.number_volume_page.locators.HISTORY_TYPE_BTN[2].to_contain_text("Операций")

    @allure.title("Просмотр номеров (История номера, несколько номеров)")
    @allure.id(580671)
    @allure.tag("can_auth", "success")
    @pytest.mark.regress
    def test_history_pair_of_numbers(self) -> None:
        self.home_page_lis.NUMBER_VOLUME_BTN.click()
        self.number_volume_page.locators.TITLE.to_contain_text("Номерная ёмкость")
        self.number_volume_page.locators.REFRESH_BTN.click()

        self.number_volume_page.locators.TABLE_LINE.wait_elements_visible(10)
        self.number_volume_page.locators.LINE_CHECKBOXES.click(0)
        self.number_volume_page.locators.LINE_CHECKBOXES.click(1)
        self.number_volume_page.locators.HISTORY_BTN.check_attribute_by_value("disabled", "disabled")

        delay(1, reason="Кнопка не активна доли секунды, даже в случае enabled")
        self.number_volume_page.locators.HISTORY_BTN.click()
        delay(1, reason="Чтобы наверняка убедиться, что окно истории не открылась")
        self.number_volume_page.locators.MODAL.wait_not_to_be_visible()

    @allure.title("Просмотр номеров (Фильтрация списка)")
    @allure.id(581638)
    @allure.tag("can_auth", "success")
    @pytest.mark.regress
    def test_filter_numbers(self, api_request_auth_context: APIRequestContext) -> None:
        phone_numbers = PhoneNumbersRequests(api_request_auth_context)
        phones = phone_numbers.get_phone_numbers()
        phones_data = phones.json()["items"]
        self.home_page_lis.NUMBER_VOLUME_BTN.wait_to_be_visible()
        self.home_page_lis.NUMBER_VOLUME_BTN.click()
        self.number_volume_page.locators.TITLE.to_contain_text("Номерная ёмкость")
        self.number_volume_page.locators.REFRESH_BTN.click()

        self.number_volume_page.locators.TABLE_LINE.wait_elements_visible(10)
        self.number_volume_page.locators.SEARCH_BTN.click()
        self.number_volume_page.check_search_elements()
        self.number_volume_page.locators.MSISDN_FILTER_BTN.click()
        self.number_volume_page.locators.MSISDN_OPTION_VALUE.click()
        self.number_volume_page.locators.MSISDN_FILTER_INPUT.fill(phones_data[2]["MSISDN"])
        self.number_volume_page.locators.FILTER_SEARCH_BTN.click()
        self.number_volume_page.locators.PHONE_NUMBERS.wait_to_have_count(1)
        self.number_volume_page.locators.PHONE_NUMBERS[0].wait_to_have_text(phones_data[2]["MSISDN"])

        self.number_volume_page.locators.HIDE_FILTER_BTN.click()
        self.number_volume_page.locators.FILTER_SEARCH_BTN.not_to_be_visible()
        self.number_volume_page.locators.PHONE_NUMBERS.wait_to_have_count(1)
        self.number_volume_page.locators.PHONE_NUMBERS[0].wait_to_have_text(phones_data[2]["MSISDN"])

        self.number_volume_page.locators.SEARCH_BTN.click()
        self.number_volume_page.locators.MSISDN_SELECTED_OPTIONS.to_contain_text("Точное значение")
        self.number_volume_page.locators.MSISDN_FILTER_INPUT.to_have_value(phones_data[2]["MSISDN"])

        self.number_volume_page.page.reload(wait_until="domcontentloaded")
        self.number_volume_page.locators.MSISDN_SELECTED_OPTIONS.to_contain_text("Точное значение")
        self.number_volume_page.locators.MSISDN_FILTER_INPUT.to_have_value(phones_data[2]["MSISDN"])

        self.number_volume_page.locators.FILTER_SEARCH_BTN.click()
        self.number_volume_page.locators.PHONE_NUMBERS.wait_to_have_count(1)
        self.number_volume_page.locators.PHONE_NUMBERS[0].wait_to_have_text(phones_data[2]["MSISDN"])

        self.number_volume_page.locators.LINK_NUMBER_FILTER_BTN.click()
        self.number_volume_page.locators.LINK_NUMBER_OPTION_INTERVAL.click()
        self.number_volume_page.locators.LINK_NUMBER_SELECTED_OPTIONS.to_contain_text("По диапазону")
        self.number_volume_page.locators.COMMENT_FILTER_BTN.click()
        self.number_volume_page.locators.COMMENT_OPTION_NOT_FILLED.click()
        self.number_volume_page.locators.COMMENT_SELECTED_OPTIONS.to_contain_text("Не заполнен")

        self.number_volume_page.locators.CLEAR_FILTER_BTN.click()
        phones_2 = phone_numbers.get_phone_numbers()
        phones_data_2 = phones_2.json()["items"]
        self.number_volume_page.locators.PHONE_NUMBERS[0].wait_to_have_text(phones_data_2[0]["MSISDN"])
        self.number_volume_page.locators.PHONE_NUMBERS[2].wait_to_have_text(phones_data_2[2]["MSISDN"])

    @allure.title("Ввод номера в эксплуатацию")
    @allure.id(580955)
    @allure.tag("can_auth", "success")
    @pytest.mark.regress
    def test_make_number_set_in_use(self, api_request_auth_context: APIRequestContext) -> None:
        phone_numbers = PhoneNumbersRequests(api_request_auth_context)
        phones = phone_numbers.get_phone_numbers(status_id=[3], state_id=[1])
        phones_data = phones.json()["items"]
        self.home_page_lis.NUMBER_VOLUME_BTN.wait_to_be_visible()
        self.home_page_lis.NUMBER_VOLUME_BTN.click()
        self.number_volume_page.locators.TITLE.to_contain_text("Номерная ёмкость")
        self.number_volume_page.locators.REFRESH_BTN.click()

        self.number_volume_page.locators.SEARCH_BTN.click()
        self.number_volume_page.locators.STATUS_FILTER_BTN.click()
        self.number_volume_page.locators.STATUS_OPTION_UNAVAILABLE.click()
        self.number_volume_page.locators.STATE_FILTER_BTN.click()
        self.number_volume_page.locators.STATE_FILTER_OPTIONS.wait_to_have_count(11)
        self.number_volume_page.locators.STATE_FILTER_OPTIONS[3].click()
        self.number_volume_page.locators.FILTER_SEARCH_BTN.click()
        self.number_volume_page.locators.TABLE_LINE.wait_elements_visible(3)
        self.number_volume_page.locators.PHONE_NUMBERS[0].wait_to_have_text(phones_data[0]["MSISDN"])

        self.number_volume_page.locators.LINE_CHECKBOXES[0].click()
        delay(0.3, reason="Кнопка не активна доли секунды, даже в случае enabled")
        self.number_volume_page.locators.SET_IN_USE_BTN.click()

        self.number_volume_page.locators.MODAL[0].wait_to_be_visible()
        self.number_volume_page.locators.MODAL_TITLE[0].to_contain_text("Подтверждение операции")
        self.number_volume_page.locators.FIRST_BTN[0].click()

        self.number_volume_page.locators.CLEAR_FILTER_BTN.click()
        self.number_volume_page.locators.STATUS_FILTER_BTN.click()
        self.number_volume_page.locators.STATUS_OPTION_FREE.click()
        self.number_volume_page.locators.FILTER_SEARCH_BTN.click()
        self.number_volume_page.locators.DATE_CHANGE_STATUS_HEADER.click()
        delay(1, reason="Время на сортировку в сторону увеличения")
        self.number_volume_page.locators.DATE_CHANGE_STATUS_HEADER.click()
        delay(1, reason="Время на сортировку в сторону уменьшения")
        self.number_volume_page.locators.PHONE_NUMBERS[0].wait_to_have_text(phones_data[0]["MSISDN"])
        self.number_volume_page.locators.PHONE_NUMBERS_STATUS[0].wait_to_have_text("Свободен")
        self.number_volume_page.locators.PHONE_NUMBERS_STATE[0].wait_to_have_text("Открыт для исп.")

    @allure.title("Вывод номера из эксплуатации")
    @allure.id(580942)
    @allure.tag("can_auth", "success")
    @pytest.mark.regress
    def test_make_number_out_of_use(self, api_request_auth_context: APIRequestContext) -> None:
        phone_numbers = PhoneNumbersRequests(api_request_auth_context)
        phones = phone_numbers.get_phone_numbers(
            status_id=[1], state_id=[2], num_sort="-statusDate", is_reserved="false"
        )
        phones_data = phones.json()["items"]
        self.home_page_lis.NUMBER_VOLUME_BTN.wait_to_be_visible()
        self.home_page_lis.NUMBER_VOLUME_BTN.click()
        self.number_volume_page.locators.TITLE.to_contain_text("Номерная ёмкость")
        self.number_volume_page.locators.REFRESH_BTN.click()

        self.number_volume_page.locators.SEARCH_BTN.click()
        self.number_volume_page.locators.MSISDN_FILTER_BTN.click()
        self.number_volume_page.locators.MSISDN_OPTION_VALUE.click()
        self.number_volume_page.locators.MSISDN_FILTER_INPUT.fill(phones_data[0]["MSISDN"])
        self.number_volume_page.locators.FILTER_SEARCH_BTN.click()
        self.number_volume_page.locators.PHONE_NUMBERS.wait_to_have_count(1)
        self.number_volume_page.locators.PHONE_NUMBERS[0].wait_to_have_text(phones_data[0]["MSISDN"])

        self.number_volume_page.locators.LINE_CHECKBOXES[0].click()
        delay(0.3, reason="Кнопка не активна доли секунды, даже в случае enabled")
        self.number_volume_page.locators.SET_OUT_USE_BTN.click()

        self.number_volume_page.locators.MODAL[0].wait_to_be_visible()
        self.number_volume_page.locators.MODAL_TITLE[0].to_contain_text("Подтверждение операции")
        (
            self.number_volume_page.locators.MODAL_BODY_TEXT[0].to_contain_text(
                ' Операция "Исключить" будет выполнена для выбранных записей (1). Выполнить операцию?'
            )
        )
        self.number_volume_page.locators.FIRST_BTN[0].click()

        self.number_volume_page.locators.PHONE_NUMBERS[0].wait_to_have_text(phones_data[0]["MSISDN"])
        self.number_volume_page.locators.PHONE_NUMBERS_STATUS[0].wait_to_have_text("Недоступен")
        self.number_volume_page.locators.PHONE_NUMBERS_STATE[0].wait_to_have_text("Закрыт для исп.")

    @allure.title("Вывод номера из карантина")
    @allure.id(581494)
    @allure.tag("can_auth", "success")
    @pytest.mark.regress
    def test_make_number_out_of_quarantine(self, api_request_auth_context: APIRequestContext) -> None:
        phone_numbers = PhoneNumbersRequests(api_request_auth_context)
        phones = phone_numbers.get_phone_numbers(status_id=[1], state_id=[4])
        phones_data = phones.json()["items"]
        suitable_number = [item["MSISDN"] for item in phones_data if item["expirationReserveDate"] is not None][0]
        # TODO как починят баг https://jira.nexign.com/browse/RMBSS-9270, проверить достаточно ли номеров на карантине
        #  генерит автотест https://allure.nexign.com/project/313/test-cases/576573?treeId=825
        self.home_page_lis.NUMBER_VOLUME_BTN.wait_to_be_visible()
        self.home_page_lis.NUMBER_VOLUME_BTN.click()
        self.number_volume_page.locators.TITLE.to_contain_text("Номерная ёмкость")
        self.number_volume_page.locators.REFRESH_BTN.click()

        self.number_volume_page.locators.SEARCH_BTN.click()
        self.number_volume_page.locators.MSISDN_FILTER_BTN.click()
        self.number_volume_page.locators.MSISDN_OPTION_VALUE.click()
        self.number_volume_page.locators.MSISDN_FILTER_INPUT.fill(suitable_number)
        self.number_volume_page.locators.FILTER_SEARCH_BTN.click()
        self.number_volume_page.locators.PHONE_NUMBERS.wait_to_have_count(1)
        self.number_volume_page.locators.PHONE_NUMBERS[0].wait_to_have_text(suitable_number)

        self.number_volume_page.locators.LINE_CHECKBOXES[0].click()
        delay(0.3, reason="Кнопка не активна доли секунды, даже в случае enabled")
        self.number_volume_page.locators.SET_OUT_OF_ISOLATION_BTN.click()

        self.number_volume_page.locators.MODAL[0].wait_to_be_visible()
        self.number_volume_page.locators.MODAL_TITLE[0].to_contain_text("Подтверждение операции")
        (
            self.number_volume_page.locators.MODAL_BODY_TEXT[0].to_contain_text(
                ' Операция "Вывод из карантина" будет выполнена для выбранных записей (1). Выполнить операцию?'
            )
        )
        self.number_volume_page.locators.FIRST_BTN[0].click()

        self.number_volume_page.locators.PHONE_NUMBERS[0].wait_to_have_text(suitable_number)
        self.number_volume_page.locators.PHONE_NUMBERS_STATUS[0].wait_to_have_text("Свободен")
        self.number_volume_page.locators.PHONE_NUMBERS_STATE[0].wait_to_have_text("Открыт для исп.")

    @allure.title("Добавление номерной емкости (DEF)")
    @allure.id(582071)
    @allure.tag("can_auth", "success")
    @pytest.mark.regress
    @pytest.mark.smoke
    def test_add_number_def(self, api_request_auth_context: APIRequestContext) -> None:
        phone_numbers = PhoneNumbersRequests(api_request_auth_context)
        phones = phone_numbers.get_phone_numbers(num_sort="-MSISDN")
        phones_data = phones.json()["items"]
        self.home_page_lis.NUMBER_VOLUME_BTN.wait_to_be_visible()
        self.home_page_lis.NUMBER_VOLUME_BTN.click()
        self.number_volume_page.locators.TITLE.to_contain_text("Номерная ёмкость")
        self.number_volume_page.locators.ZONE_TYPE[0].to_have_css("background", re.compile(r"rgb\(69, 166, 0\)"))
        self.number_volume_page.locators.ADD_NUMBER_BTN.click()
        self.number_volume_page.locators.MODAL_ADD_NUMBER.wait_to_be_visible()
        self.number_volume_page.locators.MODAL_ADD_NUMBER_TITLE.to_contain_text("Добавление номера зоны DEF")
        self.number_volume_page.check_add_new_number_elements()
        self.number_volume_page.locators.NUMBER_TYPE_FIELD.to_contain_text("Федеральная")

        self.number_volume_page.locators.START_PHONE_NUMBER.fill("9876543210")
        self.number_volume_page.locators.START_PHONE_NUMBER.to_have_value("9876543210")

        new_number = str(int(phones_data[0]["MSISDN"]) + 1)
        new_number_2 = str(int(phones_data[0]["MSISDN"]) + 2)
        self.number_volume_page.locators.START_PHONE_NUMBER.fill(new_number + "2")
        self.number_volume_page.locators.COUNT_PHONE_NUMBER.fill("2")
        self.number_volume_page.locators.CHOOSE_COMMUTATOR_BTN.click()
        self.number_volume_page.locators.COMMUTATOR_TYPE_NAME_SEARCH.fill("Коммутатор_DEF")
        self.number_volume_page.page.keyboard.press("Enter")
        self.number_volume_page.locators.COMMUTATOR_TYPE_NAMES.wait_to_be_visible()
        self.number_volume_page.locators.COMMUTATOR_TYPE_NAMES[0].click(click_count=2)
        self.number_volume_page.locators.NUMBER_TYPE_FIELD.click()
        self.number_volume_page.locators.NUMBER_TYPE_OPTIONS[2].to_contain_text("Федеральная")
        self.number_volume_page.locators.NUMBER_TYPE_OPTIONS[2].click()
        self.number_volume_page.locators.OPERATOR_FIELD.click()
        self.number_volume_page.locators.OPERATOR_OPTIONS[1].click()
        self.number_volume_page.locators.NUMBER_TYPE_ALL_CHECKBOX.click()
        delay(0.5, reason="Время на отключение чекбокса")
        self.number_volume_page.check_all_checkboxes_turned_off()

        self.number_volume_page.locators.ADD_BUTTON.wait_to_be_visible()
        self.number_volume_page.locators.CANCEL_ADD_NUMBER.wait_to_be_visible()
        self.number_volume_page.locators.ADD_BUTTON.click()
        self.number_volume_page.locators.START_PHONE_NUMBER.to_have_css("color", re.compile(r"rgb\(192, 75, 49\)"))
        self.number_volume_page.locators.START_PHONE_NUMBER.fill(new_number)

        self.number_volume_page.locators.ADD_BUTTON.click()
        self.number_volume_page.locators.CANCEL_ADD_NUMBER.not_to_be_visible()

        (
            self.number_volume_page.locators.MODAL_BODY_TEXT.to_contain_text(
                0, "Операция выполняется в фоновом режиме. Её выполнение можно отследить в мониторе операций."
            )
        )
        self.number_volume_page.locators.OK_BTN.click()
        self.number_volume_page.locators.REFRESH_BTN.click()
        self.number_volume_page.locators.MSISDN_HEADER.click()
        delay(1, reason="Время на сортировку в сторону увеличения")
        self.number_volume_page.locators.MSISDN_HEADER.click()
        delay(1, reason="Время на сортировку в сторону уменьшения")
        self.number_volume_page.locators.PHONE_NUMBERS[1].wait_to_have_text(new_number)
        self.number_volume_page.locators.PHONE_NUMBERS[0].wait_to_have_text(new_number_2)
        self.number_volume_page.locators.PHONE_NUMBERS_CLASS[1].wait_to_have_text("Обычный")
        self.number_volume_page.locators.PHONE_NUMBERS_CLASS[0].wait_to_have_text("Обычный")
        self.number_volume_page.locators.PHONE_NUMBERS_COMMUTATORS[1].wait_to_have_text("Коммутатор_DEF")
        self.number_volume_page.locators.PHONE_NUMBERS_COMMUTATORS[0].wait_to_have_text("Коммутатор_DEF")
        self.number_volume_page.locators.PHONE_NUMBERS_STANDARDS[1].wait_to_have_text("GSM")
        self.number_volume_page.locators.PHONE_NUMBERS_STANDARDS[0].wait_to_have_text("GSM")
        self.number_volume_page.locators.PHONE_NUMBERS_OPERATORS[1].wait_to_have_text("NEXIGN")
        self.number_volume_page.locators.PHONE_NUMBERS_OPERATORS[0].wait_to_have_text("NEXIGN")
        self.number_volume_page.locators.PHONE_NUMBERS_TYPES[1].wait_to_have_text("Федеральная")
        self.number_volume_page.locators.PHONE_NUMBERS_TYPES[0].wait_to_have_text("Федеральная")

    @allure.title("Добавление номерной емкости (ABC)")
    @allure.id(582091)
    @allure.tag("can_auth", "success")
    @pytest.mark.regress
    def test_add_number_abc(self, api_request_auth_context: APIRequestContext) -> None:
        phone_numbers = PhoneNumbersRequests(api_request_auth_context)
        phones = phone_numbers.get_phone_numbers(type_def=False, num_sort="-MSISDN")
        phones_data = phones.json()["items"]
        self.home_page_lis.NUMBER_VOLUME_BTN.wait_to_be_visible()
        self.home_page_lis.NUMBER_VOLUME_BTN.click()
        self.number_volume_page.locators.TITLE.to_contain_text("Номерная ёмкость")
        self.number_volume_page.locators.ZONE_TYPE[1].click()
        self.number_volume_page.locators.ZONE_TYPE[1].to_have_css("background", re.compile(r"rgb\(69, 166, 0\)"))
        self.number_volume_page.locators.ADD_NUMBER_BTN.click()
        self.number_volume_page.locators.MODAL_ADD_NUMBER.wait_to_be_visible()
        self.number_volume_page.locators.MODAL_ADD_NUMBER_TITLE.to_contain_text("Добавление номера зоны ABC")
        self.number_volume_page.check_add_new_number_elements(num_type="abc")

        self.number_volume_page.locators.START_PHONE_NUMBER.fill("8765432109")
        self.number_volume_page.locators.START_PHONE_NUMBER.to_have_value("8765432109")

        self.number_volume_page.locators.CHOSEN_CATEGORY_FIELD.to_contain_text("Дополнительный")
        self.number_volume_page.locators.NUMBER_TYPE_FIELD.to_contain_text("Городская")
        self.number_volume_page.locators.NUMBER_TYPE_FIELD.click()
        self.number_volume_page.locators.NUMBER_TYPE_OPTIONS[1].to_contain_text("Фиксированная")
        self.number_volume_page.locators.NUMBER_TYPE_OPTIONS[1].click()
        self.number_volume_page.locators.NUMBER_TYPE_FIELD.to_contain_text("Фиксированная")
        self.number_volume_page.locators.CHOSEN_CATEGORY_FIELD.to_contain_text("Телефония")

        new_number = str(int(phones_data[0]["MSISDN"]) + 1)
        new_number_2 = str(int(phones_data[0]["MSISDN"]) + 2)
        wrong_number = f"9{new_number[1:]}"
        self.number_volume_page.locators.START_PHONE_NUMBER.fill(new_number + "2")
        self.number_volume_page.locators.START_PHONE_NUMBER.to_have_value(new_number)
        self.number_volume_page.locators.START_PHONE_NUMBER.fill(wrong_number)
        self.number_volume_page.locators.START_PHONE_NUMBER.to_have_value(new_number[1:])

        self.number_volume_page.locators.START_PHONE_NUMBER.fill(new_number)
        self.number_volume_page.locators.COUNT_PHONE_NUMBER.fill("2")
        self.number_volume_page.locators.CHOOSE_COMMUTATOR_BTN.click()
        self.number_volume_page.locators.COMMUTATOR_TYPE_NAMES[0].click(click_count=2)
        self.number_volume_page.locators.NUMBER_TYPE_FIELD.click()
        self.number_volume_page.locators.NUMBER_TYPE_OPTIONS[1].to_contain_text("Фиксированная")
        self.number_volume_page.locators.NUMBER_TYPE_OPTIONS[1].click()
        self.number_volume_page.locators.OPERATOR_FIELD.click()
        self.number_volume_page.locators.OPERATOR_OPTIONS[1].click()
        self.number_volume_page.check_all_checkboxes_turned_off()

        self.number_volume_page.locators.ADD_BUTTON.wait_to_be_visible()
        self.number_volume_page.locators.CANCEL_ADD_NUMBER.wait_to_be_visible()
        self.number_volume_page.locators.ADD_BUTTON.click()

        (
            self.number_volume_page.locators.MODAL_BODY_TEXT[0].wait_to_have_text(
                "Не выбран ни один шаблон классификации. Номера будут загружены как обычные. Всё равно выполнить?"
            )
        )
        self.number_volume_page.locators.FIRST_BTN_CONFIRMATION.click()
        (
            self.number_volume_page.locators.MODAL_BODY_TEXT[0].wait_to_have_text(
                "Операция выполняется в фоновом режиме. Её выполнение можно отследить в мониторе операций."
            )
        )
        self.number_volume_page.locators.OK_BTN.click()
        self.number_volume_page.locators.REFRESH_BTN.click()
        self.number_volume_page.locators.MSISDN_HEADER.click()
        delay(1, reason="Время на сортировку в сторону увеличения")
        self.number_volume_page.locators.MSISDN_HEADER.click()
        delay(1, reason="Время на сортировку в сторону уменьшения")
        self.number_volume_page.locators.PHONE_NUMBERS[1].wait_to_have_text(new_number)
        self.number_volume_page.locators.PHONE_NUMBERS[0].wait_to_have_text(new_number_2)
        self.number_volume_page.locators.PHONE_NUMBERS_CLASS[1].wait_to_have_text("Обычный")
        self.number_volume_page.locators.PHONE_NUMBERS_CLASS[0].wait_to_have_text("Обычный")
        self.number_volume_page.locators.PHONE_NUMBERS_COMMUTATORS_ABC[1].wait_to_have_text("Коммутатор_ABC")
        self.number_volume_page.locators.PHONE_NUMBERS_COMMUTATORS_ABC[0].wait_to_have_text("Коммутатор_ABC")
        self.number_volume_page.locators.PHONE_NUMBERS_STANDARDS_ABC[1].wait_to_have_text("PSTN")
        self.number_volume_page.locators.PHONE_NUMBERS_STANDARDS_ABC[0].wait_to_have_text("PSTN")
        self.number_volume_page.locators.PHONE_NUMBERS_OPERATORS_ABC[1].wait_to_have_text("NEXIGN")
        self.number_volume_page.locators.PHONE_NUMBERS_OPERATORS_ABC[0].wait_to_have_text("NEXIGN")
        self.number_volume_page.locators.PHONE_NUMBERS_TYPES_ABC[1].wait_to_have_text("Фиксированная")
        self.number_volume_page.locators.PHONE_NUMBERS_TYPES_ABC[0].wait_to_have_text("Фиксированная")

    @allure.title("Добавление номерной емкости (8-800)")
    @allure.id(582207)
    @allure.tag("can_auth", "success")
    @pytest.mark.regress
    def test_add_number_8800(self, add_first_msisdn_8800, api_request_auth_context: APIRequestContext) -> None:
        phone_numbers = PhoneNumbersRequests(api_request_auth_context, 0)
        phones = phone_numbers.get_phone_numbers(type_def=False, num_sort="-MSISDN")
        phones_data = phones.json()["items"]
        self.home_page_lis.NUMBER_VOLUME_BTN.wait_to_be_visible()
        self.home_page_lis.NUMBER_VOLUME_BTN.click()
        self.number_volume_page.locators.TITLE.to_contain_text("Номерная ёмкость")
        self.number_volume_page.locators.ZONE_TYPE[2].click()
        self.number_volume_page.locators.ZONE_TYPE[2].to_have_css("background", re.compile(r"rgb\(69, 166, 0\)"))
        self.number_volume_page.locators.ADD_NUMBER_BTN.click()
        self.number_volume_page.locators.MODAL_ADD_NUMBER.wait_to_be_visible()
        self.number_volume_page.locators.MODAL_ADD_NUMBER_TITLE.to_contain_text("Добавление номера зоны 8-800")
        self.number_volume_page.check_add_new_number_elements(num_type="8-800")

        self.number_volume_page.locators.START_PHONE_NUMBER.fill("8765432109")
        self.number_volume_page.locators.START_PHONE_NUMBER.to_have_value("8765432109")

        self.number_volume_page.locators.CHOSEN_CATEGORY_FIELD.to_contain_text("Телефония")
        self.number_volume_page.locators.NUMBER_TYPE_FIELD.to_contain_text("8-800")

        new_number = str(int(phones_data[0]["MSISDN"]) + 1)
        new_number_2 = str(int(phones_data[0]["MSISDN"]) + 2)
        self.number_volume_page.locators.START_PHONE_NUMBER.fill(new_number)
        self.number_volume_page.locators.COUNT_PHONE_NUMBER.fill("2")
        self.number_volume_page.locators.OPERATOR_FIELD.click()
        delay(0.5)
        self.number_volume_page.locators.OPERATOR_OPTIONS[0].click()

        self.number_volume_page.locators.ADD_BUTTON.wait_to_be_visible()
        self.number_volume_page.locators.CANCEL_ADD_NUMBER.wait_to_be_visible()
        self.number_volume_page.locators.ADD_BUTTON.click()

        self.number_volume_page.locators.MODAL_BODY_TEXT[0].wait_to_have_text(
            "Операция выполняется в фоновом режиме. Её выполнение можно отследить в мониторе операций."
        )
        self.number_volume_page.locators.OK_BTN.click()

        self.number_volume_page.locators.REFRESH_BTN.click()
        self.number_volume_page.locators.MSISDN_HEADER.click()
        delay(1, reason="Время на сортировку в сторону увеличения")
        self.number_volume_page.locators.MSISDN_HEADER.click()
        delay(1, reason="Время на сортировку в сторону уменьшения")
        self.number_volume_page.locators.PHONE_NUMBERS[1].wait_to_have_text(new_number)
        self.number_volume_page.locators.PHONE_NUMBERS[0].wait_to_have_text(new_number_2)
        self.number_volume_page.locators.PHONE_NUMBERS_CLASS[1].wait_to_have_text("Обычный")
        self.number_volume_page.locators.PHONE_NUMBERS_CLASS[0].wait_to_have_text("Обычный")
        self.number_volume_page.locators.PHONE_NUMBERS_COMMUTATORS_ABC[1].wait_to_have_text("Коммутатор 8-800")
        self.number_volume_page.locators.PHONE_NUMBERS_COMMUTATORS_ABC[0].wait_to_have_text("Коммутатор 8-800")
        self.number_volume_page.locators.PHONE_NUMBERS_STANDARDS_ABC[1].wait_to_have_text("PSTN")
        self.number_volume_page.locators.PHONE_NUMBERS_STANDARDS_ABC[0].wait_to_have_text("PSTN")
        self.number_volume_page.locators.PHONE_NUMBERS_OPERATORS_ABC[1].wait_to_have_text("8800")
        self.number_volume_page.locators.PHONE_NUMBERS_OPERATORS_ABC[0].wait_to_have_text("8800")
        self.number_volume_page.locators.PHONE_NUMBERS_TYPES_ABC[1].wait_to_have_text("8-800")
        self.number_volume_page.locators.PHONE_NUMBERS_TYPES_ABC[0].wait_to_have_text("8-800")

    @allure.title("Добавление номерной емкости (ABC, PSTN из файла)")
    @allure.id(582303)
    @allure.tag("can_auth", "success")
    @pytest.mark.regress
    def test_add_number_abc_from_file(
        self, api_request_auth_context: APIRequestContext, remove_file_from_download_folder: list
    ) -> None:
        phone_numbers = PhoneNumbersRequests(api_request_auth_context)
        phones = phone_numbers.get_phone_numbers(type_def=False, num_sort="-MSISDN")
        phones_data = phones.json()["items"]
        self.home_page_lis.NUMBER_VOLUME_BTN.wait_to_be_visible()
        self.home_page_lis.NUMBER_VOLUME_BTN.click()
        self.number_volume_page.locators.TITLE.to_contain_text("Номерная ёмкость")
        self.number_volume_page.locators.ZONE_TYPE[1].click()
        self.number_volume_page.locators.ZONE_TYPE[1].to_have_css("background", re.compile(r"rgb\(69, 166, 0\)"))
        self.number_volume_page.locators.ADD_NUMBER_BTN.click()
        self.number_volume_page.locators.MODAL_ADD_NUMBER.wait_to_be_visible()
        self.number_volume_page.locators.MODAL_ADD_NUMBER_TITLE.to_contain_text("Добавление номера зоны ABC")
        self.number_volume_page.check_add_new_number_elements(num_type="abc")

        new_number = str(int(phones_data[0]["MSISDN"]) + 1)
        new_number_2 = str(int(phones_data[0]["MSISDN"]) + 2)
        file_name = "add_numbers.csv"
        file_path = self.number_volume_page.create_csv_file_to_upload_number(file_name, [new_number, new_number_2])
        remove_file_from_download_folder.append(file_path)
        with self.number_volume_page.page.expect_file_chooser() as fc_info:
            self.number_volume_page.locators.LOAD_NUMBER_BUTTON.click()
        file_chooser = fc_info.value
        file_chooser.set_files(file_path)
        self.number_volume_page.locators.DELETE_FILE_BUTTON.wait_to_be_visible()
        self.number_volume_page.locators.UPLOADED_FILE_NAME.wait_to_have_text(file_name)
        self.number_volume_page.locators.START_PHONE_NUMBER.to_have_value(new_number)
        self.number_volume_page.locators.COUNT_PHONE_NUMBER.to_have_value("2")
        self.number_volume_page.locators.CHOOSE_COMMUTATOR_BLOCK.wait_to_have_text("Коммутатор_ABC")
        self.number_volume_page.locators.CHOOSE_COMMUTATOR_BLOCK.check_attribute_by_value("disabled", "disabled")
        self.number_volume_page.locators.CHOSEN_CATEGORY_FIELD.wait_to_have_text("Телефония")
        self.number_volume_page.locators.CHOSEN_CATEGORY_BLOCK.check_attribute_by_value("disabled", "disabled")
        self.number_volume_page.locators.NUMBER_TYPE_FIELD.click()
        self.number_volume_page.locators.NUMBER_TYPE_OPTIONS[1].to_contain_text("Фиксированная")
        self.number_volume_page.locators.NUMBER_TYPE_OPTIONS[1].click()
        self.number_volume_page.locators.OPERATOR_FIELD.click()
        self.number_volume_page.locators.OPERATOR_OPTIONS[0].click()
        self.number_volume_page.check_all_checkboxes_turned_off()
        self.number_volume_page.locators.ADD_BUTTON.click()

        (
            self.number_volume_page.locators.MODAL_BODY_TEXT[0].wait_to_have_text(
                "Не выбран ни один шаблон классификации. Номера будут загружены как обычные. Всё равно выполнить?"
            )
        )
        self.number_volume_page.locators.FIRST_BTN_CONFIRMATION.click()
        (
            self.number_volume_page.locators.MODAL_BODY_TEXT[0].wait_to_have_text(
                "Операция выполняется в фоновом режиме. Её выполнение можно отследить в мониторе операций."
            )
        )
        self.number_volume_page.locators.OK_BTN.click()
        self.number_volume_page.locators.REFRESH_BTN.click()
        self.number_volume_page.locators.MSISDN_HEADER.click()
        delay(1, reason="Время на сортировку в сторону увеличения")
        self.number_volume_page.locators.MSISDN_HEADER.click()
        delay(1, reason="Время на сортировку в сторону уменьшения")
        self.number_volume_page.locators.PHONE_NUMBERS[1].wait_to_have_text(new_number)
        self.number_volume_page.locators.PHONE_NUMBERS[0].wait_to_have_text(new_number_2)
        self.number_volume_page.locators.PHONE_NUMBERS_CLASS[1].wait_to_have_text("Обычный")
        self.number_volume_page.locators.PHONE_NUMBERS_CLASS[0].wait_to_have_text("Обычный")
        self.number_volume_page.locators.PHONE_NUMBERS_COMMUTATORS_ABC[1].wait_to_have_text("Коммутатор_ABC")
        self.number_volume_page.locators.PHONE_NUMBERS_COMMUTATORS_ABC[0].wait_to_have_text("Коммутатор_ABC")
        self.number_volume_page.locators.PHONE_NUMBERS_STANDARDS_ABC[1].wait_to_have_text("PSTN")
        self.number_volume_page.locators.PHONE_NUMBERS_STANDARDS_ABC[0].wait_to_have_text("PSTN")
        self.number_volume_page.locators.PHONE_NUMBERS_OPERATORS_ABC[1].wait_to_have_text("NEXIGN")
        self.number_volume_page.locators.PHONE_NUMBERS_OPERATORS_ABC[0].wait_to_have_text("NEXIGN")
        self.number_volume_page.locators.PHONE_NUMBERS_TYPES_ABC[1].wait_to_have_text("Фиксированная")
        self.number_volume_page.locators.PHONE_NUMBERS_TYPES_ABC[0].wait_to_have_text("Фиксированная")

    @allure.title("Добавление номерной емкости (ABC, с 9)")
    @allure.id(582580)
    @allure.tag("can_auth", "success")
    @pytest.mark.regress
    def test_add_number_abc_with_nine(self, api_request_auth_context: APIRequestContext) -> None:
        phone_numbers = PhoneNumbersRequests(api_request_auth_context)
        phones = phone_numbers.get_phone_numbers(type_def=False, num_sort="-MSISDN")
        phones_data = phones.json()["items"]
        self.home_page_lis.NUMBER_VOLUME_BTN.wait_to_be_visible()
        self.home_page_lis.NUMBER_VOLUME_BTN.click()
        self.number_volume_page.locators.TITLE.to_contain_text("Номерная ёмкость")
        self.number_volume_page.locators.ZONE_TYPE[1].click()
        self.number_volume_page.locators.ZONE_TYPE[1].to_have_css("background", re.compile(r"rgb\(69, 166, 0\)"))
        self.number_volume_page.locators.ADD_NUMBER_BTN.click()
        self.number_volume_page.locators.MODAL_ADD_NUMBER.wait_to_be_visible()
        self.number_volume_page.locators.MODAL_ADD_NUMBER_TITLE.to_contain_text("Добавление номера зоны ABC")

        new_number = str(int(phones_data[0]["MSISDN"]) + 1).replace("9", "1")
        wrong_number = f"9{new_number[1:]}"
        self.number_volume_page.locators.START_PHONE_NUMBER.fill(wrong_number)

        self.number_volume_page.check_add_new_number_elements(num_type="abc")
        self.number_volume_page.locators.CHOSEN_CATEGORY_FIELD.to_contain_text("Дополнительный")
        self.number_volume_page.locators.NUMBER_TYPE_FIELD.to_contain_text("Городская")
        self.number_volume_page.locators.NUMBER_TYPE_FIELD.click()
        self.number_volume_page.locators.NUMBER_TYPE_OPTIONS[1].to_contain_text("Фиксированная")
        self.number_volume_page.locators.NUMBER_TYPE_OPTIONS[1].click()
        self.number_volume_page.locators.NUMBER_TYPE_FIELD.to_contain_text("Фиксированная")
        self.number_volume_page.locators.CHOSEN_CATEGORY_FIELD.to_contain_text("Телефония")

        self.number_volume_page.locators.START_PHONE_NUMBER.to_have_value(wrong_number[1:])
        self.number_volume_page.locators.START_PHONE_NUMBER.fill("1234567890")
        self.number_volume_page.locators.START_PHONE_NUMBER.to_have_value("1234567890")

    @allure.title("Перевод номера в состояние 'Зарезервирован'")
    @allure.id(581483)
    @allure.tag("can_auth", "success")
    @pytest.mark.regress
    @pytest.mark.smoke
    def test_reserve_number(self, api_request_auth_context: APIRequestContext) -> None:
        phone_numbers = PhoneNumbersRequests(api_request_auth_context)
        phones = phone_numbers.get_phone_numbers(status_id=[1], state_id=[2], is_reserved="false")
        suitable_number = phones.json()["items"][0]["MSISDN"]
        self.home_page_lis.NUMBER_VOLUME_BTN.wait_to_be_visible()
        self.home_page_lis.NUMBER_VOLUME_BTN.click()
        self.number_volume_page.locators.TITLE.to_contain_text("Номерная ёмкость")
        self.number_volume_page.locators.REFRESH_BTN.click()

        self.number_volume_page.locators.SEARCH_BTN.click()
        self.number_volume_page.locators.MSISDN_FILTER_BTN.click()
        self.number_volume_page.locators.MSISDN_OPTION_VALUE.click()
        self.number_volume_page.locators.MSISDN_FILTER_INPUT.fill(suitable_number)
        self.number_volume_page.locators.FILTER_SEARCH_BTN.click()
        self.number_volume_page.locators.PHONE_NUMBERS.wait_to_have_count(1)
        self.number_volume_page.locators.PHONE_NUMBERS[0].wait_to_have_text(suitable_number)
        self.number_volume_page.locators.PHONE_NUMBERS_STATUS[0].wait_to_have_text("Свободен")
        self.number_volume_page.locators.PHONE_NUMBERS_STATE[0].wait_to_have_text("Открыт для исп.")

        self.number_volume_page.locators.LINE_CHECKBOXES[0].click()
        delay(0.3, reason="Кнопка не активна доли секунды, даже в случае enabled")
        self.number_volume_page.locators.RESERVE_BTN.click()

        self.number_volume_page.locators.MODAL[0].wait_to_be_visible()
        self.number_volume_page.locators.MODAL_TITLE[0].to_contain_text("Резервирование номеров")
        self.number_volume_page.locators.MODAL_BODY_INPUT.fill("Autotest_reservation 1!%&,.")
        self.number_volume_page.locators.MODAL_BODY_INPUT.to_have_value("Autotest_reservation 1!%&,.")
        self.number_volume_page.locators.FIRST_BTN[0].to_contain_text("Зарезервировать")
        self.number_volume_page.locators.SECOND_BTN[0].to_contain_text("Отменить")
        self.number_volume_page.locators.FIRST_BTN[0].click()

        self.number_volume_page.locators.MODAL[1].wait_to_be_visible()
        self.number_volume_page.locators.MODAL_TITLE[1].to_contain_text("Подтверждение операции")
        (
            self.number_volume_page.locators.MODAL_BODY_TEXT[0].to_contain_text(
                ' Операция "Зарезервировать" будет выполнена для выбранных записей (1). Выполнить операцию?'
            )
        )
        self.number_volume_page.locators.FIRST_BTN[1].click()

        self.number_volume_page.locators.PHONE_NUMBERS[0].wait_to_have_text(suitable_number)
        self.number_volume_page.locators.PHONE_NUMBERS_STATUS[0].wait_to_have_text("Свободен")
        self.number_volume_page.locators.PHONE_NUMBERS_STATE[0].wait_to_have_text("Зарезервирован")
