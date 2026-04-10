from random import randint

import allure
import pytest

from api.exceptions import ExtractProductInfoException
from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from api.nbss.finances.billing_requests import BillingRequests
from api.nbss.finances.payments_requests import PaymentsRequests
from api.nbss.personal_account_requests import PersonalAccountRequests
from common.helpers.checker import check_that
from common.helpers.data_generator import calc_price_after_discount
from common.helpers.env_helper import BASE_URL
from models.context import test_context
from models.inquiry import prepare_inquiries
from models.product import B2BProducts, product_names_map
from pages.base_page import BasePage
from pages.locators.nbss.client.client_profile import ClientProfileElements
from pages.locators.nbss.dynamic_form_elements import CreateSalesAndServiceManagement
from pages.locators.nbss.inquiries_elements import ProductEditForm
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.finances.billing_accounts_page import BillingAccountsPage
from pages.nbss.finances.consumption_page import ConsumptionPage
from pages.nbss.inquiries_page import InquiriesPage


@allure.suite("E2E_03 Отключение ПП")
@pytest.mark.nbss_portal
@pytest.mark.regress
class TestRecalculationSubsFee:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login):
        self.client_inquiry_api = ClientInquiriesRequests()
        self.personal_account_api = PersonalAccountRequests()
        self.payment_api = PaymentsRequests()
        self.billing_api = BillingRequests()

        self.base_page = BasePage()
        self.client_profile_page = ClientProfilePage()
        self.inquiries_page = InquiriesPage()
        self.consumption_page = ConsumptionPage()
        self.billing_accounts_page = BillingAccountsPage()

        self.client_profile_elements = ClientProfileElements()
        self.product_edit_form = ProductEditForm()
        self.create_request_form = CreateSalesAndServiceManagement()

        self.individualize_percent = randint(10, 50)

    @allure.title("01. Перерасчёт АП с назначением скидки для подключенного продукта с RtUpdateс положительным балансом")
    @allure.id(815133)
    def test_recalc_subs_fee_discount(self, create_organization_with_agreement_and_account):
        with allure.step("Продажа продукта клиенту, ожидание его активации"):
            self.client_inquiry_api.product_sale(inquiry=prepare_inquiries(category="satellite_rent"))
            self.payment_api.create_default_payment(
                test_context.client.agreements[0].accounts[0].id, test_context.client.inquiry.product.total_amount
            )
            self.personal_account_api.wait_check_current_main_balance(
                test_context.client.agreements[0].accounts[0].id, 0
            )
            self.personal_account_api.wait_accruals(test_context.client.user_id)
        with allure.step("Переход на продуктовый профиль клиента, инициализация изменения стоимости"):
            self.base_page.open(
                f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/products"
            )
            self.client_profile_elements.PRODUCT_NAME.wait_to_be_visible(timeout=15000)
            self.client_profile_page.check_all_products(products=test_context.client.inquiry.product_list)

            self.client_profile_page.create_product_edit_inquiry()

        with allure.step("Ожидание создания заявки, создания КЗ"):
            self.inquiries_page.locators.INQUIRY_STATUS.wait_to_have_text("Обрабатывается", timeout=15000)
            self.inquiries_page.locators.INQUIRY_STEP.wait_to_have_text("Регистрация продажи", timeout=10000)
            self.inquiries_page.locators.INQUIRY_STEP.wait_to_have_text("Управление составом заказа", timeout=65000)

        self.inquiries_page.individualize_price(percent=self.individualize_percent)
        original_subs_fee = test_context.client.inquiry.product.subscription_fee
        expected_subscription = calc_price_after_discount(price=original_subs_fee, discount=self.individualize_percent)
        self.inquiries_page.check_individualized_price_in_inquiry(
            expected_subscription, original_subs_fee, fee_type="subscription"
        )

        self.inquiries_page.locators.CHECK_CONFIGURATION_BTN.wait_to_be_visible(timeout=15000)
        self.inquiries_page.check_configuration()

        with allure.step("Завершение продажи"):
            self.inquiries_page.locators.NEXT_STEP_BTN.wait_to_be_visible(timeout=10000)
            self.inquiries_page.locators.NEXT_STEP_BTN.click()
            self.inquiries_page.wait_connect_package_offers_and_close_inquiry(
                auto_create_agreement=True, generate_documents=True
            )

        with allure.step("Переход в продуктовый профиль клиента, проверка изменений"):
            self.base_page.open(
                f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/products"
            )
            self.client_profile_elements.PRODUCTS_LIST.wait_to_be_visible(timeout=15000)
            self.client_profile_elements.PRODUCTS.wait_to_have_count(1, timeout=10000)

            self.client_profile_page.check_individualized_subscription_fee_on_products_page(
                expected_subscription, original_subs_fee
            )

        with allure.step("Переход в начисления, проверка изменений"):
            self.base_page.open(
                f"{BASE_URL}customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
            )
            self.client_profile_elements.BURGER_MENU.select_by_value("Финансы > Потребление")

            self.consumption_page.open_accrual_list()
            self.consumption_page.check_refund_amount(
                product=test_context.client.inquiry.product,
                action="discount",
            )

    @allure.title("02. Перерасчёт АП при увеличении стоимости продукта с RtUpdate с положительным балансом")
    @allure.id(815228)
    def test_recalc_subs_fee_increase(self, create_organization_with_agreement_and_account):
        with allure.step("Продажа продукта клиенту, ожидание его активации"):
            self.client_inquiry_api.product_sale(inquiry=prepare_inquiries(category="satellite_rent"))
            self.payment_api.create_default_payment(
                test_context.client.agreements[0].accounts[0].id, test_context.client.inquiry.product.total_amount
            )
            self.personal_account_api.wait_check_current_main_balance(
                test_context.client.agreements[0].accounts[0].id, 0
            )
            self.personal_account_api.wait_accruals(test_context.client.user_id)
            original_subs_fee = test_context.client.inquiry.product.subscription_fee
            expected_subscription = calc_price_after_discount(
                price=original_subs_fee, discount=-self.individualize_percent
            )
            self.payment_api.create_default_payment(
                test_context.client.agreements[0].accounts[0].id, expected_subscription
            )
        with allure.step("Переход на продуктовый профиль клиента, инициализация изменения стоимости"):
            self.base_page.open(
                f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/products"
            )
            self.client_profile_elements.PRODUCT_NAME.wait_to_be_visible(timeout=15000)
            self.client_profile_page.check_all_products(products=test_context.client.inquiry.product_list)

            self.client_profile_page.create_product_edit_inquiry()

        with allure.step("Ожидание создания заявки, создания КЗ"):
            self.inquiries_page.locators.INQUIRY_STATUS.wait_to_have_text("Обрабатывается", timeout=15000)
            self.inquiries_page.locators.INQUIRY_STEP.wait_to_have_text("Регистрация продажи", timeout=10000)
            self.inquiries_page.locators.INQUIRY_STEP.wait_to_have_text("Управление составом заказа", timeout=65000)

        self.inquiries_page.individualize_price(final_price=expected_subscription)
        self.inquiries_page.check_individualized_price_in_inquiry(
            expected_subscription, original_subs_fee, fee_type="subscription"
        )

        self.inquiries_page.locators.CHECK_CONFIGURATION_BTN.wait_to_be_visible(timeout=15000)
        self.inquiries_page.check_configuration()

        with allure.step("Завершение продажи"):
            self.inquiries_page.locators.NEXT_STEP_BTN.wait_to_be_visible(timeout=10000)
            self.inquiries_page.locators.NEXT_STEP_BTN.click()
            self.inquiries_page.wait_connect_package_offers_and_close_inquiry(
                auto_create_agreement=True, generate_documents=True
            )

        with allure.step("Переход в продуктовый профиль клиента, проверка изменений"):
            self.base_page.open(
                f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/products"
            )
            self.client_profile_elements.PRODUCTS_LIST.wait_to_be_visible(timeout=15000)
            self.client_profile_elements.PRODUCTS.wait_to_have_count(1, timeout=10000)

            self.client_profile_page.check_individualized_subscription_fee_on_products_page(
                expected_subscription, original_subs_fee
            )

        with allure.step("Переход в начисления, проверка изменений"):
            self.base_page.open(
                f"{BASE_URL}customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
            )
            self.client_profile_elements.BURGER_MENU.select_by_value("Финансы > Потребление")

            self.consumption_page.open_accrual_list()
            self.consumption_page.check_refund_amount(product=test_context.client.inquiry.product, action="extra")

    @allure.title(
        "03. Перерасчёт АП с назначением скидки для подключенного продукта с trUpdate с отключенным Контролем Порога"
    )
    @allure.id(815245)
    def test_recalc_subs_fee_discount_postpaid_account(self, create_organization_with_postpaid_account):
        with allure.step("Продажа продукта клиенту, ожидание его активации"):
            self.client_inquiry_api.product_sale(inquiry=prepare_inquiries(category="satellite_rent"))
            self.payment_api.create_default_payment(
                test_context.client.agreements[0].accounts[0].id, test_context.client.inquiry.product.total_amount
            )
            self.personal_account_api.wait_check_current_main_balance(
                test_context.client.agreements[0].accounts[0].id, 0
            )
            self.personal_account_api.wait_accruals(test_context.client.user_id)
        with allure.step("Переход на продуктовый профиль клиента, инициализация изменения стоимости"):
            self.base_page.open(
                f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/products"
            )
            self.client_profile_elements.PRODUCT_NAME.wait_to_be_visible(timeout=15000)
            self.client_profile_page.check_all_products(products=test_context.client.inquiry.product_list)

            self.client_profile_page.create_product_edit_inquiry()

        with allure.step("Ожидание создания заявки, создания КЗ"):
            self.inquiries_page.locators.INQUIRY_STATUS.wait_to_have_text("Обрабатывается", timeout=15000)
            self.inquiries_page.locators.INQUIRY_STEP.wait_to_have_text("Регистрация продажи", timeout=10000)
            self.inquiries_page.locators.INQUIRY_STEP.wait_to_have_text("Управление составом заказа", timeout=65000)

        self.inquiries_page.individualize_price(percent=self.individualize_percent)
        original_subs_fee = test_context.client.inquiry.product.subscription_fee
        expected_subscription = calc_price_after_discount(price=original_subs_fee, discount=self.individualize_percent)
        self.inquiries_page.check_individualized_price_in_inquiry(
            expected_subscription, original_subs_fee, fee_type="subscription"
        )

        self.inquiries_page.locators.CHECK_CONFIGURATION_BTN.wait_to_be_visible(timeout=15000)
        self.inquiries_page.check_configuration()

        with allure.step("Завершение продажи"):
            self.inquiries_page.locators.NEXT_STEP_BTN.wait_to_be_visible(timeout=10000)
            self.inquiries_page.locators.NEXT_STEP_BTN.click()
            self.inquiries_page.wait_connect_package_offers_and_close_inquiry(
                auto_create_agreement=True, generate_documents=True
            )

        with allure.step("Переход в продуктовый профиль клиента, проверка изменений"):
            self.base_page.open(
                f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/products"
            )
            self.client_profile_elements.PRODUCTS_LIST.wait_to_be_visible(timeout=15000)
            self.client_profile_elements.PRODUCTS.wait_to_have_count(1, timeout=10000)

            self.client_profile_page.check_individualized_subscription_fee_on_products_page(
                expected_subscription, original_subs_fee
            )

        with allure.step("Переход в начисления, проверка изменений"):
            self.base_page.open(
                f"{BASE_URL}customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
            )
            self.client_profile_elements.BURGER_MENU.select_by_value("Финансы > Потребление")

            self.consumption_page.open_accrual_list()
            self.consumption_page.check_refund_amount(
                product=test_context.client.inquiry.product,
                action="discount",
            )

    @allure.title("05. Проведение внеочередного биллинга после отключения ПП")
    @allure.id(818338)
    def test_recalc_product_disconnect_billing(self, create_organization_with_agreement_and_account):
        with allure.step("Продажа продукта клиенту, ожидание его активации"):
            self.client_inquiry_api.product_sale(inquiry=prepare_inquiries(category="satellite_rent"))
            self.payment_api.create_default_payment(
                test_context.client.agreements[0].accounts[0].id, test_context.client.inquiry.product.total_amount
            )
            self.personal_account_api.wait_check_current_main_balance(
                test_context.client.agreements[0].accounts[0].id, 0
            )
            self.personal_account_api.wait_accruals(test_context.client.user_id)
        with allure.step(
            "Переход на продуктовый профиль клиента, инициализация отключения продукта, ожидание выполнения заявки"
        ):
            self.base_page.open(
                f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/products"
            )
            self.client_profile_elements.PRODUCT_NAME.wait_to_be_visible(timeout=15000)
            self.client_profile_page.check_all_products(products=test_context.client.inquiry.product_list)

            self.client_inquiry_api.product_disconnect()

        with allure.step("Переход в контекст ЛС, открытие 'Биллинговые счета'"):
            self.base_page.open(
                f"{BASE_URL}customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
            )
            balance = self.personal_account_api.get_current_main_balance(
                test_context.client.agreements[0].accounts[0].id
            )
            self.client_profile_elements.BURGER_MENU.select_by_value("Финансы > Биллинговые счета")

        with allure.step("Запуск внеочередного биллинга, проверка корректности"):
            self.billing_accounts_page.run_unscheduled_billing(test_context.client.agreements[0].accounts[0].number)
            self.billing_api.wait_finish_billing(
                self.billing_api.get_billing_profile_id(test_context.client.agreements[0].accounts[0].id)
            )

            self.billing_accounts_page.locators.REFRESH_BTN.click()
            self.billing_accounts_page.locators.ACCOUNT_NUMS_LIST.wait_to_have_count(1, timeout=10000)
            self.billing_accounts_page.locators.ACCOUNT_NUMS_LIST[0].click()
            expected_amount = test_context.client.inquiry.product.total_amount - balance
            self.billing_accounts_page.check_detail_adjusted_property(amount=expected_amount, accrued=True)

    @allure.title("06. Перерасчёт АП при замене ПП")
    @allure.id(815278)
    def test_recalc_product_change(self, create_organization_with_postpaid_account):
        with allure.step("Продажа продукта клиенту, ожидание его активации"):
            self.new_product_name = product_names_map.get(B2BProducts.satellite_rent_alt, None)
            check_that(lambda: self.new_product_name is not None, ExtractProductInfoException)
            self.client_inquiry_api.product_sale(inquiry=prepare_inquiries(category="satellite_rent"))
            self.payment_api.create_default_payment(
                test_context.client.agreements[0].accounts[0].id, test_context.client.inquiry.product.total_amount
            )
            self.personal_account_api.wait_check_current_main_balance(
                test_context.client.agreements[0].accounts[0].id, 0
            )
            self.personal_account_api.wait_accruals(test_context.client.user_id)
        with allure.step("Переход на продуктовый профиль клиента, инициализация смены продукта"):
            self.base_page.open(
                f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/products"
            )
            self.client_profile_elements.PRODUCT_NAME.wait_to_be_visible(timeout=15000)
            self.client_profile_page.check_all_products(products=test_context.client.inquiry.product_list)

            self.client_profile_page.change_product_offer_with_contract(product_name=self.new_product_name)

        with allure.step("Ожидание создания заявки, создания КЗ"):
            self.inquiries_page.locators.INQUIRY_STATUS.wait_to_have_text("Обрабатывается", timeout=15000)
            self.inquiries_page.locators.INQUIRY_STEP.wait_to_have_text("Регистрация продажи", timeout=10000)
            self.inquiries_page.locators.INQUIRY_STEP.wait_to_have_text("Управление составом заказа", timeout=65000)

        with allure.step("Завершение продажи"):
            self.inquiries_page.locators.NEXT_STEP_BTN.wait_to_be_visible(timeout=10000)
            self.inquiries_page.locators.NEXT_STEP_BTN.click()
            self.inquiries_page.wait_connect_package_offers_and_close_inquiry(
                auto_create_agreement=True, generate_documents=True
            )

        with allure.step("Переход в продуктовый профиль клиента, проверка изменений"):
            self.base_page.open(
                f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/products"
            )
            self.client_profile_elements.PRODUCTS_LIST.wait_to_be_visible(timeout=15000)
            self.client_profile_elements.PRODUCTS.wait_to_have_count(1, timeout=10000)

        with allure.step("Переход в начисления, проверка изменений"):
            self.base_page.open(
                f"{BASE_URL}customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
            )
            self.client_profile_elements.BURGER_MENU.select_by_value("Финансы > Потребление")

            self.consumption_page.open_accrual_list()
            self.consumption_page.check_refund_amount(product=test_context.client.inquiry.product, action="disconnect")

    @allure.title("07. Перерасчёт АП при отключении ПП")
    @allure.id(815282)
    def test_recalc_product_disconnect(self, create_organization_with_agreement_and_account):
        with allure.step("Продажа продукта клиенту, ожидание его активации"):
            self.client_inquiry_api.product_sale(inquiry=prepare_inquiries(category="satellite_rent"))
            self.payment_api.create_default_payment(
                test_context.client.agreements[0].accounts[0].id, test_context.client.inquiry.product.total_amount
            )
            self.personal_account_api.wait_check_current_main_balance(
                test_context.client.agreements[0].accounts[0].id, 0
            )
            self.personal_account_api.wait_accruals(test_context.client.user_id)
        with allure.step("Переход на продуктовый профиль клиента, инициализация отключения продукта"):
            self.base_page.open(
                f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/products"
            )
            self.client_profile_elements.PRODUCT_NAME.wait_to_be_visible(timeout=15000)
            self.client_profile_page.check_all_products(products=test_context.client.inquiry.product_list)

            self.client_profile_page.create_product_disconnect_inquiry(test_context.client.inquiry.product)
            disconnect_inquiry_id = self.client_inquiry_api._get_nth_inquiry(test_context.client.user_id, seq_number=2)
            self.client_inquiry_api.product_disconnect(existing_inquiry_id=disconnect_inquiry_id)

        with allure.step("Проверка отключения продукта"):
            self.client_profile_elements.PRODUCTS_UPDATE_BTN.click()
            self.client_profile_elements.PRODUCTS.wait_to_have_count(0, timeout=15000)

        with allure.step("Переход в начисления, проверка изменений"):
            self.base_page.open(
                f"{BASE_URL}customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
            )
            self.client_profile_elements.BURGER_MENU.select_by_value("Финансы > Потребление")

            self.consumption_page.open_accrual_list()
            self.consumption_page.check_refund_amount(product=test_context.client.inquiry.product, action="disconnect")

    @allure.title("08. Перерасчёт АП при замене ПП при недостатке средств")
    @allure.id(816916)
    def test_recalc_product_change_postpaid(self, create_organization_with_postpaid_account):
        with allure.step("Продажа продукта клиенту, ожидание его активации"):
            self.new_product_name = product_names_map.get(B2BProducts.satellite_rent_alt, None)
            check_that(lambda: self.new_product_name is not None, ExtractProductInfoException)
            self.client_inquiry_api.product_sale(inquiry=prepare_inquiries(category="satellite_rent"))
            self.personal_account_api.wait_check_current_main_balance(
                test_context.client.agreements[0].accounts[0].id, -test_context.client.inquiry.product.total_amount
            )
            self.personal_account_api.wait_accruals(test_context.client.user_id)
        with allure.step("Переход на продуктовый профиль клиента, инициализация смены продукта"):
            self.base_page.open(
                f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/products"
            )
            self.client_profile_elements.PRODUCT_NAME.wait_to_be_visible(timeout=15000)
            self.client_profile_page.check_all_products(products=test_context.client.inquiry.product_list)

            self.client_profile_page.change_product_offer_with_contract(product_name=self.new_product_name)

        with allure.step("Ожидание создания заявки, создания КЗ"):
            self.inquiries_page.locators.INQUIRY_STATUS.wait_to_have_text("Обрабатывается", timeout=15000)
            self.inquiries_page.locators.INQUIRY_STEP.wait_to_have_text("Регистрация продажи", timeout=10000)
            self.inquiries_page.locators.INQUIRY_STEP.wait_to_have_text("Управление составом заказа", timeout=65000)

        with allure.step("Завершение продажи"):
            self.inquiries_page.locators.NEXT_STEP_BTN.wait_to_be_visible(timeout=10000)
            self.inquiries_page.locators.NEXT_STEP_BTN.click()
            self.inquiries_page.wait_connect_package_offers_and_close_inquiry(
                auto_create_agreement=True, generate_documents=True
            )

        with allure.step("Переход в продуктовый профиль клиента, проверка изменений"):
            self.base_page.open(
                f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/products"
            )
            self.client_profile_elements.PRODUCTS_LIST.wait_to_be_visible(timeout=15000)
            self.client_profile_elements.PRODUCTS.wait_to_have_count(1, timeout=10000)

        with allure.step("Переход в начисления, проверка изменений"):
            self.base_page.open(
                f"{BASE_URL}customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
            )
            self.client_profile_elements.BURGER_MENU.select_by_value("Финансы > Потребление")

            self.consumption_page.open_accrual_list()
            self.consumption_page.check_refund_amount(product=test_context.client.inquiry.product, action="disconnect")
