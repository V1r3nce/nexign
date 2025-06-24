import allure
import pytest
from playwright.sync_api import Page

from models.user import OrganizationClient
from pages.locators.base_elements import BaseElements
from pages.locators.dynamic_form_elements import CreateOrganization, PromisedPaymentForm
from pages.locators.promised_payment import PromisedPaymentPage
from pages.personal_account_page import PersonalAccountPage


@allure.epic("E2E_80 Управление обещанными платежами")
@allure.suite("E2E_80 Управление обещанными платежами")
@pytest.mark.usefixtures("nexign_ui_stand_login")
class TestSomeActionsWithPromisedPayment:
    @pytest.fixture(autouse=True)
    def setup(self, page: Page, organization_user_data: OrganizationClient) -> None:
        self.personal_account_page = PersonalAccountPage(page, organization_user_data)
        self.promised_payment = PromisedPaymentPage(page)
        self.promised_payment_form = PromisedPaymentForm(page)
        self.base_elements = BaseElements(page)
        self.organization_create_form = CreateOrganization(page)

    @allure.title("05. Аннулирование ОП")
    @allure.id(581744)
    @pytest.mark.regress
    def test_cancellation_promised_payment(self) -> None:
        self.personal_account_page.create_customer_with_type("organization")
        self.organization_create_form.SAVE_BTN.click()
        self.personal_account_page.locators.INFO_MESSAGE.wait_to_be_visible()

        self.personal_account_page.locators.INFO_MESSAGE_CLOSE_BTN.click()
        self.personal_account_page.locators.CREATE_AGREEMENT_BTN.click()
        self.personal_account_page.dynamic_elements.CONTRACT_NUM.wait_to_be_visible()

        self.personal_account_page.fill_data_create_agreement(type_client="organization")
        self.personal_account_page.dynamic_form.CREATE_BTN.click()
        self.personal_account_page.locators.INFO_MESSAGE.wait_to_be_visible()

        self.personal_account_page.locators.INFO_MESSAGE_CLOSE_BTN.click()
        self.personal_account_page.locators.PERSONAL_ACCOUNTS_TAB.click()
        self.personal_account_page.locators.ADD_PERSONAL_ACCOUNT_BTN.click()
        self.personal_account_page.dynamic_form.CREATE_BTN.click()
        self.personal_account_page.locators.INFO_MESSAGE.wait_to_be_visible()
        self.personal_account_page.locators.INFO_MESSAGE_CLOSE_BTN.click()

        self.personal_account_page.base_elements.BURGER_MENU.select_by_value("Финансы > Обещанные платежи")

        self.promised_payment.CONNECT_BTN.wait_to_be_visible()
        self.promised_payment.CONNECT_BTN.click()

        self.promised_payment_form.CUSTOM_PARAM_BTN.click()
        self.promised_payment_form.fill_data_for_promised_payment()
        self.promised_payment_form.INNER_ACCEPT_BTN.click()
        self.personal_account_page.locators.INFO_MESSAGE.wait_to_be_visible()
        self.personal_account_page.locators.INFO_MESSAGE_CLOSE_BTN.click()
        self.promised_payment.PROMISED_PAYMENT_EL[0].wait_to_be_visible()

        self.personal_account_page.refresh_page(wait="domcontentloaded")
        self.promised_payment.PROMISED_PAYMENT_EL.wait_to_have_count(1)
        self.promised_payment.PROMISED_PAYMENT_EL[0].click()
        self.promised_payment.AN_CANCEL_BTN.click()

        self.promised_payment.COMMENT_FLD.fill("Это все для теста")
        self.promised_payment.AN_CANCEL_BTN_IN_FORM.click()
        self.personal_account_page.locators.INFO_MESSAGE.wait_to_be_visible()
        self.personal_account_page.locators.INFO_MESSAGE_CLOSE_BTN.click()

    @allure.title("08. Превышение срока ОП")
    @allure.id(584222)
    @pytest.mark.regress
    def test_excess_deadline_promised_payment(self) -> None:
        self.personal_account_page.create_customer_with_type("organization")
        self.personal_account_page.organization_create_form.SAVE_BTN.click()
        self.personal_account_page.locators.INFO_MESSAGE.wait_to_be_visible()

        self.personal_account_page.locators.INFO_MESSAGE_CLOSE_BTN.click()
        self.personal_account_page.locators.CREATE_AGREEMENT_BTN.click()
        self.personal_account_page.dynamic_elements.CONTRACT_NUM.wait_to_be_visible()

        self.personal_account_page.fill_data_create_agreement(type_client="organization")
        self.personal_account_page.dynamic_form.CREATE_BTN.click()
        self.personal_account_page.locators.INFO_MESSAGE.wait_to_be_visible()

        self.personal_account_page.locators.INFO_MESSAGE_CLOSE_BTN.click()
        self.personal_account_page.locators.PERSONAL_ACCOUNTS_TAB.click()
        self.personal_account_page.locators.ADD_PERSONAL_ACCOUNT_BTN.click()
        self.personal_account_page.dynamic_form.CREATE_BTN.click()
        self.personal_account_page.locators.INFO_MESSAGE.wait_to_be_visible()
        self.personal_account_page.locators.INFO_MESSAGE_CLOSE_BTN.click()

        self.personal_account_page.base_elements.BURGER_MENU.select_by_value("Финансы > Обещанные платежи")

        self.promised_payment.CONNECT_BTN.wait_to_be_visible()
        self.promised_payment.CONNECT_BTN.click()

        self.promised_payment_form.CUSTOM_PARAM_BTN.click()
        self.promised_payment_form.fill_data_for_promised_payment(duration="61")
        self.promised_payment_form.INNER_ACCEPT_BTN.click()
        self.base_elements.MODAL.wait_to_be_visible()

    @allure.title("10. Превышение суммы ОП")
    @allure.id(584285)
    @pytest.mark.regress
    def test_excess_amount_promised_payment(self) -> None:
        self.personal_account_page.create_customer_with_type("organization")
        self.personal_account_page.organization_create_form.SAVE_BTN.click()
        self.personal_account_page.locators.INFO_MESSAGE.wait_to_be_visible()

        self.personal_account_page.locators.INFO_MESSAGE_CLOSE_BTN.click()
        self.personal_account_page.locators.CREATE_AGREEMENT_BTN.click()
        self.personal_account_page.dynamic_elements.CONTRACT_NUM.wait_to_be_visible()

        self.personal_account_page.fill_data_create_agreement(type_client="organization")
        self.personal_account_page.dynamic_form.CREATE_BTN.click()
        self.personal_account_page.locators.INFO_MESSAGE.wait_to_be_visible()

        self.personal_account_page.locators.INFO_MESSAGE_CLOSE_BTN.click()
        self.personal_account_page.locators.PERSONAL_ACCOUNTS_TAB.click()
        self.personal_account_page.locators.ADD_PERSONAL_ACCOUNT_BTN.click()
        self.personal_account_page.dynamic_form.CREATE_BTN.click()
        self.personal_account_page.locators.INFO_MESSAGE.wait_to_be_visible()
        self.personal_account_page.locators.INFO_MESSAGE_CLOSE_BTN.click()

        self.personal_account_page.base_elements.BURGER_MENU.select_by_value("Финансы > Обещанные платежи")

        self.promised_payment.CONNECT_BTN.wait_to_be_visible()
        self.promised_payment.CONNECT_BTN.click()

        self.promised_payment_form.CUSTOM_PARAM_BTN.click()
        self.promised_payment_form.fill_data_for_promised_payment(amount="1100")
        self.promised_payment_form.INNER_ACCEPT_BTN.click()
        self.base_elements.MODAL.wait_to_be_visible()

    @allure.title("06. Просмотр статусов ОП")
    @allure.id(581748)
    @pytest.mark.regress
    def test_check_status_promised_payment(self) -> None:
        self.personal_account_page.create_customer_with_type("organization")
        self.personal_account_page.organization_create_form.SAVE_BTN.click()
        self.personal_account_page.locators.INFO_MESSAGE.wait_to_be_visible()

        self.personal_account_page.locators.INFO_MESSAGE_CLOSE_BTN.click()
        self.personal_account_page.locators.CREATE_AGREEMENT_BTN.click()
        self.personal_account_page.dynamic_elements.CONTRACT_NUM.wait_to_be_visible()

        self.personal_account_page.fill_data_create_agreement(type_client="organization")
        self.personal_account_page.dynamic_form.CREATE_BTN.click()
        self.personal_account_page.locators.INFO_MESSAGE.wait_to_be_visible()

        self.personal_account_page.locators.INFO_MESSAGE_CLOSE_BTN.click()
        self.personal_account_page.locators.PERSONAL_ACCOUNTS_TAB.click()
        self.personal_account_page.locators.ADD_PERSONAL_ACCOUNT_BTN.click()
        self.personal_account_page.dynamic_form.CREATE_BTN.click()
        self.personal_account_page.locators.INFO_MESSAGE.wait_to_be_visible()
        self.personal_account_page.locators.INFO_MESSAGE_CLOSE_BTN.click()

        self.personal_account_page.base_elements.BURGER_MENU.select_by_value("Финансы > Обещанные платежи")

        self.promised_payment.CONNECT_BTN.wait_to_be_visible()
        self.promised_payment.CONNECT_BTN.click()

        self.promised_payment_form.CUSTOM_PARAM_BTN.click()
        self.promised_payment_form.fill_data_for_promised_payment()
        self.promised_payment_form.INNER_ACCEPT_BTN.click()
        self.personal_account_page.locators.INFO_MESSAGE.wait_to_be_visible()
        self.personal_account_page.locators.INFO_MESSAGE_CLOSE_BTN.click()
        self.promised_payment.PROMISED_PAYMENT_EL[0].wait_to_be_visible()

        self.personal_account_page.refresh_page(wait="domcontentloaded")
        self.promised_payment.PROMISED_PAYMENT_EL.wait_to_have_count(1)
        self.promised_payment.PROMISED_PAYMENT_EL[0].click()
        self.promised_payment.STATUS_HISTORY_BTN.wait_to_be_visible()
        self.promised_payment.STATUS_HISTORY_BTN.click()

        self.promised_payment.STATUS_PAYMENTS_FORM.wait_to_be_visible()

    @allure.title("09. Превышение размера комиссии")
    @allure.id(584260)
    @pytest.mark.regress
    def test_excess_commission_amount(self) -> None:
        self.personal_account_page.create_customer_with_type("organization")
        self.personal_account_page.organization_create_form.SAVE_BTN.click()
        self.personal_account_page.locators.INFO_MESSAGE.wait_to_be_visible()

        self.personal_account_page.locators.INFO_MESSAGE_CLOSE_BTN.click()
        self.personal_account_page.locators.CREATE_AGREEMENT_BTN.click()
        self.personal_account_page.dynamic_elements.CONTRACT_NUM.wait_to_be_visible()

        self.personal_account_page.fill_data_create_agreement(type_client="organization")
        self.personal_account_page.dynamic_form.CREATE_BTN.click()
        self.personal_account_page.locators.INFO_MESSAGE.wait_to_be_visible()

        self.personal_account_page.locators.INFO_MESSAGE_CLOSE_BTN.click()
        self.personal_account_page.locators.PERSONAL_ACCOUNTS_TAB.click()
        self.personal_account_page.locators.ADD_PERSONAL_ACCOUNT_BTN.click()
        self.personal_account_page.dynamic_form.CREATE_BTN.click()
        self.personal_account_page.locators.INFO_MESSAGE.wait_to_be_visible()
        self.personal_account_page.locators.INFO_MESSAGE_CLOSE_BTN.click()

        self.personal_account_page.base_elements.BURGER_MENU.select_by_value("Финансы > Обещанные платежи")

        self.promised_payment.CONNECT_BTN.wait_to_be_visible()
        self.promised_payment.CONNECT_BTN.click()

        self.promised_payment_form.CUSTOM_PARAM_BTN.click()
        self.promised_payment_form.fill_data_for_promised_payment(commission="605")
        self.promised_payment_form.INNER_ACCEPT_BTN.click()
        self.base_elements.MODAL.wait_to_be_visible()
