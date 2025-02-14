import allure
import pytest
from playwright.sync_api import Page
from pages.locators.dynamic_form_elements import IndividualCustomerCreate, CreateOrganization, CreateEntrepreneur, PromisedPaymentForm
from pages.locators.promised_payment import PromisedPaymentPage
from pages.personal_account_page import PersonalAccountPage


@allure.epic("E2E_80 Управление обещанными платежами")
@allure.suite("E2E_80 Управление обещанными платежами")
@pytest.mark.usefixtures("nexign_ui_stand_login")
class TestConnectPromisedPayment:

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.personal_account_page = PersonalAccountPage(page)
        self.customer_create_form = IndividualCustomerCreate(page)
        self.organization_create_form = CreateOrganization(page)
        self.promised_payment = PromisedPaymentPage(page)
        self.promised_payment_form = PromisedPaymentForm(page)

    @allure.title("02. Успешное подключение ОП без комиссии ЮЛ")
    @allure.id(579874)
    def test_connect_promised_payment_b2b(self):
        self.personal_account_page.click_create_customer(type_customer='organisation')
        self.personal_account_page.dynamic_elements.INN.wait_to_be_visible()

        self.organization_create_form.fill_data_for_organization_client()
        self.personal_account_page.dynamic_form.SAVE_BTN.click()
        self.personal_account_page.notifications.SUCCESS_CREATE_CLIENT.wait_to_be_visible()

        self.personal_account_page.notifications.SUCCESS_NOTIFICATIONS_CLOSE_BTN.click()
        self.personal_account_page.locators.CREATE_AGREEMENT_BTN.click()
        self.personal_account_page.dynamic_elements.CONTRACT_NUM.wait_to_be_visible()

        self.personal_account_page.fill_data_create_agreement(type_client='organisation')
        self.personal_account_page.dynamic_form.CREATE_BTN.click()
        self.personal_account_page.notifications.SUCCESS_CREATE_CLIENT.wait_to_be_visible()

        self.personal_account_page.notifications.SUCCESS_NOTIFICATIONS_CLOSE_BTN.click()
        self.personal_account_page.locators.PERSONAL_ACCOUNTS_TAB.click()
        self.personal_account_page.locators.ADD_PERSONAL_ACCOUNT_BTN.click()
        self.personal_account_page.dynamic_form.CREATE_BTN.click()
        self.personal_account_page.notifications.SUCCESS_CREATE_CLIENT.wait_to_be_visible()
        self.personal_account_page.notifications.SUCCESS_NOTIFICATIONS_CLOSE_BTN.click()

        self.personal_account_page.base_elements.BURGER_MENU_BTN.click()
        self.personal_account_page.base_elements.BURGER_MENU_EL_BTN[3].click()

        self.promised_payment.CONNECT_BTN.wait_to_be_visible()
        self.promised_payment.CONNECT_BTN.click()
        self.promised_payment_form.CUSTOM_PARAM_BTN.click()
        self.promised_payment_form.fill_data_for_promised_payment()
        self.promised_payment_form.INNER_ACCEPT_BTN.click()
        self.personal_account_page.notifications.SUCCESS_CREATE_CLIENT.wait_to_be_visible()
        self.personal_account_page.notifications.SUCCESS_NOTIFICATIONS_CLOSE_BTN.click()

        self.promised_payment.PRODUCT_PROMISED_PAYMENT_FLD.wait_to_be_visible()

    @allure.title("01. Успешное подключение ОП без комиссии ФЛ")
    @allure.id(579843)
    def test_connect_promised_payment_b2c(self):
        self.personal_account_page.click_create_customer(type_customer='individual')
        self.personal_account_page.dynamic_elements.INN.wait_to_be_visible()

        self.customer_create_form.fill_data_for_individual_client()
        self.personal_account_page.dynamic_form.SAVE_BTN.click()
        self.personal_account_page.notifications.SUCCESS_CREATE_CLIENT.wait_to_be_visible()

        self.personal_account_page.notifications.SUCCESS_NOTIFICATIONS_CLOSE_BTN.click()
        self.personal_account_page.locators.CREATE_AGREEMENT_BTN.click()
        self.personal_account_page.dynamic_elements.CONTRACT_NUM.wait_to_be_visible()

        self.personal_account_page.fill_data_create_agreement(type_client='individual')
        self.personal_account_page.dynamic_form.CREATE_BTN.click()
        self.personal_account_page.notifications.SUCCESS_CREATE_CLIENT.wait_to_be_visible()

        self.personal_account_page.notifications.SUCCESS_NOTIFICATIONS_CLOSE_BTN.click()
        self.personal_account_page.locators.PERSONAL_ACCOUNTS_TAB.click()
        self.personal_account_page.locators.ADD_PERSONAL_ACCOUNT_BTN.click()
        self.personal_account_page.dynamic_form.CREATE_BTN.click()
        self.personal_account_page.notifications.SUCCESS_CREATE_CLIENT.wait_to_be_visible()
        self.personal_account_page.notifications.SUCCESS_NOTIFICATIONS_CLOSE_BTN.click()

        self.personal_account_page.base_elements.BURGER_MENU_BTN.click()
        self.personal_account_page.base_elements.BURGER_MENU_EL_BTN[3].click()

        self.promised_payment.CONNECT_BTN.wait_to_be_visible()
        self.promised_payment.CONNECT_BTN.click()
        self.promised_payment_form.CUSTOM_PARAM_BTN.click()
        self.promised_payment_form.fill_data_for_promised_payment()
        self.promised_payment_form.INNER_ACCEPT_BTN.click()
        self.personal_account_page.notifications.SUCCESS_CREATE_CLIENT.wait_to_be_visible()
        self.personal_account_page.notifications.SUCCESS_NOTIFICATIONS_CLOSE_BTN.click()

        self.promised_payment.PRODUCT_PROMISED_PAYMENT_FLD.wait_to_be_visible()
