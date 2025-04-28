from playwright.sync_api import Page

from pages.locators.psc_locators.base_elements_psc import BaseElementsPsc
from pages.ui_elements import Element, ElementsList


class ProductProposalDetailsElements(BaseElementsPsc):
    """Страница детали ПП"""

    def __init__(self, page: Page):
        super().__init__(page)

        # HEADER PANEL
        self.PP_STATUS = Element(
            "[data-test='ProductOfferingHeader'] [data-test='PscLabel']", "Статус проекта", self.page
        )
        self.PP_NAME = Element("[data-test='ProductOfferingHeader'] h1", "Название проекта", self.page)
        self.CHARACTERISTICS_TAB = Element("#tab-pov-characteristics", "Таб 'Характеристики'", self.page)
        self.PRICE_TAB = Element("#tab-pov-prices", "Таб 'Характеристики'", self.page)

        # CHARACTERISTICS_TAB
        self.EDIT_BUTTON = Element("[data-test='button:edit']", "Кнопка 'Редактировать'", self.page)
        self.SAVE_BUTTON = Element("[data-test='button:save']", "Кнопка 'Сохранить'", self.page)
        self.CHARACTERISTICS_GROUPS = ElementsList(
            "[data-test='PscTabSwitcher'] div", "Кнопки 'Обязательные|Добавленные|Переопределённые'", self.page
        )
        self.CONNECTION_STANDARD_DROPDOWN_BTN = Element(
            "[data-test*='internalRecurringChargesManagement'] [data-test*='arrow-triangle-down']",
            "Кнопка открытия 'CART управляет периодическими начислениями'",
            self.page,
        )
        self.MULTIPLE_OCCURRENCE_DROPDOWN_BTN = Element(
            "[data-test*='multipleOccurrence'] [data-test*='arrow-triangle-down']",
            "Кнопка открытия 'Возможность одновременного подключения'",
            self.page,
        )
        self.SUBSCRIPTION_TYPE_DROPDOWN_BTN = Element(
            "[data-test*='subscriptionType'] [data-test*='arrow-triangle-down']",
            "Кнопка открытия 'Тип подписки'",
            self.page,
        )
        self.OWNER_TYPE_DROPDOWN_BTN = Element(
            "[data-test*='ownerType'] [data-test*='arrow-triangle-down']", "Кнопка открытия 'Тип владельца'", self.page
        )
        self.PRODUCT_TECHNICAL_DROPDOWN_BTN = Element(
            "[data-test*='productTechnicalLabel'] [data-test*='arrow-triangle-down']",
            "Кнопка открытия 'Технические метки'",
            self.page,
        )
        self.CONTROL_PRODUCT_CHARGE_DROPDOWN_BTN = Element(
            "[data-test*='controlProductCharge'] [data-test*='arrow-triangle-down']",
            "Кнопка открытия 'Не предоставлять услуги при неоплате продукта'",
            self.page,
        )
        self.NUM_COLOR_DROPDOWN_BTN = Element(
            "[data-test*='connectionType'] [data-test*='arrow-triangle-down']",
            "Кнопка открытия 'Цвет номера'",
            self.page,
        )
        self.NUM_COLOR_SETTING_BTN = Element(
            "[data-test*='connectionType'] button.el-button--mini", "Кнопка 'Настроить доступные значения'", self.page
        )
        self.PRODUCT_PP_DROPDOWN_BTN = Element(
            "[data-test*='productOfferingCategory'] [data-test*='arrow-triangle-down']",
            "Кнопка открытия 'Категория ПП'",
            self.page,
        )
        self.SEGMENT_DROPDOWN_BTN = Element(
            "[data-test*='segment'] [data-test*='arrow-triangle-down']", "Кнопка открытия 'Сегмент'", self.page
        )
        self.APPLY_LIMITS_DROPDOWN_BTN = Element(
            "[data-test*='applyLimitsToMainAccount'] [data-test*='arrow-triangle-down']",
            "Кнопка открытия 'Использование лимитов на основном счете'",
            self.page,
        )
        self.CHARACTERISTIC_MENU = ElementsList("[data-test='ElButton:show-menu']", "Меню 'Характеристики'", self.page)
        self.META_CHARACTERISTIC_BTN = ElementsList(
            "[data-test='ElDropdownItem:OPEN_META_CHARS']", "Пункт меню ' Метахарактеристики '", self.page
        )

        # CHOOSE NUMBER COLOR FORM
        self.NUM_COLOR_CHECKBOXES = ElementsList(
            "[data-test*='PscTableCellCheckbox']", "Чекбоксы 'Типы номеров'", self.page
        )
        self.APPLY_BTN = Element(".footer > button:last-child", "Кнопка 'Применить'", self.page)

        # PRICE_TAB
        self.TABLE_PRICE_NAME = ElementsList("[data-test*='PscLinkButton']", "Ячейки таблицы 'Название цены'", self.page)


class CreatePriceFormElements(BaseElementsPsc):
    """Форма Добавление цены ПП"""

    def __init__(self, page: Page):
        super().__init__(page)

        self.CREATE_PRICE_LARGE_BTN = Element(
            "[data-test='PscLargeButton:create']", "Кнопка 'Создать новую цену'", self.page
        )
        self.PRICE_TYPE_DROPDOWN_BTN = Element(
            "[data-test*='price_type'] [data-test*='PscToggleDropdownIcon'] svg", "Кнопка открыть 'Тип цены'", self.page
        )
        self.STEP_NAME = ElementsList("p.header-subtitle", "Название шага формы", self.page)
        self.FORM_VALUES = ElementsList("[data-test*='PscFormItem'] > div:nth-child(2)", "Значения формы", self.page)
        self.ALLOW_PARTIAL_PAYMENT_DROPDOWN_BTN = Element(
            "[data-test*='allowPartialPaymentOnConnect'] [data-test*='arrow-triangle-down']",
            "Кнопка открытия 'Разрешено частичное списание при подключении не с начала месяца'",
            self.page,
        )
        self.PRICE_ROLE_VALUES = ElementsList(
            "[data-test*='priceRole'] .psc-tag-text", "Значения 'Роль цены'", self.page
        )
        self.MAKE_DEBIT_CHARGE_DROPDOWN_BTN = Element(
            "[data-test*='makeDebitCharge'] [data-test*='arrow-triangle-down']",
            "Кнопка открытия 'Признак списания в дебет'",
            self.page,
        )
        self.BILL_DETAILS_DROPDOWN_BTN = Element(
            "[data-test*='billDetails'] [data-test*='arrow-triangle-down']",
            "Кнопка открытия 'Платежная деталь'",
            self.page,
        )
        self.IS_INSTANTIATION_PRICE_DROPDOWN_BTN = Element(
            "[data-test*='isInstantiationPrice'] [data-test*='arrow-triangle-down']",
            "Кнопка открытия 'Цена инстанцируемая'",
            self.page,
        )
        self.CHARACTERISTIC_WEIGHT_DROPDOWN_BTN = Element(
            "[data-test*='characteristicWeight'] [data-test*='arrow-triangle-down']",
            "Кнопка открытия 'Вес характеристики'",
            self.page,
        )
        self.ADD_CHARACTERISTIC_BTN = Element(
            "[data-test='PscDialog'] [data-test='ElButton:add']", "Кнопка '+ Добавить характеристику'", self.page
        )
        self.INTERVAL_ALIGNMENT_DROPDOWN_BTN = Element(
            "[data-test*='intervalAlignment'] [data-test*='arrow-triangle-down']",
            "Кнопка открытия 'Выравнивание интервала'",
            self.page,
        )
        self.PAY_FIN_BLOCK_PERIOD_DROPDOWN_BTN = Element(
            "[data-test*='payFinblockPeriod'] [data-test*='arrow-triangle-down']",
            "Кнопка открытия 'Период оплаты при выходе из финансовой блокировки'",
            self.page,
        )

        self.PRICE_NAME_INPUT = Element(
            "[data-test*='name'] [data-test*='TemplateAttributePropertyItem']:nth-child(2) input",
            "Поле ввода 'Название цены'",
            self.page,
        )
        self.RECURRING_CHARGE_PERIOD_NAME_INPUT = Element(
            "[data-test*='recurringChargePeriod'] [data-test*='TemplateAttributePropertyItem']:nth-child(1) input",
            "Поле ввода 'Название Период возобновления цены'",
            self.page,
        )
        self.RECURRING_CHARGE_PERIOD_QUANTITY_INPUT = Element(
            "[data-test*='recurringChargePeriod'] [data-test*='TemplateAttributePropertyItem']:nth-child(2) input",
            "Поле ввода 'Количество Период возобновления цены'",
            self.page,
        )
        self.RECURRING_CHARGE_PERIOD_DROPDOWN_BTN = Element(
            "[data-test*='recurringChargePeriod'] [data-test*='arrow-triangle-down']",
            "Кнопка открытия 'Единица измерения Период возобновления цены'",
            self.page,
        )
        self.PRIORITY_INPUT = Element(
            "[data-test*='TemplateAttribute:priority'] [data-test*='TemplateAttributePropertyItem']:nth-child(2) input",
            "Поле ввода 'Приоритет скидки'",
            self.page,
        )
        self.UNIT_OF_MEASURE_QUANTITY_INPUT = Element(
            "[data-test*='unitOfMeasure'] [data-test*='TemplateAttributePropertyItem']:nth-child(2) input",
            "Поле ввода 'Количество Единица измерения'",
            self.page,
        )
        self.UNIT_OF_MEASURE_CLASS_DROPDOWN_BTN = Element(
            "[data-test*='unit_of_measure_class'] [data-test*='arrow-triangle-down']",
            "Кнопка открытия 'Класс единиц измерения Единица измерения'",
            self.page,
        )
        self.UNIT_OF_MEASURE_UNIT_DROPDOWN_BTN = Element(
            "[data-test*='unitOfMeasure'] [data-test*='TemplateAttributePropertyItem']:nth-child(4)  [data-test*='arrow-triangle-down']",
            "Кнопка открытия 'Единица измерения - Единица измерения'",
            self.page,
        )
        self.PRICE_QUANTITY_INPUT = Element(
            "[data-test*='TemplateAttribute:price'] [data-test*='TemplateAttributePropertyItem']:nth-child(2) input",
            "Поле ввода 'Количество Цена'",
            self.page,
        )
        self.PRICE_TAX_DROPDOWN_BTN = Element(
            "[data-test*='Attribute:pric'] [data-test*='PropertyItem']:nth-child(3) [data-test*='arrow-triangle-down']",
            "Кнопка открытия 'Налоги Цена'",
            self.page,
        )
        self.CURRENCY_DROPDOWN_BTN = Element(
            "[data-test*='Attribute:price'] [data-test*='PropertyItem']:nth-child(4) [data-test*='arrow-triangle-down']",
            "Кнопка открытия 'Валюта Цена'",
            self.page,
        )
        self.DONE_BTN = Element("button.button-done", "Кнопка 'Готово'", self.page)
