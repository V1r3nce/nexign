from playwright.sync_api import Page

from pages.locators.base_elements import BaseElements
from pages.locators.ui_elements import Element


class LoginForm(BaseElements):
    def __init__(self, page: Page):
        super().__init__(page)
        self.TITLE = Element("h1", "Заголовок", self.page)
        self.LOGIN = Element("#login", "Логин", self.page)
        self.PASSWORD = Element("#password", "Пароль", self.page)
        self.SUBMIT = Element("#enterBtn", "Войти", self.page)
        self.LANGUAGE_SELECT = Element("#lang", "Язык", self.page)
        self.LOGOUT = Element("#logout", "Выйти", self.page)