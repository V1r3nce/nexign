import allure
import pytest

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from api.nbss.client_requests.client_requests import ClientRequests
from api.nbss.finances.payments_requests import PaymentsRequests
from api.nbss.personal_account_requests import PersonalAccountRequests
from api.nwm_requests.nwm_requests import NwmRequests
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
class TestEditProductActivationDateAfterSaleFinishProductActive:
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
        self.nwm_requests = NwmRequests()

        self.client = create_organization_with_agreement_and_account
        self.mobile_on_date_offer_id = B2BProducts.mobile_on_date
        self.mobile_on_date = product_names_map.get(self.mobile_on_date_offer_id)
        self.product_category = "mobile"

        self.client_inquiries_requests = ClientInquiriesRequests()
        self.activation_date = get_datetime_beginning_of_day(shift="+1d", time_zone="Europe/Moscow")
        self.today_date = get_datetime_beginning_of_day()
        self.today_date_plus_month = get_datetime_beginning_of_day(shift="+31d")

    @allure.title("05. Изменение даты активации продукта после завершения продажи (продукт активен)")
    @allure.id(757489)
    def test_edit_product_activation_date_after_sale_finish_product_active(self) -> None:
        self.client_inquiries_requests.product_sale(
            inquiry=prepare_inquiries(
                category=[self.product_category],
                product_offering_id=[self.mobile_on_date_offer_id],
                activation_date=self.activation_date,
                as_list=False,
            )
        )

        self.payments_requests.create_default_payment(
            test_context.client.agreements[0].accounts[0].id,
            test_context.client.inquiry.product.one_time_payment + test_context.client.inquiry.product.subscription_fee,
        )
        self.personal_account_api.wait_check_current_main_balance(
            test_context.client.agreements[0].accounts[0].id,
            test_context.client.inquiry.product.one_time_payment + test_context.client.inquiry.product.subscription_fee,
        )

        self.nwm_requests.activate_product(
            product=test_context.client.inquiry.product, inquiry_id=test_context.client.inquiry.id
        )
        self.client_inquiries_requests.wait_products_active_by_agreement(
            test_context.client.user_id, test_context.client.agreement.id
        )
        self.personal_account_api.wait_accruals(
            subscription_id=test_context.client.inquiry.product.subs_id,
            dateFrom=self.today_date,
            dateTo=self.today_date_plus_month,
        )

        self.client_product_profile.open_products_page_and_check(
            user_id=self.client.user_id, product_list=test_context.client.inquiry.product_list, is_activated=True
        )

        self.client_product_profile.locators.PRODUCTS_DETAILS_OPEN_BTN[0].wait_to_be_visible(timeout=10000)
        self.client_product_profile.locators.PRODUCTS_DETAILS_OPEN_BTN[0].click(force=True)
        self.client_product_profile.locators.PRODUCTS_CONSUMPTION_DETAILS_BTN.wait_to_be_visible(timeout=10000)
        self.client_product_profile.locators.PRODUCT_EDIT_ACTIVATION_DATE_BTN.to_be_disabled()
