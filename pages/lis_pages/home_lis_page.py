from playwright.sync_api import Page

from pages.base_page import BasePage
from pages.locators.lis_locators.home_elements_lis import HomeElementsLis


class HomeLisPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        self.locators = HomeElementsLis(page)
