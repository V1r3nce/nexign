import allure
import pytest
from playwright.sync_api import Page

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from api.nbss.finances.billing_discount import BillingDiscountsRequests
from common.helpers.data_generator import generate_english_string
from common.helpers.time_helpers import delay, get_current_moscow_datetime
from models.context import test_context
from models.inquiry import prepare_inquiries
from models.user import IndividualClient
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
class TestViewBillingDiscount:
    @pytest.fixture(autouse=True)
    def setup(self, page: Page, nexign_ui_stand_login, api_request_context) -> None:
        self.client_profile = ClientProfilePage(nexign_ui_stand_login)
        self.client_request_api = ClientInquiriesRequests(api_request_context)
        self.discount_page = DiscountAndChargesPage(page)
        self.discount_requests_api = BillingDiscountsRequests(api_request_context)
        self.filter_form = FilterForm(page)
        self.start_date = get_current_moscow_datetime().strftime("%d.%m.%Y")
        self.end_date = "01.12.2999"
        self.discount_amount = "50"
        self.priority = "1"

    @allure.title("05. Применение фильтров для просмотра скидок")
    @allure.id(676533)
    def test_view_filter_billing_discount(self, create_individual_user: IndividualClient, base_url: str) -> None:
        self.client_request_api.product_sale()
        self.client_profile.open(
            f"{base_url}customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
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
            self.discount_page.locators.FILTER_BTN.click()
            self.filter_form.TYPE.select_by_value("Скидки")
            self.filter_form.SET_BTN.click()

        with allure.step("Проверяем, что скидка отображается"):
            self.discount_page.locators.DISCOUNTS.wait_to_have_count(1, timeout=10000)
            self.discount_page.locators.PROPERTIES.wait_to_have_count(6)
            self.discount_page.locators.PROPERTIES[0].wait_to_have_text(self.start_date)
            self.discount_page.locators.PROPERTIES[1].wait_to_have_text(self.end_date)
            self.discount_page.locators.PROPERTIES[2].wait_to_have_text(self.priority)
            self.discount_page.locators.PROPERTIES[3].wait_to_have_text("Admin")
            self.discount_page.locators.PROPERTIES[4].to_contain_text(self.start_date)
            self.discount_page.locators.PROPERTIES[5].wait_to_have_text("—")

        with allure.step("Применение фильтра по пользователю"):
            self.discount_page.locators.FILTER_BTN.click()
            self.filter_form.USER.fill(generate_english_string(10))
            delay(1, "Ожидаем прогрузку формы, иначе фильтр не применится")
            self.filter_form.SET_BTN.click()

        with allure.step("Проверяем, что скидка не отображается"):
            self.discount_page.locators.DISCOUNTS.wait_to_have_count(0)

    @allure.title("06. Сброс фильтров для просмотра скидок")
    @allure.id(676536)
    def test_clear_filter_billing_discount(self, create_individual_user: IndividualClient, base_url: str) -> None:
        inquiry = prepare_inquiries("internet")
        self.client_request_api.product_sale(inquiry=inquiry)
        self.client_profile.open(
            f"{base_url}customer-hierarchy-management/accounts/{test_context.agreements[0].accounts[0].id}/account"
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
            self.discount_page.locators.PROPERTIES.wait_to_have_count(6)
            self.discount_page.locators.PROPERTIES[0].wait_to_have_text(self.start_date)
            self.discount_page.locators.PROPERTIES[1].wait_to_have_text(self.end_date)
            self.discount_page.locators.PROPERTIES[2].wait_to_have_text(self.priority)
            self.discount_page.locators.PROPERTIES[3].wait_to_have_text("Admin")
            self.discount_page.locators.PROPERTIES[4].to_contain_text(self.start_date)
            self.discount_page.locators.PROPERTIES[5].wait_to_have_text("—")

    @allure.title("07. Просмотр продуктов, к которым применена скидка")
    @allure.id(676558)
    def test_billing_discount_products_view(self, create_individual_user: IndividualClient, base_url: str) -> None:
        self.client_request_api.product_sale()
        self.client_profile.open(
            f"{base_url}customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
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
            self.discount_page.locators.PROPERTIES[0].wait_to_have_text(self.start_date)
            self.discount_page.locators.PROPERTIES[1].wait_to_have_text(self.end_date)
            self.discount_page.locators.PROPERTIES[2].wait_to_have_text(self.priority)
            self.discount_page.locators.PROPERTIES[3].wait_to_have_text("Admin")
            self.discount_page.locators.PROPERTIES[4].to_contain_text(self.start_date)
            self.discount_page.locators.PROPERTIES[5].wait_to_have_text("—")

        with allure.step("Проверяем продукт, к которому применена скидка"):
            self.discount_page.locators.PRODUCTS_TAB.click()
            self.discount_page.locators.PRODUCTS.wait_to_have_count(1)
            self.discount_page.locators.PRODUCTS[0].wait_to_have_text(test_context.client.inquiry.product.product_name)

    @allure.title("12. Просмотр абонентов, к которым применена скидка")
    @allure.id(676636)
    def test_billing_discount_accounts_view(self, create_individual_user: IndividualClient, base_url: str) -> None:
        self.client_request_api.product_sale()
        self.client_profile.open(
            f"{base_url}customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
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
            self.discount_page.locators.DISCOUNTS.wait_to_have_count(1, timeout=10000)
            self.discount_page.locators.PROPERTIES[0].wait_to_have_text(self.start_date)
            self.discount_page.locators.PROPERTIES[1].wait_to_have_text(self.end_date)
            self.discount_page.locators.PROPERTIES[2].wait_to_have_text(self.priority)
            self.discount_page.locators.PROPERTIES[3].wait_to_have_text("Admin")
            self.discount_page.locators.PROPERTIES[4].to_contain_text(self.start_date)
            self.discount_page.locators.PROPERTIES[5].wait_to_have_text("—")

        with allure.step("Проверяем абонента, к которому применена скидка"):
            self.discount_page.locators.SUBSCRIBERS_TAB.click()
            self.discount_page.locators.SUBSCRIBERS.wait_to_have_count(1)
            self.discount_page.locators.SUBSCRIBERS[0].to_contain_text(str(test_context.client.inquiry.product.subs_id))

    @allure.title("16. Просмотр условий применимости")
    @allure.id(676640)
    def test_billing_discount_conditions_view(self, create_individual_user: IndividualClient, base_url: str) -> None:
        self.client_request_api.product_sale()
        self.client_profile.open(
            f"{base_url}customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
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
            self.discount_page.locators.DISCOUNTS.wait_to_have_count(1, timeout=10000)
            self.discount_page.locators.PROPERTIES[0].wait_to_have_text(self.start_date)
            self.discount_page.locators.PROPERTIES[1].wait_to_have_text(self.end_date)
            self.discount_page.locators.PROPERTIES[2].wait_to_have_text(self.priority)
            self.discount_page.locators.PROPERTIES[3].wait_to_have_text("Admin")
            self.discount_page.locators.PROPERTIES[4].to_contain_text(self.start_date)
            self.discount_page.locators.PROPERTIES[5].wait_to_have_text("—")

        with allure.step("Проверяем условия применимости"):
            self.discount_page.locators.CONDITIONS_TAB.click()
            self.discount_page.locators.DISCOUNT_VALUE.to_contain_text(self.discount_amount)
            self.discount_page.locators.THRESHOLD_AMOUNT.to_contain_text("100")
