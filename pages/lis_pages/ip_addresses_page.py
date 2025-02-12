from playwright.sync_api import Page

from pages.base_page import BasePage
from pages.locators.lis_locators.ip_addresses_elements import IpAdressesElementsLis


class IPAddressPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        self.locators = IpAdressesElementsLis(page)
