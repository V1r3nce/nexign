from pages.locators.nbss.dynamic_form_elements import DynamicForms
from pages.ui_elements import (
    Autocomplete,
    DatePicker,
    Element,
    ElementsList,
    RadioOrCheckboxBlock,
    ScrollableList,
    SelectWithId,
)


class TaxAndTaxSchemesSettingsElements(DynamicForms):
    """Страница 'Схемы налогообложения'"""

    def __init__(self) -> None:
        super().__init__()

        self.ADD_TAX_BUTTON = Element(
            "[class$=platform-toolbar] > div:not([style]) button:has([data-icon=Add])",
            "Кнопка добавления Схемы налогообложения",
        )
        self.REFRESH_BTN = Element(
            "[class*=platform-custom-list-extra-tools] > div:first-child > div:first-child button [data-icon=Refresh]",
            "Кнопка 'Обновить'",
        )

        # TABS
        self.TAX_SCHEMES_TAB = Element("[data-node-key='taxSchemes']", "Вкладка 'Схемы налогообложения'")

        # LISTS
        self.TAX_SCHEMES = ScrollableList(
            path="[id*=panel-taxes] [class*=list-scrollable-body]",
            item_path="p[data-name=paragraphMedium]",
            locator_name="Список схем налогообложения",
        )
        self.TAX_SCHEME_VERSIONS = ElementsList(
            "[id*=panel-taxSchemes] .platform-custom-list:has([data-icon=ContentCopy]) [class*=list-scrollable-body] p[data-name=paragraphMedium]",
            "Список версий налоговой схемы",
        )

        # TAX_CREATION_FORM
        self.TAX_CREATION_TITLE = Element(
            "[class*=drawer-content] [class*=drawer-title] h3", "Заголовок формы 'Создание налога'"
        )
        self.TAX_NAME = ElementsList("#name", "Название при создании налога или схемы налогообложения")
        self.TAX_RATE = Element("#rate", "Ставка налога")
        self.START_DATE_SELECTION = DatePicker("input[id*=startDate] ", "Поле 'дата начала' на форме создания налогов")

        # TAX_SCHEME_FORM
        self.ADD_TAX_TO_SCHEME = Element(
            "[class*=drawer-content][role=dialog] [class*=tabs-content] button[type=button][class*=variant-text]",
            "Кнопка 'Добавить' на форме создания новой схемы налогообложения",
        )
        self.TAX_SELECT_FIELD = Autocomplete("#taxId", "Поле выбора налога из существующих")
        self.ADD_TAX_ACCEPT_BTN = ElementsList("#_accept-button", "Кнопка подтверждения добавления налога в схему")
        self.MAKE_TAX_SCHEME_INVISIBLE = Element("#isInvisible", "Чекбокс 'Невидимая' для налоговой схемы")
        self.NON_TAXABLE_CHECKBOX = RadioOrCheckboxBlock("#isUntaxed", "Чекбокс 'Необлагаемая'")

        # TAX_SCHEME_VERSION_DETAILS
        self.VERSION_NAME = ElementsList("[class*=tabs-content] header h3", "Поле с названием для налоговой схемы")
        self.VERSION_STATUS = ElementsList("[class*=tabs-content] header span", "Поле со статусом для налоговой схемы")
        self.TAX_DATES = ElementsList(
            "[id*=panel-taxes] [data-testid] p[data-name=paragraph]", "Даты начала и окончания схемы налогообложения"
        )
        self.TAX_SCHEMES_CHARGES_TAB = Element("[data-node-key=charge]", "Вкладка 'Начисления' на форме налоговой схемы")
        self.TAX_SCHEMES_ADVANCES_TAB = Element("[data-node-key=advance]", "Вкладка 'Авансы' на форме налоговой схемы")
        self.TAB_EXCEPTION = Element("[id*=exceptions]", "Таб 'Исключения'")
        self.COPY_BUTTON = Element(
            "[class*=platform-toolbar] > div:not([style]) button:has([data-icon=ContentCopy])", "Кнопка 'Копировать'"
        )
        self.ADD_EXCEPTION_BUTTON = Element("[id*=panel-exceptions] button", "Кнопка Добавления Исключения")
        self.BILLING_DETAIL = SelectWithId("billDetailId", "Поле 'Биллинговая деталь'")
        self.REDEFINED_SCHEME = SelectWithId("redefinedTaxSchemeId", "Поле 'Переопределенная схема'")
        self.EXCEPTION_ROW = Element("[id*=panel-exceptions] [class*=row]", "Поля в таблице 'Исключения'")
        self.DETAIL_TAX_SCHEME_ROW = Element(
            "[id*=panel-charge] [class*=row]", "Поля в таблице 'Детали переопределеяемой схемы"
        )
