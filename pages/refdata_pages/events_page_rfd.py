import json

import allure
from playwright.sync_api import Page

from common.helpers.checker import assert_that
from pages.base_page import BasePage
from pages.locators.rfd_locators.events_element_rfd import EventsElementsRfd


class EventsPageRfd(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.locators = EventsElementsRfd(page)

    @allure.step("Проверка статуса События")
    def check_attribute_event(self, attribute: str, status: str) -> None:
        assert_that(
            lambda: json.loads(self.locators.DESCRIPTION_JSON.text.strip())[attribute] == status,
            message=f"Неверный статус события, ожидался {status}, а в результате {json.loads(self.locators.DESCRIPTION_JSON.text.strip())[attribute]}",
        )
