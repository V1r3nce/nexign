import allure
import pytest

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from api.nbss.client_requests.client_requests import ClientRequests
from common.enums.user import User
from common.helpers.data_generator import get_datetime_beginning_of_day
from models.client import OrganizationClient
from models.context import test_context
from models.inquiry import prepare_inquiries
from models.product import B2BProducts
from pages.base_page import BasePage
from pages.nbss.client.client_product_profile_page import ClientProductProfilePage
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.inquiries_page import InquiriesPage


@pytest.mark.user(User.CUSTOMER_CARE_TEST)
@pytest.mark.regress
@pytest.mark.nbss_portal
@allure.epic("E2E_62 Продажа клиенту B2B")
@allure.suite("E2E_62 Продажа клиенту B2B")
class TestEditProductActivationDateAfterSaleFinishRoleAbsence:
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

        self.client_requests = ClientRequests()
        self.client_inquiries_requests = ClientInquiriesRequests()

        self.client = create_organization_with_agreement_and_account
        self.mobile_on_date_offer_id = B2BProducts.mobile_on_date
        self.product_category = "mobile"

        self.client_inquiries_requests = ClientInquiriesRequests()
        self.activation_date = get_datetime_beginning_of_day(shift="+1d", time_zone="Europe/Moscow")

    @allure.title("04. Изменение даты активации продукта после завершения продажи (нет роли)")
    @allure.id(757488)
    def test_edit_product_activation_date_after_sale_finish_role_absence(self) -> None:
        self.client_inquiries_requests.product_sale(
            inquiry=prepare_inquiries(
                category=[self.product_category],
                product_offering_id=[self.mobile_on_date_offer_id],
                activation_date=self.activation_date,
                as_list=False,
            )
        )

        self.client_product_profile.open_products_page(
            user_id=self.client.user_id, product_list=test_context.client.inquiry.product_list, is_activated=False
        )
        self.client_product_profile.locators.PRODUCTS_DETAILS_OPEN_BTN[0].wait_to_be_visible(timeout=10000)
        self.client_product_profile.locators.PRODUCTS_DETAILS_OPEN_BTN[0].click(force=True)
        self.client_product_profile.locators.PRODUCTS_CONSUMPTION_DETAILS_BTN.wait_to_be_visible(timeout=10000)
        self.client_product_profile.locators.PRODUCT_EDIT_ACTIVATION_DATE_BTN.not_to_be_visible()
