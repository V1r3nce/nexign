import time

import allure

from pages.locators.dynamic_form_elements import DynamicForms, DynamicElements
from models.type_clients_models import data_individual, NOT_INPUT_FORMS
from playwright.sync_api import Page
from dataclasses import dataclass
from pages.base_page import BasePage
from pages.locators.home_page_elements import HomePage

@allure.severity(allure.severity_level.CRITICAL)
@dataclass
class PersonalAccountPage(BasePage):

    def __init__(self, page):
        super().__init__(page)


    @allure.step("Заполнить данные клиента ФЛ")
    def fill_data_for_individual_client(self):
        for key, value in data_individual.items():
            if key in NOT_INPUT_FORMS:
                self.page.locator(key).click()
                self.page.get_by_text(value).click()
            else:
                self.page.locator(key).click()
                self.page.fill(key, value)
                #TO DO
                #КОСТЫЛЬ ПЕРЕПИСАТЬ ПОЗЖЕ
                if key == DynamicElements.REGISTRATION_ADDRESS:
                    time.sleep(1)
                    self.page.keyboard.press("ArrowDown")
                    self.page.keyboard.press("ArrowDown")
                self.page.keyboard.press("Enter")
