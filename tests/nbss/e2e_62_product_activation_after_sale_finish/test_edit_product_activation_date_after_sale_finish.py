import allure
import pytest

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from api.nbss.client_requests.client_requests import ClientRequests
from common.helpers.data_generator import get_datetime_beginning_of_day, get_shifted_datetime_string
from models.client import OrganizationClient
from models.context import test_context
from models.inquiry import prepare_inquiries
from models.product import B2BProducts
from pages.base_page import BasePage
from pages.nbss.client.client_product_profile_page import ClientProductProfilePage
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.inquiries_page import InquiriesPage


@pytest.mark.regress
@pytest.mark.nbss_portal
@allure.epic("E2E_62 Продажа клиенту B2B")
@allure.suite("E2E_62 Продажа клиенту B2B")
class TestEditProductActivationDateAfterSaleFinish:
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

        self.activation_date = get_datetime_beginning_of_day(shift="+1d", time_zone="Europe/Moscow")
        self.shifted_activation_date = get_shifted_datetime_string(shift="+2d", is_full_format=False)

    @allure.title("01. Изменение даты активации продукта после завершения продажи")
    @allure.id(757454)
    def test_edit_product_activation_date_after_sale_finish(self) -> None:
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
        self.client_product_profile.edit_product_activation_date()
        self.client_product_profile.check_edit_product_activation_date_message()
        self.client_product_profile.fill_activation_date_and_create_request(self.shifted_activation_date)

        self.client_profile.click_tab("Заявки")
        self.client_profile.open_request_by_type_name(
            "Изменение даты активации продукта", should_check_product_name=False
        )
        self.inquiries_page.locators.INQUIRY_STEP.wait_to_have_text("Дата активации изменена", timeout=15000)
        self.inquiries_page.wait_inquiry_status("Закрыто")

        self.client_product_profile.open_products_page_and_check(
            user_id=self.client.user_id, product_list=test_context.client.inquiry.product_list, is_activated=False
        )
        self.client_product_profile.check_product_activation_date(self.shifted_activation_date)
