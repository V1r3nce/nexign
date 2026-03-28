from pages.locators.login_page import LoginFormElements
from pages.ui_elements import Element


class LoginFormGrafanaElements(LoginFormElements):
    def __init__(self) -> None:
        super().__init__()
        self.LOGIN = Element("input[data-testid*=Username]", "Логин")
        self.PASSWORD = Element("input[data-testid*=Password]", "Пароль")
        self.LOGIN_BTN = Element("button[data-testid*=Login]", "Кнопка 'Войти'")
        self.SKIP_BTN = Element("button[data-testid*=Skip]", "Кнопка 'Пропустить'")
