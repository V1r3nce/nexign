import allure
import pytest
from playwright.sync_api import Page

from common.helpers.env_helper import BASE_URL
from models.client import OrganizationClient
from models.context import test_context
from models.inquiry import prepare_inquiries
from pages.base_page import BasePage
from pages.locators.nbss.inquiries_elements import ProductEditForm
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.inquiries_page import InquiriesPage


@pytest.mark.regress
@pytest.mark.nbss_portal
@allure.epic("E2E_05 Управление атрибутами продукта/сервиса/ресурса абонента (Индивидуализация цены)")
@allure.suite("E2E_05 Управление атрибутами продукта/сервиса/ресурса абонента (Индивидуализация цены)")
class TestSaleProductWithOneTimePaymentIndividualization:
    @pytest.fixture(autouse=True)
    def setup(
        self,
        page: Page,
        nexign_stand_login,
        create_organization_with_agreement_and_account: OrganizationClient,
    ) -> None:
        self.base_page = BasePage()
        self.page = page
        self.client = create_organization_with_agreement_and_account
        self.inquiries_page = InquiriesPage()
        self.client_profile = ClientProfilePage()
        self.product_edit_form = ProductEditForm()

    @allure.title("03. Продажа продуктового предложения с индивидуализацией стоимости разовой платы")
    @allure.id(660624)
    @allure.description(
        """
        Проверить возможность продажи продуктового предложения
        с индивидуализацией стоимости разовой платы.
        """
    )
    def test_sale_product_with_individual_one_time_payment(self) -> None:
        one_time_discount_percent = 20

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
            test_context.client.inquiry_list = prepare_inquiries(category="equipment_sale", product_offering_id=500070)
            self.inquiries_page.add_product_offer_to_commercial_order(test_context.client.inquiry.product)

            product = test_context.client.inquiry.product
            original_one_time_payment = product.one_time_payment

            self.inquiries_page.auto_reserve_all_resources(test_context.client.inquiry.product.category)
            self.inquiries_page.check_configuration()

        with allure.step("Шаг 1: Открытие формы редактирования цены разовой платы"):
            self.inquiries_page.locators.LOAD_SPIN_THIRD.not_to_be_visible()
            self.inquiries_page.locators.ADDED_PRODUCT_ONE_TIME_PAYMENT_BUTTON[0].wait_to_be_visible(timeout=10000)
            self.inquiries_page.locators.ADDED_PRODUCT_ONE_TIME_PAYMENT_BUTTON[0].click(force=True)
            self.product_edit_form.PRICE_TAB.wait_to_be_visible(timeout=10000)

        with allure.step("Шаг 2: Применение скидки и проверка отображения новой цены"):
            self.product_edit_form.GENERIC_FEE_DISCOUNT_INPUT.wait_to_be_visible(timeout=5000)
            self.product_edit_form.GENERIC_FEE_DISCOUNT_INPUT.type(str(one_time_discount_percent))
            self.product_edit_form.INNER_ACCEPT_BTN.wait_to_be_visible(timeout=5000)
            self.product_edit_form.INNER_ACCEPT_BTN.click()

            self.inquiries_page.locators.LOAD_SPIN_THIRD.not_to_be_visible(timeout=30000)
            self.product_edit_form.TITLE.not_to_be_visible(timeout=10000)

            expected_one_time_payment = original_one_time_payment * (1 - one_time_discount_percent / 100)
            self.inquiries_page.check_individualized_price_in_inquiry(
                expected_one_time_payment, original_one_time_payment, fee_type="one_time"
            )

        with allure.step("Шаг 3: Повторное открытие формы для проверки сохранения цены"):
            self.inquiries_page.locators.ADDED_PRODUCT_EDIT_BTN[0].wait_to_be_visible(timeout=10000)
            self.inquiries_page.locators.ADDED_PRODUCT_EDIT_BTN[0].click(force=True)
            self.product_edit_form.PRICE_TAB.wait_to_be_visible(timeout=10000)
            self.product_edit_form.PRICE_TAB.click()

            self.inquiries_page.check_individualized_price_in_inquiry(
                expected_one_time_payment, original_one_time_payment, fee_type="one_time"
            )

            self.product_edit_form.CANCEL_BUTTON.wait_to_be_visible(timeout=5000)
            self.product_edit_form.CANCEL_BUTTON.click()
            self.product_edit_form.TITLE.not_to_be_visible(timeout=10000)

        with allure.step("Шаг 4: Проверка конфигурации и завершение продажи"):
            self.inquiries_page.check_configuration()

            self.inquiries_page.locators.NEXT_STEP_BTN.click()
            self.inquiries_page.wait_connect_package_offers_and_close_inquiry(
                auto_create_agreement=False, generate_documents=False
            )

        with allure.step("Шаг 5: Переход в продукты клиента и проверка индивидуализированной цены"):
            self.base_page.open(
                f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/products"
            )
            self.client_profile.locators.OTHER_PRODUCTS_EXPAND_ICON.wait_to_be_visible(timeout=20000)
            self.client_profile.locators.OTHER_PRODUCTS_EXPAND_ICON.click(force=True)
            self.client_profile.locators.PRODUCTS.wait_to_have_count(1, timeout=30000)

            self.client_profile.check_individualized_subscription_fee_on_products_page(
                expected_one_time_payment, original_one_time_payment
            )
