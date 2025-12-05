import re

import allure
import pytest

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from models.context import test_context
from models.inquiry import prepare_inquiries
from models.user import OrganizationClient
from pages.locators.nbss.client.client_profile import ClientProfile
from pages.locators.nbss.client.client_search import ClientSearch
from pages.locators.nbss.dynamic_form_elements import ClientChoice, CreateOrganization, CreateSalesAndServiceManagement
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
class TestOrganizationCustomerCreate:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_ui_stand_login, organization_user_data: OrganizationClient) -> None:
        self.home_page = HomePage()
        self.organization_create_form = CreateOrganization()
        self.client_search_page = ClientSearch()
        self.create_request_form = CreateSalesAndServiceManagement()
        self.client_choice = ClientChoice()
        self.client_profile = ClientProfile()
        self.client_profile_page = ClientProfilePage()
        self.inquiries_page = InquiriesPage()
        self.product_offer_form = SelectProductOffersForm()
        self.product_edit_form = ProductEditForm()
        self.user = organization_user_data
        self.client_request_api = ClientInquiriesRequests()
        self.personal_account_page = PersonalAccountPage()

    @allure.title("Создание ЮЛ клиента, заполнены все поля")
    @allure.description("Создание ЮЛ клиента, заполнены все поля")
    @allure.id(484785)
    def test_organization_create(self, base_url: str) -> None:
        with allure.step('Пользователь нажимает на "Создать клиента ЮЛ"'):
            self.home_page.CREATE_ORG_BTN.click()
            self.organization_create_form.INN.wait_to_be_visible()
        with allure.step("В открывшейся форме пользователь вводит данные клиента"):
            self.organization_create_form.fill_data_for_organization_client(self.user)
        with allure.step("Сохранить клиента"):
            self.organization_create_form.SAVE_BTN.click()
            self.organization_create_form.INN.not_to_be_visible(timeout=15000)

            self.client_profile.CLIENT_TAB.click()
            self.client_profile.CLIENT_TYPE.to_contain_text(self.user.type)
            self.client_profile.CLIENT_FIO.to_contain_text(self.user.customer_name)
            self.client_profile.RESIDENT.wait_to_have_text(self.user.is_resident)
            self.client_profile.SPEAKING_LANGUAGE.to_contain_text(self.user.speaking_language)
            self.client_profile.NATIONALITY.to_contain_text(self.user.nationality)
            self.client_profile.NOTE.to_contain_text(self.user.note)
            self.client_profile.REGISTRATION_DOCUMENT.to_contain_text(self.user.registration_document)
            self.client_profile.REGISTRATION_DATE.to_contain_text(self.user.registration_date)
            self.client_profile.REGISTRATION_NUM.to_contain_text(self.user.registration_num)
            self.client_profile.TAX_SCHEME.to_contain_text(self.user.tax_scheme)

        with allure.step("Ищем клиента"):
            self.home_page.HOME_BTN.click()
            self.home_page.HEADER_SEARCH_BTN.click()

            self.client_search_page.FOUNDED_CLIENTS.not_to_be_visible()
            self.client_profile_page.search_client(
                customer_name=self.user.customer_name,
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
            self.create_request_form.CLIENT.click()
            self.client_profile.RELATED_PERSONS_TAB.click()
            self.client_profile.RELATED_PERSONS.not_to_be_visible()

    @allure.title("Создание B2B с типом ЮЛ заполняя все поля")
    @allure.description(
        "Проверить, что из процесса продажи (быстрое создание клиента) корректно создается B2B клиент с типом ЮЛ, "
        "при этом все поля заполнены"
    )
    @allure.id(533614)
    @pytest.mark.smoke
    def test_b2b_organization_create(self, base_url: str) -> None:
        with allure.step("Пользователь нажал на кнопку создание продажи"):
            self.home_page.CREATE_APPLICATION.click()

        self.create_request_form.SELECT_CLIENT_BTN.wait_to_be_visible(timeout=20000)
        self.create_request_form.SELECT_CLIENT_BTN.wait_to_be_enabled(timeout=30000)
        self.create_request_form.SELECT_CLIENT_BTN.select_by_value("Создать ЮЛ")

        with allure.step("В открывшейся форме пользователь вводит данные клиента"):
            self.organization_create_form.fill_data_for_organization_client(self.user)
        with allure.step("Сохранить клиента"):
            self.organization_create_form.SAVE_BTN.click()

            self.create_request_form.CLIENT.to_contain_text(self.user.customer_name)

        with allure.step('Заполнить контактные данные нажать на кнопку "сохранить"'):
            self.create_request_form.EMAIL.fill(self.user.contact_email)
            self.create_request_form.PHONE.fill(self.user.contact_phone)
            self.create_request_form.ADD_SALE_TYPE.select_by_value("Сформировать, факт согласования автоматически")
            self.create_request_form.PRIORITY.select_by_value("Низкий")

            self.create_request_form.SAVE_BTN.click()

            self.inquiries_page.locators.CLIENT.to_contain_text(self.user.customer_name)
            self.inquiries_page.locators.INQUIRY_NAME.wait_to_have_text(
                re.compile(r"\d\. Продажа и управление услугами"), timeout=30000
            )
            self.inquiries_page.locators.INQUIRY_STATUS.wait_to_have_text("Обрабатывается")

    @allure.title("Создание ЮЛ клиента заполняя все поля + продажа")
    @allure.id(485729)
    @allure.description("Сценарий создания клиента ЮЛ из процесса продажи (быстрое создание клиента)")
    def test_create_organization_customer_from_process_sale(self, base_url: str) -> None:
        with allure.step("Пользователь нажал на кнопку создание продажи"):
            self.home_page.CREATE_APPLICATION.click()

        self.create_request_form.SELECT_CLIENT_BTN.wait_to_be_visible(timeout=20000)
        self.create_request_form.SELECT_CLIENT_BTN.wait_to_be_enabled(timeout=30000)
        self.create_request_form.SELECT_CLIENT_BTN.select_by_value("Создать ЮЛ")

        with allure.step("В открывшейся форме пользователь вводит данные клиента"):
            self.organization_create_form.fill_data_for_organization_client(self.user)
        with allure.step("Сохранить клиента"):
            self.organization_create_form.SAVE_BTN.click()
            self.organization_create_form.INN.not_to_be_visible(timeout=15000)

            self.create_request_form.CLIENT.to_contain_text(self.user.customer_name)

        with allure.step('Заполнить контактные данные нажать на кнопку "сохранить"'):
            self.create_request_form.EMAIL.fill(self.user.contact_email)
            self.create_request_form.PHONE.fill(self.user.contact_phone)
            self.create_request_form.PRIORITY.select_by_value("Высокий")
            self.create_request_form.ADD_SALE_TYPE.select_by_value("Сформировать, факт согласования автоматически")

            self.create_request_form.SAVE_BTN.click()

            self.inquiries_page.locators.CLIENT.click()
            client = OrganizationClient()
            client.user_id = self.personal_account_page.get_customer_id_from_url()

        self.client_request_api.product_sale(client, prepare_inquiries("internet"))

        with allure.step('Переходим на вкладку "Клиент" клиентской карточки'):
            self.inquiries_page.open(
                f"{base_url}customer-hierarchy-management/customers/{test_context.client.user_id}/overview"
            )

            self.client_profile.CLIENT_TAB.click()
            self.client_profile.CLIENT_TYPE.to_contain_text(self.user.type)
            self.client_profile.CLIENT_FIO.to_contain_text(self.user.customer_name)
            self.client_profile.RESIDENT.to_contain_text(self.user.is_resident)
            self.client_profile.SPEAKING_LANGUAGE.to_contain_text(self.user.speaking_language)
            self.client_profile.NATIONALITY.to_contain_text(self.user.nationality)
            self.client_profile.NOTE.to_contain_text(self.user.note)
            self.client_profile.REGISTRATION_DOCUMENT.to_contain_text(self.user.registration_document)
            self.client_profile.REGISTRATION_DATE.to_contain_text(self.user.registration_date)
            self.client_profile.REGISTRATION_NUM.to_contain_text(self.user.registration_num)
            self.client_profile.TAX_SCHEME.to_contain_text(self.user.tax_scheme)

        with allure.step("Ищем клиента"):
            self.home_page.HOME_BTN.click()
            self.home_page.HEADER_SEARCH_BTN.click()

            self.client_search_page.FOUNDED_CLIENTS.not_to_be_visible()
            self.client_profile_page.search_client(
                customer_name=self.user.customer_name,
                account_status="Действующий",
                contract_status="Действующий",
                customer_status="Действующий",
            )
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
