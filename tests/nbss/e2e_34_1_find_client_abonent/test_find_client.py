import allure
import pytest

from api.nbss.client_requests.client_requests import ClientRequests
from common.enums.user import User
from common.helpers.download_helper import CheckFile
from common.helpers.env_helper import BASE_URL
from models.context import test_context
from pages.base_page import BasePage
from pages.locators.nbss.client.client_search import ClientSearchElements
from pages.nbss.home_page import HomePage


@allure.epic("E2E_34_1 Поиск клиента/абонента (Этап 2)")
@allure.suite("E2E_34_1 Поиск клиента/абонента (Этап 2)")
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestFindClient:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login, create_organization) -> None:
        self.base_page = BasePage()
        self.client = create_organization
        self.client_api = ClientRequests()
        self.search_client_page = ClientSearchElements()
        self.home_page = HomePage()

    @allure.title("01. Расширенный поиск клиента с указанием юридического типа(clone)")
    @allure.id(817827)
    def test_find_client_customer_name(self) -> None:
        with allure.step("Создание клиента, переход в его контекст"):
            self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{self.client.user_id}/products")
            self.base_page.base_elements.HOME_BTN.wait_to_be_visible()
            self.base_page.base_elements.HOME_BTN.click()
        with allure.step("Переход в расширенный поиск и валидация полей"):
            self.home_page.go_to_search_and_clear_filters()
            self.home_page.verify_input_parametrs()
        with allure.step("Поиск клиента"):
            self.home_page.search_client(customer_name=test_context.client.customer_name)
        with allure.step("Проверка информации в таблице поиска"):
            self.home_page.verify_client_found(client=test_context.client)

    @allure.title("2.10. Расширенный поиск клиента (нет роли)")
    @allure.id(817830)
    @pytest.mark.user(User.FINANCE_TEST)
    def test_find_client_without_permission(self) -> None:
        with allure.step("Создание клиента, переход в его контекст"):
            self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{self.client.user_id}/products")
            self.base_page.base_elements.HOME_BTN.wait_to_be_visible()
            self.base_page.base_elements.HOME_BTN.click()
            self.home_page.locators.CUSTOMER_NAME.not_to_be_visible()

    @allure.title("2.11. Расширенный поиск клиента по ИНН")
    @allure.id(817828)
    def test_find_client_inn(self) -> None:
        with allure.step("Создание клиента, переход в его контекст"):
            self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{self.client.user_id}/products")
            self.base_page.base_elements.HOME_BTN.wait_to_be_visible()
            self.base_page.base_elements.HOME_BTN.click()
        with allure.step("Переход в расширенный поиск и валидация полей"):
            self.home_page.go_to_search_and_clear_filters()
            self.home_page.verify_input_parametrs()
        with allure.step("Поиск клиента"):
            self.home_page.search_client(inn=test_context.client.inn)
        with allure.step("Проверка информации в таблице поиска"):
            self.home_page.verify_client_found(client=test_context.client)

    @allure.title("2.12. Расширенный поиск клиента по КПП")
    @allure.id(817829)
    def test_find_client_kpp(self) -> None:
        with allure.step("Создание клиента, переход в его контекст"):
            self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{self.client.user_id}/products")
            self.base_page.base_elements.HOME_BTN.wait_to_be_visible()
            self.base_page.base_elements.HOME_BTN.click()
        with allure.step("Переход в расширенный поиск и валидация полей"):
            self.home_page.go_to_search_and_clear_filters()
            self.home_page.verify_input_parametrs()
        with allure.step("Поиск клиента"):
            self.home_page.search_client(inn=test_context.client.inn, kpp=test_context.client.kpp)
        with allure.step("Проверка информации в таблице поиска"):
            self.home_page.verify_client_found(client=test_context.client)

    @allure.title("2.13. Выгрузка результатов расширенного поиска")
    @allure.id(817831)
    @pytest.mark.skip("https://jira.nexign.com/browse/TUDS-5439")
    def test_find_client_upload_file(self, cleanup_download_files) -> None:
        with allure.step("Создание клиента, переход в его контекст"):
            self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{self.client.user_id}/products")
            self.base_page.base_elements.HOME_BTN.wait_to_be_visible()
            self.base_page.base_elements.HOME_BTN.click()
        with allure.step("Переход в расширенный поиск и валидация полей"):
            self.home_page.go_to_search_and_clear_filters()
            self.home_page.verify_input_parametrs()
        with allure.step("Поиск клиента"):
            self.home_page.search_client(inn=test_context.client.inn)
        with allure.step("Проверка информации в таблице поиска"):
            self.home_page.verify_client_found(client=test_context.client)
        with allure.step("Скачивание файла и проверка Excel"):
            self.home_page.client_search_page.EXPORT_BTN.wait_to_be_visible()
            with test_context.page.expect_download(timeout=20000) as download_info:
                self.home_page.client_search_page.EXPORT_BTN.click()
                download = download_info.value
                file_name = download.suggested_filename

                file_check = CheckFile(file_name)
                download.save_as(file_check.path)
                cleanup_download_files.append(file_check.path)

                file_check.is_exist()
                file_check.is_excel_file()

                file_check.check_excel_file_group_of_fields_contains(
                    fields=[[0, 0], [0, 1], [1, 0]],
                    expected_values=["Клиент", "Юр. тип клиента", f"АО {self.client.customer_name}"],
                )
