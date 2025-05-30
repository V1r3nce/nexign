import datetime

import allure
import pytest
from playwright.sync_api import APIRequestContext, Page

from api.requests.client_requests import ClientDataFromResponseGetClientData, ClientRequests
from common.helpers.checker import assert_that
from common.helpers.data_generator import faker_ru, get_shifted_datetime
from models.user import EntrepreneurUser, IndividualUser, OrgUser
from pages.base_page import BasePage
from pages.client_profile_page import ClientProfilePage
from pages.locators.dynamic_form_elements import CreateEntrepreneur
from pages.locators.home_page_elements import HomePage


@allure.epic("E2E_64_1 Редактирование задним числом в PRIME")
@allure.suite("E2E_64_1 Редактирование задним числом в PRIME")
@allure.tag("can_auth", "success")
@pytest.mark.regress
class TestEditPastDate:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_ui_stand_login: Page, api_request_auth_context: APIRequestContext) -> None:
        self.base_page = BasePage(nexign_ui_stand_login)
        self.client_profile_page = ClientProfilePage(nexign_ui_stand_login)
        self.home_page = HomePage(nexign_ui_stand_login)
        self.entrepreneur_create_form = CreateEntrepreneur(nexign_ui_stand_login)
        self.client_request_api = ClientRequests(api_request_auth_context)

    @allure.title("Редактирование клиента ЮЛ прошлой датой")
    @allure.id(608620)
    @allure.description("Редактирование клиента ЮЛ прошлой датой")
    def test_edit_legal_client_past_date(self, base_url: str, create_organization: int) -> None:
        user = OrgUser
        new_client_id = create_organization
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{new_client_id}/overview")
        self.client_profile_page.locators.CLIENT_TAB.click()
        old_client_data = ClientDataFromResponseGetClientData(
            self.client_request_api.get_client_data(new_client_id).json()
        )
        self.client_profile_page.locators.ORG_NAME.to_have_value(old_client_data.full_name)
        old_date = get_shifted_datetime("-100d").strftime("%Y-%m-%dT%H:%M:%S")
        new_client_data = self.client_request_api.put_client_data(
            new_client_id,
            old_date,
            "organization",
            200,
            reputation_message="Является надежным деловым партнером.",
            customer_name=user.customer_name,
            inn=user.inn,
            kpp=user.kpp,
        )
        self.base_page.refresh_page(wait="domcontentloaded")
        self.client_profile_page.locators.CURRENT_CLIENT_LINK.click()
        self.client_profile_page.locators.CURRENT_CLIENT_LINK.wait_to_have_text(f"ООО {user.customer_name}")
        self.client_profile_page.locators.CLIENT_TAB.click()

        self.client_profile_page.locators.ORG_NAME.to_have_value(user.customer_name)
        self.client_profile_page.locators.NATIONALITY.to_have_value("Россия")
        self.client_profile_page.locators.BUSINESS_ACTIVITY.to_have_value("Страховая компания")
        self.client_profile_page.locators.REPUTATION.to_have_value("Является надежным деловым партнером.")
        self.client_profile_page.locators.INN.to_have_value(user.inn)
        self.client_profile_page.locators.KPP.to_have_value(user.kpp)
        self.client_profile_page.locators.REGISTRATION_DOCUMENT.to_have_value("00D67D7D5751F")
        self.client_profile_page.locators.REGISTRATION_DATE.to_have_value("02.11.2022")
        self.client_profile_page.locators.OKPO.to_have_value("09513533")
        self.client_profile_page.locators.OKATO.to_have_value("46439000156")
        self.client_profile_page.locators.OKVED.to_have_value("4622")
        self.client_profile_page.locators.OGRN.to_have_value("1172375467400")
        assert_that(
            lambda: new_client_data.json()["party"]["nameInfo"]["name"] != old_client_data.full_name,
            "Не изменилось название ЮЛ",
        )

    @allure.title("Редактирование клиента ФЛ прошлой датой")
    @allure.id(609274)
    @allure.description("Редактирование клиента ФЛ прошлой датой")
    def test_edit_person_client_past_date(self, base_url: str, create_user: int) -> None:
        user = IndividualUser
        new_client_id = create_user
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{new_client_id}/overview")
        self.client_profile_page.locators.CLIENT_TAB.click()
        old_client_data = ClientDataFromResponseGetClientData(
            self.client_request_api.get_client_data(new_client_id).json(), client_type="individual"
        )
        self.client_profile_page.locators.FIO.to_have_value(old_client_data.full_name)
        old_date = get_shifted_datetime("-100d").strftime("%Y-%m-%dT%H:%M:%S")
        new_client_data = self.client_request_api.put_client_data(
            new_client_id,
            old_date,
            "individual",
            200,
            patronymic="Андреич",
            series=user.document_serial,
            number=user.document_num,
            inn=user.inn,
            snils=user.snils,
        )
        self.base_page.refresh_page(wait="domcontentloaded")
        self.client_profile_page.locators.CURRENT_CLIENT_LINK.click()
        self.client_profile_page.locators.CURRENT_CLIENT_LINK.wait_to_have_text(f"{old_client_data.full_name} Андреич")
        assert_that(
            lambda: new_client_data.json()["party"]["nameInfo"]["name"] != old_client_data.full_name,
            "Не изменилось имя ФЛ",
        )
        self.client_profile_page.locators.CLIENT_TAB.click()

        self.client_profile_page.locators.FIO.to_have_value(f"{old_client_data.full_name} Андреич")
        self.client_profile_page.locators.DOCUMENT_SERIAL_AND_NUM.to_have_value(
            f"{user.document_serial} {user.document_num}"
        )
        self.client_profile_page.locators.INN.to_have_value(user.inn)
        self.client_profile_page.locators.SNILS.to_have_value(user.snils)

    @allure.title("Редактирование клиента ИП прошлой датой")
    @allure.description("Редактирование клиента ИП прошлой датой")
    @allure.id(609275)
    def test_edit_entrepreneur_client_past_date(self, base_url: str) -> None:
        registration_date = faker_ru.date_between(datetime.date(1990, 1, 1), datetime.date(2020, 12, 31))
        document_date = faker_ru.date_between(datetime.date(1990, 1, 1), datetime.date(2020, 12, 31)).strftime(
            "%d.%m.%Y"
        )
        document_valid_date = faker_ru.date_between(datetime.datetime.today(), get_shifted_datetime("+500d")).strftime(
            "%d.%m.%Y"
        )
        user_1 = EntrepreneurUser()
        with allure.step('Пользователь нажимает на "Создать клиента ИП"'):
            self.home_page.CREATE_ENTREPRENEUR_BTN.click()
            self.entrepreneur_create_form.INN.wait_to_be_visible()
        with allure.step("В открывшейся форме пользователь вводит данные клиента"):
            self.entrepreneur_create_form.fill_data_for_entrepreneur_client(
                registration_date=registration_date.strftime("%d.%m.%Y"),
                snils=user_1.snils,
                okpo=user_1.okpo,
                okato=user_1.okato,
                okved=user_1.okved,
                ogrn=user_1.ogrn,
                inn=user_1.inn,
                last_name=user_1.last_name,
                first_name=user_1.first_name,
                document_serial=user_1.document_serial,
                document_num=user_1.document_num,
                document_division_code=user_1.document_division_code,
                document_date=document_date,
                document_valid_date=document_valid_date,
                birth_date=user_1.birth_date,
                birth_place=user_1.birth_place,
                contact_phone=user_1.contact_phone,
                contact_email=user_1.contact_email,
                note=user_1.note,
            )
        self.entrepreneur_create_form.SAVE_BTN.click()
        self.client_profile_page.locators.CLIENT_TAB.wait_to_be_visible(timeout=15000)
        new_client_id = self.base_page.get_customer_id_from_url()

        self.client_profile_page.locators.CLIENT_TAB.click()
        self.client_profile_page.locators.CLIENT_TYPE.to_contain_text("Индивидуальный предприниматель")
        self.client_profile_page.locators.CLIENT_FIO.to_contain_text("Автотестович")

        self.client_profile_page.locators.PUBLIC_PERSON.wait_to_have_text("Да")
        self.client_profile_page.locators.RESIDENT.to_contain_text("Да")
        self.client_profile_page.locators.SPEAKING_LANGUAGE.to_contain_text("Русский")
        self.client_profile_page.locators.NATIONALITY.to_contain_text("Россия")
        self.client_profile_page.locators.BUSINESS_ACTIVITY.to_contain_text("Агент")
        self.client_profile_page.locators.NOTE.to_contain_text(user_1.note)
        self.client_profile_page.locators.REPUTATION.to_contain_text("Автотестовая репутация")

        self.client_profile_page.locators.GENDER.to_contain_text("Мужской")
        self.client_profile_page.locators.DOCUMENT_TYPE.to_contain_text("Паспорт гражданина РФ")
        self.client_profile_page.locators.DOCUMENT_SERIAL_AND_NUM.to_contain_text(user_1.document_serial)
        self.client_profile_page.locators.DOCUMENT_SERIAL_AND_NUM.to_contain_text(user_1.document_num)
        self.client_profile_page.locators.DOCUMENT_PROVIDE_BY.to_contain_text("ГУ МВД РОССИИ")
        self.client_profile_page.locators.DOCUMENT_DIVISION_CODE.to_contain_text(user_1.document_division_code)
        self.client_profile_page.locators.DOCUMENT_DATE.to_contain_text(document_date)
        self.client_profile_page.locators.DOCUMENT_VALID_DATE.to_contain_text(document_valid_date)
        self.client_profile_page.locators.BIRTH_DATE.to_contain_text(user_1.birth_date)
        self.client_profile_page.locators.BIRTH_PLACE.to_contain_text(user_1.birth_place)
        self.client_profile_page.locators.INN.to_contain_text(user_1.inn)
        self.client_profile_page.locators.SNILS.to_contain_text(user_1.snils)
        self.client_profile_page.locators.TAX_SCHEME.to_contain_text("Схема налогообложения по умолчанию")

        old_date = get_shifted_datetime("-100d").strftime("%Y-%m-%dT%H:%M:%S")
        user_2 = EntrepreneurUser()
        new_client_data = self.client_request_api.put_client_data(
            new_client_id,
            old_date,
            "entrepreneur",
            200,
            surname=user_2.last_name,
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
            f"ИП {user_2.last_name} {user_2.first_name} Андреич"
        )
        assert_that(
            lambda: user_1.last_name not in new_client_data.json()["party"]["nameInfo"]["name"],
            "Не изменилось имя ИП",
        )
        self.client_profile_page.locators.CLIENT_TAB.click()
        self.client_profile_page.locators.FIO.to_have_value(f"{user_2.last_name} {user_2.first_name} Андреич")
        self.client_profile_page.locators.DOCUMENT_SERIAL_AND_NUM.to_contain_text(
            f"{user_2.document_serial} {user_2.document_num}"
        )
        self.client_profile_page.locators.INN.to_contain_text(user_2.inn)
        self.client_profile_page.locators.SNILS.to_contain_text(user_2.snils)

    @allure.title("Применение изменений прошлой датой без изменения данных клиента")
    @allure.id(609653)
    @allure.description("Применение изменений прошлой датой без изменения данных клиента")
    def test_edit_person_client_without_data_changes(self, base_url: str, create_user: int) -> None:
        new_client_id = create_user
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{new_client_id}/overview")
        self.client_profile_page.locators.CLIENT_TAB.click()
        old_client_data = ClientDataFromResponseGetClientData(
            self.client_request_api.get_client_data(new_client_id).json(), client_type="individual"
        )
        self.client_profile_page.locators.FIO.to_have_value(old_client_data.full_name)
        old_date = get_shifted_datetime("-100d").strftime("%Y-%m-%dT%H:%M:%S")
        new_client_data = self.client_request_api.put_client_data(new_client_id, old_date, "without_changes", 200)
        self.base_page.refresh_page(wait="domcontentloaded")
        self.client_profile_page.locators.CURRENT_CLIENT_LINK.click()
        self.client_profile_page.locators.CURRENT_CLIENT_LINK.wait_to_have_text(old_client_data.full_name)
        assert_that(
            lambda: new_client_data.json()["party"]["nameInfo"]["name"] == old_client_data.full_name,
            "Изменилось имя ФЛ",
        )
        self.client_profile_page.locators.CLIENT_TAB.click()

        self.client_profile_page.locators.FIO.to_have_value(old_client_data.full_name)
        self.client_profile_page.locators.DOCUMENT_SERIAL_AND_NUM.to_have_value(
            f"{old_client_data.document_series} {old_client_data.document_num}"
        )

    @allure.title("Ошибка редактирования клиента будущей датой")
    @allure.id(609657)
    @allure.description("Ошибка редактирования клиента будущей датой")
    def test_edit_person_client_future_date(self, base_url: str, create_user: int) -> None:
        new_client_id = create_user
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{new_client_id}/overview")
        self.client_profile_page.locators.CLIENT_TAB.click()
        old_client_data = ClientDataFromResponseGetClientData(
            self.client_request_api.get_client_data(new_client_id).json(), client_type="individual"
        )
        self.client_profile_page.locators.FIO.to_have_value(old_client_data.full_name)
        old_date = get_shifted_datetime("+2d").strftime("%Y-%m-%dT%H:%M:%S")
        client_response = self.client_request_api.put_client_data(new_client_id, old_date, "without_changes", 400)
        assert_that(
            lambda: client_response.json()["userMessage"] == "Невозможно установить дату в будущем",
            "Прошло изменение данных клиента с датой в будущем",
        )
