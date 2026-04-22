import random

import allure
import pytest

from common.helpers.data_generator import calc_price_after_discount
from common.helpers.env_helper import BASE_URL
from models.client import OrganizationClient
from models.context import test_context
from models.inquiry import prepare_inquiries
from models.product import B2BProducts
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
        nexign_stand_login,
        create_organization_with_agreement_and_account: OrganizationClient,
    ) -> None:
        self.base_page = BasePage()
        self.client = create_organization_with_agreement_and_account
        self.inquiries_page = InquiriesPage()
        self.client_profile = ClientProfilePage()
        self.product_edit_form = ProductEditForm()
        self.discount_percent = random.randint(1, 99)

    @allure.title("03. Продажа продуктового предложения с индивидуализацией стоимости разовой платы")
    @allure.id(660624)
    @allure.description(
        """
        Проверить возможность продажи продуктового предложения
        с индивидуализацией стоимости разовой платы.
        """
    )
    def test_sale_product_with_individual_one_time_payment(self) -> None:
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
            test_context.client.inquiry = prepare_inquiries(
                category="equipment_sale", product_offering_id=B2BProducts.equipment_sale, as_list=False
            )
            product = test_context.client.inquiry.product

            self.inquiries_page.add_product_offer_to_commercial_order(product)
            original_one_time_price = product.one_time_payment
            expected_one_time_price = calc_price_after_discount(original_one_time_price, self.discount_percent)

            self.inquiries_page.auto_reserve_all_resources(test_context.client.inquiry.product.category)

        with allure.step("Шаг 1: Применение скидки и проверка отображения новой цены"):
            self.inquiries_page.individualize_price(percent=self.discount_percent, fee_type="one_time")

        with allure.step("Шаг 2: Повторное открытие формы для проверки сохранения цены"):
            self.inquiries_page.open_edit_product_form()
            self.inquiries_page.open_price_tab()
            self.inquiries_page.check_individualized_price_in_edit_product_form(
                expected_base_price=original_one_time_price,
                expected_final_price=expected_one_time_price,
                fee_type="one_time",
            )
            self.inquiries_page.close_edit_product_form()

        with allure.step("Шаг 3: Проверка конфигурации и завершение продажи"):
            self.inquiries_page.check_configuration()

            self.inquiries_page.locators.NEXT_STEP_BTN.click()
            self.inquiries_page.wait_connect_package_offers_and_close_inquiry(
                auto_create_agreement=False, generate_documents=False
            )

        with allure.step("Шаг 4: Переход в продукты клиента и проверка индивидуализированной цены"):
            self.base_page.open(
                f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/products"
            )
            self.client_profile.expand_other_products()
            self.client_profile.locators.PRODUCTS.wait_to_have_count(1, timeout=10000)

            self.client_profile.check_individualized_price_on_products_page(
                fee_type="one_time",
                expected_base_price=original_one_time_price,
                expected_final_price=expected_one_time_price,
            )
