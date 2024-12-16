import time

import allure
import pytest
from playwright.sync_api import Page
from pages.personal_account_page import PersonalAccountPage




class TestPersonalAccount:

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.personal_account_page = PersonalAccountPage(page)

    def test_create_personal_account(self):
        self.personal_account_page.click_button_create_client()
        self.personal_account_page.expect_text('Создание клиента: физическое лицо')
        self.personal_account_page.fill_data_for_individual_client()
        self.personal_account_page.click_button_save_client()
