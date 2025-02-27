from playwright.sync_api import Page
from pages.locators.crab.base_elements_crab import BaseElementsCrab
from pages.ui_elements import ElementsList, Element


class CrabOrders(BaseElementsCrab):
    """Страница '#/orders' Заявки"""

    def __init__(self, page: Page):
        super().__init__(page)

        self.ORDER_ID_SEARCH = Element("(//table //input)[1]", "Поиск по номеру заявки", self.page)

        self.ORDERS = ElementsList("table:nth-child(2) tbody tr", "Заявки", self.page)
        self.ORDERS_ID = ElementsList("table:nth-child(2) tbody tr td:nth-child(2)", "Номер заявки", self.page)