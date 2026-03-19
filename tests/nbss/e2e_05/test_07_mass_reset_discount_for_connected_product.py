import allure
import pytest

from api.nbss.finances.payments_requests import PaymentsRequests
from api.nbss.personal_account_requests import PersonalAccountRequests
from common.helpers.env_helper import BASE_URL
from common.helpers.string_helper import get_price_and_currency
from models.client import OrganizationClient
from models.context import test_context
from models.inquiry import prepare_inquiries
from pages.base_page import BasePage
from pages.locators.nbss.dynamic_form_elements import CreateSalesAndServiceManagement
from pages.locators.nbss.inquiries_elements import ProductEditForm
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.inquiries_page import InquiriesPage


@pytest.mark.regress
@pytest.mark.nbss_portal
@allure.epic("E2E_05 Управление атрибутами продукта/сервиса/ресурса абонента (Индивидуализация цены)")
@allure.suite("E2E_05 Управление атрибутами продукта/сервиса/ресурса абонента (Индивидуализация цены)")
class TestSaleProductWithPriceIndividualization:
    @pytest.fixture(autouse=True)
    def setup(
        self,
        nexign_stand_login,
        create_organization_with_agreement_and_account: OrganizationClient,
    ) -> None:
        self.base_page = BasePage()
        self.client = create_organization_with_agreement_and_account
        self.inquiries_page = InquiriesPage()
        self.client_profile = ClientProfilePage()
        self.product_edit_form = ProductEditForm()
        self.payment_api = PaymentsRequests()
        self.personal_account_api = PersonalAccountRequests()

    @allure.title("07. Массовый сброс скидки у подключенного продукта")
    @allure.id(652744)
    @allure.description(
        """
        Проверить возможность массового сброса скидки у подключенного продукта.
        """
    )
    def test_sale_product_with_individual_subscription_price(self) -> None:
        subscription_discount_percent = 20

        with allure.step("Подготовка: Открытие профиля клиента и создание заявки на продажу"):
            self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{self.client.user_id}/overview")
            self.inquiries_page.sale_initialization(
                self.client,
                need_contact_data=True,
                agreement=self.client.agreements[0].number,
                account=self.client.agreements[0].accounts[0].number,
                priority="Высокий",
                add_kp="no",
                create_add_agreement="auto",
            )

        with allure.step("Подготовка: Добавление продукта, бронирование ресурсов и проверка конфигурации"):
            test_context.client.inquiry_list = prepare_inquiries(category="satellite_rent")
            self.inquiries_page.add_product_offer_to_commercial_order(test_context.client.inquiry.product)

            product = test_context.client.inquiry.product
            product.switch_name = "Коммутатор_Спутниковая_связь"

            original_subscription_fee = product.subscription_fee

            self.inquiries_page.auto_reserve_all_resources(test_context.client.inquiry.product.category)
            self.inquiries_page.check_configuration()

        with allure.step("Шаг 1: Применение скидки и завершение первой продажи"):
            self.inquiries_page.locators.LOAD_SPIN_THIRD.not_to_be_visible()
            self.inquiries_page.locators.ADDED_PRODUCT_SUBSCRIPTION_FEE_BUTTON[0].wait_to_be_visible(timeout=10000)
            self.inquiries_page.locators.ADDED_PRODUCT_SUBSCRIPTION_FEE_BUTTON[0].click(force=True)
            self.product_edit_form.PRICE_TAB.wait_to_be_visible(timeout=10000)

            self.product_edit_form.SUBSCRIPTION_FEE_DISCOUNT_INPUT.wait_to_be_visible(timeout=5000)
            self.product_edit_form.SUBSCRIPTION_FEE_DISCOUNT_INPUT.type(str(subscription_discount_percent))
            self.product_edit_form.INNER_ACCEPT_BTN.wait_to_be_visible(timeout=5000)
            self.product_edit_form.INNER_ACCEPT_BTN.click()

            self.inquiries_page.locators.LOAD_SPIN_THIRD.not_to_be_visible(timeout=30000)
            self.product_edit_form.TITLE.not_to_be_visible(timeout=10000)

            expected_subscription = original_subscription_fee * (1 - subscription_discount_percent / 100)
            self.inquiries_page.check_individualized_price_in_inquiry(
                expected_subscription, original_subscription_fee, fee_type="subscription"
            )

            self.inquiries_page.locators.ADDED_PRODUCT_EDIT_BTN[0].wait_to_be_visible(timeout=10000)
            self.inquiries_page.locators.ADDED_PRODUCT_EDIT_BTN[0].click(force=True)
            self.product_edit_form.PRICE_TAB.wait_to_be_visible(timeout=10000)
            self.product_edit_form.PRICE_TAB.click()

            self.inquiries_page.check_individualized_price_in_inquiry(
                expected_subscription, original_subscription_fee, fee_type="subscription"
            )

            self.product_edit_form.CANCEL_BUTTON.wait_to_be_visible(timeout=5000)
            self.product_edit_form.CANCEL_BUTTON.click()
            self.product_edit_form.TITLE.not_to_be_visible(timeout=10000)

            self.inquiries_page.locators.LOAD_SPIN_THIRD.not_to_be_visible(timeout=30000)
            self.inquiries_page.locators.CHECK_CONFIGURATION_BTN.wait_to_be_visible(timeout=10000)
            self.inquiries_page.check_configuration()

            self.inquiries_page.locators.NEXT_STEP_BTN.click()
            self.inquiries_page.wait_connect_package_offers_and_close_inquiry(
                auto_create_agreement=False, generate_documents=False
            )

        with allure.step("Шаг 2: Пополнение счета и проверка индивидуализированной цены на странице продуктов"):
            payment_amount = expected_subscription * 1.2
            account_id = self.client.agreements[0].accounts[0].id
            self.payment_api.create_default_payment(account_id, payment_amount)
            self.personal_account_api.wait_check_current_main_balance(account_id, payment_amount)
            self.personal_account_api.wait_accruals(test_context.client.user_id)

            self.base_page.open(
                f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/products"
            )
            self.client_profile.locators.PRODUCTS_LIST.wait_to_be_visible(timeout=15000)
            self.client_profile.locators.PRODUCTS.wait_to_have_count(1, timeout=10000)

            self.client_profile.check_individualized_subscription_fee_on_products_page(
                expected_subscription, original_subscription_fee
            )

        with allure.step("Шаг 3: Редактирование продажи и сброс скидки"):
            self.inquiries_page.locators.ADDED_PRODUCT_SUBSCRIPTION_FEE_MORE_VERT_BTN[0].wait_to_be_visible(
                timeout=10000
            )
            self.inquiries_page.locators.ADDED_PRODUCT_SUBSCRIPTION_FEE_MORE_VERT_BTN[0].click(force=True)
            self.inquiries_page.locators.EDIT_MENU_ITEM.wait_to_be_visible(timeout=10000)
            self.inquiries_page.locators.EDIT_MENU_ITEM.click()

            create_sales_form = CreateSalesAndServiceManagement()
            create_sales_form.SAVE_BTN.wait_to_be_visible(timeout=10000)
            create_sales_form.SAVE_BTN.click()
            create_sales_form.SAVE_BTN.not_to_be_visible(timeout=10000)

            self.inquiries_page.locators.LOAD_SPIN_THIRD.not_to_be_visible(timeout=30000)
            self.inquiries_page.locators.LOAD_SPINS.not_to_be_visible(timeout=30000)
            self.inquiries_page.locators.ADDED_PRODUCT.wait_to_be_visible(timeout=30000)

            self.product_edit_form.RESET_DISCOUNT_BTN.wait_to_be_visible(timeout=10000)
            self.product_edit_form.RESET_DISCOUNT_BTN.click()

            self.product_edit_form.RESET_DISCOUNT_CONFIRM_BTN.wait_to_be_visible(timeout=10000)
            self.product_edit_form.RESET_DISCOUNT_CONFIRM_BTN.click()
            self.product_edit_form.RESET_DISCOUNT_CONFIRM_BTN.not_to_be_visible(timeout=10000)

            self.inquiries_page.locators.LOAD_SPIN_THIRD.not_to_be_visible(timeout=30000)
            self.inquiries_page.locators.LOAD_SPINS.not_to_be_visible(timeout=30000)
            self.inquiries_page.locators.ADDED_PRODUCT.wait_to_be_visible(timeout=30000)

        with allure.step("Шаг 4: Проверка конфигурации и завершение продажи после сброса скидки"):
            self.inquiries_page.check_configuration()

            self.inquiries_page.locators.NEXT_STEP_BTN.wait_to_be_visible(timeout=10000)
            self.inquiries_page.locators.NEXT_STEP_BTN.click()

            self.inquiries_page.wait_connect_package_offers_and_close_inquiry(
                auto_create_agreement=False, generate_documents=False
            )

        with allure.step("Шаг 5: Переход в продукты клиента и проверка исходной цены без индивидуализации"):
            self.base_page.open(
                f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/products"
            )
            self.client_profile.locators.PRODUCTS_LIST.wait_to_be_visible(timeout=15000)
            self.client_profile.locators.PRODUCTS.wait_to_have_count(1, timeout=30000)
            self.client_profile.locators.PRODUCTS_SUBSCRIPTION_FEE.wait_elements_visible(0, timeout=10000)

            subscription_fee_text = self.client_profile.locators.PRODUCTS_SUBSCRIPTION_FEE[0].text
            subscription_fee_price, _ = get_price_and_currency(subscription_fee_text)

            assert abs(subscription_fee_price - original_subscription_fee) < 0.01, (
                f"Ожидалась базовая цена {original_subscription_fee:.2f}, но отображается {subscription_fee_price:.2f}"
            )
