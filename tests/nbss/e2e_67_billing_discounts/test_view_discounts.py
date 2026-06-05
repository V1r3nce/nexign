from datetime import timedelta

import allure
import pytest

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from api.nbss.finances.billing_discount import BillingDiscountsRequests
from common.helpers.data_generator import generate_english_string
from common.helpers.env_helper import BASE_URL
from common.helpers.time_helpers import delay, get_current_moscow_datetime
from models.context import test_context
from models.inquiry import prepare_inquiries
from pages.locators.nbss.finances.discount_and_charges import (
    FilterForm,
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
class TestViewBillingDiscount:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login, create_organization) -> None:
        self.client_profile = ClientProfilePage()
        self.client_request_api = ClientInquiriesRequests()
        self.discount_page = DiscountAndChargesPage()
        self.discount_requests_api = BillingDiscountsRequests()
        self.filter_form = FilterForm()
        self.start_dt = get_current_moscow_datetime()
        self.start_date = self.start_dt.strftime("%d.%m.%Y")
        self.end_date = (self.start_dt + timedelta(days=30)).strftime("%d.%m.%Y")
        self.discount_amount = "50"
        self.priority = "1"

    @allure.title("05. Применение фильтров для просмотра скидок")
    @allure.id(676533)
    def test_view_filter_billing_discount(self) -> None:
        self.client_request_api.product_sale()
        self.client_profile.open(
            f"{BASE_URL}customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
        )
        self.discount_requests_api.add_billing_discount(
            amount=int(self.discount_amount),
            action_type="Скидка",
            priority=int(self.priority),
        )

        self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Скидки/доначисления")
        self.discount_page.locators.SELECTED_TAB_TITLE.wait_to_have_text("Скидки/доначисления")
        self.discount_page.refresh_page(wait="domcontentloaded")

        with allure.step("Применение фильтра по типу скидки"):
            self.discount_page.locators.FILTER_BTN.wait_to_be_enabled(timeout=15000)
            self.discount_page.locators.FILTER_BTN.click()
            self.filter_form.TYPE.select_by_value("Скидки")
            self.filter_form.SET_BTN.click()

        with allure.step("Проверяем, что скидка отображается"):
            self.discount_page.locators.DISCOUNTS.wait_to_have_count(1, timeout=10000)
            self.discount_page.check_properties(start_date=self.start_date, end_date=self.end_date)

        with allure.step("Применение фильтра по пользователю"):
            self.discount_page.locators.FILTER_BTN.click()
            self.filter_form.USER.fill(generate_english_string(10))
            delay(1, "Ожидаем прогрузку формы, иначе фильтр не применится")
            self.filter_form.SET_BTN.click()

        with allure.step("Проверяем, что скидка не отображается"):
            self.discount_page.locators.DISCOUNTS.wait_to_have_count(0)

    @allure.title("06. Сброс фильтров для просмотра скидок")
    @allure.id(676536)
    def test_clear_filter_billing_discount(self) -> None:
        self.client_request_api.product_sale(inquiry=prepare_inquiries("internet"))
        self.client_profile.open(
            f"{BASE_URL}customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
        )
        self.discount_requests_api.add_billing_discount(
            amount=int(self.discount_amount),
            action_type="Скидка",
            priority=int(self.priority),
        )

        self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Скидки/доначисления")
        self.discount_page.locators.SELECTED_TAB_TITLE.wait_to_have_text("Скидки/доначисления")
        self.discount_page.refresh_page(wait="domcontentloaded")

        with allure.step("Применение фильтра по пользователю"):
            self.discount_page.locators.FILTER_BTN.click()
            self.filter_form.TYPE.select_by_value("Доначисления")
            self.filter_form.SET_BTN.click()

        with allure.step("Проверяем, что скидка не отображается"):
            self.discount_page.locators.DISCOUNTS.wait_to_have_count(0)

        self.discount_page.locators.MORE_BTN.select_by_value("Сбросить")

        with allure.step("Проверяем, что скидка отображается"):
            self.discount_page.locators.DISCOUNTS.wait_to_have_count(1, timeout=10000)
            self.discount_page.check_properties(start_date=self.start_date, end_date=self.end_date)

    @allure.title("07. Просмотр продуктов, к которым применена скидка")
    @allure.id(676558)
    def test_billing_discount_products_view(self) -> None:
        self.client_request_api.product_sale()
        self.client_profile.open(
            f"{BASE_URL}customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
        )
        self.discount_requests_api.add_billing_discount(
            amount=int(self.discount_amount),
            action_type="Доначисление",
            template_name="До фиксированной суммы",
            priority=int(self.priority),
        )

        self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Скидки/доначисления")
        self.discount_page.locators.SELECTED_TAB_TITLE.wait_to_have_text("Скидки/доначисления")
        self.discount_page.refresh_page(wait="domcontentloaded")

        with allure.step("Проверяем, что скидка создана"):
            self.discount_page.locators.DISCOUNTS.wait_to_have_count(1, timeout=10000)
            self.discount_page.check_properties(start_date=self.start_date, end_date=self.end_date)

        with allure.step("Проверяем продукт, к которому применена скидка"):
            self.discount_page.locators.PRODUCTS_TAB.click()
            self.discount_page.locators.PRODUCTS.wait_to_have_count(1)
            self.discount_page.locators.PRODUCTS[0].wait_to_have_text(test_context.client.inquiry.product.product_name)

    @allure.title("12. Просмотр абонентов, к которым применена скидка")
    @allure.id(676636)
    def test_billing_discount_accounts_view(self) -> None:
        self.client_request_api.product_sale()
        self.client_profile.open(
            f"{BASE_URL}customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
        )
        self.discount_requests_api.add_billing_discount(
            amount=int(self.discount_amount),
            action_type="Скидка",
            priority=int(self.priority),
        )

        self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Скидки/доначисления")
        self.discount_page.locators.SELECTED_TAB_TITLE.wait_to_have_text("Скидки/доначисления")
        self.discount_page.refresh_page(wait="domcontentloaded")

        with allure.step("Проверяем, что скидка создана"):
            self.discount_page.locators.DISCOUNTS.wait_to_have_count(1, timeout=15000)
            self.discount_page.check_properties(start_date=self.start_date, end_date=self.end_date)

        with allure.step("Проверяем абонента, к которому применена скидка"):
            self.discount_page.locators.SUBSCRIBERS_TAB.click()
            self.discount_page.locators.SUBSCRIBERS.wait_to_have_count(1)
            self.discount_page.locators.SUBSCRIBERS[0].to_contain_text(test_context.client.inquiry.product.phone_number)

    @allure.title("16. Просмотр условий применимости")
    @allure.id(676640)
    def test_billing_discount_conditions_view(self) -> None:
        self.client_request_api.product_sale()
        self.client_profile.open(
            f"{BASE_URL}customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
        )
        self.discount_requests_api.add_billing_discount(
            amount=int(self.discount_amount), action_type="Скидка", priority=int(self.priority), discount_threshold=100
        )

        self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Скидки/доначисления")
        self.discount_page.locators.SELECTED_TAB_TITLE.wait_to_have_text("Скидки/доначисления")
        self.discount_page.refresh_page(wait="domcontentloaded")

        with allure.step("Проверяем, что скидка создана"):
            self.discount_page.locators.DISCOUNTS.wait_to_have_count(1, timeout=10000)
            self.discount_page.check_properties(start_date=self.start_date, end_date=self.end_date)

        with allure.step("Проверяем условия применимости"):
            self.discount_page.check_conditions_of_applicability(discount_amount=self.discount_amount, threshold="100")
