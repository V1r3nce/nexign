from datetime import datetime, timedelta

import allure
import pytest
from dateutil.relativedelta import relativedelta

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from api.nbss.client_requests.client_requests import ClientRequests
from common.helpers.data_generator import get_datetime_beginning_of_day
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
class TestEditProductActivationDateAfterSaleFinishMore90Days:
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
        self.future_activation_date = (
            (datetime.now() + relativedelta(months=3) + timedelta(days=1)).date().strftime("%d.%m.%Y")
        )
        self.allowed_activation_end_date = (datetime.now() + relativedelta(months=3)).date().isoformat()

    @allure.title("07. Изменение даты активации продукта на период более 90 дней")
    @allure.id(913905)
    def test_edit_product_activation_date_after_sale_finish_more_90_days(self) -> None:
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
        self.client_product_profile.edit_product_activation_date()
        self.client_product_profile.check_edit_product_activation_date_message()
        self.client_product_profile.edit_product_activation_date_form.ACTIVATION_DATE.wait_to_be_visible()
        self.client_product_profile.edit_product_activation_date_form.ACTIVATION_DATE.fill(self.future_activation_date)
        self.client_product_profile.edit_product_activation_date_form.ACTIVATION_DATE_ERROR.to_contain_text(
            self.activation_date.date().isoformat()
        )
        self.client_product_profile.edit_product_activation_date_form.ACTIVATION_DATE_ERROR.to_contain_text(
            self.allowed_activation_end_date
        )
