import allure
import pytest
from playwright.sync_api import APIRequestContext, Page

from api.nbss.client_requests.client_requests import ClientRequests
from common.helpers.data_generator import generate_random_number, generate_russian_string
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
    def test_inn_field_validation_more_than_12_digits(self) -> None:
        wrong_inn = str(generate_random_number(13))

        with allure.step("Проверка отображения полей на главной странице"):
            self.home_page.HEADER_SEARCH_BTN.wait_to_be_visible()
            self.home_page.INN.wait_to_be_visible()

        with allure.step(f"Ввод ИНН больше 12 цифр '{wrong_inn}' в поле 'ИНН' на главной странице"):
            self.home_page.INN.fill(wrong_inn)
            self.home_page.HEADER_SEARCH_BTN.click()

        with allure.step("Проверка перехода на форму расширенного поиска"):
            self.client_search.TITLE.wait_to_have_text("Поиск клиента", timeout=10000)
            self.client_search.CUSTOMER_NAME_INPUT.wait_to_be_visible()

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

        with allure.step("Проверка отображения полей на главной странице"):
            self.home_page.HEADER_SEARCH_BTN.wait_to_be_visible()
            self.home_page.INN.wait_to_be_visible()

        with allure.step(f"Ввод буквенного значения '{wrong_inn_letters}' в поле 'ИНН' на главной странице"):
            self.home_page.INN.fill(wrong_inn_letters)
            self.home_page.HEADER_SEARCH_BTN.click()

        with allure.step("Проверка перехода на форму расширенного поиска"):
            self.client_search.TITLE.wait_to_have_text("Поиск клиента", timeout=10000)
            self.client_search.CUSTOMER_NAME_INPUT.wait_to_be_visible()

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
        entrepreneur = create_entrepreneur_with_agreement_and_account
        search_inn = entrepreneur.inn
        expected_client = entrepreneur
        expected_name = entrepreneur.sur_name

        with allure.step("Проверка отображения полей на главной странице"):
            self.home_page.HEADER_SEARCH_BTN.wait_to_be_visible()
            self.home_page.INN.wait_to_be_visible()

        with allure.step(f"Ввод ИНН '{search_inn}' в поле 'ИНН' на главной странице"):
            self.home_page.INN.fill(search_inn)
            self.home_page.HEADER_SEARCH_BTN.click()

        with allure.step("Проверка перехода на форму расширенного поиска"):
            self.client_search.TITLE.wait_to_have_text("Поиск клиента", timeout=10000)
            self.client_search.CUSTOMER_NAME_INPUT.wait_to_be_visible()

        with allure.step("Очистка предзаполненных фильтров и выполнение поиска"):
            self.client_profile._clear_all_filters()
            self.client_search.SEARCH_BTN.click()

        with allure.step("Проверка результатов поиска"):
            self.client_search.FOUNDED_FIO.wait_to_be_visible(timeout=15000)
            self.client_search.FOUNDED_FIO.wait_to_have_count(1, timeout=15000)
            self.client_search.FOUNDED_FIO[0].to_contain_text(expected_name)

        with allure.step("Проверка ИНН в профиле клиента"):
            self.client_search.FOUNDED_FIO[0].click()
            self.client_profile.locators.CLIENT_FIO_BTN.wait_to_be_visible(timeout=15000)
            self.client_profile.locators.CLIENT_TAB.click()
            self.client_profile.locators.INN.to_have_value(expected_client.inn)
            self.home_page.HOME_BTN.click()

    @allure.title("Валидация поля 'ИНН' — поиск по подстроке ИНН (меньше 10 цифр)")
    @allure.id(753888)
    @allure.description("Проверить, что поиск по подстроке ИНН (меньше 10 цифр) находит ИНН длиной 10 и 12 цифр")
    def test_inn_field_validation_substring_less_10(
        self,
        create_organization_with_agreement_and_account: OrganizationClient,
    ) -> None:
        organization = create_organization_with_agreement_and_account
        search_inn = organization.inn[:9]
        expected_name = organization.customer_name

        with allure.step("Проверка отображения полей на главной странице"):
            self.home_page.HEADER_SEARCH_BTN.wait_to_be_visible()
            self.home_page.INN.wait_to_be_visible()

        with allure.step(f"Ввод ИНН '{search_inn}' в поле 'ИНН' на главной странице"):
            self.home_page.INN.fill(search_inn)
            self.home_page.HEADER_SEARCH_BTN.click()

        with allure.step("Проверка перехода на форму расширенного поиска"):
            self.client_search.TITLE.wait_to_have_text("Поиск клиента", timeout=10000)
            self.client_search.CUSTOMER_NAME_INPUT.wait_to_be_visible()

        with allure.step("Очистка предзаполненных фильтров и выполнение поиска"):
            self.client_profile._clear_all_filters()
            self.client_search.SEARCH_BTN.click()

        with allure.step("Проверка результатов поиска"):
            self.client_search.FOUNDED_FIO.wait_to_be_visible(timeout=15000)
            self.client_search.FOUNDED_FIO.wait_to_have_count(1, timeout=15000)
            self.client_search.FOUNDED_FIO[0].to_contain_text(expected_name)

    @allure.title("Валидация поля 'ИНН' — поиск по подстроке ИНН (11 цифр)")
    @allure.id(753942)
    @allure.description("Проверить, что поиск по подстроке ИНН (11 цифр) находит ИНН длиной 12 цифр")
    def test_inn_field_validation_substring_11(
        self,
        create_entrepreneur_with_agreement_and_account: EntrepreneurClient,
    ) -> None:
        entrepreneur = create_entrepreneur_with_agreement_and_account
        search_inn = entrepreneur.inn[:11]
        expected_name = entrepreneur.sur_name

        with allure.step("Проверка отображения полей на главной странице"):
            self.home_page.HEADER_SEARCH_BTN.wait_to_be_visible()
            self.home_page.INN.wait_to_be_visible()

        with allure.step(f"Ввод ИНН '{search_inn}' в поле 'ИНН' на главной странице"):
            self.home_page.INN.fill(search_inn)
            self.home_page.HEADER_SEARCH_BTN.click()

        with allure.step("Проверка перехода на форму расширенного поиска"):
            self.client_search.TITLE.wait_to_have_text("Поиск клиента", timeout=10000)
            self.client_search.CUSTOMER_NAME_INPUT.wait_to_be_visible()

        with allure.step("Очистка предзаполненных фильтров и выполнение поиска"):
            self.client_profile._clear_all_filters()
            self.client_search.SEARCH_BTN.click()

        with allure.step("Проверка результатов поиска"):
            self.client_search.FOUNDED_FIO.wait_to_be_visible(timeout=15000)
            self.client_search.FOUNDED_FIO.wait_to_have_count(1, timeout=15000)
            self.client_search.FOUNDED_FIO[0].to_contain_text(expected_name)

    @allure.title("Валидация поля 'ИНН' — поиск по ИНН длиной 10 цифр (точное совпадение для 10 и подстрока для 12)")
    @allure.id(753953)
    @allure.description("Проверить, что поиск по ИНН длиной 10 цифр дает точное совпадение для 10 и подстроку для 12")
    def test_inn_field_validation_exact_and_substring(
        self,
        create_organization_with_agreement_and_account: OrganizationClient,
    ) -> None:
        organization = create_organization_with_agreement_and_account
        search_inn = organization.inn
        expected_name = organization.customer_name

        with allure.step("Проверка отображения полей на главной странице"):
            self.home_page.HEADER_SEARCH_BTN.wait_to_be_visible()
            self.home_page.INN.wait_to_be_visible()

        with allure.step(f"Ввод ИНН '{search_inn}' в поле 'ИНН' на главной странице"):
            self.home_page.INN.fill(search_inn)
            self.home_page.HEADER_SEARCH_BTN.click()

        with allure.step("Проверка перехода на форму расширенного поиска"):
            self.client_search.TITLE.wait_to_have_text("Поиск клиента", timeout=10000)
            self.client_search.CUSTOMER_NAME_INPUT.wait_to_be_visible()

        with allure.step("Очистка предзаполненных фильтров и выполнение поиска"):
            self.client_profile._clear_all_filters()
            self.client_search.SEARCH_BTN.click()

        with allure.step("Проверка результатов поиска"):
            self.client_search.FOUNDED_FIO.wait_to_be_visible(timeout=15000)
            self.client_search.FOUNDED_FIO.wait_to_have_count(1, timeout=15000)
            self.client_search.FOUNDED_FIO[0].to_contain_text(expected_name)
