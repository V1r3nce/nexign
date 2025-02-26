from playwright.sync_api import Page

from pages.locators.lis_locators.base_elements_lis import BaseElementsLis
from pages.ui_elements import Element, ElementsList


class SimCardShipmentElementsLis(BaseElementsLis):
    """Страница Отгрузка SIM-карт LIS"""

    def __init__(self, page: Page):
        super().__init__(page)

        # HEADER
        self.TITLE = Element("h2.content-section-header", "Заголовок страницы", self.page)

        # Верхние кнопки
        self.SHIPMENT_BTN = Element("ps-button[icon='shipping-sim-inverted']", "Кнопка 'Отгрузить'", self.page)
        self.SHIPMENT_BACK_BTN = Element("ps-button[icon='shipping-sim-back']", "Кнопка 'Вернуть на ГС'", self.page)
        self.REFRESH_BTN = Element("ps-button[ng-click*='refreshGrid']", "Кнопка 'Обновить'", self.page)
        self.EXPORT_BTN = Element("ps-button[ng-click*='csvExport']", "Кнопка 'Выгрузить в файл'", self.page)

        # Строки таблицы
        self.OPERATIONS_IDS = ElementsList("tr.n-grid__row td:nth-child(2) a", "Значения столбца 'ID операции'",
                                           self.page)
