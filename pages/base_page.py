from re import Pattern
from typing import Literal

import allure
from playwright.sync_api import Page, expect

from models.context import test_context
from pages.locators.base_elements import BaseElements


class BasePage:
    def __init__(self) -> None:
        self.page = test_context.page
        self.base_elements = BaseElements()

    @property
    def title(self) -> str:
        return self.page.title()

    @allure.step("Открыть страницу {url}")
    def open(
        self,
        url: str,
        timeout: int = 10000,
        wait: Literal["commit", "domcontentloaded", "load", "networkidle"] = None,
    ) -> None:
        self.page.goto(url, timeout=timeout, wait_until=wait)

    @allure.step("Ожидание состояния загрузки страницы '{state}'")
    def wait_for_state(
        self,
        state: Literal["domcontentloaded", "load", "networkidle"] = None,
        timeout: int = 10000,
    ) -> None:
        self.page.wait_for_load_state(state=state, timeout=timeout)

    @allure.step("Страница содержит title '{title}'")
    def expect_title(self, title: str | Pattern[str], timeout: int = 10000) -> None:
        expect(self.page).to_have_title(title, timeout=timeout)

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
        test_context.page_list.append(new_page)
        test_context.page = test_context.page_list[-1]
        return new_page

    @allure.step("Нажать на клавишу '{button}'")
    def press_keyboard_button(self, button: str) -> None:
        self.page.keyboard.press(button)

    @allure.step("Закрыть вкладку по индексу '{index}'")
    def close_page_by_index(self, index: int) -> None:
        pages = self.page.context.pages
        pages[index].close()

    @allure.step("Переключиться на вкладку '{name}'")
    def click_tab(self, name: str) -> None:
        self.base_elements.TAB.wait_for_text_in_all([name])
        tab_index = self.base_elements.TAB.text_list.index(name)
        self.base_elements.TAB.click(tab_index)

    @allure.step("Проверка: Цены соответствуют ожидаемым")
    def check_prices_match(
        self,
        expected_prices: float | list[float],
        actual_prices: list[float],
        original_prices: float | list[float] | None = None,
        price_tolerance: float = 0.01,
        check_old_price: bool = True,
        context_name: str = "",
    ) -> None:
        """
        Универсальный метод для проверки соответствия фактических цен ожидаемым.
        """
        if isinstance(expected_prices, (int, float)):
            expected_prices_list = [expected_prices]
        else:
            expected_prices_list = expected_prices

        for expected_price in expected_prices_list:
            assert any(abs(price - expected_price) < price_tolerance for price in actual_prices), (
                f"Ожидаемая цена {expected_price:.2f} не найдена {context_name}. Найдены цены: {actual_prices}"
            )

        if check_old_price and original_prices is not None:
            if isinstance(original_prices, (int, float)):
                original_prices_list = [original_prices]
            else:
                original_prices_list = original_prices

            for original_price in original_prices_list:
                assert any(abs(price - original_price) < price_tolerance for price in actual_prices), (
                    f"Зачеркнутая старая цена {original_price:.2f} не найдена {context_name}. "
                    f"Найдены цены: {actual_prices}"
                )
