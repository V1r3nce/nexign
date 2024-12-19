import time

import allure
import pytest
from playwright.sync_api import Page

from pages.locators.dynamic_form_elements import DynamicForms, FlCustomerCreate
from pages.locators.home_page_elements import HomePage
from pages.personal_account_page import PersonalAccountPage




class TestPersonalAccount:

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.personal_account_page = PersonalAccountPage(page)

    def test_create_personal_account(self, base_url: str):
        self.personal_account_page.click_button(HomePage.CREATE_CUSTOMER_BTN)
        self.personal_account_page.check_element(FlCustomerCreate.LAST_NAME)
        self.personal_account_page.fill_data_for_individual_client()
        self.personal_account_page.click_button(DynamicForms.SAVE_BTN)

