import re

import allure
import pytest

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from models.client import OrganizationClient
from models.context import test_context
from models.inquiry import prepare_inquiries
from pages.locators.nbss.client.client_profile import ClientProfileElements
from pages.locators.nbss.client.client_search import ClientSearchElements
from pages.locators.nbss.dynamic_form_elements import ClientChoice, CreateOrganization, CreateSalesAndServiceManagement
from pages.locators.nbss.inquiries_elements import ProductEditForm
from pages.locators.nbss.select_product_offers_form import SelectProductOffersFormElements
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.home_page import HomePage
from pages.nbss.inquiries_page import InquiriesPage
from pages.nbss.personal_account_page import PersonalAccountPage


@allure.suite("E2E_64 Создание и управление клиентом и его иерархиями")
@pytest.mark.regress
@pytest.mark.usefixtures("nexign_stand_login")
@pytest.mark.nbss_portal
@pytest.mark.praim
class TestOrganizationCustomerCreate:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login) -> None:
        self.home_page = HomePage()
        self.organization_create_form = CreateOrganization()
        self.client_search_page = ClientSearchElements()
        self.create_request_form = CreateSalesAndServiceManagement()
        self.client_choice = ClientChoice()
        self.client_profile = ClientProfileElements()
        self.client_profile_page = ClientProfilePage()
        self.inquiries_page = InquiriesPage()
        self.product_offer_form = SelectProductOffersFormElements()
        self.product_edit_form = ProductEditForm()
        self.client_request_api = ClientInquiriesRequests()
        self.personal_account_page = PersonalAccountPage()

    @allure.title("Создание ЮЛ клиента, заполнены все поля")
    @allure.description("Создание ЮЛ клиента, заполнены все поля")
    @allure.id(484785)
    @pytest.mark.sanity
    def test_organization_create(self, base_url: str) -> None:
        self.home_page.create_customer_with_type("organization")
        client = test_context.client

        with allure.step("Проверка данных"):
            self.client_profile.CLIENT_TAB.wait_to_be_visible()
            self.client_profile.CLIENT_TAB.click()
            self.client_profile.CLIENT_TYPE.to_contain_text(client.type)
            self.client_profile.CLIENT_FIO.to_contain_text(client.customer_name)
            self.client_profile.RESIDENT.wait_to_have_text(client.is_resident)
            self.client_profile.SPEAKING_LANGUAGE.to_contain_text(client.speaking_language)
            self.client_profile.NATIONALITY.to_contain_text(client.nationality)
            self.client_profile.NOTE.to_contain_text(client.note)
            self.client_profile.REGISTRATION_DOCUMENT.to_contain_text(client.registration_document)
            self.client_profile.REGISTRATION_DATE.to_contain_text(client.registration_date)
            self.client_profile.REGISTRATION_NUM.to_contain_text(client.registration_num)
            self.client_profile.TAX_SCHEME.to_contain_text(client.tax_scheme)

        with allure.step("Ищем клиента"):
            self.home_page.locators.HOME_BTN.click()
            self.home_page.locators.HEADER_SEARCH_BTN.click()

            self.client_search_page.FOUNDED_CLIENTS.not_to_be_visible()
            self.home_page.search_client(
                customer_name=test_context.client.customer_name,
                customer_status="Действующий",
            )
            self.client_search_page.FOUNDED_CLIENTS.wait_to_be_visible()

        with allure.step("Открываем форму продажи"):
            self.home_page.locators.CREATE_APPLICATION.click()
            self.create_request_form.SELECT_CLIENT_BTN.wait_to_be_visible(timeout=20000)
            self.create_request_form.SELECT_CLIENT_BTN.wait_to_be_enabled(timeout=30000)
            self.create_request_form.SELECT_CLIENT_BTN.select_by_value("Выбрать клиента")

            self.client_choice.INN.fill(test_context.client.inn)
            self.client_choice.FIND_BTN.click()

            self.client_choice.FOUNDED_CUSTOMER.wait_elements_visible(0, timeout=10000)
            self.client_choice.FOUNDED_CUSTOMER.click(0)
            self.client_choice.INNER_ACCEPT_BTN[0].click()

        with allure.step("Проверка связанного лица"):
            self.create_request_form.CLIENT.wait_to_be_visible(timeout=30000)
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
    @pytest.mark.sanity
    def test_b2b_organization_create(self, base_url: str) -> None:
        with allure.step("Пользователь нажал на кнопку создание продажи"):
            self.home_page.locators.CREATE_APPLICATION.click()

        self.create_request_form.SELECT_CLIENT_BTN.wait_to_be_visible(timeout=20000)
        self.create_request_form.SELECT_CLIENT_BTN.wait_to_be_enabled(timeout=30000)
        self.create_request_form.SELECT_CLIENT_BTN.select_by_value("Создать ЮЛ")

        with allure.step("В открывшейся форме пользователь вводит данные клиента"):
            self.home_page.create_customer_with_type("organization", with_initialization=False)
            client = test_context.client
            self.create_request_form.CLIENT.wait_to_be_visible(timeout=30000)
            self.create_request_form.CLIENT.wait_to_have_text(client.customer_name, timeout=15000)

        with allure.step('Заполнить контактные данные нажать на кнопку "сохранить"'):
            self.create_request_form.EMAIL.fill(client.contact_email)
            self.create_request_form.PHONE.fill(client.contact_phone)
            self.create_request_form.ADD_SALE_TYPE.select_by_value("Сформировать, факт согласования автоматически")
            self.create_request_form.PRIORITY.select_by_value("Низкий")

            self.create_request_form.SAVE_BTN.click()

            self.inquiries_page.locators.CLIENT.to_contain_text(client.customer_name, timeout_sec=15)
            self.inquiries_page.locators.INQUIRY_NAME.wait_to_have_text(
                re.compile(r"\d\. Продажа и управление услугами"), timeout=30000
            )
            self.inquiries_page.locators.INQUIRY_STATUS.wait_to_have_text("Обрабатывается")

    @allure.title("Создание ЮЛ клиента заполняя все поля + продажа")
    @allure.id(485729)
    @allure.description("Сценарий создания клиента ЮЛ из процесса продажи (быстрое создание клиента)")
    @pytest.mark.sanity
    def test_create_organization_customer_from_process_sale(self, base_url: str) -> None:
        with allure.step("Пользователь нажал на кнопку создание продажи"):
            self.home_page.locators.CREATE_APPLICATION.click()

        self.create_request_form.SELECT_CLIENT_BTN.wait_to_be_visible(timeout=20000)
        self.create_request_form.SELECT_CLIENT_BTN.wait_to_be_enabled(timeout=30000)
        self.create_request_form.SELECT_CLIENT_BTN.select_by_value("Создать ЮЛ")

        with allure.step("В открывшейся форме пользователь вводит данные клиента"):
            self.home_page.create_customer_with_type("organization", with_initialization=False)
            client = test_context.client

            self.create_request_form.CLIENT.wait_to_be_visible(timeout=30000)
            self.create_request_form.CLIENT.to_contain_text(client.customer_name, timeout_sec=15)

        with allure.step('Заполнить контактные данные нажать на кнопку "сохранить"'):
            self.create_request_form.EMAIL.fill(client.contact_email)
            self.create_request_form.PHONE.fill(client.contact_phone)
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
            self.client_profile.CLIENT_TYPE.to_contain_text(client.type)
            self.client_profile.CLIENT_FIO.to_contain_text(client.customer_name)
            self.client_profile.RESIDENT.to_contain_text(client.is_resident, timeout_sec=20)
            self.client_profile.SPEAKING_LANGUAGE.to_contain_text(client.speaking_language)
            self.client_profile.NATIONALITY.to_contain_text(client.nationality)
            self.client_profile.NOTE.to_contain_text(client.note)
            self.client_profile.REGISTRATION_DOCUMENT.to_contain_text(client.registration_document)
            self.client_profile.REGISTRATION_DATE.to_contain_text(client.registration_date)
            self.client_profile.REGISTRATION_NUM.to_contain_text(client.registration_num)
            self.client_profile.TAX_SCHEME.to_contain_text(client.tax_scheme)

        with allure.step("Ищем клиента"):
            self.home_page.locators.HOME_BTN.click()
            self.home_page.locators.HEADER_SEARCH_BTN.click()

            self.client_search_page.FOUNDED_CLIENTS.not_to_be_visible()
            self.home_page.search_client(
                customer_name=client.customer_name,
                account_status="Действующий",
                contract_status="Действующий",
                customer_status="Действующий",
            )
            self.client_search_page.FOUNDED_CLIENTS.wait_to_be_visible()

        with allure.step("Открываем форму продажи"):
            self.home_page.locators.CREATE_APPLICATION.click()
            self.create_request_form.NEED_SPD.wait_to_be_visible(timeout=20000)
            self.create_request_form.SELECT_CLIENT_BTN.wait_to_be_enabled()
            self.create_request_form.SELECT_CLIENT_BTN.select_by_value("Выбрать клиента")

            self.client_choice.INN.fill(client.inn)
            self.client_choice.FIND_BTN.click()

            self.client_choice.FOUNDED_CUSTOMER.wait_elements_visible(0, timeout=10000)
            self.client_choice.FOUNDED_CUSTOMER.click(0)
            self.client_choice.INNER_ACCEPT_BTN[0].click()
