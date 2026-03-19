import allure
import pytest

from api.nbss.finances.payments_requests import PaymentsRequests
from api.nbss.personal_account_requests import PersonalAccountRequests
from common.helpers.env_helper import BASE_URL
from models.client import OrganizationClient
from models.context import test_context
from models.inquiry import prepare_inquiries
from pages.base_page import BasePage
from pages.locators.nbss.inquiries_elements import MassDiscountEditForm, ProductEditForm
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
        self.product_edit_form = ProductEditForm()
        self.mass_discount_form = MassDiscountEditForm()
        self.consumption_page = ConsumptionPage()
        self.payment_api = PaymentsRequests()
        self.personal_account_api = PersonalAccountRequests()

    @allure.title("04. Продажа продуктового предложения с массовым редактированием скидки по продуктам заказа")
    @allure.id(703129)
    @allure.description(
        """
        Проверить возможность продажи продуктового предложения
        с массовым редактированием скидки по продуктам заказа.
        """
    )
    def test_sale_product_with_mass_discount_edit(self) -> None:
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
            self.inquiries_page.locators.ADD_SALE_BTN.wait_to_be_visible(timeout=10000)
            self.inquiries_page.locators.ADD_SALE_BTN.click()

            with allure.step("Выбор категории продуктового предложения"):
                category_name = self.inquiries_page.category_map["satellite_rent"]
                self.inquiries_page.locators.product_offer_form.PRODUCT_CATEGORY.select_by_value(
                    category_name, contains=True
                )
                self.inquiries_page.locators.product_offer_form.SEARCH_BTN.click()

            product_names = ["Спутник L Аренда", "Спутник XL Аренда"]
            products = []

            for product_name in product_names:
                product = self.inquiries_page.choose_product_offer_with_name(product_name)
                product.switch_name = "Коммутатор_Спутниковая_связь"
                products.append(product)

            self.inquiries_page.locators.product_offer_form.ADD_BTN.wait_to_be_enabled()
            self.inquiries_page.locators.product_offer_form.ADD_BTN.click()

            test_context.client.inquiry_list = prepare_inquiries(category="satellite_rent")
            test_context.client.inquiry.product_list = test_context.client.inquiry.product_list or []
            test_context.client.inquiry.product_list.extend(products)

            product_l, product_xl = products
            original_subscription_fee_l, original_subscription_fee_xl = (
                product_l.subscription_fee,
                product_xl.subscription_fee,
            )

        with allure.step("Подготовка: Бронирование ресурсов и проверка конфигурации"):
            self.inquiries_page.locators.ADDED_PRODUCT.wait_to_have_count(2, timeout=10000)

            self.inquiries_page.locators.LOAD_SPIN_THIRD.not_to_be_visible()

            test_context.client.inquiry.product = product_l
            self.inquiries_page.auto_reserve_all_resources(category="satellite_rent", equipment_patterns=["_L_", "_XL_"])

        with allure.step("Шаг 1: Назначение скидок на продукты через массовое редактирование"):
            discount_percent = 20

            self.inquiries_page.locators.ASSIGN_DISCOUNTS_BTN.wait_to_be_visible(timeout=10000)
            self.inquiries_page.locators.ASSIGN_DISCOUNTS_BTN.click()

            self.mass_discount_form.WARNING_MESSAGE.wait_to_be_visible(timeout=5000)
            self.mass_discount_form.WARNING_MESSAGE.to_contain_text(
                "Указанные значения изменят текущие значения цен и комментариев по всем выбранным Продуктовым предложениям"
            )

            self.mass_discount_form.SUBSCRIPTION_FEE_DISCOUNT_INPUTS.wait_elements_visible(0)
            self.mass_discount_form.SUBSCRIPTION_FEE_DISCOUNT_INPUTS.wait_elements_visible(1)
            self.mass_discount_form.SUBSCRIPTION_FEE_DISCOUNT_INPUTS[0].fill(str(discount_percent))
            self.mass_discount_form.SUBSCRIPTION_FEE_DISCOUNT_INPUTS[1].fill(str(discount_percent))

            expected_subscription_l = original_subscription_fee_l * (1 - discount_percent / 100)
            expected_subscription_xl = original_subscription_fee_xl * (1 - discount_percent / 100)

            self.inquiries_page.check_prices(
                expected_prices=[expected_subscription_l, expected_subscription_xl],
                mass_discount_form=self.mass_discount_form,
                check_old_price=False,
            )

            self.mass_discount_form.ACCEPT_BTN.wait_to_be_visible(timeout=5000)
            self.mass_discount_form.ACCEPT_BTN.click()
            self.page.get_by_role("heading", name="Назначение скидок").wait_for(state="hidden", timeout=10000)

        with allure.step("Шаг 2: Проверка конфигурации и завершение продажи"):
            self.inquiries_page.check_configuration()

            self.inquiries_page.locators.NEXT_STEP_BTN.click()
            self.inquiries_page.wait_connect_package_offers_and_close_inquiry(
                auto_create_agreement=False, generate_documents=False
            )

        with allure.step("Шаг 3: Переход в продукты клиента и проверка индивидуализированных цен"):
            self.base_page.open(
                f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/products"
            )
            self.client_profile.locators.PRODUCTS_LIST.wait_to_be_visible(timeout=15000)

            self.client_profile.expand_all_products()
            self.client_profile.locators.PRODUCTS.wait_to_have_count(2, timeout=60000)

            expected_subscription_l = original_subscription_fee_l * (1 - discount_percent / 100)
            expected_subscription_xl = original_subscription_fee_xl * (1 - discount_percent / 100)
            expected_subscription_l = original_subscription_fee_l * (1 - discount_percent / 100)
            expected_subscription_xl = original_subscription_fee_xl * (1 - discount_percent / 100)

            for i in range(2):
                product_name = self.client_profile.locators.PRODUCT_NAME[i].text

                if "Спутник L" in product_name:
                    self.client_profile.check_individualized_subscription_fee_on_products_page(
                        expected_subscription_l, original_subscription_fee_l, product_index=i
                    )
                elif "Спутник XL" in product_name:
                    self.client_profile.check_individualized_subscription_fee_on_products_page(
                        expected_subscription_xl, original_subscription_fee_xl, product_index=i
                    )
                else:
                    raise AssertionError(f"Неожиданное имя продукта: {product_name}")
