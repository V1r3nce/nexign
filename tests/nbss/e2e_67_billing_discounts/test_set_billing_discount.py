from datetime import timedelta

import allure
import pytest

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from api.nbss.finances.billing_discount import BillingDiscountsRequests
from common.enums.discount import DiscountErrors
from common.helpers.env_helper import BASE_URL
from common.helpers.time_helpers import get_current_moscow_datetime
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
    def setup(self, nexign_stand_login, create_organization) -> None:
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
        self.client_request_api.product_sale()

    @allure.title("01. Назначение биллинговой скидки")
    @allure.id(599270)
    def test_set_billing_discount(self) -> None:
        discount_amount = "50"
        with allure.step("Открываем страницу скидок и доначислений"):
            self.client_profile.open(
                f"{BASE_URL}customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
            )
            self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Скидки/доначисления")
            self.discount_page.locators.SELECTED_TAB_TITLE.wait_to_have_text("Скидки/доначисления")

        self.discount_page.create_billing_discount(
            start_date=self.start_date, end_date=self.end_date, discount_amount=discount_amount
        )

        with allure.step("Проверяем, что скидка создана"):
            self.discount_page.locators.DISCOUNTS.wait_to_have_count(1, timeout=15000)
            self.discount_page.check_properties(start_date=self.start_date, end_date=self.end_date)

    @allure.title("02. Назначение биллинговой скидки с тем же идентификатором")
    @allure.id(676406)
    def test_set_billing_discount_same_id(self) -> None:
        discount_amount = "50"
        priority = "1"

        self.client_profile.open(
            f"{BASE_URL}customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
        )
        self.discount_requests_api.add_billing_discount(
            amount=int(discount_amount),
            product=test_context.client.inquiry.product,
            action_type="Скидка",
            priority=int(priority),
        )

        self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Скидки/доначисления")
        self.discount_page.locators.SELECTED_TAB_TITLE.wait_to_have_text("Скидки/доначисления")
        self.discount_page.refresh_page(wait="domcontentloaded")

        self.discount_page.locators.DISCOUNTS.wait_to_have_count(1, timeout=15000)
        self.discount_page.check_properties(start_date=self.start_date, end_date=self.end_date)

        self.discount_page.create_billing_discount(
            start_date=self.start_date, end_date=self.end_date, discount_amount=discount_amount
        )
        name_error = self.discount_page.locators.MODAL_BODY_TEXT.text
        assert "Скидка с приоритетом = 1 уже существует" in name_error, (
            f"Ожидался текст 'Скидка с приоритетом = 1 уже существует', получен {name_error}"
        )

    @allure.title("03. Редактирование биллинговой скидки")
    @allure.id(676405)
    def test_edit_billing_discount(self) -> None:
        discount_amount = "50"
        priority = "1"

        self.client_profile.open(
            f"{BASE_URL}customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
        )
        self.discount_requests_api.add_billing_discount(
            amount=int(discount_amount),
            product=test_context.client.inquiry.product,
            action_type="Скидка",
            priority=int(priority),
        )

        self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Скидки/доначисления")
        self.discount_page.locators.SELECTED_TAB_TITLE.wait_to_have_text("Скидки/доначисления")
        self.discount_page.refresh_page(wait="domcontentloaded")

        with allure.step("Проверяем, что скидка создана"):
            self.discount_page.locators.DISCOUNTS.wait_to_have_count(1, timeout=15000)
            self.discount_page.check_properties(start_date=self.start_date, end_date=self.end_date)

        with allure.step("Редактируем скидку"):
            self.discount_page.locators.DISCOUNT_EDIT_BTN.click()
            self.add_discount_form_step_1.COMMENT.fill("test")
            self.add_discount_form_step_1.INNER_ACCEPT_BTN.click()

        with allure.step("Проверяем, что скидка отредактирована"):
            self.discount_page.locators.DISCOUNTS.wait_to_have_count(1)
            self.discount_page.check_properties(start_date=self.start_date, end_date=self.end_date, note="test")

    @allure.title("18. Проверка вводимых значений")
    @allure.id(839778)
    def test_check_value_set(self) -> None:
        error_message = DiscountErrors.IncorrectDiscountPercentValue
        self.client_profile.open(
            f"{BASE_URL}customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
        )

        self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Скидки/доначисления")
        self.discount_page.locators.SELECTED_TAB_TITLE.wait_to_have_text("Скидки/доначисления")
        self.discount_page.refresh_page(wait="domcontentloaded")

        self.discount_page.locators.SET_BTN.wait_to_be_visible()
        self.discount_page.locators.SET_BTN.click()
        self.discount_page.fill_billing_discount(
            start_date=self.start_date, end_date=self.end_date, discount_amount="-100"
        )
        self.add_discount_form_step_4.VALUE.to_contain_value("100")
        self.discount_page.locators.DISCOUNTS.wait_not_to_be_visible(timeout=10000)

        with allure.step("Проверка ввода значения превышающего 100"):
            self.add_discount_form_step_4.SET_BTN.wait_to_be_enabled()
            self.add_discount_form_step_4.VALUE.wait_to_be_visible()
            self.add_discount_form_step_4.VALUE.type(str(150))
            self.add_discount_form_step_4.INFO.wait_to_have_text(error_message)
            self.add_discount_form_step_4.SET_BTN.click()
            self.discount_page.locators.DISCOUNTS.wait_not_to_be_visible(timeout=10000)

        with allure.step("Проверка буквенного значения"):
            self.add_discount_form_step_4.SET_BTN.wait_to_be_enabled()
            self.add_discount_form_step_4.VALUE.wait_to_be_visible()
            self.add_discount_form_step_4.VALUE.fill("abc")
            self.add_discount_form_step_4.SET_BTN.click()

        with allure.step("Проверка созданной скидки"):
            self.discount_page.locators.DISCOUNTS.wait_to_have_count(0, timeout=20000)
