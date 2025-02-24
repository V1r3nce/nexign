from playwright.sync_api import Page

from pages.locators.base_elements import BaseElements
from pages.ui_elements import Element, ElementsList


class PromisedPaymentPage(BaseElements):
    """Страница /all/promised-payment 'Обещанный платеж'"""

    def __init__(self, page: Page):
        super().__init__(page)
        self.CONNECT_BTN = Element('(//div[contains(@class, "platform-root-scrollable-container")]//button)[1]', "Кнопка 'Подключить'",
                                   self.page)
        self.PRODUCT_PROMISED_PAYMENT_FLD = Element(".ant-table-tbody", "Поле 'Подключенного обещанного платежа'",
                                             self.page)
        self.AN_CANCEL_BTN = Element('(//div[contains(@class, "platform-root-scrollable-container")]//button)[4]', "Кнопка 'Аннулировать'",
                             self.page)
        self.PROMISED_PAYMENT_EL = ElementsList(".ant-table-tbody tr", "Обещанный платеж из таблцы",
                                                self.page)
        self.AN_CANCEL_BTN_IN_FORM = Element(".ant-modal-footer > div :nth-child(2)", "Кнопка 'Аннулировать' в форме подтвержденя",
                         self.page)
        self.COMMENT_FLD = Element(".ant-modal-body textarea", "Поле ввода комментария",
                                   self.page)