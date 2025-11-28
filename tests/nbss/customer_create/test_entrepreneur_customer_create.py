import allure
import pytest
from playwright.sync_api import APIRequestContext, Page

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from models.inquiry import prepare_inquiries
from models.user import EntrepreneurClient, generate_entrepreneur_client
from pages.locators.nbss.client.client_profile import ClientProfile
from pages.locators.nbss.client.client_search import ClientSearch
from pages.locators.nbss.dynamic_form_elements import ClientChoice, CreateEntrepreneur, CreateSalesAndServiceManagement
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
class TestEntrepreneurCustomerCreate:
    @pytest.fixture(autouse=True)
    def setup(
        self, page: Page, entrepreneur_user_data: EntrepreneurClient, api_request_context: APIRequestContext
    ) -> None:
        self.home_page = HomePage(page)
        self.entrepreneur_create_form = CreateEntrepreneur(page)
        self.client_search_page = ClientSearch(page)
        self.create_request_form = CreateSalesAndServiceManagement(page)
        self.client_choice = ClientChoice(page)
        self.client_profile = ClientProfile(page)
        self.client_profile_page = ClientProfilePage(page)
        self.inquiries_page = InquiriesPage(page)
        self.product_offer_form = SelectProductOffersForm(page)
        self.product_edit_form = ProductEditForm(page)
        self.user = entrepreneur_user_data
        self.client_request_api = ClientInquiriesRequests(api_request_context)
        self.personal_account_page = PersonalAccountPage(page)

    @allure.title("Создание ИП клиента, заполнены все поля")
    @allure.description("Сценарий регистрация клиента B2B - ИП")
    @allure.id(484786)
    def test_entrepreneur_customer_create(self, base_url: str) -> None:
        with allure.step('Пользователь нажимает на "Создать клиента ИП"'):
            self.home_page.CREATE_ENTREPRENEUR_BTN.click(timeout=30000)
            self.entrepreneur_create_form.INN.wait_to_be_visible(timeout=30000)
        with allure.step("В открывшейся форме пользователь вводит данные клиента"):
            self.entrepreneur_create_form.fill_data_for_entrepreneur_client(self.user)
        with allure.step("Сохранить клиента"):
            allure.description("Форма заполнения данных закрывается, открывается форму клиентской карточки")
            self.entrepreneur_create_form.SAVE_BTN.click()
            self.entrepreneur_create_form.INFO_MESSAGE.wait_to_be_visible(timeout=15000)
            self.entrepreneur_create_form.INFO_MESSAGE.wait_to_have_text("Клиент создан")
            self.entrepreneur_create_form.LAST_NAME.not_to_be_visible(timeout=15000)

            self.client_profile.CLIENT_TAB.click()
            self.client_profile.CLIENT_TYPE.to_contain_text(self.user.type)
            self.client_profile.CLIENT_FIO.to_contain_text(self.user.sur_name)

            self.client_profile.PUBLIC_PERSON.wait_to_have_text(self.user.is_public)
            self.client_profile.RESIDENT.to_contain_text(self.user.is_resident)
            self.client_profile.SPEAKING_LANGUAGE.to_contain_text(self.user.speaking_language)
            self.client_profile.NATIONALITY.to_contain_text(self.user.nationality)
            self.client_profile.BUSINESS_ACTIVITY.to_contain_text(self.user.business_activity)
            self.client_profile.NOTE.to_contain_text(self.user.note)
            self.client_profile.REPUTATION.to_contain_text(self.user.reputation)

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
            self.client_profile.TAX_SCHEME.to_contain_text(self.user.tax_scheme)

            self.client_profile.RELATED_PERSONS_TAB.click()
            self.client_profile.RELATED_PERSONS.wait_elements_visible(0)
            self.client_profile.RELATED_PERSONS.to_contain_text(0, self.user.sur_name)
            self.client_profile.RELATED_MOBILE_PHONE.to_contain_text(self.user.contact_phone, clear_phone=True)
            self.client_profile.RELATED_EMAIL.to_contain_text(self.user.contact_email)

        with allure.step("Ищем клиента"):
            self.home_page.HOME_BTN.click()
            self.home_page.HEADER_SEARCH_BTN.click()

            self.client_search_page.FOUNDED_CLIENTS.not_to_be_visible()
            self.client_profile_page.search_client(
                inn=self.user.inn,
                customer_status="Действующий",
            )
            self.client_search_page.FOUNDED_CLIENTS.wait_to_be_visible()

        with allure.step("Открываем форму продажи"):
            self.home_page.CREATE_APPLICATION.click()
            self.create_request_form.SELECT_CLIENT_BTN.wait_to_be_visible(timeout=20000)
            self.create_request_form.SELECT_CLIENT_BTN.wait_to_be_enabled(timeout=30000)
            self.create_request_form.SELECT_CLIENT_BTN.select_by_value("Выбрать клиента")

            self.client_choice.INN.fill(self.user.inn)
            self.client_choice.FIND_BTN.click()

            self.client_choice.FOUNDED_CUSTOMER.wait_elements_visible(0, timeout=10000)
            self.client_choice.FOUNDED_CUSTOMER.click(0)
            self.client_choice.INNER_ACCEPT_BTN[0].click()

        with allure.step("Проверка связанного лица"):
            self.create_request_form.CLIENT.click(timeout=30000, no_wait_after=True)
            self.client_profile.RELATED_PERSONS_TAB.wait_to_be_visible(timeout=20000)
            self.client_profile.RELATED_PERSONS_TAB.click()
            self.client_profile.RELATED_PERSONS.wait_elements_visible(0)
            self.client_profile.RELATED_PERSONS.to_contain_text(0, self.user.sur_name)
            self.client_profile.RELATED_MOBILE_PHONE.to_contain_text(self.user.contact_phone, clear_phone=True)
            self.client_profile.RELATED_EMAIL.to_contain_text(self.user.contact_email)

    @allure.title("Создание ИП клиента заполняя все поля + продажа")
    @allure.description("Сценарий создания клиента ИП из процесса продажи (быстрое создание клиента)")
    @allure.id(485717)
    def test_entrepreneur_customer_create_with_sale(self, base_url: str) -> None:
        with allure.step("Пользователь нажал на кнопку создание продажи"):
            self.home_page.CREATE_APPLICATION.click()

        self.create_request_form.SELECT_CLIENT_BTN.wait_to_be_enabled()
        self.create_request_form.SELECT_CLIENT_BTN.select_by_value("Создать ИП")

        with allure.step("В открывшейся форме пользователь вводит данные клиента"):
            self.entrepreneur_create_form.fill_data_for_entrepreneur_client(self.user)
        with allure.step("Сохранить клиента"):
            self.entrepreneur_create_form.SAVE_BTN.click()
            self.create_request_form.CLIENT.to_contain_text(self.user.sur_name)

        with allure.step('Заполнить контактные данные нажать на кнопку "сохранить"'):
            self.create_request_form.EMAIL.fill(self.user.contact_email)
            self.create_request_form.PHONE.fill(self.user.contact_phone)
            self.create_request_form.PRIORITY.select_by_value("Высокий")
            self.create_request_form.ADD_SALE_TYPE.select_by_value("Сформировать, факт согласования автоматически")

            self.create_request_form.SAVE_BTN.click()

        self.inquiries_page.locators.CLIENT.click()
        client_id = self.personal_account_page.get_customer_id_from_url()
        client = generate_entrepreneur_client()
        client.user_id = client_id
        self.client_request_api.product_sale(client, prepare_inquiries("internet"))

        with allure.step('Переходим на вкладку "Клиент" клиентской карточки'):
            self.client_profile.CLIENT_TAB.click()
            self.client_profile.CLIENT_TYPE.to_contain_text(self.user.type)
            self.client_profile.CLIENT_FIO.to_contain_text(self.user.sur_name)

            self.client_profile.PUBLIC_PERSON.to_contain_text(self.user.is_public)
            self.client_profile.RESIDENT.to_contain_text(self.user.is_resident)
            self.client_profile.SPEAKING_LANGUAGE.to_contain_text(self.user.speaking_language)
            self.client_profile.NATIONALITY.to_contain_text(self.user.nationality)
            self.client_profile.BUSINESS_ACTIVITY.to_contain_text(self.user.business_activity)
            self.client_profile.NOTE.to_contain_text(self.user.note)
            self.client_profile.REPUTATION.to_contain_text(self.user.reputation)

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
            self.client_profile.TAX_SCHEME.to_contain_text(self.user.tax_scheme)

            self.client_profile.RELATED_PERSONS_TAB.click()
            self.client_profile.RELATED_PERSONS.wait_elements_visible(0)
            self.client_profile.RELATED_PERSONS.to_contain_text(0, self.user.sur_name)
            self.client_profile.RELATED_MOBILE_PHONE.to_contain_text(self.user.contact_phone, clear_phone=True)
            self.client_profile.RELATED_EMAIL.to_contain_text(self.user.contact_email)

        with allure.step("Ищем клиента"):
            self.home_page.HOME_BTN.click()
            self.home_page.HEADER_SEARCH_BTN.click()

            self.client_search_page.FOUNDED_CLIENTS.not_to_be_visible()
            self.client_profile_page.search_client(
                inn=self.user.inn,
                account_status="Действующий",
                customer_status="Действующий",
                contract_status="Действующий",
            )
            self.client_search_page.FOUNDED_CLIENTS.wait_to_be_visible()

        with allure.step("Открываем форму продажи"):
            self.home_page.CREATE_APPLICATION.click()
            self.create_request_form.SELECT_CLIENT_BTN.wait_to_be_enabled()
            self.create_request_form.SELECT_CLIENT_BTN.select_by_value("Выбрать клиента")

            self.client_choice.INN.fill(self.user.inn)
            self.client_choice.FIND_BTN.click()

            self.client_choice.FOUNDED_CUSTOMER.wait_elements_visible(0, timeout=10000)
            self.client_choice.FOUNDED_CUSTOMER.click(0)
            self.client_choice.FOUNDED_FIO[0].to_contain_text(self.user.sur_name)
            self.client_choice.INNER_ACCEPT_BTN[0].click()
