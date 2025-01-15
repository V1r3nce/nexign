from playwright.sync_api import Page
from pages.ui_elements import Element, Select
from pages.locators.base_elements import BaseElements


class PersonalAccountElements(BaseElements):
    def __init__(self, page: Page = None):
        super().__init__(page)

        self.CREATE_AGREEMENT_BTN = Element(".react-grid-layout > div:nth-child(3) .platform-empty-box-container button",
                                            "Кнопка 'Создать договор'",
                                            self.page)
        self.PERSONAL_ACCOUNTS_TAB = Element("[id*='rc-tabs-1-tab-accounts']",
                                             "Вкладка 'Лицевые счета'",
                                             self.page)
        self.ADD_PERSONAL_ACCOUNT_BTN = Element(".platform-button-icon-left",
                                                "Кнопка 'Добавить' лицевой счет",
                                                self.page)
        self.EDIT_DETAILS_ACCOUNT_BTN = Element(".platform-button-icon-left",
                                                "Кнопка 'Добавить' лицевой счет",
                                                self.page)

        self.PAYMENT_METHOD_FLD = Element("//*[@id='account-card-edit']//input[contains(@id, 'ratingType')]/ancestor::div[1]",
                                         "Поле 'Способ оплаты",
                                         self.page)
        self.SAVE_BNT = Element("#save",
                                "Кнопка 'Сохранить'",
                                self.page)
