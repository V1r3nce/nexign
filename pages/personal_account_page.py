from typing import Any, Union

import allure
from playwright.sync_api import Page

from models.user import EntrepreneurClient, IndividualClient, OrganizationClient
from pages.base_page import BasePage
from pages.locators.client_profile import ClientProfile
from pages.locators.dynamic_form_elements import (
    CreateEntrepreneur,
    CreateOrganization,
    DynamicElements,
    DynamicForms,
    IndividualCustomerCreate,
)
from pages.locators.home_page_elements import HomePage


class PersonalAccountPage(BasePage):
    def __init__(self, page: Page, user_data: Union[EntrepreneurClient, IndividualClient, OrganizationClient] = None):
        super().__init__(page)
        self.locators = ClientProfile(page)
        self.home_page = HomePage(page)
        self.individual_customer_create_form = IndividualCustomerCreate(page)
        self.entrepreneur_create_form = CreateEntrepreneur(page)
        self.organization_create_form = CreateOrganization(page)
        self.dynamic_form = DynamicForms(page)
        self.dynamic_elements = DynamicElements(page)
        self.user_data = user_data

    @allure.step("Заполнить данные при создании договора")
    def fill_data_create_agreement(self, type_client: str) -> None:
        if type_client != "individual":
            self.dynamic_elements.CLIENT_BANK_DETAILS_CHBX.click()
            self.dynamic_elements.CLIENT_BANK_CURRENT_ACCOUNT.fill(self.user_data.bank_account)
            self.dynamic_elements.CLIENT_BANK.select_by_value(self.user_data.bank_name)
        self.dynamic_elements.OPERATOR_BANK_DETAILS.select_by_value(self.user_data.operator_bank_details)

    def check_related_person_by_context(self, type_context: str, **kwargs: Any) -> None:
        if type_context == "personal_account":
            self.locators.CURRENT_PERSONAL_ACCOUNT_LINK.click()
        elif type_context == "agreement":
            self.locators.CURRENT_AGREEMENT_LINK.click()
        self.locators.RELATED_PERSONS_TAB.click()
        self.locators.RELATED_PERSON_BENEFICIARY_NAME.check_attribute_by_value(
            attribute="value", value=self.user_data.name_related_person
        )

    @allure.step("Создание клиента с типом {customer_type}")
    def create_customer_with_type(self, customer_type: str) -> None:
        match customer_type:
            case "individual":
                self.home_page.CREATE_CUSTOMER_BTN.click()
                self.individual_customer_create_form.fill_data_for_individual_client(user_data=self.user_data)
            case "entrepreneur":
                self.home_page.CREATE_ENTREPRENEUR_BTN.click()
                self.entrepreneur_create_form.fill_data_for_entrepreneur_client(user_data=self.user_data)
            case "organization":
                self.home_page.CREATE_ORG_BTN.click()
                self.organization_create_form.fill_data_for_organization_client(user_data=self.user_data)
            case _:
                raise ValueError(f"Неизвестный тип клиента {customer_type}")
