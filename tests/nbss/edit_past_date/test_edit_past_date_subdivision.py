import allure
import pytest

from api.nbss.client_requests.client_requests import ClientDataFromResponseGetClientData, ClientRequests
from common.helpers.time_helpers import delay, get_shifted_datetime
from models.client import OrganizationClient
from pages.base_page import BasePage
from pages.locators.nbss.dynamic_form_elements import CreateEntrepreneur
from pages.nbss.client.client_profile_page import ClientProfilePage


@allure.epic("E2E_64_1 Редактирование задним числом в PRAIM")
@allure.suite("E2E_64_1 Редактирование задним числом в PRAIM")
@pytest.mark.regress
@pytest.mark.nbss_portal
@pytest.mark.praim
class TestEditPastDateSubdivision:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login) -> None:
        self.base_page = BasePage()
        self.client_profile_page = ClientProfilePage()
        self.entrepreneur_create_form = CreateEntrepreneur()
        self.client_request_api = ClientRequests()
        self.old_subdivision_name = "Флюгеггехайнен"

    @allure.title("Редактирование подразделения клиента прошлой датой")
    @allure.id(608621)
    @allure.description("Редактирование подразделения клиента прошлой датой")
    def test_edit_client_subdivision_past_date(self, base_url: str, create_organization: OrganizationClient) -> None:
        old_date_1 = get_shifted_datetime("-101d").strftime("%Y-%m-%dT%H:%M:%S")
        old_date_2 = get_shifted_datetime("-100d").strftime("%Y-%m-%dT%H:%M:%S")
        user_data = create_organization
        old_client_data = ClientDataFromResponseGetClientData(
            self.client_request_api.get_client_data(user_data.user_id).json()
        )
        self.client_request_api.put_client_data(
            user_data.user_id,
            old_date_1,
            "organization",
            200,
            reputation_message="Является надежным деловым партнером.",
            customer_name=old_client_data.full_name,
            inn=old_client_data.tax_number,
            kpp=old_client_data.tax_number[:-1],
        )
        delay(0.5, reason="Время для сохранения данных в БД")
        subdivision_id = self.client_request_api.make_subdivision(user_data.user_id, self.old_subdivision_name)
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{user_data.user_id}/overview")
        self.client_profile_page.locators.SUBDIVISIONS_TAB.click(timeout=10000)
        self.client_profile_page.locators.SUBDIVISIONS_NAMES[0].click()

        self.client_profile_page.locators.SUBDIVISION_ADDRESS.wait_to_be_visible()
        self.client_profile_page.locators.SUBDIVISIONS_INN.to_have_value(old_client_data.tax_number)
        self.client_request_api.put_client_subdivision_data(
            subdivision_id, old_date_2, 200, True, new_name=user_data.customer_name, kpp=user_data.kpp
        )
        self.client_request_api.check_response_content("party.nameInfo.name", "==", user_data.customer_name)
        self.client_request_api.check_response_content(
            "party.taxRegistrationCertificate.taxIdentificationNumber", "==", old_client_data.tax_number
        )
        self.client_request_api.check_response_content(
            "party.taxRegistrationCertificate.registrationReasonCode", "==", user_data.kpp
        )

        delay(0.5, reason="Время для сохранения данных в БД")

        self.base_page.refresh_page(wait="domcontentloaded")
        self.client_profile_page.locators.SUBDIVISION_TITLE_NAME.wait_to_have_text(
            f"Подразделение: {user_data.customer_name}"
        )
        self.client_profile_page.locators.SUBDIVISIONS_INN.to_have_value(old_client_data.tax_number)
        self.client_profile_page.locators.SUBDIVISIONS_KPP.to_have_value(user_data.kpp)

    @allure.title("Ошибка редактирования подразделения датой раньше даты создания клиента")
    @allure.id(609476)
    @allure.description("Ошибка редактирования подразделения датой раньше даты создания клиента")
    def test_edit_client_subdivision_past_date_earlier_than_client(
        self, base_url: str, create_organization: OrganizationClient
    ) -> None:
        old_date = get_shifted_datetime("-100d").strftime("%Y-%m-%dT%H:%M:%S")
        user_data = create_organization
        old_client_data = ClientDataFromResponseGetClientData(
            self.client_request_api.get_client_data(user_data.user_id).json()
        )
        subdivision_id = self.client_request_api.make_subdivision(user_data.user_id, self.old_subdivision_name)
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{user_data.user_id}/overview")
        self.client_profile_page.locators.SUBDIVISIONS_TAB.click(timeout=10000)
        self.client_profile_page.locators.SUBDIVISIONS_NAMES[0].click()

        self.client_profile_page.locators.SUBDIVISION_ADDRESS.wait_to_be_visible()
        self.client_profile_page.locators.SUBDIVISIONS_INN.to_have_value(old_client_data.tax_number)
        self.client_request_api.put_client_subdivision_data(
            subdivision_id, old_date, 400, True, new_name=user_data.customer_name, kpp=user_data.kpp
        )
        self.client_request_api.check_response_content(
            "userMessage",
            "==",
            "Дата применения изменений не может быть указана раньше даты создания клиента"
            ". Укажите дату применения изменений на подразделении позже даты создания"
            " клиента или измените дату создания клиента",
        )

    @allure.title("Ошибка редактирования подразделения будущей датой")
    @allure.id(609658)
    @allure.description("Ошибка редактирования подразделения будущей датой")
    def test_edit_client_subdivision_future_date(self, base_url: str, create_organization: OrganizationClient) -> None:
        old_date = get_shifted_datetime("+7d").strftime("%Y-%m-%dT%H:%M:%S")
        user_data = create_organization
        old_client_data = ClientDataFromResponseGetClientData(
            self.client_request_api.get_client_data(user_data.user_id).json()
        )
        subdivision_id = self.client_request_api.make_subdivision(user_data.user_id, self.old_subdivision_name)
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{user_data.user_id}/overview")
        self.client_profile_page.locators.SUBDIVISIONS_TAB.click(timeout=10000)
        self.client_profile_page.locators.SUBDIVISIONS_NAMES[0].click()

        self.client_profile_page.locators.SUBDIVISION_ADDRESS.wait_to_be_visible()
        self.client_profile_page.locators.SUBDIVISIONS_INN.to_have_value(old_client_data.tax_number)
        self.client_request_api.put_client_subdivision_data(
            subdivision_id, old_date, 400, True, new_name=user_data.customer_name, kpp=user_data.kpp
        )
        self.client_request_api.check_response_content("userMessage", "==", "Невозможно установить дату в будущем")

    @allure.title("Применение изменений прошлой датой без изменения данных подразделения")
    @allure.id(609659)
    @allure.description("Применение изменений прошлой датой без изменения данных подразделения")
    def test_edit_client_subdivision_past_date_without_update(
        self, base_url: str, create_organization: OrganizationClient
    ) -> None:
        old_date_1 = get_shifted_datetime("-101d").strftime("%Y-%m-%dT%H:%M:%S")
        old_date_2 = get_shifted_datetime("-100d").strftime("%Y-%m-%dT%H:%M:%S")
        user_data = create_organization
        old_client_data = ClientDataFromResponseGetClientData(
            self.client_request_api.get_client_data(user_data.user_id).json()
        )
        self.client_request_api.put_client_data(
            user_data.user_id,
            old_date_1,
            "organization",
            200,
            reputation_message="Является надежным деловым партнером.",
            customer_name=old_client_data.full_name,
            inn=old_client_data.tax_number,
            kpp=old_client_data.tax_number[:-1],
        )
        delay(0.5, reason="Время для сохранения данных в БД")
        subdivision_id = self.client_request_api.make_subdivision(user_data.user_id, self.old_subdivision_name)
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{user_data.user_id}/overview")
        self.client_profile_page.locators.SUBDIVISIONS_TAB.click(timeout=10000)
        self.client_profile_page.locators.SUBDIVISIONS_NAMES[0].click()

        self.client_profile_page.locators.SUBDIVISION_ADDRESS.wait_to_be_visible()
        self.client_profile_page.locators.SUBDIVISIONS_INN.to_have_value(old_client_data.tax_number)
        self.client_request_api.put_client_subdivision_data(subdivision_id, old_date_2, 200, False)
        self.client_request_api.check_response_content("party.nameInfo.name", "==", self.old_subdivision_name)
        self.client_request_api.check_response_content(
            "party.taxRegistrationCertificate.taxIdentificationNumber", "==", old_client_data.tax_number
        )
        self.client_request_api.check_response_content(
            "party.taxRegistrationCertificate.registrationReasonCode", "==", "None"
        )

        delay(0.5, reason="Время для сохранения данных в БД")
        self.base_page.refresh_page(wait="domcontentloaded")
        self.client_profile_page.locators.SUBDIVISION_TITLE_NAME.wait_to_have_text(
            f"Подразделение: {self.old_subdivision_name}"
        )
        self.client_profile_page.locators.SUBDIVISIONS_INN.to_have_value(old_client_data.tax_number)
        self.client_profile_page.locators.SUBDIVISIONS_KPP.to_have_value("—")
