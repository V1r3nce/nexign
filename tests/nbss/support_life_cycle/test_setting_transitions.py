import allure
import pytest
from playwright.sync_api import Page

from api.nbss.life_cycle_rules_requests import GraphInfo, LifeCycleRulesRequests
from common.helpers.checker import assert_that
from common.helpers.env_helper import UserData
from common.helpers.time_helpers import get_current_moscow_datetime
from pages.nbss.life_cycle_rules_page import LifeCycleRulesPage


@allure.suite("E2E_29 Поддержка жизненного цикла")
@allure.sub_suite("Настройка переходов")
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestSettingTransitions:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_ui_stand_login: Page, add_and_cancel_graph: GraphInfo) -> None:
        self.life_cycle_rules_page = LifeCycleRulesPage(nexign_ui_stand_login)
        self.life_cycle_rules_requests = LifeCycleRulesRequests(nexign_ui_stand_login)
        self.graph = add_and_cancel_graph
        statuses = self.life_cycle_rules_requests.get_statuses()
        self.from_status, self.to_status = self.life_cycle_rules_page.choice_statuses(
            statuses, self.graph.initial_status, self.graph.final_status
        )
        self.priority = 1
        self.event = self.life_cycle_rules_requests.get_events_names()[0]

    @allure.title("Настройка перехода ЖЦ сущности")
    @allure.description(
        "Создание перехода между ЖЦ статусами сущности для вызова сторонними системами (посредством AMQP, HTTP)"
    )
    @allure.id(479065)
    def test_setting_transition(self, page: Page, base_url: str) -> None:
        with allure.step("Выбрать граф для которого будет создан переход"):
            self.life_cycle_rules_page.open(f"{base_url}nlm/rules")
            self.life_cycle_rules_page.click_graph_with(name=self.graph.name)
            start_count_transition = self.life_cycle_rules_page.count_transitions()

        with allure.step('Нажать на форме кнопку "+ Создать"'):
            self.life_cycle_rules_page.click_add_transition_button()
            self.life_cycle_rules_page.create_transition.FORM.to_be_enabled()
            self.life_cycle_rules_page.create_transition.ACTIVE_ADD_TRANSITION_BTN.not_to_be_enabled()

        with allure.step('Заполнить форму "Создание Перехода"'):
            self.life_cycle_rules_page.create_transition.FROM_STATUS.select_by_value(self.from_status)
            self.life_cycle_rules_page.create_transition.TO_STATUS.select_by_value(self.to_status)
            self.priority = self.life_cycle_rules_page.create_transition.fill_priority(self.priority)
            self.life_cycle_rules_page.create_transition.EVENT.select_by_value(self.event)
            self.life_cycle_rules_page.create_transition.ACTIVE_ADD_TRANSITION_BTN.to_be_enabled()

        with allure.step('Нажать на кнопку "Добавить"'):
            self.life_cycle_rules_page.create_transition.ACTIVE_ADD_TRANSITION_BTN.click()
            create_date = get_current_moscow_datetime()
            self.life_cycle_rules_page.create_transition.FORM.not_to_be_visible()
            self.life_cycle_rules_page.refresh_page("domcontentloaded")
            assert_that(
                lambda: self.life_cycle_rules_page.count_transitions() == start_count_transition + 1,
                "Количество переходов правила должно увеличиться на 1",
            )

        self.life_cycle_rules_page.click_transition_with(
            from_status=self.from_status, to_status=self.to_status, priority=self.priority
        )

        with allure.step("Проверить атрибуты перехода"):
            self.life_cycle_rules_page.locators.TRANSITION_INFO.wait_to_be_visible()
            self.life_cycle_rules_page.locators.TRANSITION_STATUS.to_contain_text("Активен")
            self.life_cycle_rules_page.locators.MANUAL_START_STATUS.not_to_be_visible()
            self.life_cycle_rules_page.check_info_about_transition(
                expected_date=create_date, user=UserData.login, event=self.event
            )
            self.life_cycle_rules_page.locators.CONDITIONALS_BTN.click()
            self.life_cycle_rules_page.locators.CONDITIONALS.not_to_be_visible()
            self.life_cycle_rules_page.locators.ACTIONS_BTN.click()
            self.life_cycle_rules_page.locators.ACTIONS.not_to_be_visible()

    @allure.title("Настройка ручного перехода ЖЦ сущности")
    @allure.description("Создание перехода между ЖЦ статусами сущности для вызова в GUI")
    @allure.id(479242)
    def test_setting_manual_transition(self, page: Page, base_url: str) -> None:
        with allure.step("Выбрать граф для которого будет создан переход"):
            self.life_cycle_rules_page.open(f"{base_url}nlm/rules")
            self.life_cycle_rules_page.click_graph_with(name=self.graph.name)
            start_count_transition = self.life_cycle_rules_page.count_transitions()

        with allure.step('Нажать на форме кнопку "+ Создать"'):
            self.life_cycle_rules_page.click_add_transition_button()
            self.life_cycle_rules_page.create_transition.FORM.to_be_enabled()
            self.life_cycle_rules_page.create_transition.ACTIVE_ADD_TRANSITION_BTN.not_to_be_enabled()

        with allure.step('Заполнить форму "Создание Перехода"'):
            self.life_cycle_rules_page.create_transition.FROM_STATUS.select_by_value(self.from_status)
            self.life_cycle_rules_page.create_transition.TO_STATUS.select_by_value(self.to_status)
            self.priority = self.life_cycle_rules_page.create_transition.fill_priority(self.priority)
            self.life_cycle_rules_page.create_transition.IS_MANUAL_CHECKBOX.click()
            self.life_cycle_rules_page.create_transition.EVENT.select_by_value(self.event)
            self.life_cycle_rules_page.create_transition.ACTIVE_ADD_TRANSITION_BTN.to_be_enabled()

        with allure.step('Нажать на кнопку "Добавить"'):
            self.life_cycle_rules_page.create_transition.ACTIVE_ADD_TRANSITION_BTN.click()
            create_date = get_current_moscow_datetime()
            self.life_cycle_rules_page.create_transition.FORM.not_to_be_visible()
            self.life_cycle_rules_page.refresh_page("domcontentloaded")
            assert_that(
                lambda: self.life_cycle_rules_page.count_transitions() == start_count_transition + 1,
                "Количество переходов правила должно увеличиться на 1",
            )

        self.life_cycle_rules_page.click_transition_with(
            from_status=self.from_status, to_status=self.to_status, priority=self.priority, is_manual=True
        )

        with allure.step("Проверить атрибуты перехода"):
            self.life_cycle_rules_page.locators.TRANSITION_INFO.wait_to_be_visible()
            self.life_cycle_rules_page.locators.TRANSITION_STATUS.to_contain_text("Активен")
            self.life_cycle_rules_page.locators.MANUAL_START_STATUS.wait_to_be_visible()
            self.life_cycle_rules_page.check_info_about_transition(
                expected_date=create_date, user=UserData.login, event=self.event
            )
            self.life_cycle_rules_page.locators.CONDITIONALS_BTN.click()
            self.life_cycle_rules_page.locators.CONDITIONALS.not_to_be_visible()
            self.life_cycle_rules_page.locators.ACTIONS_BTN.click()
            self.life_cycle_rules_page.locators.ACTIONS.not_to_be_visible()
