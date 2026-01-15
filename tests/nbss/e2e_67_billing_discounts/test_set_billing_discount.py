from datetime import timedelta

import allure
import pytest

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from api.nbss.finances.billing_discount import BillingDiscountsRequests
from common.helpers.time_helpers import get_current_moscow_datetime
from models.client import IndividualClient
from models.context import test_context
from pages.locators.nbss.finances.discount_and_charges import (
    AddBillingDiscountFormStep4,
    AddBillingDiscountOrChargeForm,
    AddBillingDiscountOrChargeFormStep3,
    AddProductOfferForm,
    TemplateForm,
)
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.finances.discount_and_charges import DiscountAndChargesPage


@allure.link(
    url="confluence.nexign.com/pages/viewpage.action?pageId=659783906", name="8.6. Управление биллинговыми скидками"
)
@allure.epic("E2E_67 Управление биллинговыми скидками")
@allure.suite("E2E_67 Управление биллинговыми скидками")
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestSetBillingDiscount:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login) -> None:
        self.client_profile = ClientProfilePage()
        self.client_request_api = ClientInquiriesRequests()
        self.discount_page = DiscountAndChargesPage()
        self.add_discount_form_step_1 = AddBillingDiscountOrChargeForm()
        self.template_form = TemplateForm()
        self.add_discount_form_step_2 = AddProductOfferForm()
        self.add_discount_form_step_3 = AddBillingDiscountOrChargeFormStep3()
        self.add_discount_form_step_4 = AddBillingDiscountFormStep4()
        self.discount_requests_api = BillingDiscountsRequests()
        self.start_dt = get_current_moscow_datetime()
        self.start_date = self.start_dt.strftime("%d.%m.%Y")
        self.end_date = (self.start_dt + timedelta(days=30)).strftime("%d.%m.%Y")

    @allure.title("01. Назначение биллинговой скидки")
    @allure.id(599270)
    def test_set_billing_discount(self, create_individual_user: IndividualClient, base_url: str) -> None:
        discount_amount = "50"
        priority = "1"
        inquiry = self.client_request_api.product_sale()
        with allure.step("Открываем страницу скидок и доначислений"):
            self.client_profile.open(
                f"{base_url}customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
            )
            self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Скидки/доначисления")
            self.discount_page.locators.SELECTED_TAB_TITLE.wait_to_have_text("Скидки/доначисления")

        with allure.step("Создаем скидку"):
            self.discount_page.locators.SET_BTN.click()
            self.add_discount_form_step_1.TYPE.select_by_value("Скидка")
            self.add_discount_form_step_1.COMMENT.click()
            self.add_discount_form_step_1.START_DATE.fill(self.start_date)
            self.add_discount_form_step_1.TEMPLATE.click()

            self.template_form.TEMPLATE_TABLE.select_by_value("Скидка по умолчанию")
            self.template_form.INNER_ACCEPT_BTN.click()

            self.add_discount_form_step_1.PRIORITY.to_contain_text(priority)
            self.add_discount_form_step_1.NEXT_BTN.click()

            self.add_discount_form_step_2.PRODUCT_TABLE.select_by_value("На связи")
            self.add_discount_form_step_2.NEXT_BTN.click()

            self.add_discount_form_step_3.SUBSCRIBERS_TABLE.select_by_value(inquiry.product.phone_number)
            self.add_discount_form_step_3.NEXT_BTN.click()

            self.add_discount_form_step_4.VALUE.fill(discount_amount)
            self.add_discount_form_step_4.SET_BTN.click()

        with allure.step("Проверяем, что скидка создана"):
            self.discount_page.locators.DISCOUNTS.wait_to_have_count(1)
            self.discount_page.locators.PROPERTIES.wait_to_have_count(6)
            self.discount_page.locators.PROPERTIES[0].wait_to_have_text(self.start_date)
            self.discount_page.locators.PROPERTIES[1].wait_to_have_text(self.end_date)
            self.discount_page.locators.PROPERTIES[2].wait_to_have_text(priority)
            self.discount_page.locators.PROPERTIES[3].wait_to_have_text("Admin")
            self.discount_page.locators.PROPERTIES[4].to_contain_text(self.start_date)
            self.discount_page.locators.PROPERTIES[5].wait_to_have_text("—")

    @allure.title("02. Назначение биллинговой скидки с тем же идентификатором")
    @allure.id(676406)
    def test_set_billing_discount_same_id(self, create_individual_user: IndividualClient, base_url: str) -> None:
        discount_amount = "50"
        priority = "1"

        inquiry = self.client_request_api.product_sale()
        self.client_profile.open(
            f"{base_url}customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
        )
        self.discount_requests_api.add_billing_discount(
            amount=int(discount_amount),
            product=inquiry.product,
            action_type="Скидка",
            priority=int(priority),
        )

        self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Скидки/доначисления")
        self.discount_page.locators.SELECTED_TAB_TITLE.wait_to_have_text("Скидки/доначисления")
        self.discount_page.refresh_page(wait="domcontentloaded")

        self.discount_page.locators.DISCOUNTS.wait_to_have_count(1, timeout=15000)
        self.discount_page.locators.PROPERTIES[2].wait_to_have_text(priority)

        with allure.step("Создаем скидку"):
            self.discount_page.locators.SET_BTN.click()
            self.add_discount_form_step_1.TYPE.select_by_value("Скидка")
            self.add_discount_form_step_1.COMMENT.click()
            self.add_discount_form_step_1.TEMPLATE.click()

            self.template_form.TEMPLATE_TABLE.select_by_value("Скидка по умолчанию")
            self.template_form.INNER_ACCEPT_BTN.click()

            self.add_discount_form_step_1.PRIORITY.to_contain_text(priority)
            self.add_discount_form_step_1.NEXT_BTN.click()

            self.add_discount_form_step_2.PRODUCT_TABLE.select_by_value("На связи")
            self.add_discount_form_step_2.NEXT_BTN.click()

            self.add_discount_form_step_3.SUBSCRIBERS_TABLE.select_by_value(inquiry.product.phone_number)
            self.add_discount_form_step_3.NEXT_BTN.click()

            self.add_discount_form_step_4.VALUE.fill(discount_amount)
            self.add_discount_form_step_4.SET_BTN.click()
        name_error = self.discount_page.locators.MODAL_BODY_TEXT.text
        assert "Скидка с приоритетом = 1 уже существует" in name_error, (
            f"Ожидался текст 'Скидка с приоритетом = 1 уже существует', получен {name_error}"
        )

    @allure.title("03. Редактирование биллинговой скидки")
    @allure.id(676405)
    def test_edit_billing_discount(self, create_individual_user: IndividualClient, base_url: str) -> None:
        discount_amount = "50"
        priority = "1"

        inquiry = self.client_request_api.product_sale()
        self.client_profile.open(
            f"{base_url}customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
        )
        self.discount_requests_api.add_billing_discount(
            amount=int(discount_amount),
            product=inquiry.product,
            action_type="Скидка",
            priority=int(priority),
        )

        self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Скидки/доначисления")
        self.discount_page.locators.SELECTED_TAB_TITLE.wait_to_have_text("Скидки/доначисления")
        self.discount_page.refresh_page(wait="domcontentloaded")

        with allure.step("Проверяем, что скидка создана"):
            self.discount_page.locators.DISCOUNTS.wait_to_have_count(1, timeout=15000)
            self.discount_page.locators.PROPERTIES[0].wait_to_have_text(self.start_date)
            self.discount_page.locators.PROPERTIES[1].wait_to_have_text(self.end_date)
            self.discount_page.locators.PROPERTIES[2].wait_to_have_text(priority)
            self.discount_page.locators.PROPERTIES[3].wait_to_have_text("Admin")
            self.discount_page.locators.PROPERTIES[4].to_contain_text(self.start_date)
            self.discount_page.locators.PROPERTIES[5].wait_to_have_text("—")

        with allure.step("Редактируем скидку"):
            self.discount_page.locators.DISCOUNT_EDIT_BTN.click()
            self.add_discount_form_step_1.COMMENT.fill("test")
            self.add_discount_form_step_1.INNER_ACCEPT_BTN.click()

        with allure.step("Проверяем, что скидка отредактирована"):
            self.discount_page.locators.DISCOUNTS.wait_to_have_count(1)
            self.discount_page.locators.PROPERTIES.wait_to_have_count(6)
            self.discount_page.locators.PROPERTIES[0].wait_to_have_text(self.start_date)
            self.discount_page.locators.PROPERTIES[1].wait_to_have_text(self.end_date)
            self.discount_page.locators.PROPERTIES[2].wait_to_have_text(priority)
            self.discount_page.locators.PROPERTIES[3].wait_to_have_text("Admin")
            self.discount_page.locators.PROPERTIES[4].to_contain_text(self.start_date)
            self.discount_page.locators.PROPERTIES[5].wait_to_have_text("test")
