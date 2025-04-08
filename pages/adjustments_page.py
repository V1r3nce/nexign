import re

import allure
from playwright.sync_api import Page

from common.helpers.checker import assert_that
from common.helpers.data_generator import get_current_datetime_string
from pages.base_page import BasePage
from pages.locators.adjustments import Adjustments, ChoosePaymentForm, CreateAdjustmentForm


class AdjustmentsPage(BasePage):
    """Страница /adjustments Корректировки"""

    def __init__(self, page: Page):
        super().__init__(page)
        self.locators = Adjustments(page)
        self.create_adjustment_form = CreateAdjustmentForm(page)
        self.choose_payment_form = ChoosePaymentForm(page)

    @allure.step("Проверка активных кнопок")
    def check_buttons(self) -> None:
        self.locators.ADD_ADJUSTMENT_BTN.wait_to_be_enabled()
        self.locators.ADD_ADJUSTMENT_BTN.wait_to_have_text("Добавить корректировку")
        self.locators.UPDATE_TABLE_BTN.wait_to_be_enabled()

    def check_adjustment(
        self,
        idx: int,
        included_in_bill: str = None,
        date: str = None,
        adjustment_type: str = None,
        sum_with_tax: float = None,
        tax: float = None,
        status: str = None,
        reason: str = None,
        target: str = None,
    ) -> None:
        self.locators.ADJUSTMENT.wait_elements_visible(idx)
        if included_in_bill:
            self.locators.INCLUDED_IN_BILL[idx].wait_to_have_text(included_in_bill)
        if date:
            self.locators.ADJUSTMENT_DATE[idx].to_contain_text(date)
        if adjustment_type:
            self.locators.ADJUSTMENT_TYPE[idx].wait_to_have_text(adjustment_type)
        if sum_with_tax:
            self.locators.SUM_WITH_TAX[idx].wait_to_have_text(f"{sum_with_tax:.2f}")
        if tax:
            self.locators.TAX[idx].wait_to_have_text(f"{tax:.2f}")
        if status:
            self.locators.STATUS[idx].wait_to_have_text(status)
        if reason:
            self.locators.REASON[idx].wait_to_have_text(reason)
        if target:
            self.locators.TARGET[idx].wait_to_have_text(target)

    @allure.step("Проверка формы 'Ввод корректировки платежа'")
    def check_create_payment_adjustment_form(self) -> None:
        self.create_adjustment_form.TITLE.wait_to_have_text("Ввод корректировки платежа")
        self.create_adjustment_form.ADJUSTMENT_TYPE_RADIOBUTTONS.wait_to_have_text(
            re.compile(r"Положительная корректировка")
        )
        self.create_adjustment_form.ADJUSTMENT_TYPE_RADIOBUTTONS.wait_to_have_text(
            re.compile(r"Отрицательная корректировка")
        )
        assert_that(
            lambda: self.create_adjustment_form.ADJUSTMENT_TYPE_RADIOBUTTONS.checked_value
            == "Положительная корректировка",
            "По умолчанию не выбрано 'Положительная корректировка'",
        )

        self.create_adjustment_form.PAYMENT_INPUT.not_to_have_class(re.compile(r"ant-input-disabled"))
        self.create_adjustment_form.ADJUSTMENT_TYPE_RADIOBUTTONS.not_to_have_class(re.compile(r"ant-input-disabled"))
        self.create_adjustment_form.ADJUSTMENT_DATE_INPUT.not_to_have_class(re.compile(r"ant-input-disabled"))
        self.create_adjustment_form.SUM_WITH_TAX_INPUT.not_to_have_class(re.compile(r"ant-input-disabled"))
        self.create_adjustment_form.TAX_INPUT.not_to_have_class(re.compile(r"ant-input-disabled"))
        self.create_adjustment_form.REASON_SELECT.not_to_have_class(re.compile(r"ant-input-disabled"))
        self.create_adjustment_form.COMMENT_INPUT.not_to_have_class(re.compile(r"ant-input-disabled"))

        self.create_adjustment_form.PAYMENT_INPUT.check_attribute_by_value("aria-required", "true")
        self.create_adjustment_form.ADJUSTMENT_TYPE_RADIOBUTTONS.check_attribute_by_value("aria-required", "true")
        self.create_adjustment_form.ADJUSTMENT_DATE_INPUT.check_attribute_by_value("aria-required", "true")
        self.create_adjustment_form.SUM_WITH_TAX_INPUT.check_attribute_by_value("aria-required", "true")
        self.create_adjustment_form.TAX_INPUT.check_attribute_by_value("aria-required", "true")
        self.create_adjustment_form.REASON_SELECT.check_attribute_by_value("aria-required", "true")
        self.create_adjustment_form.COMMENT_INPUT.check_attribute_not_contain_value("aria-required", "true")

    @allure.step("Заполнить поле 'Платежи'")
    def fill_payment_input_create_adjustment_form(self, payment_date: str, document_number: int, amount: float) -> None:
        self.create_adjustment_form.PAYMENT_INPUT.click(click_count=2)
        self.choose_payment_form.TITLE.to_contain_text("Выбор платежа")
        self.choose_payment_form.PAYMENT.click(0)
        self.choose_payment_form.CHOOSE_BTN.click()
        self.create_adjustment_form.PAYMENT_INPUT.to_contain_text(
            f"{document_number} от {payment_date}.000 на сумму {amount}"
        )

    def fill_other_required_input_create_adjustment_form(
        self,
        adjustment_type: str,
        adjustment_sum: float,
        reason: str,
        adjustment_date: str = get_current_datetime_string(is_full_format=False),
    ) -> float:
        self.create_adjustment_form.ADJUSTMENT_TYPE_RADIOBUTTONS.select_by_value(adjustment_type)
        self.create_adjustment_form.ADJUSTMENT_DATE_INPUT.fill(adjustment_date)
        self.create_adjustment_form.SUM_WITH_TAX_INPUT.fill(str(adjustment_sum))
        self.create_adjustment_form.TAX_INPUT.check_attribute_not_contain_value("value", "")
        tax = float(self.create_adjustment_form.TAX_INPUT.text)
        self.create_adjustment_form.REASON_SELECT.select_by_value(reason)
        self.create_adjustment_form.ADD_ADJUSTMENT_BTN.click()
        return tax
