import allure
import pytest
from playwright.sync_api import APIRequestContext, Page

from api.nbss.payments_requests import PaymentsRequests
from api.nbss.personal_account_requests import PersonalAccountRequests
from common.helpers.checker import assert_that
from common.helpers.string_helper import balance_parse, check_price
from models.user import IndividualClient, OrganizationClient
from pages.consumption_page import ConsumptionPage
from pages.inquiries_page import InquiriesPage
from pages.locators.inquiries_elements import ProductEditForm
from pages.locators.select_product_offers_form import SelectProductOffersForm
from pages.personal_account_page import PersonalAccountPage


@allure.epic('E2E_42 Подключение платных "красивых номеров"')
@allure.suite('E2E_42 Подключение платных "красивых номеров"')
@pytest.mark.usefixtures("nexign_ui_stand_login")
@pytest.mark.regress
class TestSellPaidBeautifulNumber:
    @pytest.fixture(autouse=True)
    def setup(self, page: Page, api_request_auth_context: APIRequestContext) -> None:
        self.personal_account_page = PersonalAccountPage(page)
        self.inquiries_page = InquiriesPage(page)
        self.product_offer = SelectProductOffersForm(page)
        self.edit_product_form = ProductEditForm(page)
        self.consumption_page = ConsumptionPage(page)
        self.payment_api = PaymentsRequests(api_request_auth_context)
        self.personal_account_api = PersonalAccountRequests(api_request_auth_context)
        self.beautiful_number_color = "Платиновый"
        self.beautiful_number_cost = 2000.0

    @allure.title('Подключение платного "красивого номера" (B2B, Продажа)')
    @allure.id(576238)
    def test_connect_beautiful_number_b2b(self, base_url: str, create_organization: OrganizationClient) -> None:
        client = create_organization
        self.personal_account_page.open(f"{base_url}customer-hierarchy-management/customers/{client.user_id}/overview")
        self.inquiries_page.sale_initialization(add_kp="no")

        self.inquiries_page.locators.ADD_SALE_BTN.click()
        self.product_offer.PRODUCT_TYPE.select_by_value("Монопродукт")
        self.product_offer.PRODUCT_CATEGORY.select_by_value("Мобильная связь")
        self.product_offer.SEARCH_BTN.click()
        self.product = self.inquiries_page.choose_product_offer_with_name("Гибкий бизнес")
        self.product_offer.ADD_BTN.click()
        check_price(self.inquiries_page.locators.ADDED_MONOPRODUCT_ONE_TIME_PAYMENT[0], self.product.one_time_payment)
        check_price(self.inquiries_page.locators.ADDED_MONOPRODUCT_SUBSCRIPTION_FEE[0], self.product.subscription_fee)

        self.inquiries_page.locators.ADDED_PRODUCT_EDIT_BTN.wait_elements_visible(element_index=0)
        self.inquiries_page.locators.ADDED_PRODUCT_EDIT_BTN[0].click(force=True)
        self.edit_product_form.RESOURCES_TAB.click()
        self.product.phone_number = self.inquiries_page.auto_reserve_phone_number_resources(self.beautiful_number_color)[
            1
        ]
        self.edit_product_form.SPECIFICATION_TAB.click()
        self.edit_product_form.NUMBER_COLOR.wait_to_have_text(self.beautiful_number_color)
        self.edit_product_form.INNER_ACCEPT_BTN.click()
        self.product.subscription_fee = self.beautiful_number_cost
        self.inquiries_page.locators.LOAD_SPIN_FIRST.not_to_be_visible()
        check_price(self.inquiries_page.locators.ADDED_MONOPRODUCT_ONE_TIME_PAYMENT[0], self.product.one_time_payment)
        check_price(self.inquiries_page.locators.ADDED_MONOPRODUCT_SUBSCRIPTION_FEE[0], self.product.subscription_fee)

        self.inquiries_page.check_configuration()
        self.inquiries_page.locators.NEXT_STEP_BTN.click()
        self.inquiries_page.wait_connect_package_offers_and_close_inquiry()

        with allure.step("Активация продукта для появления начислений"):
            balance = 100.00
            account_id = self.personal_account_api.get_personal_accounts("customer", client.user_id).json()["items"][0][
                "accountId"
            ]
            self.payment_api.create_default_payment(
                account_id, self.product.one_time_payment + self.product.subscription_fee + balance
            )
            self.personal_account_api.wait_check_current_main_balance(account_id, balance)
            self.personal_account_api.wait_accruals(client.user_id)

        self.inquiries_page.locators.PRODUCT_PROFILE_BTN.click()
        self.personal_account_page.locators.PRODUCT_LIMIT.wait_to_be_visible()
        self.personal_account_page.locators.PRODUCTS_DETAILS_OPEN_BTN.wait_to_be_visible()
        self.personal_account_page.locators.PRODUCTS_DETAILS_OPEN_BTN.click(force=True)
        self.personal_account_page.locators.PRODUCTS_DETAILS_BTN.wait_to_be_visible()
        self.personal_account_page.locators.PRODUCTS_DETAILS_BTN.click(force=True)
        self.consumption_page.locators.PAGE_TITLE.wait_to_have_text("Потребление")
        self.consumption_page.locators.SUBSCRIBER_NUM.wait_to_have_count(1)
        self.consumption_page.locators.SUBSCRIBER_NUM[0].wait_to_have_text(self.product.phone_number)
        self.consumption_page.click_tab("Начисления")
        self.consumption_page.locators.CLEAR_FILTER_BTN.click()
        self.consumption_page.locators.ACCRUAL_LIST.wait_to_have_count(2)
        sum_list = [balance_parse(sum.text) for sum in self.consumption_page.locators.ACCRUAL_SUM]
        assert_that(
            lambda: self.product.one_time_payment in sum_list,
            message="Сумма разового начисления не отображается в списке начислений",
        )
        assert_that(
            lambda: self.product.subscription_fee in sum_list,
            message="Сумма периодического начисления (АП) не отображается в списке начислений",
        )

    @allure.title('Подключение платного "красивого номера" (B2C, Продажа)')
    @allure.id(577147)
    def test_connect_beautiful_number_b2c(self, base_url: str, create_individual_user: IndividualClient) -> None:
        client = create_individual_user
        self.personal_account_page.open(f"{base_url}customer-hierarchy-management/customers/{client.user_id}/overview")
        self.inquiries_page.sale_initialization()

        self.inquiries_page.locators.ADD_SALE_BTN.click()
        self.product_offer.PRODUCT_TYPE.select_by_value("Монопродукт")
        self.product_offer.PRODUCT_CATEGORY.select_by_value("Мобильная связь")
        self.product_offer.SEARCH_BTN.click()
        self.product = self.inquiries_page.choose_product_offer_with_name("На связи")
        self.product_offer.ADD_BTN.click()
        check_price(self.inquiries_page.locators.ADDED_MONOPRODUCT_ONE_TIME_PAYMENT[0], self.product.one_time_payment)
        check_price(self.inquiries_page.locators.ADDED_MONOPRODUCT_SUBSCRIPTION_FEE[0], self.product.subscription_fee)

        self.inquiries_page.locators.ADDED_PRODUCT_EDIT_BTN.wait_elements_visible(element_index=0)
        self.inquiries_page.locators.ADDED_PRODUCT_EDIT_BTN[0].click(force=True)
        self.edit_product_form.RESOURCES_TAB.click()
        self.product.phone_number = self.inquiries_page.auto_reserve_phone_number_resources(self.beautiful_number_color)[
            1
        ]
        self.edit_product_form.SPECIFICATION_TAB.click()
        self.edit_product_form.NUMBER_COLOR.wait_to_have_text(self.beautiful_number_color)
        self.edit_product_form.INNER_ACCEPT_BTN.click()
        self.product.subscription_fee = self.beautiful_number_cost
        self.inquiries_page.locators.LOAD_SPIN_FIRST.not_to_be_visible()
        check_price(self.inquiries_page.locators.ADDED_MONOPRODUCT_ONE_TIME_PAYMENT[0], self.product.one_time_payment)
        check_price(self.inquiries_page.locators.ADDED_MONOPRODUCT_SUBSCRIPTION_FEE[0], self.product.subscription_fee)

        self.inquiries_page.check_configuration()
        self.inquiries_page.locators.NEXT_STEP_BTN.click()
        self.inquiries_page.wait_connect_package_offers_and_close_inquiry()

        with allure.step("Активация продукта для появления начислений"):
            balance = 100.00
            account_id = self.personal_account_api.get_personal_accounts("customer", client.user_id).json()["items"][0][
                "accountId"
            ]
            self.payment_api.create_default_payment(
                account_id, self.product.one_time_payment + self.product.subscription_fee + balance
            )
            self.personal_account_api.wait_check_current_main_balance(account_id, balance)
            self.personal_account_api.wait_accruals(client.user_id)

        self.inquiries_page.locators.PRODUCT_PROFILE_BTN.click()
        self.personal_account_page.locators.PRODUCT_LIMIT.wait_to_be_visible()
        self.personal_account_page.locators.PRODUCTS_DETAILS_OPEN_BTN.wait_to_be_visible()
        self.personal_account_page.locators.PRODUCTS_DETAILS_OPEN_BTN.click(force=True)
        self.personal_account_page.locators.PRODUCTS_DETAILS_BTN.wait_to_be_visible()
        self.personal_account_page.locators.PRODUCTS_DETAILS_BTN.click(force=True)
        self.consumption_page.locators.PAGE_TITLE.wait_to_have_text("Потребление")
        self.consumption_page.locators.SUBSCRIBER_NUM.wait_to_have_count(1)
        self.consumption_page.locators.SUBSCRIBER_NUM[0].wait_to_have_text(self.product.phone_number)
        self.consumption_page.click_tab("Начисления")
        self.consumption_page.locators.CLEAR_FILTER_BTN.click()
        self.consumption_page.locators.ACCRUAL_LIST.wait_to_have_count(1)
        check_price(self.consumption_page.locators.ACCRUAL_SUM[0], self.product.subscription_fee)
        self.consumption_page.locators.ACCRUAL_TYPE[0].wait_to_have_text("Периодическое начисление (АП)")
