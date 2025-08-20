from playwright.sync_api import Page

from pages.locators.base_elements import BaseElements
from pages.ui_elements import Element, ElementsList


class DebtRestructuring(BaseElements):
    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page

        self.ADD_BTN = Element(
            "(//button [contains(@class, 'btn-variant-solid')]) [1]",
            "Кнопка '+'",
            self.page,
        )

        self.NEXT_BTN = Element("//span[@data-icon='KeyboardArrowRight']", "Кнопка Далее", self.page)

        self.REFRESH_BTN = Element("(//span[@data-icon='Refresh']) [1]", "Кнопка обновить заявку", self.page)

        self.REFRESH_INSTALLMENTS_BTN = Element(
            "(//div[contains(@class,'extra-tools')]//span[@data-icon='Refresh'])[1]", "Кнопка обновить", self.page
        )

        self.INSTALLMENTS = ElementsList(
            "//div[contains(@class,'custom-list-scrollable-body')] /div[not(contains(@class, 'empty-state'))]",
            "Рассрочки",
            self.page,
        )

        # INSTALLMENTS_TAB
        self.SCHEDULE = Element(
            "(//div[contains(@class,'platform-table')] //button) [3]", "Кнопка Детальный график рассрочки", self.page
        )

        self.INSTALLMENT_DATES = ElementsList(
            "//div[contains(@class,'drawer-body')] //tr[contains(@class,'table-row')]", "Даты рассрочки", self.page
        )

        self.SIDEBAR_CLOSE_BTN = Element("//button[@id='_cancel-button']", "Кнопка Закрыть", self.page)

        self.PAYMENT_HEADER = ElementsList("//div[@role='button'] //p", "Заголовки платежей рассрочки", self.page)

        self.STATUS = Element("//h3 /..//span/div", "Поле со статусом рассрочки", self.page)

        self.INIT_PAYMENT_DONE = Element("//span[@data-icon='Done']", "Поле Первоначальный платеж внесен", self.page)

        self.PAYMENTS_STATUSES = ElementsList("//td //div", "Поле статус из таблицы с платежами", self.page)

        self.PAYMENTS_PAID_SUM = ElementsList("//tr //td[5]", "Столбец оплачено из таблицы с платежами", self.page)

        self.EDIT_BTN = Element("//span[@data-icon='Edit']", "Кнопка Редактировать", self.page)

        self.CANCEL_BTN = Element("//span[@data-icon='Cancel']", "Кнопка Аннулировать", self.page)

        self.CANCEL_ACCEPT_BTN = Element(
            "//div[contains(@class,'modal-footer')]//button[contains(@class, 'btn-variant-solid')]",
            "Кнопка Аннулировать на модальном окне",
            self.page,
        )
        # ADD_SIDEBAR
        self.BILL_CHECKBOXES = ElementsList(
            "//td[contains(@class,'table-selection-column')] //input", "Чекбоксы счетов", self.page
        )

        self.BILL_WITHDRAW = ElementsList(
            "//td[contains(@class,'no-padding-cell')] //input", "Окно для ввода 'Отобрано'", self.page
        )

        self.BILL_DEBT = ElementsList(
            "//tr[contains(@class,'table-row')] //td[contains(@class,'table-cell')] [6]",
            "Значения из столбца Не оплачено таблицы",
            self.page,
        )

        self.NEXT_SIDEBAR_BTN = Element(
            "//div[contains(@class,'drawer')]//button[contains(@class,'-btn-icon-end')]", "Кнопка Далее", self.page
        )

        self.REGISTER_BTN = Element(
            "(//div[contains(@class,'drawer')]//button[contains(@class,'-btn-lg')]) [4]", "Кнопка Оформить ДС", self.page
        )

        self.DRAFT_SAVE_BTN = Element(
            "(//div[contains(@class, 'drawer-footer')] //button) [2]", "Кнопка Сохранить как черновик", self.page
        )

        self.CALCULATE_BTN = Element(
            "(//div[contains(@class,'drawer')]//button[contains(@class,'-btn-lg')]) [1]", "Кнопка Рассчитать", self.page
        )

        self.FIRST_PAYMENT_DATE = Element(
            "//input[@id='dateOfSecondPayment']", "Окно для выбора Дата первого платежа", self.page
        )

        self.PAYMENT_NUMBER = Element("//input[@id='numberOfPayments']", "Количество платежей", self.page)

        self.SUM_OF_PAYMENT = Element("#sumOfPayments", "Сумма платежей", self.page)

        self.INIT_PAYMENT_CHECKBOX = Element(
            "//span[contains(@class, 'checkbox-label')]", "Чекбокс Требуется первоначальный платеж", self.page
        )

        self.INIT_PAYMENT = Element("#sumOfFirstPayment", "Сумма первоначального платежа", self.page)

        self.INIT_PAYMENT_DATE = Element("#dateOfFirstPayment", "Дата первоначального платежа", self.page)

        self.PAYMENTS = ElementsList(
            "//div[contains(@class,'-table-row')] //div[contains(@class,'table-cell')] [1]", "Платежи", self.page
        )

        self.PAYMENT_DELETE_BTN = Element("//span[@data-icon='Delete']", "Кнопка удалить", self.page)

        # AGREEMENT_TAB
        self.AGREEMENTS = ElementsList("//tr[contains(@class,'table-row')]", "Строки с соглашениями", self.page)

        self.AGREE_BTN = Element("(//span[@data-icon='CheckCircle']) [1]", "Кнопка согласовать", self.page)

        self.AGREEMENT_FLAG = ElementsList(
            "//tr[contains(@class,'table-row')] //span[@data-icon='CheckCircle']",
            "Кружок согласования документа",
            self.page,
        )

        self.TEXT_CELL = ElementsList("//td //div", "Столбцы с текстом", self.page)
