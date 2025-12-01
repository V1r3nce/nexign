import allure
import pytest
from playwright.sync_api import APIRequestContext, Page

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from models.inquiry import prepare_inquiries
from models.user import IndividualClient, generate_individual_client
from pages.locators.nbss.client.client_profile import ClientProfile
from pages.locators.nbss.client.client_search import ClientSearch
from pages.locators.nbss.dynamic_form_elements import (
    ClientChoice,
    CreateSalesAndServiceManagement,
    IndividualCustomerCreate,
)
from pages.locators.nbss.home_page_elements import HomePage
from pages.locators.nbss.inquiries_elements import ProductEditForm
from pages.locators.nbss.select_product_offers_form import SelectProductOffersForm
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.inquiries_page import InquiriesPage
from pages.nbss.personal_account_page import PersonalAccountPage


@allure.suite("E2E_64 Создание и управление клиентом и его иерархиями")
@pytest.mark.regress
@pytest.mark.usefixtures("nexign_ui_stand_login")
@pytest.mark.nbss_portal
@pytest.mark.praim
class TestIndividualCustomerCreate:
    @pytest.fixture(autouse=True)
    def setup(self, page: Page, individual_user_data: IndividualClient, api_request_context: APIRequestContext) -> None:
        self.home_page = HomePage(page)
        self.customer_create_form = IndividualCustomerCreate(page)
        self.client_search_page = ClientSearch(page)
        self.create_request_form = CreateSalesAndServiceManagement(page)
        self.client_choice = ClientChoice(page)
        self.client_profile = ClientProfile(page)
        self.client_profile_page = ClientProfilePage(page)
        self.inquiries_page = InquiriesPage(page)
        self.product_offer_form = SelectProductOffersForm(page)
        self.product_edit_form = ProductEditForm(page)
        self.user = individual_user_data
        self.client_request_api = ClientInquiriesRequests(api_request_context)
        self.personal_account_page = PersonalAccountPage(page)

    @allure.title("Создание ФЛ клиента, заполнены все поля")
    @allure.description("Сценарий регистрация клиента B2C - ФЛ")
    @allure.id(484399)
    @pytest.mark.smoke
    def test_individual_customer_create(self, base_url: str) -> None:
        with allure.step('Пользователь нажимает на "Создать клиента ФЛ"'):
            self.home_page.CREATE_CUSTOMER_BTN.click()
            self.customer_create_form.LAST_NAME.wait_to_be_visible()
        with allure.step("В открывшейся форме пользователь вводит данные клиента"):
            self.customer_create_form.fill_data_for_individual_client(self.user)
        with allure.step("Сохранить клиента"):
            allure.description("Форма заполнения данных закрывается, открывается форму клиентской карточки")
            self.customer_create_form.SAVE_BTN.click()
            self.customer_create_form.LAST_NAME.not_to_be_visible(timeout=10000)

            self.client_profile.CLIENT_TAB.click()
            self.client_profile.CLIENT_FIO.to_contain_text(self.user.sur_name)
            self.client_profile.GENDER.to_have_value(self.user.gender)
            self.client_profile.DOCUMENT_TYPE.to_contain_text(self.user.document_type)
            self.client_profile.DOCUMENT_SERIAL_AND_NUM.to_contain_text(self.user.document_serial)
            self.client_profile.DOCUMENT_SERIAL_AND_NUM.to_contain_text(self.user.document_num)
            self.client_profile.DOCUMENT_PROVIDE_BY.to_contain_text(self.user.document_provide_by)
            self.client_profile.DOCUMENT_DIVISION_CODE.to_contain_text(self.user.document_division_code)
            self.client_profile.DOCUMENT_DATE.to_contain_text(self.user.document_date)
            self.client_profile.DOCUMENT_VALID_DATE.to_contain_text(self.user.document_valid_date)
            self.client_profile.BIRTH_DATE.to_contain_text(self.user.birth_date)
            self.client_profile.BIRTH_PLACE.to_contain_text(self.user.birth_place)
            self.client_profile.INN.to_contain_text(self.user.inn)
            self.client_profile.SNILS.to_contain_text(self.user.snils)

            self.client_profile.RELATED_PERSONS_TAB.click()
            self.client_profile.RELATED_PERSONS.wait_elements_visible(0, timeout=10000)
            self.client_profile.RELATED_PERSONS.to_contain_text(0, self.user.sur_name)
            self.client_profile.RELATED_MOBILE_PHONE.to_contain_text(self.user.contact_phone, clear_phone=True)
            self.client_profile.RELATED_EMAIL.to_contain_text(self.user.contact_email)

        with allure.step("Ищем клиента"):
            self.home_page.HOME_BTN.click()
            self.home_page.HEADER_SEARCH_BTN.click()

            self.client_search_page.FOUNDED_CLIENTS.not_to_be_visible()
            self.client_profile_page.search_client(inn=self.user.inn, customer_status="Действующий")
            self.client_search_page.FOUNDED_CLIENTS.wait_to_be_visible()

        with allure.step("Открываем форму продажи"):
            self.home_page.CREATE_APPLICATION.click()
            self.create_request_form.NEED_SPD.wait_to_be_visible(timeout=20000)
            self.create_request_form.SELECT_CLIENT_BTN.wait_to_be_enabled()
            self.create_request_form.SELECT_CLIENT_BTN.select_by_value("Выбрать клиента")

            self.client_choice.INN.fill(self.user.inn)
            self.client_choice.FIND_BTN.click()

            self.client_choice.FOUNDED_CUSTOMER.wait_elements_visible(0, timeout=10000)
            self.client_choice.FOUNDED_CUSTOMER.click(0)
            self.client_choice.INNER_ACCEPT_BTN[0].click()

        with allure.step("Проверка связанного лица"):
            self.create_request_form.CLIENT.click()
            self.client_profile.RELATED_PERSONS_TAB.click()
            self.client_profile.RELATED_PERSONS.wait_elements_visible(0, timeout=10000)
            self.client_profile.RELATED_PERSONS.to_contain_text(0, self.user.sur_name)
            self.client_profile.RELATED_MOBILE_PHONE.to_contain_text(self.user.contact_phone, clear_phone=True)
            self.client_profile.RELATED_EMAIL.to_contain_text(self.user.contact_email)

    @allure.title("Создание ФЛ клиента, заполняя только обязательные поля")
    @allure.description("Сценарий регистрация клиента B2C - ФЛ")
    @allure.id(484387)
    def test_individual_customer_create_only_required_fields(self, base_url: str) -> None:
        with allure.step('Пользователь нажимает на "Создать клиента ФЛ"'):
            self.home_page.CREATE_CUSTOMER_BTN.click()
            self.customer_create_form.LAST_NAME.wait_to_be_visible()
        with allure.step("В открывшейся форме пользователь вводит данные клиента"):
            self.customer_create_form.fill_data_for_individual_client(self.user, only_required_fields=True)
        with allure.step("Сохранить клиента"):
            allure.description("Форма заполнения данных закрывается, открывается форму клиентской карточки")
            self.customer_create_form.SAVE_BTN.click()
            self.customer_create_form.LAST_NAME.not_to_be_visible()

            self.client_profile.CLIENT_TAB.click()
            self.client_profile.CLIENT_FIO.to_contain_text(self.user.sur_name)
            self.client_profile.GENDER.to_contain_text(self.user.gender)
            self.client_profile.DOCUMENT_TYPE.to_contain_text(self.user.document_type)
            self.client_profile.DOCUMENT_SERIAL_AND_NUM.to_contain_text(self.user.document_num)
            self.client_profile.DOCUMENT_PROVIDE_BY.wait_to_have_text("")
            self.client_profile.DOCUMENT_DIVISION_CODE.wait_to_have_text("")
            self.client_profile.DOCUMENT_DATE.wait_to_have_text("")
            self.client_profile.DOCUMENT_VALID_DATE.wait_to_have_text("")
            self.client_profile.BIRTH_DATE.to_contain_text(self.user.birth_date)
            self.client_profile.BIRTH_PLACE.wait_to_have_text("")
            self.client_profile.INN.wait_to_have_text("")
            self.client_profile.SNILS.wait_to_have_text("")

            self.client_profile.RELATED_PERSONS_TAB.click()
            self.client_profile.EMPTY_RELATED_PERSONS.wait_to_be_visible()
            self.client_profile.EMPTY_RELATED_PERSONS.to_contain_text("Попробуйте уточнить запрос")

        with allure.step("Ищем клиента"):
            self.home_page.HOME_BTN.click()
            self.home_page.HEADER_SEARCH_BTN.click()

            self.client_search_page.FOUNDED_CLIENTS.not_to_be_visible()
            self.client_profile_page.search_client(customer_name=self.user.sur_name, customer_status="Действующий")
            self.client_search_page.FOUNDED_CLIENTS.wait_to_be_visible()

        with allure.step("Открываем форму продажи"):
            self.home_page.CREATE_APPLICATION.click()
            self.create_request_form.NEED_SPD.wait_to_be_visible(timeout=20000)
            self.create_request_form.SELECT_CLIENT_BTN.wait_to_be_enabled()
            self.create_request_form.SELECT_CLIENT_BTN.select_by_value("Выбрать клиента")

            full_name = f"{self.user.sur_name} {self.user.first_name} {self.user.patronymic}"
            self.client_choice.CUSTOMER_NAME.fill(full_name)
            self.client_choice.FIND_BTN.click()

            self.client_choice.FOUNDED_CUSTOMER.wait_elements_visible(0, timeout=10000)
            self.client_choice.FOUNDED_CUSTOMER.click(0)
            self.client_choice.INNER_ACCEPT_BTN[0].click()

            self.create_request_form.EMAIL.wait_to_have_text("")
            self.create_request_form.PHONE.wait_to_have_text("")

        with allure.step("Проверка связанного лица"):
            self.create_request_form.CLIENT.click()
            self.client_profile.RELATED_PERSONS_TAB.click()
            self.client_profile.EMPTY_RELATED_PERSONS.wait_to_be_visible()
            self.client_profile.EMPTY_RELATED_PERSONS.to_contain_text("Попробуйте уточнить запрос")

    @allure.suite("E2E_64 Создание и управление клиентом и его иерархиями")
    @allure.title("Создание клиента документ регистрации клиента просрочен")
    @allure.tag("CAN_AUTH", "SUCCESS")
    @allure.description(
        "Сценарий регистрация клиента B2C - ввод некорректных данных документа регистрации "
        "(дата окончания в прошлом) клиент не может быть создан"
    )
    @allure.id(484808)
    @pytest.mark.regress
    def test_individual_customer_create_document_out_of_date(self, base_url: str) -> None:
        with allure.step('Пользователь нажимает на "Создать клиента ФЛ"'):
            self.home_page.CREATE_CUSTOMER_BTN.click()
            self.customer_create_form.LAST_NAME.wait_to_be_visible()
        with allure.step("В открывшейся форме пользователь вводит данные клиента"):
            self.customer_create_form.fill_data_for_individual_client(self.user, only_required_fields=True)
            self.customer_create_form.DOCUMENT_VALID_DATE.fill(self.user.document_date)
        with allure.step("Сохранить клиента"):
            allure.description("Форма заполнения данных закрывается, открывается форму клиентской карточки")
            self.customer_create_form.SAVE_BTN.click()
            self.customer_create_form.MODAL.wait_to_have_count(1)
            self.customer_create_form.MODAL_TITLE[0].to_contain_text("Ошибка")
            self.customer_create_form.MODAL_BODY_TEXT[0].to_contain_text("Невозможно установить дату в прошлом")

    @allure.suite("E2E_64 Создание и управление клиентом и его иерархиями")
    @allure.title("Создание В2С ФЛ клиента заполняя все поля + продажа")
    @allure.tag("CAN_AUTH", "SUCCESS")
    @allure.description("Сценарий создания клиента ФЛ из процесса продажи (быстрое создание клиента)")
    @allure.id(479467)
    @pytest.mark.regress
    def test_create_individual_customer_from_process_sale(self, base_url: str) -> None:
        with allure.step("Пользователь нажал на кнопку создание продажи"):
            self.home_page.CREATE_APPLICATION.click()

        self.create_request_form.NEED_SPD.wait_to_be_visible(timeout=20000)
        self.create_request_form.SELECT_CLIENT_BTN.wait_to_be_enabled()
        self.create_request_form.SELECT_CLIENT_BTN.select_by_value("Создать ФЛ")

        with allure.step("В открывшейся форме пользователь вводит данные клиента"):
            self.customer_create_form.fill_data_for_individual_client(self.user)
        with allure.step("Сохранить клиента"):
            self.customer_create_form.SAVE_BTN.click()
            self.customer_create_form.CUSTOMER_NAME.not_to_be_visible()

            self.create_request_form.CLIENT.to_contain_text(self.user.first_name)

        with allure.step('Заполнить контактные данные нажать на кнопку "сохранить"'):
            self.create_request_form.EMAIL.fill(self.user.contact_email)
            self.create_request_form.PHONE.fill(self.user.contact_phone)
            self.create_request_form.PRIORITY.select_by_value("Высокий")
            self.create_request_form.ADD_SALE_TYPE.select_by_value("Сформировать, факт согласования автоматически")

            self.create_request_form.SAVE_BTN.click()

        self.inquiries_page.locators.CLIENT.click()
        client_id = self.personal_account_page.get_customer_id_from_url()
        client = generate_individual_client()
        client.user_id = client_id
        self.client_request_api.product_sale(client, prepare_inquiries("mobile"))

        with allure.step('Переходим на вкладку "Клиент" клиентской карточки'):
            self.client_profile.CLIENT_TAB.click()
            self.client_profile.CLIENT_FIO.to_contain_text(self.user.sur_name)
            self.client_profile.GENDER.to_contain_text(self.user.gender)
            self.client_profile.DOCUMENT_TYPE.to_contain_text(self.user.document_type)
            self.client_profile.DOCUMENT_SERIAL_AND_NUM.to_contain_text(self.user.document_serial)
            self.client_profile.DOCUMENT_SERIAL_AND_NUM.to_contain_text(self.user.document_num)
            self.client_profile.DOCUMENT_PROVIDE_BY.to_contain_text(self.user.document_provide_by)
            self.client_profile.DOCUMENT_DIVISION_CODE.to_contain_text(self.user.document_division_code)
            self.client_profile.DOCUMENT_DATE.to_contain_text(self.user.document_date)
            self.client_profile.DOCUMENT_VALID_DATE.to_contain_text(self.user.document_valid_date)
            self.client_profile.BIRTH_DATE.to_contain_text(self.user.birth_date)
            self.client_profile.BIRTH_PLACE.to_contain_text(self.user.birth_place)
            self.client_profile.INN.to_contain_text(self.user.inn)
            self.client_profile.SNILS.to_contain_text(self.user.snils)

            self.client_profile.RELATED_PERSONS_TAB.click()
            self.client_profile.RELATED_PERSONS.wait_elements_visible(0)
            self.client_profile.RELATED_PERSONS.to_contain_text(0, self.user.sur_name)
            self.client_profile.RELATED_MOBILE_PHONE.to_contain_text(self.user.contact_phone, clear_phone=True)
            self.client_profile.RELATED_EMAIL.to_contain_text(self.user.contact_email)

        with allure.step("Ищем клиента"):
            self.home_page.HOME_BTN.click()
            self.home_page.HEADER_SEARCH_BTN.click()

            self.client_search_page.FOUNDED_CLIENTS.not_to_be_visible()
            self.client_profile_page.search_client(inn=self.user.inn, customer_status="Действующий")
            self.client_search_page.FOUNDED_CLIENTS.wait_to_be_visible()

        with allure.step("Открываем форму продажи"):
            self.home_page.CREATE_APPLICATION.click()
            self.create_request_form.NEED_SPD.wait_to_be_visible(timeout=20000)
            self.create_request_form.SELECT_CLIENT_BTN.wait_to_be_enabled()
            self.create_request_form.SELECT_CLIENT_BTN.select_by_value("Выбрать клиента")

            self.client_choice.INN.fill(self.user.inn)
            self.client_choice.FIND_BTN.click()

            self.client_choice.FOUNDED_CUSTOMER.wait_elements_visible(0, timeout=10000)
            self.client_choice.FOUNDED_CUSTOMER.click(0)
            self.client_choice.FOUNDED_FIO[0].to_contain_text(self.user.sur_name)
            self.client_choice.INNER_ACCEPT_BTN[0].click()
