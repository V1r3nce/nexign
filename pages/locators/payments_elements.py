import allure
from playwright.sync_api import Page
from pages.locators.base_elements import BaseElements
from pages.locators.dynamic_form_elements import DynamicElements
from pages.ui_elements import Element, ElementsList, Select, Autocomplete, DatePicker, Dropdown


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

        self.CREATE_PAYMENT_BTN = Element("div:first-child button[variant='primary']:first-child",
                                          "Кнопка 'Создать платеж'", self.page)
        self.SET_AMOUNT = Element("input[id='amount']", "Сумма платежа", self.page)
        self.PAYMENT_POINT = Select("input[id='paymentPointId']", "Выбор кассы", self.page)
        self.BALANCE_TRANSFER_BTN = Element("(//div[contains(@class, 'platform-custom-table')] //button)[6]",
                                            "Кнопка 'Перенести баланс'", self.page)

        # ФОРМА ПЕРЕНОС БАЛАНСА
        self.PERSONAL_ACCOUNT_SELECTOR = Element("(//*[@id='recipientAccountNumber']/parent::span)",
                                                 "3 точки в выборе лицевого счета для переноса средств", self.page)
        self.PERSONAL_ACCOUNT_TO_SEARCH = Element('(//div[contains(@id, "searchValue")] //input)',
                                                  "Поле ввода ЛС для переноса баланса", self.page)
        self.PERSONAL_ACCOUNT_CHOOSE_BTN = Element(
            "div[class *= 'ant-drawer-right'] > div > div[role = 'dialog'] > div[class = 'ant-drawer-wrapper-body'] > div > button[id='_accept-button']",
            "Кнопка 'Выбрать'", self.page)
        self.DONOR_ADJUSTMENT_REASON = Select("input[id*='sourceAdjustmentReasonId']", "Причина корректировки донора",
                                              self.page)
        self.RECIPIENT_ADJUSTMENT_REASON = Element("input[id*='recipientAdjustmentReasonId']",
                                                   "Причина корректировки реципиента", self.page)
        self.BALANCE_TO_TRANSFER = Element("//input[id*='amount']",
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
