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
class TestSearchWithSpecialSymbols:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_ui_stand_login: Page):
        self.page = nexign_ui_stand_login
        self.home_page = HomePage(self.page)
        self.client_search_page = ClientSearch(self.page)

    @allure.title("Валидация поля Лицевой счет — ввод специальных символов")
    @allure.id(516084)
    def test_search_account_with_special_symbols(self) -> None:
        special_symbols = "@#%!"

        with allure.step("Проверка отображения полей на главной странице"):
            self.home_page.CUSTOMER_NAME.wait_to_be_visible()
            self.home_page.HEADER_ACCOUNT_NUM.wait_to_be_visible()

        with allure.step(f"Ввод спецсимволов '{special_symbols}' в поле 'Лицевой счёт'"):
            self.home_page.HEADER_ACCOUNT_NUM.fill(special_symbols)
            self.home_page.HEADER_SEARCH_BTN.click()

        with allure.step("Проверка перехода на форму расширенного поиска"):
            self.client_search_page.TITLE.wait_to_be_visible(timeout=10000)
            self.client_search_page.CUSTOMER_NAME_INPUT.wait_to_be_visible()

        with allure.step("Проверка, что спецсимволы сохранены в поле"):
            self.client_search_page.ACCOUNT_NUM.to_have_value(special_symbols)

    @allure.title("Валидация поля 'Абонент' — ввод специальных символов")
    @allure.id(518260)
    def test_search_subscriber_with_special_symbols(self) -> None:
        special_symbols = "@#%!"

        with allure.step("Проверка отображения полей на главной странице"):
            self.home_page.CUSTOMER_NAME.wait_to_be_visible()
            self.home_page.HEADER_SUBSCRIBER.wait_to_be_visible()
            self.home_page.HEADER_ACCOUNT_NUM.wait_to_be_visible()
            self.home_page.INN.wait_to_be_visible()
            self.home_page.HEADER_SEARCH_BTN.wait_to_be_visible()

        with allure.step(f"Ввод спецсимволов '{special_symbols}' в поле 'Абонент'"):
            self.home_page.HEADER_SUBSCRIBER.fill(special_symbols)
            self.home_page.HEADER_SEARCH_BTN.click()

        with allure.step("Проверка перехода на форму расширенного поиска"):
            self.client_search_page.TITLE.wait_to_be_visible(timeout=10000)
            self.client_search_page.CUSTOMER_NAME_INPUT.wait_to_be_visible()
            self.client_search_page.SUBSCRIPTION_ID.wait_to_be_visible()
            self.client_search_page.SEARCH_BTN.wait_to_be_visible()

        with allure.step("Проверка, что спецсимволы сохранены в поле 'Абонент'"):
            self.client_search_page.SUBSCRIPTION_ID.to_have_value(special_symbols)

    @allure.title("Валидация поля 'Клиент' — ввод специальных символов")
    @allure.id(517683)
    @allure.description(
        "Проверить, что поле 'Клиент' принимает только буквы и специальные символы '-', '(', ')', ','. "
        "Поиск выполняется корректно, строка со специальными символами принимается системой"
    )
    def test_search_client_with_allowed_special_symbols(
        self,
        nexign_ui_stand_login: Page,
        api_request_context: APIRequestContext,
    ) -> None:
        unique_id = generate_random_number(6)
        client_name_with_symbols = f"ООО Тест-Компания (Автотесты-{unique_id}), Лтд"
        organization = OrganizationClient()
        organization.customer_name = client_name_with_symbols

        client_requests = ClientRequests(api_request_context)
        personal_account_api = PersonalAccountRequests(api_request_context)
        client_profile = ClientProfilePage(nexign_ui_stand_login)

        with allure.step("Создание клиента с именем, содержащим спецсимволы '-', '(', ')', ','"):
            created_client = client_requests.create_organization(organization)
            personal_account_api.create_agreement_and_account(created_client)

        with allure.step("Проверка отображения полей на главной странице"):
            self.home_page.CUSTOMER_NAME.wait_to_be_visible()
            self.home_page.HEADER_SEARCH_BTN.wait_to_be_visible()

        with allure.step(f"Ввод имени клиента '{client_name_with_symbols}' в поле 'Клиент'"):
            self.home_page.CUSTOMER_NAME.fill(client_name_with_symbols)
            self.home_page.HEADER_SEARCH_BTN.click()

        with allure.step("Проверка перехода на форму расширенного поиска"):
            self.client_search_page.TITLE.wait_to_have_text("Поиск клиента", timeout=10000)
            self.client_search_page.CUSTOMER_NAME_INPUT.wait_to_be_visible()

        with allure.step("Проверка доступности параметров поиска"):
            self.client_search_page.ACCOUNT_NUM.wait_to_be_visible()
            self.client_search_page.INN_INPUT.wait_to_be_visible()
            self.client_search_page.SUBSCRIPTION_ID.wait_to_be_visible()
            self.client_search_page.SEARCH_BTN.wait_to_be_visible()

        with allure.step("Проверка предзаполненных параметров поиска"):
            self.client_search_page.CUSTOMER_NAME_INPUT.to_have_value(client_name_with_symbols)

        with allure.step("Очистка предзаполненных фильтров и выполнение поиска"):
            client_profile.clear_all_filters()
            self.client_search_page.SEARCH_BTN.click()

        with allure.step("Проверка результатов поиска"):
            self.client_search_page.FOUNDED_FIO.wait_to_be_visible(timeout=15000)
            self.client_search_page.FOUNDED_FIO.wait_to_have_count(1, timeout=15000)
            self.client_search_page.FOUNDED_FIO[0].to_contain_text(client_name_with_symbols)

        with allure.step("Проверка отображения информации о клиенте в таблице результатов"):
            self.client_search_page.FOUNDED_CUSTOMER_TYPE.wait_to_be_visible()
            self.client_search_page.FOUNDED_CUSTOMER_STATUS.wait_to_be_visible()
            self.client_search_page.FOUNDED_ACCOUNT_NUM.wait_to_be_visible()
