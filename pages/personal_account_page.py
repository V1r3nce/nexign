import time
import allure
from pages.locators.dynamic_form_elements import DynamicElements, IndividualCustomerCreate, DynamicForms, Notifications
from models.type_clients_models import data_client, dropdown_fields, dynamic_elements
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

    @allure.step("Заполнить данные клиента ФЛ")
    def fill_data_client(self, type_client: str):
        data = data_client[type_client]
        for key, value in data.items():
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

    def click_create_customer(self, type_customer: str):
        if type_customer == 'individual':
            self.home_page.CREATE_CUSTOMER_BTN.click()
        elif type_customer == 'entrepreneur':
            self.home_page.CREATE_ENTREPRENEUR_BTN.click()
        elif type_customer == 'organisation':
            self.home_page.CREATE_ORG_BTN.click()

    @allure.step("Заполнить данные при создании договора")
    def fill_data_create_agreement(self, type_client: str):
        if type_client != 'individual':
            self.dynamic_elements.CLIENT_BANK_DETAILS_CHBX.click()
            self.dynamic_elements.CLIENT_BANK_CURRENT_ACCOUNT.fill('12345678900987654321')
            self.dynamic_elements.CLIENT_BANK.select_by_value('АО "Россельхозбанк", 044525111')
        self.dynamic_elements.OPERATOR_BANK_DETAILS.select_by_value(
            "СЕВЕРО-ЗАПАДНЫЙ БАНК ПАО СБЕРБАНК, 40702840109998965649")

    def check_related_person_by_context(self, type_context: str, **kwargs):
        if type_context == 'personal_account':
            self.locators.CURRENT_PERSONAL_ACCOUNT_LINK.click()
        elif type_context == 'agreement':
            self.locators.CURRENT_AGREEMENT_LINK.click()
        self.locators.RELATED_PERSONS_TAB.click()
        self.locators.FINISH_DATA_RELATED_PERSON_NAME.check_attribute_by_value(attribute='value', value=(kwargs.get('name_related_person') or 'Тестовое наименование'))



