from playwright.sync_api import Page

from pages.locators.base_elements import BaseElements
from pages.ui_elements import Element, ElementsList, RadioOrCheckboxBlock


class BillingTasks(BaseElements):
    def __init__(self, page: Page):
        super().__init__(page)

        self.TITLE = Element("div:first-child > a:first-child", "Заголовок страницы", self.page)

        self.CONTROL_BTNS = ElementsList("h2 + div  button", "Кнопки управления", self.page)
        self.NEW_TASK_BTN = Element("button span div", "Кнопка 'Новое задание'", self.page)
        self.ROLLBACK_TASK_OPTION = Element(
            "div.ui-dropdown_placement_bottomRight [role='menuitem']:last-child",
            "Вариант задания 'Задание на откат'",
            self.page,
        )
        self.LOADER = Element(".ui-spin_spinning", "Иконка загрузки", self.page)

        # TABLE
        self.START_OF_EXECUTION = Element(
            "th:nth-child(6) > div > div:nth-child(1)", "Наименование столбца 'Начало выполнения'", self.page
        )
        self.END_OF_EXECUTION = Element(
            "th:nth-child(7) > div > div:nth-child(1)", "Наименование столбца 'Окончание выполнения'", self.page
        )
        self.TABLE = Element(".ui-table", "Таблица биллинговых заданий", self.page)
        self.TABLE_ROW = ElementsList(".ui-table__body tbody tr", "Список строк таблицы", self.page)
        self.STATUS_LIST = ElementsList(".ui-table__body tbody td:nth-child(2) div", "Список статусов", self.page)
        self.TASK_TYPE_LIST = ElementsList(".ui-table__body tbody td:nth-child(3)", "Список типов заданий", self.page)
        self.TASK_NUMBER_LIST = ElementsList("td:nth-child(4) a", "Список номеров заданий", self.page)
        self.CHECKBOX_LIST = ElementsList(
            ".ui-table__body tbody td:nth-child(1) .ui-checkbox", "Список чекбоксов", self.page
        )

        # ROLLBACK_FORM
        self.ROLLBACK_FORM_TITLE = Element("h3:nth-child(1)", "Заголовок 'Задание на откат биллинга'", self.page)
        self.FROM_INTERVAL = Element(".js-ui-calendar-picker-1", "Интервал 'От'", self.page)
        self.UNTIL_INTERVAL = Element(
            ".js-ui-calendar-picker-2 .ui-masked-datetime-input__value", "Интервал 'До'", self.page
        )
        self.FROM_FILE_BTN = Element(
            "label.ui-radio-button-wrapper:nth-child(2) > span:nth-child(2)", "Кнопка 'Из файла'", self.page
        )
        self.FILE_UPLOAD_BTN = Element("input + div p p", "Кнопка загрузки файла 'Выберите вручную'", self.page)
        self.BY_CONDITION_BTN = Element(
            "label.ui-radio-button-wrapper:nth-child(1) div", "Кнопка 'По условию'", self.page
        )
        self.ADD_CONDITION_BTN = Element(
            ".ui-drawer-body button.ui-dropdown-trigger", "Кнопка 'Добавить условия'", self.page
        )
        self.LEGAL_TYPE_BTN = Element(
            ".ui-dropdown_placement_bottomCenter li:last-child", "Вариант выброра 'Юридичксий тип'", self.page
        )
        self.LEGAL_TYPE_FIELD = Element(".ui-select-selection_multiple", "Поле ввода 'Юридического типа'", self.page)
        self.LEGAL_TYPE_OPTIONS = RadioOrCheckboxBlock(".ui-select-dropdown-menu_vertical", "Юридический тип", self.page)
        self.CANCEL_TASK_BTN = Element("hr + div>div>button:first-child span", "Кнопка 'Отменить' задание", self.page)
        self.CREATE_TASK_BTN = Element("hr +div button + button span", "Кнопка 'Создать' задание", self.page)

        self.ERROR_BODY = Element(".ui-modal-body div", "Текст всплывающей ошибки", self.page)
        self.ERROR_CLOSE_BTN = Element(".ui-modal-footer button", "Кнопка 'Закрыть' всплывающей ошибки", self.page)
