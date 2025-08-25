import allure
import pytest
from playwright.sync_api import Page

from models.user import EntrepreneurClient, IndividualClient, OrganizationClient
from pages.client_profile_page import ClientProfilePage
from pages.locators.dynamic_form_elements import (
    AddRelatedPersonForms,
    CreateEntrepreneur,
    CreateOrganization,
    IndividualCustomerCreate,
    PersonalAccountForm,
)
from pages.personal_account_page import PersonalAccountPage


@allure.epic("Управление лицевым счетом")
@allure.suite("Управление лицевым счетом")
@pytest.mark.usefixtures("nexign_ui_stand_login")
class TestPersonalAccount:
    @pytest.fixture(autouse=True)
    def setup(self, page: Page) -> None:
        self.personal_account_page = PersonalAccountPage(page)
        self.client_profile_page = ClientProfilePage(page)
        self.customer_create_form = IndividualCustomerCreate(page)
        self.organization_create_form = CreateOrganization(page)
        self.entrepreneur_create_form = CreateEntrepreneur(page)
        self.add_related_person_form = AddRelatedPersonForms(page)
        self.personal_account_form = PersonalAccountForm(page)

    @allure.title("Создание и редактирование Предоплатного ЛС для ФЛ")
    @allure.id(486082)
    @pytest.mark.regress
    def test_create_personal_account_prepaid_individual(self, individual_user_data: IndividualClient) -> None:
        self.personal_account_page.user_data = individual_user_data
        self.personal_account_page.create_customer_with_type("individual")
        self.personal_account_page.dynamic_form.SAVE_BTN.click()
        self.personal_account_page.locators.INFO_MESSAGE_CLOSE_BTN.click(timeout=10000)

        self.client_profile_page.locators.AGREEMENTS_TAB.click()
        self.client_profile_page.locators.ADD_AGREEMENT_BTN.wait_to_have_text("Добавить")
        self.client_profile_page.locators.ADD_AGREEMENT_BTN.click()
        self.personal_account_page.dynamic_elements.CONTRACT_NUM.wait_to_be_visible()

        self.personal_account_page.fill_data_create_agreement(type_client="individual")
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
    def test_create_personal_account_postpaid_individual(self, individual_user_data: IndividualClient) -> None:
        self.personal_account_page.user_data = individual_user_data
        self.personal_account_page.create_customer_with_type("individual")
        self.personal_account_page.dynamic_form.SAVE_BTN.click()
        self.personal_account_page.locators.INFO_MESSAGE_CLOSE_BTN.click()

        self.client_profile_page.locators.AGREEMENTS_TAB.click()
        self.client_profile_page.locators.ADD_AGREEMENT_BTN.wait_to_have_text("Добавить")
        self.personal_account_page.locators.ADD_AGREEMENT_BTN.click()
        self.personal_account_page.dynamic_elements.CONTRACT_NUM.wait_to_be_visible()

        self.personal_account_page.fill_data_create_agreement(type_client="individual")
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
    def test_create_personal_account_prepaid_entrepreneur(self, entrepreneur_user_data: EntrepreneurClient) -> None:
        self.personal_account_page.user_data = entrepreneur_user_data
        self.personal_account_page.create_customer_with_type("entrepreneur")
        self.personal_account_page.dynamic_form.SAVE_BTN.click()
        self.personal_account_page.locators.INFO_MESSAGE_CLOSE_BTN.click(timeout=10000)
        self.client_profile_page.locators.AGREEMENTS_TAB.click()
        self.client_profile_page.locators.ADD_AGREEMENT_BTN.wait_to_have_text("Добавить")
        self.personal_account_page.locators.ADD_AGREEMENT_BTN.click()
        self.personal_account_page.dynamic_elements.CONTRACT_NUM.wait_to_be_visible()

        self.personal_account_page.fill_data_create_agreement(type_client="entrepreneur")
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
    def test_create_personal_account_postpaid_entrepreneur(self, entrepreneur_user_data: EntrepreneurClient) -> None:
        self.personal_account_page.user_data = entrepreneur_user_data
        self.personal_account_page.create_customer_with_type("entrepreneur")
        self.personal_account_page.dynamic_form.SAVE_BTN.click()
        self.personal_account_page.locators.INFO_MESSAGE_CLOSE_BTN.click(timeout=10000)

        self.client_profile_page.locators.AGREEMENTS_TAB.click()
        self.client_profile_page.locators.ADD_AGREEMENT_BTN.wait_to_have_text("Добавить")
        self.personal_account_page.locators.ADD_AGREEMENT_BTN.click()
        self.personal_account_page.dynamic_elements.CONTRACT_NUM.wait_to_be_visible()

        self.personal_account_page.fill_data_create_agreement(type_client="entrepreneur")
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

    @allure.title("Создание и редактирование Предоплатного ЛС для ЮЛ")
    @allure.id(486086)
    @pytest.mark.regress
    def test_create_personal_account_prepaid_organization(self, organization_user_data: OrganizationClient) -> None:
        self.personal_account_page.user_data = organization_user_data
        self.personal_account_page.create_customer_with_type("organization")
        self.organization_create_form.SAVE_BTN.click()
        self.personal_account_page.locators.INFO_MESSAGE_CLOSE_BTN.click()

        self.client_profile_page.locators.AGREEMENTS_TAB.click()
        self.client_profile_page.locators.ADD_AGREEMENT_BTN.wait_to_have_text("Добавить")
        self.personal_account_page.locators.ADD_AGREEMENT_BTN.click()
        self.personal_account_page.dynamic_elements.CONTRACT_NUM.wait_to_be_visible()

        self.personal_account_page.fill_data_create_agreement(type_client="organization")
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

    @allure.title("Создание и редактирование Постоплатного ЛС для ЮЛ")
    @allure.id(486087)
    @pytest.mark.regress
    @pytest.mark.smoke
    def test_create_personal_account_postpaid_organization(self, organization_user_data: OrganizationClient) -> None:
        self.personal_account_page.user_data = organization_user_data
        self.personal_account_page.create_customer_with_type("organization")
        self.organization_create_form.SAVE_BTN.click()
        self.personal_account_page.locators.INFO_MESSAGE_CLOSE_BTN.click()

        self.client_profile_page.locators.AGREEMENTS_TAB.click()
        self.client_profile_page.locators.ADD_AGREEMENT_BTN.wait_to_have_text("Добавить")
        self.personal_account_page.locators.ADD_AGREEMENT_BTN.click()
        self.personal_account_page.dynamic_elements.CONTRACT_NUM.wait_to_be_visible()

        self.personal_account_page.fill_data_create_agreement(type_client="organization")
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

    @allure.title("Создание ЛС со связанными лицами")
    @allure.id(519835)
    @allure.tag("can_auth", "success")
    @pytest.mark.regress
    def test_create_personal_account_with_related_persons(self, organization_user_data: OrganizationClient) -> None:
        self.personal_account_page.user_data = organization_user_data
        self.personal_account_page.user_data.name_related_person = "Тестовое наименование"
        self.personal_account_page.create_customer_with_type("organization")
        self.personal_account_page.organization_create_form.SAVE_BTN.click()
        self.personal_account_page.locators.INFO_MESSAGE_CLOSE_BTN.click()

        self.client_profile_page.locators.AGREEMENTS_TAB.click()
        self.client_profile_page.locators.ADD_AGREEMENT_BTN.wait_to_have_text("Добавить")
        self.personal_account_page.locators.ADD_AGREEMENT_BTN.click()
        self.personal_account_page.dynamic_elements.CONTRACT_NUM.wait_to_be_visible()

        self.personal_account_page.fill_data_create_agreement(type_client="organization")
        self.personal_account_page.dynamic_form.SAVE_BTN.click()
        self.personal_account_page.locators.INFO_MESSAGE.wait_to_be_visible()
        self.personal_account_page.locators.INFO_MESSAGE_CLOSE_BTN.click()

        self.personal_account_page.locators.RELATED_PERSONS_TAB.click()
        self.personal_account_page.locators.ADD_RELATED_PERSON_BTN.click()
        self.add_related_person_form.fill_data_for_related_person()

        self.personal_account_page.locators.PERSONAL_ACCOUNTS_TAB.click()
        self.personal_account_page.locators.ADD_PERSONAL_ACCOUNT_BTN.click()
        self.personal_account_page.dynamic_form.SAVE_BTN.click()
        self.personal_account_page.locators.INFO_MESSAGE.wait_to_be_visible()
        self.personal_account_page.locators.INFO_MESSAGE_CLOSE_BTN.click()

        self.personal_account_page.locators.RELATED_PERSONS_TAB.click()
        self.personal_account_page.locators.ADD_RELATED_PERSON_BTN.click()
        self.add_related_person_form.fill_data_for_related_person()
        self.personal_account_page.check_related_person_by_context(type_context="personal_account")
        self.personal_account_page.check_related_person_by_context(type_context="agreement")
