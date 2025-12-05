from pages.base_page import BasePage
from pages.locators.nbss.finances.discount_and_charges import DiscountAndCharges


class DiscountAndChargesPage(BasePage):
    """Страница /finance/discounts Скидки/Доначисления"""

    def __init__(self) -> None:
        super().__init__()

        self.locators = DiscountAndCharges()
