from pages.locators.base_elements import BaseElements
from pages.ui_elements import Element


class LoginFormElements(BaseElements):
    def __init__(self) -> None:
        super().__init__()
        self.TITLE = Element("h1", "Заголовок")
        self.LOGIN = Element("#login", "Логин")
        self.PASSWORD = Element("#pwd, #password", "Пароль")
        self.SUBMIT = Element("#enterBtn", "Войти")
        self.LANGUAGE_SELECT = Element("#lang", "Язык")
        self.LOGOUT = Element("#logout", "Выйти")
        self.ERROR_MESSAGE = Element("#error_message", "Сообщение об ошибке")
