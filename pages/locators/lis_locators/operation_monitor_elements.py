from playwright.sync_api import Page

from pages.locators.lis_locators.base_elements_lis import BaseElementsLis
from pages.ui_elements import Element, ElementsList


class OperationMonitorElementsLis(BaseElementsLis):
    """Страница Монитор операций LIS"""

    def __init__(self, page: Page):
        super().__init__(page)

        self.TITLE = Element("h2", "Заголовок страницы", self.page)

        self.STATE_LIST = ElementsList("tbody tr td:nth-child(7) div", "Список ip", self.page)

        self.MODAL_RESPONSE_BTN = Element("li:nth-child(2) .n-tab__title", "Кнопка 'Response'", self.page)
        self.RESPONSE_ERROR_TEXT = Element("section[ng-class*='response.conflictsResultJson'] code", "Текст кода 'Ошибки'", self.page)
