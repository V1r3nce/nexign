import allure
import pytest
from playwright.sync_api import APIRequestContext, Page

from api.requests.client_requests import ClientDataFromResponseGetClientData, ClientRequests
from common.helpers.checker import assert_that
from common.helpers.data_generator import get_shifted_datetime
from common.helpers.time_helpers import delay
from models.user import OrgUser
from pages.base_page import BasePage
from pages.client_profile_page import ClientProfilePage
from pages.locators.dynamic_form_elements import CreateEntrepreneur


@allure.epic("E2E_64_1 Редактирование задним числом в PRIME")
@allure.suite("E2E_64_1 Редактирование задним числом в PRIME")
@pytest.mark.regress
class TestEditPastDateSubdivision:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_ui_stand_login: Page, api_request_auth_context: APIRequestContext) -> None:
        self.base_page = BasePage(nexign_ui_stand_login)
        self.client_profile_page = ClientProfilePage(nexign_ui_stand_login)
        self.entrepreneur_create_form = CreateEntrepreneur(nexign_ui_stand_login)
        self.client_request_api = ClientRequests(api_request_auth_context)
        self.user = OrgUser
        self.old_subdivision_name = "Флюгеггехайнен"

    @allure.title("Редактирование подразделения клиента прошлой датой")
    @allure.id(608621)
    @allure.description("Редактирование подразделения клиента прошлой датой")
    def test_edit_client_subdivision_past_date(self, base_url: str, create_organization: int) -> None:
        old_date_1 = get_shifted_datetime("-101d").strftime("%Y-%m-%dT%H:%M:%S")
        old_date_2 = get_shifted_datetime("-100d").strftime("%Y-%m-%dT%H:%M:%S")
        new_client_id = create_organization
        old_client_data = ClientDataFromResponseGetClientData(
            self.client_request_api.get_client_data(new_client_id).json()
        )
        self.client_request_api.put_client_data(
            new_client_id,
            old_date_1,
            "organization",
            200,
            reputation_message="Является надежным деловым партнером.",
            customer_name=old_client_data.full_name,
            inn=old_client_data.tax_number,
            kpp=old_client_data.tax_number[:-1],
        )
        delay(0.5, reason="Время для сохранения данных в БД")
        subdivision_id = self.client_request_api.make_subdivision(new_client_id, self.old_subdivision_name)
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{new_client_id}/overview")
        self.client_profile_page.locators.SUBDIVISIONS_TAB.click()
        self.client_profile_page.locators.SUBDIVISIONS_NAMES[0].click()

        self.client_profile_page.locators.SUBDIVISION_ADDRESS.wait_to_be_visible()
        self.client_profile_page.locators.SUBDIVISIONS_INN.to_have_value(old_client_data.tax_number)
        subdivision = self.client_request_api.put_client_subdivision_data(
            subdivision_id, old_date_2, 200, True, new_name=self.user.customer_name, kpp=self.user.kpp
        )
        with allure.step("Проверка, что вернулись корректные данные в ответе"):
            assert_that(
                lambda: subdivision.json()["party"]["nameInfo"]["name"] == self.user.customer_name,
                "Не изменилось название подразделения ЮЛ",
            )
            assert_that(
                lambda: subdivision.json()["party"]["taxRegistrationCertificate"]["taxIdentificationNumber"]
                == old_client_data.tax_number,
                "Не корректное ИНН подразделения ЮЛ",
            )
            assert_that(
                lambda: subdivision.json()["party"]["taxRegistrationCertificate"]["registrationReasonCode"]
                == self.user.kpp,
                "Не корректное КПП подразделения ЮЛ",
            )
        delay(0.5, reason="Время для сохранения данных в БД")

        self.base_page.refresh_page(wait="domcontentloaded")
        self.client_profile_page.locators.SUBDIVISION_TITLE_NAME.wait_to_have_text(
            f"Подразделение: {self.user.customer_name}"
        )
        self.client_profile_page.locators.SUBDIVISIONS_INN.to_have_value(old_client_data.tax_number)
        self.client_profile_page.locators.SUBDIVISIONS_KPP.to_have_value(self.user.kpp)

    @allure.title("Ошибка редактирования подразделения датой раньше даты создания клиента")
    @allure.id(609476)
    @allure.description("Ошибка редактирования подразделения датой раньше даты создания клиента")
    def test_edit_client_subdivision_past_date_earlier_than_client(
        self, base_url: str, create_organization: int
    ) -> None:
        old_date = get_shifted_datetime("-100d").strftime("%Y-%m-%dT%H:%M:%S")
        new_client_id = create_organization
        old_client_data = ClientDataFromResponseGetClientData(
            self.client_request_api.get_client_data(new_client_id).json()
        )
        subdivision_id = self.client_request_api.make_subdivision(new_client_id, self.old_subdivision_name)
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{new_client_id}/overview")
        self.client_profile_page.locators.SUBDIVISIONS_TAB.click()
        self.client_profile_page.locators.SUBDIVISIONS_NAMES[0].click()

        self.client_profile_page.locators.SUBDIVISION_ADDRESS.wait_to_be_visible()
        self.client_profile_page.locators.SUBDIVISIONS_INN.to_have_value(old_client_data.tax_number)
        subdivision = self.client_request_api.put_client_subdivision_data(
            subdivision_id, old_date, 400, True, new_name=self.user.customer_name, kpp=self.user.kpp
        )
        with allure.step("Проверка, что вернулись корректные данные в ответе"):
            assert_that(
                lambda: subdivision.json()["userMessage"]
                == "Дата применения изменений не может быть указана раньше даты создания клиента"
                ". Укажите дату применения изменений на подразделении позже даты создания"
                " клиента или измените дату создания клиента",
                "Прошло изменение данных подразделения клиента с датой раньше создания клиента",
            )

    @allure.title("Ошибка редактирования подразделения будущей датой")
    @allure.id(609658)
    @allure.description("Ошибка редактирования подразделения будущей датой")
    def test_edit_client_subdivision_future_date(self, base_url: str, create_organization: int) -> None:
        old_date = get_shifted_datetime("+7d").strftime("%Y-%m-%dT%H:%M:%S")
        new_client_id = create_organization
        old_client_data = ClientDataFromResponseGetClientData(
            self.client_request_api.get_client_data(new_client_id).json()
        )
        subdivision_id = self.client_request_api.make_subdivision(new_client_id, self.old_subdivision_name)
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{new_client_id}/overview")
        self.client_profile_page.locators.SUBDIVISIONS_TAB.click()
        self.client_profile_page.locators.SUBDIVISIONS_NAMES[0].click()

        self.client_profile_page.locators.SUBDIVISION_ADDRESS.wait_to_be_visible()
        self.client_profile_page.locators.SUBDIVISIONS_INN.to_have_value(old_client_data.tax_number)
        subdivision = self.client_request_api.put_client_subdivision_data(
            subdivision_id, old_date, 400, True, new_name=self.user.customer_name, kpp=self.user.kpp
        )
        with allure.step("Проверка, что вернулись корректные данные в ответе"):
            assert_that(
                lambda: subdivision.json()["userMessage"] == "Невозможно установить дату в будущем",
                "Прошло изменение данных подразделения клиента с датой в будущем",
            )

    @allure.title("Применение изменений прошлой датой без изменения данных подразделения")
    @allure.id(609659)
    @allure.description("Применение изменений прошлой датой без изменения данных подразделения")
    def test_edit_client_subdivision_past_date_without_update(self, base_url: str, create_organization: int) -> None:
        old_date_1 = get_shifted_datetime("-101d").strftime("%Y-%m-%dT%H:%M:%S")
        old_date_2 = get_shifted_datetime("-100d").strftime("%Y-%m-%dT%H:%M:%S")
        new_client_id = create_organization
        old_client_data = ClientDataFromResponseGetClientData(
            self.client_request_api.get_client_data(new_client_id).json()
        )
        self.client_request_api.put_client_data(
            new_client_id,
            old_date_1,
            "organization",
            200,
            reputation_message="Является надежным деловым партнером.",
            customer_name=old_client_data.full_name,
            inn=old_client_data.tax_number,
            kpp=old_client_data.tax_number[:-1],
        )
        delay(0.5, reason="Время для сохранения данных в БД")
        subdivision_id = self.client_request_api.make_subdivision(new_client_id, self.old_subdivision_name)
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{new_client_id}/overview")
        self.client_profile_page.locators.SUBDIVISIONS_TAB.click()
        self.client_profile_page.locators.SUBDIVISIONS_NAMES[0].click()

        self.client_profile_page.locators.SUBDIVISION_ADDRESS.wait_to_be_visible()
        self.client_profile_page.locators.SUBDIVISIONS_INN.to_have_value(old_client_data.tax_number)
        subdivision = self.client_request_api.put_client_subdivision_data(subdivision_id, old_date_2, 200, False)
        with allure.step("Проверка, что вернулись корректные данные в ответе"):
            assert_that(
                lambda: subdivision.json()["party"]["nameInfo"]["name"] == self.old_subdivision_name,
                "Изменилось название подразделения ЮЛ",
            )
            assert_that(
                lambda: subdivision.json()["party"]["taxRegistrationCertificate"]["taxIdentificationNumber"]
                == old_client_data.tax_number,
                "Не корректное ИНН подразделения ЮЛ",
            )
            assert_that(
                lambda: subdivision.json()["party"]["taxRegistrationCertificate"]["registrationReasonCode"] is None,
                "Не корректное КПП подразделения ЮЛ",
            )

        delay(0.5, reason="Время для сохранения данных в БД")
        self.base_page.refresh_page(wait="domcontentloaded")
        self.client_profile_page.locators.SUBDIVISION_TITLE_NAME.wait_to_have_text(
            f"Подразделение: {self.old_subdivision_name}"
        )
        self.client_profile_page.locators.SUBDIVISIONS_INN.to_have_value(old_client_data.tax_number)
        self.client_profile_page.locators.SUBDIVISIONS_KPP.to_have_value("—")
