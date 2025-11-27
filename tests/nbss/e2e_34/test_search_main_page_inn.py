import random

import allure
import pytest
from playwright.sync_api import APIRequestContext, Page

from api.nbss.client_requests.client_requests import ClientRequests
from common.helpers.data_generator import generate_random_number, generate_russian_string
from models.context import test_context
from models.user import EntrepreneurClient, OrganizationClient
from pages.locators.nbss.client.client_search import ClientSearch
from pages.locators.nbss.home_page_elements import HomePage
from pages.nbss.client.client_profile_page import ClientProfilePage


@pytest.mark.regress
@pytest.mark.nbss_portal
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

    @allure.title("Валидация поля 'ИНН' — ввод ИНН больше 12 цифр")
    @allure.id(753715)
    @allure.description(
        "Проверить, что система корректно выполняет поиск по ИНН больше 12 цифр и не находит результатов"
    )
    def test_inn_field_validation_more_than_12_digits(
        self, create_entrepreneur_with_agreement_and_account: EntrepreneurClient
    ) -> None:
        wrong_inn = test_context.client.inn + str(generate_random_number(random.randint(1, 3)))

        self.client_profile.search_from_main_page(inn=wrong_inn)

        with allure.step("Проверка, что результаты поиска не найдены"):
            self.client_search.FOUNDED_FIO.wait_not_to_be_visible()

        with allure.step("Проверка, что некорректный ИНН сохранен в поле"):
            self.client_search.INN_INPUT.to_have_value(wrong_inn)

    @allure.title("Валидация поля 'ИНН' — ввод буквенного значения")
    @allure.id(754030)
    @allure.description(
        "Проверить, что система корректно выполняет поиск по ИНН буквенное значение и не находит результатов"
    )
    def test_inn_field_validation_letters(self) -> None:
        wrong_inn_letters = generate_russian_string(10)

        self.client_profile.search_from_main_page(inn=wrong_inn_letters)

        with allure.step("Проверка, что результаты поиска не найдены"):
            self.client_search.FOUNDED_FIO.wait_not_to_be_visible()

        with allure.step("Проверка, что буквенное значение сохранено в поле"):
            self.client_search.INN_INPUT.to_have_value(wrong_inn_letters)

    @allure.title("Валидация поля 'ИНН' — поиск по ИНН длиной 12 цифр (точное совпадение)")
    @allure.id(753834)
    @allure.description("Проверить, что система корректно выполняет поиск по ИНН длиной 12 цифр - точное совпадение")
    def test_inn_field_validation_exact_match_12(
        self,
        create_entrepreneur_with_agreement_and_account: EntrepreneurClient,
    ) -> None:
        expected_name = test_context.client.sur_name

        self.client_profile.search_from_main_page(inn=test_context.client.inn)

        with allure.step("Проверка результатов поиска"):
            self.client_search.FOUNDED_FIO.wait_to_be_visible(timeout=15000)
            assert self.client_search.FOUNDED_FIO.elements_len() > 0, "Список найденных клиентов пуст"
            self.client_search.FOUNDED_FIO.to_contain_text_in_any(expected_name, timeout=5)

        with allure.step("Проверка ИНН в профиле клиента"):
            self.client_search.FOUNDED_FIO[0].click()
            self.client_profile.locators.CLIENT_FIO_BTN.wait_to_be_visible(timeout=15000)
            self.client_profile.locators.CLIENT_TAB.click()
            self.client_profile.locators.INN.to_have_value(test_context.client.inn)
            self.home_page.HOME_BTN.click()

    @allure.title("Валидация поля 'ИНН' — поиск по подстроке ИНН (меньше 10 цифр)")
    @allure.id(753888)
    @allure.description("Проверить, что поиск по подстроке ИНН (меньше 10 цифр) находит ИНН длиной 10 и 12 цифр")
    def test_inn_field_validation_substring_less_10(
        self,
        create_organization_with_agreement_and_account: OrganizationClient,
    ) -> None:
        substring_length = random.randint(6, 9)
        search_inn = test_context.client.inn[:substring_length]
        expected_name = test_context.client.customer_name

        self.client_profile.search_from_main_page(inn=search_inn)

        with allure.step("Проверка результатов поиска"):
            self.client_search.FOUNDED_FIO.wait_to_be_visible(timeout=15000)
            assert self.client_search.FOUNDED_FIO.elements_len() > 0, "Список найденных клиентов пуст"
            self.client_search.FOUNDED_FIO.to_contain_text_in_any(expected_name, timeout=5)

    @allure.title("Валидация поля 'ИНН' — поиск по подстроке ИНН (11 цифр)")
    @allure.id(753942)
    @allure.description("Проверить, что поиск по подстроке ИНН (11 цифр) находит ИНН длиной 12 цифр")
    def test_inn_field_validation_substring_11(
        self,
        create_entrepreneur_with_agreement_and_account: EntrepreneurClient,
    ) -> None:
        search_inn = test_context.client.inn[:11]
        expected_name = test_context.client.sur_name

        self.client_profile.search_from_main_page(inn=search_inn)

        with allure.step("Проверка результатов поиска"):
            self.client_search.FOUNDED_FIO.wait_to_be_visible(timeout=15000)
            assert self.client_search.FOUNDED_FIO.elements_len() > 0, "Список найденных клиентов пуст"
            self.client_search.FOUNDED_FIO.to_contain_text_in_any(expected_name, timeout=5)

    @allure.title("Валидация поля 'ИНН' — поиск по ИНН длиной 10 цифр (точное совпадение для 10 и подстрока для 12)")
    @allure.id(753953)
    @allure.description("Проверить, что поиск по ИНН длиной 10 цифр дает точное совпадение для 10 и подстроку для 12")
    def test_inn_field_validation_exact_and_substring(
        self,
        create_organization_with_agreement_and_account: OrganizationClient,
    ) -> None:
        expected_name = test_context.client.customer_name

        self.client_profile.search_from_main_page(inn=test_context.client.inn)

        with allure.step("Проверка результатов поиска"):
            self.client_search.FOUNDED_FIO.wait_to_be_visible(timeout=15000)
            assert self.client_search.FOUNDED_FIO.elements_len() > 0, "Список найденных клиентов пуст"
            self.client_search.FOUNDED_FIO.to_contain_text_in_any(expected_name, timeout=5)
