import allure
import pytest
from playwright.sync_api import APIRequestContext, Page

from common.helpers.env_helper import BASE_URL
from models.context import test_context
from models.inquiry import prepare_inquiries
from models.product import ProductInfo
from pages.base_page import BasePage
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.inquiries_page import InquiriesPage


@allure.epic("Общие бизнес-процессы")
@allure.suite("Общие бизнес-процессы")
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestCommonBusinessProcessesB2B:
    @pytest.fixture(autouse=True)
    def setup(
        self,
        nexign_ui_stand_login: Page,
        api_request_context: APIRequestContext,
        create_organization,
    ) -> None:
        self.base_page = BasePage(nexign_ui_stand_login)
        self.client = create_organization
        self.inquiries_page = InquiriesPage(nexign_ui_stand_login)
        self.client_profile_page = ClientProfilePage(nexign_ui_stand_login)

    @allure.title(
        "Продажа оборудования как независимого продукта существующему клиенту, формирование и согласование документов вручную/ поиск по наименованию / клиент существует"
    )
    @allure.id(738808)
    def test_equipment_sale(self):
        self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{self.client.user_id}/overview")
        self.inquiries_page.sale_initialization(
            self.client, need_contact_data=True, priority="Высокий", add_kp="no", create_add_agreement="manual"
        )
        product = ProductInfo(product_category="satellite", product_name="Спутник L Продажа")
        product = self.inquiries_page.add_product_offer_to_commercial_order(product)
        prepare_inquiries(category="satellite")
        test_context.client.inquiry.product = product
        self.inquiries_page.auto_reserve_all_resources(product.category)
        self.inquiries_page.check_configuration()
        self.inquiries_page.click_next("Регистрация/Выбор договора")
        self.inquiries_page.agreement_and_account_steps_pass()
        self.inquiries_page.wait_close_inquiry()
        self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/products")
        self.client_profile_page.check_all_products([test_context.client.inquiry.product], is_activated=False)

    @allure.title(
        "Аренда оборудования как независимого продукта существующему клиенту, формирование и согласование документов вручную/ поиск по наименованию / клиент существует"
    )
    @allure.id(738242)
    def test_equipment_rent(self):
        self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{self.client.user_id}/overview")
        self.inquiries_page.sale_initialization(
            self.client, need_contact_data=True, priority="Высокий", add_kp="no", create_add_agreement="manual"
        )
        product = ProductInfo(product_category="satellite", product_name="Спутник L Аренда")
        product = self.inquiries_page.add_product_offer_to_commercial_order(product)
        prepare_inquiries(category="satellite")
        test_context.client.inquiry.product = product
        self.inquiries_page.auto_reserve_all_resources(product.category)
        self.inquiries_page.check_configuration()
        self.inquiries_page.click_next("Регистрация/Выбор договора")
        self.inquiries_page.agreement_and_account_steps_pass()
        self.inquiries_page.wait_close_inquiry()
        self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/products")
        self.client_profile_page.check_all_products([test_context.client.inquiry.product], is_activated=False)
