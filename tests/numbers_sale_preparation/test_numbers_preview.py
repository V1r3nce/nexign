import pytest
import allure
from playwright.sync_api import Page, APIRequestContext
import re

from api.requests.lis_requests.phone_numbers import PhoneNumbersRequests
from common.helpers.download_helper import CheckFile
from common.helpers.env_helper import BASE_URL_LIS
from common.helpers.time_helpers import delay
from pages.base_page import BasePage
from pages.locators.lis_locators.home_elements_lis import HomeElementsLis
from pages.locators.lis_locators.number_volume_elements import NumberVolumeElementsLis


@allure.epic("E2E_11 Подготовка номеров к продаже")
@allure.suite("E2E_11 Подготовка номеров к продаже")
class TestSaleNumbersPreview:
    @pytest.fixture(autouse=True)
    def setup(self, stand_login_lis: Page):
        self.base_page = BasePage(stand_login_lis)
        self.home_page_lis = HomeElementsLis(stand_login_lis)
        self.number_volume_page = NumberVolumeElementsLis(stand_login_lis)

    @allure.title("Просмотр номеров")
    @allure.id(580593)
    @allure.description("Проверка отображения номеров и элементов страницы Номерная емкость")
    @allure.tag("can_auth", "success")
    def test_numbers_preview(self, api_request_auth_context: APIRequestContext):
        self.home_page_lis.NUMBER_VOLUME_BTN.click()
        self.number_volume_page.TITLE.to_contain_text("Номерная ёмкость")
        self.number_volume_page.PAGE_TABS[0].wait_to_have_text("Список MSISDN")
        self.number_volume_page.RESERVE_BTN.wait_to_be_visible()
        self.number_volume_page.LINK_NUMBER_BTN.wait_to_be_visible()
        self.number_volume_page.REFRESH_BTN.wait_to_be_visible()
        self.number_volume_page.SEARCH_BTN.wait_to_be_visible()

        self.number_volume_page.REFRESH_BTN.click()
        self.number_volume_page.PHONE_NUMBERS[0].wait_to_be_visible()
        self.number_volume_page.PHONE_NUMBERS[10].wait_to_be_visible()
        self.number_volume_page.NUMBERS_COUNTER.wait_to_be_visible()
        phone_numbers = PhoneNumbersRequests(api_request_auth_context)
        phones = phone_numbers.get_phone_numbers(BASE_URL_LIS)
        self.number_volume_page.NUMBERS_COUNTER.to_contain_text("Всего*")
        self.number_volume_page.NUMBERS_COUNTER.to_contain_text(str(phones.json()['listInfo']['count']))
        self.number_volume_page.LINE_CHECKBOXES[0].click()
        self.number_volume_page.LINE_CHECKBOXES[10].click()
        self.number_volume_page.TABLE_LINE[0].to_have_class(class_name=re.compile(r"js-selected"))
        self.number_volume_page.TABLE_LINE[10].to_have_class(class_name=re.compile(r"js-selected"))

    @allure.title("Просмотр номеров (Выбор зоны нумерации)")
    @allure.id(580669)
    @allure.description("Проверка отображения номеров для разных зон нумерации")
    @allure.tag("can_auth", "success")
    def test_numbers_zone_preview(self, api_request_auth_context: APIRequestContext):
        self.home_page_lis.NUMBER_VOLUME_BTN.click()
        self.number_volume_page.TITLE.to_contain_text("Номерная ёмкость")
        self.number_volume_page.ZONE_TYPE[0].click()
        self.number_volume_page.REFRESH_BTN.click()

        phone_numbers = PhoneNumbersRequests(api_request_auth_context)
        phones_1 = phone_numbers.get_phone_numbers(BASE_URL_LIS)
        phones_data_1 = phones_1.json()['items']
        self.number_volume_page.PHONE_NUMBERS[0].wait_to_be_visible()
        self.number_volume_page.PHONE_NUMBERS[0].to_contain_text(phones_data_1[0]['MSISDN'])
        self.number_volume_page.PHONE_NUMBERS[10].to_contain_text(phones_data_1[10]['MSISDN'])

        self.number_volume_page.ZONE_TYPE[1].click()
        self.number_volume_page.REFRESH_BTN.click()

        phones_2 = phone_numbers.get_phone_numbers(server_url=BASE_URL_LIS, type_def=False)
        phones_data_2 = phones_2.json()['items']
        self.number_volume_page.PHONE_NUMBERS[0].wait_to_have_text(phones_data_2[0]['MSISDN'])
        self.number_volume_page.PHONE_NUMBERS[10].wait_to_have_text(phones_data_2[10]['MSISDN'])

        self.number_volume_page.LINK_NUMBER_BTN.wait_to_be_visible()
        self.number_volume_page.REFRESH_BTN.wait_to_be_visible()
        self.number_volume_page.SEARCH_BTN.wait_to_be_visible()

        self.number_volume_page.NUMBERS_COUNTER.to_contain_text("Всего*")
        self.number_volume_page.NUMBERS_COUNTER.to_contain_text(str(phones_2.json()['listInfo']['count']))

        self.number_volume_page.LINE_CHECKBOXES[0].click()
        self.number_volume_page.LINE_CHECKBOXES[10].click()
        self.number_volume_page.TABLE_LINE[0].to_have_class(class_name=re.compile(r"js-selected"))
        self.number_volume_page.TABLE_LINE[10].to_have_class(class_name=re.compile(r"js-selected"))

    @pytest.mark.skip("В Selenoid не доступен скачанный файл, ждем подключения Moon для проверки работоспособности")
    @allure.title("Просмотр номеров (Выгрузка в файл)")
    @allure.id(580927)
    @allure.description("Проверка сохранения данных по номерам в Excel")
    @allure.tag("can_auth", "success")
    def test_numbers_download(self, api_request_auth_context: APIRequestContext, remove_file_from_download_folder):
        phone_numbers = PhoneNumbersRequests(api_request_auth_context)
        phones = phone_numbers.get_phone_numbers(BASE_URL_LIS)
        phones_data = phones.json()['items']
        self.home_page_lis.NUMBER_VOLUME_BTN.click()
        self.number_volume_page.TITLE.to_contain_text("Номерная ёмкость")
        self.number_volume_page.REFRESH_BTN.click()

        self.number_volume_page.CHECK_ALL_BTN.click()
        delay(1, reason="Кнопка не активна доли секунды, даже в случае enabled")
        self.number_volume_page.DOWNLOAD_BTN.hover()
        self.number_volume_page.DOWNLOAD_BTN.click()
        self.number_volume_page.MODAL.wait_to_be_visible()
        self.number_volume_page.MODAL_TITLE.to_contain_text("Подтверждение операции")
        with self.number_volume_page.page.expect_download(timeout=20000) as download_info:
            self.number_volume_page.FIRST_BTN.click()
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
        self.number_volume_page.TITLE.to_contain_text("Номерная ёмкость")
        self.number_volume_page.REFRESH_BTN.click()

        self.number_volume_page.LINE_CHECKBOXES.wait_to_be_visible(10)
        self.number_volume_page.LINE_CHECKBOXES.click(0)
        self.number_volume_page.HISTORY_BTN.wait_to_be_enabled()
        delay(1, reason="Кнопка не активна доли секунды, даже в случае enabled")
        self.number_volume_page.HISTORY_BTN.click()

        self.number_volume_page.MODAL.wait_to_be_visible()
        self.number_volume_page.MODAL_TITLE.to_contain_text(f"История по MSISDN {phones_data[0]['MSISDN']}")
        self.number_volume_page.REFRESH_HISTORY_BTN.wait_to_be_visible()
        self.number_volume_page.HISTORY_TYPE_BTN[0].to_contain_text("LIS")
        self.number_volume_page.HISTORY_TYPE_BTN[1].to_contain_text("Greenfield")
        self.number_volume_page.HISTORY_TYPE_BTN[2].to_contain_text("Операций")

    @allure.title("Просмотр номеров (История номера, несколько номеров)")
    @allure.id(580671)
    @allure.tag("can_auth", "success")
    def test_history_pair_of_numbers(self):
        self.home_page_lis.NUMBER_VOLUME_BTN.click()
        self.number_volume_page.TITLE.to_contain_text("Номерная ёмкость")
        self.number_volume_page.REFRESH_BTN.click()

        self.number_volume_page.LINE_CHECKBOXES.wait_to_be_visible(10)
        self.number_volume_page.LINE_CHECKBOXES.click(0)
        self.number_volume_page.LINE_CHECKBOXES.click(1)
        self.number_volume_page.HISTORY_BTN.check_attribute_by_value("disabled", "disabled")

        delay(1, reason="Кнопка не активна доли секунды, даже в случае enabled")
        self.number_volume_page.HISTORY_BTN.click()
        delay(1, reason="Чтобы наверняка убедиться, что окно истории не открылась")
        self.number_volume_page.MODAL.not_to_be_visible()
