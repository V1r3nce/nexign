from playwright.sync_api import Page

from pages.base_page import BasePage
from pages.locators.consumption import Consumption


class ConsumptionPage(BasePage):
    """Страница /consuming/subscribers Потребление"""

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        self.locators = Consumption(page)
