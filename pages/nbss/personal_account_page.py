import re
from typing import Union

import allure

from common.helpers.string_helper import check_price
from models.context import test_context
from models.user import EntrepreneurClient, IndividualClient, OrganizationClient
from pages.base_page import BasePage
from pages.locators.nbss.client.client_profile import ClientProfileElements
from pages.locators.nbss.dynamic_form_elements import (
    CreateEntrepreneur,
    CreateOrganization,
    DynamicElements,
    DynamicForms,
    IndividualCustomerCreate,
    PersonalAccountForm,
)
from pages.locators.nbss.home_page_elements import HomePageElements


class PersonalAccountPage(BasePage):
    def __init__(self, user_data: Union[EntrepreneurClient, IndividualClient, OrganizationClient] = None):
        super().__init__()
        self.locators = ClientProfileElements()
        self.home_page = HomePageElements()
        self.individual_customer_create_form = IndividualCustomerCreate()
        self.entrepreneur_create_form = CreateEntrepreneur()
        self.organization_create_form = CreateOrganization()
        self.dynamic_form = DynamicForms()
        self.dynamic_elements = DynamicElements()
        self.personal_account_form = PersonalAccountForm()
        self.user_data = user_data

    @allure.step("Заполнить данные при создании договора")
    def fill_data_create_agreement(self, type_client: str) -> None:
        if type_client != "individual":
            self.dynamic_elements.CLIENT_BANK_DETAILS_CHBX.click()
            self.dynamic_elements.CLIENT_BANK_CURRENT_ACCOUNT.fill(self.user_data.bank_account)
            self.dynamic_elements.CLIENT_BANK.select_by_value(self.user_data.bank_name)
        self.dynamic_elements.OPERATOR_BANK_DETAILS.select_by_value(self.user_data.operator_bank_details)
        self.dynamic_elements.OPERATOR_AGENT_FIO.select_by_value("Иванович Иван Иванов")

    def check_related_person_by_context(self, type_context: str) -> None:
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
        test_context.client_list.append(self.user_data)
        test_context.client = self.user_data

    def check_personal_account_data(
        self,
        account_number: int | None = None,
        payment_method: str | None = None,
        threshold_control: str | None = None,
        threshold_break: str | None = None,
        check_tabs: bool = True,
    ) -> None:
        if check_tabs:
            self.locators.PERSONAL_ACCOUNT_STATUS.wait_to_have_text("Действующий")
            self.locators.PROPERTIES_TAB.check_attribute_by_value("class", re.compile(r".*active.*"))
        if account_number:
            self.locators.CLIENT_FIO.wait_to_have_text(f"Лицевой счет: {account_number}")
        if payment_method:
            self.locators.PAYMENT_METHOD_FLD.wait_to_have_text(payment_method)
        if threshold_control:
            self.locators.THRESHOLD_CONTROL.wait_to_have_text(threshold_control)
        if threshold_break:
            check_price(self.locators.THRESHOLD_BREAK, float(threshold_break), False)

    def add_personal_account(self, payment_method: str = "Предоплатный") -> None:
        self.locators.ADD_PERSONAL_ACCOUNT_BTN.click()
        self.personal_account_form.PAYMENT_METHOD.select_by_value(payment_method)
        self.dynamic_form.SAVE_BTN.click()
        self.locators.INFO_MESSAGE.wait_to_be_visible()
        self.locators.INFO_MESSAGE_CLOSE_BTN.click()
