from playwright.sync_api import Page

from pages.locators.lis_locators.base_elements_lis import BaseElementsLis
from pages.ui_elements import Element, ElementsList


class SimCardElementsLis(BaseElementsLis):
    """Страница SIM-карты LIS"""

    def __init__(self, page: Page):
        super().__init__(page)

        # HEADER
        self.PAGE_TABS = ElementsList("a.n-tab__title", "Вкладки страницы", self.page)

        # TAB Список SIM-карт верхние кнопки
        self.REFRESH_BTN = Element("[user-value*='simSearch'] [ng-click*='searchSim']",
                                   "Кнопка 'Обновить'", self.page)
        self.HISTORY_BTN = Element("[user-value*='simSearch'] [ng-click*='historyDialog.open']",
                                   "Кнопка 'История'", self.page)
        self.EDIT_ATTRIBUTE_BTN = Element("[user-value*='simSearch'] [ng-click*='dialogs.massEditSim.open']",
                                          "Кнопка 'Редактировать атрибуты'", self.page)
        self.EDIT_EXPIRATION_DATE_BTN = Element("[user-value*='simSearch'] [ng-click*='dialogs.periodChange.open']",
                                                "Кнопка 'Изменить срок действия'", self.page)
        self.DOWNLOAD_BTN = Element("[user-value*='simSearch'] [ng-click*='dialogs.csvExport.export']",
                                    "Кнопка 'Выгрузить в Excel'", self.page)
        self.SEARCH_BTN = Element("[user-value*='simSearch'] a.lis-toolbar-search__link", "Кнопка 'Поиск'",
                                  self.page)
        self.NUMBERS_COUNTER = Element("[user-value*='simSearch'] div.toolbar-right a.toolbar-quick-filter__item_active",
                                       "Счетчик номеров", self.page)

        # Поиск
        self.MSISDN_FILTER_BTN = Element("//div[@class='lis-search-numbers-params__item'][1]//div[contains(@class,"
                                         " 'button')]", "Кнопка открыть фильтр 'MSISDN'", self.page)
        self.MSISDN_OPTION_INTERVAL = Element("//*[count(ps-list-item) = 6]/ps-list-item[contains(@user-value,"
                                              " 'INTERVAL')]", "Опция фильтра 'MSISDN' По диапазону", self.page)
        self.MSISDN_OPTION_VALUE = Element("//*[count(ps-list-item) = 6]/ps-list-item[contains(@user-value, 'VALUE')]",
                                           "Опция фильтра 'MSISDN' Точное значение", self.page)
        self.MSISDN_SELECTED_OPTIONS = Element("//div[@class='lis-search-numbers-params__item'][1]"
                                               "//div[contains(@ps-link-element, 'elements.value')]",
                                               "Выбранное значение 'MSISDN'", self.page)
        self.MSISDN_FILTER_INPUT = Element("//div[@class='lis-search-numbers-params__item'][1]//input",
                                           "Поле ввода фильтр 'MSISDN'", self.page)

        # TAB Список SIM-карт
        self.CHECK_ALL_BTN = Element("[user-value*='simSearch'] tr th:nth-child(2)", "Кнопка 'Выбрать все'", self.page)
        self.TABLE_LINE = ElementsList("[user-value*='simSearch'] tr.n-grid__row", "Строки таблицы", self.page)
        self.LINE_CHECKBOXES = ElementsList("[user-value*='simSearch'] tr.n-grid__row span.n-check-checkbox",
                                            "Чекбоксы строк таблицы", self.page)
        self.IMSI_NUMBERS = ElementsList("[user-value*='simSearch'] tr.n-grid__row td:nth-child(3)", "Номера IMSI",
                                         self.page)
        self.EXPIRATIONS_DATES = ElementsList("[user-value*='simSearch'] tr.n-grid__row td:nth-child(14)",
                                              "Сроки действия", self.page)

        # Модальное окно Изменение срока действия
        self.MODAL_EXPIRATION_DATE_INPUT = Element("[value*='dialogs.periodChange.expirationDate'] input",
                                                   "Поле ввода 'Изменение срока действия'", self.page)
        self.CONFIRM_CHANGE_EXPIRATION_DATE_BTN = Element("[on-submit*='dialogs.periodChange.changeExpirationDate']",
                                                          "Кнопка 'Сохранить'", self.page)

        # Модальное окно История по IMSI
        self.HISTORY_TYPE_BTN = ElementsList("a[ng-click*='historyDialog']", "Кнопки типов истории изменений", self.page)
