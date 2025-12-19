import random

import allure
import pytest

from api.nbss.personal_account_requests import PersonalAccountRequests
from models.client import OrganizationClient
from pages.locators.nbss.dynamic_form_elements import PersonalAccountForm
from pages.nbss.personal_account_page import PersonalAccountPage


@allure.epic("E2E_53 Управление кредитным порогом клиента (Экстра)")
@allure.suite("E2E_53 Управление кредитным порогом клиента (Экстра)")
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestCreatePersonalAccount:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login, create_organization: OrganizationClient) -> None:
        self.personal_account_api = PersonalAccountRequests()
        self.personal_account_page = PersonalAccountPage()
        self.personal_account_form = PersonalAccountForm()
        self.client = create_organization
        self.client.add_agreement(*self.personal_account_api.create_agreement(self.client))

    @allure.title("Создание ЛС с постоплатным способом оплаты")
    @allure.id(539822)
    def test_create_personal_account_with_postpaid_payment_method(self, base_url: str) -> None:
        deactivation_threshold = str(random.randint(0, 100000))
        self.personal_account_page.open(
            f"{base_url}customer-hierarchy-management/agreements/{self.client.agreements[0].id}/agreement"
        )
        self.personal_account_page.locators.PERSONAL_ACCOUNTS_TAB.click()
        self.personal_account_page.locators.ADD_PERSONAL_ACCOUNT_BTN.click()

        account_number = self.personal_account_form.check_personal_account_form()
        self.personal_account_form.THRESHOLD_CONTROL_CHECKBOX.not_to_be_visible()
        self.personal_account_form.PAYMENT_METHOD.select_by_value("Постоплатный")
        self.personal_account_form.THRESHOLD_CONTROL_FLD.not_to_be_visible()
        self.personal_account_form.THRESHOLD_CONTROL_CHECKBOX.click()
        self.personal_account_form.THRESHOLD_CONTROL_FLD.check_attribute_by_value("value", "0")
        self.personal_account_form.THRESHOLD_CONTROL_FLD.fill(deactivation_threshold)
        self.personal_account_form.SAVE_BTN.click()

        self.personal_account_form.TITLE.not_to_be_visible()
        self.personal_account_page.locators.INFO_MESSAGE.wait_to_have_text("Лицевой счёт создан")
        self.personal_account_page.check_personal_account_data(
            account_number=account_number,
            payment_method="Постоплатный",
            threshold_control="Да",
            threshold_break=deactivation_threshold,
        )

    @allure.title("Отмена создания ЛС с постоплатным способом оплаты")
    @allure.id(540235)
    def test_cancel_create_personal_account_with_postpaid_payment_method(self, base_url: str) -> None:
        self.personal_account_page.open(
            f"{base_url}customer-hierarchy-management/agreements/{self.client.agreements[0].id}/agreement"
        )
        self.personal_account_page.locators.PERSONAL_ACCOUNTS_TAB.click()
        self.personal_account_page.locators.ADD_PERSONAL_ACCOUNT_BTN.click()

        self.personal_account_form.check_personal_account_form()
        self.personal_account_form.PAYMENT_METHOD.select_by_value("Постоплатный")
        self.personal_account_form.THRESHOLD_CONTROL_CHECKBOX.click()
        self.personal_account_form.THRESHOLD_CONTROL_FLD.fill(str(random.randint(0, 100000)))
        self.personal_account_form.CANCEL_BTN.click()

        self.personal_account_form.TITLE.not_to_be_visible()
        self.personal_account_page.locators.NO_PERSONAL_ACCOUNTS_BLOCK.wait_to_be_visible()
