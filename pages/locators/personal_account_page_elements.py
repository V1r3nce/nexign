from playwright.sync_api import Page
from pages.ui_elements import Element, Select
from pages.locators.base_elements import BaseElements


class PersonalAccountElements(BaseElements):
    def __init__(self, page: Page = None):
        super().__init__(page)

        self.CREATE_AGREEMENT_BTN = Element(".react-grid-layout > div:nth-child(3) .platform-empty-box__container button",
                                            "Кнопка 'Создать договор'",
                                            self.page)
        self.PERSONAL_ACCOUNTS_TAB = Element("[id*='rc-tabs-1-tab-accounts']",
                                             "Вкладка 'Лицевые счета'",
                                             self.page)
        self.PERSONAL_ACCOUNTS_AFTER_RELATED_PERSON_TAB = Element("[id*='rc-tabs-3-tab-accounts']",
                                             "Вкладка 'Лицевые счета' после добавления связанного лица",
                                             self.page)
        self.ADD_PERSONAL_ACCOUNT_BTN = Element(".platform-button__icon_left",
                                                "Кнопка 'Добавить' лицевой счет",
                                                self.page)
        self.EDIT_DETAILS_ACCOUNT_BTN = Element(".platform-button__icon_left",
                                                "Кнопка 'Добавить' лицевой счет",
                                                self.page)

        self.PAYMENT_METHOD_FLD = Element("//*[@id='account-card-edit']//input[contains(@id, 'ratingType')]/ancestor::div[1]",
                                         "Поле 'Способ оплаты",
                                         self.page)
        self.SAVE_BNT = Element("#save",
                                "Кнопка 'Сохранить'",
                                self.page)
        self.RELATED_PERSONS_TAB = Element("[id*='tab-linked-persons']", "Вкладка 'Связанные лица'",
                                           self.page)
        self.ADD_RELATED_PERSON_BTN = Element(".platform-button__icon_left",
                                                "Кнопка 'Добавить' связанное лицо",
                                                self.page)
        self.CURRENT_PERSONAL_ACCOUNT_LINK = Element("[href*='accounts']","Кнопка-ссылка на текущий Лицевой счет клиента",
                                                   self.page)
        self.CURRENT_AGREEMENT_LINK = Element("[href*='agreements']","Кнопка-ссылка на текущий Лицевой счет клиента",
                                                   self.page)
        self.FINISH_DATA_RELATED_PERSON_NAME = Element("[id='beneficiary-function-impersonal-view_name']", "Поле именования Связанного лица",
                                                       self.page)
        self.CLIENT_TAB = Element("[id='rc-tabs-0-tab-customer']","Вкладка 'Клиент'", self.page)
