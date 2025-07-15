import re

import allure
import pytest
from playwright.sync_api import Page

from common.helpers.checker import assert_that
from common.helpers.time_helpers import delay
from pages.base_page import BasePage
from pages.lis_pages.ip_addresses_page import IPAddressPage
from pages.locators.lis_locators.home_elements_lis import HomeElementsLis


class TestViewHistoryOfIPAddresses:
    @pytest.fixture(autouse=True)
    def setup(self, stand_login_lis: Page) -> None:
        self.base_page = BasePage(stand_login_lis)
        self.ip_addresses_page = IPAddressPage(stand_login_lis)
        self.home_page_lis = HomeElementsLis(stand_login_lis)

    @allure.suite("E2E_16 Подготовка IP-адресов к продаже")
    @allure.title("Просмотр истории IP-адреса (1 адрес)")
    @allure.id(583574)
    @pytest.mark.regress
    def test_view_history_of_ip_addresses(self, page: Page, base_url: str) -> None:
        with allure.step('Открыть окно "IP-адреса"'):
            self.home_page_lis.IP_ADDRESSES_BTN.wait_to_be_visible()
            delay(0.2, reason="Кнопке нужно время даже после того, как она стала доступной")
            self.home_page_lis.IP_ADDRESSES_BTN.click()
            self.ip_addresses_page.locators.IP_RESULT_VIEW.wait_to_be_visible()
            self.ip_addresses_page.locators.ADD_ADDRESS_BTN.wait_to_be_visible()
            self.ip_addresses_page.locators.ADDRESS_REFRESH.wait_to_be_visible()
            self.ip_addresses_page.locators.SEARCH_BTN.wait_to_be_visible()
            self.ip_addresses_page.locators.CLEAR_FILTERS_BTN.wait_to_be_visible()
            self.ip_addresses_page.locators.CHOOSE_TEMPLATE_BTN.wait_to_be_visible()
            self.ip_addresses_page.locators.SAVE_TEMPLATE_BTN.wait_to_be_visible()

        with allure.step("Нажать кнопку 'Обновить'"):
            self.ip_addresses_page.locators.ADDRESS_REFRESH.click()
            self.ip_addresses_page.locators.IP_LIST.wait_to_be_visible()
            self.ip_addresses_page.locators.TOOLBAR_TOTAL_TEXT.to_contain_text("Всего")
            self.ip_addresses_page.locators.TOOLBAR_IP_COUNT.wait_to_be_visible()
            delay(0.2, reason="Элементу нужно время на загрузку информации")
            ip_count = self.ip_addresses_page.locators.TOOLBAR_IP_COUNT.text
            assert_that(lambda: int(ip_count) > 0, f"Недопустимое кол-во ip-адресов: '{ip_count}'")

            self.ip_addresses_page.locators.CHECKBOX_LIST.click(0)
            self.ip_addresses_page.locators.TABLE_LINE[0].to_have_class(class_name=re.compile(r"js-selected"))
            delay(0.3, reason="Кнопке нужно время после активации")

            self.ip_addresses_page.locators.HISTORY_BTN.click()
            self.ip_addresses_page.locators.MODAL_TITLE[-1].wait_to_be_visible()
            self.ip_addresses_page.locators.HISTORY_REFRESH_BTN.click()
