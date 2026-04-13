import allure
import pytest

from api.nbss.client_requests.client_requests import ClientRequests
from models.client import OrganizationClient
from pages.locators.nbss.dynamic_form_elements import CreateOrganization
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.home_page import HomePage


@allure.epic("E2E_64 Создание и управление клиентом и его иерархиями")
@allure.suite('E2E_64_13 Создание и управление клиентом и его иерархиями (Поддержать статус Клиента "Потенциальный")')
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestMaintainClientStatus:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login, organization_user_data: OrganizationClient) -> None:
        self.home_page = HomePage()
        self.form_create_organization = CreateOrganization()
        self.client_profile_page = ClientProfilePage()
        self.client_requests = ClientRequests()
        self.user = organization_user_data
        self.type_client = "Потенциальный"

    @allure.id(818603)
    @allure.title("08. Создание клиента/партнера ЮЛ, включена функциональность проверки дублей (ввод данных вручную)")
    def test_create_legal_entity_client_or_partner_with_duplicate_check_manual_input(self):
        self.home_page.locators.CREATE_ORG_BTN.wait_to_be_visible(timeout=15000)
        self.home_page.locators.CREATE_ORG_BTN.click()
        self.form_create_organization.fill_data_for_organization_client(
            user_data=self.user, new_ui=True, only_required_fields=True
        )
        self.client_profile_page.locators.CLIENT_STATUS.wait_to_have_text(self.type_client, timeout=35000)
        self.client_profile_page.locators.RELATED_PERSONS_TAB.click()
        self.client_profile_page.locators.RELATED_PERSONS.wait_to_have_count(1, timeout=15000)

    @allure.id(818605)
    @allure.title(
        "09. Создание клиента/партнера ЮЛ, включена функциональность проверки дублей (ввод данных вручную, в том числе ИНН и КПП, есть дубликат)"
    )
    def test_create_organization_client_or_partner_duplicate_check_manual_inn_kpp_duplicate_found(self) -> None:
        self.client = self.client_requests.create_organization(client_data=OrganizationClient())

        self.home_page.locators.CREATE_ORG_BTN.wait_to_be_visible(timeout=15000)
        self.home_page.locators.CREATE_ORG_BTN.click()
        self.form_create_organization.fill_data_for_organization_client(
            user_data=self.client, new_ui=True, need_second_page=False
        )
        self.home_page.locators.MODAL.wait_to_be_visible(timeout=15000)
        self.home_page.refresh_page(wait="load")
        self.form_create_organization.INN.wait_to_be_visible(timeout=15000)
        self.form_create_organization.fill_data_for_organization_client(user_data=self.user, new_ui=True)
        self.client_profile_page.locators.CLIENT_STATUS.wait_to_have_text(self.type_client, timeout=35000)
        self.client_profile_page.locators.RELATED_PERSONS_TAB.click()
        self.client_profile_page.locators.RELATED_PERSONS.wait_to_have_count(1, timeout=15000)

    @allure.id(818608)
    @allure.title(
        "10. Создание клиента/партнера ЮЛ, включена функциональность проверки дублей (ввод данных вручную, в том числе ИНН и КПП, нет дубликатов)"
    )
    def test_create_organization_client_or_partner_duplicate_check_manual_inn_kpp_no_duplicates_found(self) -> None:
        self.home_page.locators.CREATE_ORG_BTN.wait_to_be_visible(timeout=15000)
        self.home_page.locators.CREATE_ORG_BTN.click()
        self.form_create_organization.fill_data_for_organization_client(user_data=self.user, new_ui=True)
        self.client_profile_page.locators.CLIENT_STATUS.wait_to_have_text(self.type_client, timeout=35000)
        self.client_profile_page.locators.RELATED_PERSONS_TAB.click()
        self.client_profile_page.locators.RELATED_PERSONS.wait_to_have_count(1, timeout=15000)
