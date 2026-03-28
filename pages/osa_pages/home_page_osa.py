from pages.base_page import BasePage
from pages.locators.osa_locators.home_page_osa import HomeOsaElements


class HomeOsaPage(BasePage):
    def __init__(self) -> None:
        super().__init__()
        self.locators = HomeOsaElements()
