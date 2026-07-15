import random

import allure
import pytest

from common.enums.user import User
from models.address_info import AlternativeAddress, BasicSystemAddress
from models.client import OrganizationClient
from models.context import test_context
from models.inquiry import prepare_inquiries
from pages.base_page import BasePage
from pages.locators.nbss.dynamic_form_elements import ProductInfoForm
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.inquiries_page import InquiriesPage


@allure.epic("E2E_22 Управление адресной информацией")
@allure.suite("E2E_62 Продажа клиенту B2B")
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestAddGeocoordinatesDuringSaleNoAddressInDictionary:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login, create_organization: OrganizationClient) -> None:
        self.base_page = BasePage()
        self.client_profile = ClientProfilePage()
        self.inquiries_page = InquiriesPage()
        self.product_info_form = ProductInfoForm()

        self.address = BasicSystemAddress()
        self.new_address = AlternativeAddress()

        self.latitude = f"{random.randint(0, 90)}.{random.randint(100000, 999999)}"
        self.longitude = f"{random.randint(0, 180)}.{random.randint(100000, 999999)}"

        self.client = create_organization

    @pytest.mark.user(User.SELLER_TEST)
    @allure.title("02. Использование географических координат при продаже клиенту B2B. Адрес отсутствует в справочнике")
    @allure.id(840764)
    def test_add_geocoordinates_during_sale_no_address_in_dictionary(self) -> None:
        self.client_profile.open_client_profile_page(test_context.client.user_id)
        self.inquiries_page.sale_initialization(
            self.client,
            priority="Высокий",
            add_kp="no",
            create_add_agreement="auto",
        )

        test_context.client.inquiry_list = prepare_inquiries(category="satellite_sale")
        self.inquiries_page.add_product_offer_to_commercial_order(
            test_context.client.inquiry.product, latitude=self.latitude, longitude=self.longitude
        )
        test_context.client.inquiry.product.switch_name = "Коммутатор_Спутниковая_связь"
        self.inquiries_page.auto_reserve_all_resources(test_context.client.inquiry.product.category)
        self.inquiries_page.check_configuration()
        self.inquiries_page.click_next("Автоматическое управление Договором/ДС и ЛС")
        self.inquiries_page.wait_close_inquiry()

        self.client_profile.open_products_page(
            user_id=test_context.client.user_id, product_list=[test_context.client.inquiry.product], is_activated=False
        )
        self.client_profile.locators.PRODUCT_ADDRESS.wait_to_have_text(f"{self.latitude};{self.longitude}")
        self.client_profile.click_first_product(
            subscriber=test_context.client.inquiry.product.phone_number,
            product_name=test_context.client.inquiry.product.product_name,
        )
        self.product_info_form.verify_product_addresses(BasicSystemAddress.address, f"{self.latitude};{self.longitude}")
