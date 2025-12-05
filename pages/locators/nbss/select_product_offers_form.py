from pages.locators.base_elements import BaseElements
from pages.ui_elements import CheckboxBlock, Element, ElementsList, RadioOrCheckboxBlock, Select


class SelectProductOffersForm(BaseElements):
    """Форма 'Выбор продуктовых предложений'"""

    def __init__(self) -> None:
        super().__init__()

        self.TITLE = Element("[class*=drawer-title] h3", "Заголовок формы")
        self.ADDRESS = Select("//input[contains(@id, 'address')]", "Адрес")
        self.PRODUCT_SEARCH = Element("#productOfferingName", "Поиск")
        self.EXPRESS_PTV = Select("//button[span[.='Экспресс ПТВ']]", "Экспресс ПТВ")  # требует дата атрибута от фронтов
        self.SHOW_ONLY_CHOOSE_BTN = Element(
            "//*[contains(@class, 'drawer-body')] //button[@id='switch']/../../..",
            "Переключатель 'Показать только выбранные'",
        )
        self.PRODUCT_TYPE = RadioOrCheckboxBlock("#productType", "Тип продукта")
        self.PRODUCT_CATEGORY = RadioOrCheckboxBlock("#productOfferingCategoryCodes", "Категория")
        self.PRODUCT_CATEGORY_CHECKBOX = CheckboxBlock("#productOfferingCategoryCodes", "Категория")
        self.PRODUCT_CATEGORY_NAMES = ElementsList(
            "#productOfferingCategoryCodes span[class*='radio-label']", "Названия категорий продуктов"
        )
        self.TECHNOLOGY = CheckboxBlock("#technologies", "Технологии")
        self.CLEAR_FILTER_BTN = Element("//button[.='Сбросить']", "Сбросить")
        self.SEARCH_BTN = Element("//button[.='Найти']", "Найти")

        self.CANCEL_BTN = Element("#_cancel-button", "Отмена")
        self.ADD_BTN = Element("[class*=drawer-open] #_accept-button", "Добавить")

        # PRODUCT_CARD
        self.PRODUCT_CARD = ElementsList(
            "//*[contains(@class, 'card-body')]/../../*[contains(@class, 'card')]", "Карточка продукта"
        )
        self.PRODUCT_CARD_NAME = ElementsList("[class*=card-head-title] h4", "Название товара")
        self.PRODUCT_CARD_SELECT_BTN = ElementsList("[id=card_buttons] button:nth-child(1)", "Выбрать карточку продукта")
        self.PRODUCT_CARD_PRODUCTS = ElementsList(
            "[class*=card-body] > div:first-child > div:not([paddingright]):not(#card_prices) > p:not([color])",
            "Продукты бандла",
        )
        self.PRODUCT_CARD_DETAILS = ElementsList(
            "[class*=card-body] button[variant=secondary]", "Детали карточки продукта"
        )
        self.PRODUCT_SINGLE_PAYMENTS = ElementsList(
            "div[id=card_prices] div div:nth-child(1) div h4",
            "Поля 'Разовый платеж' продукта",
        )
        self.PRODUCT_CARD_SUMS = ElementsList(
            "div[id=card_prices] div div:nth-child(3) h4",
            "Поля 'Абонентская плата' продукта",
        )
