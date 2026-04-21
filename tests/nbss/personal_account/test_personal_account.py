import allure
import pytest

from pages.locators.nbss.dynamic_form_elements import (
    AddRelatedPersonForms,
    CreateEntrepreneur,
    CreateOrganization,
    IndividualCustomerCreate,
    PersonalAccountForm,
)
from pages.nbss.agreement_page import AgreementPage
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.home_page import HomePage
from pages.nbss.personal_account_page import PersonalAccountPage


@allure.epic("Управление лицевым счетом")
@allure.suite("Управление лицевым счетом")
@pytest.mark.nbss_portal
class TestPersonalAccount:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login) -> None:
        self.personal_account_page = PersonalAccountPage()
        self.home_page = HomePage()
        self.agreement_page = AgreementPage()
        self.client_profile_page = ClientProfilePage()
        self.customer_create_form = IndividualCustomerCreate()
        self.organization_create_form = CreateOrganization()
        self.entrepreneur_create_form = CreateEntrepreneur()
        self.add_related_person_form = AddRelatedPersonForms()
        self.personal_account_form = PersonalAccountForm()

    @allure.title("Создание и редактирование Предоплатного ЛС для ФЛ")
    @allure.id(486082)
    @pytest.mark.regress
    def test_create_personal_account_prepaid_individual(self) -> None:
        self.home_page.create_customer_with_type("individual")
        self.personal_account_page.locators.INFO_MESSAGE_CLOSE_BTN.click(timeout=10000)

        self.client_profile_page.locators.AGREEMENTS_TAB.click()
        self.client_profile_page.locators.ADD_AGREEMENT_BTN.wait_to_have_text("Добавить")
        self.client_profile_page.locators.ADD_AGREEMENT_BTN.click()
        self.personal_account_page.dynamic_elements.CONTRACT_NUM.wait_to_be_visible()

        self.agreement_page.fill_data_create_agreement()
        self.personal_account_page.dynamic_form.SAVE_BTN.click()
        self.personal_account_page.locators.INFO_MESSAGE.wait_to_be_visible()
        self.personal_account_page.locators.INFO_MESSAGE_CLOSE_BTN.click()

        self.personal_account_page.locators.PERSONAL_ACCOUNTS_TAB.click()
        self.personal_account_page.locators.ADD_PERSONAL_ACCOUNT_BTN.click()
        self.personal_account_page.dynamic_form.SAVE_BTN.click()
        self.personal_account_page.locators.INFO_MESSAGE.wait_to_be_visible()
        self.personal_account_page.locators.INFO_MESSAGE_CLOSE_BTN.click()

        self.personal_account_page.locators.EDIT_DETAILS_ACCOUNT_BTN.click()
        self.personal_account_form.TITLE.wait_to_be_visible()
        self.personal_account_form.PAYMENT_METHOD.select_by_value("Предоплатный")
        self.personal_account_form.SAVE_BTN.click()
        self.personal_account_page.locators.INFO_MESSAGE.wait_to_be_visible()

        self.personal_account_page.locators.INFO_MESSAGE_CLOSE_BTN.click()

    @allure.title("Создание и редактирование Постоплатного ЛС для ФЛ")
    @allure.id(581810)
    @pytest.mark.regress
    def test_create_personal_account_postpaid_individual(self) -> None:
        self.home_page.create_customer_with_type("individual")
        self.personal_account_page.locators.INFO_MESSAGE_CLOSE_BTN.click()

        self.client_profile_page.locators.AGREEMENTS_TAB.click()
        self.client_profile_page.locators.ADD_AGREEMENT_BTN.wait_to_have_text("Добавить")
        self.personal_account_page.locators.ADD_AGREEMENT_BTN.click()
        self.personal_account_page.dynamic_elements.CONTRACT_NUM.wait_to_be_visible()

        self.agreement_page.fill_data_create_agreement()
        self.personal_account_page.dynamic_form.SAVE_BTN.click()
        self.personal_account_page.locators.INFO_MESSAGE.wait_to_be_visible()
        self.personal_account_page.locators.INFO_MESSAGE_CLOSE_BTN.click()

        self.personal_account_page.locators.PERSONAL_ACCOUNTS_TAB.click()
        self.personal_account_page.locators.ADD_PERSONAL_ACCOUNT_BTN.click()
        self.personal_account_page.dynamic_form.SAVE_BTN.click()
        self.personal_account_page.locators.INFO_MESSAGE.wait_to_be_visible()
        self.personal_account_page.locators.INFO_MESSAGE_CLOSE_BTN.click()

        self.personal_account_page.locators.EDIT_DETAILS_ACCOUNT_BTN.click()
        self.personal_account_form.TITLE.wait_to_be_visible()
        self.personal_account_form.PAYMENT_METHOD.select_by_value("Постоплатный")
        self.personal_account_form.SAVE_BTN.click()
        self.personal_account_page.locators.INFO_MESSAGE.wait_to_be_visible()

        self.personal_account_page.locators.INFO_MESSAGE_CLOSE_BTN.click()

    @allure.title("Создание и редактирование Предоплатного ЛС для ИП")
    @allure.id(486084)
    @pytest.mark.regress
    def test_create_personal_account_prepaid_entrepreneur(self) -> None:
        self.home_page.create_customer_with_type("entrepreneur")
        self.personal_account_page.locators.INFO_MESSAGE_CLOSE_BTN.click(timeout=10000)
        self.client_profile_page.locators.AGREEMENTS_TAB.click()
        self.client_profile_page.locators.ADD_AGREEMENT_BTN.wait_to_have_text("Добавить")
        self.personal_account_page.locators.ADD_AGREEMENT_BTN.click()
        self.personal_account_page.dynamic_elements.CONTRACT_NUM.wait_to_be_visible()

        self.agreement_page.fill_data_create_agreement()
        self.personal_account_page.dynamic_form.SAVE_BTN.click()
        self.personal_account_page.locators.INFO_MESSAGE.wait_to_be_visible()
        self.personal_account_page.locators.INFO_MESSAGE_CLOSE_BTN.click()

        self.personal_account_page.locators.PERSONAL_ACCOUNTS_TAB.click()
        self.personal_account_page.locators.ADD_PERSONAL_ACCOUNT_BTN.click()
        self.personal_account_page.dynamic_form.SAVE_BTN.click()
        self.personal_account_page.locators.INFO_MESSAGE.wait_to_be_visible()
        self.personal_account_page.locators.INFO_MESSAGE_CLOSE_BTN.click()

        self.personal_account_page.locators.EDIT_DETAILS_ACCOUNT_BTN.click()
        self.personal_account_form.TITLE.wait_to_be_visible()
        self.personal_account_form.PAYMENT_METHOD.select_by_value("Предоплатный")
        self.personal_account_form.SAVE_BTN.click()
        self.personal_account_page.locators.INFO_MESSAGE.wait_to_be_visible()

        self.personal_account_page.locators.INFO_MESSAGE_CLOSE_BTN.click()

    @allure.title("Создание и редактирование Постоплатного ЛС для ИП")
    @allure.id(486085)
    @pytest.mark.regress
    def test_create_personal_account_postpaid_entrepreneur(self) -> None:
        self.home_page.create_customer_with_type("entrepreneur")
        self.personal_account_page.dynamic_form.SAVE_BTN.click(timeout=10000)
        self.personal_account_page.locators.INFO_MESSAGE_CLOSE_BTN.click(timeout=10000)

        self.client_profile_page.locators.AGREEMENTS_TAB.click()
        self.client_profile_page.locators.ADD_AGREEMENT_BTN.wait_to_have_text("Добавить")
        self.personal_account_page.locators.ADD_AGREEMENT_BTN.click()
        self.personal_account_page.dynamic_elements.CONTRACT_NUM.wait_to_be_visible()

        self.agreement_page.fill_data_create_agreement()
        self.personal_account_page.dynamic_form.SAVE_BTN.click()
        self.personal_account_page.locators.INFO_MESSAGE.wait_to_be_visible(timeout=10000)
        self.personal_account_page.locators.INFO_MESSAGE_CLOSE_BTN.click()

        self.personal_account_page.locators.PERSONAL_ACCOUNTS_TAB.click()
        self.personal_account_page.locators.ADD_PERSONAL_ACCOUNT_BTN.click()
        self.personal_account_page.dynamic_form.SAVE_BTN.click()
        self.personal_account_page.locators.INFO_MESSAGE.wait_to_be_visible()
        self.personal_account_page.locators.INFO_MESSAGE_CLOSE_BTN.click()

        self.personal_account_page.locators.EDIT_DETAILS_ACCOUNT_BTN.click()
        self.personal_account_form.TITLE.wait_to_be_visible()
        self.personal_account_form.PAYMENT_METHOD.select_by_value("Постоплатный")
        self.personal_account_form.SAVE_BTN.click()
        self.personal_account_page.locators.INFO_MESSAGE.wait_to_be_visible()

        self.personal_account_page.locators.INFO_MESSAGE_CLOSE_BTN.click()
