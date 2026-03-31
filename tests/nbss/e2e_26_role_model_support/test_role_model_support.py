import allure
import pytest

from common.enums.user import User
from common.helpers.env_helper import BASE_URL, UserData
from pages.nbss.home_page import HomePage
from pages.nbss.login_page import LoginPage


@allure.epic("E2E_26 Поддержка ролевой модели (группы)")
@allure.suite("E2E_26 Поддержка ролевой модели (группы)")
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestRoleModelSupport:
    @pytest.fixture(autouse=True)
    def setup(self, page) -> None:
        self.link = f"{BASE_URL}common-faults-list/all"
        self.fake_link = f"{BASE_URL}dasqw/aewdsa/wasdq123"
        self.login_page = LoginPage()
        self.home_page = HomePage()

    @allure.title("01. Открытие ЭФ (не авторизован)")
    @allure.id(762431)
    def test_open_portal_check_login_form(self, stand_login_nbss_without_auth):
        self.login_page.locators.LOGIN.wait_to_be_visible()
        self.login_page.locators.PASSWORD.wait_to_be_visible()
        self.login_page.locators.SUBMIT.wait_to_be_visible()

    @allure.title("02. Открытие ЭФ (не авторизован, неверный ввод данных)")
    @allure.id(762452)
    def test_check_login_form_error(self, stand_login_nbss_without_auth):
        self.login_page.locators.LOGIN.type("abc")
        self.login_page.locators.PASSWORD.type("qazxswedc")
        self.login_page.locators.SUBMIT.wait_to_be_enabled()
        self.login_page.locators.SUBMIT.click()
        self.login_page.locators.ERROR_MESSAGE.wait_to_have_text("Неверно указаны логин или пароль пользователя")

    @allure.title("03. Открытие ЭФ (есть права)")
    @allure.id(762450)
    def test_check_login_form_success(self, stand_login_nbss_without_auth):
        self.login_page.locators.LOGIN.type(UserData.login)
        self.login_page.locators.PASSWORD.type(UserData.password)
        self.login_page.locators.SUBMIT.wait_to_be_enabled()
        self.login_page.locators.SUBMIT.click()
        self.home_page.locators.WIDGETS.wait_to_be_visible(timeout=25000)

    @allure.title("04. Открытие ЭФ (нет прав)")
    @allure.id(762451)
    @pytest.mark.user(User.SECURITY_TEST)
    def test_check_not_access(self, nexign_stand_login):
        self.home_page.open(self.link)
        self.home_page.locators.MODAL.wait_to_be_visible(timeout=15000)

    @allure.title("05. Открытие ЭФ (некорректная ссылка)")
    @allure.id(762453)
    def test_check_error_404_message(self, nexign_stand_login):
        self.home_page.open(self.fake_link)
        self.home_page.locators.DESCRIPTION_MESSAGE_404_ERROR.wait_to_have_text(
            "Страница не существует или у вас нет к ней доступа", timeout=15000
        )
