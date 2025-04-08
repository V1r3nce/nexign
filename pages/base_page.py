from dataclasses import dataclass
from typing import Literal

import allure
from playwright.sync_api import Page, expect

from pages.locators.base_elements import BaseElements


@dataclass
class BasePage:
    def __init__(self, page: Page):
        self.page = page
        self.base_elements = BaseElements(page)

    @allure.step("Открыть страницу {url}")
    def open(self, url: str) -> None:
        self.page.goto(url)

    @allure.step("Страница содержит title '{title}'")
    def expect_title(self, title: str) -> None:
        expect(self.page).to_have_title(title)

    @allure.step("Страница содержит text '{text}'")
    def expect_text(self, text: str) -> None:
        assert self.page.get_by_text(text).is_visible()

    @allure.step("Страница содержит URL '{url}'")
    def expect_url(self, url: str) -> None:
        expect(self.page).to_have_url(url)

    @allure.step("Получить customerId из URL страницы")
    def get_customer_id_from_url(self) -> int:
        return int(self.page.url.split("/")[-2])

    def bring_to_front(self, title: str) -> None:
        with allure.step(f"Сделать вкладку '{title}' активной"):
            self.page.bring_to_front()

    @allure.step("Обновить страницу")
    def refresh_page(self, wait: Literal["commit", "domcontentloaded", "load", "networkidle"]) -> None:
        self.page.reload(wait_until=wait)

    @allure.step("Открыть новую вкладку")
    def open_new_tab(self) -> Page:
        new_page = self.page.context.new_page()
        return new_page

    @allure.step("Нажать на клавишу '{button}'")
    def press_keyboard_button(self, button: str) -> None:
        self.page.keyboard.press(button)

    @allure.step("Закрыть вкладку по индексу '{index}'")
    def close_page_by_index(self, index: int) -> None:
        pages = self.page.context.pages
        pages[index].close()
