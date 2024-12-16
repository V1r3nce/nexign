import time

import allure

from playwright.sync_api import Page
from dataclasses import dataclass

from pages.locators.client_profile import ClientProfile
from pages.locators.dynamic_form_elements import AddAddress


@allure.severity(allure.severity_level.CRITICAL)
@allure.story("Client Profile")
@dataclass
class ClientProfilePage:
    def __init__(self, page: Page):
        self.page = page
        self.locators = ClientProfile(page)
        self.add_address_element = AddAddress(page)

    @allure.step("Перейти во вкладку 'Клиент'")
    def click_client_tab(self):
        self.locators.CLIENT_TAB.wait_to_be_visible()
        self.locators.CLIENT_TAB.click()

    @allure.step("Выбрать Тип адреса '{0}' c названием {name}")
    def choose_option_with_name(self, name: str):
        time.sleep(1)
        self.add_address_element.ADDRESS_TYPE_OPTIONS.wait_elements_visible(element_index=0)
        for item in range(self.add_address_element.ADDRESS_TYPE_OPTIONS.elements_len()):
            if self.add_address_element.ADDRESS_TYPE_OPTIONS.get_text(element_index=item) == name:
                self.add_address_element.ADDRESS_TYPE_OPTIONS.click(element_index=item)
