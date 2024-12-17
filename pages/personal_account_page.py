import time

import allure

from pages.locators.dynamic_form_elements import DynamicElements
from models.type_clients_models import data_individual, dropdown_fields
from dataclasses import dataclass
from pages.base_page import BasePage


@allure.severity(allure.severity_level.CRITICAL)
@dataclass
class PersonalAccountPage(BasePage):

    def __init__(self, page):
        super().__init__(page)


    @allure.step("Заполнить данные клиента ФЛ")
    def fill_data_for_individual_client(self):
        for key, value in data_individual.items():
            if key in dropdown_fields:
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
