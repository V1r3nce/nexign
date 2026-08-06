import random

import allure
import pytest

from common.helpers.data_generator import calc_price_after_discount
from common.helpers.env_helper import BASE_URL
from models.client import OrganizationClient
from models.context import test_context
from models.inquiry import prepare_inquiries
from models.product import B2BProducts, product_names_map
from pages.base_page import BasePage
from pages.locators.nbss.inquiries_elements import ProductEditForm
from pages.nbss.client.client_product_profile_page import ClientProductProfilePage
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.inquiries_page import InquiriesPage


@pytest.mark.regress
@pytest.mark.nbss_portal
@allure.epic("E2E_05 Управление атрибутами продукта/сервиса/ресурса абонента (Индивидуализация цены)")
@allure.suite("E2E_05 Управление атрибутами продукта/сервиса/ресурса абонента (Индивидуализация цены)")
class TestSaleProductsWithPriceIndividualization:
    @pytest.fixture(autouse=True)
    def setup(
        self,
        nexign_stand_login,
        create_organization_with_agreement_and_account: OrganizationClient,
    ) -> None:
        self.base_page = BasePage()
        self.inquiries_page = InquiriesPage()
        self.client_profile = ClientProfilePage()
        self.client_product_profile = ClientProductProfilePage()
        self.product_edit_form = ProductEditForm()
        self.client = create_organization_with_agreement_and_account
        self.discount_percent = random.randint(1, 19) * 5

    @allure.title(
        "01. Продажа продуктового предложения с индивидуализацией стоимостей разового списания и абонентской платы"
    )
    @allure.id(703128)
    def test_sale_product_with_individual_subscription_and_one_time_price(self) -> None:
        product_name_rent = product_names_map.get(B2BProducts.satellite_rent)
        product_name_sale = product_names_map.get(B2BProducts.equipment_sale)

        with allure.step("Подготовка: API Создание заявки на продажу и добавление продукта"):
            self.base_page.open(
                f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/overview"
            )
            self.inquiries_page.sale_initialization(
                self.client,
                need_contact_data=True,
                agreement=self.client.agreements[0].number,
                account=self.client.agreements[0].accounts[0].number,
                priority="Высокий",
                add_kp="no",
                create_add_agreement="auto",
            )

            test_context.client.inquiry = prepare_inquiries(category=["satellite_rent", "equipment_sale"], as_list=False)
            products = {product.product_name: product for product in test_context.client.inquiry.product_list}

            self.inquiries_page.add_product_offer_to_commercial_order(products[product_name_rent])
            self.inquiries_page.add_product_offer_to_commercial_order(products[product_name_sale])
            products[product_name_rent].switch_name = "Коммутатор_Спутниковая_связь"
            products[product_name_sale].switch_name = "Коммутатор_Спутниковая_связь"
            original_subscription_fee = products[product_name_rent].subscription_fee
            original_one_time_price = products[product_name_sale].one_time_payment
            expected_subscription_fee = calc_price_after_discount(original_subscription_fee, self.discount_percent)
            expected_one_time_price = calc_price_after_discount(original_one_time_price, self.discount_percent)

        with allure.step("Подготовка: Бронирование ресурсов и проверка конфигурации"):
            self.inquiries_page.auto_reserve_all_resources(
                [products[product_name_rent].category, products[product_name_sale].category]
            )
            self.inquiries_page.check_configuration()

        self.inquiries_page.individualize_price(
            product_offering_index=0, percent=self.discount_percent, fee_type="subscription"
        )
        self.inquiries_page.individualize_price(
            product_offering_index=1, percent=self.discount_percent, fee_type="one_time"
        )

        with allure.step("Шаг 3: Повторное открытие формы для проверки сохранения цены"):
            self.inquiries_page.open_edit_product_form()
            self.inquiries_page.open_price_tab()
            self.inquiries_page.check_individualized_price_in_edit_product_form(
                expected_base_price=original_subscription_fee,
                expected_final_price=expected_subscription_fee,
                fee_type="subscription",
            )
            self.inquiries_page.close_edit_product_form()

            self.inquiries_page.open_edit_product_form(1)
            self.inquiries_page.open_price_tab()
            self.inquiries_page.check_individualized_price_in_edit_product_form(
                expected_base_price=original_one_time_price,
                expected_final_price=expected_one_time_price,
                fee_type="one_time",
            )
            self.inquiries_page.close_edit_product_form()

        with allure.step("Шаг 4: Проверка конфигурации и завершение продажи"):
            self.inquiries_page.check_configuration()
            self.inquiries_page.locators.NEXT_STEP_BTN.wait_to_be_enabled()
            self.inquiries_page.locators.NEXT_STEP_BTN.click()
            self.inquiries_page.wait_connect_package_offers_and_close_inquiry(
                auto_create_agreement=False, generate_documents=False
            )

        with allure.step("Шаг 5: Переход в продукты клиента и проверка индивидуализированной цены"):
            self.client_product_profile.open_products_page(
                user_id=test_context.client.user_id,
                product_list=test_context.client.inquiry.product_list,
                is_activated=False,
            )
            self.client_product_profile.check_individualized_price_on_products_page(
                product_index=0,
                expected_base_price=original_subscription_fee,
                expected_final_price=expected_subscription_fee,
            )
