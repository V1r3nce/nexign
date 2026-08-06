import random

import allure
import pytest

from api.nbss.finances.payments_requests import PaymentsRequests
from api.nbss.personal_account_requests import PersonalAccountRequests
from common.helpers.data_generator import calc_price_after_discount
from common.helpers.env_helper import BASE_URL
from common.helpers.string_helper import check_price
from models.client import OrganizationClient
from models.context import test_context
from models.inquiry import prepare_inquiries
from pages.base_page import BasePage
from pages.locators.nbss.inquiries_elements import ProductEditForm
from pages.nbss.client.client_product_profile_page import ClientProductProfilePage
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
        self.client_product_profile = ClientProductProfilePage()
        self.product_edit_form = ProductEditForm()
        self.payment_api = PaymentsRequests()
        self.personal_account_api = PersonalAccountRequests()
        self.discount_percent = random.randint(1, 99)

    @allure.title("07. Массовый сброс скидки у подключенного продукта")
    @allure.id(703131)
    @allure.description(
        """
        Проверить возможность массового сброса скидки у подключенного продукта.
        """
    )
    def test_sale_product_with_individual_subscription_price(self) -> None:
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
            test_context.client.inquiry = prepare_inquiries(category="satellite_rent", as_list=False)
            product = test_context.client.inquiry.product

            self.inquiries_page.add_product_offer_to_commercial_order(product)
            product.switch_name = "Коммутатор_Спутниковая_связь"
            original_subscription_fee = product.subscription_fee
            expected_subscription_fee = calc_price_after_discount(original_subscription_fee, self.discount_percent)

            self.inquiries_page.auto_reserve_all_resources(test_context.client.inquiry.product.category)
            self.inquiries_page.check_configuration()

        with allure.step("Шаг 1: Применение скидки и завершение первой продажи"):
            self.inquiries_page.individualize_price(percent=self.discount_percent)
            self.inquiries_page.check_individualized_price_in_inquiry(
                fee_type="subscription",
                expected_base_price=original_subscription_fee,
                expected_final_price=expected_subscription_fee,
            )

            self.inquiries_page.open_edit_product_form()
            self.inquiries_page.open_price_tab()
            self.inquiries_page.check_individualized_price_in_edit_product_form(
                expected_base_price=original_subscription_fee,
                expected_final_price=expected_subscription_fee,
                fee_type="subscription",
            )
            self.inquiries_page.close_edit_product_form()

            self.inquiries_page.check_configuration()

            self.inquiries_page.locators.NEXT_STEP_BTN.wait_to_be_enabled(timeout=10000)
            self.inquiries_page.locators.NEXT_STEP_BTN.click()
            self.inquiries_page.wait_connect_package_offers_and_close_inquiry(
                auto_create_agreement=False, generate_documents=False
            )

        with allure.step("Шаг 2: Пополнение счета и проверка индивидуализированной цены на странице продуктов"):
            payment_amount = original_subscription_fee
            account_id = self.client.agreements[0].accounts[0].id
            self.payment_api.create_default_payment(account_id, payment_amount)
            self.personal_account_api.wait_check_current_main_balance(
                account_id, payment_amount - expected_subscription_fee
            )
            self.personal_account_api.wait_accruals(test_context.client.user_id)

            self.client_product_profile.open_products_page(
                user_id=test_context.client.user_id,
                product_list=test_context.client.inquiry.product_list,
                is_activated=True,
            )
            self.client_product_profile.check_individualized_price_on_products_page(
                expected_base_price=original_subscription_fee,
                expected_final_price=expected_subscription_fee,
            )

        with allure.step("Шаг 3: Редактирование продажи и сброс скидки"):
            self.client_product_profile.create_product_edit_inquiry()
            self.inquiries_page.reset_discount()

        with allure.step("Шаг 4: Проверка конфигурации и завершение продажи после сброса скидки"):
            self.inquiries_page.check_configuration()
            self.inquiries_page.locators.NEXT_STEP_BTN.click()
            self.inquiries_page.wait_connect_package_offers_and_close_inquiry(
                auto_create_agreement=False, generate_documents=False
            )

        with allure.step("Шаг 5: Переход в продукты клиента и проверка исходной цены без индивидуализации"):
            self.client_product_profile.open_products_page(
                user_id=test_context.client.user_id,
                product_list=test_context.client.inquiry.product_list,
                is_activated=True,
            )
            check_price(
                self.client_product_profile.locators.PRODUCTS_SUBSCRIPTION_FEE[0],
                original_subscription_fee,
                check_format=False,
            )
