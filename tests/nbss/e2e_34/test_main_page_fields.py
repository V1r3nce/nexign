import allure
import pytest
from playwright.sync_api import Page

from pages.locators.nbss.home_page_elements import HomePage


@pytest.mark.regress
@pytest.mark.nbss_portal
@allure.epic("E2E_34 Поиск клиента/абонента")
@allure.suite("E2E_34 Поиск клиента/абонента")
@allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=674672853", name="Поиск клиента/абонента")
class TestDisplayingAllFieldsMainPage:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_ui_stand_login: Page):
        self.page = nexign_ui_stand_login
        self.home_page = HomePage(self.page)

    @allure.title("Авторизация и проверка основных полей на главной форме")
    @allure.id(681536)
    def test_displaying_all_fields_mainpage(self):
        self.home_page.CUSTOMER_NAME.wait_to_be_visible()
        self.home_page.HEADER_SUBSCRIBER.wait_to_be_visible()
        self.home_page.HEADER_ACCOUNT_NUM.wait_to_be_visible()
        self.home_page.INN.wait_to_be_visible()
        self.home_page.HEADER_SEARCH_BTN.wait_to_be_visible()
