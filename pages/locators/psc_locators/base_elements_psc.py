from pages.ui_elements import Element, ElementsList


class BaseElementsPsc:
    def __init__(self) -> None:
        self.APP_LOGO = Element("a[href='/ProductCatalog/ui/']", "Логотип сервиса")

        # FORM ELEMENTS
        self.SECOND_BTN_FORM = Element(".footer-actions > button:last-child", "Вторая кнопка формы")
        self.OPTIONS = ElementsList("[class*='psc-option']", "Варианты выбора в выпадающем списке")
        self.CHECKBOX_OPTIONS = ElementsList(
            "[class*='psc-option'] > span", "Варианты выбора в выпадающем списке чекбоксов"
        )
        self.STATIC_CHECKBOX_OPTIONS = ElementsList(
            "[data-test='PscTableCellCheckbox'] > span", "Варианты выбора чекбоксы"
        )
        self.STATIC_CHECKBOX_VALUE = ElementsList(
            "//label[@data-test='PscTableCellCheckbox']/parent::div/parent::div//div[@data-test='PscTableCell:name-id']",
            "Значения чекбоксов",
        )
        self.FORM_DIALOG_SEARCH_INPUT = Element(
            "[data-test*='PscDialog'] [data-test*='PscTableFilterPanelInput:name'] input",
            "Поле поиска фильтра формы",
        )
        self.RADIO_OPTIONS = ElementsList("[data-test*='PscTableCellRadioButton']", "Варианты выбора радио баттоны")
        self.NEXT_BTN = Element("[data-test='PscDialogButtonNext']", "Кнопка 'Далее'")
        self.LOADING_SPINNER = Element(".el-loading-fade-enter-active svg", "Лоадер")

        # CHARACTERISTIC LOCATORS
        self.ADD_BTN = Element("[data-test='ElButton:add']", "Кнопка 'Добавить'")
        self.META_ATTRIBUTE_TAB = Element("#tab-meta", "Таб 'Мета-атрибуты'")
        self.META_ADD_BTN = Element("#pane-meta [data-test='ElButton:add']", "Кнопка 'Добавить'")
        self.SEARCH_INPUT = Element("[data-test*='Input'][placeholder]", "Поле ввода 'Характеристики'")
        self.CHARACTERISTICS_OPTIONS = ElementsList("[data-test='item'] > div:first-child", "Варианты 'Характеристики'")
        self.META_CHARACTERISTIC_DROPDOWN_BTN = ElementsList(
            "[data-test*='FlexibleCharacteristicMetaItem'] [data-test='PscIcon:arrow-triangle-down']",
            "Кнопка открытия 'Метахарактеристики'",
        )

        # NOTIFICATION
        self.NOTIFICATION_CONTENT = Element(".snackbar-notification-content", "Информационное сообщение")
        self.NOTIFICATION_CLOSE_BTN = Element(".el-notification__closeBtn", "Закрыть информационное сообщение")
