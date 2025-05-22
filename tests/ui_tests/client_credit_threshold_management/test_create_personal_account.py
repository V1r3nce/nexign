import random

import allure
import pytest
from playwright.sync_api import Page

from pages.locators.dynamic_form_elements import PersonalAccountForm
from pages.personal_account_page import PersonalAccountPage


@allure.epic("E2E_53 Управление кредитным порогом клиента")
@allure.suite("E2E_53 Управление кредитным порогом клиента")
@pytest.mark.usefixtures("nexign_ui_stand_login")
class TestCreatePersonalAccount:
    @pytest.fixture(autouse=True)
    def setup(self, page: Page) -> None:
        self.personal_account_page = PersonalAccountPage(page)
        self.personal_account_form = PersonalAccountForm(page)

    @allure.title("Создание ЛС с постоплатным способом оплаты")
    @allure.id(539822)
    @pytest.mark.regress
    def test_create_personal_account_with_postpaid_payment_method(self) -> None:
        self.personal_account_page.create_customer_with_type("organization")
        self.personal_account_page.dynamic_form.SAVE_BTN.click()
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

        self.personal_account_form.TITLE.wait_to_be_visible()
        self.personal_account_form.PAYMENT_METHOD.select_by_value("Постоплатный")
        self.personal_account_form.THRESHOLD_CONTROL_CHECKBOX.click()
        self.personal_account_form.THRESHOLD_CONTROL_CREATE_FLD.fill(str(random.randint(0, 100000)))
        self.personal_account_form.CREATE_BTN.click()

        self.personal_account_page.locators.INFO_MESSAGE.wait_to_be_visible()

    @allure.title("Отмена создания ЛС с постоплатным способом оплаты")
    @allure.id(540235)
    @pytest.mark.regress
    def test_cancel_create_personal_account_with_postpaid_payment_method(self) -> None:
        self.personal_account_page.create_customer_with_type("organization")
        self.personal_account_page.dynamic_form.SAVE_BTN.click()
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

        self.personal_account_form.TITLE.wait_to_be_visible()
        self.personal_account_form.PAYMENT_METHOD.select_by_value("Постоплатный")
        self.personal_account_form.THRESHOLD_CONTROL_CHECKBOX.click()
        self.personal_account_form.THRESHOLD_CONTROL_CREATE_FLD.fill(str(random.randint(0, 100000)))
        self.personal_account_form.CANCEL_BTN.click()
