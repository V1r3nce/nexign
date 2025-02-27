from playwright.sync_api import Page

from pages.base_page import BasePage
from pages.locators.crab.orders import CrabOrders

class CrabBasePage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        self.locators = CrabOrders(page)
