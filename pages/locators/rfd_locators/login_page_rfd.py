from pages.locators.login_page import LoginForm
from pages.ui_elements import Element


class LoginFormRfd(LoginForm):
    def __init__(self) -> None:
        super().__init__()
        self.PASSWORD = Element("#pwd", "Пароль")
