from playwright.sync_api import Page

from pages.locators.lis_locators.base_elements_lis import BaseElementsLis
from pages.ui_elements import Element, ElementsList


class CreateSimCardElementsLis(BaseElementsLis):
    """Страница Изготовление SIM-карт LIS"""

    def __init__(self, page: Page):
        super().__init__(page)

        # HEADER
        self.PAGE_TABS = ElementsList("a.n-tab__title", "Вкладки страницы", self.page)

        # TAB Список MSISDN верхние кнопки
        self.ADD_BLOCK_BTN = Element("[ng-click*='model.dialogs.poolManagement.showDialog(false)']",
                                     "Кнопка 'Добавить блок'", self.page)
        self.EDIT_BLOCK_BTN = Element("[ng-click*='model.dialogs.poolManagement.showDialog(true)']",
                                      "Кнопка 'Редактировать блок'", self.page)
        self.CHANGE_STATUS_BTN = Element("[ng-click*='invertSimStatus']", "Кнопка 'Изменить статус'", self.page)
        self.REFRESH_BTN = Element("[user-value*='simManagement'] [ng-click*='refreshGrid']",
                                   "Кнопка 'Обновить'", self.page)

        # Заголовки таблицы Разметка IMSI
        self.START_RANGE_HEADER = Element("#simManagementGrid tr th.n-grid__title:nth-child(5)",
                                          "Заголовок/Кнопка 'Начальный номер'", self.page)
        self.STATUS_FILTER_FIELD = Element("#simManagementGrid tr td:nth-child(4) [data-for='drop-single']",
                                           "Поле фильтра 'Статус'", self.page)
        self.STATUS_FILTER_OPTIONS = ElementsList("[ng-repeat*='imsiPoolStatuses']", "Опции фильтра 'Статус'",
                                                  self.page)

        # Таблица Разметка IMSI
        self.LINE_CHECKBOXES = ElementsList("#simManagementGrid tr.n-grid__row span.n-check-checkbox",
                                            "Чекбоксы строк таблицы", self.page)
        self.PROJECT_FIELDS = ElementsList("#simManagementGrid tr.n-grid__row td:nth-child(3)",
                                           "Ячейки таблицы Проект", self.page)
        self.STATUS_FIELDS = ElementsList("#simManagementGrid tr.n-grid__row td:nth-child(4)",
                                          "Ячейки таблицы Статус", self.page)
        self.START_RANGE_FIELDS = ElementsList("#simManagementGrid tr.n-grid__row td:nth-child(5)",
                                               "Ячейки таблицы Начальный номер", self.page)
        self.END_RANGE_FIELDS = ElementsList("#simManagementGrid tr.n-grid__row td:nth-child(6)",
                                             "Ячейки таблицы Конечное значение", self.page)

        # Модальное окно Добавление блока
        self.PROJECT_VALUE = Element("[ng-model*='model.dialogs.poolManagement.SIMCardProjectId'] div div",
                                     "Поле выбора 'Проект'", self.page)
        self.BY_QUANTITY_BTN = Element("[ng-click*='initByAmount']", "Кнопка 'Отбор по количеству'", self.page)
        self.BY_RANGE_BTN = Element("[ng-click*='initByRange']", "Кнопка 'Отбор по диапазону'", self.page)
        self.QUANTITY_INPUT = Element("[ng-model*='model.dialogs.poolManagement.count']",
                                      "Поле ввода количество", self.page)
        self.START_RANGE_INPUT = Element("[ng-model*='model.dialogs.poolManagement.startRange']",
                                         "Поле ввода Начальное значение", self.page)
        self.END_RANGE_INPUT = Element("[ng-model*='model.dialogs.poolManagement.endRange']",
                                       "Поле ввода Конечное значение", self.page)
        self.ADD_RANGE_BTN = Element("[ng-click*='model.dialogs.poolManagement.submitDialog']",
                                     "Кнопка 'Добавить'", self.page)
        self.CANCEL_ADD_RANGE_BTN = Element("[ng-click*='model.dialogs.poolManagement.closeDialog']",
                                            "Кнопка 'Отменить'", self.page)
