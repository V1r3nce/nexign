import allure
import pytest

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from api.nbss.client_requests.client_requests import ClientRequests
from api.nbss.finances.payments_requests import PaymentsRequests
from models.context import test_context
from models.inquiry import prepare_inquiries
from models.user import IndividualClient, OrganizationClient
from pages.locators.nbss.client.client_search import ClientSearch
from pages.locators.nbss.dynamic_form_elements import AddOptionsForm
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.inquiries_page import InquiriesPage


@allure.epic("E2E_33_1 Подключение персональных счетов")
@allure.suite("E2E_33_1 Подключение персональных счетов")
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestPersonalAccountView:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login) -> None:
        self.client_profile_page = ClientProfilePage()
        self.client_requests = ClientRequests()
        self.client_inquiries_requests = ClientInquiriesRequests()
        self.client_search = ClientSearch()
        self.add_options_form = AddOptionsForm()
        self.payments_request = PaymentsRequests()
        self.inquiries_page = InquiriesPage()

    @allure.title("08 Поиск клиента по абоненту (UI)")
    @allure.id(584090)
    @allure.link(
        url="allure.nexign.com/project/313/test-cases/584090",
        name="08 Поиск клиента по абоненту (UI)",
    )
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=691454115",
        name="КР [UDS] Управление персональными счетами без управления лимитами (Детальное)",
    )
    def test_search_client_by_subscriber(
        self,
        create_individual_user: IndividualClient,
        create_organization: OrganizationClient,
        base_url: str,
    ) -> None:
        client_b2c = create_individual_user
        client_b2b = create_organization

        self.client_profile_page.open(f"{base_url}customer-hierarchy-management/customers/{client_b2b.user_id}/overview")

        inquiry = self.client_inquiries_requests.product_sale(client_b2b, prepare_inquiries("internet"))

        self.client_profile_page.locators.PRODUCTS_TAB.click()
        self.client_profile_page.locators.SUBSCRIBER.click(0)
        self.client_profile_page.add_existing_end_user(client_b2c)
        self.client_profile_page.end_user_form.CLOSE_END_USER_MODAL_BUTTON.click()

        self.client_profile_page.locators.HEADER_SUBSCRIBER.fill(inquiry.product.internet_number)
        self.client_profile_page.locators.HEADER_SEARCH_BTN.click()
        self.client_search.CONTRACT_STATUS.clear_select()
        self.client_search.SEARCH_BTN.click()

        client_b2b_name = self.client_requests.get_client_data(test_context.client.user_id).json()["party"]["nameInfo"][
            "corporateName"
        ]

        self.client_search.FOUNDED_FIO.wait_to_have_count(2)
        self.client_search.FOUNDED_FIO[0].to_contain_text(client_b2b_name)
        self.client_search.FOUNDED_FIO[1].to_contain_text(
            f"{client_b2c.sur_name} {client_b2c.first_name} {client_b2c.patronymic}"
        )

    @allure.title("09 Просмотр Продуктовового профиля Корпоративного клиента (ППК режим По абонентам)")
    @allure.id(585916)
    @allure.link(
        url="allure.nexign.com/project/313/test-cases/585916",
        name="09 Просмотр Продуктовового профиля Корпоративного клиента (ППК режим По абонентам)",
    )
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=691454115",
        name="КР [UDS] Управление персональными счетами без управления лимитами (Детальное)",
    )
    @pytest.mark.smoke
    def test_view_product_profile_for_corporate_client_subscriber_mode(
        self,
        create_individual_user: IndividualClient,
        create_organization: OrganizationClient,
        base_url: str,
    ) -> None:
        client_b2c = create_individual_user
        client_b2b = create_organization

        self.client_profile_page.open(f"{base_url}customer-hierarchy-management/customers/{client_b2b.user_id}/overview")

        self.client_inquiries_requests.product_sale(client_b2b, prepare_inquiries("internet"))

        self.payments_request.create_default_payment(test_context.client.agreements[0].accounts[0].id, 3000.0)

        self.client_profile_page.locators.PRODUCTS_TAB.click()
        self.client_profile_page.locators.SUBSCRIBER.click(0)
        self.client_profile_page.add_existing_end_user(client_b2c)
        self.client_profile_page.end_user_form.CLOSE_END_USER_MODAL_BUTTON.click()

        self.client_profile_page.locators.PRODUCTS_OPTIONS_OPEN_BTN[0].click()
        self.client_profile_page.locators.PRODUCTS_OPTIONS_ADD_BTN.click()

        self.add_options_form.SEARCH_OPTIONS_FLD.fill("Безлимит ВК Видео")
        self.add_options_form.SEARCH_BTN.click()
        self.add_options_form.CHOSE_OPTION_BTN.wait_elements_visible(element_index=0)
        self.add_options_form.CHOSE_OPTION_BTN[0].click()
        self.add_options_form.PERSONAL_ACCOUNT_CHECKBOX.click(0)
        self.add_options_form.INNER_ACCEPT_BTN.click()

        self.add_options_form.PERSONAL_ACCOUNT_MODAL_FIELDS.to_contain_text(
            0,
            f"{client_b2c.sur_name} {client_b2c.first_name} {client_b2c.patronymic}",
        )
        self.add_options_form.PERSONAL_ACCOUNT_MODAL_FIELDS.to_contain_text(1, client_b2c.document_type)
        self.add_options_form.PERSONAL_ACCOUNT_MODAL_FIELDS.to_contain_text(
            2, f"{client_b2c.document_serial} {client_b2c.document_num}"
        )
        self.add_options_form.PERSONAL_ACCOUNT_MODAL_FIELDS.to_contain_text(3, client_b2c.document_division_code)
        self.add_options_form.PERSONAL_ACCOUNT_MODAL_FIELDS.to_contain_text(4, client_b2c.issue_date)
        self.add_options_form.PERSONAL_ACCOUNT_MODAL_FIELDS.to_contain_text(5, client_b2c.registration_address)
        self.add_options_form.MODAL_SECOND_BTN.click()

        self.client_profile_page.locators.PRODUCTS_UPDATE_BTN.wait_to_be_visible()

        self.client_profile_page.locators.REQUESTS_TAB.click()
        self.inquiries_page.locators.LOAD_SPIN_SECOND.not_to_be_visible(timeout=80000)
        self.client_profile_page.locators.REQUEST_NUMBER[1].wait_to_be_visible()
        self.client_profile_page.locators.REQUEST_NUMBER[1].click()
        self.inquiries_page.locators.LOAD_SPIN_SECOND.not_to_be_visible(timeout=80000)
        self.inquiries_page.locators.SUCCESS_SETUP.wait_to_be_visible()

        self.client_profile_page.locators.CURRENT_CLIENT_LINK.click()
        self.client_profile_page.locators.PRODUCTS_TAB.click()
        self.client_profile_page.locators.OPEN_OPTIONS_BTN.click(0)
        self.client_profile_page.locators.PERSONAL_ACCOUNT_OPTION_ICON.wait_to_be_visible()
        self.client_profile_page.locators.wait_to_be_enabled(type_offer="option")

        self.client_profile_page.locators.SUBSCRIBER.click(0)
        self.client_profile_page.check_end_user_form(client_b2c)
