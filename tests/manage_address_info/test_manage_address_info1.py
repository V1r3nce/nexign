import time

import allure
from playwright.sync_api import Page


@allure.epic("Управление адресной информацией")
class TestPlaywright:
    @allure.title("Добавление адреса. Ввод всех полей")
    def test_playwright_website(self, get_start_page: Page):
        allure.id("525413")
        time.sleep(5)
        assert False
