import allure
import pytest

from pages.base_page import BasePage
from pages.locators.nbss.client.client_search import ClientSearch


@pytest.mark.nbss_portal_mock
class TestPortalStartPageClientSearch:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_ui_mock_login, base_url) -> None:
        self.base_page = BasePage()
        self.client_search = ClientSearch()
        self.base_url = base_url

    @allure.title("Проверка поиска по Абоненту")
    def test_subs_search(self):
        self.client_search.HEADER_SUBSCRIBER.wait_to_be_visible()
        self.client_search.HEADER_SUBSCRIBER.type("%%%")
        self.client_search.HEADER_SEARCH_BTN.click()
        self.client_search.FOUNDED_CLIENTS.wait_to_have_count(1)

    @allure.title("Проверка поиска по Лицевому счету")
    def test_account_number_search(self):
        self.client_search.HEADER_ACCOUNT_NUM.wait_to_be_visible()
        self.client_search.HEADER_ACCOUNT_NUM.type("%%%")
        self.client_search.HEADER_SEARCH_BTN.click()
        self.client_search.FOUNDED_CLIENTS.wait_to_have_count(1)

    @allure.title("Проверка поиска по Абоненту в титульной строчке")
    def test_topline_subs_search(self):
        self.base_page.open(self.base_url + "external-sso-ui")
        self.client_search.HEADER_SUBSCRIBER.wait_to_be_visible()
        self.client_search.HEADER_SUBSCRIBER.type("%%%")
        self.client_search.HEADER_SEARCH_BTN.click()
        self.client_search.FOUNDED_CLIENTS.wait_to_have_count(1)

    @allure.title("Проверка поиска по Лицевому счету в титульной строчке")
    def test_topline_account_number_search(self):
        self.base_page.open(self.base_url + "external-sso-ui")
        self.client_search.HEADER_ACCOUNT_NUM.wait_to_be_visible()
        self.client_search.HEADER_ACCOUNT_NUM.type("%%%")
        self.client_search.HEADER_SEARCH_BTN.click()
        self.client_search.FOUNDED_CLIENTS.wait_to_have_count(1)
