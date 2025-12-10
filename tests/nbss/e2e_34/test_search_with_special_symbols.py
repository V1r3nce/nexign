import allure
import pytest

from api.nbss.client_requests.client_requests import ClientRequests
from api.nbss.personal_account_requests import PersonalAccountRequests
from common.helpers.data_generator import generate_random_number
from models.user import OrganizationClient
from pages.locators.nbss.client.client_search import ClientSearchElements
from pages.locators.nbss.home_page_elements import HomePageElements
from pages.nbss.client.client_profile_page import ClientProfilePage


@pytest.mark.regress
@pytest.mark.nbss_portal
@allure.epic("E2E_34 Поиск клиента/абонента")
@allure.suite("E2E_34 Поиск клиента/абонента")
@allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=674672853", name="Поиск клиента/абонента")
class TestSearchWithSpecialSymbols:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login) -> None:
        self.home_page = HomePageElements()
        self.client_search_page = ClientSearchElements()
        self.client_profile = ClientProfilePage()

    @allure.title("Валидация поля Лицевой счет — ввод специальных символов")
    @allure.id(516084)
    def test_search_account_with_special_symbols(self) -> None:
        special_symbols = "@#%!"

        self.client_profile.search_from_main_page(account_number=special_symbols)

        with allure.step("Проверка, что спецсимволы сохранены в поле"):
            self.client_search_page.ACCOUNT_NUM.to_have_value(special_symbols)

    @allure.title("Валидация поля 'Абонент' — ввод специальных символов")
    @allure.id(518260)
    def test_search_subscriber_with_special_symbols(self) -> None:
        special_symbols = "@#%!"

        self.client_profile.search_from_main_page(subscriber=special_symbols)

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
    ) -> None:
        unique_id = generate_random_number(6)
        client_name_with_symbols = f"ООО Тест-Компания (Автотесты-{unique_id}), Лтд"
        organization = OrganizationClient()
        organization.customer_name = client_name_with_symbols

        client_requests = ClientRequests()
        personal_account_api = PersonalAccountRequests()

        with allure.step("Создание клиента с именем, содержащим спецсимволы '-', '(', ')', ','"):
            created_client = client_requests.create_organization(organization)
            personal_account_api.create_agreement_and_account(created_client)

        self.client_profile.search_from_main_page(customer_name=client_name_with_symbols)

        with allure.step("Проверка результатов поиска"):
            self.client_search_page.FOUNDED_FIO.wait_to_be_visible(timeout=15000)
            assert self.client_search_page.FOUNDED_FIO.elements_len() > 0, "Список найденных клиентов пуст"
            self.client_search_page.FOUNDED_FIO.to_contain_text_in_any(client_name_with_symbols, timeout=5)

        with allure.step("Проверка отображения информации о клиенте в таблице результатов"):
            self.client_search_page.FOUNDED_CUSTOMER_TYPE.wait_to_be_visible()
            self.client_search_page.FOUNDED_CUSTOMER_STATUS.wait_to_be_visible()
            self.client_search_page.FOUNDED_ACCOUNT_NUM.wait_to_be_visible()
