import random

import allure
import pytest

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from api.nbss.finances.payments_requests import PaymentsRequests
from api.nbss.personal_account_requests import PersonalAccountRequests
from models.client import OrganizationClient
from models.context import test_context
from models.inquiry import prepare_inquiries
from models.product import B2BProducts, product_names_map
from pages.base_page import BasePage
from pages.locators.nbss.dynamic_form_elements import ReplaceResource
from pages.nbss.client.client_product_profile_page import ClientProductProfilePage
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.inquiries_page import InquiriesPage


@pytest.mark.regress
@pytest.mark.nbss_portal
@allure.epic("E2E_05 Управление атрибутами продукта/сервиса/ресурса абонента (Индивидуализация цены)")
@allure.suite("E2E_05 Управление атрибутами продукта/сервиса/ресурса абонента (Индивидуализация цены)")
class TestEquipmentResourceReplaceFromSidebar:
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
        self.replace_resource_form = ReplaceResource()

        self.client_inquiries_requests = ClientInquiriesRequests()
        self.payment_api = PaymentsRequests()
        self.personal_account_api = PersonalAccountRequests()

        self.client = create_organization_with_agreement_and_account
        self.discount_percent = random.randint(1, 99)

    @allure.title("10. Замена ресурса Оборудование из ранее приобретенных ресурсов из бокового меню (с индивид.цены)")
    @allure.id(844998)
    def test_equipment_resource_replace_from_sidebar(self) -> None:
        product_name_rent = product_names_map.get(B2BProducts.satellite_rent)
        product_name_sale = product_names_map.get(B2BProducts.equipment_sale)

        inquiry = prepare_inquiries(category=["satellite_rent", "equipment_sale"], as_list=False)
        self.client_inquiries_requests.product_sale(self.client, inquiry)
        products = {product.product_name: product for product in test_context.client.inquiry.product_list}

        original_subscription_fee = products[product_name_rent].subscription_fee
        original_one_time_price = products[product_name_sale].one_time_payment

        payment_amount = original_subscription_fee + original_one_time_price
        account_id = self.client.agreements[0].accounts[0].id
        self.payment_api.create_default_payment(account_id, payment_amount)
        self.personal_account_api.wait_check_current_main_balance(account_id, payment_amount)
        self.personal_account_api.wait_accruals(test_context.client.user_id)

        self.client_product_profile.open_products_page(
            user_id=test_context.client.user_id, product_list=test_context.client.inquiry.product_list, is_activated=True
        )
        self.client_product_profile.locators.PRODUCTS_DETAILS_OPEN_BTN[0].wait_to_be_visible(timeout=15000)
        self.client_product_profile.locators.PRODUCTS_DETAILS_OPEN_BTN[0].click()
        self.client_product_profile.locators.EDIT_BTN.to_be_enabled()
        self.client_product_profile.locators.TURN_OFF_BTN.to_be_enabled()

        self.client_profile.open_replace_resource_form()
        self.client_profile.fill_replace_resource_fields(
            replaceable_resource_serial_number=products[product_name_rent].serial_number,
            for_replace_serial_number=products[product_name_sale].serial_number,
            need_add_agreement=True,
            need_acceptance_certificate=True,
            discount=self.discount_percent,
        )
        self.client_profile.check_replace_resource_fields(
            product_name=products[product_name_rent].product_name,
            subscriber=products[product_name_rent].phone_number,
            nomenclature="at_L_001",
            type_of_sale="Аренда",
        )

        self.replace_resource_form.DO_REPLACE_BTN.click()
        self.replace_resource_form.DO_REPLACE_BTN.not_to_be_visible()
