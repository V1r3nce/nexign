from pages.locators.rfd_locators.base_elements_rfd import BaseRfdElements, SelectRFD
from pages.ui_elements import Element, ElementsList


class HomeRfdElements(BaseRfdElements):
    """Страница Домашняя /ps/refdata/references Refdata UI"""

    def __init__(self) -> None:
        super().__init__()

        # HEADER PANEL
        self.LOGOUT_BTN = Element('a[class="app-header-user-logout"]', "Кнопка 'Выход из сервиса'")

        self.ADD_BNT = Element('ps-button[icon="plus"]', "Кнопка 'Добавить справочник'")
        self.IMPORT_BNT = Element('ps-button[ng-click*="ctrl.importReference()"]', "Кнопка 'Импорт'")
        self.CHOSE_IMPORT_FILE_BTN = Element(
            '[class="js-button-select-file b-button ps-component b-button_only_icon"]',
            "Кнопка выбора файла для импорта",
        )
        self.SUCCESS_IMPORT_BTN = Element('[ng-click="ctrl.save()"] ps-icon', "Кнопка успешного импорта")
        self.SUCCESS_IMPORT_INFO = Element(
            'table[class="n-popup-message-align bi-focus-element-wrapper__ng"]',
            "Информация об успешном импорте",
        )
        self.SUCCESS_OK_BNT = Element('[ng-click="psDialog.close(button.result)"]', "Успешная кнопка 'ОК'")
        self.EXPORT_BNT = Element('ps-button[ng-click*="ctrl.exportReference()"]', "Кнопка 'Экспорт'")
        self.SEARCH_CODE_FLD = Element(
            "input[ng-model=\"ctrl.referencesGrid.filter['referenceCode']\"]", "Поле для поиска по коду"
        )
        self.NAME_ELEMENT_CURRENCIES_FLD = Element(
            "input[ng-model=\"ctrl.referenceItemsGrid.filter['name']\"]", "Поле для поиска по наименованию"
        )
        self.CODE_ELEMENT_CURRENCIES_FLD = Element(
            "input[ng-model=\"ctrl.referenceItemsGrid.filter['referenceItemCode']\"]",
            "Поле для поиска по коду у элемента",
        )

        self.DIRECTORY = ElementsList("(//div[contains(@data-cell, 'view.columns[0]')])", "Справочник")
        self.DIRECTORY_INFORMATION = Element('[class="grid-holder collapsible-wrapper"]', "Информация о справочнике")
        # СВОЙСТВА
        self.CODE_PROPERTIES = Element('[name="referenceCode"]', "Свойство 'Код'")
        self.NAME_PROPERTIES = Element('[name="editReferenceName"]', "Свойство 'Наименование'")
        self.CREATED_PROPERTIES = Element('[name="created"]', "Свойство 'Дата создания'")

        self.NEXT_ON_ONE_BTN = Element('a[class="n-pager__link n-pager__link_next"]', "Кнопка пагинации 'Следующая'")

        self.ELEMENTS_BNT = Element('[class="toolbar-quick-filter"] > :nth-child(2)', "Кнопка 'Элементы'")
        self.ELEMENTS_PANEL = Element('ps-grid[rows="ctrl.referenceItemsGrid.items"]', "Панель элементов справочника")
        self.ADD_ELEMENT_DIRECTORY_BTN = Element(
            'ps-button[icon="plus-inverted"]', "Кнопка 'Добавить Элемент Справочника'"
        )
        self.DELETE_ELEMENT_BTN = Element('[ng-click="ctrl.deleteElement()"]', "Кнопка 'Удалить элемент'")
        self.CONFIRM_DELETE_ELEMENT_BTN = Element('[ng-click="ctrl.apply($event);"]', "Кнопка подтвеждения 'Удалить'")
        self.CONFIG_MESSAGE = Element('[ng-bind-html="config.message"]', "Сообщение об ошибке")
        self.EDIT_ELEMENT_BTN = Element('ps-button[icon="edit-inverted"]', "Кнопка 'Редактировать Элемент'")
        self.PUBLISH_BTN = Element(
            'ps-button[icon="publish"][ng-click="ctrl.publishElement()"]', "Кнопка 'Опубликовать'"
        )
        self.PUBLISH_All_BTN = Element(
            'ps-button[icon="publish"][ng-click="ctrl.publishAllElements()"]', "Кнопка 'Опубликовать все'"
        )
        self.TO_LAST_PAGE_BTN = Element(
            "(//a[contains(@class, 'n-pager__link_end')])[2]", "Кнопка пагинации 'Последняя'"
        )
        self.COUNT_CURRENT_ELEMENT = Element(
            "(//div[contains(@class, 'grid-counter__value')])[2]", "Количество текущих элементов справочника"
        )


class CreateElementDirectoryForm(BaseRfdElements):
    """Форма Создания Элемента справочника"""

    def __init__(self) -> None:
        super().__init__()
        self.CODE_FLD = Element('input[name="referenceItemCodeField"]', "Поле 'Код'")
        self.NAME_FLD = Element('ps-button[icon="dots"]', "Наименование")
        self.CODE_CURRENCIES_FLD = Element(
            '[class="b-groupbox__body fixed-height-container"] > :nth-child(2) > input', "Код валюты"
        )
        self.DEFAULT_CURRENCIES_FLD = SelectRFD(
            '[class="b-groupbox__body fixed-height-container"] > :nth-child(3) > :nth-child(2) > :nth-child(1)',
            "Валюта по умолчанию",
        )
        self.CODE_CURRENCIES_RUS_CLASS_FLD = Element(
            '[class="b-groupbox__body fixed-height-container"] > :nth-child(4) > input',
            "Код валюты по российскому классификатору валют",
        )

        """Форма Редактирование Наименования"""
        self.DEFAULT_VALUE_FLD = Element('input[ng-model="ctrl.formData.defaultValue"]', "Значение по умолчанию")
        self.RU_LANG_FLD = Element('[id="scroll"] > div > :nth-child(2) > input', "Русский (RU)")
        self.EN_LAND_FLD = Element('[id="scroll"] > div > :nth-child(3) > input', "Английский (EN)")
        self.FR_LAND_FLD = Element('[id="scroll"] > div > :nth-child(4) > input', "Французский (FR)")
        self.AR_LAND_FLD = Element('[id="scroll"] > div > :nth-child(5) > input', "Арабский (AR)")


class CreateDirectoryForm(CreateElementDirectoryForm):
    """Форма Создания справочника"""

    def __init__(self) -> None:
        super().__init__()
        self.CODE_DIRECTORY_FLD = Element('input[name="codeField"]', "Поле 'Код'")
        self.TYPE_CODE_FLD = SelectRFD('[name="typeField"]', "Поле 'Тип кода справочника'")
