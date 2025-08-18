from copy import deepcopy
from datetime import datetime
from random import choice

import allure
from playwright.sync_api import Page, expect

from common.helpers.string_helper import check_that_date_later
from pages.base_page import BasePage
from pages.locators.dynamic_form_elements import CreateTransition
from pages.locators.life_cycle_rules import LifeCircleRules


class LifeCycleRulesPage(BasePage):
    TIME_FOR_CREATE_TRANSITION = 5

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        self.locators = LifeCircleRules(page)
        self.create_transition = CreateTransition(page)

    @allure.step("Нажать на граф: {name}, Тип сущности={type_entity}, Базовое правило={is_default}")
    def click_graph_with(self, name: str = "", type_entity: str = "", is_default: bool = False) -> None:
        self.locators.GRAPHS_LIST.wait_to_be_visible(timeout=10000)
        graph_count = self.locators.GRAPHS_LIST.elements_len()
        for graph_index in range(graph_count):
            graph_text = self.locators.GRAPHS_LIST[graph_index].text
            if f"{name}Тип сущности: {type_entity}" in graph_text and ("Базовое правило" in graph_text) == is_default:
                self.locators.GRAPHS_LIST.click(graph_index)
                break

    @allure.step(
        "Нажать на переход: {from_status} ➜ {to_status} Приоритет={priority} Возможен ручной запуск={is_manual}"
    )
    def click_transition_with(
        self, from_status: str = "", to_status: str = "", priority: str = "", is_manual: bool = False
    ) -> None:
        self.locators.TRANSITIONS_LIST.wait_to_be_visible()
        for transition in self.locators.TRANSITIONS_LIST:
            if (
                f"{from_status} ➜ {to_status}" in transition.text
                and f"Приоритет: {priority}" in transition.text
                and ("Возможен ручной запуск" in transition.text) == is_manual
            ):
                transition.click()

    @allure.step("Проверить данные о переходе: Дата создания {expected_date}, Создал {user}, Связанное событие {event}")
    def check_info_about_transition(self, expected_date: datetime = None, user: str = "", event: str = "") -> None:
        self.locators.CREATE_INFO.wait_to_have_count(3)
        if expected_date is not None:
            check_that_date_later(self.locators.CREATE_INFO[0], expected_date, self.TIME_FOR_CREATE_TRANSITION)
        self.locators.CREATE_INFO[1].to_contain_text(user)
        self.locators.CREATE_INFO[2].to_contain_text(event)

    @allure.step("Получить количество действующих переходов для правила")
    def count_transitions(self) -> int:
        expect(
            self.page.locator(self.locators.ADD_FIRST_TRANSITION_BTN.path)
            .or_(self.page.locator(self.locators.TRANSITIONS_LIST.path))
            .or_(self.page.locator(self.locators.NO_TRANSITIONS_MESSAGE.path))
            .first
        ).to_be_visible(timeout=15000)
        return self.locators.TRANSITIONS_LIST.elements_len()

    @allure.step("Нажать на кнопку создания перехода")
    def click_add_transition_button(self) -> None:
        if self.page.locator(self.locators.ADD_FIRST_TRANSITION_BTN.path).is_visible():
            self.locators.ADD_FIRST_TRANSITION_BTN.click()
        else:
            self.locators.ADD_TRANSITION_BTN.click()

    @allure.step("Выбрать рандомные исходный и конечный статусы для будущего перехода")
    def choice_statuses(self, statuses: set, initial_status: str, final_status: str) -> tuple[str, str]:
        """
        Выбрать рандомные исходный и конечный статусы для будущего перехода, удовлетворяющие условиям:
        * Исходный и Следующий статус не должны совпадать
        * Исходный статус не должен совпадать с финальным статусом выбранного графа
        * Следующий статус не должен совпадать с начальным статусом выбранного графа
        """
        allowed_from_statuses = deepcopy(statuses)
        allowed_from_statuses.discard(final_status)
        random_from_status = choice(tuple(allowed_from_statuses))

        allowed_to_statuses = deepcopy(statuses)
        allowed_to_statuses.discard(initial_status)
        allowed_to_statuses.discard(random_from_status)
        random_to_status = choice(tuple(allowed_to_statuses))
        return random_from_status, random_to_status
