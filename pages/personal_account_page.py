from pages.locators.dynamic_form_elements import DynamicElements, IndividualCustomerCreate, DynamicForms, Notifications
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
        self.fl_customer_create = IndividualCustomerCreate(page)
        self.dynamic_form = DynamicForms(page)
        self.dynamic_elements = DynamicElements(page)
        self.notifications = Notifications(page)