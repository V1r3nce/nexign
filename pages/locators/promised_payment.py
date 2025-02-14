from playwright.sync_api import Page

from pages.locators.base_elements import BaseElements
from pages.ui_elements import Element, ElementsList, Select


class PromisedPaymentPage(BaseElements):
    """Страница /all/promised-payment 'Обещанный платеж'"""

    def __init__(self, page: Page):
        super().__init__(page)
        self.CONNECT_BTN = Element('(//div[contains(@class, "platform-root-scrollable-container")]//button)[1]', "Кнопка 'Подключить'",
                                   self.page)
        self.PRODUCT_PROMISED_PAYMENT_FLD = Element(".ant-table-tbody", "Поле 'Подключенного обещанного платежа'",
                                             self.page)