import allure
import pytest

from api.psc_requests.offerings_requests import ProductOfferingRequests
from models.client import OrganizationClient
from models.context import test_context
from models.product import B2BProducts
from pages.nbss.client.client_product_profile_page import ClientProductProfilePage
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.inquiries_page import InquiriesPage
from pages.nbss.inquiry_order_structure_management_page import InquiryOrderStructureManagement


@pytest.mark.regress
@pytest.mark.nbss_portal
@allure.epic("E2E_62 Продажа клиенту B2B")
@allure.suite("E2E_62 Продажа клиенту B2B")
class TestDisplayVolumesDuringSale:
    @pytest.fixture(autouse=True)
    def setup(
        self,
        nexign_stand_login,
        create_organization: OrganizationClient,
    ) -> None:
        self.inquiries_page = InquiriesPage()
        self.inquiries_page_order_structure = InquiryOrderStructureManagement()
        self.client_profile = ClientProfilePage()
        self.client_product_profile = ClientProductProfilePage()

        self.client = create_organization

        self.psc_requests = ProductOfferingRequests()

        self.internet_volume = self.psc_requests.get_product_offering_volume(B2BProducts.mobile_business, "Интернет")
        self.minutes_volume = self.psc_requests.get_product_offering_volume(B2BProducts.mobile_business, "Минуты")
        self.sms_volume = self.psc_requests.get_product_offering_volume(B2BProducts.mobile_business, "SMS")

    @allure.title("02. Отображение сконфигурированных объемов ПП на шагах продажи")
    @allure.id(844810)
    def test_display_volumes_during_sale(self) -> None:
        self.client_profile.open_client_profile_page(self.client.user_id)
        self.inquiries_page.sale_initialization(self.client, need_contact_data=True, priority="Высокий", add_kp="auto")

        self.inquiries_page.locators.ADD_SALE_BTN.click()
        self.inquiries_page.search_products_in_form(
            product_offer_name="Бизнес на связи", product_category_name="Мобильная связь"
        )
        self.inquiries_page_order_structure.check_product_volumes_on_product_card(
            [self.minutes_volume, self.internet_volume, self.sms_volume]
        )

        self.inquiries_page.locators.product_offer_form.PRODUCT_CARD_DETAILS[0].click()
        self.inquiries_page_order_structure.check_product_volumes_in_sidebar(
            [self.minutes_volume, self.internet_volume, self.sms_volume]
        )

        self.inquiries_page.locators.product_offer_form.product_info_form.CROSS_BTN.click()
        self.inquiries_page.find_product_in_form(
            product_offer_name="Бизнес на связи", product_category_name="Мобильная связь"
        )
        self.inquiries_page_order_structure.show_volumes_tooltip()
        self.inquiries_page_order_structure.check_product_volumes_in_tooltip(
            [self.internet_volume, self.minutes_volume, self.sms_volume]
        )

        self.inquiries_page.locators.PRODUCTS_NAME[0].click(force=True)
        self.inquiries_page.product_edit_form.VOLUMES_TAB.wait_to_be_visible()
        self.inquiries_page.product_edit_form.VOLUMES_TAB.click()
        self.inquiries_page_order_structure.check_product_volumes_on_volumes_tab(
            [self.internet_volume, self.minutes_volume, self.sms_volume]
        )

        self.inquiries_page.product_edit_form.INNER_CANCEL_BTN.click()
        self.inquiries_page.product_edit_form.PRODUCT_NAME.not_to_be_visible()

        self.inquiries_page.auto_reserve_all_resources()
        self.inquiries_page.check_configuration()
        self.inquiries_page.locators.NEXT_STEP_BTN.wait_to_be_enabled()
        self.inquiries_page.locators.NEXT_STEP_BTN.click()
        self.inquiries_page.wait_connect_package_offers_and_close_inquiry()

        self.client_product_profile.open_products_page(
            self.client.user_id, product_list=test_context.client.inquiry.product_list, is_activated=False
        )
        self.client_product_profile.check_product_volumes(
            [self.minutes_volume, self.internet_volume, self.sms_volume],
            [self.minutes_volume, self.internet_volume, self.sms_volume],
        )

        self.client_product_profile.click_first_product(
            test_context.client.inquiry.product.phone_number, test_context.client.inquiry.product.product_name
        )
        self.client_product_profile.check_product_volumes(
            [self.minutes_volume, self.internet_volume, self.sms_volume],
            [self.minutes_volume, self.internet_volume, self.sms_volume],
        )
