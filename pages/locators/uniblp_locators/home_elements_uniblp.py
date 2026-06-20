from pages.locators.uniblp_locators.base_elements_uniblp import BaseUniblpElements
from pages.ui_elements import Element


class HomeUniblpElements(BaseUniblpElements):
    """Страница Домашняя UNIBLP UI"""

    def __init__(self) -> None:
        super().__init__()

        # LEFT PANEL
        self.DISCHARGES = Element("//a[contains(@class, 'app-menu-link_discharges')]", "Кнопка 'Выписки'")
        self.FILES = Element("//a[contains(@class, 'app-menu-link_files')]", "Кнопка 'Файлы'")
        self.SEARCH_DOCS = Element("//a[contains(@class, 'app-menu-link_wide-search')]", "Кнопка 'Поиск документов'")
        self.REPORTS = Element("//a[contains(@class, 'app-menu-link_reports')]", "Кнопка 'Отчеты'")
        self.DICTIONARY = Element("//a[contains(@class, 'app-menu-link_dictionary')]", "Кнопка 'Справочники'")
