import allure
import pytest
from playwright.sync_api import APIRequestContext, Page

from api.nbss.client_requests.client_requests import ClientDataFromResponseGetClientData, ClientRequests
from common.helpers.time_helpers import get_shifted_datetime
from models.user import EntrepreneurClient, IndividualClient, OrganizationClient
from pages.base_page import BasePage
from pages.client_profile_page import ClientProfilePage
from pages.locators.dynamic_form_elements import CreateEntrepreneur
from pages.locators.home_page_elements import HomePage


@allure.epic("E2E_64_1 Редактирование задним числом в PRIME")
@allure.suite("E2E_64_1 Редактирование задним числом в PRIME")
@pytest.mark.regress
class TestEditPastDate:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_ui_stand_login: Page, api_request_context: APIRequestContext) -> None:
        self.base_page = BasePage(nexign_ui_stand_login)
        self.client_profile_page = ClientProfilePage(nexign_ui_stand_login)
        self.home_page = HomePage(nexign_ui_stand_login)
        self.entrepreneur_create_form = CreateEntrepreneur(nexign_ui_stand_login)
        self.client_request_api = ClientRequests(api_request_context)

    @allure.title("Редактирование клиента ЮЛ прошлой датой")
    @allure.id(608620)
    @allure.description("Редактирование клиента ЮЛ прошлой датой")
    def test_edit_legal_client_past_date(self, base_url: str, create_organization: OrganizationClient) -> None:
        user_data = create_organization
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{user_data.user_id}/overview")
        self.client_profile_page.locators.CLIENT_TAB.click(timeout=10000)
        old_client_data = ClientDataFromResponseGetClientData(
            self.client_request_api.get_client_data(user_data.user_id).json()
        )
        self.client_profile_page.locators.ORG_NAME.to_have_value(old_client_data.full_name)
        old_date = get_shifted_datetime("-100d").strftime("%Y-%m-%dT%H:%M:%S")

        self.client_request_api.put_client_data(
            user_data.user_id,
            old_date,
            "organization",
            200,
            reputation_message="Является надежным деловым партнером.",
            customer_name=user_data.customer_name + "_NEW",
            inn=user_data.inn,
            kpp=user_data.kpp,
        )
        self.base_page.refresh_page(wait="domcontentloaded")
        self.client_profile_page.locators.CURRENT_CLIENT_LINK.click()
        self.client_profile_page.locators.CURRENT_CLIENT_LINK.wait_to_have_text(
            "ООО " + user_data.customer_name + "_NEW"
        )
        self.client_profile_page.locators.CLIENT_TAB.click()

        self.client_profile_page.locators.ORG_NAME.to_have_value(user_data.customer_name + "_NEW")
        self.client_profile_page.locators.NATIONALITY.to_have_value("Россия")
        self.client_profile_page.locators.BUSINESS_ACTIVITY.to_have_value("Страховая компания")
        self.client_profile_page.locators.REPUTATION.to_have_value("Является надежным деловым партнером.")
        self.client_profile_page.locators.INN.to_have_value(user_data.inn)
        self.client_profile_page.locators.KPP.to_have_value(user_data.kpp)
        self.client_profile_page.locators.REGISTRATION_DOCUMENT.to_have_value("00D67D7D5751F")
        self.client_profile_page.locators.REGISTRATION_DATE.to_have_value("02.11.2022")
        self.client_profile_page.locators.OKPO.to_have_value("09513533")
        self.client_profile_page.locators.OKATO.to_have_value("46439000156")
        self.client_profile_page.locators.OKVED.to_have_value("4622")
        self.client_profile_page.locators.OGRN.to_have_value("1172375467400")
        self.client_request_api.check_response_content("party.nameInfo.name", "!=", old_client_data.full_name)

    @allure.title("Редактирование клиента ФЛ прошлой датой")
    @allure.id(609274)
    @allure.description("Редактирование клиента ФЛ прошлой датой")
    def test_edit_person_client_past_date(self, base_url: str, create_individual_user: IndividualClient) -> None:
        user = create_individual_user
        new_user = IndividualClient()
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{user.user_id}/overview")
        self.client_profile_page.locators.CLIENT_TAB.click(timeout=10000)
        old_client_data = ClientDataFromResponseGetClientData(
            self.client_request_api.get_client_data(user.user_id).json(), client_type="individual"
        )
        self.client_profile_page.locators.FIO.to_have_value(old_client_data.full_name)
        old_date = get_shifted_datetime("-100d").strftime("%Y-%m-%dT%H:%M:%S")
        self.client_request_api.put_client_data(
            user.user_id,
            old_date,
            "individual",
            200,
            patronymic="Андреич",
            series=new_user.document_serial,
            number=new_user.document_num,
            inn=new_user.inn,
            snils=new_user.snils,
        )
        self.base_page.refresh_page(wait="domcontentloaded")
        self.client_profile_page.locators.CURRENT_CLIENT_LINK.click()
        self.client_profile_page.locators.CURRENT_CLIENT_LINK.wait_to_have_text(
            f"{user.sur_name} {user.first_name} Андреич"
        )
        self.client_request_api.check_response_content("party.nameInfo.name", "!=", old_client_data.full_name)
        self.client_profile_page.locators.CLIENT_TAB.click()

        self.client_profile_page.locators.FIO.to_have_value(f"{user.sur_name} {user.first_name} Андреич")
        self.client_profile_page.locators.DOCUMENT_SERIAL_AND_NUM.to_have_value(
            f"{new_user.document_serial} {new_user.document_num}"
        )
        self.client_profile_page.locators.INN.to_have_value(new_user.inn)
        self.client_profile_page.locators.SNILS.to_have_value(new_user.snils)

    @allure.title("Редактирование клиента ИП прошлой датой")
    @allure.description("Редактирование клиента ИП прошлой датой")
    @allure.id(609275)
    def test_edit_entrepreneur_client_past_date(self, base_url: str, entrepreneur_user_data: EntrepreneurClient) -> None:
        user_1 = entrepreneur_user_data
        with allure.step('Пользователь нажимает на "Создать клиента ИП"'):
            self.home_page.CREATE_ENTREPRENEUR_BTN.click()
            self.entrepreneur_create_form.INN.wait_to_be_visible()
        with allure.step("В открывшейся форме пользователь вводит данные клиента"):
            self.entrepreneur_create_form.fill_data_for_entrepreneur_client(user_1)
        self.entrepreneur_create_form.SAVE_BTN.click()
        self.client_profile_page.locators.CLIENT_TAB.wait_to_be_visible(timeout=15000)
        new_client_id = self.base_page.get_customer_id_from_url()

        self.client_profile_page.locators.CLIENT_TAB.click()
        self.client_profile_page.locators.CLIENT_TYPE.to_contain_text("Индивидуальный предприниматель")
        self.client_profile_page.locators.CLIENT_FIO.to_contain_text(user_1.sur_name)

        self.client_profile_page.locators.PUBLIC_PERSON.wait_to_have_text(user_1.is_public)
        self.client_profile_page.locators.RESIDENT.to_contain_text(user_1.is_resident)
        self.client_profile_page.locators.SPEAKING_LANGUAGE.to_contain_text(user_1.speaking_language)
        self.client_profile_page.locators.NATIONALITY.to_contain_text(user_1.nationality)
        self.client_profile_page.locators.BUSINESS_ACTIVITY.to_contain_text(user_1.business_activity)
        self.client_profile_page.locators.NOTE.to_contain_text(user_1.note)
        self.client_profile_page.locators.REPUTATION.to_contain_text(user_1.reputation)

        self.client_profile_page.locators.GENDER.to_contain_text(user_1.gender)
        self.client_profile_page.locators.DOCUMENT_TYPE.to_contain_text(user_1.document_type)
        self.client_profile_page.locators.DOCUMENT_SERIAL_AND_NUM.to_contain_text(user_1.document_serial)
        self.client_profile_page.locators.DOCUMENT_SERIAL_AND_NUM.to_contain_text(user_1.document_num)
        self.client_profile_page.locators.DOCUMENT_PROVIDE_BY.to_contain_text(user_1.document_provide_by)
        self.client_profile_page.locators.DOCUMENT_DIVISION_CODE.to_contain_text(user_1.document_division_code)
        self.client_profile_page.locators.DOCUMENT_DATE.to_contain_text(user_1.document_date)
        self.client_profile_page.locators.DOCUMENT_VALID_DATE.to_contain_text(user_1.document_valid_date)
        self.client_profile_page.locators.BIRTH_DATE.to_contain_text(user_1.birth_date)
        self.client_profile_page.locators.BIRTH_PLACE.to_contain_text(user_1.birth_place)
        self.client_profile_page.locators.INN.to_contain_text(user_1.inn)
        self.client_profile_page.locators.SNILS.to_contain_text(user_1.snils)
        self.client_profile_page.locators.TAX_SCHEME.to_contain_text(user_1.tax_scheme)

        old_date = get_shifted_datetime("-100d").strftime("%Y-%m-%dT%H:%M:%S")
        user_2 = EntrepreneurClient()
        self.client_request_api.put_client_data(
            new_client_id,
            old_date,
            "entrepreneur",
            200,
            surname=user_2.sur_name,
            first_name=user_2.first_name,
            patronymic="Андреич",
            series=user_2.document_serial,
            number=user_2.document_num,
            inn=user_2.inn,
            snils=user_2.snils,
        )
        self.base_page.refresh_page(wait="domcontentloaded")
        self.client_profile_page.locators.CURRENT_CLIENT_LINK.click()
        self.client_profile_page.locators.CURRENT_CLIENT_LINK.wait_to_have_text(
            f"ИП {user_2.sur_name} {user_2.first_name} Андреич"
        )
        self.client_request_api.check_response_content("party.nameInfo.name", "not has", user_1.sur_name)

        self.client_profile_page.locators.CLIENT_TAB.click()
        self.client_profile_page.locators.FIO.to_have_value(f"{user_2.sur_name} {user_2.first_name} Андреич")
        self.client_profile_page.locators.DOCUMENT_SERIAL_AND_NUM.to_contain_text(
            f"{user_2.document_serial} {user_2.document_num}"
        )
        self.client_profile_page.locators.INN.to_contain_text(user_2.inn)
        self.client_profile_page.locators.SNILS.to_contain_text(user_2.snils)

    @allure.title("Применение изменений прошлой датой без изменения данных клиента")
    @allure.id(609653)
    @allure.description("Применение изменений прошлой датой без изменения данных клиента")
    def test_edit_person_client_without_data_changes(
        self, base_url: str, create_individual_user: IndividualClient
    ) -> None:
        new_client_id = create_individual_user.user_id
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{new_client_id}/overview")
        self.client_profile_page.locators.CLIENT_TAB.click(timeout=10000)
        old_client_data = ClientDataFromResponseGetClientData(
            self.client_request_api.get_client_data(new_client_id).json(), client_type="individual"
        )
        self.client_profile_page.locators.FIO.to_have_value(old_client_data.full_name)
        old_date = get_shifted_datetime("-100d").strftime("%Y-%m-%dT%H:%M:%S")
        self.client_request_api.put_client_data(new_client_id, old_date, "without_changes", 200)
        self.base_page.refresh_page(wait="domcontentloaded")
        self.client_profile_page.locators.CURRENT_CLIENT_LINK.click()
        self.client_profile_page.locators.CURRENT_CLIENT_LINK.wait_to_have_text(old_client_data.full_name)
        self.client_request_api.check_response_content("party.nameInfo.name", "==", old_client_data.full_name)
        self.client_profile_page.locators.CLIENT_TAB.click()

        self.client_profile_page.locators.FIO.to_have_value(old_client_data.full_name)
        self.client_profile_page.locators.DOCUMENT_SERIAL_AND_NUM.to_have_value(
            f"{old_client_data.document_series} {old_client_data.document_num}"
        )

    @allure.title("Ошибка редактирования клиента будущей датой")
    @allure.id(609657)
    @allure.description("Ошибка редактирования клиента будущей датой")
    def test_edit_person_client_future_date(self, base_url: str, create_individual_user: IndividualClient) -> None:
        new_client_id = create_individual_user.user_id
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{new_client_id}/overview")
        self.client_profile_page.locators.CLIENT_TAB.click(timeout=10000)
        old_client_data = ClientDataFromResponseGetClientData(
            self.client_request_api.get_client_data(new_client_id).json(), client_type="individual"
        )
        self.client_profile_page.locators.FIO.to_have_value(old_client_data.full_name)
        old_date = get_shifted_datetime("+2d").strftime("%Y-%m-%dT%H:%M:%S")
        self.client_request_api.put_client_data(new_client_id, old_date, "without_changes", 400)
        self.client_request_api.check_response_content("userMessage", "==", "Невозможно установить дату в будущем")
