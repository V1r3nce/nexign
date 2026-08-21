import allure
import pytest

from api.nbss.client_requests.client_requests import ClientRequests
from common.helpers.env_helper import BASE_URL
from models.client import OrganizationClient
from models.context import test_context
from models.inquiry import prepare_inquiries
from pages.base_page import BasePage
from pages.locators.nbss.select_product_offers_form import SelectProductOffersFormElements
from pages.nbss.client.client_product_profile_page import ClientProductProfilePage
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.inquiries_page import InquiriesPage


@allure.epic("E2E_62 Продажа клиенту B2B")
@allure.suite("E2E_62 Продажа клиенту B2B")
@pytest.mark.regress
@pytest.mark.nbss_portal
@pytest.mark.praim
class TestSellB2BClient:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login, create_organization: OrganizationClient) -> None:
        self.base_page = BasePage()
        self.inquiries_page = InquiriesPage()
        self.client_profile_page = ClientProfilePage()
        self.client_product_profile = ClientProductProfilePage()
        self.product_offer = SelectProductOffersFormElements()
        self.client_request_api = ClientRequests()
        self.client = create_organization
        self.client_request_api.create_linked_person(test_context.client.user_id, "Тест связанное лицо")

    @allure.title('Продажа "бандл" продукта B2B клиенту с ручным созданием договора и ЛС')
    @allure.id(533492)
    def test_selling_bundle_b2b_product_client_manual_creation_agreement(self, base_url: str) -> None:
        self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")
        self.inquiries_page.sale_bundle()
        self.client_product_profile.open_products_page_and_check(
            user_id=test_context.client.user_id,
            product_list=test_context.client.inquiry.product_list,
            is_activated=False,
        )

    @allure.title('Продажа "моно" продукта B2B клиенту с ручным созданием договора и ЛС')
    @allure.id(539223)
    @pytest.mark.smoke
    @pytest.mark.sanity
    def test_selling_mono_b2b_product_client_manual_creation_agreement(self) -> None:
        self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")
        self.inquiries_page.sale_initialization(
            self.client, need_contact_data=True, priority="Высокий", add_kp="no", create_add_agreement="manual"
        )
        prepare_inquiries(category="mobile")
        test_context.client.inquiry.product.product_name = "Гибкий бизнес"
        product = self.inquiries_page.add_product_offer_to_commercial_order(test_context.client.inquiry.product)
        test_context.client.inquiry.product = product
        self.inquiries_page.auto_reserve_all_resources(product.category)
        self.inquiries_page.check_configuration()
        self.inquiries_page.click_next("Регистрация/Выбор договора")
        self.inquiries_page.agreement_and_account_steps_pass()
        self.inquiries_page.wait_close_inquiry()
        self.client_product_profile.open_products_page_and_check(
            user_id=test_context.client.user_id,
            product_list=test_context.client.inquiry.product_list,
            is_activated=False,
        )
