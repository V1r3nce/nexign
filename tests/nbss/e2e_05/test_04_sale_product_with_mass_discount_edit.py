import random

import allure
import pytest

from api.nbss.finances.payments_requests import PaymentsRequests
from api.nbss.personal_account_requests import PersonalAccountRequests
from common.helpers.data_generator import calc_price_after_discount
from common.helpers.env_helper import BASE_URL
from models.client import OrganizationClient
from models.context import test_context
from models.inquiry import prepare_inquiries
from models.product import B2BProducts, product_names_map
from pages.base_page import BasePage
from pages.locators.nbss.inquiries_elements import MassDiscountEditForm, ProductEditForm
from pages.nbss.client.client_product_profile_page import ClientProductProfilePage
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.finances.consumption_page import ConsumptionPage
from pages.nbss.inquiries_page import InquiriesPage


@pytest.mark.regress
@pytest.mark.nbss_portal
@allure.epic("E2E_05 Управление атрибутами продукта/сервиса/ресурса абонента (Индивидуализация цены)")
@allure.suite("E2E_05 Управление атрибутами продукта/сервиса/ресурса абонента (Индивидуализация цены)")
class TestSaleProductWithMassDiscountEdit:
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
        self.mass_discount_form = MassDiscountEditForm()
        self.consumption_page = ConsumptionPage()
        self.payment_api = PaymentsRequests()
        self.personal_account_api = PersonalAccountRequests()
        self.discount_percent = random.randint(1, 99)

    @allure.title("04. Продажа продуктового предложения с массовым редактированием скидки по продуктам заказа")
    @allure.id(703129)
    @allure.description(
        """
        Проверить возможность продажи продуктового предложения
        с массовым редактированием скидки по продуктам заказа.
        """
    )
    def test_sale_product_with_mass_discount_edit(self) -> None:
        satellite_l_offer_id = B2BProducts.satellite_rent
        satellite_xl_offer_id = B2BProducts.satellite_rent_alt
        product_name_l = product_names_map.get(satellite_l_offer_id)
        product_name_xl = product_names_map.get(satellite_xl_offer_id)
        switch_name = "Коммутатор_Спутниковая_связь"

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

        with allure.step("Подготовка: Добавление продуктов с поддержкой индивидуализации цены"):
            test_context.client.inquiry = prepare_inquiries(
                category=["satellite_rent", "satellite_rent"],
                product_offering_id=[satellite_l_offer_id, satellite_xl_offer_id],
                as_list=False,
            )
            products = {product.product_name: product for product in test_context.client.inquiry.product_list}

            self.inquiries_page.add_product_offer_to_commercial_order(products[product_name_l])
            self.inquiries_page.add_product_offer_to_commercial_order(products[product_name_xl])
            products[product_name_l].switch_name = switch_name
            products[product_name_xl].switch_name = switch_name
            subscription_fee_l = products[product_name_l].subscription_fee
            subscription_fee_xl = products[product_name_xl].subscription_fee

        with allure.step("Подготовка: Бронирование ресурсов и проверка конфигурации"):
            self.inquiries_page.auto_reserve_all_resources(category="satellite_rent", equipment_patterns=["_L_", "_XL_"])

        with allure.step("Шаг 1: Назначение скидок на продукты через массовое редактирование"):
            expected_subscription_fee_l = calc_price_after_discount(subscription_fee_l, self.discount_percent)
            expected_subscription_fee_xl = calc_price_after_discount(subscription_fee_xl, self.discount_percent)

            self.inquiries_page.open_mass_discount_assignment_form()
            self.inquiries_page.fill_discounts_on_mass_discount_assignment_form(
                [self.discount_percent, self.discount_percent]
            )
            self.inquiries_page.check_individualized_price_in_mass_discounts_form(
                product_index=0,
                fee_type="subscription",
                expected_final_price=expected_subscription_fee_xl,
            )
            self.inquiries_page.check_individualized_price_in_mass_discounts_form(
                product_index=1,
                fee_type="subscription",
                expected_final_price=expected_subscription_fee_l,
            )
            self.inquiries_page.save_discounts_on_mass_discount_assignment_form()

        with allure.step("Шаг 2: Проверка конфигурации и завершение продажи"):
            self.inquiries_page.check_configuration()
            self.inquiries_page.locators.NEXT_STEP_BTN.click()
            self.inquiries_page.wait_connect_package_offers_and_close_inquiry(
                auto_create_agreement=False, generate_documents=False
            )

        with allure.step("Шаг 3: Переход в продукты клиента и проверка индивидуализированных цен"):
            self.client_product_profile.open_products_page(
                user_id=test_context.client.user_id,
                product_list=test_context.client.inquiry.product_list,
                is_activated=False,
            )
            self.client_product_profile.check_individualized_price_on_products_page(
                product_index=0,
                expected_base_price=subscription_fee_l,
                expected_final_price=expected_subscription_fee_l,
                individualized_price_index=0,
            )

            self.client_product_profile.check_individualized_price_on_products_page(
                product_index=1,
                expected_base_price=subscription_fee_xl,
                expected_final_price=expected_subscription_fee_xl,
                individualized_price_index=1,
            )
