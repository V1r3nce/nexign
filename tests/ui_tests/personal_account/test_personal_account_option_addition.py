import allure
import pytest
from playwright.sync_api import APIRequestContext, Page

from api.requests.client_requests.client_inquiries_requests import ClientInquiriesRequests
from api.requests.payments_requests import PaymentsRequests
from api.requests.personal_account_requests import PersonalAccountRequests
from common.helpers.data_generator import get_current_datetime_string
from common.helpers.time_helpers import get_shifted_datetime
from models.user import IndividualClient, OrganizationClient
from pages.client_profile_page import ClientProfilePage
from pages.inquiries_page import InquiriesPage
from pages.locators.dynamic_form_elements import AddOptionsForm


@allure.epic("E2E_33_1 Подключение персональных счетов")
@allure.suite("E2E_33_1 Подключение персональных счетов")
@pytest.mark.regress
class TestPersonalAccountOptionAddition:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_ui_stand_login: Page, api_request_auth_context: APIRequestContext) -> None:
        self.client_profile_page = ClientProfilePage(nexign_ui_stand_login)
        self.payments_request = PaymentsRequests(api_request_auth_context)
        self.personal_account_requests = PersonalAccountRequests(api_request_auth_context)
        self.add_options_form = AddOptionsForm(nexign_ui_stand_login)
        self.client_requests = ClientInquiriesRequests(api_request_auth_context)
        self.inquiries_page = InquiriesPage(nexign_ui_stand_login)

        self.today = get_current_datetime_string(False)
        self.last_year_plus_day = get_shifted_datetime("-499d").strftime("%d.%m.%Y")
        self.next_year_plus_day = get_shifted_datetime("+501d").strftime("%d.%m.%Y")

    @allure.title("12 Добавление опции через ППК Корпоративного клиента(Персональный счет существует)")
    @allure.id(585918)
    @allure.link(
        url="allure.nexign.com/project/313/test-cases/585918",
        name="12 Добавление опции через ППК Корпоративного клиента(Персональный счет существует)",
    )
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=691454115",
        name="КР [UDS] Управление персональными счетами без управления лимитами (Детальное)",
    )
    @pytest.mark.smoke
    def test_add_option_to_existing_personal_account(
        self,
        create_individual_user: IndividualClient,
        create_organization: OrganizationClient,
        base_url: str,
    ) -> None:
        client_b2c = create_individual_user
        client_b2b = create_organization

        self.client_profile_page.open(f"{base_url}customer-hierarchy-management/customers/{client_b2b.user_id}/overview")

        client, product = self.client_requests.product_sale(
            user_id=client_b2b.user_id, category="internet", product_offering_id=500001
        )

        self.payments_request.create_default_payment(client.agreements[0].accounts[0].id, 3000.0)

        self.client_profile_page.locators.PRODUCTS_TAB.click()
        self.client_profile_page.locators.SUBSCRIBER.click(0)
        self.client_profile_page.add_existing_end_user(client_b2c)
        self.client_profile_page.end_user_form.CLOSE_END_USER_MODAL_BUTTON.click()

        self.client_profile_page.locators.PRODUCTS_OPTIONS_OPEN_BTN[0].click()
        self.client_profile_page.locators.PRODUCTS_OPTIONS_ADD_BTN.click()

        self.add_options_form.SEARCH_BTN.wait_to_be_visible()
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

        b2c_account_id = self.personal_account_requests.get_personal_accounts("customer", client_b2c.user_id).json()[
            "items"
        ][0]["accountId"]
        self.payments_request.create_default_payment(b2c_account_id, 3000.0)

        self.inquiries_page.locators.TABS[1].click()
        self.inquiries_page.locators.PRODUCTS[1].wait_to_be_visible(timeout=80000)
        self.inquiries_page.locators.PERSONAL_ACCOUNT_OPTION_ICON.wait_to_be_visible()

        self.client_profile_page.locators.CURRENT_CLIENT_LINK.click()
        self.client_profile_page.locators.PRODUCTS_TAB.click()
        self.client_profile_page.locators.OPEN_OPTIONS_BTN.click(0)
        self.client_profile_page.locators.PERSONAL_ACCOUNT_OPTION_ICON.wait_to_be_visible()
        self.client_profile_page.locators.wait_to_be_enabled(type_offer="option")

        self.client_profile_page.locators.RELATED_PERSONS_TAB.click()
        self.client_profile_page.locators.RELATED_PERSONS.click(1)
        self.client_profile_page.locators.RELATED_PERSON_CLIENT_FL.click()
        self.client_profile_page.locators.PRODUCTS_TAB.click()
        self.client_profile_page.locators.OPEN_OPTIONS_BTN.click(0)
        self.client_profile_page.locators.PERSONAL_ACCOUNT_OPTION_ICON.wait_to_be_visible()
        self.client_profile_page.locators.wait_to_be_enabled(type_offer="option")

    @allure.title("13 Добавление опции через ППК Корпоративного клиента(Если Персонального счёта нет:)")
    @allure.id(586640)
    @allure.link(
        url="allure.nexign.com/project/313/test-cases/586640",
        name="13 Добавление опции через ППК Корпоративного клиента(Если Персонального счёта нет:)",
    )
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=691454115",
        name="КР [UDS] Управление персональными счетами без управления лимитами (Детальное)",
    )
    def test_add_option_when_personal_account_not_exists(
        self, create_organization: OrganizationClient, base_url: str, individual_user_data: IndividualClient
    ) -> None:
        user_data = individual_user_data
        client_b2b = create_organization
        self.client_profile_page.open(f"{base_url}customer-hierarchy-management/customers/{client_b2b.user_id}/overview")

        client, product = self.client_requests.product_sale(
            user_id=client_b2b.user_id, category="internet", product_offering_id=500001
        )

        self.payments_request.create_default_payment(client.agreements[0].accounts[0].id, 3000.0)

        self.client_profile_page.locators.PRODUCTS_TAB.click()
        self.client_profile_page.locators.SUBSCRIBER.click(0)
        self.client_profile_page.add_non_existing_end_user(user_data)
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
            f"{user_data.sur_name} {user_data.first_name} {user_data.patronymic}",
        )
        self.add_options_form.PERSONAL_ACCOUNT_MODAL_FIELDS.to_contain_text(1, user_data.document_type)
        self.add_options_form.PERSONAL_ACCOUNT_MODAL_FIELDS.to_contain_text(
            2, f"{user_data.document_serial} {user_data.document_num}"
        )
        self.add_options_form.PERSONAL_ACCOUNT_MODAL_FIELDS.to_contain_text(3, user_data.document_division_code)
        self.add_options_form.PERSONAL_ACCOUNT_MODAL_FIELDS.to_contain_text(4, user_data.issue_date)
        self.add_options_form.PERSONAL_ACCOUNT_MODAL_FIELDS.to_contain_text(5, user_data.registration_address)
        self.add_options_form.MODAL_SECOND_BTN.click()

        self.client_profile_page.locators.PRODUCTS_UPDATE_BTN.wait_to_be_visible()

        self.client_profile_page.locators.REQUESTS_TAB.click()
        self.inquiries_page.locators.LOAD_SPIN_SECOND.not_to_be_visible(timeout=80000)
        self.client_profile_page.locators.REQUEST_NUMBER[1].wait_to_be_visible()
        self.client_profile_page.locators.REQUEST_NUMBER[1].click()
        self.inquiries_page.locators.LOAD_SPIN_SECOND.not_to_be_visible(timeout=80000)
        self.inquiries_page.locators.SUCCESS_SETUP.wait_to_be_visible()

        self.inquiries_page.locators.TABS[1].click()
        self.inquiries_page.locators.PRODUCTS[1].wait_to_be_visible(timeout=80000)
        self.inquiries_page.locators.PERSONAL_ACCOUNT_OPTION_ICON.wait_to_be_visible()

        self.client_profile_page.locators.CURRENT_CLIENT_LINK.click()
        self.client_profile_page.locators.PRODUCTS_TAB.click()
        self.client_profile_page.locators.OPEN_OPTIONS_BTN.click()
        self.client_profile_page.locators.PERSONAL_ACCOUNT_OPTION_ICON.wait_to_be_visible()
        self.client_profile_page.locators.wait_to_be_enabled(type_offer="option")

        self.client_profile_page.locators.RELATED_PERSONS_TAB.click()
        self.client_profile_page.locators.RELATED_PERSON_CLIENT_FL.click()
        self.client_profile_page.locators.PRODUCTS_TAB.click()
        self.client_profile_page.locators.OPEN_PRODUCT_BTN.click()
        self.client_profile_page.locators.OPEN_OPTIONS_BTN.click()
        self.client_profile_page.locators.PERSONAL_ACCOUNT_OPTION_ICON.wait_to_be_visible()
        self.client_profile_page.locators.wait_to_be_enabled(type_offer="option")

    @allure.title("16 Добавление опции через ППК Физического клиента")
    @allure.id(586643)
    @allure.link(
        url="allure.nexign.com/project/313/test-cases/586643",
        name="16 Добавление опции через ППК Физического клиента",
    )
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=691454115",
        name="КР [UDS] Управление персональными счетами без управления лимитами (Детальное)",
    )
    def test_add_option_to_personal_account_from_b2c_client(
        self,
        create_individual_user: IndividualClient,
        create_organization: OrganizationClient,
        base_url: str,
    ) -> None:
        client_b2c = create_individual_user
        client_b2b = create_organization
        self.client_profile_page.open(f"{base_url}customer-hierarchy-management/customers/{client_b2b.user_id}/overview")

        client, product = self.client_requests.product_sale(
            user_id=client_b2b.user_id, category="internet", product_offering_id=500001
        )

        self.payments_request.create_default_payment(client.agreements[0].accounts[0].id, 3000.0)

        self.client_profile_page.locators.PRODUCTS_TAB.click()
        self.client_profile_page.locators.SUBSCRIBER.click(0)
        self.client_profile_page.add_existing_end_user(client_b2c)
        self.client_profile_page.end_user_form.CLOSE_END_USER_MODAL_BUTTON.click()

        self.client_profile_page.locators.RELATED_PERSONS_TAB.click()
        self.client_profile_page.locators.RELATED_PERSONS.click(1)
        self.client_profile_page.locators.RELATED_PERSON_CLIENT_FL.click()

        self.client_profile_page.locators.PRODUCTS_TAB.click()
        self.client_profile_page.locators.PRODUCTS_OPTIONS_OPEN_BTN[0].click()
        self.client_profile_page.locators.PRODUCTS_OPTIONS_ADD_BTN.click()

        self.add_options_form.PERSONAL_ACCOUNT_CHARGING_TEXT.to_contain_text(
            "Списания по выбранным продуктам будут происходить с персонального счета абонента"
        )
        self.add_options_form.SEARCH_OPTIONS_FLD.fill("Безлимит ВК Видео")
        self.add_options_form.SEARCH_BTN.click()
        self.add_options_form.CHOSE_OPTION_BTN.wait_elements_visible(element_index=0)
        self.add_options_form.CHOSE_OPTION_BTN[0].click()
        self.add_options_form.PERSONAL_ACCOUNT_CHECKBOX.click(0)
        self.add_options_form.INNER_ACCEPT_BTN.click()

        self.client_profile_page.locators.PRODUCTS_UPDATE_BTN.wait_to_be_visible()

        self.client_profile_page.locators.REQUESTS_TAB.click()
        self.inquiries_page.locators.LOAD_SPIN_SECOND.not_to_be_visible(timeout=80000)
        self.client_profile_page.locators.REQUEST_NUMBER[1].wait_to_be_visible()
        self.client_profile_page.locators.REQUEST_NUMBER[1].click()
        self.inquiries_page.locators.LOAD_SPIN_SECOND.not_to_be_visible(timeout=80000)
        self.inquiries_page.locators.SUCCESS_SETUP.wait_to_be_visible()

        b2c_account_id = self.personal_account_requests.get_personal_accounts("customer", client_b2c.user_id).json()[
            "items"
        ][0]["accountId"]
        self.payments_request.create_default_payment(b2c_account_id, 3000.0)

        self.inquiries_page.locators.TABS[1].click()
        self.inquiries_page.locators.PRODUCTS[1].wait_to_be_visible(timeout=80000)
        self.inquiries_page.locators.PERSONAL_ACCOUNT_OPTION_ICON.wait_to_be_visible()

        self.client_profile_page.locators.CURRENT_CLIENT_LINK.click()
        self.client_profile_page.locators.PRODUCTS_TAB.click()
        self.client_profile_page.locators.OPEN_PRODUCT_BTN.click(0)
        self.client_profile_page.locators.OPEN_OPTIONS_BTN.click(0)
        self.client_profile_page.locators.PERSONAL_ACCOUNT_OPTION_ICON.wait_to_be_visible()
        self.client_profile_page.locators.wait_to_be_enabled(type_offer="option")
