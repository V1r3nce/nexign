from pages.locators.login_page import LoginFormElements
from pages.ui_elements import Element


class LoginFormPscElements(LoginFormElements):
    def __init__(self) -> None:
        super().__init__()
        self.PASSWORD = Element("#pwd", "Пароль")
