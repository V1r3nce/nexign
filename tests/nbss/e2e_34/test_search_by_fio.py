import allure
import pytest
from playwright.sync_api import Page

from models.user import IndividualClient
from pages.nbss.client.client_profile_page import ClientProfilePage


@pytest.mark.regress
@pytest.mark.nbss_portal
@allure.epic("E2E_34 Поиск клиента/абонента")
@allure.suite("E2E_34 Поиск клиента/абонента")
@allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=674672853", name="Поиск клиента/абонента")
class TestSearchByFIO:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_ui_stand_login: Page):
        self.page = nexign_ui_stand_login
        self.client_profile_page = ClientProfilePage(self.page)

    @allure.title("Поиск клиента по наименованию/ФИО")
    @allure.id(680911)
    def test_search_individual_client_by_fio(self, create_individual_user: IndividualClient) -> None:
        client = create_individual_user
        full_name = f"{client.sur_name} {client.first_name} {client.patronymic}"

        with allure.step("Переход на страницу расширенного поиска и очистка фильтров"):
            self.client_profile_page.go_to_search_and_clear_filters()

        with allure.step(f"Поиск клиента по ФИО '{full_name}'"):
            self.client_profile_page.search_client(customer_name=full_name)

        self.client_profile_page._verify_client_found(client)

    @allure.title("Поиск клиента по наименованию/ФИО с указанием статуса")
    @allure.id(680912)
    def test_search_client_with_status_filter(self, create_individual_user: IndividualClient) -> None:
        client = create_individual_user
        full_name = f"{client.sur_name} {client.first_name} {client.patronymic}"

        with allure.step("Переход на страницу расширенного поиска и очистка фильтров"):
            self.client_profile_page.go_to_search_and_clear_filters()

        with allure.step("Поиск клиента по ФИО с неправильным статусом"):
            self.client_profile_page.search_client(customer_name=full_name, customer_status="Потенциальный")

        with allure.step("Проверка, что клиент НЕ найден"):
            self.client_profile_page.verify_client_not_found()

        with allure.step("Смена статуса на 'Действующий' и повторный поиск"):
            self.client_profile_page.search_client(customer_name=full_name, customer_status="Действующий")

        self.client_profile_page._verify_client_found(client)

    @allure.title("Валидация поля Клиент— чувствительность к регистру")
    @allure.id(517704)
    def test_search_case_insensitive(self, create_individual_user: IndividualClient) -> None:
        client = create_individual_user
        full_name = f"{client.sur_name} {client.first_name}"
        full_name_upper = full_name.upper()
        full_name_lower = full_name.lower()

        with allure.step("Переход на страницу расширенного поиска и очистка фильтров"):
            self.client_profile_page.go_to_search_and_clear_filters()

        with allure.step(f"Ввод имени клиента в ВЕРХНЕМ регистре: {full_name_upper}"):
            self.client_profile_page.client_search_page.CUSTOMER_NAME_INPUT.fill(full_name_upper)

        with allure.step("Запуск поиска"):
            self.client_profile_page.client_search_page.SEARCH_BTN.click()

        with allure.step("Проверка результатов поиска в верхнем регистре"):
            self.client_profile_page.client_search_page.FOUNDED_CLIENTS.wait_to_be_visible(timeout=15000)

        with allure.step("Очистка поля поиска"):
            self.client_profile_page.client_search_page.CUSTOMER_NAME_INPUT.clear_input()

        with allure.step(f"Ввод имени клиента в нижнем регистре: {full_name_lower}"):
            self.client_profile_page.client_search_page.CUSTOMER_NAME_INPUT.fill(full_name_lower)

        with allure.step("Запуск поиска"):
            self.client_profile_page.client_search_page.SEARCH_BTN.click()

        with allure.step("Проверка результатов поиска в нижнем регистре"):
            self.client_profile_page.client_search_page.FOUNDED_CLIENTS.wait_to_be_visible(timeout=15000)

        with allure.step("Проверка найденного клиента"):
            self.client_profile_page.client_search_page.FOUNDED_CLIENTS.wait_to_have_count(1)
