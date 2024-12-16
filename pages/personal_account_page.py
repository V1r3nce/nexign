import time

import allure

from pages.locators.dynamic_form_elements import DynamicForms
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

    @allure.step("Нажать кнопку 'Создать клиента ФЛ'")
    def click_button_create_client(self):
        self.page.locator(HomePage.CREATE_CUSTOMER_BTN).click()
        time.sleep(1)

    @allure.step("Заполнить данные клиента ФЛ")
    def fill_data_for_individual_client(self):
        for key, value in data_individual.items():
            if key in NOT_INPUT_FORMS:
                self.page.locator(key).click()
                self.page.get_by_text(value).click()
            else:
                self.page.locator(key).click()
                self.page.fill(key, value)
                self.page.keyboard.press("Enter")

    @allure.step("Нажать кнопку 'Сохранить клиента ФЛ'")
    def click_button_save_client(self):
        self.page.locator(DynamicForms.SAVE_BTN).click()