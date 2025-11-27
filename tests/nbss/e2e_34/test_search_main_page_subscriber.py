import allure
import pytest
from playwright.sync_api import APIRequestContext, Page

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from common.helpers.data_generator import generate_random_number
from models.inquiry import prepare_inquiries
from models.user import IndividualClient, OrganizationClient
from pages.locators.nbss.client.client_search import ClientSearch
from pages.locators.nbss.home_page_elements import HomePage
from pages.nbss.client.client_profile_page import ClientProfilePage


@pytest.mark.regress
@pytest.mark.nbss_portal
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

    @allure.title("Валидация поля 'Абонент' — чувствительность к регистру")
    @allure.id(518302)
    @allure.description("Проверить, что поиск по полю 'Абонент' не зависит от регистра букв")
    def test_subscriber_field_case_sensitivity(
        self, create_organization_with_agreement_and_account: OrganizationClient
    ) -> None:
        with allure.step("Создание абонента с логином"):
            inquiry = self.client_request_api.product_sale(inquiry=prepare_inquiries("internet"))
            subscriber_login = inquiry.product.internet_number

        with allure.step(f"Поиск абонента с логином в ВЕРХНЕМ регистре: {subscriber_login.upper()}"):
            self.client_profile.search_from_main_page(subscriber=subscriber_login.upper())

        with allure.step("Проверка результатов поиска в верхнем регистре"):
            self.client_search.FOUNDED_FIO.wait_to_have_count(1, timeout=15000)
            self.client_search.FOUNDED_FIO[0].click()
            self.client_profile.locators.CLIENT_FIO_BTN.wait_to_be_visible()
            self.client_profile.locators.PRODUCTS_TAB.click()
            self.client_profile.locators.SUBSCRIBER.wait_to_have_text(subscriber_login)

        with allure.step("Возврат на главную страницу для повторного поиска"):
            self.home_page.HOME_BTN.click()
            self.home_page.HEADER_SUBSCRIBER.wait_to_be_visible()

        with allure.step(f"Поиск абонента с логином в нижнем регистре: {subscriber_login.lower()}"):
            self.client_profile.search_from_main_page(subscriber=subscriber_login.lower())

        with allure.step("Проверка результатов поиска в нижнем регистре"):
            self.client_search.FOUNDED_FIO.wait_to_have_count(1, timeout=15000)
            self.client_search.FOUNDED_FIO[0].click()
            self.client_profile.locators.CLIENT_FIO_BTN.wait_to_be_visible()
            self.client_profile.locators.PRODUCTS_TAB.click()
            self.client_profile.locators.SUBSCRIBER.wait_to_have_text(subscriber_login)
