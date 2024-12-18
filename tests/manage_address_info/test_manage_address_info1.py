import pytest
import allure
from playwright.sync_api import Page

from common.time_helpers import delay
from pages.base_page import BasePage
from pages.client_profile_page import ClientProfilePage


@allure.epic("Управление адресной информацией")
class TestPlaywright:
    @pytest.fixture(autouse=True)
    def setup(self, page: Page, add_new_address_to_lam: dict):
        self.base_page = BasePage(page)
        self.client_profile_page = ClientProfilePage(page)
        self.new_address = add_new_address_to_lam["addressString"]

    @allure.title("Добавление адреса. Ввод всех полей")
    def test_add_address_input_all_fields(self, page: Page, base_url: str, create_user):
        self.base_page.stand_login(base_url)
        allure.id("525413")
        page.goto(f"{base_url}customer-hierarchy-management/customers/{create_user}/overview")
        short_address = self.new_address.split("ул. ")[1]
        self.client_profile_page.click_client_tab()
        self.client_profile_page.locators.ADDRESSES_TAB.click()
        delay(1, reason="Без ожидания пустой список адресов")
        self.client_profile_page.locators.ADD_BTN.click()
        self.client_profile_page.add_address_element.TITLE.to_contain_text("Добавление адреса")
        self.client_profile_page.add_address_element.ADDRESS_TYPE_FIELD.click()
        self.client_profile_page.choose_option_with_name("Фактический адрес")
        self.client_profile_page.add_address_element.ADDRESS_INPUT.fill(short_address)
        (self.client_profile_page.add_address_element.ADDRESS_OPTION.
         to_contain_text(element_index=0, text=short_address))
        self.client_profile_page.add_address_element.ADDRESS_OPTION.click(element_index=0)
        self.client_profile_page.add_address_element.SAVE_BTN.click()
        (self.client_profile_page.locators.TABLE_LINE.
         to_contain_text(element_index=2, text=f"Фактический адрес{self.new_address}"))
