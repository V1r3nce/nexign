import allure
import pytest

from api.lis_requests.equipment import EquipmentRequests
from api.lis_requests.phone_numbers import PhoneNumbersRequests
from api.lis_requests.sim_cards import SimCardsRequests
from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from api.nbss.client_requests.client_requests import ClientRequests
from common.enums.lis import DefaultStandardNames
from common.helpers.env_helper import BASE_URL
from models.address_info import BasicSystemAddress
from models.client import OrganizationClient
from models.context import test_context
from models.product import B2BProducts, MainProduct, product_names_map
from pages.base_page import BasePage
from pages.locators.nbss.dynamic_form_elements import ProductInfoForm
from pages.locators.nbss.inquiries_elements import ProductEditForm, ReserveResourcesForm
from pages.locators.nbss.select_product_offers_form import SelectProductOffersFormElements
from pages.nbss.client.client_product_profile_page import ClientProductProfilePage
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.inquiries_page import InquiriesPage


@allure.epic("E2E_15 Бронирование номеров")
@allure.suite("E2E_15 Бронирование номеров")
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestReferenceSwitch:
    @pytest.fixture(autouse=True)
    def setup(
        self, nexign_stand_login, create_switch, create_and_ship_sim_cards, create_number_and_start_exploitation
    ) -> None:
        self.sim_requests = SimCardsRequests()
        self.equipment_requests = EquipmentRequests()
        self.number_requests = PhoneNumbersRequests()
        self.client_api = ClientRequests()
        self.inquiry_api = ClientInquiriesRequests()

        self.base_page = BasePage()
        self.inquiries_page = InquiriesPage()
        self.product_offer_form = SelectProductOffersFormElements()
        self.product_edit_form = ProductEditForm()
        self.reserve_form = ReserveResourcesForm()
        self.client_profile = ClientProfilePage()
        self.client_product_profile = ClientProductProfilePage()
        self.product_info_form = ProductInfoForm()

        self.switch_name = create_switch.name
        self.imsi = create_and_ship_sim_cards
        self.number = create_number_and_start_exploitation
        self.product = MainProduct(
            product_offering_id=B2BProducts.satellite_sale,
            product_name=product_names_map.get(B2BProducts.satellite_sale),
        )

    @allure.title("12. Первичное бронирование мобильного номера во время продажи (Опорный коммутатор)")
    @allure.id(818607)
    @pytest.mark.parametrize("create_switch", [DefaultStandardNames.satellite_standard_names], indirect=True)
    def test_mobile_phone_first_reservation(self, create_organization: OrganizationClient) -> None:
        self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")

        self.inquiries_page.sale_initialization(
            test_context.client, need_contact_data=True, priority="Высокий", add_kp="no"
        )

        self.inquiries_page.locators.ADD_SALE_BTN.click()
        self.product_offer_form.REGION.wait_to_be_visible()
        region = self.product_offer_form.REGION.text
        self.product_offer_form.ADDRESS.to_contain_text(BasicSystemAddress.address)

        self.inquiries_page.find_product_in_form(self.product.product_name, "Спутниковая связь")
        self.inquiries_page.check_inquiry_state_after_product_addition(product_count=1)

        self.inquiries_page.locators.PRODUCT_RESOURCES_UNFILLED_BTN[0].hover()
        self.inquiries_page.locators.PRODUCT_RESOURCES_UNFILLED_BTN[0].click(force=True)
        self.product_edit_form.PRODUCT_REGION.wait_to_have_text(region)
        self.product_edit_form.RESOURCES_TAB.click()

        self.product_edit_form.CHANGE_NUMBER_BTN.click()
        # self.reserve_form.SWITCH.wait_to_have_text("")
        self.reserve_form.SWITCH.check_option_in_values(self.switch_name)
        self.reserve_form.SWITCH.select_by_value(self.switch_name)
        phone_number = self.inquiries_page.reserve_number(mask=self.number)

        self.inquiry_api.get_client_inquiries_info_and_enrich(test_context.client)
        self.inquiry_api.wait_for_resource_reservation(
            product_id=test_context.client.inquiry.product.product_id, resource_value=phone_number
        )

        self.product_edit_form.CHANGE_ICCID_BTN.click()
        self.inquiries_page.check_switch_selected_and_disabled(switch_name=self.switch_name)
        self.inquiries_page.reserve_sim(search_type="IMSI", mask=self.imsi)

        self.inquiries_page.reserve_equipment()

        self.product_edit_form.INNER_ACCEPT_BTN.click()
        self.product_edit_form.RESOURCES_TAB.not_to_be_visible()
        self.inquiries_page.locators.LOAD_SPIN_FIRST.not_to_be_visible()

        self.inquiries_page.check_configuration()

        self.inquiries_page.locators.NEXT_STEP_BTN.click()
        self.inquiries_page.wait_connect_package_offers_and_close_inquiry()

        self.inquiries_page.locators.PRODUCT_PROFILE_BTN.click()
        self.client_product_profile.click_first_product(phone_number, self.product.product_name, False)
        self.product_info_form.REGION.wait_to_be_visible()
        self.product_info_form.REGION.wait_to_have_text(region)

    @allure.title("13. Первичное бронирование SIM во время продажи (Опорный коммутатор)")
    @allure.id(818606)
    @pytest.mark.parametrize("create_switch", [DefaultStandardNames.satellite_standard_names], indirect=True)
    def test_sim_first_reservation(self, create_organization: OrganizationClient) -> None:
        self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")
        region = "Новосибирская область"

        self.inquiries_page.sale_initialization(
            test_context.client, need_contact_data=True, priority="Высокий", add_kp="no"
        )

        self.inquiries_page.locators.ADD_SALE_BTN.click()
        self.product_offer_form.REGION.wait_to_be_visible()
        self.product_offer_form.REGION.select_by_value(region)
        self.product_offer_form.ADDRESS.to_have_value("")

        self.inquiries_page.find_product_in_form(self.product.product_name, "Спутниковая связь")
        self.inquiries_page.check_inquiry_state_after_product_addition(product_count=1, region=region)

        self.inquiries_page.locators.PRODUCT_RESOURCES_UNFILLED_BTN[0].hover()
        self.inquiries_page.locators.PRODUCT_RESOURCES_UNFILLED_BTN[0].click(force=True)
        self.product_edit_form.PRODUCT_REGION.wait_to_have_text(region)

        self.product_edit_form.RESOURCES_TAB.click()
        self.product_edit_form.CHANGE_ICCID_BTN.click()
        self.reserve_form.SWITCH.wait_to_have_text("")
        self.reserve_form.SWITCH.check_option_in_values(self.switch_name)
        self.reserve_form.SWITCH.select_by_value(self.switch_name)
        self.reserve_form.REGION.wait_to_have_text(region)
        iccid = self.inquiries_page.reserve_sim(search_type="IMSI", mask=self.imsi)

        self.inquiry_api.get_client_inquiries_info_and_enrich(test_context.client)
        self.inquiry_api.wait_for_resource_reservation(product_id=self.product.product_id, resource_value=iccid)

        self.product_edit_form.CHANGE_NUMBER_BTN.click()
        self.inquiries_page.check_switch_selected_and_disabled(switch_name=self.switch_name)
        self.reserve_form.REGION.wait_to_have_text(region)
        phone_number = self.inquiries_page.reserve_number(mask=self.number)

        self.inquiries_page.reserve_equipment()

        self.product_edit_form.INNER_ACCEPT_BTN.click()
        self.product_edit_form.RESOURCES_TAB.not_to_be_visible()

        self.inquiries_page.locators.LOAD_SPIN_FIRST.not_to_be_visible()
        self.inquiries_page.check_configuration()

        self.inquiries_page.locators.NEXT_STEP_BTN.click()
        self.inquiries_page.wait_connect_package_offers_and_close_inquiry()

        self.inquiries_page.locators.PRODUCT_PROFILE_BTN.click()
        self.client_product_profile.click_first_product(phone_number, self.product.product_name, False)
        self.product_info_form.REGION.wait_to_be_visible()
        self.product_info_form.REGION.wait_to_have_text(region)
