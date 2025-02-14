import allure
from pages.locators.dynamic_form_elements import DynamicElements, IndividualCustomerCreate, DynamicForms, Notifications, \
    CreateEntrepreneur, CreateOrganization
from dataclasses import dataclass
from pages.base_page import BasePage
from pages.locators.home_page_elements import HomePage
from pages.locators.client_profile import ClientProfile


@dataclass
class PersonalAccountPage(BasePage):

    def __init__(self, page):
        super().__init__(page)
        self.locators = ClientProfile(page)
        self.home_page = HomePage(page)
        self.individual_customer_create_form = IndividualCustomerCreate(page)
        self.entrepreneur_create_form = CreateEntrepreneur(page)
        self.organization_create_form = CreateOrganization(page)
        self.dynamic_form = DynamicForms(page)
        self.dynamic_elements = DynamicElements(page)
        self.notifications = Notifications(page)

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
        self.locators.RELATED_PERSON_BENEFICIARY_NAME.check_attribute_by_value(attribute='value', value=(kwargs.get('name_related_person') or 'Тестовое наименование'))

    @allure.step("Создание клиента с типом {customer_type}")
    def create_customer_with_type(self, customer_type: str):
        match customer_type:
            case "individual":
                self.home_page.CREATE_CUSTOMER_BTN.click()
                self.individual_customer_create_form.fill_data_for_individual_client()
            case "entrepreneur":
                self.home_page.CREATE_ENTREPRENEUR_BTN.click()
                self.entrepreneur_create_form.fill_data_for_entrepreneur_client()
            case "organization":
                self.home_page.CREATE_ORG_BTN.click()
                self.organization_create_form.fill_data_for_organization_client()
            case _:
                raise ValueError(f"Неизвестный тип клиента {customer_type}")
