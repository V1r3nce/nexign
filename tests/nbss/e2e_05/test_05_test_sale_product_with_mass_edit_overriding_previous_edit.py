import allure
import pytest

from common.helpers.env_helper import BASE_URL
from common.helpers.string_helper import get_price_and_currency
from models.client import OrganizationClient
from models.context import test_context
from models.inquiry import prepare_inquiries
from pages.base_page import BasePage
from pages.locators.nbss.inquiries_elements import MassDiscountEditForm, ProductEditForm
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
        self.product_edit_form = ProductEditForm()
        self.mass_discount_form = MassDiscountEditForm()

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
        subscription_discount_percent = 20
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
            test_context.client.inquiry_list = prepare_inquiries(category="satellite_rent")
            self.inquiries_page.add_product_offer_to_commercial_order(test_context.client.inquiry.product)

            product = test_context.client.inquiry.product
            product.switch_name = "Коммутатор_Спутниковая_связь"

            original_subscription_fee = product.subscription_fee

            self.inquiries_page.auto_reserve_all_resources(test_context.client.inquiry.product.category)
            self.inquiries_page.check_configuration()

        with allure.step("Шаг 1: Применение первой скидки и проверка результата"):
            self.inquiries_page.locators.LOAD_SPIN_THIRD.not_to_be_visible()
            self.inquiries_page.locators.ADDED_PRODUCT_SUBSCRIPTION_FEE_BUTTON[0].wait_to_be_visible(timeout=10000)
            self.inquiries_page.locators.ADDED_PRODUCT_SUBSCRIPTION_FEE_BUTTON[0].click(force=True)
            self.product_edit_form.PRICE_TAB.wait_to_be_visible(timeout=10000)

            self.product_edit_form.SUBSCRIPTION_FEE_DISCOUNT_INPUT.wait_to_be_visible(timeout=5000)
            self.product_edit_form.SUBSCRIPTION_FEE_DISCOUNT_INPUT.type(str(subscription_discount_percent))

            self.product_edit_form.PRICE_COMMENT_TEXTAREA.wait_to_be_visible(timeout=5000)
            self.product_edit_form.PRICE_COMMENT_TEXTAREA.fill(price_comment)

            self.product_edit_form.INNER_ACCEPT_BTN.wait_to_be_visible(timeout=5000)
            self.product_edit_form.INNER_ACCEPT_BTN.click()

            self.inquiries_page.locators.LOAD_SPIN_THIRD.not_to_be_visible(timeout=30000)
            self.product_edit_form.TITLE.not_to_be_visible(timeout=10000)

            expected_subscription = original_subscription_fee * (1 - subscription_discount_percent / 100)
            self.inquiries_page.check_individualized_price_in_inquiry(
                expected_subscription, original_subscription_fee, fee_type="subscription"
            )

        with allure.step("Шаг 2: Массовое редактирование скидки и проверка перезатирания"):
            self.inquiries_page.locators.LOAD_SPIN_THIRD.not_to_be_visible(timeout=30000)
            self.inquiries_page.locators.CHECK_CONFIGURATION_BTN.wait_to_be_visible(timeout=10000)
            self.inquiries_page.check_configuration()

            self.product_edit_form.TITLE.not_to_be_visible(timeout=10000)
            self.inquiries_page.locators.ASSIGN_DISCOUNTS_BTN.wait_to_be_visible(timeout=10000)
            self.inquiries_page.locators.ASSIGN_DISCOUNTS_BTN.click()
            self.mass_discount_form.TITLE.wait_to_be_visible(timeout=10000)

            self.mass_discount_form.SUBSCRIPTION_FEE_FINAL_PRICE.wait_elements_visible(0, timeout=10000)
            current_price_text = self.mass_discount_form.SUBSCRIPTION_FEE_FINAL_PRICE[0].get_attribute("value")
            current_price, _ = get_price_and_currency(current_price_text)
            expected_price_after_first_discount = original_subscription_fee * (1 - subscription_discount_percent / 100)
            assert abs(current_price - expected_price_after_first_discount) < 0.01, (
                f"БАГ: При повторном открытии формы массового редактирования отображается оригинальная цена "
                f"{current_price:.2f} вместо цены после первой скидки {expected_price_after_first_discount:.2f}. "
                f"Оригинальная цена: {original_subscription_fee:.2f}, "
                f"скидка была применена: {subscription_discount_percent}%"
            )

            mass_discount_percent = 20
            self.mass_discount_form.SUBSCRIPTION_FEE_DISCOUNT_INPUTS.wait_elements_visible(0)
            self.mass_discount_form.SUBSCRIPTION_FEE_DISCOUNT_INPUTS[0].fill(str(mass_discount_percent))

            self.mass_discount_form.ACCEPT_BTN.wait_to_be_visible(timeout=5000)
            self.mass_discount_form.ACCEPT_BTN.click()
            self.mass_discount_form.TITLE.not_to_be_visible(timeout=10000)

        with allure.step("Шаг 3: Обновление заявки, проверка конфигурации и завершение продажи"):
            self.inquiries_page.locators.REFRESH_BTN_INQUIRY.wait_to_be_visible(timeout=10000)
            self.inquiries_page.locators.REFRESH_BTN_INQUIRY.click()

            self.inquiries_page.locators.LOAD_SPIN_THIRD.not_to_be_visible(timeout=30000)
            self.inquiries_page.locators.CHECK_CONFIGURATION_BTN.wait_to_be_visible(timeout=10000)
            self.inquiries_page.check_configuration()

            self.inquiries_page.locators.NEXT_STEP_BTN.click()
            self.inquiries_page.wait_connect_package_offers_and_close_inquiry(
                auto_create_agreement=False, generate_documents=False
            )

        with allure.step("Шаг 4: Переход в продукты клиента и проверка индивидуализированной цены"):
            self.base_page.open(
                f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/products"
            )
            self.client_profile.locators.PRODUCTS_LIST.wait_to_be_visible(timeout=15000)

            self.client_profile.expand_all_products()
            self.client_profile.locators.PRODUCTS.wait_to_have_count(1, timeout=30000)

            mass_discount_percent = 20
            expected_subscription = original_subscription_fee * (1 - mass_discount_percent / 100)
            self.client_profile.check_individualized_subscription_fee_on_products_page(
                expected_subscription, original_subscription_fee, product_index=0
            )
