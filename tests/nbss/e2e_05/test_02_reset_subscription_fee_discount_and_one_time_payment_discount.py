import allure
import pytest

from api.nbss.finances.payments_requests import PaymentsRequests
from api.nbss.personal_account_requests import PersonalAccountRequests
from common.helpers.data_generator import calc_price_after_discount
from common.helpers.env_helper import BASE_URL
from common.helpers.pdf_helper import check_text_in_pdf
from models.client import OrganizationClient
from models.context import test_context
from models.inquiry import prepare_inquiries
from models.product import B2BProducts, product_names_map
from pages.base_page import BasePage
from pages.locators.nbss.inquiries_elements import ProductEditForm
from pages.nbss.client.client_product_profile_page import ClientProductProfilePage
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.finances.consumption_page import ConsumptionPage
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
        self.consumption_page = ConsumptionPage()

        self.payment_api = PaymentsRequests()
        self.personal_account_api = PersonalAccountRequests()

        self.client = create_organization_with_agreement_and_account

    @allure.title("02. Сброс индивидуализации абонентской платы и разового списания на продукте клиента")
    @allure.id(703127)
    def test_reset_subscription_fee_discount_and_one_time_discount(self) -> None:
        discount_percent = 20
        product_name_rent = product_names_map.get(B2BProducts.satellite_rent)
        product_name_sale = product_names_map.get(B2BProducts.equipment_sale)

        self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")
        self.inquiries_page.sale_initialization(
            self.client,
            need_contact_data=True,
            agreement=self.client.agreements[0].number,
            account=self.client.agreements[0].accounts[0].number,
            priority="Высокий",
            add_kp="auto",
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
        expected_subscription_fee = calc_price_after_discount(original_subscription_fee, discount_percent)
        expected_one_time_price = calc_price_after_discount(original_one_time_price, discount_percent)

        self.inquiries_page.individualize_price(percent=discount_percent, fee_type="subscription")
        self.inquiries_page.individualize_price(percent=discount_percent, fee_type="one_time")

        self.inquiries_page.check_individualized_price_in_inquiry(
            product_index=0,
            fee_type="subscription",
            expected_base_price=original_subscription_fee,
            expected_final_price=expected_subscription_fee,
        )
        self.inquiries_page.check_individualized_price_in_inquiry(
            product_index=1,
            fee_type="one_time",
            expected_base_price=original_one_time_price,
            expected_final_price=expected_one_time_price,
        )
        self.inquiries_page.check_total_fields(expected_one_time_price, expected_subscription_fee)

        self.inquiries_page.individualize_price(percent=0, fee_type="subscription")
        self.inquiries_page.individualize_price(percent=0, fee_type="one_time")

        self.inquiries_page.check_product_individualized_price(
            price_index=0, fee_type="subscription", expected_price=original_subscription_fee
        )
        self.inquiries_page.check_product_individualized_price(
            price_index=0, fee_type="one_time", expected_price=original_one_time_price
        )
        self.inquiries_page.check_total_fields(original_one_time_price, original_subscription_fee)

        self.inquiries_page.auto_reserve_all_resources(
            [products[product_name_rent].category, products[product_name_sale].category]
        )
        self.inquiries_page.check_configuration()
        self.inquiries_page.locators.NEXT_STEP_BTN.click()
        self.inquiries_page.wait_connect_package_offers_and_close_inquiry(
            auto_create_agreement=False, generate_documents=False
        )

        self.inquiries_page.open_tab("Документы")
        pdf_file, path = self.inquiries_page.download_document("Коммерческое предложение")
        check_text_in_pdf(path=path, search_string="СпутникLАренда", expected_texts=[" 0,00 ", "50 000,00"])

        payment_amount = original_subscription_fee + original_one_time_price
        account_id = self.client.agreements[0].accounts[0].id
        self.payment_api.create_default_payment(account_id, payment_amount)
        self.personal_account_api.wait_check_current_main_balance(account_id, 0)
        self.personal_account_api.wait_accruals(test_context.client.user_id)

        self.client_product_profile.open_products_page(
            user_id=test_context.client.user_id, product_list=test_context.client.inquiry.product_list, is_activated=True
        )

        self.client_product_profile.check_product_price(
            product_index=0, fee_type="subscription", expected_price=original_subscription_fee
        )
        self.client_product_profile.check_product_price(
            product_index=1, fee_type="one_time", expected_price=original_one_time_price
        )

        self.client_profile.click_tab("Потребление")
        self.consumption_page.open_accrual_list()
        self.consumption_page.check_accrual_amount(expected_amount=original_subscription_fee, index=0)
        self.consumption_page.locators.SUBSCRIBER_SWITCH.click(1)
        self.consumption_page.check_accrual_amount(expected_amount=original_one_time_price, index=0)
