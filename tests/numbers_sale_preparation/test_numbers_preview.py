import pytest
import allure
from playwright.sync_api import Page, APIRequestContext
import re

from api.requests.lis_requests.phone_numbers import PhoneNumbersRequests
from common.helpers.download_helper import CheckFile
from common.helpers.env_helper import BASE_URL_LIS
from common.helpers.time_helpers import delay
from pages.base_page import BasePage
from pages.lis_pages.number_volume_page import NumberVolumePage
from pages.locators.lis_locators.home_elements_lis import HomeElementsLis


@allure.epic("E2E_11 Подготовка номеров к продаже")
@allure.suite("E2E_11 Подготовка номеров к продаже")
class TestSaleNumbersPreview:
    @pytest.fixture(autouse=True)
    def setup(self, stand_login_lis: Page):
        self.base_page = BasePage(stand_login_lis)
        self.home_page_lis = HomeElementsLis(stand_login_lis)
        self.number_volume_page = NumberVolumePage(stand_login_lis)

    @allure.title("Просмотр номеров")
    @allure.id(580593)
    @allure.description("Проверка отображения номеров и элементов страницы Номерная емкость")
    @allure.tag("can_auth", "success")
    def test_numbers_preview(self, api_request_auth_context: APIRequestContext):
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
        phones = phone_numbers.get_phone_numbers(BASE_URL_LIS)
        self.number_volume_page.locators.NUMBERS_COUNTER.to_contain_text("Всего*")
        self.number_volume_page.locators.NUMBERS_COUNTER.to_contain_text(str(phones.json()['listInfo']['count']))
        self.number_volume_page.locators.LINE_CHECKBOXES[0].click()
        self.number_volume_page.locators.LINE_CHECKBOXES[10].click()
        self.number_volume_page.locators.TABLE_LINE[0].to_have_class(class_name=re.compile(r"js-selected"))
        self.number_volume_page.locators.TABLE_LINE[10].to_have_class(class_name=re.compile(r"js-selected"))

    @allure.title("Просмотр номеров (Выбор зоны нумерации)")
    @allure.id(580669)
    @allure.description("Проверка отображения номеров для разных зон нумерации")
    @allure.tag("can_auth", "success")
    def test_numbers_zone_preview(self, api_request_auth_context: APIRequestContext):
        self.home_page_lis.NUMBER_VOLUME_BTN.click()
        self.number_volume_page.locators.TITLE.to_contain_text("Номерная ёмкость")
        self.number_volume_page.locators.ZONE_TYPE[0].click()
        self.number_volume_page.locators.REFRESH_BTN.click()

        phone_numbers = PhoneNumbersRequests(api_request_auth_context)
        phones_1 = phone_numbers.get_phone_numbers(BASE_URL_LIS)
        phones_data_1 = phones_1.json()['items']
        self.number_volume_page.locators.PHONE_NUMBERS[0].wait_to_be_visible()
        self.number_volume_page.locators.PHONE_NUMBERS[0].to_contain_text(phones_data_1[0]['MSISDN'])
        self.number_volume_page.locators.PHONE_NUMBERS[10].to_contain_text(phones_data_1[10]['MSISDN'])

        self.number_volume_page.locators.ZONE_TYPE[1].click()
        self.number_volume_page.locators.REFRESH_BTN.click()

        phones_2 = phone_numbers.get_phone_numbers(server_url=BASE_URL_LIS, type_def=False)
        phones_data_2 = phones_2.json()['items']
        self.number_volume_page.locators.PHONE_NUMBERS[0].wait_to_have_text(phones_data_2[0]['MSISDN'])
        self.number_volume_page.locators.PHONE_NUMBERS[10].wait_to_have_text(phones_data_2[10]['MSISDN'])

        self.number_volume_page.locators.LINK_NUMBER_BTN.wait_to_be_visible()
        self.number_volume_page.locators.REFRESH_BTN.wait_to_be_visible()
        self.number_volume_page.locators.SEARCH_BTN.wait_to_be_visible()

        self.number_volume_page.locators.NUMBERS_COUNTER.to_contain_text("Всего*")
        self.number_volume_page.locators.NUMBERS_COUNTER.to_contain_text(str(phones_2.json()['listInfo']['count']))

        self.number_volume_page.locators.LINE_CHECKBOXES[0].click()
        self.number_volume_page.locators.LINE_CHECKBOXES[10].click()
        self.number_volume_page.locators.TABLE_LINE[0].to_have_class(class_name=re.compile(r"js-selected"))
        self.number_volume_page.locators.TABLE_LINE[10].to_have_class(class_name=re.compile(r"js-selected"))

    @allure.title("Просмотр номеров (Выгрузка в файл)")
    @allure.id(580927)
    @allure.description("Проверка сохранения данных по номерам в Excel")
    @allure.tag("can_auth", "success")
    def test_numbers_download(self, api_request_auth_context: APIRequestContext, remove_file_from_download_folder):
        phone_numbers = PhoneNumbersRequests(api_request_auth_context)
        phones = phone_numbers.get_phone_numbers(BASE_URL_LIS)
        phones_data = phones.json()['items']
        self.home_page_lis.NUMBER_VOLUME_BTN.click()
        self.number_volume_page.locators.TITLE.to_contain_text("Номерная ёмкость")
        self.number_volume_page.locators.REFRESH_BTN.click()

        self.number_volume_page.locators.CHECK_ALL_BTN.click()
        delay(1, reason="Кнопка не активна доли секунды, даже в случае enabled")
        self.number_volume_page.locators.DOWNLOAD_BTN.hover()
        self.number_volume_page.locators.DOWNLOAD_BTN.click()
        self.number_volume_page.locators.MODAL.wait_to_be_visible()
        self.number_volume_page.locators.MODAL_TITLE.to_contain_text("Подтверждение операции")
        with self.number_volume_page.page.expect_download(timeout=20000) as download_info:
            self.number_volume_page.locators.FIRST_BTN.click()
        download = download_info.value
        file_name = download.suggested_filename
        self.file_check = CheckFile(file_name)
        download.save_as(self.file_check.path)
        remove_file_from_download_folder.append(file_name)
        self.file_check.check_excel_file_group_of_fields_contains([[1, 1], [11, 1]],
                                                                  [phones_data[0]['MSISDN'],
                                                                   phones_data[10]['MSISDN']])

    @allure.title("Просмотр номеров (История номера)")
    @allure.id(580670)
    @allure.tag("can_auth", "success")
    def test_numbers_history(self, api_request_auth_context: APIRequestContext):
        phone_numbers = PhoneNumbersRequests(api_request_auth_context)
        phones = phone_numbers.get_phone_numbers(BASE_URL_LIS)
        phones_data = phones.json()['items']
        self.home_page_lis.NUMBER_VOLUME_BTN.click()
        self.number_volume_page.locators.TITLE.to_contain_text("Номерная ёмкость")
        self.number_volume_page.locators.REFRESH_BTN.click()

        self.number_volume_page.locators.TABLE_LINE.wait_elements_visible(10)
        self.number_volume_page.locators.LINE_CHECKBOXES.click(0)
        self.number_volume_page.locators.HISTORY_BTN.wait_to_be_enabled()
        delay(1, reason="Кнопка не активна доли секунды, даже в случае enabled")
        self.number_volume_page.locators.HISTORY_BTN.click()

        self.number_volume_page.locators.MODAL.wait_to_be_visible()
        self.number_volume_page.locators.MODAL_TITLE.to_contain_text(f"История по MSISDN {phones_data[0]['MSISDN']}")
        self.number_volume_page.locators.REFRESH_HISTORY_BTN.wait_to_be_visible()
        self.number_volume_page.locators.HISTORY_TYPE_BTN[0].to_contain_text("LIS")
        self.number_volume_page.locators.HISTORY_TYPE_BTN[1].to_contain_text("Greenfield")
        self.number_volume_page.locators.HISTORY_TYPE_BTN[2].to_contain_text("Операций")

    @allure.title("Просмотр номеров (История номера, несколько номеров)")
    @allure.id(580671)
    @allure.tag("can_auth", "success")
    def test_history_pair_of_numbers(self):
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
        self.number_volume_page.locators.MODAL.not_to_be_visible()

    @allure.title("Просмотр номеров (Фильтрация списка)")
    @allure.id(581638)
    @allure.tag("can_auth", "success")
    def test_filter_numbers(self, api_request_auth_context: APIRequestContext):
        phone_numbers = PhoneNumbersRequests(api_request_auth_context)
        phones = phone_numbers.get_phone_numbers(BASE_URL_LIS)
        phones_data = phones.json()['items']
        self.home_page_lis.NUMBER_VOLUME_BTN.wait_to_be_visible()
        self.home_page_lis.NUMBER_VOLUME_BTN.click()
        self.number_volume_page.locators.TITLE.to_contain_text("Номерная ёмкость")
        self.number_volume_page.locators.REFRESH_BTN.click()

        self.number_volume_page.locators.TABLE_LINE.wait_elements_visible(10)
        self.number_volume_page.locators.SEARCH_BTN.click()
        self.number_volume_page.check_search_elements()
        self.number_volume_page.locators.MSISDN_FILTER_BTN.click()
        self.number_volume_page.locators.MSISDN_OPTION_VALUE.click()
        self.number_volume_page.locators.MSISDN_FILTER_INPUT.fill(phones_data[2]['MSISDN'])
        self.number_volume_page.locators.FILTER_SEARCH_BTN.click()
        self.number_volume_page.locators.PHONE_NUMBERS.wait_to_have_count(1)
        self.number_volume_page.locators.PHONE_NUMBERS[0].wait_to_have_text(phones_data[2]['MSISDN'])

        self.number_volume_page.locators.HIDE_FILTER_BTN.click()
        self.number_volume_page.locators.FILTER_SEARCH_BTN.not_to_be_visible()
        self.number_volume_page.locators.PHONE_NUMBERS.wait_to_have_count(1)
        self.number_volume_page.locators.PHONE_NUMBERS[0].wait_to_have_text(phones_data[2]['MSISDN'])

        self.number_volume_page.locators.SEARCH_BTN.click()
        self.number_volume_page.locators.MSISDN_SELECTED_OPTIONS.to_contain_text("Точное значение")
        self.number_volume_page.locators.MSISDN_FILTER_INPUT.to_have_value(phones_data[2]['MSISDN'])

        self.number_volume_page.page.reload(wait_until="domcontentloaded")
        self.number_volume_page.locators.MSISDN_SELECTED_OPTIONS.to_contain_text("Точное значение")
        self.number_volume_page.locators.MSISDN_FILTER_INPUT.to_have_value(phones_data[2]['MSISDN'])

        self.number_volume_page.locators.FILTER_SEARCH_BTN.click()
        self.number_volume_page.locators.PHONE_NUMBERS.wait_to_have_count(1)
        self.number_volume_page.locators.PHONE_NUMBERS[0].wait_to_have_text(phones_data[2]['MSISDN'])

        self.number_volume_page.locators.LINK_NUMBER_FILTER_BTN.click()
        self.number_volume_page.locators.LINK_NUMBER_OPTION_INTERVAL.click()
        self.number_volume_page.locators.LINK_NUMBER_SELECTED_OPTIONS.to_contain_text("По диапазону")
        self.number_volume_page.locators.COMMENT_FILTER_BTN.click()
        self.number_volume_page.locators.COMMENT_OPTION_NOT_FILLED.click()
        self.number_volume_page.locators.COMMENT_SELECTED_OPTIONS.to_contain_text("Не заполнен")

        self.number_volume_page.locators.CLEAR_FILTER_BTN.click()
        phones_2 = phone_numbers.get_phone_numbers(BASE_URL_LIS)
        phones_data_2 = phones_2.json()['items']
        self.number_volume_page.locators.PHONE_NUMBERS[0].wait_to_have_text(phones_data_2[0]['MSISDN'])
        self.number_volume_page.locators.PHONE_NUMBERS[2].wait_to_have_text(phones_data_2[2]['MSISDN'])

    @allure.title("Ввод номера в эксплуатацию")
    @allure.id(580955)
    @allure.tag("can_auth", "success")
    def test_make_number_set_in_use(self, api_request_auth_context: APIRequestContext):
        phone_numbers = PhoneNumbersRequests(api_request_auth_context)
        phones = phone_numbers.get_phone_numbers(BASE_URL_LIS, status_id=[3])
        phones_data = phones.json()['items']
        self.home_page_lis.NUMBER_VOLUME_BTN.wait_to_be_visible()
        self.home_page_lis.NUMBER_VOLUME_BTN.click()
        self.number_volume_page.locators.TITLE.to_contain_text("Номерная ёмкость")
        self.number_volume_page.locators.REFRESH_BTN.click()

        self.number_volume_page.locators.SEARCH_BTN.click()
        self.number_volume_page.locators.STATUS_FILTER_BTN.click()
        self.number_volume_page.locators.STATUS_OPTION_UNAVAILABLE.click()
        self.number_volume_page.locators.FILTER_SEARCH_BTN.click()
        self.number_volume_page.locators.TABLE_LINE.wait_elements_visible(10)
        self.number_volume_page.locators.PHONE_NUMBERS[0].wait_to_have_text(phones_data[0]['MSISDN'])

        self.number_volume_page.locators.LINE_CHECKBOXES[0].click()
        delay(1, reason="Кнопка не активна доли секунды, даже в случае enabled")
        self.number_volume_page.locators.SET_IN_USE_BTN.click()

        self.number_volume_page.locators.MODAL.wait_to_be_visible()
        self.number_volume_page.locators.MODAL_TITLE.to_contain_text("Подтверждение операции")
        self.number_volume_page.locators.FIRST_BTN.click()

        self.number_volume_page.locators.CLEAR_FILTER_BTN.click()
        self.number_volume_page.locators.STATUS_FILTER_BTN.click()
        self.number_volume_page.locators.STATUS_OPTION_FREE.click()
        self.number_volume_page.locators.FILTER_SEARCH_BTN.click()
        self.number_volume_page.locators.DATE_CHANGE_STATUS_HEADER.click()
        delay(1, reason="Время на сортировку в сторону увеличения")
        self.number_volume_page.locators.DATE_CHANGE_STATUS_HEADER.click()
        delay(1, reason="Время на сортировку в сторону уменьшения")
        self.number_volume_page.locators.PHONE_NUMBERS[0].wait_to_have_text(phones_data[0]['MSISDN'])
        self.number_volume_page.locators.PHONE_NUMBERS_STATUS[0].wait_to_have_text("Свободен")
        self.number_volume_page.locators.PHONE_NUMBERS_STATE[0].wait_to_have_text("Открыт для исп.")

    @allure.title("Вывод номера из эксплуатации")
    @allure.id(580942)
    @allure.tag("can_auth", "success")
    def test_make_number_out_of_use(self, api_request_auth_context: APIRequestContext):
        phone_numbers = PhoneNumbersRequests(api_request_auth_context)
        phones = phone_numbers.get_phone_numbers(BASE_URL_LIS, status_id=[1], state_id=[2], num_sort="-statusDate")
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

        self.number_volume_page.locators.LINE_CHECKBOXES[0].click()
        delay(1, reason="Кнопка не активна доли секунды, даже в случае enabled")
        self.number_volume_page.locators.SET_OUT_USE_BTN.click()

        self.number_volume_page.locators.MODAL.wait_to_be_visible()
        self.number_volume_page.locators.MODAL_TITLE.to_contain_text("Подтверждение операции")
        (self.number_volume_page.locators.MODAL_BODY_TEXT.
         to_contain_text(' Операция "Исключить" будет выполнена для выбранных записей (1). Выполнить операцию?'))
        self.number_volume_page.locators.FIRST_BTN.click()

        self.number_volume_page.locators.PHONE_NUMBERS[0].wait_to_have_text(phones_data[0]['MSISDN'])
        self.number_volume_page.locators.PHONE_NUMBERS_STATUS[0].wait_to_have_text("Недоступен")
        self.number_volume_page.locators.PHONE_NUMBERS_STATE[0].wait_to_have_text("Закрыт для исп.")

    @allure.title("Вывод номера из карантина")
    @allure.id(581494)
    @allure.tag("can_auth", "success")
    def test_make_number_out_of_quarantine(self, api_request_auth_context: APIRequestContext):
        phone_numbers = PhoneNumbersRequests(api_request_auth_context)
        phones = phone_numbers.get_phone_numbers(BASE_URL_LIS, status_id=[1], state_id=[4])
        phones_data = phones.json()['items']
        suitable_number = [item['MSISDN'] for item in phones_data if item['expirationReserveDate'] is not None][0]
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
        delay(1, reason="Кнопка не активна доли секунды, даже в случае enabled")
        self.number_volume_page.locators.SET_OUT_OF_ISOLATION_BTN.click()

        self.number_volume_page.locators.MODAL.wait_to_be_visible()
        self.number_volume_page.locators.MODAL_TITLE.to_contain_text("Подтверждение операции")
        (self.number_volume_page.locators.MODAL_BODY_TEXT.
         to_contain_text(' Операция "Вывод из карантина" будет выполнена для выбранных записей (1). Выполнить операцию?'))
        self.number_volume_page.locators.FIRST_BTN.click()

        self.number_volume_page.locators.PHONE_NUMBERS[0].wait_to_have_text(suitable_number)
        self.number_volume_page.locators.PHONE_NUMBERS_STATUS[0].wait_to_have_text("Свободен")
        self.number_volume_page.locators.PHONE_NUMBERS_STATE[0].wait_to_have_text("Открыт для исп.")

    @allure.title("Добавление номерной емкости (DEF)")
    @allure.id(582071)
    @allure.tag("can_auth", "success")
    def test_add_number_def(self, api_request_auth_context: APIRequestContext):
        phone_numbers = PhoneNumbersRequests(api_request_auth_context)
        phones = phone_numbers.get_phone_numbers(BASE_URL_LIS, num_sort="-MSISDN")
        phones_data = phones.json()['items']
        self.home_page_lis.NUMBER_VOLUME_BTN.wait_to_be_visible()
        self.home_page_lis.NUMBER_VOLUME_BTN.click()
        self.number_volume_page.locators.TITLE.to_contain_text("Номерная ёмкость")
        self.number_volume_page.locators.ZONE_TYPE[0].to_have_css("background", re.compile(r'rgb\(69, 166, 0\)'))
        self.number_volume_page.locators.ADD_NUMBER_BTN.click()
        self.number_volume_page.locators.MODAL_ADD_NUMBER.wait_to_be_visible()
        self.number_volume_page.locators.MODAL_ADD_NUMBER_TITLE.to_contain_text("Добавление номера зоны DEF")
        self.number_volume_page.check_add_new_number_elements()

        self.number_volume_page.locators.START_PHONE_NUMBER.fill("9876543210")
        self.number_volume_page.locators.START_PHONE_NUMBER.to_have_value("9876543210")

        new_number = str(int(phones_data[0]["MSISDN"]) + 1)
        new_number_2 = str(int(phones_data[0]["MSISDN"]) + 2)
        self.number_volume_page.locators.START_PHONE_NUMBER.fill(new_number + "2")
        self.number_volume_page.locators.COUNT_PHONE_NUMBER.fill("2")
        self.number_volume_page.locators.CHOOSE_COMMUTATOR_BTN.click()
        self.number_volume_page.locators.COMMUTATOR_TYPE_NAMES[0].click(click_count=2)
        self.number_volume_page.locators.NUMBER_TYPE_FIELD.click()
        self.number_volume_page.locators.NUMBER_TYPE_OPTIONS[2].to_contain_text("Федеральная")
        self.number_volume_page.locators.NUMBER_TYPE_OPTIONS[2].click()
        self.number_volume_page.locators.OPERATOR_FIELD.click()
        self.number_volume_page.locators.OPERATOR_OPTIONS[0].click()
        self.number_volume_page.locators.NUMBER_TYPE_ALL_CHECKBOX.click()
        delay(0.5, reason="Время на отключение чекбокса")
        check_box_html = self.number_volume_page.locators.NUMBER_TYPE_ALL_CHECKBOX.inner_html()
        assert "checkbox_checked" not in check_box_html and "n-check-checkbox_partially" not in check_box_html, \
            "Чекбокс не отключен"

        self.number_volume_page.locators.ADD_BUTTON.wait_to_be_visible()
        self.number_volume_page.locators.CANCEL_ADD_NUMBER.wait_to_be_visible()
        self.number_volume_page.locators.ADD_BUTTON.click()
        self.number_volume_page.locators.START_PHONE_NUMBER.to_have_css("color", re.compile(r'rgb\(192, 75, 49\)'))
        self.number_volume_page.locators.START_PHONE_NUMBER.fill(new_number)

        self.number_volume_page.locators.ADD_BUTTON.click()
        self.number_volume_page.locators.CANCEL_ADD_NUMBER.not_to_be_visible()

        (self.number_volume_page.locators.MODAL_BODY_TEXT.
         to_contain_text("Операция выполняется в фоновом режиме. Её выполнение можно отследить в мониторе операций."))
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
