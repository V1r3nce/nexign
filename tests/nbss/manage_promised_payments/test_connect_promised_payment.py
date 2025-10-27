import allure
import pytest
from playwright.sync_api import APIRequestContext, Page

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from common.helpers.env_helper import BASE_URL
from models.user import IndividualClient, OrganizationClient
from pages.locators.nbss.dynamic_form_elements import (
    CreateOrganization,
    IndividualCustomerCreate,
    PromisedPaymentForm,
    RequestCreate,
)
from pages.locators.nbss.finances.promised_payment import PromisedPaymentPage
from pages.locators.nbss.inquiries_elements import ChangeResourcesForm, ProductEditForm
from pages.locators.nbss.select_product_offers_form import SelectProductOffersForm
from pages.nbss.inquiries_page import InquiriesPage
from pages.nbss.personal_account_page import PersonalAccountPage


@allure.epic("E2E_80 Управление обещанными платежами")
@allure.suite("E2E_80 Управление обещанными платежами")
@pytest.mark.usefixtures("nexign_ui_stand_login")
@pytest.mark.nbss_portal
class TestConnectPromisedPayment:
    @pytest.fixture(autouse=True)
    def setup(self, page: Page, api_request_context: APIRequestContext) -> None:
        self.personal_account_page = PersonalAccountPage(page)
        self.customer_create_form = IndividualCustomerCreate(page)
        self.organization_create_form = CreateOrganization(page)
        self.promised_payment = PromisedPaymentPage(page)
        self.promised_payment_form = PromisedPaymentForm(page)
        self.create_request = RequestCreate(page)
        self.inquiries_page = InquiriesPage(page)
        self.product_offer = SelectProductOffersForm(page)
        self.edit_product_form = ProductEditForm(page)
        self.change_product_form = ChangeResourcesForm(page)
        self.client_requests = ClientInquiriesRequests(api_request_context)

    @allure.title("01. Успешное подключение ОП без комиссии ФЛ")
    @allure.id(579843)
    @pytest.mark.regress
    def test_connect_promised_payment_b2c(self, create_user_with_agreement_and_account: IndividualClient) -> None:
        client_b2c = create_user_with_agreement_and_account
        self.personal_account_page.open(
            f"{BASE_URL}customer-hierarchy-management/accounts/{client_b2c.agreements[0].accounts[0].id}/account"
        )

        self.personal_account_page.locators.BURGER_MENU.select_by_value("Финансы > Обещанные платежи")

        self.promised_payment.CONNECT_BTN.wait_to_be_visible()
        self.promised_payment.CONNECT_BTN.click()
        self.promised_payment_form.CUSTOM_PARAM_BTN.click()
        self.promised_payment_form.fill_data_for_promised_payment()
        self.promised_payment_form.INNER_ACCEPT_BTN.click()
        self.personal_account_page.locators.INFO_MESSAGE.wait_to_be_visible()
        self.personal_account_page.locators.INFO_MESSAGE_CLOSE_BTN.click()

        self.promised_payment.PRODUCT_PROMISED_PAYMENT_FLD.wait_to_be_visible()

    @allure.title("02. Успешное подключение ОП без комиссии ЮЛ")
    @allure.id(579874)
    @pytest.mark.regress
    def test_connect_promised_payment_b2b(
        self, create_organization_with_agreement_and_account: OrganizationClient
    ) -> None:
        client_b2b = create_organization_with_agreement_and_account
        self.personal_account_page.open(
            f"{BASE_URL}customer-hierarchy-management/accounts/{client_b2b.agreements[0].accounts[0].id}/account"
        )

        self.personal_account_page.locators.BURGER_MENU.select_by_value("Финансы > Обещанные платежи")

        self.promised_payment.CONNECT_BTN.wait_to_be_visible()
        self.promised_payment.CONNECT_BTN.click()
        self.promised_payment_form.CUSTOM_PARAM_BTN.click()
        self.promised_payment_form.fill_data_for_promised_payment()
        self.promised_payment_form.INNER_ACCEPT_BTN.click()
        self.personal_account_page.locators.INFO_MESSAGE.wait_to_be_visible()
        self.personal_account_page.locators.INFO_MESSAGE_CLOSE_BTN.click()

        self.promised_payment.PRODUCT_PROMISED_PAYMENT_FLD.wait_to_be_visible()

    @allure.title("04. Подключение ОП из списка продуктовых предложений")
    @allure.id(583495)
    @pytest.mark.regress
    def test_connect_promised_payment_from_list_product_offer(
        self, create_organization_with_agreement_and_account: OrganizationClient
    ) -> None:
        client_b2b = create_organization_with_agreement_and_account
        self.personal_account_page.open(
            f"{BASE_URL}customer-hierarchy-management/accounts/{client_b2b.agreements[0].accounts[0].id}/account"
        )

        self.personal_account_page.locators.BURGER_MENU.select_by_value("Финансы > Обещанные платежи")

        self.promised_payment.CONNECT_BTN.wait_to_be_visible()
        self.promised_payment.CONNECT_BTN.click()

        self.promised_payment_form.PRODUCT_OFFER_FLD.select_by_value(value="ОП на 100 на 1 день с комиссией 0")
        self.promised_payment_form.INNER_ACCEPT_BTN.click()
        self.personal_account_page.locators.INFO_MESSAGE.wait_to_be_visible()
        self.personal_account_page.locators.INFO_MESSAGE_CLOSE_BTN.click()

        self.promised_payment.PRODUCT_PROMISED_PAYMENT_FLD.wait_to_be_visible()

    @allure.title("07. Подключение ОП с произвольными параметрами")
    @allure.id(583882)
    @pytest.mark.regress
    def test_connect_promised_payment_with_arbitrary_parameters(
        self, create_user_with_agreement_and_account: IndividualClient
    ) -> None:
        client_b2c = create_user_with_agreement_and_account
        self.personal_account_page.open(
            f"{BASE_URL}customer-hierarchy-management/accounts/{client_b2c.agreements[0].accounts[0].id}/account"
        )
        inquiry = self.client_requests.product_sale()

        self.personal_account_page.locators.BURGER_MENU.select_by_value("Финансы > Обещанные платежи")

        self.promised_payment.CONNECT_BTN.wait_to_be_visible(timeout=60000)
        self.promised_payment.CONNECT_BTN.click()

        self.promised_payment_form.CUSTOM_PARAM_BTN.click()
        self.promised_payment_form.fill_data_for_promised_payment(commission_type=True, abonent=inquiry.product.subs_id)
        self.promised_payment_form.INNER_ACCEPT_BTN.click()
        self.personal_account_page.locators.INFO_MESSAGE.wait_to_be_visible()
        self.personal_account_page.locators.INFO_MESSAGE_CLOSE_BTN.click()

        self.promised_payment.PRODUCT_PROMISED_PAYMENT_FLD.wait_to_be_visible()
