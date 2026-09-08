import re
from datetime import datetime, timedelta
from typing import Pattern

import allure

from api.nbss.finances.billing_requests import BillingRequests
from common.enums.billing_account_fields import BillingAccountFields
from common.helpers.checker import assert_that, wait_that
from common.helpers.string_helper import check_price, check_that_date_later
from common.helpers.time_helpers import delay, get_current_moscow_datetime, get_datetime_from_string
from models.context import test_context
from pages.base_page import BasePage
from pages.locators.nbss.dynamic_form_elements import DynamicForms
from pages.locators.nbss.finances.billing_accounts import BillingAccountsElements
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.ui_elements import Element


class BillingAccountsPage(BasePage):
    """Страница /bills/{account_num}/properties Биллинговые счета"""

    def __init__(self) -> None:
        super().__init__()
        self.base_page = BasePage()
        self.locators = BillingAccountsElements()
        self.dynamic = DynamicForms()
        self.client_profile_page = ClientProfilePage()
        self.billing_api = BillingRequests()

    @allure.step("Открыть страницу Биллинговые счета через бургер-меню")
    def open_billing_page_via_burger(self) -> None:
        self.locators.BURGER_MENU.select_by_value("Финансы > Биллинговые счета")
        self.locators.SELECTED_TAB_TITLE.wait_to_have_text("Биллинговые счета")
        self.locators.BILLING_LAUNCH_BTN.wait_to_be_visible()

    @allure.step("Открыть биллинговый счет с индексом {index}")
    def open_billing(self, index: int = 0) -> None:
        wait_that(
            lambda: self.locators.ACCOUNT_NUMS_LIST.elements_len() > index,
            message="Отсутствует нужное количество биллинговых счетов",
            timeout=15,
            exception=AssertionError,
        )
        self.locators.ACCOUNT_NUMS_LIST[index].wait_to_be_visible()
        self.locators.ACCOUNT_NUMS_LIST[index].click()
        self.locators.BILLING_NUM.wait_to_be_visible(timeout=15000)
        self.locators.BILLING_PROPERTIES.wait_to_be_visible()

    @allure.step("Открыть таб документы у биллинга")
    def open_documents_tab(self) -> None:
        self.locators.DOCUMENTS_TAB.wait_to_be_visible(timeout=15000)
        self.locators.DOCUMENTS_TAB.click()
        self.locators.DOCUMENT_ADD_BTN.wait_to_be_visible(timeout=15000)

    @allure.step("Проверить информацию о биллинговом счёте")
    def check_bill(
        self,
        bill_index: int = 0,
        billing_id: str | None = None,
        date: str | None = None,
        amount_due: float = 0,
        status_color: str = "green",
    ) -> None:
        self.locators.ACCOUNT_NUMS_LIST.wait_elements_visible(bill_index)
        if billing_id:
            self.locators.ACCOUNT_NUMS_LIST[bill_index].wait_to_have_text(billing_id)
        else:
            self.locators.ACCOUNT_NUMS_LIST[bill_index].wait_to_have_text(re.compile(r"\d{4}-\d{2}-\d{8}"))
        if date is None:
            date = get_current_moscow_datetime().strftime("%d.%m.%Y")
        self.locators.BILL_DATE[bill_index].wait_to_have_text(f"От {date}")
        if amount_due == 0:
            self.locators.BILL_AMOUNT_DUE[bill_index].wait_to_have_text("—")
        else:
            check_price(self.locators.BILL_AMOUNT_DUE[bill_index], amount_due)
        self.locators.BILL_STATUS[bill_index].element_have_css_color("background-color", status_color)

    @allure.step("Проверка отображения признака 'Рассрочка' у биллингового счёта")
    def check_installment_sign(self, bill_index: int = 0, timeout: int = 60) -> None:
        """
        Проверка того, что в списке биллинговых счетов у счёта отображается признак «Рассрочка».
        Список обновляется по кнопке «Обновить», так как признак проставляется не сразу после оформления рассрочки.

        :param bill_index: порядковый номер биллингового счёта в списке на UI (0 — первый)
        :param timeout: время ожидания появления признака
        :return: None
        """

        def is_sign_displayed() -> bool:
            self.locators.REFRESH_BTN.click()
            self.locators.ACCOUNT_NUMS_LIST.wait_to_have_count_or_greater(bill_index + 1)
            return "Рассрочка" in self.locators.BILL_INSTALLMENT_SIGN[bill_index].text

        wait_that(
            is_sign_displayed,
            timeout=timeout,
            sleep_seconds=5,
            exception=AssertionError,
            message=f"Признак 'Рассрочка' не отобразился у биллингового счёта за {timeout} секунд",
        )

    @allure.step("Проверка свойств биллинга")
    def check_billing_properties(self) -> None:
        billing_properties = [
            BillingAccountFields.billing_category,
            BillingAccountFields.payment_due_date,
            BillingAccountFields.period,
            BillingAccountFields.payment_amount,
            BillingAccountFields.related_inquiries,
            BillingAccountFields.is_restructuring,
            BillingAccountFields.in_balance,
            BillingAccountFields.out_balance,
            BillingAccountFields.paid_amount,
            BillingAccountFields.accounted_additional_charges,
            BillingAccountFields.charges_adjusted,
            BillingAccountFields.payments_adjusted,
            BillingAccountFields.accounted_billing_discounts,
            BillingAccountFields.accounted_charges,
            BillingAccountFields.accounted_payments,
            BillingAccountFields.accounted_product_discounts,
            BillingAccountFields.accounted_payment_adjustments,
            BillingAccountFields.accounted_charge_adjustments,
            BillingAccountFields.account_type,
            BillingAccountFields.generation_date,
        ]
        self.locators.BILLING_PROPERTIES.wait_elements_visible(len(billing_properties) - 1)
        for billing_property in billing_properties:
            self.locators.BILLING_PROPERTIES.to_contain_text_in_any(billing_property)

    @allure.step("Проверка значений свойств биллинга")
    def check_billing_properties_value(
        self,
        payment_due_date: datetime | None = None,
        start_period: datetime | None = None,
        end_period: datetime | None = None,
        payment_amount: float = 0,
        related_inquiries: str = "—",
        is_restructuring: str = "Нет",
        in_balance: float = 0,
        out_balance: float = 0,
        paid_amount: float = 0,
        accounted_additional_charges: float = 0,
        charges_adjusted: float = 0,
        payments_adjusted: float = 0,
        accounted_billing_discounts: float = 0,
        accounted_charges: float = 0,
        accounted_payments: float = 0,
        accounted_product_discounts: float = 0,
        accounted_payment_adjustments: float = 0,
        accounted_charge_adjustments: float = 0,
        account_type: str = "Основной счет",
        generation_date: datetime | None = None,
    ) -> None:
        time_for_close_period = 10
        time_for_generate = 100
        self.check_billing_properties()
        if payment_due_date:
            check_that_date_later(
                self.get_billing_property_value(BillingAccountFields.payment_due_date),
                payment_due_date,
                time_for_close_period,
            )
        if end_period:
            if start_period is None:
                start_period = end_period.replace(hour=0, minute=0, second=0, microsecond=0)
            current_start_period = get_datetime_from_string(
                self.get_billing_property_value(BillingAccountFields.period).text[:19]
            )
            current_end_period = get_datetime_from_string(
                self.get_billing_property_value(BillingAccountFields.period).text[-19:]
            )
            assert_that(
                lambda: current_start_period - start_period < timedelta(seconds=time_for_close_period),
                f"Начало периода отличается более чем на {time_for_close_period} секунд",
            )
            assert_that(
                lambda: current_end_period - end_period < timedelta(seconds=time_for_close_period),
                f"Конец периода отличается более чем на {time_for_close_period} секунд",
            )
        check_price(self.get_billing_property_value(BillingAccountFields.payment_amount), payment_amount)
        self.get_billing_property_value(BillingAccountFields.related_inquiries).wait_to_have_text(related_inquiries)
        self.get_billing_property_value(BillingAccountFields.is_restructuring).wait_to_have_text(is_restructuring)
        check_price(self.get_billing_property_value(BillingAccountFields.in_balance), in_balance)
        check_price(self.get_billing_property_value(BillingAccountFields.out_balance), out_balance)
        check_price(self.get_billing_property_value(BillingAccountFields.paid_amount), paid_amount)
        check_price(
            self.get_billing_property_value(BillingAccountFields.accounted_additional_charges),
            accounted_additional_charges,
        )
        check_price(self.get_billing_property_value(BillingAccountFields.charges_adjusted), charges_adjusted)
        check_price(self.get_billing_property_value(BillingAccountFields.payments_adjusted), payments_adjusted)
        check_price(
            self.get_billing_property_value(BillingAccountFields.accounted_billing_discounts),
            accounted_billing_discounts,
        )
        check_price(self.get_billing_property_value(BillingAccountFields.accounted_charges), accounted_charges)
        check_price(self.get_billing_property_value(BillingAccountFields.accounted_payments), accounted_payments)
        check_price(
            self.get_billing_property_value(BillingAccountFields.accounted_product_discounts),
            accounted_product_discounts,
        )
        check_price(
            self.get_billing_property_value(BillingAccountFields.accounted_payment_adjustments),
            accounted_payment_adjustments,
        )
        check_price(
            self.get_billing_property_value(BillingAccountFields.accounted_charge_adjustments),
            accounted_charge_adjustments,
        )
        self.get_billing_property_value(BillingAccountFields.account_type).wait_to_have_text(account_type)
        if generation_date:
            check_that_date_later(
                self.get_billing_property_value(BillingAccountFields.generation_date), generation_date, time_for_generate
            )

    def get_billing_property_value(self, field: BillingAccountFields) -> Element | list[Element]:
        if field.value in self.locators.BILLING_PROPERTIES.text_list:
            index = self.locators.BILLING_PROPERTIES.text_list.index(field.value)
            return self.locators.BILLING_PROPERTY_VALUES[index]
        else:
            raise AssertionError(f"Свойство '{field.value}' не найдено среди свойств биллинга")

    @allure.step("Проверка значений детали биллингового счёта")
    def check_detail(
        self,
        detail_index: int = 0,
        detail_name: str | None = None,
        charged: float = 0,
        discount: float = 0,
        charged_additionally: float = 0,
        unit: str = "Основное бизнес подразделение",
        subscriber: str = "—",
        tax_scheme: str = "Схема налогообложения по умолчанию",
        adjusted: float = 0,
        product: str = "—",
        repaid: float = 0,
        available_for_adjustment: float = 0,
        linked_inquiry: str = "—",
    ) -> None:
        self.locators.DETAIL.wait_elements_visible(detail_index)
        if detail_name:
            self.locators.DETAIL_NAME[detail_index].wait_to_have_text(detail_name)
        check_price(self.locators.DETAIL_CHARGED[detail_index], charged)
        if discount == 0:
            self.locators.DETAIL_DISCOUNT[detail_index].wait_to_have_text("—")
        else:
            check_price(self.locators.DETAIL_CHARGED[detail_index], discount)
        if charged_additionally == 0:
            self.locators.DETAIL_DISCOUNT[detail_index].wait_to_have_text("—")
        else:
            check_price(self.locators.DETAIL_CHARGED_ADDITIONALLY[detail_index], charged_additionally)
        self.locators.DETAIL_UNIT[detail_index].wait_to_have_text(unit)
        self.locators.DETAIL_SUBSCRIBER[detail_index].wait_to_have_text(subscriber)
        self.locators.DETAIL_TAX_SCHEME[detail_index].wait_to_have_text(tax_scheme)
        check_price(self.locators.DETAIL_ADJUSTED[detail_index], adjusted)
        self.locators.DETAIL_PRODUCT[detail_index].wait_to_have_text(product)
        check_price(self.locators.DETAIL_REPAID[detail_index], repaid)
        check_price(self.locators.DETAIL_AVAILABLE_ADJUSTMENT[detail_index], available_for_adjustment)
        self.locators.DETAIL_LINKED_INQUIRES[detail_index].wait_to_have_text(linked_inquiry)

    @allure.step("Проверка значений счет-фактуры биллингового счёта")
    def check_invoice(
        self,
        invoice_index: int = 0,
        invoice_type: str | None = None,
        number: str = re.compile(r"\d{4}-\d{2}-\d{1,2}"),
        date: datetime | None = None,
        amount: float = 0,
        tax: float = 0,
        unit: str = "Основное бизнес подразделение",
        adjustment_tax_invoice: Pattern[str] | str = "—",
        adjustment_number: int | str = "—",
        adjustment_date: datetime | None = None,
        adjusted: float | str = "—",
        balance: float | str = "—",
    ) -> None:
        time_for_invoice = 10
        self.locators.INVOICE.wait_elements_visible(invoice_index)
        if invoice_type:
            self.locators.INVOICE_TYPE[invoice_index].wait_to_have_text(invoice_type)
        self.locators.INVOICE_NUMBER[invoice_index].wait_to_have_text(number)
        if date:
            check_that_date_later(self.locators.INVOICE_DATE[invoice_index], date, time_for_invoice)
        check_price(self.locators.INVOICE_AMOUNT[invoice_index], amount)
        check_price(self.locators.INVOICE_TAX[invoice_index], tax)
        self.locators.INVOICE_UNIT[invoice_index].wait_to_have_text(unit)
        self.locators.INVOICE_ADJUSTMENT_TAX_INVOICE[invoice_index].wait_to_have_text(adjustment_tax_invoice)
        self.locators.INVOICE_ADJUSTMENT_NUMBER[invoice_index].wait_to_have_text(str(adjustment_number))
        if adjustment_date:
            check_that_date_later(
                self.locators.INVOICE_ADJUSTMENT_DATE[invoice_index], adjustment_date, time_for_invoice
            )
        if adjusted == "—":
            self.locators.INVOICE_ADJUSTED[invoice_index].wait_to_have_text(adjusted)
        else:
            check_price(self.locators.INVOICE_ADJUSTED[invoice_index], adjusted)
        if balance == "—":
            self.locators.INVOICE_BALANCE[invoice_index].wait_to_have_text(balance)
        else:
            check_price(self.locators.INVOICE_BALANCE[invoice_index], balance)

    @allure.step("Получение индекса счет-фактуры биллингового счёта")
    def get_invoice_index(self, invoice_type: str) -> int:
        """
        Метод получает индекс счета-фактуры по его типу в таблице счетов

        :param invoice_type: тип счета-фактуры для поиска
        :return: индекс найденного счета-фактуры в таблице
        :raises AssertionError: если счет-фактура с указанным типом не найден
        """
        self.locators.INVOICE.wait_to_be_visible()
        invoice_count = self.locators.INVOICE.elements_len()
        for invoice_index in range(invoice_count):
            try:
                self.locators.INVOICE_TYPE[invoice_index].wait_to_have_text(invoice_type)
                return invoice_index
            except Exception:
                continue
        raise AssertionError(f"Счет-фактура с типом '{invoice_type}' не найден")

    @allure.step("Выбрать нужный счет, запомнить значения полей 'Начислено' и 'Доначислено'")
    def choose_bill_and_get_charged_charged_additionally(self, bill_index: int = 0) -> tuple[float, float]:
        self.locators.ACCOUNT_NUMS_LIST.wait_to_be_visible()
        self.locators.ACCOUNT_NUMS_LIST.click(bill_index)
        self.locators.BILLING_PROPERTIES.wait_for_text_in_all(["Учтено начислений"])
        property_index = self.locators.BILLING_PROPERTIES.text_list.index("Учтено начислений")
        charged = float(self.locators.BILLING_PROPERTY_VALUES[property_index].text)
        self.locators.BILLING_PROPERTIES.wait_for_text_in_all(["Откорректировано начислений"])
        property_index = self.locators.BILLING_PROPERTIES.text_list.index("Откорректировано начислений")
        charged_additionally = float(self.locators.BILLING_PROPERTY_VALUES[property_index].text)
        return charged, charged_additionally

    @allure.step("Перейти на вкладку 'Детали', запомнить значение поля 'Откорректированно'")
    def get_detail_adjusted_property(self) -> float:
        self.locators.DETAILS_TAB.click()
        self.locators.DETAIL.wait_to_be_visible()
        return float(self.locators.DETAIL_ADJUSTED[0].text)

    @allure.step("Перейти на вкладку 'Счета-фактуры', запомнить значение поля 'Откорректированно'")
    def get_tax_invoice_adjusted_property(self, tax_invoice_type: str = "Счет-фактура на начисления") -> float:
        self.locators.INVOICES_TAB.click()
        self.locators.INVOICE.wait_to_be_visible()
        self.locators.INVOICE_TYPE.wait_for_text_in_all([tax_invoice_type])
        tax_invoice_index = self.locators.INVOICE_TYPE.text_list.index(tax_invoice_type)
        return float(self.locators.INVOICE_ADJUSTED[tax_invoice_index].text)

    @allure.step("Проверить отображение суммы корректировки на вкладке 'Свойства'")
    def check_charged_additionally_property(self, bill_id: str, amount: float, field: str, acc_num: int = 1) -> None:
        """
        Проверка отображения суммы корректировки начислений в свойствах биллингового счёта на UI
        :param bill_id: идентификатор биллингового счёта, в котором ожидается изменение значения
        :param amount: ожидаемая сумма корректировки
        :param field: название поля в bill info (например adjustedChargesWithTax), в котором ожидается появление значения
        :param acc_num: порядковый номер биллингового счёта в списке на UI (1 — первый, 2 — второй и т.д.)
        :return: None
        """
        self.billing_api.wait_bill_info_value(bill_id, field, int(amount))
        self.locators.REFRESH_BTN.click()
        self.locators.ACCOUNT_NUMS_LIST.wait_to_be_visible()
        self.locators.ACCOUNT_NUMS_LIST.click(acc_num)
        self.locators.BILLING_PROPERTIES.wait_for_text_in_all(["Учтено корректировок начислений"])
        property_index = self.locators.BILLING_PROPERTIES.text_list.index("Учтено корректировок начислений")
        self.locators.BILLING_PROPERTY_VALUES[property_index].scroll_into_view_if_needed()
        self.locators.BILLING_PROPERTY_VALUES[property_index].wait_to_have_text(f"{amount:.2f}")

    @allure.step("Перейти на вкладку 'Детали', проверить что сумма корректировки учтена")
    def check_detail_adjusted_property(self, amount: float, accrued: bool = True) -> None:
        """
        Проверка отображения суммы корректировки на вкладке «Детали»
        :param amount: ожидаемая сумма корректировки
        :param accrued: флаг проверки поля (True — проверка в поле «Начислено», False — в поле «Откорректировано»)
        :return: None
        """
        self.locators.DETAILS_TAB.click()
        self.locators.UPDATE_DETAILS_LIST_BTN.click()
        self.locators.DETAIL.wait_to_be_visible()
        if accrued:
            self.locators.DETAIL_CHARGED[0].wait_to_have_text(f"{amount:.2f}")
        else:
            self.locators.DETAIL_ADJUSTED[0].wait_to_have_text(f"{amount:.2f}")

    @allure.step("Перейти на вкладку 'Счета-фактуры', проверить что сумма корректировки учтена")
    def check_tax_invoice_adjusted_property(
        self,
        amount: float,
        tax_invoice_type: str = "Исправленный счет-фактура на начисления",
    ) -> None:
        self.locators.INVOICES_TAB.click()
        self.locators.UPDATE_INVOICE_LIST_BTN.click()
        self.locators.INVOICE.wait_to_be_visible()
        self.locators.INVOICE_TYPE.wait_for_text_in_all([tax_invoice_type])
        tax_invoice_index = self.locators.INVOICE_TYPE.text_list.index(tax_invoice_type)
        self.locators.INVOICE_ADJUSTED[tax_invoice_index].wait_to_have_text(f"{amount:.2f}")

    @allure.step("Запуск внеочередного биллинга")
    def run_unscheduled_billing(self, account_num: int | None = None) -> str:
        self.locators.BILLING_LAUNCH_BTN.click()
        self.locators.MODAL.wait_to_be_visible()
        self.locators.MODAL_SECOND_BTN.click()
        self.locators.MODAL.wait_not_to_be_visible()
        self.locators.INFO_MESSAGE[0].wait_to_have_text("Формируется заявка на запуск")
        self.locators.INFO_MESSAGE.wait_elements_visible(1)
        if account_num:
            message = re.compile(
                f"Запущен внеочередной биллинг по лицевому счету: {account_num}"
                r"Задание: \d{4}-\d{12}-\d{2}"
            )
        else:
            message = re.compile(r"Запущен внеочередной биллинг по лицевому счету: \d+Задание: \d{4}-\d{12}-\d{2}")
        self.locators.INFO_MESSAGE[-1].wait_to_have_text(message)
        return self.locators.INFO_MESSAGE[-1].text[-20:]

    @allure.step("Запуск внеочередного биллинга")
    def run_unscheduled_billing_and_wait_completion(self) -> None:
        self.run_unscheduled_billing()
        self.billing_api.wait_finish_billing(
            self.billing_api.get_billing_profile_id(test_context.client.agreement.account.id)
        )
        self.locators.REFRESH_BTN.click()
        self.locators.ACCOUNT_NUMS_LIST.wait_to_have_count_or_greater(1, timeout=15000)

    @allure.step("Проверка атрибутов задания биллинга")
    def check_billing_task(
        self,
        task_index: int = 0,
        task: str | None = None,
        task_type: str | None = None,
        run_date: datetime | None = None,
        status: str | None = None,
        user: str | None = None,
        billing_type: str | None = None,
        bill_date: datetime | None = None,
    ) -> None:
        time_for_billing = 60
        self.locators.BILLING_TASK.wait_elements_visible(task_index)
        if task:
            self.locators.TASK_NUMBER_LIST[task_index].wait_to_have_text(task)
        if task_type:
            self.locators.TASK_TYPE_LIST[task_index].wait_to_have_text(task_type)
        if run_date:
            check_that_date_later(self.locators.TASK_RUN_DATE_LIST[task_index], run_date, time_for_billing)
        if status:
            self.locators.TASK_STATUS_LIST[task_index].wait_to_have_text(status)
        if user:
            self.locators.TASK_USER_LIST[task_index].wait_to_have_text(user)
        if billing_type:
            self.locators.TASK_BILLING_TYPE_LIST[task_index].wait_to_have_text(billing_type)
        if bill_date:
            check_that_date_later(self.locators.TASK_BILLING_DATE_LIST[task_index], bill_date, time_for_billing)

    @allure.step("Проверить вкладку 'Связанные операции'")
    def check_linked_operation_tab(
        self, repayments: float = 0, debited: float = 0, charged_additionally: float = 0
    ) -> None:
        self.locators.LINKED_OPERATIONS_VALUE_LOADER.wait_not_to_be_visible()
        expected_heading = {"Погашения": repayments, "Списано": debited, "Доначислено": charged_additionally}

        assert_that(
            lambda: len(self.locators.LINKED_OPERATIONS.options.keys()) > 0,
            "Заголовки связанных операций не загрузились",
            timeout=10,
        )

        assert_that(
            lambda: len(self.locators.LINKED_OPERATIONS.options.keys()) == len(expected_heading),
            f"Ожидалось {len(expected_heading)} элемента",
            timeout=10,
        )

        for heading_name, heading_value in expected_heading.items():
            expected_text = f"{heading_name}: {heading_value:.2f}"
            assert_that(
                lambda text=expected_text: text in self.locators.LINKED_OPERATIONS.options.keys(),
                f"Ожидалось присутствие заголовка '{expected_text}'",
                timeout=10,
            )

    @allure.step("Проверка значений таблицы 'Погашено'")
    def check_repayments(
        self, repayments_index: int = 0, repayments_object: str = "—", date: datetime | None = None, amount: float = 0
    ) -> None:
        self.locators.TABLE_ROW_LINKED_OPERATION.wait_elements_visible(repayments_index)
        self.locators.REPAYMENTS_OBJECT[repayments_index].wait_to_have_text(repayments_object)
        check_that_date_later(self.locators.REPAYMENTS_DATE[repayments_index], date, 0)
        check_price(self.locators.REPAYMENTS_AMOUNT[repayments_index], amount)

    @allure.step("Проверка значений таблицы 'Списано'")
    def check_debited(
        self,
        debited_index: int = 0,
        date: datetime | None = None,
        amount: float = 0,
        tax: float = 0,
        detail: str = "—",
        reason: str = "—",
    ) -> None:
        self.locators.TABLE_ROW_LINKED_OPERATION.wait_elements_visible(debited_index)
        check_that_date_later(self.locators.DEBITED_DATE[debited_index], date, 0)
        check_price(self.locators.DEBITED_AMOUNT_AFTER_TAX[debited_index], amount)
        check_price(self.locators.DEBITED_TAX[debited_index], tax)
        self.locators.DEBITED_DETAIL[debited_index].wait_to_have_text(detail)
        self.locators.DEBITED_REASON[debited_index].wait_to_have_text(reason)

    @allure.step("Заказ документа")
    def order_document(
        self,
        document_type: str = "Счёт-фактура",
        document_format: str = "PDF",
        delivery_type: str = "Скачивание по ссылке",
        document_name: str | None = None,
    ) -> None:
        self.locators.DOCUMENT_ADD_BTN.wait_to_be_visible(timeout=15000)
        self.locators.DOCUMENT_ADD_BTN.click()
        self.locators.DOCUMENT_FORMATION_TAB_FORM.wait_to_be_visible()
        self.locators.LOAD_SPINS.wait_not_to_be_visible()
        self.locators.DOCUMENT_FORMATION_TAB_HEADER.wait_to_have_text("Параметры формирования документа", timeout=15000)
        self.locators.DOCUMENT_TYPE.select_by_value(document_type)
        self.locators.DOCUMENT_FORMAT.select_by_value(document_format)
        if document_name is not None:
            self.locators.DOCUMENT_NAME.fill(document_name)
        self.locators.DOCUMENT_DELIVERY_TYPE.select_by_value(delivery_type)
        self.dynamic.INNER_ACCEPT_BTN.wait_to_be_visible()
        self.dynamic.INNER_ACCEPT_BTN.click()

    @allure.step("Проверка документа")
    def check_document(self, document_type: str = "Счет-фактура", document_name: str = "nbss_invoice_bill.pdf") -> None:
        self.locators.REFRESH_DOCUMENT_BTN.wait_to_be_visible()
        self.locators.REFRESH_DOCUMENT_BTN.click()
        self.locators.DOCUMENTS.wait_to_be_visible(timeout=15000)
        document_index = next((i for i, x in enumerate(self.locators.DOCUMENTS) if document_name in x.text), None)
        for _ in range(3):
            if "Обработка завершена" in self.locators.DOCUMENTS[document_index].text:
                break
            delay(5, reason="Ожидание обновления статуса документа")
            self.locators.REFRESH_DOCUMENT_BTN.click()
        self.locators.DOCUMENTS[document_index].to_contain_text("Обработка завершена")
        self.locators.DOCUMENTS[document_index].to_contain_text(document_type)
        self.locators.DOCUMENTS[document_index].click()
        self.locators.DOCUMENT_DOWNLOAD_BTN.wait_to_be_enabled()
