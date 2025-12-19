import allure
import pytest

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from api.nbss.client_requests.client_requests import ClientRequests
from api.nbss.finances.payments_requests import PaymentsRequests
from api.nbss.personal_account_requests import PersonalAccountRequests
from api.psc_requests.offerings_requests import ProductOfferingRequests
from api.psc_requests.projects_requests import ProjectRequests
from models.context import test_context
from models.inquiry import prepare_inquiries
from models.product import get_default_offering_id
from models.user import generate_organization_client


@allure.suite("E2E_47_1 Подключение дополнительных ПП (Учесть репрайс при проливке данных из PSC)")
@pytest.mark.regress
@pytest.mark.influencing
class TestMainPoReprice:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login, create_organization, create_nwm_ssh_connection):
        self.psc_po_api = ProductOfferingRequests()
        self.psc_project_api = ProjectRequests()
        self.client_api = ClientRequests()
        self.client_inquiry_api = ClientInquiriesRequests()
        self.payment_api = PaymentsRequests()
        self.personal_account_api = PersonalAccountRequests()
        self.ssh_nwm = create_nwm_ssh_connection
        self.new_amount = "685"
        self.payment_amount = 2000
        self.internet_po_id = get_default_offering_id("internet")
        self.mobile_po_id = get_default_offering_id("mobile")

    @allure.title("Подключение ПП после репрайса (Абон. плата). Монопродукт")
    @allure.id(601638)
    def test_main_po_subscription_fee_reprice(self, clean_project_product_offerings):
        po_id, project_id, po_name = self.psc_po_api.clone_po_and_wait_success(self.internet_po_id)
        self.psc_project_api.publish_project_and_wait_success(project_id)
        clean_project_product_offerings.append(project_id)
        self.ssh_nwm.reload_ocs_and_check_product_offering(po_id, po_name)
        self.client_inquiry_api.product_sale(inquiry=prepare_inquiries(category="internet", product_offering_id=po_id))
        self.payment_api.create_default_payment(test_context.client.agreements[0].accounts[0].id, self.payment_amount)
        self.personal_account_api.wait_check_current_main_balance(
            test_context.client.agreements[0].accounts[0].id,
            self.payment_amount - test_context.client.inquiry.product.total_amount,
            is_assert=True,
        )
        self.psc_project_api.back_project_and_wait_success(project_id)
        self.psc_po_api.reprice_product_offering_price(
            product_offering_id=po_id, project_id=project_id, new_amount=self.new_amount, price_type="recurringCharge"
        )
        self.psc_project_api.publish_project_and_wait_success(project_id)
        self.ssh_nwm.reload_ocs_and_check_product_offering(po_id, po_name)
        self.client_api.create_organization(generate_organization_client())
        self.client_inquiry_api.product_sale(
            client=test_context.client_list[1], inquiry=prepare_inquiries(category="internet", product_offering_id=po_id)
        )
        self.payment_api.create_default_payment(
            test_context.client_list[1].agreements[0].accounts[0].id, self.payment_amount
        )
        self.personal_account_api.wait_check_current_main_balance(
            test_context.client_list[1].agreements[0].accounts[0].id,
            self.payment_amount - test_context.client.inquiry.product.one_time_payment - int(self.new_amount),
            is_assert=True,
        )

    @allure.title("Подключение ПП после рапрайса (Разовое начисление). Монопродукт")
    @allure.id(606889)
    def test_main_po_onetime_charge_reprice(self, clean_project_product_offerings):
        po_id, project_id, po_name = self.psc_po_api.clone_po_and_wait_success(self.internet_po_id)
        self.psc_project_api.publish_project_and_wait_success(project_id)
        clean_project_product_offerings.append(project_id)
        self.ssh_nwm.reload_ocs_and_check_product_offering(po_id, po_name)
        self.client_inquiry_api.product_sale(inquiry=prepare_inquiries(category="internet", product_offering_id=po_id))
        self.payment_api.create_default_payment(test_context.client.agreements[0].accounts[0].id, self.payment_amount)
        self.personal_account_api.wait_check_current_main_balance(
            test_context.client.agreements[0].accounts[0].id,
            self.payment_amount - test_context.client.inquiry.product.total_amount,
            is_assert=True,
        )
        self.psc_project_api.back_project_and_wait_success(project_id)
        self.psc_po_api.reprice_product_offering_price(
            product_offering_id=po_id,
            project_id=project_id,
            new_amount=self.new_amount,
            price_type="feeProdOfferingPrice",
        )
        self.psc_project_api.publish_project_and_wait_success(project_id)
        self.ssh_nwm.reload_ocs_and_check_product_offering(po_id, po_name)
        self.client_api.create_organization(generate_organization_client())
        self.client_inquiry_api.product_sale(
            client=test_context.client_list[1], inquiry=prepare_inquiries(category="internet", product_offering_id=po_id)
        )
        self.payment_api.create_default_payment(
            test_context.client_list[1].agreements[0].accounts[0].id, self.payment_amount
        )
        self.personal_account_api.wait_check_current_main_balance(
            test_context.client_list[1].agreements[0].accounts[0].id,
            self.payment_amount - int(self.new_amount) - test_context.client.inquiry.product.subscription_fee,
            is_assert=True,
        )

    @allure.title("Подключение ПП после репрайса (Объемы). Монопродукт")
    @allure.id(606741)
    def test_main_po_volumes_reprice(self, clean_project_product_offerings):
        po_id, project_id, po_name = self.psc_po_api.clone_po_and_wait_success(self.mobile_po_id)
        self.psc_project_api.publish_project_and_wait_success(project_id)
        clean_project_product_offerings.append(project_id)
        self.ssh_nwm.reload_ocs_and_check_product_offering(po_id, po_name)
        self.client_inquiry_api.product_sale(inquiry=prepare_inquiries(category="mobile", product_offering_id=po_id))
        self.payment_api.create_default_payment(test_context.client.agreements[0].accounts[0].id, self.payment_amount)
        self.personal_account_api.wait_check_current_main_balance(
            test_context.client.agreements[0].accounts[0].id,
            self.payment_amount - test_context.client.inquiry.product.total_amount,
            is_assert=True,
        )
        self.psc_project_api.back_project_and_wait_success(project_id)
        self.psc_po_api.reprice_product_offering_price(
            product_offering_id=po_id,
            project_id=project_id,
            new_amount=self.new_amount,
            price_type="trafficUsage",
            is_volume=True,
        )
        self.psc_project_api.publish_project_and_wait_success(project_id)
        self.ssh_nwm.reload_ocs_and_check_product_offering(po_id, po_name)
        self.ssh_nwm.check_po_internet_price(po_id, self.new_amount)
        self.client_api.create_organization(generate_organization_client())
        self.client_inquiry_api.product_sale(
            client=test_context.client_list[1], inquiry=prepare_inquiries(category="mobile", product_offering_id=po_id)
        )
        self.payment_api.create_default_payment(
            test_context.client_list[1].agreements[0].accounts[0].id, self.payment_amount
        )
        self.personal_account_api.wait_check_current_main_balance(
            test_context.client_list[1].agreements[0].accounts[0].id,
            self.payment_amount - test_context.client.inquiry.product.total_amount,
            is_assert=True,
        )

    @allure.title("Подключение ПП после репрайса (Трафик). Монопродукт")
    @allure.id(606744)
    def test_main_po_traffic_reprice(self, clean_project_product_offerings):
        po_id, project_id, po_name = self.psc_po_api.clone_po_and_wait_success(self.mobile_po_id)
        self.psc_project_api.publish_project_and_wait_success(project_id)
        clean_project_product_offerings.append(project_id)
        self.ssh_nwm.reload_ocs_and_check_product_offering(po_id, po_name)
        self.client_inquiry_api.product_sale(inquiry=prepare_inquiries(category="mobile", product_offering_id=po_id))
        self.payment_api.create_default_payment(test_context.client.agreements[0].accounts[0].id, self.payment_amount)
        self.personal_account_api.wait_check_current_main_balance(
            test_context.client.agreements[0].accounts[0].id,
            self.payment_amount - test_context.client.inquiry.product.total_amount,
            is_assert=True,
        )
        self.psc_project_api.back_project_and_wait_success(project_id)
        self.psc_po_api.reprice_product_offering_price(
            product_offering_id=po_id,
            project_id=project_id,
            new_amount=self.new_amount,
            price_type="trafficUsage",
        )
        self.psc_project_api.publish_project_and_wait_success(project_id)
        self.ssh_nwm.reload_ocs_and_check_product_offering(po_id, po_name)
        self.ssh_nwm.check_po_internet_price(po_id, self.new_amount, is_volume=False)
        self.client_api.create_organization(generate_organization_client())
        self.client_inquiry_api.product_sale(
            client=test_context.client_list[1], inquiry=prepare_inquiries(category="mobile", product_offering_id=po_id)
        )
        self.payment_api.create_default_payment(
            test_context.client_list[1].agreements[0].accounts[0].id, self.payment_amount
        )
        self.personal_account_api.wait_check_current_main_balance(
            test_context.client_list[1].agreements[0].accounts[0].id,
            self.payment_amount - test_context.client.inquiry.product.total_amount,
            is_assert=True,
        )
