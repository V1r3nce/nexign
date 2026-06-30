from pages.locators.nbss.dynamic_form_elements import DynamicForms
from pages.ui_elements import (
    DatePicker,
    Dropdown,
    Element,
    ElementsList,
    Select,
    VirtualTable,
    VirtualTableCheckbox,
)


class DiscountAndChargesElements(DynamicForms):
    """Страница 'Скидки/Доначисления'"""

    def __init__(self) -> None:
        super().__init__()

        self.ADD_BTN = ElementsList("//button/span[contains(text(), 'Добавить')]", "Кнопка 'Добавить'")
        self.SET_BTN = Element("div[class*=platform-toolbar] >div:not([style]) span[data-icon=Add]", "Назначить")
        self.FILTER_BTN = Element("[class*=extra-tools] > div > div:not([style]) [data-icon=FilterSettings]", "Фильтры")
        self.MORE_BTN = Dropdown("[class*=extra-tools] > div > div:not([style]) [data-icon=ArrowDropDown]", "Еще")
        self.DISCOUNTS = ElementsList(
            "[role*=tabpanel][id*=panel-discounts] .platform-custom-list-scrollable-body > div:not([class*=empty])",
            "Скидки",
        )
        self.SAVE_BTN = ElementsList("div[class*=bottom-toolbar-area] button[type='submit']", "Сохранить")

        self.DISCOUNT_EDIT_BTN = Element("[data-icon=Edit]", "Редактировать")
        self.DISCOUNT_DELETE_BTN = Element("[data-icon=Delete]", "Удалить")

        # TABS
        self.PROPERTIES_TAB = Element("[data-node-key=properties]", "Таб Свойства")
        self.CONDITIONS_TAB = Element("[data-node-key=conditions-applicability]", "Таб Условия применимости")
        self.PRODUCTS_TAB = Element("[data-node-key=application-products]", "Таб Применение к продуктам")
        self.SUBSCRIBERS_TAB = Element("[data-node-key=application-subscribers]", "Таб Применение к абонентам")

        # NEW DISCOUNT TAB
        self.DISCOUNT_NAME = ElementsList("#add-new-template_name", "Название шаблона")
        self.DATE = ElementsList(
            "//div[@id='validFor_control']//input[@date-range]", "Даты периода когда шаблон может быть назначен"
        )
        self.ACTION = Dropdown("#add-action_actionName", "Действие шаблона")
        self.ACTION_PRIORITY = Element("#add-action_priority", "Приоритет")
        self.DISCOUNT = Element("#add-action_discountValue", "Размер скидки")
        self.THRESHOLD = Element("#add-action_threshold", "Порог суммы, с которой предоставляется скидка")

        # PROPERTIES TAB
        self.PROPERTIES = ElementsList("[id*=panel-properties] > div > div:has(div)", "Свойства скидки")
        self.PROPERTIES_VALUES = ElementsList(
            "[id*=panel-properties] > div > div > div:nth-child(2)", "Значения свойств скидки"
        )

        # CONDITIONS TAB
        self.CONDITIONS = ElementsList(
            "[id*=panel-conditions-applicability] [class*=custom-list-scrollable-body] > div", "Условия"
        )
        self.CONDITION_ATTR_EDIT_BTN = Element(
            "[id*=panel-conditions-applicability] > div > div > div:nth-of-type(2) button", "Редактировать"
        )
        self.DISCOUNT_VALUE = Element(
            "((//*[contains(@id, 'panel-conditions-applicability')] /div /div /div[2] /div[2]) //div)[5]",
            "Размер скидки",
        )
        self.THRESHOLD_AMOUNT = Element(
            "((//*[contains(@id, 'panel-conditions-applicability')] /div /div /div[2] /div[2]) //div)[8]",
            "Порог суммы",
        )

        # PRODUCTS TAB
        self.PRODUCT_ADD_BTN = Element("[id*=panel-application-products] [data-icon=Add]", "Добавить продукт")
        self.PRODUCT_DELETE_BTN = Element(
            "(//*[contains(@id, 'panel-application-products')] //span[@data-icon='Delete'])[1]",
            "Удалить выбранный",
        )
        self.DELETE_ALL_PRODUCTS_BTN = Element(
            "(//*[contains(@id, 'panel-application-products')] //span[@data-icon='Delete'])[2]", "Удалить все"
        )
        self.PRODUCTS = ElementsList(
            "div[id*=products][role=tabpanel] [class*=table-tbody-virtual-holder] [class*=row]", "Продукты"
        )

        # SUBSCRIBERS TAB
        self.SUBSCRIBER_ADD_BTN = Element("[id*=panel-application-subscribers] [data-icon=Add]", "Добавить абонента")
        self.SUBSCRIBER_DELETE_BTN = Element(
            "[id*=panel-application-subscribers] [data-icon=Delete]", "Удалить абонента"
        )
        self.SUBSCRIBERS = ElementsList(
            "div[id*=subscribers][role=tabpanel] [class*=table-tbody-virtual-holder] [class*=row]", "Абоненты"
        )


class AddBillingDiscountOrChargeForm(DynamicForms):
    """Форма 'Добавление биллинговой скидки или доначисления'"""

    def __init__(self) -> None:
        super().__init__()

        self.TYPE = Select("#billingDiscountActionId", "Тип")
        self.TEMPLATE = Element("#billDiscountTemplate", "Шаблон")
        self.PRIORITY = Element("#priority", "Последовательность применения")
        self.START_DATE = DatePicker("#startDateTime", "Начало действия")
        self.END_DATE = DatePicker("#endDateTime", "Окончание действия")
        self.COMMENT = Element("//textarea[@id='comment']", "Комментарий")


class TemplateForm(DynamicForms):
    """Форма 'Доначисление' Шаг 1"""

    def __init__(self) -> None:
        super().__init__()

        self.TEMPLATE_TABLE = VirtualTable("[class*=table-tbody]", "Таблица шаблонов")


class AddProductOfferForm(DynamicForms):
    """Форма 'Добавление продуктового предложения' Шаг 2"""

    def __init__(self) -> None:
        super().__init__()

        self.PRODUCT_TABLE = VirtualTableCheckbox("[class*=table-tbody-virtual-holder-inner]", "Таблица продуктов")


class AddBillingDiscountOrChargeFormStep3(DynamicForms):
    """Форма 'Добавление биллинговой скидки или доначисления' Шаг 3"""

    def __init__(self) -> None:
        super().__init__()

        self.SUBSCRIBERS_TABLE = VirtualTableCheckbox(
            "[class*=table-fixed-column] [class*=table-tbody-virtual-holder-inner]", "Таблица абонентов"
        )


class AddBillingDiscountFormStep4(DynamicForms):
    """Форма 'Назначение биллинговой скидки' Шаг 4"""

    def __init__(self) -> None:
        super().__init__()

        self.VALUE = Element("[style*='block;'] input[role=spinbutton]", "Значение")
        self.EDIT_VALUE = Element("input[role=spinbutton][id=attributeValue]", "Поле Значение во время редактирования")
        self.SET_BTN = Element(
            "(//*[contains(@class, 'drawer-open')]//div[contains(@class, 'drawer-footer')]//button)[2]",
            "Назначить",
        )
        self.INFO = Element("[id*=attribute][id*=help] > [class*=item-explain]", "Сообщение под полем с вводом значения")


class FilterForm(DynamicForms):
    """Форма 'Фильтры'"""

    def __init__(self) -> None:
        super().__init__()

        self.TYPE = Select("input[type=search]", "Тип")
        self.START_DATE = DatePicker("(//span[@data-icon='DateRange'])[1]", "Дата начала предоставления")
        self.END_DATE = DatePicker("(//span[@data-icon='DateRange'])[2]", "Дата конца предоставления")
        self.USER = Element("[class*=drawer-body] input[type=text]", "Пользователь")
        self.EDIT_DATE = DatePicker("(//span[@data-icon='DateRange'])[3]", "Дата редактирования")

        self.SET_BTN = Element(
            "(//*[contains(@class, 'drawer-open')]//div[contains(@class, 'drawer-footer')]//button)[3]",
            "Назначить",
        )
