import allure
import pytest

from common.helpers.env_helper import BASE_URL
from models.context import test_context
from models.inquiry import prepare_inquiries
from pages.base_page import BasePage
from pages.nbss.client.client_product_profile_page import ClientProductProfilePage
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.inquiries_page import InquiriesPage


@allure.epic("Общие бизнес-процессы")
@allure.suite("Общие бизнес-процессы")
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestCommonBusinessProcessesB2B:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login, create_organization) -> None:
        self.base_page = BasePage()
        self.client = create_organization
        self.inquiries_page = InquiriesPage()
        self.client_profile_page = ClientProfilePage()
        self.client_product_profile = ClientProductProfilePage()

    @allure.title(
        "Продажа оборудования как независимого продукта существующему клиенту, формирование и согласование документов вручную/ поиск по наименованию / клиент существует"
    )
    @allure.id(738808)
    @pytest.mark.sanity
    def test_equipment_sale(self):
        self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{self.client.user_id}/overview")
        self.inquiries_page.sale_initialization(
            self.client, need_contact_data=True, priority="Высокий", add_kp="no", create_add_agreement="manual"
        )
        test_context.client.inquiry_list = prepare_inquiries(category="satellite_sale")
        self.inquiries_page.add_product_offer_to_commercial_order(test_context.client.inquiry.product)
        self.inquiries_page.auto_reserve_all_resources(test_context.client.inquiry.product.category)
        self.inquiries_page.check_configuration()
        self.inquiries_page.click_next("Регистрация/Выбор договора")
        self.inquiries_page.agreement_and_account_steps_pass()
        self.inquiries_page.wait_close_inquiry()
        self.client_product_profile.open_products_page_and_check(
            user_id=test_context.client.user_id,
            product_list=test_context.client.inquiry.product_list,
            is_activated=False,
        )

    @allure.title(
        "Аренда оборудования как независимого продукта существующему клиенту, формирование и согласование документов вручную/ поиск по наименованию / клиент существует"
    )
    @allure.id(738242)
    @pytest.mark.sanity
    def test_equipment_rent(self):
        self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{self.client.user_id}/overview")
        self.inquiries_page.sale_initialization(
            self.client, need_contact_data=True, priority="Высокий", add_kp="no", create_add_agreement="manual"
        )
        test_context.client.inquiry_list = prepare_inquiries(category="satellite_rent")
        self.inquiries_page.add_product_offer_to_commercial_order(test_context.client.inquiry.product)
        self.inquiries_page.auto_reserve_all_resources(test_context.client.inquiry.product.category)
        self.inquiries_page.check_configuration()
        self.inquiries_page.click_next("Регистрация/Выбор договора")
        self.inquiries_page.agreement_and_account_steps_pass()
        self.inquiries_page.wait_close_inquiry()
        self.client_product_profile.open_products_page_and_check(
            user_id=test_context.client.user_id,
            product_list=test_context.client.inquiry.product_list,
            is_activated=False,
        )
