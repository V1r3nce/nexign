import allure

from playwright.sync_api import Page
from dataclasses import dataclass
from common.selector.welcome import WelcomePage


@allure.severity(allure.severity_level.CRITICAL)
@allure.story("Base")
@dataclass
class BasePage:
    def __init__(self, page: Page):
        self.page = page
        self.menu = WelcomePage.menu
        self.logout = WelcomePage.logout

    @allure.step("Logout from system")
    def logout(self):
        self.page.locator(self.menu).click()
        self.page.locator(self.logout).click()