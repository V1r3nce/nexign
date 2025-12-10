import re
from typing import Any, Pattern

import allure

from api.nbss.finances.adjustment_requests import AdjustmentRequests
from common.helpers.checker import assert_that
from common.helpers.string_helper import convert_amount_to_balance_string
from common.helpers.time_helpers import delay
from pages.base_page import BasePage
from pages.locators.nbss.finances.adjustments import (
    AdjustmentDetails,
    AdjustmentsElements,
    ChooseAdjustmentObjectForm,
    CreateAdjustmentForm,
)


class AdjustmentsPage(BasePage):
    """Страница /adjustments Корректировки"""

    def __init__(self) -> None:
        super().__init__()
        self.locators = AdjustmentsElements()
        self.details_locators = AdjustmentDetails()
        self.create_adjustment_form = CreateAdjustmentForm()
        self.choose_adjustment_object_form = ChooseAdjustmentObjectForm()

    @allure.step("Проверка активных кнопок")
    def check_buttons(self) -> None:
        self.locators.ADD_ADJUSTMENT_BTN.wait_to_be_enabled()
        self.locators.ADD_ADJUSTMENT_BTN.wait_to_have_text("Добавить корректировку")
        self.locators.UPDATE_TABLE_BTN.wait_to_be_enabled()
        self.locators.OPEN_BILLING_FORM.wait_to_be_enabled()
        self.locators.OPEN_BILLING_FORM.wait_to_have_text("Провести биллинг")

    @allure.step("Открыть форму для добавления корректировки начисления")
    def open_add_adjustment_form(self) -> None:
        self.locators.LOADER_SPIN.not_to_be_visible()
        self.locators.CURRENCY.wait_to_be_visible()
        self.locators.ADD_ADJUSTMENT_BTN.wait_to_be_visible()
        self.locators.ADD_ADJUSTMENT_BTN.select_by_value("Ввод корректировки начисления")

    @allure.step("Открыть форму для добавления корректировки платежа")
    def open_add_payment_form(self) -> None:
        self.locators.LOADER_SPIN.not_to_be_visible()
        self.locators.CURRENCY.wait_to_be_visible()
        self.locators.ADD_ADJUSTMENT_BTN.wait_to_be_visible()
        self.locators.ADD_ADJUSTMENT_BTN.select_by_value("Ввод корректировки платежа")

    @allure.step(
        "Заполнить форму создания корректировки: Дата - {date_time}, Сумма - {sum_with_tax}, Комментарий - {comment}"
    )
    def fill_add_adjustment_form(
        self,
        adjustment_option: str,
        adjustment_type: str,
        correction_type: str = "target",
        correction_object: str = "bill",
        bill_number: str = None,
        end_date_period: str = None,
        detail_name: str = None,
        date_time: str = None,
        sum_with_tax: str = None,
        comment: str = None,
    ) -> None:
        if adjustment_option == "charge":
            if correction_type == "target":
                self.create_adjustment_form.ADJUSTMENT_TARGET.select_by_value("Цель")
                self.fill_detail_input_create_adjustment_form(detail_name)
            if correction_type == "object":
                self.create_adjustment_form.ADJUSTMENT_TARGET.select_by_value("Объект")
                if correction_object == "bill":
                    self.fill_bill_input_create_adjustment_form(bill_number, end_date_period)
                if correction_object == "invoice":
                    self.fill_tax_invoice_input_create_adjustment_form("Счет-фактура на начисления")

        if adjustment_option == "payment":
            self.create_adjustment_form.PAYMENT_INPUT.wait_to_be_visible()
            self.create_adjustment_form.PAYMENT_INPUT.click()
            self.choose_adjustment_object_form.PAYMENT[0].click()
            self.choose_adjustment_object_form.CHOOSE_BTN.click()

        if adjustment_type == "negative":
            self.create_adjustment_form.ADJUSTMENT_TYPE_RADIOBUTTONS.select_by_value("Отрицательная корректировка")
        elif adjustment_type == "positive":
            self.create_adjustment_form.ADJUSTMENT_TYPE_RADIOBUTTONS.select_by_value("Положительная корректировка")

        delay(0.5, "Для того, чтобы при клике на select появились опции")
        self.select_reason(adjustment_option, adjustment_type, correction_object)
        self.create_adjustment_form.ADJUSTMENT_DATE_INPUT.fill(date_time)
        self.create_adjustment_form.SUM_WITH_TAX_INPUT.fill(sum_with_tax)
        self.create_adjustment_form.COMMENT_INPUT.type(comment)
        self.create_adjustment_form.ADD_ADJUSTMENT_BUTTON.click()
        self.locators.BILLING_TITLE.not_to_be_visible(timeout=10000)

    def select_reason(self, adjustment_option: str, adjustment_type: str, correction_object: str = None) -> None:
        if adjustment_option == "charge":
            if adjustment_type == "negative":
                if correction_object == "invoice":
                    self.create_adjustment_form.REASON_SELECT.select_by_value("Отрицательная корректировка счёт-фактуры")
                else:
                    self.create_adjustment_form.REASON_SELECT.select_by_value("Отрицательная корректировка счета")
            elif adjustment_type == "positive":
                self.create_adjustment_form.REASON_SELECT.select_by_value(
                    "Положительная корректировка детали счета в текущем периоде"
                )
        elif adjustment_option == "payment":
            if adjustment_type == "positive":
                self.create_adjustment_form.REASON_SELECT.select_by_value("Положительная корректировка платежа")
            else:
                self.create_adjustment_form.REASON_SELECT.select_by_value("Корректировка платежа")

    @allure.step("Открыть форму для проведения биллинга")
    def open_billing_form(self) -> None:
        self.locators.OPEN_BILLING_FORM.click()
        self.open_billing_form.START_BILLING.wait_to_be_visible()
        self.open_billing_form.START_BILLING.not_to_be_enabled()

    def check_adjustment(
        self,
        idx: int,
        adjustment_id: int = None,
        included_in_bill: str | Pattern[str] = None,
        date: str = None,
        adjustment_type: str = None,
        sum_with_tax: float = None,
        tax: float = None,
        status: str = None,
        reason: str = None,
        target_type: str = None,
        target: str | Pattern[str] = None,
        document_number: str = None,
        document_date: str = None,
        transferred: str = None,
        advance: str = None,
    ) -> None:
        self.locators.ADJUSTMENTS.wait_elements_visible(idx)
        column_list = [
            "ID",
            "Учтено в счете",
            "Тип",
            "Дата",
            "Сумма с учётом налога",
            "Налог",
            "Статус",
            "Причина",
            "Целевой тип счёта",
            "Цель",
            "Номер документа основания",
            "Дата документа основания",
            "Перенесено",
            "Аванс",
        ]
        if self.locators.ADJUSTMENT_TITLE.elements_len() != len(column_list):
            self.locators.SETTING_BTN.click()
            self.locators.COLUMN_LIST.choose_all_options()
            self.locators.SETTING_BTN.click()
        self.locators.ADJUSTMENT_TITLE.wait_to_have_count(len(column_list))
        self.locators.ADJUSTMENT_TITLE.wait_for_text_in_all(column_list)

        if adjustment_id:
            self.locators.ADJUSTMENT_ID[idx].wait_to_have_text(str(adjustment_id))
        if included_in_bill:
            self.locators.INCLUDED_IN_BILL[idx].wait_to_have_text(included_in_bill)
        if date:
            self.locators.ADJUSTMENT_DATE[idx].to_contain_text(date)
        if adjustment_type:
            self.locators.ADJUSTMENT_TYPE[idx].wait_to_have_text(adjustment_type)
        if sum_with_tax:
            self.locators.SUM_WITH_TAX[idx].wait_to_have_text(convert_amount_to_balance_string(sum_with_tax))
        if tax:
            self.locators.TAX[idx].wait_to_have_text(f"{tax:.2f}")
        if status:
            self.locators.STATUS[idx].wait_to_have_text(status)
        if reason:
            self.locators.REASON[idx].wait_to_have_text(reason)
        if target_type:
            self.locators.TARGET_TYPE[idx].wait_to_have_text(target_type)
        if target:
            self.locators.TARGET[idx].wait_to_have_text(target)
        if document_number:
            self.locators.DOCUMENT_NUMBER[idx].wait_to_have_text(document_number)
        if document_date:
            self.locators.DOCUMENT_DATE[idx].wait_to_have_text(document_date)
        if transferred:
            self.locators.TRANSFERRED[idx].wait_to_have_text(transferred)
        if advance:
            self.locators.ADVANCE[idx].wait_to_have_text(f"{float(advance):,.2f}".replace(",", " "))

    def check_adjustment_on_billing_form(
        self,
        idx: int,
        included_in_bill: str,
        adjustment_type: str,
        sum_with_tax: str,
        tax: str,
        reason: str,
        target: str,
        advance: str,
    ) -> None:
        if included_in_bill:
            self.locators.INCLUDED_IN_BILL_BILLING[idx].to_contain_text(included_in_bill)
        self.locators.ADJUSTMENT_TYPE_BILLING[idx].wait_to_have_text(adjustment_type)
        self.locators.SUM_WITH_TAX_BILLING[idx].wait_to_have_text(sum_with_tax)
        self.locators.TAX_BILLING[idx].wait_to_have_text(tax)
        self.locators.REASON_BILLING[idx].wait_to_have_text(reason)
        self.locators.TARGET_BILLING[idx].wait_to_have_text(target)
        self.locators.ADVANCE_BILLING[idx].wait_to_have_text(advance)

    def check_general_input(self) -> None:
        self.create_adjustment_form.ADJUSTMENT_TYPE_RADIOBUTTONS.wait_to_have_text(
            re.compile(r"Положительная корректировка")
        )
        self.create_adjustment_form.ADJUSTMENT_TYPE_RADIOBUTTONS.wait_to_have_text(
            re.compile(r"Отрицательная корректировка")
        )
        assert_that(
            lambda: self.create_adjustment_form.ADJUSTMENT_TYPE_RADIOBUTTONS.checked_value
            == "Отрицательная корректировка",
            "По умолчанию не выбрано 'Отрицательная корректировка'",
        )

        self.create_adjustment_form.ADJUSTMENT_TYPE_RADIOBUTTONS.check_attribute_not_contain_value("disabled", "")
        self.create_adjustment_form.ADJUSTMENT_DATE_INPUT.check_attribute_not_contain_value("disabled", "")
        self.create_adjustment_form.SUM_WITH_TAX_INPUT.check_attribute_by_value("disabled", "")
        self.create_adjustment_form.TAX_INPUT.check_attribute_by_value("disabled", "")
        self.create_adjustment_form.REASON_SELECT.check_attribute_by_value("disabled", "")
        self.create_adjustment_form.COMMENT_INPUT.check_attribute_not_contain_value("disabled", "")

        self.create_adjustment_form.ADJUSTMENT_TYPE_RADIOBUTTONS.check_attribute_by_value("aria-required", "true")
        self.create_adjustment_form.ADJUSTMENT_DATE_INPUT.check_attribute_by_value("aria-required", "true")
        self.create_adjustment_form.SUM_WITH_TAX_INPUT.check_attribute_by_value("aria-required", "true")
        self.create_adjustment_form.TAX_INPUT.check_attribute_by_value("aria-required", "true")
        self.create_adjustment_form.REASON_SELECT.check_attribute_by_value("aria-required", "true")
        self.create_adjustment_form.COMMENT_INPUT.check_attribute_not_contain_value("aria-required", "true")

    @allure.step("Проверка формы 'Ввод корректировки платежа'")
    def check_create_payment_adjustment_form(self) -> None:
        self.create_adjustment_form.TITLE.wait_to_have_text("Ввод корректировки платежа")
        self.create_adjustment_form.PAYMENT_INPUT.check_attribute_not_contain_value("disabled", "")
        self.create_adjustment_form.PAYMENT_INPUT.check_attribute_by_value("aria-required", "true")
        self.check_general_input()

    @allure.step("Проверка формы 'Ввод корректировки начисления'")
    def check_create_charge_adjustment_form(self) -> None:
        self.create_adjustment_form.TITLE.wait_to_have_text("Ввод корректировки начисления")
        self.create_adjustment_form.ADJUSTMENT_TARGET.all_elements_not_to_have_class(re.compile(r"disabled"))
        assert_that(
            lambda: self.create_adjustment_form.ADJUSTMENT_TARGET.checked_value == "Объект",
            "По умолчанию не выбрано 'Объект'",
        )
        self.create_adjustment_form.ADJUSTMENT_OBJECT.check_attribute_not_contain_value("disabled", "")
        self.create_adjustment_form.ADJUSTMENT_OBJECT.to_contain_text("Счет")
        self.create_adjustment_form.DETAILS.check_attribute_by_value("disabled", "")

        self.create_adjustment_form.ADJUSTMENT_TARGET.check_attribute_not_contain_value("aria-required", "true")
        self.create_adjustment_form.ADJUSTMENT_OBJECT.check_attribute_by_value("aria-required", "true")
        self.create_adjustment_form.DETAILS.check_attribute_not_contain_value("aria-required", "true")
        self.check_general_input()

    @allure.step("Заполнить поле 'Платежи'")
    def fill_payment_input_create_adjustment_form(
        self, payment_date: str | None, document_number: int | str, amount: float
    ) -> None:
        self.create_adjustment_form.PAYMENT_INPUT.click()
        self.choose_adjustment_object_form.TITLE.wait_to_be_visible()
        self.choose_adjustment_object_form.TITLE.to_contain_text("Выбор платежа")
        self.choose_adjustment_object_form.PAYMENT.click(0)
        self.choose_adjustment_object_form.CHOOSE_BTN.click()
        if payment_date is None:
            self.create_adjustment_form.PAYMENT_INPUT.to_contain_text(str(document_number))
            self.create_adjustment_form.PAYMENT_INPUT.to_contain_text(str(amount))
        else:
            self.create_adjustment_form.PAYMENT_INPUT.to_contain_text(
                f"{document_number} от {payment_date}.000 на сумму {amount}"
            )

    @allure.step("Заполнить поле 'Счет'")
    def fill_bill_input_create_adjustment_form(self, bill_number: str, end_date_period: str) -> None:
        self.create_adjustment_form.ADJUSTMENT_OBJECT_VALUE.click()
        self.choose_adjustment_object_form.TITLE.to_contain_text("Выбор счёта")
        self.choose_adjustment_object_form.BILL.click(0)
        self.choose_adjustment_object_form.CHOOSE_BTN.click()
        self.create_adjustment_form.ADJUSTMENT_OBJECT_VALUE.to_contain_text(f"Счёт №{bill_number} от {end_date_period}")

    @allure.step("Заполнить поле 'Счет-фактура'")
    def fill_tax_invoice_input_create_adjustment_form(self, tax_invoice_type: str) -> str:
        self.create_adjustment_form.ADJUSTMENT_OBJECT.select_by_value("Счет-фактура")
        self.create_adjustment_form.ADJUSTMENT_OBJECT_VALUE.click()

        with allure.step("На форме 'Выбор счета-фактуры' выбрать необходимую счет-фактуру"):
            self.choose_adjustment_object_form.TITLE.to_contain_text("Выбор счёта-фактуры")
            self.choose_adjustment_object_form.TAX_INVOICE_TYPE.wait_for_text_in_all([tax_invoice_type])
            tax_invoice_index = self.choose_adjustment_object_form.TAX_INVOICE_TYPE.text_list.index(tax_invoice_type)
            self.choose_adjustment_object_form.TAX_INVOICE.click(tax_invoice_index)
            tax_invoice_number = self.choose_adjustment_object_form.TAX_INVOICE_NUMBER[tax_invoice_index].text
            end_date_period = self.choose_adjustment_object_form.TAX_INVOICE_DATE[tax_invoice_index].text
            self.choose_adjustment_object_form.CHOOSE_BTN.click()

        with allure.step("Проверить изменение формы"):
            tax_invoice = f"№{tax_invoice_number} от {end_date_period}"
            self.create_adjustment_form.ADJUSTMENT_OBJECT_VALUE.to_contain_text(tax_invoice)
            self.create_adjustment_form.DETAILS.not_to_be_visible()
            self.create_adjustment_form.TAX_INVOICE_LINE.wait_to_be_visible()
        return tax_invoice

    @allure.step("Заполнить поле 'Детали' при корректировке Цели")
    def fill_detail_input_create_adjustment_form(self, detail: str) -> None:
        self.create_adjustment_form.DETAILS.click()
        self.choose_adjustment_object_form.TITLE.to_contain_text("Выбор детали")
        self.choose_adjustment_object_form.DETAIL.wait_to_be_visible()
        while (
            detail not in self.choose_adjustment_object_form.DETAIL_NAME.text_list
            and self.page.locator(self.choose_adjustment_object_form.NEXT_PAGE_BTN.path).is_enabled()
        ):
            self.choose_adjustment_object_form.NEXT_PAGE_BTN.click()
            self.choose_adjustment_object_form.DETAIL.wait_to_be_visible()

        detail_index = self.choose_adjustment_object_form.DETAIL_NAME.text_list.index(detail)
        self.choose_adjustment_object_form.DETAIL[detail_index].click()
        self.choose_adjustment_object_form.CHOOSE_BTN.click()
        self.create_adjustment_form.DETAILS.to_contain_text(detail)

    @allure.step("Заполнить поле 'Детали' при корректировке Объекта 'Счет'")
    def fill_bill_detail_input_create_adjustment_form(self) -> Any:
        self.create_adjustment_form.DETAILS.click()
        self.choose_adjustment_object_form.TITLE.to_contain_text("Выбор деталей счёта")
        self.choose_adjustment_object_form.DETAIL.click(0)
        detail = self.choose_adjustment_object_form.DETAIL_NAME[0].text
        self.choose_adjustment_object_form.CHOOSE_BTN.click()
        self.create_adjustment_form.DETAILS.to_contain_text(detail)
        return detail

    def fill_other_required_input_create_adjustment_form(
        self,
        adjustment_sum: float,
        reason: str,
        adjustment_type: str = None,
        adjustment_date: str = None,
    ) -> float:
        if adjustment_type:
            self.create_adjustment_form.ADJUSTMENT_TYPE_RADIOBUTTONS.select_by_value(adjustment_type)
        if adjustment_date:
            self.create_adjustment_form.ADJUSTMENT_DATE_INPUT.fill(adjustment_date)
        self.create_adjustment_form.SUM_WITH_TAX_INPUT.fill(str(adjustment_sum))
        self.create_adjustment_form.TAX_INPUT.check_attribute_not_contain_value("value", "")
        tax = float(self.create_adjustment_form.TAX_INPUT.text)
        self.create_adjustment_form.REASON_SELECT.select_by_value(reason)
        self.create_adjustment_form.ADD_ADJUSTMENT_BUTTON.click()
        return tax

    @allure.step("Проверка окна с подтверждением аннулирования")
    def check_cancel_adjustment_form(self) -> None:
        self.locators.MODAL.wait_to_be_visible()
        self.locators.MODAL_TITLE.wait_to_have_text("Аннулирование")
        self.locators.MODAL_BODY_TEXT[0].to_contain_text("Вы действительно хотите аннулировать корректировку")
        self.locators.MODAL_FIRST_BTN.wait_to_be_enabled()
        self.locators.MODAL_SECOND_BTN.wait_to_be_enabled()

    @allure.step("Получение информации о таблице корректировок")
    def get_info_about_adjustment_table(self) -> tuple[list[str | None], list[list[str | None]]]:
        self.check_adjustment(0)
        headers = [title.text for title in self.locators.ADJUSTMENT_TITLE]
        adjustment_list: list = []
        properties_list = [
            self.locators.ADJUSTMENT_ID,
            self.locators.INCLUDED_IN_BILL,
            self.locators.ADJUSTMENT_TYPE,
            self.locators.ADJUSTMENT_DATE,
            self.locators.SUM_WITH_TAX,
            self.locators.TAX,
            self.locators.STATUS,
            self.locators.REASON,
            self.locators.TARGET_TYPE,
            self.locators.TARGET,
            self.locators.DOCUMENT_NUMBER,
            self.locators.DOCUMENT_DATE,
            self.locators.TRANSFERRED,
            self.locators.ADVANCE,
        ]
        for i in range(self.locators.ADJUSTMENTS.elements_len()):
            adjustment_list.append([])
            for adjustment_property in properties_list:
                adjustment_property.wait_to_be_visible()
                property_value = adjustment_property[i].text
                if property_value == "—":
                    adjustment_list[i].append(None)
                else:
                    adjustment_list[i].append(property_value)
        return headers, adjustment_list

    @allure.step("Проверка корректировки переноса баланса")
    def check_monetary_balance_transfer_adjustment(
        self,
        account_id: int,
        transfer_type: str,
        amount: int,
        alter_reason: str = None,
        seq_number: int = 1,
    ) -> None:
        """
        Метод ожидает завершение корректировки. Далее проверяет корректировку на наличие нужного типа, причины, суммы и суммы погашения.

        :param account_id: Идентификатор лицевого счета, который участвовал в переносе баланса
        :param transfer_type: тип переноса. Может быть donor, donor_postpaid, recipient
        :param amount: сумма переноса баланса
        :param alter_reason: причина, которую можно указать при необходимости
        :param seq_number: последовательный номер переноса на данном лицевом счете
        """
        adj_api = AdjustmentRequests()
        with allure.step("Ожидание завершения переноса баланса"):
            adj_api.wait_adjustment_status(account_id, adjustment_seq_number=seq_number)
        if transfer_type in ["donor", "donor_postpaid"]:
            reason = "Перенос средств по заявлению клиента"
            adj_type = "Отрицательная корректировка лицевого счета"
            amount = -amount
        else:
            reason = "Перенос средств по заявлению клиента."
            adj_type = "Положительная корректировка счета"
        if alter_reason is not None:
            reason = alter_reason
            adj_type = "Отрицательная корректировка платежа"
        with allure.step("Проверка наличия корректировки с заданными параметрами"):
            self.check_adjustment(
                0,
                sum_with_tax=amount,
                adjustment_type=adj_type,
                reason=reason,
            )
        with allure.step("Проверка деталей корректировки"):
            self.locators.ADJUSTMENT_DATE[0].click()
            self.details_locators.RELATED_TAB.click()
            if transfer_type == "donor":
                self.details_locators.REFRESH_BTN.click()
                self.details_locators.REPAYMENTS_ROW.wait_to_have_count(1)
                self.details_locators.REPAYMENTS_SUM.wait_to_have_text(convert_amount_to_balance_string(-amount))
            else:
                self.details_locators.REPAYMENTS_ROW.wait_to_have_count(0)
            self.details_locators.CLOSE_BTN.click()
