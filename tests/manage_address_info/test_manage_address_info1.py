import time

import allure
from playwright.sync_api import Page


@allure.epic("Управление адресной информацией")
class TestPlaywright:
    @allure.title("Добавление адреса. Ввод всех полей")
    def test_playwright_website(self, stand_login: Page):
        allure.id("525413")
        time.sleep(5)
        assert False
