import re

import allure
import pytest

from api.nbss.client_requests.client_requests import ClientRequests
from common.enums.user import User
from common.helpers.data_generator import generate_random_number
from common.helpers.env_helper import BASE_URL
from models.context import test_context
from pages.locators.nbss.dynamic_form_elements import ClientAuthorizationForm
from pages.locators.nbss.home_page_elements import HomePageElements
from pages.nbss.client.client_profile_page import ClientProfilePage


@pytest.mark.regress
@pytest.mark.nbss_portal
@allure.epic("Работа с клиентом ФЛ/ИП")
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
class TestPersonSecurityAudit:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login) -> None:
        self.home_page = HomePageElements()
        self.client_profile_page = ClientProfilePage()
        self.authorization_form = ClientAuthorizationForm()
        self.client_requests = ClientRequests()

    @pytest.mark.user(User.SELLER_JR_TEST)
    @allure.title("00. Просмотр замаскированных данных клиента ФЛ/ИП")
    @allure.id(682168)
    def test_view_masked_client_data(self, create_user_with_agreement_and_account):
        self.client_profile_page.open(
            f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/overview"
        )
        self.client_profile_page.locators.CLIENT_TAB.click()
        self.client_profile_page.check_personal_data_form(masked=True)

        self.client_profile_page.locators.EDIT_BTN.not_to_be_enabled()
        self.client_profile_page.locators.EDIT_BTN.hover()
        self.client_profile_page.locators.TOOLTIP.wait_to_have_text(
            "Операция недоступна, для доступа требуется авторизация"
        )

        self.client_profile_page.locators.ADDRESSES_TAB.click()
        self.client_profile_page.locators.TABLE_ADDRESS_LINE[0].to_contain_text("***", timeout_sec=10)
        self.client_profile_page.locators.TABLE_ADDRESS_LINE[0].click()
        self.client_profile_page.locators.EDIT_ADDRESS.not_to_be_enabled()

    @pytest.mark.user(User.SELLER_JR_TEST)
    @allure.title("01. Успешная вторичная авторизация по постоянному коду (ДУЛ) для просмотра данных клиента ФЛ/ИП")
    @allure.id(682738)
    def test_success_authorization_by_constant_code_for_view_data(self, create_user_with_agreement_and_account):
        client = create_user_with_agreement_and_account
        self.client_profile_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{client.user_id}/overview")
        self.client_profile_page.locators.CLIENT_TAB.click()
        self.client_profile_page.check_personal_data_form(masked=True)

        self.client_profile_page.locators.AUTHORIZATION.click()
        self.authorization_form.FOUR_DIGITS_CODE.wait_to_be_visible()
        self.authorization_form.ATTEMPTS_NUMBER.wait_to_be_visible()
        self.authorization_form.ATTEMPTS_NUMBER.to_contain_text("0 из 3")

        self.authorization_form.FOUR_DIGITS_CODE.fill(client.document_num[2:])
        self.authorization_form.AUTHORIZE_BTN.click()

        self.client_profile_page.locators.AUTHORIZATION.not_to_be_visible()

        self.client_profile_page.check_personal_data_form(masked=False)

    @pytest.mark.user(User.SELLER_JR_TEST)
    @allure.title("02. Неуспешная вторичная авторизация по постоянному коду (ДУЛ) для просмотра данных клиента ФЛ/ИП")
    @allure.id(683533)
    def test_not_success_authorization_by_invalid_constant_code(self, create_user_with_agreement_and_account):
        client = create_user_with_agreement_and_account
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
                r"Количество попыток авторизации по документу исчерпаны. Повторная авторизация будет доступна через \d+:\d+ минут."
            )
        )
