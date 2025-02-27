from playwright.sync_api import Page

from pages.locators.base_elements import BaseElements
from pages.ui_elements import Element, Select, RadioOrCheckboxBlock, ElementsList


class SelectProductOffersForm(BaseElements):
    """Форма 'Выбор продуктовых предложений'"""

    def __init__(self, page: Page):
        super().__init__(page)

        self.TITLE = Element(".ant-drawer-title h4", "Заголовок формы", self.page)
        self.ADDRESS = Select("//*[contains(@class, 'ant-drawer')]//input[contains(@id, 'rc_select')]", "Адрес", self.page)
        self.PRODUCT_SEARCH = Element("#productOfferingName", "Поиск", self.page)
        self.EXPRESS_PTV = Select("//button[div[.='Экспресс ПТВ']]", "Экспресс ПТВ", self.page) # требует дата атрибута от фронтов
        self.PRODUCT_TYPE = RadioOrCheckboxBlock("#productType", "Тип продукта", self.page)
        self.PRODUCT_CATEGORY = RadioOrCheckboxBlock("#productOfferingCategoryCodes", "Категория", self.page)
        self.TECHNOLOGY = RadioOrCheckboxBlock("#technologies", "Технологии", self.page)
        self.CLEAR_FILTER_BTN = Element("//button[.='Сбросить']", "Сбросить", self.page)
        self.SEARCH_BTN = Element("//button[.='Найти']", "Найти", self.page)

        self.CANCEL_BTN = Element("#_cancel-button", "Отмена", self.page)
        self.ADD_BTN = Element("#_accept-button", "Добавить", self.page)

        #PRODUCT_CARD
        self.PRODUCT_CARD = ElementsList(".ant-card", "Карточка продукта", self.page)
        self.PRODUCT_CARD_NAME = ElementsList(".ant-card .ant-card-head h4", "Название товара", self.page)
        self.PRODUCT_CARD_SELECT_BTN = ElementsList(".ant-card-body button[variant=primary]", "Выбрать карточку продукта", self.page)
        self.PRODUCT_CARD_DETAILS = ElementsList(".ant-card-body button[variant=secondary]", "Детали карточки продукта", self.page)