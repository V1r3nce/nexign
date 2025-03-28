from playwright.sync_api import Page
from pages.locators.base_elements import BaseElements
from pages.locators.dynamic_form_elements import DynamicElements, DynamicForms
from pages.ui_elements import Element, ElementsList, Select, DatePicker, RadioOrCheckboxBlock


class PaymentElements(BaseElements):
    """Страница Платежи клиента rm-ui/all/payment-search"""
    def __init__(self, page: Page):
        super().__init__(page)
        # ДАННЫЕ АККАУНТА
        self.ACCOUNT_NUM = Element("//div[contains(@class, 'platform-root-scrollable-container')]//div[1]/div[1]/p[2]",
                                   "Номер ЛС", self.page)
        self.USER_NAME = Element("//div[contains(@class, 'platform-root-scrollable-container')]//div[1]/div[1]/h3",
                                 "Имя пользователя", self.page)
        self.USER_BALANCE = Element("//div[contains(@class, 'platform-root-scrollable-container')]//div[1]/div[2]"
                                    "//h3[1]", "Баланс пользователя", self.page)
        self.USER_CURRENCY = Element("//div[contains(@class, 'platform-root-scrollable-container')]//div[1]/div[2]"
                                     "//h3[2]", "Валюта пользователя", self.page)

        # КНОПКИ УПРАВЛЕНИЯ НАД ТАБЛИЦЕЙ
        self.CREATE_PAYMENT_BTN = Element("div:first-child button[variant='primary']:first-child",
                                          "Кнопка 'Создать платеж'", self.page)
        self.REFRESH_PAYMENTS_BTN = Element("(//div[contains(@class, 'platform-custom-table')]//button)[2]",
                                            "Кнопка 'Обновить'", self.page)
        self.CANCEL_PAYMENT_BTN = Element("(//div[contains(@class, 'platform-custom-table')]//button)[4]",
                                          "Кнопка 'Аннулировать платёж'", self.page)
        self.ADD_CORRECTION_BTN = Element("(//div[contains(@class, 'platform-custom-table')]//button)[5]",
                                          "Кнопка 'Добавить корректировку'", self.page)
        self.BALANCE_TRANSFER_BTN = Element("(//div[contains(@class, 'platform-custom-table')]//button)[6]",
                                            "Кнопка 'Перенести баланс'", self.page)

        # ФОРМА ПЕРЕНОС БАЛАНСА
        self.PERSONAL_ACCOUNT_SELECTOR = Element("(//*[@id='recipientAccountNumber']/parent::span)",
                                                 "3 точки в выборе лицевого счета для переноса средств", self.page)
        self.PERSONAL_ACCOUNT_INPUT = Element("input#recipientAccountNumber",
                                              "Поле ввода лицевого счета для переноса средств", self.page)
        self.PERSONAL_ACCOUNT_TO_SEARCH = Element('(//div[contains(@id, "searchValue")]//input)',
                                                  "Поле ввода ЛС для переноса баланса", self.page)
        self.PERSONAL_ACCOUNT_CHOOSE_BTN = Element(
            "div[class *= 'ant-drawer-right'] > div > div[role = 'dialog'] > div[class = 'ant-drawer-wrapper-body'] > div > button[id='_accept-button']",
            "Кнопка 'Выбрать'", self.page)
        self.PERSONAL_ACCOUNT_SEARCH_BTN = Element("form.ant-form-horizontal button[type='submit']",
                                                   "Кнопка 'Найти'", self.page)
        self.PERSONAL_ACCOUNT_DATA = ElementsList("//form/parent::div/div[1]/div/p[2]", "Данные о счете", self.page)
        self.PERSONAL_ACCOUNT_CHOOSE_BTN = Element("#root > div > div:nth-child(7) button[id='_accept-button'] ",
                                                   "Кнопка 'Выбрать'", self.page)
        self.ACCOUNT_DATA_BLOCKS = ElementsList("//form//label[not(@for='searchType')]/parent::div/parent::div/div[2]",
                                                "Данные Со счета/На счет", self.page)
        self.DONOR_ADJUSTMENT_REASON = Select("input[id*='sourceAdjustmentReasonId']", "Причина корректировки донора",
                                              self.page)
        self.RECIPIENT_ADJUSTMENT_REASON = Element("input[id*='recipientAdjustmentReasonId']",
                                                   "Причина корректировки реципиента", self.page)
        self.CHOSEN_DONOR_ADJUSTMENT_REASON = Element("//input[@id='sourceAdjustmentReasonId']/parent::span/parent"
                                                      "::div/span[2]", "Выбранная причина корректировки Со счета",
                                                      self.page)
        self.FROM_ACCOUNT_COMMENT = Element("#sourceComment", "Комментарий 'Со счета'", self.page)
        self.RELOCATE_SUM_INPUT = Element("input#amount", "Комментарий 'Со счета'", self.page)
        self.RECIPIENT_ADJUSTMENT_REASON = Select("input[id*='recipientAdjustmentReasonId']",
                                                  "Причина корректировки реципиента", self.page)
        self.CHOSEN_RECIPIENT_ADJUSTMENT_REASON = Element("//input[@id='recipientAdjustmentReasonId']/parent::span/"
                                                          "parent::div/span[2]", "Выбранная причина корректировки"
                                                                                 " На счет", self.page)
        self.TO_ACCOUNT_COMMENT = Element("#recipientComment", "Комментарий 'На счет'", self.page)
        self.BALANCE_TO_TRANSFER = Element("//input[@id='amount']",
                                           "Сумма для переноса баланса", self.page)
        self.TRANSFER_ACCEPT = Element("div[class *=ant-drawer-open] div > div> div > button[id ='_accept-button']",
                                       "Кнопка 'Перенести'", self.page)

        # ТАБЛИЦА ПЛАТЕЖИ
        self.CHECK_NUM_FIELDS = ElementsList("//tbody/tr/td[1]/span[2]", "Поля 'Номер чека'", self.page)
        self.PAYMENT_DATES_FIELDS = ElementsList("//tbody/tr/td[2]", "Поля 'Дата платежа'", self.page)
        self.REGISTRY_DATES_FIELDS = ElementsList("//tbody/tr/td[3]", "Поля 'Дата регистрации платежа'", self.page)
        self.SUM_FIELDS = ElementsList("//tbody/tr/td[4]", "Поля 'Сумма зачисления'", self.page)
        self.TAX_FIELDS = ElementsList("//tbody/tr/td[5]", "Поля 'Налог'", self.page)
        self.STATUS_FIELDS = ElementsList("//tbody/tr/td[6]", "Поля 'Статус'", self.page)


class PaymentDetailsElements(DynamicElements):
    """Форма с подробной информацией о Платеже"""
    def __init__(self, page: Page):
        super().__init__(page)

        self.FORM_TITLE = Element("div.ant-drawer-title h3", "Заголовок формы", self.page)
        self.FORM_STATUS = Element("div.ant-drawer-title div p", "Статус", self.page)
        self.SUBTITLE = Element("div.ant-drawer-title > p", "Статус", self.page)
        self.FORM_TABS = ElementsList("div.ant-tabs-tab", "Табы формы", self.page)
        self.PAYMENT_DETAILS = ElementsList("[role*='tabpanel'] > div > div > div:last-child", "Строки детали платежа",
                                            self.page)
        self.PAYMENT_TYPE_BTN = ElementsList("[role*='tabpanel'] label", "Погашения/Корректировки",
                                             self.page)
        self.PAYMENT_DATE_FIELDS = ElementsList("[role*='tabpanel'] tbody tr td:nth-child(1)",
                                                "Даты Погашения/Корректировки", self.page)
        self.PAYMENT_SUM_FIELDS = ElementsList("[role*='tabpanel'] tbody tr td:nth-child(2)",
                                               "Суммы Погашения/Корректировки", self.page)
        self.PAYMENT_OBJECTS_FIELDS = ElementsList("[role*='tabpanel'] tbody tr td:nth-child(3)",
                                                   "Объекты Погашения/Корректировки", self.page)
        self.CORRECTION_TYPE_FIELDS = ElementsList("[role*='tabpanel'] tbody tr td:nth-child(2)",
                                                   "Поля 'Тип корректировки'", self.page)
        self.CORRECTION_SUM_FIELDS = ElementsList("[role*='tabpanel'] tbody tr td:nth-child(3)",
                                                  "Поля 'Сумма'", self.page)
        self.CORRECTION_STATUS_FIELDS = ElementsList("[role*='tabpanel'] tbody tr td:nth-child(5)",
                                                     "Поля 'Статус'", self.page)
        self.CORRECTION_PURPOSE_FIELDS = ElementsList("[role*='tabpanel'] tbody tr td:nth-child(6)",
                                                      "Поля 'Причина'", self.page)


class PaymentCorrectionForm(DynamicForms):
    """Форма корректировки платежа"""

    def __init__(self, page: Page):
        super().__init__(page)

        self.CORRECTION_TYPE_RADIOBUTTONS = RadioOrCheckboxBlock("#adjustmentTypeId",
                                                                 "Радио-баттон 'Тип корректировки'", self.page)
        self.CORRECTION_DATE_INPUT = DatePicker("#adjustmentDate", "Поле ввода 'Дата корректировки'",
                                                self.page)
        self.CORRECTION_SUM_INPUT = Element("#amountWithTax", "Поле ввода 'Сумма'",
                                            self.page)
        self.CORRECTION_REASON = Select("input#adjustmentReasonId", "Причина корректировки", self.page)
        self.CORRECTION_COMMENT = Element("#comment", "Комментарий корректировки", self.page)
