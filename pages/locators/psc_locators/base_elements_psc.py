from playwright.sync_api import Page

from pages.ui_elements import Element, ElementsList


class BaseElementsPsc:
    def __init__(self, page: Page):
        self.page = page

        self.APP_LOGO = Element("a[href='/ProductCatalog/ui/']", "Логотип сервиса", self.page)

        # FORM ELEMENTS
        self.SECOND_BTN_FORM = Element(".footer-actions > button:last-child", "Вторая кнопка формы", self.page)
        self.OPTIONS = ElementsList("[data-test='PscOption']", "Варианты выбора в выпадающем списке", self.page)
        self.CHECKBOX_OPTIONS = ElementsList(
            "[data-test='PscOption'] > span", "Варианты выбора в выпадающем списке чекбоксов", self.page
        )
        self.STATIC_CHECKBOX_OPTIONS = ElementsList(
            "[data-test='PscTableCellCheckbox'] > span", "Варианты выбора чекбоксы", self.page
        )
        self.STATIC_CHECKBOX_VALUE = ElementsList(
            "//label[@data-test='PscTableCellCheckbox']/parent::div/parent::div//div[@data-test='PscTableCell:name-id']",
            "Значения чекбоксов",
            self.page,
        )
        self.FORM_DIALOG_SEARCH_INPUT = Element(
            "[data-test*='PscDialog'] [data-test*='PscTableFilterPanelInput:name'] input",
            "Поле поиска фильтра формы",
            self.page,
        )
        self.RADIO_OPTIONS = ElementsList(
            "[data-test*='PscTableCellRadioButton']", "Варианты выбора радио баттоны", self.page
        )
        self.NEXT_BTN = Element("[data-test='PscDialogButtonNext']", "Кнопка 'Далее'", self.page)
        self.LOADING_SPINNER = Element(".el-loading-fade-enter-active svg", "Лоадер", self.page)

        # CHARACTERISTIC LOCATORS
        self.ADD_BTN = Element("[data-test='ElButton:add']", "Кнопка 'Добавить'", self.page)
        self.META_ATTRIBUTE_TAB = Element("#tab-meta", "Таб 'Мета-атрибуты'", self.page)
        self.META_ADD_BTN = Element("#pane-meta [data-test='ElButton:add']", "Кнопка 'Добавить'", self.page)
        self.SEARCH_INPUT = Element("[data-test='ElInput:search']", "Поле ввода 'Характеристики'", self.page)
        self.CHARACTERISTICS_OPTIONS = ElementsList(
            "[data-test='item'] > div:first-child", "Варианты 'Характеристики'", self.page
        )
        self.META_CHARACTERISTIC_DROPDOWN_BTN = ElementsList(
            "[data-test*='FlexibleCharacteristicMetaItem'] [data-test='PscIcon:arrow-triangle-down']",
            "Кнопка открытия 'Метахарактеристики'",
            self.page,
        )

        # NOTIFICATION
        self.NOTIFICATION_CONTENT = Element(".snackbar-notification-content", "Информационное сообщение", self.page)
        self.NOTIFICATION_CLOSE_BTN = Element(
            ".el-notification__closeBtn", "Закрыть информационное сообщение", self.page
        )
