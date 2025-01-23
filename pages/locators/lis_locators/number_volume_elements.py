from playwright.sync_api import Page

from pages.locators.base_elements import BaseElements
from pages.ui_elements import Element, ElementsList


class NumberVolumeElementsLis(BaseElements):
    """Страница Номерная емкость LIS"""

    def __init__(self, page: Page):
        super().__init__(page)

        # HEADER
        self.TITLE = Element("div.content-section-header__left", "Заголовок страницы", self.page)
        self.PAGE_TABS = ElementsList("a.n-tab__title", "Вкладки страницы", self.page)

        # TAB List MSISDN

        # TAB List MSISDN TOP BUTTONS
        self.RESERVE_BTN = Element("[ng-click*='reserveDialog']", "Кнопка 'Зарезервировать'", self.page)
        self.LINK_NUMBER_BTN = Element("[ng-click*='linkingNumberDialog']", "Кнопка 'Связывание номеров DEF и ABC'",
                                       self.page)
        self.REFRESH_BTN = Element("[ng-click*='search']", "Кнопка 'Обновить'", self.page)
        self.SEARCH_BTN = Element("a.lis-toolbar-search__link", "Кнопка 'Поиск'", self.page)
        self.NUMBERS_COUNTER = Element("div.toolbar-right a.toolbar-quick-filter__item_active", "Счетчик номеров",
                                       self.page)

        # TAB List MSISDN Table
        self.TABLE_LINE = ElementsList("tr.n-grid__row", "Строки таблицы", self.page)
        self.LINE_CHECKBOXES = ElementsList("tr.n-grid__row span.n-check-checkbox", "Чекбоксы строк таблицы", self.page)
        self.PHONE_NUMBERS = ElementsList("tr.n-grid__row td:nth-child(3)", "Номера телефонов", self.page)
