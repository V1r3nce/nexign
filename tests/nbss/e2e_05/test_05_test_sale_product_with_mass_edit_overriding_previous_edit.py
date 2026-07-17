import random

import allure
import pytest

from common.helpers.data_generator import calc_price_after_discount
from common.helpers.env_helper import BASE_URL
from models.client import OrganizationClient
from models.context import test_context
from models.inquiry import prepare_inquiries
from pages.base_page import BasePage
from pages.locators.nbss.inquiries_elements import MassDiscountEditForm, ProductEditForm
from pages.nbss.client.client_product_profile_page import ClientProductProfilePage
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.inquiries_page import InquiriesPage


@pytest.mark.regress
@pytest.mark.nbss_portal
@allure.epic("E2E_05 Управление атрибутами продукта/сервиса/ресурса абонента (Индивидуализация цены)")
@allure.suite("E2E_05 Управление атрибутами продукта/сервиса/ресурса абонента (Индивидуализация цены)")
class TestSaleProductWithPriceIndividualizationPartial:
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
        self.discount_percent = random.randint(1, 99)
        self.mass_discount_percent = random.randint(1, 99)

    @allure.title(
        "05. Продажа продуктового предложения с массовым редактированием, перезатирающим ранее произведенное редактирование"
    )
    @allure.id(703132)
    @allure.description(
        """
        Проверить возможность продажи продуктового предложения
        с массовым редактированием, перезатирающим ранее произведенное редактирование.
        """
    )
    def test_sale_product_with_individual_subscription_price_partial(self) -> None:
        price_comment = f"Цены согласованы с тест-менеджером {test_context.client.contact_phone}"

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

            self.inquiries_page.auto_reserve_all_resources(product.category)
            self.inquiries_page.check_configuration()

        with allure.step("Шаг 1: Применение первой скидки и проверка результата"):
            self.inquiries_page.individualize_price(
                percent=self.discount_percent, fee_type="subscription", comment=price_comment
            )
            self.inquiries_page.check_individualized_price_in_inquiry(
                fee_type="subscription",
                expected_base_price=original_subscription_fee,
                expected_final_price=expected_subscription_fee,
            )

        with allure.step("Шаг 2: Массовое редактирование скидки и проверка перезатирания"):
            self.inquiries_page.locators.LOAD_SPIN_THIRD.not_to_be_visible(timeout=30000)
            self.inquiries_page.check_configuration()

            self.inquiries_page.open_mass_discount_assignment_form()
            self.inquiries_page.check_individualized_price_in_mass_discounts_form(
                product_index=0,
                fee_type="subscription",
                expected_base_price=original_subscription_fee,
                expected_final_price=original_subscription_fee,
            )
            self.inquiries_page.fill_discounts_on_mass_discount_assignment_form([self.mass_discount_percent])
            self.inquiries_page.check_individualized_price_in_mass_discounts_form(
                product_index=0,
                fee_type="subscription",
                expected_base_price=original_subscription_fee,
                expected_final_price=expected_subscription_fee,
            )
            self.inquiries_page.save_discounts_on_mass_discount_assignment_form()

        with allure.step("Шаг 3: Обновление заявки, проверка конфигурации и завершение продажи"):
            self.inquiries_page.refresh_inquiry()
            self.inquiries_page.check_configuration()

            self.inquiries_page.locators.NEXT_STEP_BTN.click()
            self.inquiries_page.wait_connect_package_offers_and_close_inquiry(
                auto_create_agreement=False, generate_documents=False
            )

        with allure.step("Шаг 4: Переход в продукты клиента и проверка индивидуализированной цены"):
            self.client_product_profile.open_products_page(
                user_id=test_context.client.user_id,
                product_list=test_context.client.inquiry.product_list,
                is_activated=False,
            )
            self.client_product_profile.check_individualized_price_on_products_page(
                fee_type="subscription",
                expected_base_price=original_subscription_fee,
                expected_final_price=expected_subscription_fee,
            )
