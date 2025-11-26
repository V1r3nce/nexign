import allure
import pytest
from playwright.sync_api import APIRequestContext, Page

from api.nbss.client_requests.client_requests import ClientRequests
from api.nbss.personal_account_requests import PersonalAccountRequests
from common.helpers.data_generator import generate_random_number
from models.user import OrganizationClient
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
    def setup(self, nexign_ui_stand_login: Page, api_request_context: APIRequestContext) -> None:
        self.home_page = HomePage(nexign_ui_stand_login)
        self.client_search = ClientSearch(nexign_ui_stand_login)
        self.client_request_api = ClientRequests(api_request_context)
        self.personal_account_api = PersonalAccountRequests(api_request_context)
        self.client_profile = ClientProfilePage(nexign_ui_stand_login)

    @allure.title("Валидация поля 'Лицевой счет' — корректное заполнение")
    @allure.id(514723)
    @allure.description(
        "Проверить, что поиск по полю 'Лицевой счет' выполняется корректно, когда введен полный номер ЛС не превышающий 128 символов"
    )
    def test_account_number_field_validation_positive(self) -> None:
        with allure.step("Создание клиента OrganizationClient"):
            organization = OrganizationClient()
            created_client = self.client_request_api.create_organization(organization)
            self.personal_account_api.create_agreement_and_account(created_client)
            account_number = created_client.agreements[0].accounts[0].number

        with allure.step("Проверка отображения полей на главной странице"):
            self.home_page.HEADER_SEARCH_BTN.wait_to_be_visible()
            self.home_page.HEADER_ACCOUNT_NUM.wait_to_be_visible()

        with allure.step(f"Ввод номера лицевого счета '{account_number}' в поле 'Лицевой счет'"):
            self.home_page.HEADER_ACCOUNT_NUM.fill(account_number)
            self.home_page.HEADER_SEARCH_BTN.click()

        with allure.step("Проверка перехода на форму расширенного поиска"):
            self.client_search.TITLE.wait_to_have_text("Поиск клиента", timeout=10000)
            self.client_search.CUSTOMER_NAME_INPUT.wait_to_be_visible()

        with allure.step("Очистка предзаполненных фильтров и выполнение поиска"):
            self.client_profile._clear_all_filters()
            self.client_search.SEARCH_BTN.click()

        with allure.step("Проверка результатов поиска"):
            self.client_search.FOUNDED_FIO.wait_to_have_count(1, timeout=15000)
            self.client_search.FOUNDED_ACCOUNT_NUM[0].wait_to_have_text(str(account_number))

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
