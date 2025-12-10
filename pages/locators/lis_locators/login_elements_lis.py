from pages.locators.lis_locators.base_elements_lis import BaseLisElements
from pages.ui_elements import Element


class LoginFormLisElements(BaseLisElements):
    def __init__(self) -> None:
        super().__init__()

        self.TITLE = Element("h1", "Заголовок")
        self.LOGIN = Element("#login", "Логин")
        self.PASSWORD = Element("#pwd", "Пароль")
        self.SUBMIT = Element("#enterBtn", "Войти")
