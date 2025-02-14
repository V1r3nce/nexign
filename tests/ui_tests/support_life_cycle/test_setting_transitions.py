from datetime import datetime

import allure
import pytest
from playwright.sync_api import Page

from api.requests.life_cycle_rules_requests import LifeCycleRulesRequests
from common.helpers.env_helper import UserData
from pages.life_cycle_rules_page import LifeCycleRulesPage


@pytest.mark.usefixtures("nexign_ui_stand_login")
class TestSettingTransitions:
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.life_cycle_rules_page = LifeCycleRulesPage(page)
        self.life_cycle_rules_requests = LifeCycleRulesRequests(page)

    @allure.suite("E2E_29 Поддержка жизненного цикла")
    @allure.sub_suite("Настройка переходов")
    @allure.title("Настройка перехода ЖЦ сущности")
    @allure.tag("CAN_AUTH", "SUCCESS")
    @allure.description("Создание перехода между ЖЦ статусами сущности для вызова сторонними системами (посредством AMQP, HTTP)")
    @allure.id(479065)
    def test_setting_transition(self, page: Page, base_url: str):
        graph = self.life_cycle_rules_requests.get_info_about_default_graph()
        statuses = self.life_cycle_rules_requests.get_statuses()
        from_status, to_status = self.life_cycle_rules_page.choice_statuses(statuses, graph.initial_status,
                                                                            graph.final_status)
        priority = 1
        event = self.life_cycle_rules_requests.get_events_names()[0]

        with allure.step('Зайти в форму "Правила ЖЦ сущностей"'):
            page.goto(f"{base_url}nlm/rules-list")

        with allure.step('Выбрать граф для которого будет создан переход'):
            self.life_cycle_rules_page.click_graph_with(name=graph.name, is_default=True)
            start_count_transition = self.life_cycle_rules_page.count_transitions()

        with allure.step('Нажать на форме кнопку "+ Создать"'):
            self.life_cycle_rules_page.click_add_transition_button()
            self.life_cycle_rules_page.create_transition.FORM.to_be_enabled()
            self.life_cycle_rules_page.create_transition.ACTIVE_ADD_TRANSITION_BTN.not_to_be_visible()

        with allure.step('Заполнить форму "Создание Перехода"'):
            with allure.step(f'Выбрать Исходный статус {from_status}, Конечный статус {to_status}'):
                self.life_cycle_rules_page.create_transition.FROM_STATUS.select_by_value(from_status)
                self.life_cycle_rules_page.create_transition.TO_STATUS.select_by_value(to_status)
            with allure.step(f'Выбрать Приоритет выполнения перехода'):
                priority = self.life_cycle_rules_page.create_transition.fill_priority(priority)
            with allure.step(f'Выбрать событие для перехода {event}'):
                self.life_cycle_rules_page.create_transition.EVENT.select_by_value(event)
            self.life_cycle_rules_page.create_transition.ACTIVE_ADD_TRANSITION_BTN.to_be_enabled()

        with allure.step('Нажать на кнопку "Добавить"'):
            self.life_cycle_rules_page.create_transition.ACTIVE_ADD_TRANSITION_BTN.click()
            create_date = datetime.now()
            self.life_cycle_rules_page.create_transition.FORM.not_to_be_visible()
            page.reload()
            assert self.life_cycle_rules_page.count_transitions() == start_count_transition + 1, "Количество переходов правила должно увеличиться на 1"

        with allure.step('Выбрать созданный нами переход'):
            self.life_cycle_rules_page.click_transition_with(from_status=from_status, to_status=to_status,
                                                             priority=priority)

        with allure.step('Проверить атрибуты перехода'):
            self.life_cycle_rules_page.locators.TRANSITION_INFO.wait_to_be_visible()
            self.life_cycle_rules_page.locators.TRANSITION_STATUS.to_contain_text("Активен")
            self.life_cycle_rules_page.locators.MANUAL_START_STATUS.not_to_be_visible()
            self.life_cycle_rules_page.check_info_about_transition(expected_date=create_date,
                                                                   user=UserData.login, event=event)
            self.life_cycle_rules_page.locators.CONDITIONALS_BTN.click()
            self.life_cycle_rules_page.locators.CONDITIONALS.not_to_be_visible()
            self.life_cycle_rules_page.locators.ACTIONS_BTN.click()
            self.life_cycle_rules_page.locators.ACTIONS.not_to_be_visible()

    @allure.suite("E2E_29 Поддержка жизненного цикла")
    @allure.sub_suite("Настройка переходов")
    @allure.title("Настройка ручного перехода ЖЦ сущности")
    @allure.tag("CAN_AUTH", "SUCCESS")
    @allure.description("Создание перехода между ЖЦ статусами сущности для вызова в GUI")
    @allure.id(479242)
    def test_setting_manual_transition(self, page: Page, base_url: str):
        graph = self.life_cycle_rules_requests.get_info_about_default_graph()
        statuses = self.life_cycle_rules_requests.get_statuses()
        from_status, to_status = self.life_cycle_rules_page.choice_statuses(statuses, graph.initial_status,
                                                                            graph.final_status)
        priority = 1
        event = self.life_cycle_rules_requests.get_events_names()[0]

        with allure.step('Зайти в форму "Правила ЖЦ сущностей"'):
            page.goto(f"{base_url}nlm/rules-list")

        with allure.step('Выбрать граф для которого будет создан переход'):
            self.life_cycle_rules_page.click_graph_with(name=graph.name, is_default=True)
            start_count_transition = self.life_cycle_rules_page.count_transitions()

        with allure.step('Нажать на форме кнопку "+ Создать"'):
            self.life_cycle_rules_page.click_add_transition_button()
            self.life_cycle_rules_page.create_transition.FORM.to_be_enabled()
            self.life_cycle_rules_page.create_transition.ACTIVE_ADD_TRANSITION_BTN.not_to_be_visible()

        with allure.step('Заполнить форму "Создание Перехода"'):
            with allure.step(f'Выбрать Исходный статус {from_status}, Конечный статус {to_status}'):
                self.life_cycle_rules_page.create_transition.FROM_STATUS.select_by_value(from_status)
                self.life_cycle_rules_page.create_transition.TO_STATUS.select_by_value(to_status)
            with allure.step(f'Выбрать Приоритет выполнения перехода'):
                priority = self.life_cycle_rules_page.create_transition.fill_priority(priority)
            with allure.step('Нажать галочку Ручной запуск перехода'):
                self.life_cycle_rules_page.create_transition.IS_MANUAL_CHECKBOX.click()
            with allure.step(f'Выбрать событие для перехода {event}'):
                self.life_cycle_rules_page.create_transition.EVENT.select_by_value(event)
            self.life_cycle_rules_page.create_transition.ACTIVE_ADD_TRANSITION_BTN.to_be_enabled()

        with allure.step('Нажать на кнопку "Добавить"'):
            self.life_cycle_rules_page.create_transition.ACTIVE_ADD_TRANSITION_BTN.click()
            create_date = datetime.now()
            self.life_cycle_rules_page.create_transition.FORM.not_to_be_visible()
            assert self.life_cycle_rules_page.count_transitions() == start_count_transition + 1, "Количество переходов правила должно увеличиться на 1"

        with allure.step('Выбрать созданный нами переход'):
            self.life_cycle_rules_page.click_transition_with(from_status=from_status, to_status=to_status,
                                                             priority=priority, is_manual=True)

        with allure.step('Проверить атрибуты перехода'):
            self.life_cycle_rules_page.locators.TRANSITION_INFO.wait_to_be_visible()
            self.life_cycle_rules_page.locators.TRANSITION_STATUS.to_contain_text("Активен")
            self.life_cycle_rules_page.locators.MANUAL_START_STATUS.wait_to_be_visible()
            self.life_cycle_rules_page.check_info_about_transition(expected_date=create_date,
                                                                   user=UserData.login, event=event)
            self.life_cycle_rules_page.locators.CONDITIONALS_BTN.click()
            self.life_cycle_rules_page.locators.CONDITIONALS.not_to_be_visible()
            self.life_cycle_rules_page.locators.ACTIONS_BTN.click()
            self.life_cycle_rules_page.locators.ACTIONS.not_to_be_visible()
