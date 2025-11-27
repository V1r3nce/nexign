import allure
import pytest
from playwright.sync_api import Page

from common.helpers.data_generator import generate_random_number
from models.context import test_context
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
    def setup(self, nexign_ui_stand_login: Page) -> None:
        self.home_page = HomePage(nexign_ui_stand_login)
        self.client_search = ClientSearch(nexign_ui_stand_login)
        self.client_profile = ClientProfilePage(nexign_ui_stand_login)

    @allure.title("Валидация поля 'Лицевой счет' — корректное заполнение")
    @allure.id(514723)
    @allure.description(
        "Проверить, что поиск по полю 'Лицевой счет' выполняется корректно, когда введен полный номер ЛС не превышающий 128 символов"
    )
    def test_account_number_field_validation_positive(
        self, create_organization_with_agreement_and_account: OrganizationClient
    ) -> None:
        account_number = test_context.client.agreements[0].accounts[0].number

        self.client_profile.search_from_main_page(account_number=account_number)

        with allure.step("Проверка результатов поиска"):
            self.client_search.FOUNDED_FIO.wait_to_be_visible(timeout=15000)
            assert self.client_search.FOUNDED_FIO.elements_len() > 0, "Список найденных клиентов пуст"
            found_account = False
            for i in range(self.client_search.FOUNDED_FIO.elements_len()):
                if str(account_number) in self.client_search.FOUNDED_ACCOUNT_NUM[i].text:
                    found_account = True
                    break
            assert found_account, f"Лицевой счет '{account_number}' не найден в списке результатов"

    @allure.title("Валидация поля 'Лицевой счет'— некорректное заполнение поля")
    @allure.id(516072)
    @allure.description("Проверить, что при вводе некорректного значения происходит переход на страницу 'Поиск'")
    def test_account_number_field_validation_wrong_num(self) -> None:
        wrong_account_number = f"{generate_random_number(15)}%$&"

        self.client_profile.search_from_main_page(account_number=wrong_account_number)

        with allure.step("Проверка, что результаты поиска не найдены"):
            self.client_search.FOUNDED_FIO.wait_not_to_be_visible()

        with allure.step("Проверка, что некорректный номер лицевого счета сохранен в поле"):
            self.client_search.ACCOUNT_NUM.to_have_value(wrong_account_number)
