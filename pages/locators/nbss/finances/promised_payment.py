import allure

from pages.locators.base_elements import BaseElements
from pages.ui_elements import Element, ElementsList


class PromisedPaymentPageElements(BaseElements):
    """Страница /all/promised-payment 'Обещанный платеж'"""

    def __init__(self) -> None:
        super().__init__()
        self.CONNECT_BTN = Element(
            "div[class*='platform-table'] div div:nth-child(1) button:nth-of-type(1)",
            "Кнопка 'Подключить'",
        )
        self.PRODUCT_PROMISED_PAYMENT_FLD = Element(
            "[class*='table-container'] > [class*='table-tbody']", "Поле 'Подключенного обещанного платежа'"
        )
        self.AN_CANCEL_BTN = Element(
            "div[class*='platform-table'] div div:nth-child(1) button:nth-of-type(4)",
            "Кнопка 'Аннулировать'",
        )
        self.PROMISED_PAYMENT_EL = ElementsList(
            "[class*='table-tbody'] [class*='table-row']", "Обещанный платеж из таблицы"
        )
        self.AN_CANCEL_BTN_IN_FORM = Element(
            "[class*='modal-footer'] button:nth-of-type(2)", "Кнопка 'Аннулировать' в форме подтвержденя"
        )
        self.COMMENT_FLD = Element(".ant-modal-body textarea", "Поле ввода комментария")
        self.STATUS_HISTORY_BTN = Element(
            "div[class*='platform-table'] div div:nth-child(1) button:nth-of-type(5)",
            "Кнопка 'История статусов'",
        )
        self.STATUS_PAYMENTS_FORM = Element("[class*='drawer-content-wrapper']", "Форма со статусами обещанного платежа")
        self.CHARACTERISTICS_BTN = Element(
            "div[class*='platform-table'] div div:nth-child(2) button", "Кнопка 'Шестеренка"
        )
        self.CHARACTERISTICS_FLD = ElementsList(
            "[class*='dropdown-placement-bottomRight'] [type='checkbox']", "Настраиваемая характеристика"
        )
        self.CHARACTERISTICS_FORM_BTN = ElementsList(
            "[class*='dropdown-placement-bottomRight'] button", "Кнопки в поле характеристик"
        )

    @allure.step("Выбрать настраиваемые характиристики")
    def choose_characteristics(self) -> None:
        for i in range(1, 13, 2):
            self.CHARACTERISTICS_FLD[i].click()
        self.CHARACTERISTICS_FORM_BTN[0].click()
