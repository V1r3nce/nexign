from pages.base_page import BasePage
from pages.locators.crab.orders import CrabOrdersElements


class CrabBasePage(BasePage):
    def __init__(self) -> None:
        super().__init__()

        self.locators = CrabOrdersElements()
