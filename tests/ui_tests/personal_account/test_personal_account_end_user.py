import allure
import pytest
from playwright.sync_api import APIRequestContext, Page

from api.requests.client_requests import ClientRequests
from common.helpers.time_helpers import delay, get_shifted_datetime
from models.user import IndividualClient, OrganizationClient
from pages.client_profile_page import ClientProfilePage
from pages.locators.base_elements import BaseElements
from pages.locators.dynamic_form_elements import CreateSalesAndServiceManagement, RequestCreate
from pages.locators.home_page_elements import HomePage
from pages.locators.inquiries_elements import InquiriesElements
from pages.locators.select_product_offers_form import SelectProductOffersForm


@allure.epic("E2E_33_1 Подключение персональных счетов")
@allure.suite("E2E_33_1 Подключение персональных счетов")
@allure.tag("can_auth", "success")
@pytest.mark.regress
class TestPersonalAccountEndUser:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_ui_stand_login: Page, api_request_auth_context: APIRequestContext) -> None:
        self.client_profile_page = ClientProfilePage(nexign_ui_stand_login)
        self.base_elements = BaseElements(nexign_ui_stand_login)
        self.create_request = RequestCreate(nexign_ui_stand_login)
        self.create_sales_and_service = CreateSalesAndServiceManagement(nexign_ui_stand_login)
        self.inquiries_page = InquiriesElements(nexign_ui_stand_login)
        self.product_offer = SelectProductOffersForm(nexign_ui_stand_login)
        self.home_page = HomePage(nexign_ui_stand_login)
        self.client_request = ClientRequests(api_request_auth_context)

        self.last_year_plus_day = get_shifted_datetime("-499d").strftime("%d.%m.%Y")
        self.next_year_plus_day = get_shifted_datetime("+501d").strftime("%d.%m.%Y")

    @allure.title("02 Добавление Конечного пользователя Абоненту (клиент существует))")
    @allure.id(605659)
    @allure.link(
        url="allure.nexign.com/project/313/test-cases/605659",
        name="02 Добавление Конечного пользователя Абоненту (клиент существует)",
    )
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=691454115",
        name="КР [UDS] Управление персональными счетами без управления лимитами (Детальное)",
    )
    @pytest.mark.smoke
    def test_create_end_user_when_client_exists(
        self,
        create_individual_user: IndividualClient,
        create_organization: OrganizationClient,
        base_url: str,
    ) -> None:
        client_b2c = create_individual_user
        client_b2b = create_organization

        self.client_profile_page.open(f"{base_url}customer-hierarchy-management/customers/{client_b2b.user_id}/overview")

        self.client_request.product_sale(user_id=client_b2b.user_id, category="internet", product_offering_id=500001)

        self.client_profile_page.locators.PRODUCTS_TAB.click()
        self.client_profile_page.locators.SUBSCRIBER.click(0)
        self.client_profile_page.add_existing_end_user(client_b2c)
        self.client_profile_page.end_user_form.CLOSE_END_USER_MODAL_BUTTON.click()

        self.client_profile_page.locators.SUBSCRIBER.click(0)
        self.client_profile_page.check_end_user_form(client_b2c)

    @allure.title("02 Добавление Конечного пользователя Абоненту (клиент не существует)")
    @allure.id(605659)
    @allure.link(
        url="allure.nexign.com/project/313/test-cases/605659",
        name="02 Добавление Конечного пользователя Абоненту (клиент не существует)",
    )
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=691454115",
        name="КР [UDS] Управление персональными счетами без управления лимитами (Детальное)",
    )
    def test_create_end_user_when_client_not_exists(
        self, create_organization: OrganizationClient, base_url: str, individual_user_data: IndividualClient
    ) -> None:
        self.client_profile_page.open(
            f"{base_url}customer-hierarchy-management/customers/{create_organization.user_id}/overview"
        )
        user_data = individual_user_data
        client_b2b = create_organization
        self.client_request.product_sale(user_id=client_b2b.user_id, category="internet", product_offering_id=500001)

        self.client_profile_page.locators.PRODUCTS_TAB.click()
        self.client_profile_page.locators.SUBSCRIBER.click(0)
        self.client_profile_page.add_non_existing_end_user(user_data)
        self.client_profile_page.end_user_form.CLOSE_END_USER_MODAL_BUTTON.click()

        self.client_profile_page.locators.SUBSCRIBER.click(0)
        self.client_profile_page.check_end_user_form(user_data)

    @allure.title("03 Редактирования Конечного Пользователя Абонента")
    @allure.id(581355)
    @allure.link(
        url="allure.nexign.com/project/313/test-cases/581355",
        name="03 Редактирования Конечного Пользователя Абонента",
    )
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=691454115",
        name="КР [UDS] Управление персональными счетами без управления лимитами (Детальное)",
    )
    def test_check_end_user_editing(
        self, create_organization: OrganizationClient, base_url: str, individual_user_data: IndividualClient
    ) -> None:
        self.client_profile_page.open(
            f"{base_url}customer-hierarchy-management/customers/{create_organization.user_id}/overview"
        )
        user_data = individual_user_data
        client_b2b = create_organization
        self.client_request.product_sale(user_id=client_b2b.user_id, category="internet", product_offering_id=500001)

        self.client_profile_page.locators.PRODUCTS_TAB.click()
        self.client_profile_page.locators.SUBSCRIBER.click(0)
        self.client_profile_page.add_non_existing_end_user(user_data)

        user_data.speaking_language = "Английский"
        user_data.birth_place = "Гродно"
        user_data.birth_date = "23.03.1998"
        user_data.gender = "Женский"
        user_data.issue_date = self.last_year_plus_day
        user_data.document_valid_date = self.next_year_plus_day
        user_data.document_provide_by = "ГУ МВД БЕЛАРУСИ"
        user_data.is_public = "Да"
        user_data.is_resident = "Нет"

        self.client_profile_page.end_user_form.EDIT_END_USER_BUTTON.click()
        self.client_profile_page.end_user_form.SURNAME_INPUT.wait_to_be_visible()
        self.client_profile_page.end_user_form.LOADER.not_to_be_visible()
        self.client_profile_page.end_user_form.SURNAME_INPUT.fill(user_data.sur_name)
        self.client_profile_page.end_user_form.NAME_INPUT.fill(user_data.first_name)
        self.client_profile_page.end_user_form.PATRONYMIC_INPUT.fill(user_data.patronymic)
        self.client_profile_page.end_user_form.GENDER_DROPDOWN.select_by_value(user_data.gender)
        self.client_profile_page.end_user_form.WHO_ISSUED_THE_DOCUMENT_INPUT.fill(user_data.document_provide_by)
        self.client_profile_page.end_user_form.SUBDIVISION_CODE_INPUT.fill(user_data.document_division_code)
        self.client_profile_page.end_user_form.DATE_OF_ISSUE_INPUT.click()
        self.client_profile_page.end_user_form.DATE_OF_ISSUE_INPUT.clear_input()
        self.client_profile_page.end_user_form.DATE_OF_ISSUE_INPUT.type(user_data.issue_date)
        self.client_profile_page.press_keyboard_button("Enter")
        self.client_profile_page.end_user_form.DOCUMENT_VALID_FOR_INPUT.click()
        self.client_profile_page.end_user_form.DOCUMENT_VALID_FOR_INPUT.clear_input()
        self.client_profile_page.end_user_form.DOCUMENT_VALID_FOR_INPUT.type(user_data.document_valid_date)
        self.client_profile_page.press_keyboard_button("Enter")
        self.client_profile_page.end_user_form.PLACE_OF_BIRTH_INPUT.fill(user_data.birth_place)
        self.client_profile_page.end_user_form.BIRTHDAY_INPUT.click()
        self.client_profile_page.end_user_form.BIRTHDAY_INPUT.clear_input()
        self.client_profile_page.end_user_form.BIRTHDAY_INPUT.type(user_data.birth_date)
        self.client_profile_page.press_keyboard_button("Enter")
        self.client_profile_page.end_user_form.LANGUAGE_DROPDOWN.select_by_value(user_data.speaking_language)
        self.client_profile_page.end_user_form.REGISTRATION_ADDRESS_INPUT.select_by_value(user_data.registration_address)
        self.client_profile_page.end_user_form.IS_PUBLIC_CHECKBOX.click()
        self.client_profile_page.end_user_form.IS_RESIDENT_CHECKBOX.click()
        self.client_profile_page.end_user_form.INNER_ACCEPT_BTN.click()
        self.client_profile_page.end_user_form.INNER_ACCEPT_BTN.not_to_be_visible()

        self.client_profile_page.check_end_user_form(user_data)

    @allure.title("04 Замена Конечного Пользователя Абонента")
    @allure.id(581356)
    @allure.link(
        url="allure.nexign.com/project/313/test-cases/581356",
        name="04 Замена Конечного Пользователя Абонента",
    )
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=691454115",
        name="КР [UDS] Управление персональными счетами без управления лимитами (Детальное)",
    )
    def test_check_end_user_replacement(
        self,
        create_individual_user: IndividualClient,
        individual_user_data: IndividualClient,
        create_organization: OrganizationClient,
        base_url: str,
    ) -> None:
        client_b2c = create_individual_user
        non_exist_client_b2c = individual_user_data
        client_b2b = create_organization

        self.client_profile_page.open(f"{base_url}customer-hierarchy-management/customers/{client_b2b.user_id}/overview")

        self.client_request.product_sale(user_id=client_b2b.user_id, category="internet", product_offering_id=500001)

        self.client_profile_page.locators.PRODUCTS_TAB.click()
        self.client_profile_page.locators.SUBSCRIBER.click(0)
        self.client_profile_page.add_non_existing_end_user(client_b2c)
        self.client_profile_page.end_user_form.CLOSE_END_USER_MODAL_BUTTON.click()

        self.client_profile_page.locators.SUBSCRIBER.click(0)
        self.client_profile_page.check_end_user_form(client_b2c)

        self.client_profile_page.end_user_form.REPLACE_END_USER_BUTTON.click()
        self.client_profile_page.add_existing_end_user(non_exist_client_b2c)
        self.client_profile_page.end_user_form.CLOSE_END_USER_MODAL_BUTTON.click()

        self.client_profile_page.locators.SUBSCRIBER.click(0)
        self.client_profile_page.check_end_user_form(non_exist_client_b2c)

    @allure.title("05 Просмотр Связанных лиц с ролью Конечный пользователь")
    @allure.id(582386)
    @allure.link(
        url="allure.nexign.com/project/313/test-cases/582386",
        name="05 Просмотр Связанных лиц с ролью Конечный пользователь",
    )
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=691454115",
        name="КР [UDS] Управление персональными счетами без управления лимитами (Детальное)",
    )
    def test_check_end_user_on_related_persons_form(
        self,
        create_individual_user: IndividualClient,
        create_organization: OrganizationClient,
        base_url: str,
    ) -> None:
        client_b2c = create_individual_user
        client_b2b = create_organization

        self.client_profile_page.open(f"{base_url}customer-hierarchy-management/customers/{client_b2b.user_id}/overview")

        self.client_request.product_sale(user_id=client_b2b.user_id, category="internet", product_offering_id=500001)

        self.client_profile_page.locators.PRODUCTS_TAB.click()
        self.client_profile_page.locators.SUBSCRIBER.click(0)
        self.client_profile_page.add_existing_end_user(client_b2c)
        self.client_profile_page.end_user_form.CLOSE_END_USER_MODAL_BUTTON.click()

        self.client_profile_page.locators.RELATED_PERSONS_TAB.click()
        self.client_profile_page.locators.RELATED_PERSONS.click(1)
        delay(3, "Не успевают подтянуться данные по конечному пользователю")
        self.client_profile_page.check_related_person(client_b2c)

    @allure.title("07 Редактирование Связанных лиц с ролью Конечный пользователь('Редактирование Клиента (физ.лицо)')")
    @allure.id(584086)
    @allure.link(
        url="allure.nexign.com/project/313/test-cases/584086",
        name="07 Редактирование Связанных лиц с ролью Конечный пользователь('Редактирование Клиента (физ.лицо)')",
    )
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=691454115",
        name="КР [UDS] Управление персональными счетами без управления лимитами (Детальное)",
    )
    def test_check_end_user_editing_on_related_persons_form(
        self,
        create_individual_user: IndividualClient,
        create_organization: OrganizationClient,
        base_url: str,
    ) -> None:
        client_b2c = create_individual_user
        client_b2b = create_organization
        self.client_profile_page.open(f"{base_url}customer-hierarchy-management/customers/{client_b2b.user_id}/overview")

        self.client_request.product_sale(user_id=client_b2b.user_id, category="internet", product_offering_id=500001)

        self.client_profile_page.locators.PRODUCTS_TAB.click()
        self.client_profile_page.locators.SUBSCRIBER.click(0)
        self.client_profile_page.add_existing_end_user(client_b2c)
        self.client_profile_page.end_user_form.CLOSE_END_USER_MODAL_BUTTON.click()

        self.client_profile_page.locators.SUBSCRIBER.click(0)
        self.client_profile_page.check_end_user_form(client_b2c)
        self.client_profile_page.end_user_form.CLOSE_END_USER_MODAL_BUTTON.click()

        self.client_profile_page.locators.RELATED_PERSONS_TAB.click()
        self.client_profile_page.locators.RELATED_PERSONS.click(1)
        delay(3, "Не успевают подтянуться данные по конечному пользователю")
        self.client_profile_page.check_related_person(client_b2c)

        self.client_profile_page.locators.RELATED_PERSON_CLIENT_FL.click()
        self.client_profile_page.locators.PERSONAL_DATA_LOADER.wait_to_be_visible()
        self.client_profile_page.locators.PERSONAL_DATA_LOADER.not_to_be_visible()
        self.client_profile_page.locators.FIO.to_contain_text(
            f"{client_b2c.sur_name} {client_b2c.first_name} {client_b2c.patronymic}"
        )
        self.client_profile_page.locators.GENDER.to_contain_text(client_b2c.gender)
        self.client_profile_page.locators.DOCUMENT_TYPE.to_contain_text(client_b2c.document_type)
        self.client_profile_page.locators.DOCUMENT_SERIAL_AND_NUM.to_contain_text(
            f"{client_b2c.document_serial} {client_b2c.document_num}"
        )
        self.client_profile_page.locators.DOCUMENT_PROVIDE_BY.to_contain_text(client_b2c.document_provide_by)
        self.client_profile_page.locators.DOCUMENT_DIVISION_CODE.to_contain_text(client_b2c.document_division_code)
        self.client_profile_page.locators.DOCUMENT_DATE.to_contain_text(client_b2c.document_date)
        self.client_profile_page.locators.DOCUMENT_VALID_DATE.to_contain_text(client_b2c.document_valid_date)
        self.client_profile_page.locators.BIRTH_PLACE.to_contain_text(client_b2c.birth_place)
        self.client_profile_page.locators.BIRTH_DATE.to_contain_text(client_b2c.birth_date)
        self.client_profile_page.locators.COUNTRY.to_contain_text(client_b2c.nationality)
        self.client_profile_page.locators.SPEAKING_LANGUAGE.to_contain_text(client_b2c.speaking_language)
        self.client_profile_page.locators.PUBLIC_PERSON.to_contain_text(client_b2c.is_public)
        self.client_profile_page.locators.RESIDENT.to_contain_text(client_b2c.is_resident)
        self.client_profile_page.locators.INN.to_contain_text(client_b2c.inn)

        client_b2c.sur_name = client_b2c.sur_name + client_b2c.sur_name
        client_b2c.first_name = client_b2c.first_name + client_b2c.first_name
        client_b2c.patronymic = client_b2c.patronymic + client_b2c.patronymic
        client_b2c.speaking_language = "Английский"
        client_b2c.birth_place = "Гродно"
        client_b2c.birth_date = "23.03.1998"
        client_b2c.gender = "Женский"
        client_b2c.document_date = self.last_year_plus_day
        client_b2c.document_valid_date = self.next_year_plus_day
        client_b2c.document_provide_by = "ГУ МВД БЕЛАРУСИ"
        client_b2c.is_resident = "Нет"
        client_b2c.is_public = ""

        self.client_profile_page.locators.EDIT_BTN.click()
        self.client_profile_page.edit_client_form.EDIT_FORM_LOADER.not_to_be_visible()
        self.client_profile_page.edit_client_form.SURNAME_INPUT.wait_to_be_visible()
        self.client_profile_page.edit_client_form.SURNAME_INPUT.fill(client_b2c.sur_name + client_b2c.sur_name)
        self.client_profile_page.edit_client_form.NAME_INPUT.fill(client_b2c.first_name + client_b2c.first_name)
        self.client_profile_page.edit_client_form.PATRONYMIC_INPUT.fill(client_b2c.patronymic + client_b2c.patronymic)
        self.client_profile_page.edit_client_form.IS_PUBLIC_CHECKBOX.click()
        self.client_profile_page.edit_client_form.IS_RESIDENT_CHECKBOX.click()
        self.client_profile_page.edit_client_form.LANGUAGE_DROPDOWN.select_by_value(client_b2c.speaking_language)
        self.client_profile_page.edit_client_form.REGISTRATION_ADDRESS.select_by_value(client_b2c.registration_address)

        self.client_profile_page.edit_client_form.BIRTH_PLACE.fill(client_b2c.birth_place)
        self.client_profile_page.edit_client_form.BIRTH_DATE.clear_input()
        self.client_profile_page.edit_client_form.BIRTH_DATE.type(client_b2c.birth_date)
        self.client_profile_page.edit_client_form.GENDER.select_by_value(client_b2c.gender)
        self.client_profile_page.edit_client_form.DOCUMENT_SERIAL.fill(client_b2c.document_serial)
        self.client_profile_page.edit_client_form.DOCUMENT_NUMBER.fill(client_b2c.document_num)
        self.client_profile_page.edit_client_form.DOCUMENT_DATE.clear_input()
        self.client_profile_page.edit_client_form.DOCUMENT_DATE.type(client_b2c.document_date)
        self.client_profile_page.edit_client_form.DOCUMENT_PROVIDE_BY.fill(client_b2c.document_provide_by)
        self.client_profile_page.edit_client_form.DOCUMENT_DIVISION_CODE.fill(client_b2c.document_division_code)
        self.client_profile_page.edit_client_form.DOCUMENT_VALID_DATE.clear_input()
        self.client_profile_page.edit_client_form.DOCUMENT_VALID_DATE.type(client_b2c.document_valid_date)
        self.client_profile_page.edit_client_form.INN.fill(client_b2c.inn)
        self.client_profile_page.edit_client_form.TAX_SCHEME.select_by_value(client_b2c.tax_scheme)
        self.client_profile_page.edit_client_form.SAVE_BTN.click()
        self.client_profile_page.edit_client_form.SAVE_BTN.not_to_be_visible()

        self.client_profile_page.refresh_page()
        self.client_profile_page.locators.CLIENT_FIO.to_contain_text(
            f"{client_b2c.sur_name} {client_b2c.first_name} {client_b2c.patronymic}"
        )

        self.client_profile_page.locators.GENDER.to_contain_text(client_b2c.gender)
        self.client_profile_page.locators.DOCUMENT_TYPE.to_contain_text(client_b2c.document_type)
        self.client_profile_page.locators.DOCUMENT_SERIAL_AND_NUM.to_contain_text(
            f"{client_b2c.document_serial} {client_b2c.document_num}"
        )
        self.client_profile_page.locators.DOCUMENT_PROVIDE_BY.to_contain_text(client_b2c.document_provide_by)
        self.client_profile_page.locators.DOCUMENT_DIVISION_CODE.to_contain_text(client_b2c.document_division_code)
        self.client_profile_page.locators.DOCUMENT_DATE.to_contain_text(client_b2c.document_date)
        self.client_profile_page.locators.DOCUMENT_VALID_DATE.to_contain_text(client_b2c.document_valid_date)
        self.client_profile_page.locators.BIRTH_PLACE.to_contain_text(client_b2c.birth_place)
        self.client_profile_page.locators.BIRTH_DATE.to_contain_text(client_b2c.birth_date)
        self.client_profile_page.locators.COUNTRY.to_contain_text(client_b2c.nationality)
        self.client_profile_page.locators.SPEAKING_LANGUAGE.to_contain_text(client_b2c.speaking_language)
        self.client_profile_page.locators.PUBLIC_PERSON.to_contain_text(client_b2c.is_public)
        self.client_profile_page.locators.RESIDENT.to_contain_text(client_b2c.is_resident)
        self.client_profile_page.locators.INN.to_contain_text(client_b2c.inn)

        self.client_profile_page.open(f"{base_url}customer-hierarchy-management/customers/{client_b2b.user_id}/overview")

        self.client_profile_page.locators.RELATED_PERSONS_TAB.click()
        self.client_profile_page.locators.RELATED_PERSONS.click(1)
        self.client_profile_page.check_related_person(client_b2c)

        self.client_profile_page.locators.PRODUCTS_TAB.click()
        self.client_profile_page.locators.SUBSCRIBER.click(0)
        self.client_profile_page.check_end_user_form(client_b2c)
