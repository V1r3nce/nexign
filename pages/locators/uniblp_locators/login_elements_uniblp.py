from pages.locators.uniblp_locators.base_elements_uniblp import BaseUniblpElements
from pages.ui_elements import Element


class LoginFormUniblpElements(BaseUniblpElements):
    def __init__(self) -> None:
        super().__init__()

        self.TITLE = Element("h1", "Заголовок")
        self.LOGIN = Element("input[name='login']", "Логин")
        self.PASSWORD = Element("input[name='password']", "Пароль")
        self.SUBMIT = Element("input[type='submit']", "Войти")
