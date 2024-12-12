import allure
import pytest
from playwright.sync_api import Page, expect
from pages.base_page import BasePage
import time


class TestAuth:

    @pytest.fixture(autouse=True)
    def setup(self, base_url, page: Page):
        self.base_page = BasePage(page)

    @allure.title("logout")
    def test_logout(self, base_url, page: Page):
        self.base_page.logout()

        # @pytest.fixture(scope="class", autouse=True)
        # def login(page: Page, request: SubRequest, base_url: str, base_login: str, base_password: str):
        #
        #     # page.locator(WelcomePage.input_login).fill(base_login)
        #     # page.locator(WelcomePage.input_password).fill(base_password)
        #     # page.click(WelcomePage.login_submit)
