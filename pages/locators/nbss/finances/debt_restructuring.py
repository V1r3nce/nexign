from pages.locators.base_elements import BaseElements
from pages.ui_elements import Element, ElementsList


class DebtRestructuringElements(BaseElements):
    def __init__(self) -> None:
        super().__init__()

        self.ADD_BTN = Element(
            "(//button [contains(@class, 'btn-variant-solid')]) [1]",
            "Кнопка '+'",
        )

        self.NEXT_BTN = Element("//span[@data-icon='KeyboardArrowRight']", "Кнопка Далее")

        self.REFRESH_BTN = Element("(//span[@data-icon='Refresh']) [1]", "Кнопка обновить заявку")

        self.REFRESH_INSTALLMENTS_BTN = Element(
            "(//div[contains(@class,'extra-tools')]//span[@data-icon='Refresh'])[1]", "Кнопка обновить"
        )

        self.INSTALLMENTS = ElementsList(
            "//div[contains(@class,'custom-list-scrollable-body')] /div[not(contains(@class, 'empty-state'))]",
            "Рассрочки",
        )

        # INSTALLMENTS_TAB
        self.SCHEDULE = Element(
            "(//div[contains(@class,'platform-table')] //button) [3]", "Кнопка Детальный график рассрочки"
        )
        self.INSTALLMENT_DATES = ElementsList(
            "div[class*=drawer-content][role=dialog] div[class*=table-row]", "Поля таблицы рассрочки"
        )

        self.SIDEBAR_CLOSE_BTN = Element("//button[@id='_cancel-button']", "Кнопка Закрыть")

        self.PAYMENT_HEADER = ElementsList("//div[@role='button'] //p", "Заголовки платежей рассрочки")

        self.STATUS = Element(
            "header.platform-summary-header span[display='inline-block'] > div", "Поле со статусом рассрочки"
        )

        self.INIT_PAYMENT_DONE = Element("//span[@data-icon='Done']", "Поле Первоначальный платеж внесен")

        self.PAYMENTS_STATUSES = ElementsList(
            "//div[@data-row-key]/div[2]//span/div", "Поле статус из таблицы с платежами"
        )

        self.PAYMENTS_PAID_SUM = ElementsList("//tr //td[5]", "Столбец оплачено из таблицы с платежами")

        self.EDIT_BTN = Element("//span[@data-icon='Edit']", "Кнопка Редактировать")

        self.CANCEL_BTN = Element("//span[@data-icon='Cancel']", "Кнопка Аннулировать")

        self.CANCEL_ACCEPT_BTN = Element(
            "//div[contains(@class,'modal-footer')]//button[contains(@class, 'btn-variant-solid')]",
            "Кнопка Аннулировать на модальном окне",
        )
        # ADD_SIDEBAR
        self.BILL_CHECKBOXES = ElementsList(
            "[class*='table-selection-column'] input[class*=checkbox]", "Чекбоксы счетов"
        )

        self.BILL_WITHDRAW = ElementsList(
            "[class*='table-row'] [class*='no-padding-cell'] input", "Окно для ввода 'Отобрано'"
        )

        self.BILL_DEBT = ElementsList(
            "[class*='table-row'] [class*='table-cell']:nth-child(6)", "Значения из столбца Не оплачено таблицы"
        )

        self.NEXT_SIDEBAR_BTN = Element(
            "[class*=drawer-content][role=dialog] [class*=footer] button[class*='-btn-icon-end'] ", "Кнопка Далее"
        )

        self.REGISTER_BTN = Element(
            "[class*=drawer-content][role=dialog] [class*=footer] button:nth-child(2)", "Кнопка Оформить ДС"
        )

        self.DRAFT_SAVE_BTN = Element(
            "(//div[contains(@class, 'drawer-footer')] //button) [2]", "Кнопка Сохранить как черновик"
        )

        self.CALCULATE_BTN = Element("[class*=drawer-body] form:has(button) button", "Кнопка Рассчитать")

        self.FIRST_PAYMENT_DATE = Element("//input[@id='dateOfSecondPayment']", "Окно для выбора Дата первого платежа")

        self.PAYMENT_NUMBER = Element("//input[@id='numberOfPayments']", "Количество платежей")

        self.SUM_OF_PAYMENT = Element("#sumOfPayments", "Сумма платежей")

        self.INIT_PAYMENT_CHECKBOX = Element(
            "//span[contains(@class, 'checkbox-label')]", "Чекбокс Требуется первоначальный платеж"
        )

        self.INIT_PAYMENT = Element("#sumOfFirstPayment", "Сумма первоначального платежа")

        self.INIT_PAYMENT_DATE = Element("#dateOfFirstPayment", "Дата первоначального платежа")

        self.PAYMENTS = ElementsList(
            "div[class*=drawer-content][role=dialog] div[class*=table-tbody] div[class*=table-row]", "Платежи"
        )
        self.PAYMENTS_DATES = ElementsList(
            "div[class*=drawer-content][role=dialog] div[class*=table-tbody] div[class*=table-row] div[class*=platform-table]",
            "Даты платежей",
        )

        self.PAYMENT_DELETE_BTN = Element("//span[@data-icon='Delete']", "Кнопка удалить")

        # AGREEMENT_TAB
        self.AGREEMENTS = ElementsList("[class*='table-row']", "Строки с соглашениями")

        self.AGREE_BTN = Element("(//span[@data-icon='CheckCircle']) [1]", "Кнопка согласовать")

        self.AGREEMENT_FLAG = ElementsList(
            "[class*='table-row'] [data-icon='CheckCircle']", "Кружок согласования документа"
        )

        self.TEXT_CELL = ElementsList("//td //div", "Столбцы с текстом")
