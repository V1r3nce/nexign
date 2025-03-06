from playwright.sync_api import Page

from pages.locators.lis_locators.base_elements_lis import BaseElementsLis
from pages.ui_elements import Element, ElementsList


class DirectoriesElementsLis(BaseElementsLis):
    """Страница Справочники LIS"""

    def __init__(self, page: Page):
        super().__init__(page)

        self.TITLE = Element("h2", "Заголовок страницы", self.page)
        self.ADD_NEW_ELEMENT_BTN = Element("ps-button[ng-click*=dialogAddDictionary]",
                                           "Кнопка 'Добавить элемент'", self.page)
        self.EDIT_ELEMENT_BTN = Element("ps-button[ng-click*=showEditDictionaryDialog]",
                                        "Кнопка 'Редактировать элемент'", self.page)
        self.DELETE_ELEMENT_BTN = Element("ps-button[ng-click*=showDeleteDictionaryDialog]",
                                          "Кнопка 'Удалить элемент'", self.page)
        self.UPDATE_ELEMENTS_LIST_BTN = Element("ps-button[ng-click*=refreshGrid]",
                                                "Кнопка 'Обновить список элементов'", self.page)
        self.LOADER = Element(".b-loading-indication__align__content", "Окно загрузки", self.page)

        # Список справочников
        self.DIRECTORY_NUMBER_CLASSES = Element("(//*[@rows='dictionaries.rows'] //td)[2]",
                                                "Справочник 'Классы номеров'", self.page)

        # Таблица справочника
        self.TABLE_COLUMN_NAMES = ElementsList("[rows='dictionaries.values.rows'] tr.n-grid__head-row th",
                                               "Названия столбцов справочника", self.page)
        self.TABLE_LINE = ElementsList("[rows='dictionaries.values.rows'] tr.n-grid__row",
                                       "Строки таблицы справочника", self.page)
        self.DIRECTORY_ELEMENTS = ElementsList("[rows='dictionaries.values.rows'] tr.n-grid__row td:nth-child(1)",
                                               "Элементы справочника", self.page)
        self.SECOND_COLUMN_ELEMENTS = ElementsList("[rows='dictionaries.values.rows'] tr.n-grid__row td:nth-child(2)",
                                                   "Элементы второй колонки таблицы", self.page)
        self.SECOND_COLUMN_CHECKBOXES = ElementsList(
            "[rows='dictionaries.values.rows'] tr.n-grid__row td:nth-child(2) ps-checkbox>span",
            "Чекбоксы второй колонки таблицы", self.page)

        # Модальное окно Добавление элемента справочника
        self.NAME_INPUT_TITLE = Element("//*[contains(@ng-model, 'dictionaries.values.add.name')]/../div[1]",
                                        "Название поля 'Наименование'", self.page)
        self.NAME_INPUT = Element("[ng-model='dictionaries.values.add.name']", "Поле 'Наименование'", self.page)
        self.ACTIVE_CHECKBOX = Element("[ng-model='dictionaries.values.add.isActive']", "Чекбокс 'Активный'", self.page)
        self.FEDERAL_CHECKBOX = Element("[ng-model='dictionaries.values.add.isFederal']",
                                        "Чекбокс 'Федеральный'", self.page)
        self.ADD_ELEMENT_BTN = Element("ps-button[on-submit='addDictionaryValue()']", "Кнопка 'Добавить'", self.page)
        self.CANCEL_ADD_ELEMENT_BTN = Element("ps-button[ng-click='closeAddDictionaryDialog()']",
                                              "Кнопка 'Отменить' добавление элемента справочника", self.page)
