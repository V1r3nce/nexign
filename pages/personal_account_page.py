import time
import allure
from pages.locators.dynamic_form_elements import DynamicElements, FlCustomerCreate, DynamicForms, Notifications
from models.type_clients_models import data_individual, dropdown_fields, dynamic_elements
from dataclasses import dataclass
from pages.base_page import BasePage
from pages.locators.home_page_elements import HomePage
from pages.locators.personal_account_page_elements import PersonalAccountElements


@dataclass
class PersonalAccountPage(BasePage):

    def __init__(self, page):
        super().__init__(page)

        self.locators = PersonalAccountElements(page)
        self.home_page = HomePage(page)
        self.fl_customer_create = FlCustomerCreate(page)
        self.dynamic_form = DynamicForms(page)
        self.dynamic_elements = DynamicElements(page)
        self.notifications = Notifications(page)



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
                if key == dynamic_elements.REGISTRATION_ADDRESS.path:
                    time.sleep(1)
                    self.page.keyboard.press("ArrowDown")
                    self.page.keyboard.press("ArrowDown")
                self.page.keyboard.press("Enter")

