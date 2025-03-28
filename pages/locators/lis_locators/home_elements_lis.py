from playwright.sync_api import Page

from pages.locators.lis_locators.base_elements_lis import BaseElementsLis
from pages.ui_elements import Element, ElementsList


class HomeElementsLis(BaseElementsLis):
    """Страница Домашняя LIS UI"""

    def __init__(self, page: Page):
        super().__init__(page)

        # LEFT PANEL
        self.MENU_LINK_LIST = ElementsList(".app-menu-link", "Список ссылок меню", self.page)
        self.SIM_SHIPPING_BTN = Element(
            "li:first-child a.app-menu-link.app-menu-link_shipping", "Кнопка 'Отгрузка SIM-карт'", self.page
        )
        self.SIM_CARD_CREATE_BTN = Element(
            "li a.app-menu-link.app-menu-link_factory", "Кнопка 'Изготовление SIM-карт'", self.page
        )
        self.MANAGE_LINK_BTN = Element(
            "li a.app-menu-link.app-menu-link_link", "Кнопка 'Управление предсвязками'", self.page
        )
        self.SIM_CARD_BTN = Element("li a.app-menu-link.app-menu-link_sim", "Кнопка 'SIM-карты'", self.page)
        self.NUMBER_VOLUME_BTN = Element(
            "li a.app-menu-link.app-menu-link_numValue", "Кнопка 'Номерная емкость'", self.page
        )
        self.IP_ADDRESSES_BTN = Element("li a.app-menu-link.app-menu-link_ip", "Кнопка 'IP-адреса'", self.page)
        self.DIRECTORIES_BTN = Element("li a.app-menu-link.app-menu-link_directories", "Кнопка 'Справочники'", self.page)
        self.OPERATION_MONITOR_BTN = Element("li a.app-menu-link.app-menu-link_monitor", "Монитор операций'", self.page)
