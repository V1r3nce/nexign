import allure
import pytest
from playwright.sync_api import APIRequestContext, Page

from api.requests.client_requests import ClientRequests
from common.helpers.data_generator import (
    generate_random_number,
    generate_russian_string,
    get_shifted_datetime,
)
from common.helpers.time_helpers import delay
from pages.client_profile_page import ClientProfilePage
from pages.locators.base_elements import BaseElements
from pages.locators.dynamic_form_elements import CreateSalesAndServiceManagement, RequestCreate
from pages.locators.home_page_elements import HomePage
from pages.locators.inquiries_page import InquiriesPage
from pages.locators.select_product_offers_form import SelectProductOffersForm
from tests.ui_tests.personal_account.conftest import Client


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
        self.inquiries_page = InquiriesPage(nexign_ui_stand_login)
        self.product_offer = SelectProductOffersForm(nexign_ui_stand_login)
        self.home_page = HomePage(nexign_ui_stand_login)
        self.client_request = ClientRequests(api_request_auth_context)

        self.last_year = get_shifted_datetime("-500d").strftime("%d.%m.%Y")
        self.last_year_plus_day = get_shifted_datetime("-499d").strftime("%d.%m.%Y")
        self.next_year = get_shifted_datetime("+500d").strftime("%d.%m.%Y")
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
        create_user_b2c: Client,
        create_organization: int,
        base_url: str,
    ) -> None:
        client_b2c = create_user_b2c

        self.client_profile_page.open(
            f"{base_url}customer-hierarchy-management/customers/{create_organization}/overview"
        )

        self.client_request.product_sale(user_id=create_organization, category="internet", product_offering_id=500001)

        self.client_profile_page.locators.PRODUCTS_TAB.click()
        self.client_profile_page.locators.SUBSCRIBER.click(0)
        self.client_profile_page.add_existing_end_user(str(client_b2c.passport_series), str(client_b2c.passport_number))
        self.client_profile_page.end_user_form.CLOSE_END_USER_MODAL_BUTTON.click()

        self.client_profile_page.locators.SUBSCRIBER.click(0)
        self.client_profile_page.check_end_user_form(
            surname=client_b2c.customer_surname,
            name=client_b2c.customer_name,
            patronymic=client_b2c.customer_patronymic,
            gender="Мужской",
            passport_series=str(client_b2c.passport_series),
            passport_number=str(client_b2c.passport_number),
            who_issued_the_document="ГУ МВД РОССИИ",
            subdivision_code="123-456",
            document_date_of_issue=self.last_year,
            document_valid_for=self.next_year,
            birth_date="11.07.1983",
        )

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
    def test_create_end_user_when_client_not_exists(self, create_organization: int, base_url: str) -> None:
        passport_series = str(generate_random_number(4))
        passport_number = str(generate_random_number(6))
        surname = "Тест" + generate_russian_string(5)
        name = "Пользователь"
        patronymic = "Конечный"
        subdivision_code = str(generate_random_number(3)) + "-" + str(generate_random_number(3))
        birth_date = "23.03.1998"

        self.client_profile_page.open(
            f"{base_url}customer-hierarchy-management/customers/{create_organization}/overview"
        )

        self.client_request.product_sale(user_id=create_organization, category="internet", product_offering_id=500001)

        self.client_profile_page.locators.PRODUCTS_TAB.click()
        self.client_profile_page.locators.SUBSCRIBER.click(0)
        self.client_profile_page.add_non_existing_end_user(
            passport_series,
            passport_number,
            surname,
            name,
            patronymic,
            subdivision_code,
            self.last_year,
            self.next_year,
            birth_date,
        )
        self.client_profile_page.end_user_form.CLOSE_END_USER_MODAL_BUTTON.click()

        self.client_profile_page.locators.SUBSCRIBER.click(0)
        self.client_profile_page.check_end_user_form(
            surname=surname,
            name=name,
            patronymic=patronymic,
            gender="Мужской",
            passport_series=passport_series,
            passport_number=passport_number,
            who_issued_the_document="ГУ МВД РОССИИ",
            subdivision_code=subdivision_code,
            document_date_of_issue=self.last_year,
            document_valid_for=self.next_year,
            birth_date=birth_date,
        )

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
    def test_check_end_user_editing(self, create_organization: int, base_url: str) -> None:
        passport_series = str(generate_random_number(4))
        passport_number = str(generate_random_number(6))
        surname = "Тест" + generate_russian_string(5)
        name = "Пользователь"
        patronymic = "Конечный"
        subdivision_code = str(generate_random_number(3)) + "-" + str(generate_random_number(3))
        birth_date = "23.03.1998"

        birth_date_edited = "23.03.1990"
        subdivision_code_edited = str(generate_random_number(3)) + "-" + str(generate_random_number(3))

        self.client_profile_page.open(
            f"{base_url}customer-hierarchy-management/customers/{create_organization}/overview"
        )

        self.client_request.product_sale(user_id=create_organization, category="internet", product_offering_id=500001)

        self.client_profile_page.locators.PRODUCTS_TAB.click()
        self.client_profile_page.locators.SUBSCRIBER.click(0)
        self.client_profile_page.add_non_existing_end_user(
            passport_series,
            passport_number,
            surname,
            name,
            patronymic,
            subdivision_code,
            self.last_year,
            self.next_year,
            birth_date,
        )

        self.client_profile_page.end_user_form.EDIT_END_USER_BUTTON.click()
        self.client_profile_page.end_user_form.SURNAME_INPUT.wait_to_be_visible()
        self.client_profile_page.end_user_form.LOADER.not_to_be_visible()
        self.client_profile_page.end_user_form.SURNAME_INPUT.fill(surname + surname)
        self.client_profile_page.end_user_form.NAME_INPUT.fill(name + name)
        self.client_profile_page.end_user_form.PATRONYMIC_INPUT.fill(patronymic + patronymic)
        self.client_profile_page.end_user_form.GENDER_DROPDOWN.select_by_value("Женский")
        self.client_profile_page.end_user_form.WHO_ISSUED_THE_DOCUMENT_INPUT.fill("ГУ МВД БЕЛАРУСИ")
        self.client_profile_page.end_user_form.SUBDIVISION_CODE_INPUT.fill(subdivision_code_edited)
        self.client_profile_page.end_user_form.DATE_OF_ISSUE_INPUT.click()
        self.client_profile_page.end_user_form.DATE_OF_ISSUE_INPUT.clear_input()
        self.client_profile_page.end_user_form.DATE_OF_ISSUE_INPUT.type(self.last_year_plus_day)
        self.client_profile_page.press_keyboard_button("Enter")
        self.client_profile_page.end_user_form.DOCUMENT_VALID_FOR_INPUT.click()
        self.client_profile_page.end_user_form.DOCUMENT_VALID_FOR_INPUT.clear_input()
        self.client_profile_page.end_user_form.DOCUMENT_VALID_FOR_INPUT.type(self.next_year_plus_day)
        self.client_profile_page.press_keyboard_button("Enter")
        self.client_profile_page.end_user_form.PLACE_OF_BIRTH_INPUT.fill("Гродно")
        self.client_profile_page.end_user_form.BIRTHDAY_INPUT.click()
        self.client_profile_page.end_user_form.BIRTHDAY_INPUT.clear_input()
        self.client_profile_page.end_user_form.BIRTHDAY_INPUT.type(birth_date_edited)
        self.client_profile_page.press_keyboard_button("Enter")
        self.client_profile_page.end_user_form.LANGUAGE_DROPDOWN.select_by_value("Английский")
        self.client_profile_page.end_user_form.REGISTRATION_ADDRESS_INPUT.select_by_value(
            "Россия, Санкт-Петербург г., ул. Уральская"
        )
        self.client_profile_page.end_user_form.IS_PUBLIC_CHECKBOX.click()
        self.client_profile_page.end_user_form.IS_RESIDENT_CHECKBOX.click()
        self.client_profile_page.end_user_form.INNER_ACCEPT_BTN.click()
        self.client_profile_page.end_user_form.INNER_ACCEPT_BTN.not_to_be_visible()

        self.client_profile_page.check_end_user_form(
            surname=surname + surname,
            name=name + name,
            patronymic=patronymic + patronymic,
            gender="Женский",
            passport_series=passport_series,
            passport_number=passport_number,
            who_issued_the_document="ГУ МВД БЕЛАРУСИ",
            subdivision_code=subdivision_code_edited,
            document_date_of_issue=self.last_year_plus_day,
            document_valid_for=self.next_year_plus_day,
            birth_date=birth_date_edited,
            language="Английский",
            is_public="Да",
            is_resident="Нет",
            place_of_birth="Гродно",
        )

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
        create_user_b2c: Client,
        create_organization: int,
        base_url: str,
    ) -> None:
        passport_series = str(generate_random_number(4))
        passport_number = str(generate_random_number(6))
        surname = "Тест" + generate_russian_string(5)
        name = "Пользователь"
        patronymic = "Конечный"
        subdivision_code = str(generate_random_number(3)) + "-" + str(generate_random_number(3))
        birth_date = "23.03.1998"

        client_b2c = create_user_b2c

        self.client_profile_page.open(
            f"{base_url}customer-hierarchy-management/customers/{create_organization}/overview"
        )

        self.client_request.product_sale(user_id=create_organization, category="internet", product_offering_id=500001)

        self.client_profile_page.locators.PRODUCTS_TAB.click()
        self.client_profile_page.locators.SUBSCRIBER.click(0)
        self.client_profile_page.add_non_existing_end_user(
            passport_series,
            passport_number,
            surname,
            name,
            patronymic,
            subdivision_code,
            self.last_year,
            self.next_year,
            birth_date,
        )
        self.client_profile_page.end_user_form.CLOSE_END_USER_MODAL_BUTTON.click()

        self.client_profile_page.locators.SUBSCRIBER.click(0)
        self.client_profile_page.check_end_user_form(
            surname=surname,
            name=name,
            patronymic=patronymic,
            gender="Мужской",
            passport_series=passport_series,
            passport_number=passport_number,
            who_issued_the_document="ГУ МВД РОССИИ",
            subdivision_code=subdivision_code,
            document_date_of_issue=self.last_year,
            document_valid_for=self.next_year,
            birth_date=birth_date,
        )

        self.client_profile_page.end_user_form.REPLACE_END_USER_BUTTON.click()
        self.client_profile_page.add_existing_end_user(str(client_b2c.passport_series), str(client_b2c.passport_number))
        self.client_profile_page.end_user_form.CLOSE_END_USER_MODAL_BUTTON.click()

        self.client_profile_page.locators.SUBSCRIBER.click(0)
        self.client_profile_page.check_end_user_form(
            surname=client_b2c.customer_surname,
            name=client_b2c.customer_name,
            patronymic=client_b2c.customer_patronymic,
            gender="Мужской",
            passport_series=str(client_b2c.passport_series),
            passport_number=str(client_b2c.passport_number),
            who_issued_the_document="ГУ МВД РОССИИ",
            subdivision_code="123-456",
            document_date_of_issue=self.last_year,
            document_valid_for=self.next_year,
            birth_date="11.07.1983",
        )

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
        create_user_b2c: Client,
        create_organization: int,
        base_url: str,
    ) -> None:
        client_b2c = create_user_b2c

        self.client_profile_page.open(
            f"{base_url}customer-hierarchy-management/customers/{create_organization}/overview"
        )

        self.client_request.product_sale(user_id=create_organization, category="internet", product_offering_id=500001)

        self.client_profile_page.locators.PRODUCTS_TAB.click()
        self.client_profile_page.locators.SUBSCRIBER.click(0)
        self.client_profile_page.add_existing_end_user(str(client_b2c.passport_series), str(client_b2c.passport_number))
        self.client_profile_page.end_user_form.CLOSE_END_USER_MODAL_BUTTON.click()

        self.client_profile_page.locators.RELATED_PERSONS_TAB.click()
        self.client_profile_page.locators.RELATED_PERSONS.click(1)
        delay(3, "Не успевают подтянуться данные по конечному пользователю")
        self.client_profile_page.check_related_person(
            surname=client_b2c.customer_surname,
            name=client_b2c.customer_name,
            patronymic=client_b2c.customer_patronymic,
            gender="Мужской",
            passport_series=str(client_b2c.passport_series),
            passport_number=str(client_b2c.passport_number),
            who_issued_the_document="ГУ МВД РОССИИ",
            subdivision_code="123-456",
            document_date_of_issue=self.last_year,
            document_valid_for=self.next_year,
            birth_date="11.07.1983",
        )

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
        create_user_b2c: Client,
        create_organization: int,
        base_url: str,
    ) -> None:
        passport_series = str(generate_random_number(4))
        passport_number = str(generate_random_number(6))
        subdivision_code = str(generate_random_number(3)) + "-" + str(generate_random_number(3))
        inn = str(generate_random_number(12))

        client_b2c = create_user_b2c

        self.client_profile_page.open(
            f"{base_url}customer-hierarchy-management/customers/{create_organization}/overview"
        )

        self.client_request.product_sale(user_id=create_organization, category="internet", product_offering_id=500001)

        self.client_profile_page.locators.PRODUCTS_TAB.click()
        self.client_profile_page.locators.SUBSCRIBER.click(0)
        self.client_profile_page.add_existing_end_user(str(client_b2c.passport_series), str(client_b2c.passport_number))
        self.client_profile_page.end_user_form.CLOSE_END_USER_MODAL_BUTTON.click()

        self.client_profile_page.locators.SUBSCRIBER.click(0)
        self.client_profile_page.check_end_user_form(
            client_b2c.customer_surname,
            client_b2c.customer_name,
            client_b2c.customer_patronymic,
            "Мужской",
            str(client_b2c.passport_series),
            str(client_b2c.passport_number),
            "ГУ МВД РОССИИ",
            "123-456",
            self.last_year,
            self.next_year,
            "11.07.1983",
        )
        self.client_profile_page.end_user_form.CLOSE_END_USER_MODAL_BUTTON.click()

        self.client_profile_page.locators.RELATED_PERSONS_TAB.click()
        self.client_profile_page.locators.RELATED_PERSONS.click(1)
        delay(3, "Не успевают подтянуться данные по конечному пользователю")
        self.client_profile_page.check_related_person(
            client_b2c.customer_surname,
            client_b2c.customer_name,
            client_b2c.customer_patronymic,
            "Мужской",
            str(client_b2c.passport_series),
            str(client_b2c.passport_number),
            "ГУ МВД РОССИИ",
            "123-456",
            self.last_year,
            self.next_year,
            "11.07.1983",
        )

        self.client_profile_page.locators.RELATED_PERSON_CLIENT_FL.click()
        self.client_profile_page.locators.PERSONAL_DATA_LOADER.wait_to_be_visible()
        self.client_profile_page.locators.PERSONAL_DATA_LOADER.not_to_be_visible()
        self.client_profile_page.locators.FIO.to_contain_text(
            f"{client_b2c.customer_surname} {client_b2c.customer_name} {client_b2c.customer_patronymic}"
        )
        self.client_profile_page.locators.GENDER.to_contain_text("Мужской")
        self.client_profile_page.locators.DOCUMENT_TYPE.to_contain_text("Паспорт гражданина РФ")
        self.client_profile_page.locators.DOCUMENT_SERIAL_AND_NUM.to_contain_text(
            f"{client_b2c.passport_series} {client_b2c.passport_number}"
        )
        self.client_profile_page.locators.DOCUMENT_PROVIDE_BY.to_contain_text("ГУ МВД РОССИИ")
        self.client_profile_page.locators.DOCUMENT_DIVISION_CODE.to_contain_text("123-456")
        self.client_profile_page.locators.DOCUMENT_DATE.to_contain_text(self.last_year)
        self.client_profile_page.locators.DOCUMENT_VALID_DATE.to_contain_text(self.next_year)
        self.client_profile_page.locators.BIRTH_PLACE.to_contain_text("Москва")
        self.client_profile_page.locators.BIRTH_DATE.to_contain_text("11.07.1983")
        self.client_profile_page.locators.COUNTRY.to_contain_text("Россия")
        self.client_profile_page.locators.SPEAKING_LANGUAGE.to_contain_text("Русский")
        self.client_profile_page.locators.PUBLIC_PERSON.to_contain_text("Нет")
        self.client_profile_page.locators.RESIDENT.to_contain_text("Да")
        self.client_profile_page.locators.INN.to_contain_text("123456789123")

        self.client_profile_page.locators.EDIT_BTN.click()
        self.client_profile_page.edit_client_form.EDIT_FORM_LOADER.not_to_be_visible()
        self.client_profile_page.edit_client_form.SURNAME_INPUT.wait_to_be_visible()
        self.client_profile_page.edit_client_form.SURNAME_INPUT.fill(
            str(client_b2c.customer_surname + client_b2c.customer_surname)
        )
        self.client_profile_page.edit_client_form.NAME_INPUT.fill(
            str(client_b2c.customer_name + client_b2c.customer_name)
        )
        self.client_profile_page.edit_client_form.PATRONYMIC_INPUT.fill(
            str(client_b2c.customer_patronymic + client_b2c.customer_patronymic)
        )
        self.client_profile_page.edit_client_form.IS_PUBLIC_CHECKBOX.click()
        self.client_profile_page.edit_client_form.IS_RESIDENT_CHECKBOX.click()
        self.client_profile_page.edit_client_form.LANGUAGE_DROPDOWN.select_by_value("Английский")
        self.client_profile_page.edit_client_form.REGISTRATION_ADDRESS.select_by_value(
            "Россия, Санкт-Петербург г., ул. Уральская"
        )
        self.client_profile_page.edit_client_form.BIRTH_PLACE.fill("Гродно")
        self.client_profile_page.edit_client_form.BIRTH_DATE.clear_input()
        self.client_profile_page.edit_client_form.BIRTH_DATE.type("23.03.1998")
        self.client_profile_page.edit_client_form.GENDER.select_by_value("Женский")
        self.client_profile_page.edit_client_form.DOCUMENT_SERIAL.fill(passport_series)
        self.client_profile_page.edit_client_form.DOCUMENT_NUMBER.fill(passport_number)
        self.client_profile_page.edit_client_form.DOCUMENT_DATE.clear_input()
        self.client_profile_page.edit_client_form.DOCUMENT_DATE.type(self.last_year_plus_day)
        self.client_profile_page.edit_client_form.DOCUMENT_PROVIDE_BY.fill("ГУ МВД БЕЛАРУСИ")
        self.client_profile_page.edit_client_form.DOCUMENT_DIVISION_CODE.fill(subdivision_code)
        self.client_profile_page.edit_client_form.DOCUMENT_VALID_DATE.clear_input()
        self.client_profile_page.edit_client_form.DOCUMENT_VALID_DATE.type(self.next_year_plus_day)
        self.client_profile_page.edit_client_form.INN.fill(inn)
        self.client_profile_page.edit_client_form.TAX_SCHEME.select_by_value("Схема налогообложения по умолчанию")
        self.client_profile_page.edit_client_form.SAVE_BTN.click()
        self.client_profile_page.edit_client_form.SAVE_BTN.not_to_be_visible()

        self.client_profile_page.refresh_page()
        self.client_profile_page.locators.CLIENT_FIO.to_contain_text(
            f"{client_b2c.customer_surname + client_b2c.customer_surname} {client_b2c.customer_name + client_b2c.customer_name} {client_b2c.customer_patronymic + client_b2c.customer_patronymic}"
        )
        self.client_profile_page.locators.GENDER.to_contain_text("Женский")
        self.client_profile_page.locators.DOCUMENT_TYPE.to_contain_text("Паспорт гражданина РФ")
        self.client_profile_page.locators.DOCUMENT_SERIAL_AND_NUM.to_contain_text(f"{passport_series} {passport_number}")
        self.client_profile_page.locators.DOCUMENT_PROVIDE_BY.to_contain_text("ГУ МВД БЕЛАРУСИ")
        self.client_profile_page.locators.DOCUMENT_DIVISION_CODE.to_contain_text(subdivision_code)
        self.client_profile_page.locators.DOCUMENT_DATE.to_contain_text(self.last_year_plus_day)
        self.client_profile_page.locators.DOCUMENT_VALID_DATE.to_contain_text(self.next_year_plus_day)
        self.client_profile_page.locators.BIRTH_PLACE.to_contain_text("Гродно")
        self.client_profile_page.locators.BIRTH_DATE.to_contain_text("23.03.1998")
        self.client_profile_page.locators.COUNTRY.to_contain_text("Россия")
        self.client_profile_page.locators.SPEAKING_LANGUAGE.to_contain_text("Английский")
        self.client_profile_page.locators.PUBLIC_PERSON.to_contain_text("Да")
        self.client_profile_page.locators.RESIDENT.to_contain_text("Нет")
        self.client_profile_page.locators.INN.to_contain_text(inn)

        self.client_profile_page.open(
            f"{base_url}customer-hierarchy-management/customers/{create_organization}/overview"
        )

        self.client_profile_page.locators.RELATED_PERSONS_TAB.click()
        self.client_profile_page.locators.RELATED_PERSONS.click(1)
        self.client_profile_page.check_related_person(
            client_b2c.customer_surname + client_b2c.customer_surname,
            client_b2c.customer_name + client_b2c.customer_name,
            client_b2c.customer_patronymic + client_b2c.customer_patronymic,
            "Женский",
            passport_series,
            passport_number,
            "ГУ МВД БЕЛАРУСИ",
            subdivision_code,
            self.last_year_plus_day,
            self.next_year_plus_day,
            "23.03.1998",
            "Россия",
            "Английский",
            "Да",
            "Нет",
            "Гродно",
            "inn",
        )

        self.client_profile_page.locators.PRODUCTS_TAB.click()
        self.client_profile_page.locators.SUBSCRIBER.click(0)
        self.client_profile_page.check_end_user_form(
            client_b2c.customer_surname + client_b2c.customer_surname,
            client_b2c.customer_name + client_b2c.customer_name,
            client_b2c.customer_patronymic + client_b2c.customer_patronymic,
            "Женский",
            passport_series,
            passport_number,
            "ГУ МВД БЕЛАРУСИ",
            subdivision_code,
            self.last_year_plus_day,
            self.next_year_plus_day,
            "23.03.1998",
            "Россия",
            "Английский",
            "Да",
            "Нет",
            "Гродно",
        )
