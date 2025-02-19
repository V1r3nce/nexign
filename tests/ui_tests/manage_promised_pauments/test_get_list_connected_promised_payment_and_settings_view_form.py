import allure
import pytest
from playwright.sync_api import Page

from common.helpers.time_helpers import delay
from pages.base_page import BasePage
from pages.locators.dynamic_form_elements import  PromisedPaymentForm
from pages.locators.promised_payment import PromisedPaymentPage
from pages.personal_account_page import PersonalAccountPage


@allure.epic("E2E_80 Управление обещанными платежами")
@allure.suite("E2E_80 Управление обещанными платежами")
@pytest.mark.usefixtures("nexign_ui_stand_login")
class TestGetSettingsPromisedPayment:

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.personal_account_page = PersonalAccountPage(page)
        self.promised_payment = PromisedPaymentPage(page)
        self.promised_payment_form = PromisedPaymentForm(page)
        self.base_page = BasePage(page)

    @allure.title("03. Получение списка подключенных ОП и настройка вида формы ОП")
    @allure.id(581262)
    def test_get_list_connected_promised_payment(self):
        self.personal_account_page.create_customer_with_type('organization')
        self.personal_account_page.dynamic_form.SAVE_BTN.click()
        self.personal_account_page.notifications.SUCCESS_CREATE_CLIENT.wait_to_be_visible()

        self.personal_account_page.notifications.SUCCESS_NOTIFICATIONS_CLOSE_BTN.click()
        self.personal_account_page.locators.CREATE_AGREEMENT_BTN.click()
        self.personal_account_page.dynamic_elements.CONTRACT_NUM.wait_to_be_visible()

        self.personal_account_page.fill_data_create_agreement(type_client='organization')
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
        self.promised_payment.PROMISED_PAYMENT_EL[0].wait_to_be_visible()
        self.base_page.refresh_page(wait='domcontentloaded')
        self.promised_payment.PROMISED_PAYMENT_EL.wait_to_have_count(1)
        self.promised_payment.PROMISED_PAYMENT_EL[0].click()
        self.promised_payment.AN_CANCEL_BTN.click()
        self.promised_payment.AN_CANCEL_BTN_IN_FORM.click()
        delay(2, reason="не успевает выполниться запрос с прошлого шага, это ожидание нужно")

        self.promised_payment.CONNECT_BTN.wait_to_be_visible()
        self.promised_payment.CONNECT_BTN.click()
        self.promised_payment_form.CUSTOM_PARAM_BTN.click()
        self.promised_payment_form.fill_data_for_promised_payment()
        self.promised_payment_form.INNER_ACCEPT_BTN.click()
        self.personal_account_page.notifications.SUCCESS_CREATE_CLIENT.wait_to_be_visible()
        self.personal_account_page.notifications.SUCCESS_NOTIFICATIONS_CLOSE_BTN.click()

        self.promised_payment.PROMISED_PAYMENT_EL.wait_to_have_count(2)
        self.promised_payment.PROMISED_PAYMENT_EL[1].wait_to_be_visible()
