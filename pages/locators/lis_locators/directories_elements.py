from pages.locators.lis_locators.base_elements_lis import BaseLisElements
from pages.ui_elements import Element, ElementsList


class DirectoriesLisElements(BaseLisElements):
    """Страница Справочники LIS"""

    def __init__(self) -> None:
        super().__init__()

        self.TITLE = Element("h2", "Заголовок страницы")
        self.ADD_NEW_ELEMENT_BTN = Element("ps-button[id]:has(ps-icon[class*=plus])", "Кнопка 'Добавить элемент'")
        self.EDIT_ELEMENT_BTN = Element(
            "ps-button[ng-click*=showEditDictionaryDialog]", "Кнопка 'Редактировать элемент'"
        )
        self.DELETE_ELEMENT_BTN = Element("ps-button[ng-click*=showDeleteDictionaryDialog]", "Кнопка 'Удалить элемент'")
        self.UPDATE_ELEMENTS_LIST_BTN = Element("ps-button[ng-click*=refreshGrid]", "Кнопка 'Обновить список элементов'")

        # Список справочников
        self.DIRECTORY_NUMBER_CLASSES = Element(
            "(//*[@rows='dictionaries.rows'] //td)[2]", "Справочник 'Классы номеров'"
        )

        # Таблица справочника
        self.TABLE_COLUMN_NAMES = ElementsList(
            "[rows='dictionaries.values.rows'] tr.n-grid__head-row th", "Названия столбцов справочника"
        )
        self.TABLE_LINE = ElementsList("[rows='dictionaries.values.rows'] tr.n-grid__row", "Строки таблицы справочника")
        self.DIRECTORY_ELEMENTS = ElementsList(
            "[rows='dictionaries.values.rows'] tr.n-grid__row td:nth-child(1)", "Элементы справочника"
        )
        self.SECOND_COLUMN_ELEMENTS = ElementsList(
            "[rows='dictionaries.values.rows'] tr.n-grid__row td:nth-child(2)",
            "Элементы второй колонки таблицы",
        )
        self.SECOND_COLUMN_CHECKBOXES = ElementsList(
            "[rows='dictionaries.values.rows'] tr.n-grid__row td:nth-child(2) ps-checkbox>span",
            "Чекбоксы второй колонки таблицы",
        )

        # Модальное окно Добавление элемента справочника
        self.ADD_NAME_INPUT_TITLE = Element(
            "//*[contains(@ng-model, 'dictionaries.values.add.name')]/../div[1]",
            "Название поля 'Наименование'",
        )
        self.ADD_NAME_INPUT = Element("[ng-model='dictionaries.values.add.name']", "Поле 'Наименование'")
        self.ADD_ACTIVE_CHECKBOX = Element("[ng-model='dictionaries.values.add.isActive']", "Чекбокс 'Активный'")
        self.ADD_FEDERAL_CHECKBOX = Element("[ng-model='dictionaries.values.add.isFederal']", "Чекбокс 'Федеральный'")
        self.ADD_ELEMENT_BTN = Element("ps-button[on-submit*='addDictionaryValue']", "Кнопка 'Добавить'")
        self.CANCEL_ADD_ELEMENT_BTN = Element(
            "ps-button[ng-click*='closeAddDictionaryDialog']",
            "Кнопка 'Отменить' добавление элемента справочника",
        )

        # Модальное окно Редактирование элемента справочника
        self.EDIT_NAME_INPUT = Element("[ng-model='dictionaries.values.edit.name']", "Поле 'Наименование'")
        self.EDIT_ACTIVE_CHECKBOX = Element("[ng-model='dictionaries.values.edit.isActive']", "Чекбокс 'Активный'")
        self.SAVE_EDIT_ELEMENT_BTN = Element(
            "ps-button[on-submit*='editDictionaryValue']",
            "Кнопка 'Сохранить' редактирование элемента справочника",
        )
        self.CANCEL_EDIT_ELEMENT_BTN = Element(
            "ps-button[ng-click*='closeEditDictionaryDialog']",
            "Кнопка 'Отменить' редактирование элемента справочника",
        )
