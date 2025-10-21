import re

import allure
import pytest
from playwright.sync_api import APIRequestContext, Page

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from common.helpers.time_helpers import delay
from models.user import OrganizationClient
from pages.locators.nbss.client.client_profile import ClientProfile
from pages.locators.nbss.client.client_search import ClientSearch
from pages.locators.nbss.dynamic_form_elements import ClientChoice, CreateOrganization, CreateSalesAndServiceManagement
from pages.locators.nbss.home_page_elements import HomePage
from pages.locators.nbss.inquiries_elements import ProductEditForm
from pages.locators.nbss.select_product_offers_form import SelectProductOffersForm
from pages.nbss.inquiries_page import InquiriesPage
from pages.nbss.personal_account_page import PersonalAccountPage


@allure.suite("E2E_64 Создание и управление клиентом и его иерархиями")
@pytest.mark.regress
@pytest.mark.usefixtures("nexign_ui_stand_login")
@pytest.mark.nbss_portal
@pytest.mark.praim
class TestOrganizationCustomerCreate:
    @pytest.fixture(autouse=True)
    def setup(
        self, page: Page, organization_user_data: OrganizationClient, api_request_context: APIRequestContext
    ) -> None:
        self.home_page = HomePage(page)
        self.organization_create_form = CreateOrganization(page)
        self.client_search_page = ClientSearch(page)
        self.create_request_form = CreateSalesAndServiceManagement(page)
        self.client_choice = ClientChoice(page)
        self.client_profile = ClientProfile(page)
        self.inquiries_page = InquiriesPage(page)
        self.product_offer_form = SelectProductOffersForm(page)
        self.product_edit_form = ProductEditForm(page)
        self.user = organization_user_data
        self.client_request_api = ClientInquiriesRequests(api_request_context)
        self.personal_account_page = PersonalAccountPage(page)

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
            self.organization_create_form.INN.not_to_be_visible()

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
            self.home_page.CUSTOMER_NAME.fill(self.user.customer_name)
            self.home_page.HEADER_SEARCH_BTN.click()

            self.client_search_page.FOUNDED_CLIENTS.not_to_be_visible()
            self.client_search_page.ACCOUNT_STATUSES.select_by_value("Действующий", check=False)
            self.client_search_page.CONTRACT_STATUS.select_by_value("Оформлен", check=False)
            delay(2, "Не успевает примениться фильтр")
            self.client_search_page.SEARCH_BTN.click()
            self.client_search_page.FOUNDED_CLIENTS.wait_to_be_visible()

        with allure.step("Открываем форму продажи"):
            self.home_page.CREATE_APPLICATION.click()
            self.create_request_form.SELECT_CLIENT_BTN.select_by_value("Выбрать клиента")

            self.client_choice.INN.fill(self.user.inn)
            self.client_choice.FIND_BTN.click()

            self.client_choice.FOUNDED_CUSTOMER.wait_elements_visible(0, timeout=10000)
            self.client_choice.FOUNDED_CUSTOMER.click(0)
            self.client_choice.INNER_ACCEPT_BTN.click()

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
                re.compile(r"\d\. Продажа и управление услугами")
            )
            self.inquiries_page.locators.INQUIRY_STATUS.wait_to_have_text("Обрабатывается")

    @allure.title("Создание ЮЛ клиента заполняя все поля + продажа")
    @allure.id(485729)
    @allure.description("Сценарий создания клиента ЮЛ из процесса продажи (быстрое создание клиента)")
    def test_create_organization_customer_from_process_sale(self, base_url: str) -> None:
        with allure.step("Пользователь нажал на кнопку создание продажи"):
            self.home_page.CREATE_APPLICATION.click()

        self.create_request_form.SELECT_CLIENT_BTN.select_by_value("Создать ЮЛ")

        with allure.step("В открывшейся форме пользователь вводит данные клиента"):
            self.organization_create_form.fill_data_for_organization_client(self.user)
        with allure.step("Сохранить клиента"):
            self.organization_create_form.SAVE_BTN.click()
            self.organization_create_form.INN.not_to_be_visible()

            self.create_request_form.CLIENT.to_contain_text(self.user.customer_name)

        with allure.step('Заполнить контактные данные нажать на кнопку "сохранить"'):
            self.create_request_form.EMAIL.fill(self.user.contact_email)
            self.create_request_form.PHONE.fill(self.user.contact_phone)
            self.create_request_form.PRIORITY.select_by_value("Высокий")
            self.create_request_form.ADD_SALE_TYPE.select_by_value("Сформировать, факт согласования автоматически")

            self.create_request_form.SAVE_BTN.click()

            self.inquiries_page.locators.CLIENT.click()
            client_id = self.personal_account_page.get_customer_id_from_url()

        self.client_request_api.product_sale(client_id, category="internet", product_offering_id=500001)

        with allure.step('Переходим на вкладку "Клиент" клиентской карточки'):
            self.inquiries_page.open(f"{base_url}customer-hierarchy-management/customers/{client_id}/overview")

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
            self.home_page.CUSTOMER_NAME.fill(self.user.customer_name)
            self.home_page.HEADER_SEARCH_BTN.click()

            self.client_search_page.FOUNDED_CLIENTS.not_to_be_visible()
            self.client_search_page.ACCOUNT_STATUSES.select_by_value("Действующий", check=False)
            self.client_search_page.CONTRACT_STATUS.select_by_value("Оформлен", check=False)
            delay(2, "Не успевает примениться фильтр")
            self.client_search_page.SEARCH_BTN.click()
            self.client_search_page.FOUNDED_CLIENTS.wait_to_be_visible()

        with allure.step("Открываем форму продажи"):
            self.home_page.CREATE_APPLICATION.click()
            self.create_request_form.SELECT_CLIENT_BTN.select_by_value("Выбрать клиента")

            self.client_choice.INN.fill(self.user.inn)
            self.client_choice.FIND_BTN.click()

            self.client_choice.FOUNDED_CUSTOMER.wait_elements_visible(0, timeout=10000)
            self.client_choice.FOUNDED_CUSTOMER.click(0)
            self.client_choice.INNER_ACCEPT_BTN.click()
