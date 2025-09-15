from playwright.sync_api import Page

from pages.locators.base_elements import BaseElements
from pages.ui_elements import CheckboxBlock, Element, ElementsList, RadioOrCheckboxBlock, Select


class SelectProductOffersForm(BaseElements):
    """Форма 'Выбор продуктовых предложений'"""

    def __init__(self, page: Page):
        super().__init__(page)

        self.TITLE = Element("[class*=drawer-title] h3", "Заголовок формы", self.page)
        self.ADDRESS = Select("//input[contains(@id, 'address')]", "Адрес", self.page)
        self.PRODUCT_SEARCH = Element("#productOfferingName", "Поиск", self.page)
        self.EXPRESS_PTV = Select(
            "//button[span[.='Экспресс ПТВ']]", "Экспресс ПТВ", self.page
        )  # требует дата атрибута от фронтов
        self.SHOW_ONLY_CHOOSE_BTN = Element(
            "//*[contains(@class, 'drawer-body')] //button[@id='switch']/../../..",
            "Переключатель 'Показать только выбранные'",
            self.page,
        )
        self.PRODUCT_TYPE = RadioOrCheckboxBlock("#productType", "Тип продукта", self.page)
        self.PRODUCT_CATEGORY = RadioOrCheckboxBlock("#productOfferingCategoryCodes", "Категория", self.page)
        self.PRODUCT_CATEGORY_CHECKBOX = CheckboxBlock("#productOfferingCategoryCodes", "Категория", self.page)
        self.TECHNOLOGY = CheckboxBlock("#technologies", "Технологии", self.page)
        self.CLEAR_FILTER_BTN = Element("//button[.='Сбросить']", "Сбросить", self.page)
        self.SEARCH_BTN = Element("//button[.='Найти']", "Найти", self.page)

        self.CANCEL_BTN = Element("#_cancel-button", "Отмена", self.page)
        self.ADD_BTN = Element("#_accept-button", "Добавить", self.page)

        # PRODUCT_CARD
        self.PRODUCT_CARD = ElementsList(
            "//*[contains(@class, 'card-body')]/../../*[contains(@class, 'card')]", "Карточка продукта", self.page
        )
        self.PRODUCT_CARD_NAME = ElementsList("[class*=card-head-title] h4", "Название товара", self.page)
        self.PRODUCT_CARD_SELECT_BTN = ElementsList(
            "[id=card_buttons] button:nth-child(1)", "Выбрать карточку продукта", self.page
        )
        self.PRODUCT_CARD_PRODUCTS = ElementsList(
            "[class*=card-body] > div:first-child div:not([paddingright]) > p:not([color])", "Продукты бандла", self.page
        )
        self.PRODUCT_CARD_DETAILS = ElementsList(
            "[class*=card-body] button[variant=secondary]", "Детали карточки продукта", self.page
        )
        self.PRODUCT_SINGLE_PAYMENTS = ElementsList(
            "div[id=card_prices] div div:nth-child(1) div h4",
            "Поля 'Разовый платеж' продукта",
            self.page,
        )
        self.PRODUCT_CARD_SUMS = ElementsList(
            "div[id=card_prices] div div:nth-child(3) h4",
            "Поля 'Абонентская плата' продукта",
            self.page,
        )
