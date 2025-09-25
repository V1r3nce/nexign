from playwright.sync_api import Page

from pages.locators.dynamic_form_elements import DynamicForms
from pages.ui_elements import (
    DatePicker,
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
        self.DISCOUNTS = ElementsList(".platform-custom-list-scrollable-body > div", "Скидки", page)

        self.DISCOUNT_EDIT_BTN = Element("[data-icon=Edit]", "Редактировать", page)
        self.DISCOUNT_DELETE_BTN = Element("[data-icon=Delete]", "Редактировать", page)

        # PROPERTIES TABLE
        self.PROPERTIES = ElementsList(
            "[aria-labelledby*=tab-properties] > div > div > div:nth-of-type(2)", "Свойства скидки", page
        )


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
