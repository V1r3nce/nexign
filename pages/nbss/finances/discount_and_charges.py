from playwright.sync_api import Page

from pages.base_page import BasePage
from pages.locators.nbss.finances.discount_and_charges import DiscountAndCharges


class DiscountAndChargesPage(BasePage):
    """Страница /finance/discounts Скидки/Доначисления"""

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        self.locators = DiscountAndCharges(page)
