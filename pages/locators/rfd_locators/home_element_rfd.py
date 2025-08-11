from playwright.sync_api import Page

from pages.locators.rfd_locators.base_elements_rfd import BaseElementsRfd, SelectRFD
from pages.ui_elements import Element, ElementsList


class HomeElementsRfd(BaseElementsRfd):
    """Страница Домашняя /ps/refdata/references Refdata UI"""

    def __init__(self, page: Page):
        super().__init__(page)

        # HEADER PANEL
        self.LOGOUT_BTN = Element('a[class="app-header-user-logout"]', "Кнопка 'Выход из сервиса'", self.page)

        self.ADD_BNT = Element('ps-button[icon="plus"]', "Кнопка 'Добавить справочник'", self.page)
        self.IMPORT_BNT = Element('ps-button[ng-click*="ctrl.importReference()"]', "Кнопка 'Импорт'", self.page)
        self.CHOSE_IMPORT_FILE_BTN = Element(
            '[class="js-button-select-file b-button ps-component b-button_only_icon"]',
            "Кнопка выбора файла для импорта",
            self.page,
        )
        self.SUCCESS_IMPORT_BTN = Element('[ng-click="ctrl.save()"] ps-icon', "Кнопка успешного импорта", self.page)
        self.SUCCESS_IMPORT_INFO = Element(
            'table[class="n-popup-message-align bi-focus-element-wrapper__ng"]',
            "Информация об успешном импорте",
            self.page,
        )
        self.SUCCESS_OK_BNT = Element('[ng-click="psDialog.close(button.result)"]', "Успешная кнопка 'ОК'", self.page)
        self.EXPORT_BNT = Element('ps-button[ng-click*="ctrl.exportReference()"]', "Кнопка 'Экспорт'", self.page)
        self.SEARCH_CODE_FLD = Element(
            "input[ng-model=\"ctrl.referencesGrid.filter['referenceCode']\"]", "Поле для поиска по коду", self.page
        )
        self.NAME_ELEMENT_CURRENCIES_FLD = Element(
            "input[ng-model=\"ctrl.referenceItemsGrid.filter['name']\"]", "Поле для поиска по наименованию", self.page
        )
        self.CODE_ELEMENT_CURRENCIES_FLD = Element(
            "input[ng-model=\"ctrl.referenceItemsGrid.filter['referenceItemCode']\"]",
            "Поле для поиска по коду у элемента",
            self.page,
        )

        self.DIRECTORY = ElementsList("(//div[contains(@data-cell, 'view.columns[0]')])", "Справочник", self.page)
        self.DIRECTORY_INFORMATION = Element(
            '[class="grid-holder collapsible-wrapper"]', "Информация о справочнике", self.page
        )
        # СВОЙСТВА
        self.CODE_PROPERTIES = Element('[name="referenceCode"]', "Свойство 'Код'", self.page)
        self.NAME_PROPERTIES = Element('[name="editReferenceName"]', "Свойство 'Наименование'", self.page)
        self.CREATED_PROPERTIES = Element('[name="created"]', "Свойство 'Дата создания'", self.page)

        self.NEXT_ON_ONE_BTN = Element(
            'a[class="n-pager__link n-pager__link_next"]', "Кнопка пагинации 'Следующая'", self.page
        )

        self.ELEMENTS_BNT = Element('[class="toolbar-quick-filter"] > :nth-child(2)', "Кнопка 'Элементы'", self.page)
        self.ELEMENTS_PANEL = Element(
            'ps-grid[rows="ctrl.referenceItemsGrid.items"]', "Панель элементов справочника", self.page
        )
        self.ADD_ELEMENT_DIRECTORY_BTN = Element(
            'ps-button[icon="plus-inverted"]', "Кнопка 'Добавить Элемент Справочника'", self.page
        )
        self.DELETE_ELEMENT_BTN = Element('[ng-click="ctrl.deleteElement()"]', "Кнопка 'Удалить элемент'", self.page)
        self.CONFIRM_DELETE_ELEMENT_BTN = Element(
            '[ng-click="ctrl.apply($event);"]', "Кнопка подтвеждения 'Удалить'", self.page
        )
        self.CONFIG_MESSAGE = Element('[ng-bind-html="config.message"]', "Сообщение об ошибке", self.page)
        self.EDIT_ELEMENT_BTN = Element('ps-button[icon="edit-inverted"]', "Кнопка 'Редактировать Элемент'", self.page)
        self.PUBLISH_BTN = Element(
            'ps-button[icon="publish"][ng-click="ctrl.publishElement()"]', "Кнопка 'Опубликовать'", self.page
        )
        self.PUBLISH_All_BTN = Element(
            'ps-button[icon="publish"][ng-click="ctrl.publishAllElements()"]', "Кнопка 'Опубликовать все'", self.page
        )
        self.TO_LAST_PAGE_BTN = Element(
            "(//a[contains(@class, 'n-pager__link_end')])[2]", "Кнопка пагинации 'Последняя'", self.page
        )
        self.COUNT_CURRENT_ELEMENT = Element(
            "(//div[contains(@class, 'grid-counter__value')])[2]", "Количество текущих элементов справочника", self.page
        )


class CreateElementDirectoryForm(BaseElementsRfd):
    """Форма Создания Элемента справочника"""

    def __init__(self, page: Page):
        super().__init__(page)
        self.CODE_FLD = Element('input[name="referenceItemCodeField"]', "Поле 'Код'", self.page)
        self.NAME_FLD = Element('ps-button[icon="dots"]', "Наименование", self.page)
        self.CODE_CURRENCIES_FLD = Element(
            '[class="b-groupbox__body fixed-height-container"] > :nth-child(2) > input', "Код валюты", self.page
        )
        self.DEFAULT_CURRENCIES_FLD = SelectRFD(
            '[class="b-groupbox__body fixed-height-container"] > :nth-child(3) > :nth-child(2) > :nth-child(1)',
            "Валюта по умолчанию",
            self.page,
        )
        self.CODE_CURRENCIES_RUS_CLASS_FLD = Element(
            '[class="b-groupbox__body fixed-height-container"] > :nth-child(4) > input',
            "Код валюты по российскому классификатору валют",
            self.page,
        )

        """Форма Редактирование Наименования"""
        self.DEFAULT_VALUE_FLD = Element(
            'input[ng-model="ctrl.formData.defaultValue"]', "Значение по умолчанию", self.page
        )
        self.RU_LANG_FLD = Element('[id="scroll"] > div > :nth-child(2) > input', "Русский (RU)", self.page)
        self.EN_LAND_FLD = Element('[id="scroll"] > div > :nth-child(3) > input', "Английский (EN)", self.page)
        self.FR_LAND_FLD = Element('[id="scroll"] > div > :nth-child(4) > input', "Французский (FR)", self.page)
        self.AR_LAND_FLD = Element('[id="scroll"] > div > :nth-child(5) > input', "Арабский (AR)", self.page)


class CreateDirectoryForm(CreateElementDirectoryForm):
    """Форма Создания справочника"""

    def __init__(self, page: Page):
        super().__init__(page)
        self.CODE_DIRECTORY_FLD = Element('input[name="codeField"]', "Поле 'Код'", self.page)
        self.TYPE_CODE_FLD = SelectRFD('[name="typeField"]', "Поле 'Тип кода справочника'", self.page)
