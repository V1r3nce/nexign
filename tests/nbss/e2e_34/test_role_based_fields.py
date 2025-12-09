import allure
import pytest

from common.enums.user import User
from pages.locators.nbss.home_page_elements import HomePage


@pytest.mark.regress
@pytest.mark.nbss_portal
@allure.epic("E2E_34 Поиск клиента/абонента")
@allure.suite("E2E_34 Поиск клиента/абонента")
@allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=674672853", name="Поиск клиента/абонента")
class TestRoleBasedFields:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login) -> None:
        self.home_page = HomePage()

    @pytest.mark.user(User.SP_MANAGER_TEST)
    @allure.title("Отображение поля Клиент бизнес - роль SP_MANAGER_TEST")
    @allure.id(681541)
    def test_check_customer_name_field(self) -> None:
        with allure.step("Проверка отображения поля 'Клиент'"):
            self.home_page.CUSTOMER_NAME.wait_to_be_visible(timeout=10000)

        with allure.step("Проверка возможности ввода в поле"):
            test_input = "Тестовый ввод"
            self.home_page.CUSTOMER_NAME.fill(test_input)
            self.home_page.CUSTOMER_NAME.to_have_value(test_input)

    @pytest.mark.user(User.SECURITY_TEST)
    @allure.title("Отображение полей Клиент, Лицевой счет, Абонент бизнес - роль SECURITY_TEST")
    @allure.id(681591)
    def test_check_all_search_fields(self) -> None:
        with allure.step("Проверка отображения поля 'Клиент'"):
            self.home_page.CUSTOMER_NAME.wait_to_be_visible(timeout=10000)
            test_customer = "Иванов Иван"
            self.home_page.CUSTOMER_NAME.fill(test_customer)
            self.home_page.CUSTOMER_NAME.to_have_value(test_customer)

        with allure.step("Проверка отображения поля 'Лицевой счёт'"):
            self.home_page.HEADER_ACCOUNT_NUM.wait_to_be_visible()
            test_account = "12345678"
            self.home_page.HEADER_ACCOUNT_NUM.fill(test_account)
            self.home_page.HEADER_ACCOUNT_NUM.to_have_value(test_account)

        with allure.step("Проверка отображения поля 'Абонент'"):
            self.home_page.HEADER_SUBSCRIBER.wait_to_be_visible()
            test_subscriber = "79001234567"
            self.home_page.HEADER_SUBSCRIBER.fill(test_subscriber)
            self.home_page.HEADER_SUBSCRIBER.to_have_value(test_subscriber)

        with allure.step("Проверка отображения кнопки 'Найти'"):
            self.home_page.HEADER_SEARCH_BTN.wait_to_be_visible()
            self.home_page.HEADER_SEARCH_BTN.wait_to_be_enabled()
