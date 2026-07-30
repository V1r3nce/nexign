import allure
import pytest

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from api.nbss.finances.payments_requests import PaymentsRequests
from api.nbss.personal_account_requests import PersonalAccountRequests
from common.helpers.env_helper import BASE_URL
from models.client import OrganizationClient
from models.context import test_context
from models.inquiry import prepare_inquiries
from models.product import B2BProducts, product_names_map
from pages.base_page import BasePage
from pages.locators.nbss.dynamic_form_elements import CreateSalesAndServiceManagement
from pages.nbss.client.client_product_profile_page import ClientProductProfilePage
from pages.nbss.inquiries_page import InquiriesPage
from pages.nbss.inquiry_order_structure_management_page import InquiryOrderStructureManagement


@allure.epic("E2E_43 Подключение пакетных предложений")
@allure.suite(
    "E2E_43_3 Подключение пакетных предложений "
    "(Применение различных схем списаний абонентской платы и выдачи новых объемов клиенту)"
)
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestDisplayTaxesDuringSale:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login, create_organization_with_agreement_and_account: OrganizationClient) -> None:
        self.base_page = BasePage()
        self.inquiries_page = InquiriesPage()
        self.order_structure = InquiryOrderStructureManagement()
        self.client_product_profile = ClientProductProfilePage()
        self.client_inquiries_requests = ClientInquiriesRequests()
        self.personal_account_api = PersonalAccountRequests()
        self.payment_api = PaymentsRequests()
        self.create_request_form = CreateSalesAndServiceManagement()
        self.client = create_organization_with_agreement_and_account
        self.discount_percent = 20
        self.PRODUCT_RENT = product_names_map[B2BProducts.satellite_rent]
        self.PRODUCT_SALE = product_names_map[B2BProducts.equipment_sale]
        self.OPTION_NAME = "+2 ГБ"

    @allure.step("Создать заявку на продажу и перейти на шаг 'Управление составом заказа'")
    def create_sale_inquiry(self) -> None:
        self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")
        self.inquiries_page.sale_initialization(
            self.client,
            agreement=self.client.agreements[0].number,
            account=self.client.agreements[0].accounts[0].number,
            add_kp="no",
            create_add_agreement="auto",
        )
        self.inquiries_page.locators.ADD_SALE_BTN.wait_to_be_visible(timeout=60000)
        self.inquiries_page.locators.INQUIRY_STEP.wait_to_have_text("Управление составом заказа", timeout=30000)

    @allure.step("Подготовить клиенту активный мобильный продукт через API")
    def prepare_active_mobile_product(self) -> None:
        inquiry = self.client_inquiries_requests.product_sale(
            inquiry=prepare_inquiries(category=["mobile"], product_offering_id=[B2BProducts.mobile], as_list=False)
        )
        account_id = test_context.client.agreements[0].accounts[0].id
        self.payment_api.create_default_payment(
            account_id, inquiry.product.one_time_payment + inquiry.product.subscription_fee + 100
        )
        self.personal_account_api.wait_check_current_main_balance(account_id, 100)

    @allure.id(885693)
    @allure.title("01. Проверка отображения налога при продаже с индивидуализацией")
    def test_display_taxes_with_price_individualization(self) -> None:
        with allure.step("Создание заявки продажи"):
            self.create_sale_inquiry()

        with allure.step("Выбор продуктовых предложений и проверка налога в детальной информации о продукте"):
            test_context.client.inquiry = prepare_inquiries(category=["satellite_rent", "equipment_sale"], as_list=False)
            products = {product.product_name: product for product in test_context.client.inquiry.product_list}

            self.inquiries_page.locators.ADD_SALE_BTN.click()
            self.inquiries_page.search_products_in_form(
                product_offer_name=self.PRODUCT_RENT, product_category_name="Спутниковая связь"
            )
            self.inquiries_page.check_product_details_taxes(product_offer_name=self.PRODUCT_RENT)
            self.inquiries_page.add_found_product_to_commercial_order(products[self.PRODUCT_RENT])

            self.inquiries_page.add_product_offer_to_commercial_order(products[self.PRODUCT_SALE])
            products[self.PRODUCT_RENT].switch_name = "Коммутатор_Спутниковая_связь"
            products[self.PRODUCT_SALE].switch_name = "Коммутатор_Спутниковая_связь"

        with allure.step("Проверка налога во всплывающих подсказках 'Итого' до применения скидки"):
            self.inquiries_page.check_total_payment_tax_tooltip(fee_type="one_time")
            self.inquiries_page.check_total_payment_tax_tooltip(fee_type="subscription")

        with allure.step("Проверка отображения налога на форме 'Назначение скидок'"):
            self.inquiries_page.open_mass_discount_assignment_form()
            self.inquiries_page.check_taxes_in_mass_discount_form(
                product_offering_id=B2BProducts.equipment_sale, fee_type="one_time"
            )
            self.inquiries_page.check_taxes_in_mass_discount_form(
                product_offering_id=B2BProducts.satellite_rent, fee_type="subscription"
            )

        with allure.step("Назначить скидки продуктам заказа"):
            self.inquiries_page.fill_discounts_on_mass_discount_assignment_form([self.discount_percent])
            self.inquiries_page.fill_one_time_discounts_on_mass_discount_assignment_form([self.discount_percent])
            self.inquiries_page.save_discounts_on_mass_discount_assignment_form()

        with allure.step("Проверка налога во всплывающих подсказках 'Итого' после применения скидки"):
            self.inquiries_page.check_total_payment_tax_tooltip(fee_type="one_time")
            self.inquiries_page.check_total_payment_tax_tooltip(fee_type="subscription")

        with allure.step("Проверка пересчитанного налога на вкладке 'Цены' формы редактирования продуктов"):
            self.inquiries_page.open_product_price_tab_by_price_link(fee_type="subscription")
            self.inquiries_page.check_taxes_on_price_tab(fee_type="subscription")
            self.inquiries_page.close_edit_product_form()

            self.inquiries_page.open_product_price_tab_by_price_link(fee_type="one_time")
            self.inquiries_page.check_taxes_on_price_tab(fee_type="one_time")
            self.inquiries_page.close_edit_product_form()

        with allure.step("Завершение продажи"):
            self.inquiries_page.auto_reserve_all_resources(
                [products[self.PRODUCT_RENT].category, products[self.PRODUCT_SALE].category]
            )
            self.inquiries_page.check_configuration()
            self.inquiries_page.locators.NEXT_STEP_BTN.click()
            self.inquiries_page.wait_connect_package_offers_and_close_inquiry(
                auto_create_agreement=False, generate_documents=False
            )

        with allure.step("Проверка отображения налога в продуктовом профиле клиента"):
            self.client_product_profile.open_products_page(
                user_id=test_context.client.user_id,
                product_list=test_context.client.inquiry.product_list,
                is_activated=False,
            )
            self.client_product_profile.check_taxes_on_product_sidebar()

    @allure.id(885691)
    @allure.title("02. Проверка отображения налога при продаже без индивидуализации")
    def test_display_taxes_without_price_individualization(self) -> None:
        with allure.step("Создание заявки продажи"):
            self.create_sale_inquiry()

        with allure.step("Выбор ПП: проверка налога на вкладке 'Цены' детальной информации о продукте"):
            test_context.client.inquiry = prepare_inquiries(category=["equipment_sale"], as_list=False)
            product = test_context.client.inquiry.product

            self.inquiries_page.locators.ADD_SALE_BTN.click()
            self.inquiries_page.search_products_in_form(
                product_offer_name=self.PRODUCT_SALE, product_category_name="Товары и оборудование"
            )
            self.inquiries_page.check_product_details_taxes(product_offer_name=self.PRODUCT_SALE)

        with allure.step("Добавить продуктовое предложение в коммерческий заказ"):
            self.inquiries_page.add_found_product_to_commercial_order(product)

        with allure.step("Проверка налога во всплывающих подсказках 'Итого'"):
            self.inquiries_page.check_total_payment_tax_tooltip(fee_type="one_time")

        with allure.step("Проверка налога на вкладке 'Цены' формы редактирования продукта"):
            self.inquiries_page.open_product_price_tab_by_price_link(fee_type="one_time")
            self.inquiries_page.check_taxes_on_price_tab(fee_type="one_time")
            self.inquiries_page.close_edit_product_form()

        with allure.step("Завершение продажи"):
            self.inquiries_page.auto_reserve_all_resources(product.category)
            self.inquiries_page.check_configuration()
            self.inquiries_page.locators.NEXT_STEP_BTN.click()
            self.inquiries_page.wait_connect_package_offers_and_close_inquiry(
                auto_create_agreement=False, generate_documents=False
            )

        with allure.step("Проверка отображения налога в продуктовом профиле клиента"):
            self.client_product_profile.open_products_page(
                user_id=test_context.client.user_id,
                product_list=test_context.client.inquiry.product_list,
                is_activated=False,
            )
            self.client_product_profile.check_taxes_on_product_sidebar()

    @allure.id(885692)
    @allure.title("03. Проверка отображения налога при продаже доп. продукта")
    def test_display_taxes_for_additional_product(self) -> None:
        with allure.step("Подготовка: продажа основного продукта клиенту через API"):
            self.prepare_active_mobile_product()

        with allure.step("Создание заявки на подключение опции"):
            self.client_product_profile.open_products_page(
                user_id=test_context.client.user_id, product_list=test_context.client.inquiry.product_list
            )
            self.client_product_profile.add_adoption_product(self.OPTION_NAME)
            self.create_request_form.NEED_SPD.wait_to_be_visible(timeout=15000)
            self.create_request_form.SAVE_BTN.click()
            self.inquiries_page.locators.INQUIRY_STATUS.wait_to_have_text("Обрабатывается", timeout=30000)
            self.inquiries_page.locators.LOAD_SPINS.wait_not_to_be_visible(timeout=60000)

        with allure.step("Выполнение заявки: проверка налога у основного продукта"):
            self.order_structure.check_order_management_step()
            self.inquiries_page.open_product_price_tab_by_price_link(fee_type="subscription")
            self.inquiries_page.check_taxes_on_price_tab(fee_type="subscription")
            self.inquiries_page.close_edit_product_form()

        with allure.step("Завершение заявки на подключение опции"):
            self.inquiries_page.check_configuration()
            self.inquiries_page.locators.NEXT_STEP_BTN.click()
            self.inquiries_page.wait_connect_package_offers_and_close_inquiry(
                auto_create_agreement=False, generate_documents=False
            )

        with allure.step("Проверка отображения налога у опции в продуктовом профиле клиента"):
            self.client_product_profile.open_products_page(
                user_id=test_context.client.user_id, product_list=test_context.client.inquiry.product_list
            )
            self.client_product_profile.check_taxes_on_option_sidebar()
