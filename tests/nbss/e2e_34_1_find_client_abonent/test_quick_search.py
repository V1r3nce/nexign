import allure
import pytest

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from common.enums.user import User
from models.context import test_context
from models.inquiry import prepare_inquiries
from pages.nbss.home_page import HomePage


@allure.epic("E2E_34_1 Поиск клиента/абонента (Этап 2)")
@allure.suite("E2E_34_1 Поиск клиента/абонента (Этап 2)")
@pytest.mark.regress
class TestFindClientQuick:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login) -> None:
        self.home_page = HomePage()
        self.client_inquiries_api = ClientInquiriesRequests()

    @allure.title("Быстрый поиск клиента/подразделения с титульной строки оболочки (у пользователя недостаточно прав)")
    @allure.id(676017)
    @pytest.mark.user(User.FINANCE_TEST)
    def test_unavailable_quick_search(self) -> None:
        self.home_page.locators.HEADER_ACCOUNT_NUM.not_to_be_visible()
        self.home_page.locators.HEADER_SUBSCRIBER.not_to_be_visible()

    @allure.title("Быстрый поиск клиента/подразделения с титульной строки оболочки (у пользователя достаточно прав)")
    @allure.id(676018)
    @pytest.mark.user(User.SELLER_TEST)
    def test_available_quick_search(self, create_organization_with_agreement_and_account) -> None:
        self.home_page.locators.HEADER_ACCOUNT_NUM.wait_to_be_visible()
        self.home_page.locators.HEADER_SUBSCRIBER.wait_to_be_visible()
        self.home_page.search_from_main_page(account_number=str(test_context.client.agreements[0].accounts[0].number))

    @allure.title("Быстрый поиск абонента с титульной строки оболочки (у пользователя достаточно прав)")
    @allure.id(676709)
    @pytest.mark.user(User.SELLER_TEST)
    def test_available_quick_subs_search(self, create_organization_with_agreement_and_account) -> None:
        self.client_inquiries_api.product_sale(inquiry=prepare_inquiries(category="internet"))
        self.home_page.locators.HEADER_ACCOUNT_NUM.wait_to_be_visible()
        self.home_page.locators.HEADER_SUBSCRIBER.wait_to_be_visible()
        self.home_page.search_from_main_page(subscriber=str(test_context.client.agreements[0].accounts[0].number))
