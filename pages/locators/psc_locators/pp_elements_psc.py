from pages.locators.psc_locators.base_elements_psc import BaseElementsPsc
from pages.ui_elements import Element, ElementsList


class ProductProposalDetailsElements(BaseElementsPsc):
    """Страница детали ПП"""

    def __init__(self) -> None:
        super().__init__()

        # HEADER PANEL
        self.PP_STATUS = Element("[data-test='ProductOfferingHeader'] [data-test='PscLabel']", "Статус проекта")
        self.PP_NAME = Element("[data-test='ProductOfferingHeader'] h1", "Название проекта")
        self.PROJECT_LINK = Element("[data-test*='reference'] a", "Ссылка на проект ПП")
        self.CHARACTERISTICS_TAB = Element("#tab-pov-characteristics", "Таб 'Характеристики'")
        self.PRICE_TAB = Element("#tab-pov-prices", "Таб 'Цена'")
        self.RULES_TAB = Element("#tab-pov-policy-sets", "Таб 'Правила'")

        # CHARACTERISTICS_TAB
        self.EDIT_BUTTON = Element("[data-test='button:edit']", "Кнопка 'Редактировать'")
        self.SAVE_BUTTON = Element("[data-test='button:save']", "Кнопка 'Сохранить'")
        self.CHARACTERISTICS_GROUPS = ElementsList(
            "[data-test='PscTabSwitcher'] div", "Кнопки 'Обязательные|Добавленные|Переопределённые'"
        )
        self.CONNECTION_STANDARD_DROPDOWN_BTN = Element(
            "[data-test*='internalRecurringChargesManagement'] [data-test*='arrow-triangle-down']",
            "Кнопка открытия 'CART управляет периодическими начислениями'",
        )
        self.MULTIPLE_OCCURRENCE_DROPDOWN_BTN = Element(
            "[data-test*='multipleOccurrence'] [data-test*='arrow-triangle-down']",
            "Кнопка открытия 'Возможность одновременного подключения'",
        )
        self.SUBSCRIPTION_TYPE_DROPDOWN_BTN = Element(
            "[data-test*='subscriptionType'] [data-test*='arrow-triangle-down']",
            "Кнопка открытия 'Тип подписки'",
        )
        self.OWNER_TYPE_DROPDOWN_BTN = Element(
            "[data-test*='ownerType'] [data-test*='arrow-triangle-down']", "Кнопка открытия 'Тип владельца'"
        )
        self.PRODUCT_TECHNICAL_DROPDOWN_BTN = Element(
            "[data-test*='productTechnicalLabel'] [data-test*='arrow-triangle-down']",
            "Кнопка открытия 'Технические метки'",
        )
        self.CONTROL_PRODUCT_CHARGE_DROPDOWN_BTN = Element(
            "[data-test*='controlProductCharge'] [data-test*='arrow-triangle-down']",
            "Кнопка открытия 'Не предоставлять услуги при неоплате продукта'",
        )
        self.NUM_COLOR_DROPDOWN_BTN = Element(
            "[data-test*='connectionType'] [data-test*='arrow-triangle-down']",
            "Кнопка открытия 'Цвет номера'",
        )
        self.NUM_COLOR_SETTING_BTN = Element(
            "[data-test*='connectionType'] button.el-button--mini", "Кнопка 'Настроить доступные значения'"
        )
        self.PRODUCT_PP_DROPDOWN_BTN = Element(
            "[data-test*='productOfferingCategory'] [data-test*='arrow-triangle-down']",
            "Кнопка открытия 'Категория ПП'",
        )
        self.SEGMENT_DROPDOWN_BTN = Element(
            "[data-test*='segment'] [data-test*='arrow-triangle-down']", "Кнопка открытия 'Сегмент'"
        )
        self.APPLY_LIMITS_DROPDOWN_BTN = Element(
            "[data-test*='applyLimitsToMainAccount'] [data-test*='arrow-triangle-down']",
            "Кнопка открытия 'Использование лимитов на основном счете'",
        )
        self.CHARACTERISTIC_MENU = ElementsList("[data-test='ElButton:show-menu']", "Меню 'Характеристики'")
        self.META_CHARACTERISTIC_BTN = ElementsList(
            "[data-test='ElDropdownItem:OPEN_META_CHARS']", "Пункт меню ' Метахарактеристики '"
        )

        # CHOOSE NUMBER COLOR FORM
        self.NUM_COLOR_CHECKBOXES = ElementsList("[data-test*='PscTableCellCheckbox']", "Чекбоксы 'Типы номеров'")
        self.APPLY_BTN = Element(".footer > button:last-child", "Кнопка 'Применить'")

        # TABS_TABLE
        self.TABLE_NAME_LINK_FIELDS = ElementsList(
            "[data-test*='PscLinkButton']", "Ячейки таблицы 'Название(с ссылкой)'"
        )

        # RULES_TAB
        self.ADD_RULE_BTN = Element("[data-test*='create-policy-set-button']", "Кнопка 'Добавить набор правил'")


class CreatePriceFormElements(BaseElementsPsc):
    """Форма Добавление цены ПП"""

    def __init__(self) -> None:
        super().__init__()

        self.CREATE_PRICE_LARGE_BTN = Element("[data-test='PscLargeButton:create']", "Кнопка 'Создать новую цену'")
        self.PRICE_TYPE_DROPDOWN_BTN = Element(
            "[data-test*='price_type'] [data-test*='PscToggleDropdownIcon'] svg", "Кнопка открыть 'Тип цены'"
        )
        self.STEP_NAME = ElementsList("p.header-subtitle", "Название шага формы")
        self.FORM_VALUES = ElementsList("[data-test*='PscFormItem'] > div:nth-child(2)", "Значения формы")
        self.ALLOW_PARTIAL_PAYMENT_DROPDOWN_BTN = Element(
            "[data-test*='allowPartialPaymentOnConnect'] [data-test*='arrow-triangle-down']",
            "Кнопка открытия 'Разрешено частичное списание при подключении не с начала месяца'",
        )
        self.PRICE_ROLE_VALUES = ElementsList("[data-test*='priceRole'] .psc-tag-text", "Значения 'Роль цены'")
        self.COUNTER_REPORT_THRESHOLD_VALUES = ElementsList(
            "[data-test*='priceCounterReportThreshold'] .psc-tag-text",
            "Значения 'Порог для формирования нотификации'",
        )
        self.MAKE_DEBIT_CHARGE_DROPDOWN_BTN = Element(
            "[data-test*='makeDebitCharge'] [data-test*='arrow-triangle-down']",
            "Кнопка открытия 'Признак списания в дебет'",
        )
        self.BILL_DETAILS_DROPDOWN_BTN = Element(
            "[data-test*='billDetails'] [data-test*='arrow-triangle-down']",
            "Кнопка открытия 'Платежная деталь'",
        )
        self.IS_INSTANTIATION_PRICE_DROPDOWN_BTN = Element(
            "[data-test*='isInstantiationPrice'] [data-test*='arrow-triangle-down']",
            "Кнопка открытия 'Цена инстанцируемая'",
        )
        self.CHARACTERISTIC_WEIGHT_DROPDOWN_BTN = Element(
            "[data-test*='characteristicWeight'] [data-test*='arrow-triangle-down']",
            "Кнопка открытия 'Вес характеристики'",
        )
        self.ADD_CHARACTERISTIC_BTN = Element(
            "[data-test='PscDialog'] [data-test='ElButton:add']", "Кнопка '+ Добавить характеристику'"
        )
        self.INTERVAL_ALIGNMENT_DROPDOWN_BTN = Element(
            "[data-test*='intervalAlignment'] [data-test*='arrow-triangle-down']",
            "Кнопка открытия 'Выравнивание интервала'",
        )
        self.PAY_FIN_BLOCK_PERIOD_DROPDOWN_BTN = Element(
            "[data-test*='payFinblockPeriod'] [data-test*='arrow-triangle-down']",
            "Кнопка открытия 'Период оплаты при выходе из финансовой блокировки'",
        )

        self.PRICE_NAME_INPUT = Element(
            "[data-test*='name'] [data-test*='TemplateAttributePropertyItem']:nth-child(2) input",
            "Поле ввода 'Название цены'",
        )
        self.RECURRING_CHARGE_PERIOD_NAME_INPUT = Element(
            "[data-test*='recurringChargePeriod'] [data-test*='TemplateAttributePropertyItem']:nth-child(1) input",
            "Поле ввода 'Название Период возобновления цены'",
        )
        self.RECURRING_CHARGE_PERIOD_QUANTITY_INPUT = Element(
            "[data-test*='recurringChargePeriod'] [data-test*='TemplateAttributePropertyItem']:nth-child(2) input",
            "Поле ввода 'Количество Период возобновления цены'",
        )
        self.RECURRING_CHARGE_PERIOD_DROPDOWN_BTN = Element(
            "[data-test*='recurringChargePeriod'] [data-test*='arrow-triangle-down']",
            "Кнопка открытия 'Единица измерения Период возобновления цены'",
        )
        self.PRIORITY_INPUT = Element(
            "[data-test*='TemplateAttribute:priority'] [data-test*='TemplateAttributePropertyItem']:nth-child(2) input",
            "Поле ввода 'Приоритет скидки'",
        )
        self.UNIT_OF_MEASURE_QUANTITY_INPUT = Element(
            "[data-test*='unitOfMeasure'] [data-test*='TemplateAttributePropertyItem']:nth-child(2) input",
            "Поле ввода 'Количество Единица измерения'",
        )
        self.UNIT_OF_MEASURE_CLASS_DROPDOWN_BTN = Element(
            "[data-test*='unit_of_measure_class'] [data-test*='arrow-triangle-down']",
            "Кнопка открытия 'Класс единиц измерения Единица измерения'",
        )
        self.UNIT_OF_MEASURE_UNIT_DROPDOWN_BTN = Element(
            "[data-test*='unitOfMeasure'] [data-test*='TemplateAttributePropertyItem']:nth-child(4)"
            "  [data-test*='arrow-triangle-down']",
            "Кнопка открытия 'Единица измерения - Единица измерения'",
        )
        self.PRICE_QUANTITY_INPUT = Element(
            "[data-test*='TemplateAttribute:price'] [data-test*='TemplateAttributePropertyItem']:nth-child(2) input",
            "Поле ввода 'Количество Цена'",
        )
        self.PRICE_TAX_DROPDOWN_BTN = Element(
            "[data-test*='Attribute:pric'] [data-test*='PropertyItem']:nth-child(3) [data-test*='arrow-triangle-down']",
            "Кнопка открытия 'Налоги Цена'",
        )
        self.CURRENCY_DROPDOWN_BTN = Element(
            "[data-test*='Attribute:price'] [data-test*='PropertyItem']:nth-child(4) [data-test*='arrow-triangle-down']",
            "Кнопка открытия 'Валюта Цена'",
        )
        self.DONE_BTN = Element("button.button-done", "Кнопка 'Готово'")
        self.MAX_VOLUME_QUANTITY_INPUT = Element(
            "[data-test*='maxVolume'] [data-test*='TemplateAttributePropertyItem']:nth-child(2) input",
            "Поле ввода 'Количество Максимальный объем'",
        )
        self.MAX_VOLUME_UNIT_DROPDOWN_BTN = Element(
            "[data-test*='maxVolume'] [data-test*='arrow-triangle-down']",
            "Кнопка открытия 'Единица измерения Максимальный объем'",
        )


class CreateRuleFormElements(BaseElementsPsc):
    """Форма Добавление набора правил ПП"""

    def __init__(self) -> None:
        super().__init__()

        self.CHOOSE_RULE_LARGE_BTN = Element(
            "[data-test='PscLargeButton:select-rule']", "Кнопка 'Выбрать набор правил из базы'"
        )
        self.SEARCH_NAME_INPUT = Element(
            "[data-test*='PolicySetCreateSelectFromBase'] [data-test*='name-id'] input",
            "Поле ввода 'Наименование или ID'",
        )
