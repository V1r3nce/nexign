from pages.locators.osa_locators.base_element_osa import BaseOsaElements
from pages.ui_elements import ElementsList


class HomeOsaElements(BaseOsaElements):
    """Страница Домашняя OSA UI"""

    def __init__(self) -> None:
        super().__init__()

        self.LIST_TAB = ElementsList("//a[@class='needauth alink item']", "Список Вкладок")
