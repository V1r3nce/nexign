from playwright.sync_api import Page

from pages.locators.lis_locators.base_elements_lis import BaseElementsLis
from pages.ui_elements import Element, ElementsList


class NumberVolumeElementsLis(BaseElementsLis):
    """Страница Номерная емкость LIS"""

    def __init__(self, page: Page):
        super().__init__(page)

        # HEADER
        self.TITLE = Element("div.content-section-header__left", "Заголовок страницы", self.page)
        self.PAGE_TABS = ElementsList("a.n-tab__title", "Вкладки страницы", self.page)

        # TAB List MSISDN

        # TAB List MSISDN TOP BUTTONS
        self.RESERVE_BTN = Element("[ng-click*='reserveDialog']", "Кнопка 'Зарезервировать'", self.page)
        self.HISTORY_BTN = Element("[ng-click*='historyDialog']", "Кнопка 'Зарезервировать'", self.page)
        self.LINK_NUMBER_BTN = Element("[ng-click*='linkingNumberDialog']", "Кнопка 'Связывание номеров DEF и ABC'",
                                       self.page)
        self.DOWNLOAD_BTN = Element("[ng-click*='massActions.csvExport']", "Кнопка 'Обновить'", self.page)
        self.REFRESH_BTN = Element("[ng-click*='search']", "Кнопка 'Обновить'", self.page)
        self.SEARCH_BTN = Element("a.lis-toolbar-search__link", "Кнопка 'Поиск'", self.page)
        self.NUMBERS_COUNTER = Element("div.toolbar-right a.toolbar-quick-filter__item_active", "Счетчик номеров",
                                       self.page)
        self.ZONE_TYPE = ElementsList("[ng-click*='numZoneSwitch']", "Кнопки 'Код зоны нумерации'", self.page)

        # TAB List MSISDN Table
        self.CHECK_ALL_BTN = Element("//ps-tabs//tr/th[2]", "Кнопка 'Выбрать все'", self.page)
        self.TABLE_LINE = ElementsList("tr.n-grid__row", "Строки таблицы", self.page)
        self.LINE_CHECKBOXES = ElementsList("tr.n-grid__row span.n-check-checkbox", "Чекбоксы строк таблицы", self.page)
        self.PHONE_NUMBERS = ElementsList("tr.n-grid__row td:nth-child(3)", "Номера телефонов", self.page)

        # Модалка История по номеру
        self.REFRESH_HISTORY_BTN = Element("[ng-click*='refreshGrid()']", "Кнопка 'Обновить данные'", self.page)
        self.HISTORY_TYPE_BTN = ElementsList("[ng-click*='historyDialog.setActive']", "Кнопка 'Обновить данные'", self.page)
