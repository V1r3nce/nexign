from pages.locators.base_elements import BaseElements
from pages.locators.nbss.dynamic_form_elements import DynamicElements, DynamicForms
from pages.ui_elements import DatePicker, Element, ElementsList, RadioOrCheckboxBlock, Select


class PaymentElements(BaseElements):
    """Страница Платежи клиента rm-ui/all/payment-search"""

    def __init__(self) -> None:
        super().__init__()
        # ДАННЫЕ АККАУНТА
        self.ACCOUNT_NUM = Element(
            "//div[contains(@class, 'platform-root-scrollable-container')]//div[1]/div[1]/p[2]", "Номер ЛС"
        )
        self.USER_NAME = Element(
            "//div[contains(@class, 'platform-root-scrollable-container')]//div[1]/div[1]/h3",
            "Имя пользователя",
        )
        self.USER_BALANCE = Element(
            "//div[contains(@class, 'platform-root-scrollable-container')]//div[2]//h3[1][@color and @display]",
            "Баланс пользователя",
        )
        self.USER_CURRENCY = Element(
            "//div[contains(@class, 'platform-root-scrollable-container')]//div[1]/div[2]//h3[2]",
            "Валюта пользователя",
        )
        self.USER_BALANCE_UPDATE_TIME = Element(
            "//div[contains(@class, 'platform-root-scrollable-container')]//div[2]//p[@color and @class]",
            "Время обновления баланса",
        )

        # КНОПКИ УПРАВЛЕНИЯ НАД ТАБЛИЦЕЙ
        self.CREATE_PAYMENT_BTN = Element("[data-icon=Add]", "Кнопка 'Создать платеж'")
        self.REFRESH_PAYMENTS_BTN = Element(
            "(//div[contains(@class, 'platform-table')]//button)[2]", "Кнопка 'Обновить'"
        )
        self.CANCEL_PAYMENT_BTN = Element(
            "(//div[contains(@class, 'platform-table')]//button)[4]", "Кнопка 'Аннулировать платёж'"
        )
        self.ADD_CORRECTION_BTN = Element(
            "(//div[contains(@class, 'platform-table')]//button)[5]", "Кнопка 'Добавить корректировку'"
        )
        self.BALANCE_TRANSFER_BTN = Element(
            "(//div[contains(@class, 'platform-table')]//button)[6]", "Кнопка 'Перенести баланс'"
        )

        # ФОРМА ПЕРЕНОС БАЛАНСА
        self.PERSONAL_ACCOUNT_SELECTOR = Element(
            "input#recipientAccountNumber[aria-required='true'][type='text']",
            "3 точки в выборе лицевого счета для переноса средств",
        )
        self.PERSONAL_ACCOUNT_INPUT = Element(
            "input#recipientAccountNumber", "Поле ввода лицевого счета для переноса средств"
        )
        self.PERSONAL_ACCOUNT_TO_SEARCH = Element(
            '(//div[contains(@id, "searchValue")]//input)', "Поле ввода ЛС для переноса баланса"
        )
        self.PERSONAL_ACCOUNT_CHOOSE_BTN = Element(
            "div[class *= 'ant-drawer-right'] > div > div[role = 'dialog'] > div[class = 'ant-drawer-wrapper-body'] > div > button[id='_accept-button']",
            "Кнопка 'Выбрать'",
        )
        self.PERSONAL_ACCOUNT_SEARCH_BTN = Element(
            "form[class*=form-horizontal] button[type='submit']", "Кнопка 'Найти'"
        )
        self.PERSONAL_ACCOUNT_DATA = ElementsList("//form/parent::div/div[2]//p[2]", "Данные о счете")
        self.PERSONAL_ACCOUNT_CHOOSE_BTN = Element(
            "//div[contains(@class, 'drawer-right')][2]//div[contains(@class, 'drawer-footer')]//button[@id='_accept-button'] | div",
            "Кнопка 'Выбрать'",
        )
        self.ACCOUNT_DATA_BLOCKS = ElementsList(
            "//form//label[not(@for='searchType')]/parent::div/parent::div/div[2]", "Данные Со счета/На счет"
        )
        self.DONOR_ADJUSTMENT_REASON = Select("input[id*='sourceAdjustmentReasonId']", "Причина корректировки донора")
        self.RECIPIENT_ADJUSTMENT_REASON = Element(
            "input[id*='recipientAdjustmentReasonId']", "Причина корректировки реципиента"
        )
        self.CHOSEN_DONOR_ADJUSTMENT_REASON = Element(
            "//input[@id='sourceAdjustmentReasonId']/parent::span/parent::span/span[2]",
            "Выбранная причина корректировки Со счета",
        )
        self.FROM_ACCOUNT_COMMENT = Element("#sourceComment", "Комментарий 'Со счета'")
        self.RELOCATE_SUM_INPUT = Element("input#amount", "Комментарий 'Со счета'")
        self.RECIPIENT_ADJUSTMENT_REASON = Select(
            "input[id*='recipientAdjustmentReasonId']", "Причина корректировки реципиента"
        )
        self.CHOSEN_RECIPIENT_ADJUSTMENT_REASON = Element(
            "//input[@id='recipientAdjustmentReasonId']/parent::span/parent::span/span[2]",
            "Выбранная причина корректировки На счет",
        )
        self.TO_ACCOUNT_COMMENT = Element("#recipientComment", "Комментарий 'На счет'")
        self.BALANCE_TO_TRANSFER = Element("//input[@id='amount']", "Сумма для переноса баланса")
        self.TRANSFER_ACCEPT = Element(
            "div[class *=drawer-open] div > div> div > button[id ='_accept-button']", "Кнопка 'Перенести'"
        )

        # ТАБЛИЦА ПЛАТЕЖИ
        self.CHECK_NUM_FIELDS = ElementsList(
            "[class*=table-tbody] [class*=table-row] > [class*=table-cell]:nth-child(1) span",
            "Поля 'Номер чека'",
        )
        self.PAYMENT_DATES_FIELDS = ElementsList(
            "[class*=table-row] > [class*=table-cell]:nth-child(2)", "Поля 'Дата платежа'"
        )
        self.REGISTRY_DATES_FIELDS = ElementsList(
            "[class*=table-row] > [class*=table-cell]:nth-child(3)", "Поля 'Дата регистрации платежа'"
        )
        self.SUM_FIELDS = ElementsList(
            "[class*=table-row] > [class*=table-cell]:nth-child(4)", "Поля 'Сумма зачисления'"
        )
        self.TAX_FIELDS = ElementsList("[class*=table-row] > [class*=table-cell]:nth-child(5)", "Поля 'Налог'")
        self.STATUS_FIELDS = ElementsList("[class*=table-row] > [class*=table-cell]:nth-child(6)", "Поля 'Статус'")


class ConsumptionElements(BaseElements):
    """Страница потребление клиента"""

    def __init__(self) -> None:
        super().__init__()

        self.PROFIT_ACTIONS = ElementsList(
            "//div[contains(@style,'max-height') and .//tr[@data-row-key]]//tr[@data-row-key]",
            "Поля в таблице 'Начисления'",
        )


class PaymentDetailsElements(DynamicElements):
    """Форма с подробной информацией о Платеже"""

    def __init__(self) -> None:
        super().__init__()

        self.FORM_TITLE = Element("[class*=drawer-open] [class*=drawer-title] h3", "Заголовок формы")
        self.FORM_STATUS = Element("[class*=drawer-open] [class*=drawer-title]  div span", "Статус")
        self.SUBTITLE = Element("[class*=drawer-open] [class*=drawer-title] > p", "Статус")
        self.FORM_TABS = ElementsList("[class*=drawer-body] div[class*=tabs-tab-btn]", "Табы формы")
        self.PAYMENT_DETAILS = ElementsList(
            "[class*=drawer-body] [role*='tabpanel'] > div > div > div > div:last-child",
            "Строки детали платежа",
        )
        self.PAYMENT_TYPE_BTN = ElementsList("[role*='tabpanel'] label", "Погашения/Корректировки")
        self.PAYMENT_DATE_FIELDS = ElementsList(
            "[class*=drawer-body]  [class*=table-row] > [class*=table-cell]:nth-child(1)",
            "Даты Погашения/Корректировки",
        )
        self.PAYMENT_SUM_FIELDS = ElementsList(
            "[class*=drawer-body] [class*=table-row] [class*=table-cell]:nth-child(2)",
            "Суммы Погашения/Корректировки",
        )
        self.PAYMENT_OBJECTS_FIELDS = ElementsList(
            "[class*=drawer-body] [class*=table-row] [class*=table-cell]:nth-child(3)",
            "Объекты Погашения/Корректировки",
        )
        self.CORRECTION_TYPE_FIELDS = ElementsList(
            "[class*=drawer-body] [role*='tabpanel'] [class*=tbody] tr td:nth-child(2)",
            "Поля 'Тип корректировки'",
        )
        self.CORRECTION_SUM_FIELDS = ElementsList(
            "[class*=drawer-body] [role*='tabpanel'] [class*=tbody] tr td:nth-child(3)", "Поля 'Сумма'"
        )
        self.CORRECTION_STATUS_FIELDS = ElementsList(
            "[class*=drawer-body] [role*='tabpanel'] [class*=tbody] tr td:nth-child(5)", "Поля 'Статус'"
        )
        self.CORRECTION_PURPOSE_FIELDS = ElementsList(
            "[class*=drawer-body] [role*='tabpanel'] [class*=tbody] tr td:nth-child(6)", "Поля 'Причина'"
        )


class PaymentCorrectionForm(DynamicForms):
    """Форма корректировки платежа"""

    def __init__(self) -> None:
        super().__init__()

        self.CORRECTION_TYPE_RADIOBUTTONS = RadioOrCheckboxBlock("#adjustmentTypeId", "Радио-баттон 'Тип корректировки'")
        self.CORRECTION_DATE_INPUT = DatePicker("#adjustmentDate", "Поле ввода 'Дата корректировки'")
        self.CORRECTION_SUM_INPUT = Element("#amountWithTax", "Поле ввода 'Сумма'")
        self.CORRECTION_REASON = Select("input#adjustmentReasonId", "Причина корректировки")
        self.CORRECTION_COMMENT = Element("#comment", "Комментарий корректировки")
