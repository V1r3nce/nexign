import allure
import pytest

from api.nbss.finances.payments_requests import PaymentsRequests
from api.nbss.personal_account_requests import PersonalAccountRequests
from common.helpers.checker import assert_that
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
        negative_discount = -10
        excessive_discount = 150

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

            self.inquiries_page.auto_reserve_all_resources(product.category)
            self.inquiries_page.check_configuration()

        with allure.step(
            "Шаг 2: Нажать на синюю цену абонентской платы для перехода к редактированию, проверить обработку отрицательной скидки"
        ):
            self.inquiries_page.individualize_price(percent=negative_discount)

        with allure.step("Шаг 3: Проверка обработки скидки, превышающей стоимость продукта"):
            self.inquiries_page.individualize_price(percent=excessive_discount, should_check_price=False, should_save_discount=False)

            error_message_text = self.product_edit_form.SUBSCRIPTION_FEE_DISCOUNT_ERROR.text
            assert_that(
                lambda: "Допустимое значение от 0 до 100" in error_message_text,
                f"Сообщение об ошибке не соответствует ожидаемому. Ожидалось: 'Допустимое значение от 0 до 100'. Получено: {error_message_text}",
            )

            self.product_edit_form.SUBSCRIPTION_FEE_FINAL_PRICE.wait_to_be_visible(timeout=2000)
            final_price_text = self.product_edit_form.SUBSCRIPTION_FEE_FINAL_PRICE.text
            final_price, _ = get_price_and_currency(final_price_text)
            assert_that(lambda: final_price >= 0, f"Итоговая цена стала отрицательной: {final_price}")
            assert_that(
                lambda: final_price <= original_subscription_fee,
                f"Итоговая цена превышает исходную цену при скидке {excessive_discount}%: {final_price} > {original_subscription_fee}",
            )

        with allure.step("Шаг 4: Ввод итоговой цены, превышающей исходную, и проверка сохранения"):
            excessive_final_price = original_subscription_fee * 2
            self.product_edit_form.SUBSCRIPTION_FEE_FINAL_PRICE.fill(str(excessive_final_price))
            self.inquiries_page.save_individualized_prices()

            self.inquiries_page.check_individualized_price_in_inquiry(
                product_index=0,
                fee_type="subscription",
                expected_base_price=original_subscription_fee,
                expected_final_price=excessive_final_price,
            )

        with allure.step("Шаг 5: Проверка конфигурации и завершение продажи"):
            self.inquiries_page.check_configuration()

            self.inquiries_page.locators.NEXT_STEP_BTN.click()
            self.inquiries_page.wait_connect_package_offers_and_close_inquiry(
                auto_create_agreement=False, generate_documents=False
            )

        with allure.step("Шаг 6: Пополнение счета и переход в продукты клиента"):
            payment_amount = excessive_final_price
            account_id = self.client.agreements[0].accounts[0].id
            self.payment_api.create_default_payment(account_id, payment_amount)
            self.personal_account_api.wait_check_current_main_balance(account_id, payment_amount)
            self.personal_account_api.wait_accruals(test_context.client.user_id)

            self.base_page.open(
                f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/products"
            )
            self.client_profile.locators.PRODUCTS_LIST.wait_to_be_visible(timeout=15000)
            self.client_profile.locators.PRODUCTS.wait_to_have_count(1, timeout=15000)

        with allure.step("Шаг 7: Проверка статуса продукта и индивидуализированной цены"):
            self.client_profile.check_individualized_price_on_products_page(
                product_index=0,
                fee_type="subscription",
                expected_base_price=original_subscription_fee,
                expected_final_price=excessive_final_price,
            )

        with allure.step("Шаг 8: Переход в детали потребления и проверка начислений"):
            self.client_profile.open_product_consumption_details()

            self.consumption_page.click_tab("Начисления")
            self.consumption_page.check_accrual_amount(excessive_final_price, index=0)
