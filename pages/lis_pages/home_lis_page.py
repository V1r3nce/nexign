from pages.base_page import BasePage
from pages.locators.lis_locators.home_elements_lis import HomeLisElements


class HomeLisPage(BasePage):
    def __init__(self) -> None:
        super().__init__()

        self.locators = HomeLisElements()
