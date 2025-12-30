import allure
import pytest
from playwright.sync_api import Page

from api.nbss.finances.payments_requests import PaymentsRequests
from api.nbss.personal_account_requests import PersonalAccountRequests
from common.helpers.env_helper import BASE_URL
from common.helpers.string_helper import get_price_and_currency
from models.client import OrganizationClient
from models.context import test_context
from models.inquiry import prepare_inquiries
from pages.base_page import BasePage
from pages.locators.nbss.inquiries_elements import ProductEditForm
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.finances.consumption_page import ConsumptionPage
from pages.nbss.inquiries_page import InquiriesPage


@pytest.mark.regress
@pytest.mark.nbss_portal
@allure.epic("E2E_05 Управление атрибутами продукта/сервиса/ресурса абонента (Индивидуализация цены)")
@allure.suite("E2E_05 Управление атрибутами продукта/сервиса/ресурса абонента (Индивидуализация цены)")
class TestSaleProductWithNegativeAndExcessiveDiscount:
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
        self.payment_api = PaymentsRequests()
        self.personal_account_api = PersonalAccountRequests()
        self.consumption_page = ConsumptionPage()

    @allure.title(
        "09. Продажа продуктового предложения с индивидуализацией стоимости абонентской платы (отрицательная скидка и скидка, превышающая стоимость продукта)"
    )
    @allure.id(703126)
    @allure.description(
        """
        Проверить обработку некорректных значений скидки:
        - отрицательная скидка
        - скидка, превышающая стоимость продукта
        """
    )
    def test_sale_product_with_negative_and_excessive_discount(self) -> None:
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

        with allure.step("Шаг 1: Нажать на синюю цену абонентской платы для перехода к редактированию"):
            self.inquiries_page.locators.LOAD_SPIN_THIRD.not_to_be_visible()
            self.inquiries_page.locators.ADDED_PRODUCT_SUBSCRIPTION_FEE_BUTTON[0].wait_to_be_visible(timeout=10000)
            self.inquiries_page.locators.ADDED_PRODUCT_SUBSCRIPTION_FEE_BUTTON[0].click(force=True)
            self.product_edit_form.PRICE_TAB.wait_to_be_visible(timeout=10000)

        with allure.step("Шаг 2: Проверка обработки отрицательной скидки"):
            self.product_edit_form.SUBSCRIPTION_FEE_DISCOUNT_INPUT.wait_to_be_visible(timeout=5000)

            negative_discount = -10
            self.product_edit_form.SUBSCRIPTION_FEE_DISCOUNT_INPUT.type(str(negative_discount))
            self.product_edit_form.SUBSCRIPTION_FEE_DISCOUNT_INPUT.wait_to_be_visible(timeout=5000)

            current_value = self.product_edit_form.SUBSCRIPTION_FEE_DISCOUNT_INPUT.get_attribute("value")
            assert current_value is None or current_value == "" or int(current_value) >= 0, (
                f"Система приняла отрицательную скидку {negative_discount}%. Текущее значение: {current_value}"
            )

        with allure.step("Шаг 3: Проверка обработки скидки, превышающей стоимость продукта"):
            excessive_discount = 150
            self.product_edit_form.SUBSCRIPTION_FEE_DISCOUNT_INPUT.type(str(excessive_discount))

            self.product_edit_form.SUBSCRIPTION_FEE_DISCOUNT_ERROR.wait_to_be_visible(timeout=5000)
            error_message_text = self.product_edit_form.SUBSCRIPTION_FEE_DISCOUNT_ERROR.inner_text
            assert "Допустимое значение от 0 до 100" in error_message_text, (
                f"Сообщение об ошибке не соответствует ожидаемому. Ожидалось: 'Допустимое значение от 0 до 100'. Получено: {error_message_text}"
            )

            self.product_edit_form.SUBSCRIPTION_FEE_FINAL_PRICE.wait_to_be_visible(timeout=2000)
            final_price_value = self.product_edit_form.SUBSCRIPTION_FEE_FINAL_PRICE.get_attribute("value")
            final_price, _ = get_price_and_currency(final_price_value)
            assert final_price >= 0, f"Итоговая цена стала отрицательной: {final_price}"
            assert final_price <= original_subscription_fee, (
                f"Итоговая цена превышает исходную цену при скидке {excessive_discount}%: {final_price} > {original_subscription_fee}"
            )

        with allure.step("Шаг 4: Ввод итоговой цены, превышающей исходную, и проверка сохранения"):
            self.product_edit_form.SUBSCRIPTION_FEE_DISCOUNT_INPUT.fill("")
            self.product_edit_form.SUBSCRIPTION_FEE_DISCOUNT_INPUT.wait_to_be_visible(timeout=5000)

            excessive_final_price = original_subscription_fee * 1.1
            self.product_edit_form.SUBSCRIPTION_FEE_FINAL_PRICE.wait_to_be_visible(timeout=5000)

            self.product_edit_form.SUBSCRIPTION_FEE_FINAL_PRICE.fill("")
            self.product_edit_form.SUBSCRIPTION_FEE_FINAL_PRICE.fill(str(int(excessive_final_price)))
            self.product_edit_form.SUBSCRIPTION_FEE_FINAL_PRICE.wait_to_be_visible(timeout=5000)

            self.product_edit_form.INNER_ACCEPT_BTN.wait_to_be_visible(timeout=5000)
            self.product_edit_form.INNER_ACCEPT_BTN.click()
            self.product_edit_form.TITLE.not_to_be_visible(timeout=10000)

            self.inquiries_page.check_individualized_price_in_inquiry(
                excessive_final_price, original_subscription_fee, fee_type="subscription"
            )

        with allure.step("Шаг 5: Проверка конфигурации и завершение продажи"):
            self.inquiries_page.check_configuration()

            self.inquiries_page.locators.NEXT_STEP_BTN.click()
            self.inquiries_page.wait_connect_package_offers_and_close_inquiry(
                auto_create_agreement=False, generate_documents=False
            )

        with allure.step("Шаг 6: Пополнение счета и переход в продукты клиента"):
            self.inquiries_page.locators.LOAD_SPIN_THIRD.not_to_be_visible(timeout=30000)
            payment_amount = excessive_final_price * 1.2
            account_id = self.client.agreements[0].accounts[0].id
            self.payment_api.create_default_payment(account_id, payment_amount)
            self.personal_account_api.wait_check_current_main_balance(account_id, payment_amount)
            self.personal_account_api.wait_accruals(test_context.client.user_id)

            self.base_page.open(
                f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/products"
            )
            self.client_profile.locators.PRODUCTS_LIST.wait_to_be_visible(timeout=15000)
            self.client_profile.locators.PRODUCTS.wait_to_have_count(1, timeout=30000)

        with allure.step("Шаг 7: Проверка статуса продукта и индивидуализированной цены"):
            self.client_profile.locators.PRODUCTS_STATUS_COLOR[0].wait_to_be_visible(timeout=30000)
            self.client_profile.locators.PRODUCTS_STATUS_COLOR[0].element_have_css_color("background-color", "green")

            self.client_profile.check_individualized_subscription_fee_on_products_page(
                excessive_final_price, original_subscription_fee
            )

        with allure.step("Шаг 8: Переход в детали потребления и проверка начислений"):
            self.client_profile.locators.PRODUCTS_DETAILS_OPEN_BTN.wait_to_be_visible(timeout=5000)
            self.client_profile.locators.PRODUCTS_DETAILS_OPEN_BTN.click(force=True)
            self.client_profile.locators.PRODUCTS_DETAILS_BTN.wait_to_be_visible(timeout=5000)
            self.client_profile.locators.PRODUCTS_DETAILS_BTN.click(force=True)

            self.consumption_page.click_tab("Начисления")
            self.consumption_page.check_accrual_amount(excessive_final_price, index=0)
