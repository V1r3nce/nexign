from playwright.sync_api import Page

from pages.locators.base_elements import BaseElements
from pages.ui_elements import Element


class HomeElementsLis(BaseElements):
    """Страница Домашняя LIS UI"""

    def __init__(self, page: Page):
        super().__init__(page)

        #LEFT PANEL
        self.SIM_SHIPPING_BTN = Element("li:first-child a.app-menu-link.app-menu-link_shipping",
                                        "Кнопка 'Отгрузка SIM-карт'", self.page)
        self.NUMBER_VOLUME_BTN = Element("li a.app-menu-link.app-menu-link_numValue", "Кнопка 'Номерная емкость'",
                                         self.page)
