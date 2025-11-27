import random

import allure
import pytest
from playwright.sync_api import Page

from common.helpers.data_generator import generate_russian_string
from models.user import OrganizationClient
from pages.locators.nbss.client.client_search import ClientSearch
from pages.locators.nbss.home_page_elements import HomePage
from pages.nbss.client.client_profile_page import ClientProfilePage


@pytest.mark.regress
@pytest.mark.nbss_portal
@allure.epic("E2E_34 Поиск клиента/абонента")
@allure.suite("E2E_34 Поиск клиента/абонента")
@allure.tag("can_auth", "success")
@allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=674672853", name="Поиск клиента/абонента")
class TestSearchMainPageClient:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_ui_stand_login: Page) -> None:
        self.home_page = HomePage(nexign_ui_stand_login)
        self.client_search = ClientSearch(nexign_ui_stand_login)
        self.client_profile = ClientProfilePage(nexign_ui_stand_login)

    @allure.title("Валидация поля 'Клиент' — корректное заполнение")
    @allure.id(517381)
    @allure.description(
        "Проверить, что поиск выполняется корректно, когда введено более 3 символов и менее 240 символов"
    )
    def test_client_field_validation_positive(
        self, create_organization_with_agreement_and_account: OrganizationClient
    ) -> None:
        created_client = create_organization_with_agreement_and_account

        self.client_profile.search_from_main_page(customer_name=created_client.customer_name)

        with allure.step("Проверка результатов поиска"):
            self.client_search.FOUNDED_FIO.wait_to_be_visible(timeout=15000)
            assert self.client_search.FOUNDED_FIO.elements_len() > 0, "Список найденных клиентов пуст"
            self.client_search.FOUNDED_FIO.to_contain_text_in_any(created_client.customer_name, timeout=5)

    @allure.title("Валидация поля 'Клиент'— некорректное заполнение поля")
    @allure.id(517386)
    @allure.description("Проверить, что при вводе некорректного значения происходит переход на страницу 'Поиск'")
    def test_client_field_validation_wrong_num(self) -> None:
        wrong_customer_name = f"{generate_russian_string(15)}%$&"

        self.client_profile.search_from_main_page(customer_name=wrong_customer_name)

        with allure.step("Проверка, что результаты поиска не найдены"):
            self.client_search.FOUNDED_FIO.wait_not_to_be_visible()

        with allure.step("Проверка, что некорректное значение сохранено в поле"):
            self.client_search.CUSTOMER_NAME_INPUT.to_have_value(wrong_customer_name)

    @allure.title("Валидация поля 'Клиент' — поиск по подстроке")
    @allure.id(517428)
    @allure.description("Проверить, что поиск работает по вхождению подстроки в имени клиента.")
    def test_client_field_validation_part_of_name(
        self, create_organization_with_agreement_and_account: OrganizationClient
    ) -> None:
        client_name = create_organization_with_agreement_and_account.customer_name

        min_length = 4
        max_length = len(client_name)
        substring_length = random.randint(min_length, max_length)
        max_start_position = max(0, max_length - substring_length)
        start_position = random.randint(0, max_start_position)
        search_substring = client_name[start_position : start_position + substring_length]

        self.client_profile.search_from_main_page(customer_name=search_substring)

        with allure.step("Проверка результатов поиска"):
            self.client_search.FOUNDED_FIO.wait_to_be_visible(timeout=15000)
            assert self.client_search.FOUNDED_FIO.elements_len() > 0, "Список найденных клиентов пуст"
            self.client_search.FOUNDED_FIO.to_contain_text_in_any(client_name, timeout=5)
