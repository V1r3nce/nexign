import allure

from playwright.sync_api import Page
from dataclasses import dataclass
from pages.locators.welcome import WelcomePage


@allure.severity(allure.severity_level.CRITICAL)
@allure.story("Base")
@dataclass
class BasePage:
    def __init__(self, page: Page):
        self.page = page
        self.menu = WelcomePage.menu
        self.logout_key = WelcomePage.logout

    @allure.step("Logout from system")
    def logout(self):
        # TODO change this from text to selectors
        self.page.get_by_text(self.menu).click()
        self.page.get_by_text(self.logout_key).click()
