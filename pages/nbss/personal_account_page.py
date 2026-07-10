import re
from typing import Union

import allure

from common.enums.ats import PersonalAccountPaymentMethod
from common.helpers.env_helper import BASE_URL
from common.helpers.string_helper import check_price
from models.client import EntrepreneurClient, IndividualClient, OrganizationClient
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

    @allure.step("Открытие страницы Лицевой счет")
    def open_personal_account_page(self, account_id: int | str) -> None:
        self.open(f"{BASE_URL}customer-hierarchy-management/accounts/{account_id}/account")
        self.locators.PROPERTIES_TAB.wait_to_be_visible(timeout=15000)

    def check_related_person_by_context(self, type_context: str) -> None:
        if type_context == "personal_account":
            self.locators.CURRENT_PERSONAL_ACCOUNT_LINK.click()
        elif type_context == "agreement":
            self.locators.CURRENT_AGREEMENT_LINK.click()
        self.locators.RELATED_PERSONS_TAB.click()
        self.locators.RELATED_PERSON_BENEFICIARY_NAME.check_attribute_by_value(
            attribute="value", value=self.user_data.name_related_person
        )

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

    @allure.step("Создание ЛС")
    def add_personal_account(
        self,
        payment_method: str = PersonalAccountPaymentMethod.prepaid,
        account_type: str = "Биллинговый",
        currency: str = "RUB"
    ) -> None:
        self.locators.ADD_PERSONAL_ACCOUNT_BTN.click()
        self.personal_account_form.ACCOUNT_TYPE.wait_to_be_visible()
        self.personal_account_form.ACCOUNT_TYPE.select_by_value(account_type)
        self.personal_account_form.CURRENCY.select_by_value(currency)
        self.personal_account_form.PAYMENT_METHOD.select_by_value(payment_method)
        self.dynamic_form.SAVE_BTN.click()
        self.locators.INFO_MESSAGE.wait_to_be_visible()
        self.locators.INFO_MESSAGE_CLOSE_BTN.click()

    def edit_account_payment_method(self, payment_method: str = PersonalAccountPaymentMethod.prepaid) -> None:
        self.locators.EDIT_DETAILS_ACCOUNT_BTN.wait_to_be_enabled(timeout=15000)
        self.locators.EDIT_DETAILS_ACCOUNT_BTN.click()
        self.personal_account_form.TITLE.wait_to_be_visible()
        self.personal_account_form.PAYMENT_METHOD.select_by_value(payment_method)
        self.personal_account_form.SAVE_BTN.click()
        self.locators.INFO_MESSAGE.wait_to_be_visible()

        self.locators.INFO_MESSAGE_CLOSE_BTN.click()
