import re
from typing import Pattern

import allure

from models.context import test_context
from models.product import AdditionalProduct, MainProduct
from pages.base_page import BasePage
from pages.locators.nbss.finances.discount_and_charges import (
    AddBillingDiscountFormStep4,
    AddBillingDiscountOrChargeForm,
    AddBillingDiscountOrChargeFormStep3,
    AddProductOfferForm,
    DiscountAndChargesElements,
    TemplateForm,
)


class DiscountAndChargesPage(BasePage):
    """Страница /finance/discounts Скидки/Доначисления"""

    def __init__(self) -> None:
        super().__init__()

        self.locators = DiscountAndChargesElements()
        self.add_discount_form_step_1 = AddBillingDiscountOrChargeForm()
        self.template_form = TemplateForm()
        self.add_discount_form_step_2 = AddProductOfferForm()
        self.add_discount_form_step_3 = AddBillingDiscountOrChargeFormStep3()
        self.add_discount_form_step_4 = AddBillingDiscountFormStep4()

    @allure.step("Проверка свойств биллинговой скидки")
    def check_properties(
        self,
        start_date: str,
        end_date: str,
        change_date: str | Pattern[str] | None = None,
        priority: str = "1",
        user: str = "Admin",
        note: str = "—",
    ) -> None:
        """
        :param start_date: дата начала действия скидки
        :param end_date: дата окончания действия скидки
        :param change_date: дата изменения
        :param priority: приоритет скидки
        :param user: пользователь, создавший скидку
        :param note: комментарий
        """
        with allure.step("Проверяем свойства"):
            self.locators.PROPERTIES.wait_to_have_count(6)
            self.locators.PROPERTIES_VALUES.wait_to_have_count(6)
            self.locators.PROPERTIES_VALUES[0].wait_to_have_text(start_date)
            self.locators.PROPERTIES_VALUES[1].wait_to_have_text(end_date)
            self.locators.PROPERTIES_VALUES[2].wait_to_have_text(priority)
            self.locators.PROPERTIES_VALUES[3].wait_to_have_text(user)
            if change_date is None:
                change_date = re.compile(re.escape(start_date) + r"\s+\d{2}:\d{2}:\d{2}")
            self.locators.PROPERTIES_VALUES[4].wait_to_have_text(change_date)
            self.locators.PROPERTIES_VALUES[5].wait_to_have_text(note)

    @allure.step("Проверка условий применимости")
    def check_conditions_of_applicability(self, discount_amount: str = "10", threshold: str = "1000") -> None:
        self.locators.CONDITIONS_TAB.click()
        self.locators.DISCOUNT_VALUE.to_contain_text(discount_amount)
        self.locators.THRESHOLD_AMOUNT.to_contain_text(threshold, separated=True)

    @allure.step("Создаем скидку")
    def create_billing_discount(
        self,
        priority: str = "1",
        product: MainProduct | AdditionalProduct | None = None,
        discount_amount: str = "10",
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> None:
        if product is None:
            product = test_context.client.inquiry.product
        self.locators.SET_BTN.wait_to_be_visible()
        self.locators.SET_BTN.click()
        self.add_discount_form_step_1.TYPE.wait_to_be_visible()
        self.add_discount_form_step_1.TYPE.select_by_value("Скидка")
        self.add_discount_form_step_1.COMMENT.click()
        self.add_discount_form_step_1.TEMPLATE.click()
        self.template_form.TEMPLATE_TABLE.select_by_value("Скидка по умолчанию")
        self.template_form.INNER_ACCEPT_BTN.click()
        if start_date is not None:
            self.add_discount_form_step_1.START_DATE.fill(start_date)
            self.add_discount_form_step_1.PRIORITY.click()
        if end_date is not None:
            self.add_discount_form_step_1.END_DATE.fill(end_date)

        if priority == "1":
            self.add_discount_form_step_1.PRIORITY.to_contain_text(priority)
        else:
            self.add_discount_form_step_1.PRIORITY.fill(priority)
        self.add_discount_form_step_1.COMMENT.click()
        self.add_discount_form_step_1.NEXT_BTN.click()

        self.add_discount_form_step_2.PRODUCT_TABLE.select_by_value(product.product_name)
        self.add_discount_form_step_2.NEXT_BTN.click()

        self.add_discount_form_step_3.SUBSCRIBERS_TABLE.select_by_value(product.phone_number)
        self.add_discount_form_step_3.NEXT_BTN.click()

        self.add_discount_form_step_4.VALUE.fill(discount_amount)
        self.add_discount_form_step_4.SET_BTN.click()
