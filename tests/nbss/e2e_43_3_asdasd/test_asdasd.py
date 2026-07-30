import allure
import pytest

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from api.nbss.personal_account_requests import PersonalAccountRequests
from common.helpers.env_helper import BASE_URL
from models.client import OrganizationClient
from models.context import test_context
from pages.base_page import BasePage
from pages.nbss.client.client_product_profile_page import ClientProductProfilePage
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.inquiries_page import InquiriesPage
from pages.nbss.inquiry_order_structure_management_page import InquiryOrderStructureManagement


@allure.epic("E2E_62 Продажа клиенту B2B")
@allure.suite("E2E_62_29 продажа клиенту B2B (Подключение/Изменение/Отключение продуктов будущей датой)")
@pytest.mark.regress
@pytest.mark.nbss_portal
class Testasdasd:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login: None, create_organization: OrganizationClient) -> None:
        self.base_page = BasePage()
        self.client_profile = ClientProfilePage()
        self.client_product_profile = ClientProductProfilePage()
        self.inquiries_page = InquiriesPage()
        self.order_structure = InquiryOrderStructureManagement()
        self.client_inquiries_requests = ClientInquiriesRequests()
        self.personal_account_api = PersonalAccountRequests()
        self.PRODUCT_CURRENT = "Терминал L"
        self.PRODUCT_TYPE = "Товары и оборудование"

    @allure.id(890120)
    @allure.title("01. Создание заявки на подключение продукта текущей датой")
    def test_create_inquiry_current_date(self) -> None:
        with allure.step("Создание заявки продажи"):
            self.base_page.open(
                f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/overview"
            )
            self.inquiries_page.sale_initialization(add_kp="auto")
        with allure.step("Выбор продуктовых предложений"):
            self.inquiries_page.locators.ADD_SALE_BTN.click()
            self.inquiries_page.find_product_in_form(
                product_offer_name=self.PRODUCT_CURRENT, product_category_name=self.PRODUCT_TYPE
            )

        with allure.step("Завершить продажу текущей датой"):
            self.inquiries_page.auto_reserve_all_resources("mobile")
            self.inquiries_page.check_configuration()
            self.inquiries_page.locators.NEXT_STEP_BTN.click()
