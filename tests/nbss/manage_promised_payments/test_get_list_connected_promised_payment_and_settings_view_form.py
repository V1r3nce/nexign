import allure
import pytest

from common.helpers.env_helper import BASE_URL
from common.helpers.time_helpers import delay
from models.client import OrganizationClient
from pages.base_page import BasePage
from pages.locators.nbss.dynamic_form_elements import PromisedPaymentForm
from pages.locators.nbss.finances.promised_payment import PromisedPaymentPageElements
from pages.nbss.personal_account_page import PersonalAccountPage


@allure.epic("E2E_80 Управление обещанными платежами")
@allure.suite("E2E_80 Управление обещанными платежами")
@pytest.mark.nbss_portal
class TestGetSettingsPromisedPayment:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login, organization_user_data: OrganizationClient) -> None:
        self.personal_account_page = PersonalAccountPage(organization_user_data)
        self.promised_payment = PromisedPaymentPageElements()
        self.promised_payment_form = PromisedPaymentForm()
        self.base_page = BasePage()

    @allure.title("03. Получение списка подключенных ОП и настройка вида формы ОП")
    @allure.id(581262)
    @pytest.mark.regress
    def test_get_list_connected_promised_payment(
        self, create_organization_with_agreement_and_account: OrganizationClient
    ) -> None:
        client_b2b = create_organization_with_agreement_and_account
        self.base_page.open(
            f"{BASE_URL}customer-hierarchy-management/accounts/{client_b2b.agreements[0].accounts[0].id}/account"
        )

        self.personal_account_page.base_elements.BURGER_MENU.select_by_value("Финансы > Обещанные платежи")

        self.promised_payment.CONNECT_BTN.wait_to_be_visible()
        self.promised_payment.CONNECT_BTN.click()
        self.promised_payment_form.CUSTOM_PARAM_BTN.click()
        self.promised_payment_form.fill_data_for_promised_payment()
        self.promised_payment_form.INNER_ACCEPT_BTN.click()
        self.personal_account_page.locators.INFO_MESSAGE.wait_to_be_visible()
        self.personal_account_page.locators.INFO_MESSAGE_CLOSE_BTN.click()
        self.promised_payment.PROMISED_PAYMENT_EL[0].wait_to_be_visible()
        self.base_page.refresh_page(wait="domcontentloaded")
        self.promised_payment.PROMISED_PAYMENT_EL.wait_to_have_count(1)
        self.promised_payment.PROMISED_PAYMENT_EL[0].click()
        self.promised_payment.AN_CANCEL_BTN.click()
        self.promised_payment.AN_CANCEL_BTN_IN_FORM.click()
        self.personal_account_page.locators.INFO_MESSAGE.wait_to_be_visible()
        self.personal_account_page.locators.INFO_MESSAGE_CLOSE_BTN.click()
        delay(2, reason="не успевает выполниться запрос с прошлого шага, это ожидание нужно")

        self.promised_payment.CONNECT_BTN.wait_to_be_visible()
        self.promised_payment.CONNECT_BTN.click()
        self.promised_payment_form.CUSTOM_PARAM_BTN.click()
        self.promised_payment_form.fill_data_for_promised_payment()
        self.promised_payment_form.INNER_ACCEPT_BTN.click()
        self.personal_account_page.locators.INFO_MESSAGE.wait_to_be_visible()
        self.personal_account_page.locators.INFO_MESSAGE_CLOSE_BTN.click()

        self.promised_payment.PROMISED_PAYMENT_EL.wait_to_have_count(2)
        self.promised_payment.PROMISED_PAYMENT_EL[1].wait_to_be_visible()
        self.promised_payment.CHARACTERISTICS_BTN.click()
        self.promised_payment.CHARACTERISTICS_FLD.wait_to_have_count(12)
        self.promised_payment.choose_characteristics()
