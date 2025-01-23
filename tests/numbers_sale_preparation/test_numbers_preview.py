import pytest
import allure
from playwright.sync_api import Page, APIRequestContext

import re

from api.requests.lis_requests.phone_numbers import PhoneNumbersRequests
from common.helpers.env_helper import BASE_URL_LIS
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
        addresses = phone_numbers.get_phone_numbers(BASE_URL_LIS)
        self.number_volume_page.NUMBERS_COUNTER.to_contain_text("Всего*")
        self.number_volume_page.NUMBERS_COUNTER.to_contain_text(str(addresses.json()['listInfo']['count']))
        self.number_volume_page.LINE_CHECKBOXES[0].click()
        self.number_volume_page.LINE_CHECKBOXES[10].click()
        self.number_volume_page.TABLE_LINE[0].to_have_class(class_name=re.compile(r"js-selected"))
        self.number_volume_page.TABLE_LINE[10].to_have_class(class_name=re.compile(r"js-selected"))
