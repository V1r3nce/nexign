from playwright.sync_api import Page

from pages.base_page import BasePage
from pages.locators.lis_locators.operation_monitor_elements import OperationMonitorElementsLis


class OperationMonitorPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        self.locators = OperationMonitorElementsLis(page)
