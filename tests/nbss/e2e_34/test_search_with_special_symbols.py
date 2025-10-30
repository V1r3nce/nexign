import allure
import pytest
from playwright.sync_api import Page

from pages.locators.nbss.client.client_search import ClientSearch
from pages.locators.nbss.home_page_elements import HomePage


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
