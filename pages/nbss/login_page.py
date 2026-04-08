import allure

from common.helpers.env_helper import BASE_URL, UserData
from common.helpers.time_helpers import delay
from pages.base_page import BasePage
from pages.locators.login_page import LoginFormElements


class LoginPage(BasePage):
    def __init__(self) -> None:
        super().__init__()

        self.locators = LoginFormElements()

    @allure.step("Авторизация через UI")
    def login(self, login: str = None, password: str = None) -> None:
        user_login = login or UserData.login
        user_password = password or UserData.password

        self.page.goto(BASE_URL)
        login_page = LoginFormElements()
        login_page.TITLE.wait_to_have_text("Nexign BSS", timeout=15000)
        delay(1, "Страница не успевает прогрузиться до конца")
        login_page.LOGIN.fill(user_login)
        self.page.locator(login_page.PASSWORD.path).click()
        self.page.keyboard.type(user_password)
        login_page.SUBMIT.element_have_css_color("background-color", "deep_blue")
        delay(0.5, "Кнопка без задержки иногда не срабатывает")
        login_page.SUBMIT.click()
