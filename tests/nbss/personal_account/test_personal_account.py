import allure
import pytest

from models.client import IndividualClient
from models.context import test_context
from pages.locators.nbss.dynamic_form_elements import (
    CreateEntrepreneur,
    CreateOrganization,
    IndividualCustomerCreate,
    PersonalAccountForm,
    RelatedPersonForms,
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
        self.add_related_person_form = RelatedPersonForms()
        self.personal_account_form = PersonalAccountForm()

    @allure.title("Создание и редактирование Предоплатного ЛС для ФЛ")
    @allure.id(486082)
    @pytest.mark.regress
    def test_create_personal_account_prepaid_individual(
        self, base_url: str, create_user_with_agreement_and_account: IndividualClient
    ) -> None:
        self.personal_account_page.open(
            f"{base_url}customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
        )
        self.personal_account_page.edit_account_payment_method()

    @allure.title("Создание и редактирование Постоплатного ЛС для ФЛ")
    @allure.id(581810)
    @pytest.mark.regress
    def test_create_personal_account_postpaid_individual(
        self, base_url: str, create_user_with_agreement_and_account: IndividualClient
    ) -> None:
        self.personal_account_page.open(
            f"{base_url}customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
        )
        self.personal_account_page.edit_account_payment_method(payment_method="Постоплатный")

    @allure.title("Создание и редактирование Постоплатного ЛС для ИП")
    @allure.id(486085)
    @pytest.mark.regress
    def test_create_personal_account_postpaid_entrepreneur(
        self, base_url: str, create_entrepreneur_with_agreement_and_account: IndividualClient
    ) -> None:
        self.personal_account_page.open(
            f"{base_url}customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
        )
        self.personal_account_page.edit_account_payment_method(payment_method="Постоплатный")

    @allure.title("Создание и редактирование Предоплатного ЛС для ИП")
    @allure.id(486084)
    @pytest.mark.regress
    def test_create_personal_account_prepaid_entrepreneur(
        self, base_url: str, create_entrepreneur_with_agreement_and_account: IndividualClient
    ) -> None:
        self.personal_account_page.open(
            f"{base_url}customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
        )
        self.personal_account_page.edit_account_payment_method()
