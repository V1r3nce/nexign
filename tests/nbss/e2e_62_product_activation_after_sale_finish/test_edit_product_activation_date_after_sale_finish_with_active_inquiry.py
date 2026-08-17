import allure
import pytest

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from api.nbss.client_requests.client_requests import ClientRequests
from api.nbss.finances.payments_requests import PaymentsRequests
from api.nbss.personal_account_requests import PersonalAccountRequests
from common.helpers.data_generator import get_datetime_beginning_of_day
from models.client import OrganizationClient
from models.context import test_context
from models.inquiry import prepare_inquiries
from models.product import B2BProducts, product_names_map
from pages.base_page import BasePage
from pages.nbss.client.client_product_profile_page import ClientProductProfilePage
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.inquiries_page import InquiriesPage


@pytest.mark.regress
@pytest.mark.nbss_portal
@allure.epic("E2E_62 Продажа клиенту B2B")
@allure.suite("E2E_62 Продажа клиенту B2B")
class TestEditProductActivationDateAfterSaleFinishWithActiveInquiry:
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
        self.payments_requests = PaymentsRequests()
        self.personal_account_api = PersonalAccountRequests()

        self.client = create_organization_with_agreement_and_account
        self.mobile_on_date_offer_id = B2BProducts.mobile_on_date
        self.mobile_on_date = product_names_map.get(self.mobile_on_date_offer_id)
        self.product_category = "mobile"

        self.client_inquiries_requests = ClientInquiriesRequests()
        self.activation_date = get_datetime_beginning_of_day(shift="+1d", time_zone="Europe/Moscow")

    @allure.title("03. Изменение даты активации продукта после завершения продажи (есть активная заявка)")
    @allure.id(757487)
    def test_edit_product_activation_date_after_sale_finish_with_active_inquiry(self) -> None:
        self.client_inquiries_requests.product_sale(
            inquiry=prepare_inquiries(
                category=[self.product_category],
                product_offering_id=[self.mobile_on_date_offer_id],
                activation_date=self.activation_date,
                as_list=False,
            )
        )

        self.client_product_profile.open_products_page_and_check(
            user_id=self.client.user_id, product_list=test_context.client.inquiry.product_list, is_activated=False
        )
        self.client_product_profile.create_product_disconnect_inquiry(
            test_context.client.inquiry.product, is_active=False, create_add_agreement="manual"
        )
        inquiry_id = self.client_profile.get_inquiry_id_from_info_message()
        self.client_inquiries_requests.wait_inquiry_step(inquiry_id, "ORDER_MANAGEMENT")
        self.client_product_profile.refresh_page(wait="load")

        self.client_product_profile.locators.PRODUCTS_DETAILS_OPEN_BTN[0].wait_to_be_visible(timeout=10000)
        self.client_product_profile.locators.PRODUCTS_DETAILS_OPEN_BTN[0].click(force=True)
        self.client_product_profile.locators.PRODUCTS_CONSUMPTION_DETAILS_BTN.wait_to_be_visible(timeout=10000)
        self.client_product_profile.locators.PRODUCT_EDIT_ACTIVATION_DATE_BTN.to_be_disabled()
