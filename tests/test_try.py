import allure
import pytest
from playwright.sync_api import Page
from pages.base_page import BasePage


class TestAuth:

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.base_page = BasePage(page)

    @allure.title("logout")
    def test_logout(self, base_url):
        self.base_page.logout()