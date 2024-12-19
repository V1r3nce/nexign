import time

import allure

from playwright.sync_api import Page, expect
from dataclasses import dataclass

from common.env_helper import UserData
from pages.locators.login_page import LoginForm


@allure.severity(allure.severity_level.CRITICAL)
@allure.story("Base")
@dataclass
class BasePage:
    def __init__(self, page: Page):
        self.page = page
        self.menu = LoginForm.MENU
        self.logout_key = LoginForm.LOGOUT

    @allure.step("Открыть страницу {url}")
    def open(self, url):
        self.page.goto(url)

    @allure.step("Страница содержит title '{title}'")
    def expect_title(self, title: str):
        expect(self.page).to_have_title(title)

    @allure.step("Страница содержит text '{text}'")
    def expect_text(self, text: str):
        assert self.page.get_by_text(text).is_visible()

    @allure.step("Страница содержит URL '{url}'")
    def expect_url(self, url: str):
        expect(self.page).to_have_url(url)

    @allure.step("Logout from system")
    def logout(self):
        # TODO change this from text to selectors
        self.page.get_by_text(self.menu).click()
        self.page.get_by_text(self.logout_key).click()

    def click_button(self, selector: str):
        self.page.locator(selector).click()

    def check_element(self, selector: str):
        expect(self.page.locator(selector)).to_be_visible()
