from playwright.sync_api import Page

from pages.locators.login_page import LoginForm
from pages.ui_elements import Element


class LoginFormRfd(LoginForm):
    def __init__(self, page: Page):
        super().__init__(page)
        self.PASSWORD = Element("#pwd", "Пароль", self.page)
