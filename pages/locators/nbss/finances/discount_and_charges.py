from playwright.sync_api import Page

from pages.locators.dynamic_form_elements import DynamicForms
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

    def __init__(self, page: Page):
        super().__init__(page)

        self.SET_BTN = Element("div[class*=platform-toolbar] >div:not([style]) span[data-icon=Add]", "Назначить", page)
        self.FILTER_BTN = Element(
            "[class*=extra-tools] > div > div:not([style]) [data-icon=FilterSettings]", "Фильтры", page
        )
        self.MORE_BTN = Dropdown(
            "[class*=extra-tools] > div > div:not([style]) [data-icon=ArrowDropDown]", "Фильтры", page
        )
        self.DISCOUNTS = ElementsList(".platform-custom-list-scrollable-body > div:not([class*=empty])", "Скидки", page)

        self.DISCOUNT_EDIT_BTN = Element("[data-icon=Edit]", "Редактировать", page)
        self.DISCOUNT_DELETE_BTN = Element("[data-icon=Delete]", "Редактировать", page)

        # TABS
        self.PROPERTIES_TAB = Element("[data-node-key=properties]", "Таб Свойства", page)
        self.CONDITIONS_TAB = Element("[data-node-key=conditions-applicability]", "Таб Условия применимости", page)
        self.PRODUCTS_TAB = Element("[data-node-key=application-products]", "Таб Применение к продуктам", page)
        self.SUBSCRIBERS_TAB = Element("[data-node-key=application-subscribers]", "Таб Применение к абонентам", page)

        # PROPERTIES TAB
        self.PROPERTIES = ElementsList(
            "[aria-labelledby*=tab-properties] > div > div > div:nth-of-type(2)", "Свойства скидки", page
        )

        # CONDITIONS TAB
        self.CONDITIONS = ElementsList(
            "[id*=panel-conditions-applicability] [class*=custom-list-scrollable-body] > div", "Условия", page
        )
        self.CONDITION_ATTR_EDIT_BTN = Element(
            "[id*=panel-conditions-applicability] > div > div > div:nth-of-type(2) button", "Редактировать", page
        )
        self.DISCOUNT_VALUE = Element(
            "((//*[contains(@id, 'panel-conditions-applicability')] /div /div /div[2] /div[2]) //div)[5]",
            "Размер скидки",
            page,
        )
        self.THRESHOLD_AMOUNT = Element(
            "((//*[contains(@id, 'panel-conditions-applicability')] /div /div /div[2] /div[2]) //div)[8]",
            "Порог суммы",
            page,
        )

        # PRODUCTS TAB
        self.PRODUCT_ADD_BTN = Element("[id*=panel-application-products] [data-icon=Add]", "Добавить продукт", page)
        self.PRODUCTS = ElementsList("[class*=table-tbody-virtual-holder-inner] [class*=row]", "Продукты", page)

        # SUBSCRIBERS TAB
        self.SUBSCRIBER_ADD_BTN = Element(
            "[id*=panel-application-subscribers] [data-icon=Add]", "Добавить абонента", page
        )
        self.SUBSCRIBERS = ElementsList("[class*=table-tbody-virtual-holder-inner] [class*=row]", "Абоненты", page)


class AddBillingDiscountOrChargeForm(DynamicForms):
    """Форма 'Добавление биллинговой скидки или доначисления'"""

    def __init__(self, page: Page):
        super().__init__(page)

        self.TYPE = Select("#billingDiscountActionId", "Тип", page)
        self.TEMPLATE = Element("#billDiscountTemplate", "Шаблон", page)
        self.PRIORITY = Element("#priority", "Последовательность применения", page)
        self.START_DATE = DatePicker("#startDateTime", "Начало действия", page)
        self.END_DATE = DatePicker("#endDateTime", "Окончание действия", page)
        self.COMMENT = Element("#comment", "Комментарий", page)


class TemplateForm(DynamicForms):
    """Форма 'Доначисление' Шаг 1"""

    def __init__(self, page: Page):
        super().__init__(page)

        self.TEMPLATE_TABLE = VirtualTable("[class*=table-tbody-virtual-holder-inner]", "Таблица шаблонов", page)


class AddProductOfferForm(DynamicForms):
    """Форма 'Добавление продуктового предложения' Шаг 2"""

    def __init__(self, page: Page):
        super().__init__(page)

        self.PRODUCT_TABLE = VirtualTableCheckbox("[class*=table-tbody-virtual-holder-inner]", "Таблица продуктов", page)


class AddBillingDiscountOrChargeFormStep3(DynamicForms):
    """Форма 'Добавление биллинговой скидки или доначисления' Шаг 3"""

    def __init__(self, page: Page):
        super().__init__(page)

        self.ABONENT_TABLE = VirtualTableCheckbox("[class*=table-tbody-virtual-holder-inner]", "Таблица абонентов", page)


class AddBillingDiscountFormStep4(DynamicForms):
    """Форма 'Назначение биллинговой скидки' Шаг 4"""

    def __init__(self, page: Page):
        super().__init__(page)

        self.VALUE = Element("[role=spinbutton]", "Значение", page)
        self.SET_BTN = Element(
            "(//*[contains(@class, 'drawer-open')]//div[contains(@class, 'drawer-footer')]//button)[2]",
            "Назначить",
            self.page,
        )


class FilterForm(DynamicForms):
    """Форма 'Фильтры'"""

    def __init__(self, page: Page):
        super().__init__(page)

        self.TYPE = Select("input[type=search]", "Тип", page)
        self.START_DATE = DatePicker("(//span[@data-icon='DateRange'])[1]", "Дата начала предоставления", page)
        self.END_DATE = DatePicker("(//span[@data-icon='DateRange'])[2]", "Дата начала предоставления", page)
        self.USER = Element("[class*=drawer-body] input[type=text]", "Пользователь", page)
        self.EDIT_DATE = DatePicker("(//span[@data-icon='DateRange'])[3]", "Дата начала предоставления", page)

        self.SET_BTN = Element(
            "(//*[contains(@class, 'drawer-open')]//div[contains(@class, 'drawer-footer')]//button)[3]",
            "Назначить",
            self.page,
        )
