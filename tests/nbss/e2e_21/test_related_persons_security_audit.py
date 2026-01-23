import re

import allure
import pytest

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from api.nbss.client_requests.client_requests import ClientRequests
from common.enums.linked_person import Specialization
from common.enums.user import User
from common.helpers.data_generator import generate_random_number
from common.helpers.env_helper import BASE_URL
from common.helpers.time_helpers import delay
from models.client import IndividualClient, OrganizationClient
from models.inquiry import prepare_inquiries
from pages.locators.nbss.dynamic_form_elements import ClientAuthorizationForm, CreateOrganization
from pages.locators.nbss.home_page_elements import HomePageElements
from pages.nbss.client.client_profile_page import ClientProfilePage


@pytest.mark.regress
@pytest.mark.nbss_portal
@allure.epic("Работа с клиентом ЮЛ")
@allure.suite("E2E_21 Ведение аудита безопасности")
@allure.link(
    url="confluence.nexign.com/pages/viewpage.action?pageId=760620397",
    name="KP [NBSS] Маскирование чувствительных данных (Стандартное)",
)
@allure.link(
    url="confluence.nexign.com/pages/viewpage.action?pageId=792861024",
    name="NBSS.TPM.21 Маскирование чувствительных данных",
)
@allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=765419795", name="Перечень маскируемых данных")
class TestRelatedPersonsSecurityAudit:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login) -> None:
        self.home_page = HomePageElements()
        self.client_profile_page = ClientProfilePage()
        self.authorization_form = ClientAuthorizationForm()
        self.client_requests = ClientRequests()
        self.organization_create_form = CreateOrganization()
        self.client_inquiries_request = ClientInquiriesRequests()

    @pytest.mark.user(User.SELLER_JR_TEST)
    @allure.title("00. Просмотр замаскированных данных КП")
    @allure.id(685149)
    def test_check_end_user_masked_data(
        self,
        individual_user_data: IndividualClient,
        create_organization: OrganizationClient,
    ) -> None:
        client_b2c = individual_user_data
        client_b2b = create_organization
        self.client_profile_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{client_b2b.user_id}/overview")

        self.client_inquiries_request.product_sale(inquiry=prepare_inquiries("internet"))
        self.client_inquiries_request.create_end_user_to_subscriber(client_b2c)

        delay(1, "Не успевают подтянуться данные по конечному пользователю")
        self.client_profile_page.locators.RELATED_PERSONS_TAB.click()
        self.client_profile_page.locators.RELATED_PERSONS.wait_to_have_count(2)
        self.client_profile_page.locators.RELATED_PERSONS[1].click()
        self.client_profile_page.check_related_person(client_b2c, masked=True, end_user=True)

        self.client_profile_page.locators.EDIT_BTN.not_to_be_enabled()
        self.client_profile_page.locators.AUTHORIZE_BTN.to_be_enabled()

    @pytest.mark.user(User.SELLER_JR_TEST)
    @allure.title("00. Просмотр замаскированных данных СЛ")
    @allure.id(684250)
    def test_check_related_person_masked_data(
        self, create_organization_with_agreement_and_account, individual_user_data: IndividualClient
    ) -> None:
        client = create_organization_with_agreement_and_account
        client_b2c_data = individual_user_data
        self.client_requests.create_linked_person(
            client.user_id, linked_person=client_b2c_data, specialization=Specialization.PaymentQuestions, phone=True
        )
        self.client_profile_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{client.user_id}/overview")

        delay(1, "Не успевают подтянуться данные по конечному пользователю")
        self.client_profile_page.locators.RELATED_PERSONS_TAB.click()
        self.client_profile_page.locators.RELATED_PERSONS.wait_to_have_count(1)
        self.client_profile_page.locators.RELATED_PERSONS[0].click()
        self.client_profile_page.check_related_person(client_b2c_data, masked=True)

        self.client_profile_page.locators.EDIT_BTN.not_to_be_enabled()
        self.client_profile_page.locators.AUTHORIZE_BTN.to_be_enabled()

    @pytest.mark.user(User.SELLER_JR_TEST)
    @allure.title("01. Успешная вторичная авторизация по коду авторизации для просмотра данных СЛ")
    @allure.id(684497)
    def test_success_authorization_by_related_person_constant_code_for_organization_data(
        self,
        create_organization_with_agreement_and_account,
        individual_user_data: IndividualClient,
    ):
        client = create_organization_with_agreement_and_account
        client_b2c_data = individual_user_data
        self.client_requests.create_linked_person(
            client.user_id, linked_person=client_b2c_data, specialization=Specialization.PaymentQuestions, phone=True
        )
        self.client_profile_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{client.user_id}/overview")
        self.client_profile_page.locators.CLIENT_TAB.click()
        self.client_profile_page.check_personal_data_form(masked=True)

        self.client_profile_page.locators.AUTHORIZATION.click()
        self.authorization_form.FOUR_DIGITS_CODE.wait_to_be_visible()
        self.authorization_form.ATTEMPTS_NUMBER.wait_to_be_visible()
        self.authorization_form.ATTEMPTS_NUMBER.to_contain_text("0 из 3")

        self.authorization_form.FOUR_DIGITS_CODE.fill(client.auth_code)
        self.authorization_form.AUTHORIZE_BTN.click()

        self.client_profile_page.locators.AUTHORIZATION.not_to_be_visible()

        self.client_profile_page.check_personal_data_form(masked=False)

    @pytest.mark.user(User.SELLER_JR_TEST)
    @allure.title("02. Неуспешная вторичная авторизация по коду авторизации для просмотра данных СЛ")
    @allure.id(684684)
    def test_failed_authorization_by_invalid_relate_person_constant_code(
        self, create_organization_with_agreement_and_account, individual_user_data: IndividualClient
    ):
        client = create_organization_with_agreement_and_account
        client_b2c_data = individual_user_data
        self.client_requests.create_linked_person(
            client.user_id, linked_person=client_b2c_data, specialization=Specialization.PaymentQuestions, phone=True
        )
        self.client_profile_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{client.user_id}/overview")
        self.client_profile_page.locators.CLIENT_TAB.click()
        self.client_profile_page.check_personal_data_form(masked=True)

        self.client_profile_page.locators.AUTHORIZATION.click()
        self.authorization_form.FOUR_DIGITS_CODE.wait_to_be_visible()
        self.authorization_form.ATTEMPTS_NUMBER.wait_to_be_visible()
        self.authorization_form.ATTEMPTS_NUMBER.to_contain_text("0 из 3")

        self.authorization_form.FOUR_DIGITS_CODE.fill(str(generate_random_number(4)))
        self.authorization_form.AUTHORIZE_BTN.click()
        self.authorization_form.ERROR_TEXT.to_contain_text("Передано некорректное значение кода")
        self.authorization_form.ATTEMPTS_NUMBER.to_contain_text("1 из 3", timeout_sec=5)

        self.authorization_form.AUTHORIZE_BTN.click()
        self.authorization_form.ERROR_TEXT.to_contain_text("Передано некорректное значение кода")
        self.authorization_form.ATTEMPTS_NUMBER.to_contain_text("2 из 3", timeout_sec=5)

        self.authorization_form.AUTHORIZE_BTN.click()
        self.authorization_form.ERROR_TEXT.to_contain_text("Передано некорректное значение кода")
        self.authorization_form.ATTEMPTS_NUMBER.to_contain_text("3 из 3", timeout_sec=5)

        self.authorization_form.ATTENTION_TEXT.wait_to_have_text(
            re.compile(
                r"Количество попыток авторизации по коду исчерпаны. Повторная авторизация будет доступна через \d+:\d+ минут."
            )
        )
