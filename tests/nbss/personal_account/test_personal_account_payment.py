import allure
import pytest

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from api.nbss.finances.payments_requests import PaymentInfo, PaymentsRequests
from common.helpers.data_generator import generate_random_number, get_current_datetime_string_for_api
from models.inquiry import prepare_inquiries
from models.user import IndividualClient, OrganizationClient
from pages.nbss.client.client_profile_page import ClientProfilePage


@allure.epic("E2E_33_1 Подключение персональных счетов")
@allure.suite("E2E_33_1 Подключение персональных счетов")
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestPersonalAccountPayment:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login) -> None:
        self.client_profile_page = ClientProfilePage()
        self.payments_request = PaymentsRequests()
        self.client_requests = ClientInquiriesRequests()

        self.today_with_time = get_current_datetime_string_for_api(True)

    @allure.title("17 Платеж по номеру Абонента")
    @allure.id(586645)
    @allure.link(
        url="allure.nexign.com/project/313/test-cases/586645",
        name="17 Платеж по номеру Абонента",
    )
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=691454115",
        name="КР [UDS] Управление персональными счетами без управления лимитами (Детальное)",
    )
    @pytest.mark.smoke
    def test_add_payment_to_priority_account(
        self,
        create_individual_user: IndividualClient,
        create_organization: OrganizationClient,
        base_url: str,
    ) -> None:
        client_b2c = create_individual_user
        client_b2b = create_organization

        self.client_profile_page.open(f"{base_url}customer-hierarchy-management/customers/{client_b2b.user_id}/overview")

        inquiry = self.client_requests.product_sale(inquiry=prepare_inquiries("internet"))

        self.client_profile_page.locators.PRODUCTS_TAB.click()
        self.client_profile_page.locators.SUBSCRIBER.click(0)
        self.client_profile_page.add_existing_end_user(client_b2c)
        self.client_profile_page.end_user_form.CLOSE_END_USER_MODAL_BUTTON.click()

        payment = PaymentInfo(
            amount=3000,
            document_number=generate_random_number(8),
            item_type="PHONE_NUMBER",
            phone_number=inquiry.product.internet_number,
        )
        self.payments_request.create_payment(payment)

        self.client_profile_page.locators.RELATED_PERSONS_TAB.click()
        self.client_profile_page.locators.RELATED_PERSONS.click(1)
        self.client_profile_page.locators.RELATED_PERSON_CLIENT_FL.click()
        self.client_profile_page.locators.OVERVIEW_TAB.click()
        self.client_profile_page.check_balance(0, 3000.00)

    @allure.title("18 Установить приоритетный ЛС для приема платежей по Абоненту")
    @allure.id(586644)
    @allure.link(
        url="allure.nexign.com/project/313/test-cases/586644",
        name="18 Установить приоритетный ЛС для приема платежей по Абоненту",
    )
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=691454115",
        name="КР [UDS] Управление персональными счетами без управления лимитами (Детальное)",
    )
    def test_set_personal_account_payment_priority(
        self,
        create_individual_user: IndividualClient,
        create_organization: OrganizationClient,
        base_url: str,
    ) -> None:
        client_b2c = create_individual_user
        client_b2b = create_organization

        self.client_profile_page.open(f"{base_url}customer-hierarchy-management/customers/{client_b2b.user_id}/overview")

        self.client_requests.product_sale(client_b2b, prepare_inquiries("internet"))

        self.client_profile_page.locators.PRODUCTS_TAB.click()
        self.client_profile_page.locators.SUBSCRIBER.click(0)
        self.client_profile_page.add_existing_end_user(client_b2c)
        self.client_profile_page.end_user_form.CLOSE_END_USER_MODAL_BUTTON.click()

        self.client_profile_page.locators.RELATED_PERSONS_TAB.click()
        self.client_profile_page.locators.RELATED_PERSONS.click(1)
        self.client_profile_page.locators.RELATED_PERSON_CLIENT_FL.click()
        self.client_profile_page.locators.OVERVIEW_TAB.click()

        self.client_profile_page.locators.WIDGET_PERSONAL_ACCOUNT_IDS.click(0)
        self.client_profile_page.personal_account.ACCOUNT_PRIORITY.to_contain_text("Да")
        self.client_profile_page.locators.EDIT_BTN.click()
        self.client_profile_page.personal_account.ACCOUNT_PRIORITY_INPUT.click()
        self.client_profile_page.personal_account.SAVE_BTN.click()
        self.client_profile_page.refresh_page("domcontentloaded")
        self.client_profile_page.personal_account.ACCOUNT_PRIORITY.to_contain_text("Нет")
