from playwright.sync_api import Page

from pages.locators.lis_locators.base_elements_lis import BaseElementsLis
from pages.ui_elements import Element


class LoginFormLis(BaseElementsLis):

    def __init__(self, page: Page):
        super().__init__(page)

        self.TITLE = Element("h1", "Заголовок", self.page)
        self.LOGIN = Element("#login", "Логин", self.page)
        self.PASSWORD = Element("#pwd", "Пароль", self.page)
        self.SUBMIT = Element("#enterBtn", "Войти", self.page)
