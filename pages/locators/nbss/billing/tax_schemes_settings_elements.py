from pages.locators.nbss.dynamic_form_elements import DynamicForms
from pages.ui_elements import (
    Element,
    ElementsList,
    RadioOrCheckboxBlock,
    SelectWithId,
)


class TaxSchemesSettingsElements(DynamicForms):
    """Страница 'Схемы налогообложения'"""

    def __init__(self) -> None:
        super().__init__()

        self.ADD_TAX_BUTTON = Element("[id*=Add]", "Кнопка добавления налога")
        self.TAB_TAX_SCHEME = Element("[data-node-key*=taxSchemes]", "Таб Схемы налогообложения")

        self.NAME_TAX_SCHEME = ElementsList("[id=name][type]", "Название схемы налогообложения")
        self.NON_TAXABLE_CHECKBOX = RadioOrCheckboxBlock("#isUntaxed", "Чекбокс 'Необлагаемая'")
        self.TAB_EXCEPTION = Element("[id*=exceptions]", "Таб 'Исключения'")
        self.ADD_EXCEPTION_BUTTON = Element("[id*=panel-exceptions] button", "Кнопка Добавления Исключения")
        self.BILLING_DETAIL = SelectWithId("billDetailId", "Поле 'Биллинговая деталь'")
        self.REDEFINED_SCHEME = SelectWithId("redefinedTaxSchemeId", "Поле 'Переопределенная схема'")
        self.EXCEPTION_ROW = Element("[id*=panel-exceptions] [class*=row]", "Поля в таблице 'Исключения'")
        self.DETAIL_TAX_SCHEME_ROW = Element(
            "[id*=panel-charge] [class*=row]", "Поля в таблице 'Детали переопределеяемой схемы"
        )
        self.ACCEPT_EXCEPTION_BUTTON = Element(
            "(//button[@id='_accept-button'])[2]", "Кнопка 'Добавить' в форме исключений"
        )
