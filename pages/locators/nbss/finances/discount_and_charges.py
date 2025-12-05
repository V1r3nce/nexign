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


class DiscountAndCharges(DynamicForms):
    """Страница 'Скидки/Доначисления'"""

    def __init__(self) -> None:
        super().__init__()

        self.SET_BTN = Element("div[class*=platform-toolbar] >div:not([style]) span[data-icon=Add]", "Назначить")
        self.FILTER_BTN = Element("[class*=extra-tools] > div > div:not([style]) [data-icon=FilterSettings]", "Фильтры")
        self.MORE_BTN = Dropdown("[class*=extra-tools] > div > div:not([style]) [data-icon=ArrowDropDown]", "Еще")
        self.DISCOUNTS = ElementsList(".platform-custom-list-scrollable-body > div:not([class*=empty])", "Скидки")

        self.DISCOUNT_EDIT_BTN = Element("[data-icon=Edit]", "Редактировать")
        self.DISCOUNT_DELETE_BTN = Element("[data-icon=Delete]", "Редактировать")

        # TABS
        self.PROPERTIES_TAB = Element("[data-node-key=properties]", "Таб Свойства")
        self.CONDITIONS_TAB = Element("[data-node-key=conditions-applicability]", "Таб Условия применимости")
        self.PRODUCTS_TAB = Element("[data-node-key=application-products]", "Таб Применение к продуктам")
        self.SUBSCRIBERS_TAB = Element("[data-node-key=application-subscribers]", "Таб Применение к абонентам")

        # PROPERTIES TAB
        self.PROPERTIES = ElementsList(
            "[aria-labelledby*=tab-properties] > div > div > div:nth-of-type(2)", "Свойства скидки"
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
        self.PRODUCTS = ElementsList("[class*=table-tbody-virtual-holder-inner] [class*=row]", "Продукты")

        # SUBSCRIBERS TAB
        self.SUBSCRIBER_ADD_BTN = Element("[id*=panel-application-subscribers] [data-icon=Add]", "Добавить абонента")
        self.SUBSCRIBER_DELETE_BTN = Element(
            "[id*=panel-application-subscribers] [data-icon=Delete]", "Удалить абонента"
        )
        self.SUBSCRIBERS = ElementsList("[class*=table-tbody-virtual-holder-inner] [class*=row]", "Абоненты")


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

        self.TEMPLATE_TABLE = VirtualTable("[class*=table-tbody-virtual-holder-inner]", "Таблица шаблонов")


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

        self.VALUE = Element("[role=spinbutton]", "Значение")
        self.SET_BTN = Element(
            "(//*[contains(@class, 'drawer-open')]//div[contains(@class, 'drawer-footer')]//button)[2]",
            "Назначить",
        )


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
