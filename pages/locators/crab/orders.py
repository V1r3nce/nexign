from pages.locators.crab.base_elements_crab import BaseElementsCrab
from pages.ui_elements import Element, ElementsList


class CrabOrders(BaseElementsCrab):
    """Страница '#/orders' Заявки"""

    def __init__(self) -> None:
        super().__init__()

        self.ORDER_ID_SEARCH = Element("(//table //input)[1]", "Поиск по номеру заявки")

        self.ORDERS = ElementsList("table:nth-child(2) tbody tr", "Заявки")
        self.ORDERS_ID = ElementsList("table:nth-child(2) tbody tr td:nth-child(2)", "Номер заявки")
