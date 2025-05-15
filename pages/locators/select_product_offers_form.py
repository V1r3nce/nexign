from playwright.sync_api import Page

from pages.locators.base_elements import BaseElements
from pages.ui_elements import CheckboxBlock, Element, ElementsList, RadioOrCheckboxBlock, Select


class SelectProductOffersForm(BaseElements):
    """Форма 'Выбор продуктовых предложений'"""

    def __init__(self, page: Page):
        super().__init__(page)

        self.TITLE = Element(".ant-drawer-title h3", "Заголовок формы", self.page)
        self.ADDRESS = Select(
            "//*[contains(@class, 'ant-drawer')]//input[contains(@id, 'rc_select')]", "Адрес", self.page
        )
        self.PRODUCT_SEARCH = Element("#productOfferingName", "Поиск", self.page)
        self.EXPRESS_PTV = Select(
            "//button[div[.='Экспресс ПТВ']]", "Экспресс ПТВ", self.page
        )  # требует дата атрибута от фронтов
        self.SHOW_ONLY_CHOOSE_BTN = Element(
            "//button[contains(@class, 'ant-switch')]/..", "Переключатель 'Показать только выбранные'", self.page
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
        self.PRODUCT_CARD = ElementsList(".ant-card", "Карточка продукта", self.page)
        self.PRODUCT_CARD_NAME = ElementsList(".ant-card .ant-card-head h4", "Название товара", self.page)
        self.PRODUCT_CARD_SELECT_BTN = ElementsList(
            ".ant-card-body div:nth-child(3) button", "Выбрать карточку продукта", self.page
        )
        self.PRODUCT_CARD_PRODUCTS = ElementsList(".ant-card-body > div:first-child p", "Продукты бандла", self.page)
        self.PRODUCT_CARD_DETAILS = ElementsList(
            ".ant-card-body button[variant=secondary]", "Детали карточки продукта", self.page
        )
        self.PRODUCT_SINGLE_PAYMENTS = ElementsList(
            ".ant-card-body > div:nth-child(2) > div:nth-child(2) > div:nth-child(1) h4",
            "Поля 'Разовый платеж' продукта",
            self.page,
        )
        self.PRODUCT_CARD_SUMS = ElementsList(
            ".ant-card-body > div:nth-child(2) > div:nth-child(2) > div:nth-child(3) h4",
            "Поля 'Абонентская плата' продукта",
            self.page,
        )
