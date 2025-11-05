import re

import allure
import pytest
from playwright.sync_api import APIRequestContext, Page

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from api.nbss.client_requests.client_requests import ClientRequests
from common.helpers.data_generator import generate_random_number, generate_russian_string
from models.user import EntrepreneurClient, IndividualClient, OrganizationClient
from pages.locators.nbss.client.client_search import ClientSearch
from pages.locators.nbss.home_page_elements import HomePage
from pages.nbss.client.client_profile_page import ClientProfilePage


@pytest.mark.regress
@pytest.mark.nbss_portal
@allure.epic("E2E_34 Поиск клиента/абонента")
@allure.suite("E2E_34 Поиск клиента/абонента")
@allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=674672853", name="Поиск клиента/абонента")
class TestSearchMainPageAccountNumber:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_ui_stand_login: Page) -> None:
        self.home_page = HomePage(nexign_ui_stand_login)
        self.client_search = ClientSearch(nexign_ui_stand_login)

    @allure.title("Валидация поля 'Лицевой счет' — корректное заполнение")
    @allure.id(514723)
    @allure.description(
        "Проверить, что поиск по полю 'Лицевой счет' выполняется корректно, когда введен полный номер ЛС не превышающий 128 символов"
    )
    def test_account_number_field_validation_positive(self, create_user_with_agreement_and_account) -> None:
        account = create_user_with_agreement_and_account
        self.home_page.HEADER_SEARCH_BTN.wait_to_be_visible()
        self.home_page.HEADER_ACCOUNT_NUM.fill(account.agreements[0].accounts[0].number)
        self.home_page.HEADER_SEARCH_BTN.click()
        self.client_search.FOUNDED_FIO.wait_to_have_count(1)
        self.client_search.FOUNDED_ACCOUNT_NUM[0].wait_to_have_text(str(account.agreements[0].accounts[0].number))

    @allure.title("Валидация поля 'Лицевой счет'— некорректное заполнение поля")
    @allure.id(516072)
    @allure.description("Проверить, что при вводе некорректного значения происходит переход на страницу 'Поиск'")
    def test_account_number_field_validation_wrong_num(self) -> None:
        wrong_account_number = f"{generate_random_number(15)}%$&"
        self.home_page.HEADER_SEARCH_BTN.wait_to_be_visible()
        self.home_page.HEADER_ACCOUNT_NUM.fill(wrong_account_number)
        self.home_page.HEADER_SEARCH_BTN.click()
        self.client_search.TITLE.wait_to_have_text("Поиск клиента")
        self.client_search.FOUNDED_FIO.wait_not_to_be_visible()
        self.client_search.ACCOUNT_NUM.to_have_value(wrong_account_number)


@pytest.mark.regress
@allure.epic("E2E_34 Поиск клиента/абонента")
@allure.suite("E2E_34 Поиск клиента/абонента")
@allure.tag("can_auth", "success")
@allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=674672853", name="Поиск клиента/абонента")
class TestSearchMainPageClient:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_ui_stand_login: Page, api_request_context: APIRequestContext) -> None:
        self.home_page = HomePage(nexign_ui_stand_login)
        self.client_search = ClientSearch(nexign_ui_stand_login)
        self.client_request_api = ClientRequests(api_request_context)

    @allure.title("Валидация поля 'Клиент' — корректное заполнение")
    @allure.id(517381)
    @allure.description(
        "Проверить, что поиск выполняется корректно, когда введено более 3 символов и менее 240 символов"
    )
    def test_client_field_validation_positive(self) -> None:
        clients = self.client_request_api.search_client(
            account_status_ids=[2], agreement_status_ids=[2], customer_status_ids=[2], customer_name="Авто"
        ).json()["items"]
        first_client_type = clients[0]["customerProprietaryFormShortName"]
        client_type = "" if first_client_type is None else first_client_type
        self.home_page.HEADER_SEARCH_BTN.wait_to_be_visible()
        self.home_page.CUSTOMER_NAME.fill(clients[0]["customerName"])
        self.home_page.HEADER_SEARCH_BTN.click()
        self.client_search.FOUNDED_FIO.wait_to_have_count(1)
        self.client_search.FOUNDED_FIO[0].wait_to_have_text(f"{client_type} {clients[0]['customerName']}")

    @allure.title("Валидация поля 'Клиент'— некорректное заполнение поля")
    @allure.id(517386)
    @allure.description("Проверить, что при вводе некорректного значения происходит переход на страницу 'Поиск'")
    def test_client_field_validation_wrong_num(self) -> None:
        wrong_customer_name = f"{generate_russian_string(15)}%$&"
        self.home_page.HEADER_SEARCH_BTN.wait_to_be_visible()
        self.home_page.CUSTOMER_NAME.fill(wrong_customer_name)
        self.home_page.HEADER_SEARCH_BTN.click()
        self.client_search.TITLE.wait_to_have_text("Поиск клиента")
        self.client_search.FOUNDED_FIO.wait_not_to_be_visible()
        self.client_search.CUSTOMER_NAME_INPUT.to_have_value(wrong_customer_name)

    @allure.title("Валидация поля 'Клиент' — поиск по подстроке")
    @allure.id(517428)
    @allure.description("Проверить, что поиск работает по вхождению подстроки в имени клиента.")
    def test_client_field_validation_part_of_name(self) -> None:
        self.home_page.HEADER_SEARCH_BTN.wait_to_be_visible()
        self.home_page.CUSTOMER_NAME.fill("авто")
        self.home_page.HEADER_SEARCH_BTN.click()
        self.client_search.FOUNDED_FIO[-1].wait_to_have_text(re.compile("авто"), timeout=20000)
        self.client_search.FOUNDED_FIO.to_contain_text_in_all(expected_text="авто")


@pytest.mark.regress
@allure.epic("E2E_34 Поиск клиента/абонента")
@allure.suite("E2E_34 Поиск клиента/абонента")
@allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=674672853", name="Поиск клиента/абонента")
class TestSearchMainPageSubscriber:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_ui_stand_login: Page, api_request_context: APIRequestContext) -> None:
        self.home_page = HomePage(nexign_ui_stand_login)
        self.client_search = ClientSearch(nexign_ui_stand_login)
        self.client_profile = ClientProfilePage(nexign_ui_stand_login)
        self.client_request_api = ClientInquiriesRequests(api_request_context)

    @allure.title("Валидация поля 'Абонент' — корректный формат")
    @allure.id(517432)
    @allure.description(
        "Проверить, что при вводе значения до 15 символов поиск выполняется корректно по полному совпадению номера/логина абонента"
    )
    def test_subscriber_field_validation_positive(self, create_individual_user: IndividualClient) -> None:
        inquiry = self.client_request_api.product_sale(create_individual_user)
        self.home_page.HEADER_SEARCH_BTN.wait_to_be_visible()
        self.home_page.HEADER_SUBSCRIBER.fill(inquiry.product.phone_number)
        self.home_page.HEADER_SEARCH_BTN.click()
        self.client_search.FOUNDED_FIO.wait_to_have_count(1)
        self.client_search.FOUNDED_FIO[0].click()
        self.client_profile.locators.CLIENT_FIO_BTN.wait_to_be_visible()
        self.client_profile.locators.PRODUCTS_TAB.click()
        self.client_profile.locators.SUBSCRIBER.wait_to_have_text(inquiry.product.phone_number)

    @allure.title("Валидация поля 'Абонент'— некорректное заполнение поля")
    @allure.id(517438)
    @allure.description("Проверить, что при вводе некорректного значения происходит переход на страницу 'Поиск'")
    def test_subscriber_field_validation_wrong_num(self) -> None:
        wrong_subscriber = f"{generate_random_number(15)}%$&"
        self.home_page.HEADER_SEARCH_BTN.wait_to_be_visible()
        self.home_page.HEADER_SUBSCRIBER.fill(wrong_subscriber)
        self.home_page.HEADER_SEARCH_BTN.click()
        self.client_search.TITLE.wait_to_have_text("Поиск клиента")
        self.client_search.FOUNDED_FIO.wait_not_to_be_visible()
        self.client_search.SUBSCRIPTION_ID.to_have_value(wrong_subscriber)


@pytest.mark.regress
@allure.epic("E2E_34 Поиск клиента/абонента")
@allure.suite("E2E_34 Поиск клиента/абонента")
@allure.tag("can_auth", "success")
@allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=674672853", name="Поиск клиента/абонента")
class TestSearchMainPageInn:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_ui_stand_login: Page, api_request_context: APIRequestContext) -> None:
        self.home_page = HomePage(nexign_ui_stand_login)
        self.client_search = ClientSearch(nexign_ui_stand_login)
        self.client_profile = ClientProfilePage(nexign_ui_stand_login)
        self.client_request_api = ClientRequests(api_request_context)

    @allure.title("Валидация поля 'ИНН' — корректный формат")
    @allure.id(517442)
    @allure.description("Проверить, что система корректно выполняет поиск по ИНН длиной 10 или 12 символов.")
    def test_inn_field_validation_positive(
        self,
        create_organization_with_agreement_and_account: OrganizationClient,
        create_entrepreneur_with_agreement_and_account: EntrepreneurClient,
    ) -> None:
        organization = create_organization_with_agreement_and_account
        entrepreneur = create_entrepreneur_with_agreement_and_account

        with allure.step("Проверка поиска ИНН с 10-значным значением"):
            self.home_page.HEADER_SEARCH_BTN.wait_to_be_visible()
            self.home_page.INN.fill(organization.inn)
            self.home_page.HEADER_SEARCH_BTN.click()

            self.client_search.FOUNDED_FIO.wait_to_be_visible(timeout=15000)
            self.client_search.FOUNDED_FIO.wait_to_have_count(1, timeout=15000)
            self.client_search.FOUNDED_FIO[0].to_contain_text(organization.customer_name)

        with allure.step("Проверка поиска ИНН с 12-значным значением"):
            self.home_page.HOME_BTN.click()
            self.home_page.HEADER_SEARCH_BTN.wait_to_be_visible()
            self.home_page.INN.fill(entrepreneur.inn)
            self.home_page.HEADER_SEARCH_BTN.click()

            self.client_search.FOUNDED_FIO.wait_to_be_visible(timeout=15000)
            self.client_search.FOUNDED_FIO.wait_to_have_count(1, timeout=15000)
            self.client_search.FOUNDED_FIO[0].to_contain_text(entrepreneur.sur_name)

            self.client_search.FOUNDED_FIO[0].click()
            self.client_profile.locators.CLIENT_FIO_BTN.wait_to_be_visible(timeout=15000)
            self.client_profile.locators.CLIENT_TAB.click()
            self.client_profile.locators.INN.to_have_value(entrepreneur.inn)

        with allure.step("Очистить фильтры поиска"):
            self.home_page.HOME_BTN.click()

    @allure.title("Валидация поля 'ИНН'— некорректное заполнение поля")
    @allure.id(518347)
    @allure.description("Проверить, что при вводе некорректного значения происходит переход на страницу 'Поиск'")
    def test_inn_field_validation_wrong_num(self) -> None:
        wrong_inn = f"{generate_random_number(15)}"
        self.home_page.HEADER_SEARCH_BTN.wait_to_be_visible()
        self.home_page.INN.fill(wrong_inn)
        self.home_page.HEADER_SEARCH_BTN.click()
        self.client_search.TITLE.wait_to_have_text("Поиск клиента")
        self.client_search.FOUNDED_FIO.wait_not_to_be_visible()
        self.client_search.INN_INPUT.to_have_value(wrong_inn)
