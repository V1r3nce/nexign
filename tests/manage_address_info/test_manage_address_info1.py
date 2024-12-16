import time

import pytest
import allure
from playwright.sync_api import Page

from common.time_helpers import delay
from pages.base_page import BasePage
from pages.client_profile_page import ClientProfilePage


@allure.epic("Управление адресной информацией")
class TestPlaywright:
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.base_page = BasePage(page)
        self.client_profile_page = ClientProfilePage(page)

    @allure.title("Добавление адреса. Ввод всех полей")
    def test_add_address_input_all_fields(self, page: Page, base_url: str):
        allure.id("525413")
        page.goto(f"{base_url}customer-hierarchy-management/customers/18404/overview")
        self.client_profile_page.click_client_tab()
        self.client_profile_page.locators.ADDRESSES_TAB.click()
        delay(1, reason="Без ожидания пустой список адресов")
        self.client_profile_page.locators.ADD_BTN.click()
        self.client_profile_page.add_address_element.TITLE.to_contain_text("Добавление адреса")
        self.client_profile_page.add_address_element.ADDRESS_TYPE_FIELD.click()
        self.client_profile_page.choose_option_with_name("Фактический адрес")
        delay(5)
        assert False
