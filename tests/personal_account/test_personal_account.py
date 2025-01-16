import time

import allure
import pytest
from playwright.sync_api import Page
from pages.locators.dynamic_form_elements import IndividualCustomerCreate, CreateOrganization, CreateEntrepreneur, \
    AddRelatedPersonForms
from pages.personal_account_page import PersonalAccountPage


@allure.epic("Управление лицевым счетом")
@allure.suite("Управление лицевым счетом")
class TestPersonalAccount:

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.personal_account_page = PersonalAccountPage(page)
        self.customer_create_form = IndividualCustomerCreate(page)
        self.organization_create_form = CreateOrganization(page)
        self.entrepreneur_create_form = CreateEntrepreneur(page)
        self.add_related_person_form = AddRelatedPersonForms(page)

    @pytest.mark.parametrize(
        "title, case_id, type_account, type_client",
        [
            ("Создание и редактирование Предоплатного ЛС для ФЛ", 486082, "prepaid", "individual"),
            ("Создание и редактирование Постоплатного ЛС для ФЛ", 581810, "postpaid", "individual"),
            ("Создание и редактирование Предоплатного ЛС для ИП", 486084, "prepaid", "entrepreneur"),
            ("Создание и редактирование Постоплатного ЛС для ИП", 486085, "postpaid", "entrepreneur"),
            ("Создание и редактирование Предоплатного ЛС для ЮЛ", 486086, "prepaid", "organisation"),
            ("Создание и редактирование Постоплатного ЛС для ЮЛ", 486087, "postpaid", "organisation")
        ]
    )
    def test_create_personal_account(self, type_client, type_account, title, case_id):
        type_client_list = {
            "prepaid": 1,
            "postpaid": 2
        }

        allure.dynamic.title(title)
        allure.dynamic.id(case_id)
        self.personal_account_page.click_create_customer(type_customer=type_client)
        self.personal_account_page.dynamic_elements.INN.wait_to_be_visible()

        if type_client == "individual":
            self.customer_create_form.fill_data_for_individual_client()
        elif type_client == "entrepreneur":
            self.entrepreneur_create_form.fill_data_for_entrepreneur_client()
        elif type_client == "organisation":
            self.organization_create_form.fill_data_for_organization_client()
        self.personal_account_page.dynamic_form.SAVE_BTN.click()
        self.personal_account_page.notifications.SUCCESS_CREATE_CLIENT.wait_to_be_visible()

        self.personal_account_page.notifications.SUCCESS_NOTIFICATIONS_CLOSE_BTN.click()
        self.personal_account_page.locators.CREATE_AGREEMENT_BTN.click()
        self.personal_account_page.dynamic_elements.CONTRACT_NUM.wait_to_be_visible()

        self.personal_account_page.fill_data_create_agreement(type_client=type_client)
        self.personal_account_page.dynamic_form.CREATE_BTN.click()
        self.personal_account_page.notifications.SUCCESS_CREATE_CLIENT.wait_to_be_visible()

        self.personal_account_page.notifications.SUCCESS_NOTIFICATIONS_CLOSE_BTN.click()
        self.personal_account_page.locators.PERSONAL_ACCOUNTS_TAB.click()
        self.personal_account_page.locators.ADD_PERSONAL_ACCOUNT_BTN.click()
        self.personal_account_page.dynamic_form.CREATE_BTN.click()
        self.personal_account_page.notifications.SUCCESS_CREATE_CLIENT.wait_to_be_visible()

        self.personal_account_page.notifications.SUCCESS_NOTIFICATIONS_CLOSE_BTN.click()
        self.personal_account_page.locators.EDIT_DETAILS_ACCOUNT_BTN.click()
        self.personal_account_page.locators.PAYMENT_METHOD_FLD.click_and_choose(order_value=type_client_list[type_account])
        self.personal_account_page.locators.SAVE_BNT.click()
        self.personal_account_page.notifications.SUCCESS_CREATE_CLIENT.wait_to_be_visible()

        self.personal_account_page.notifications.SUCCESS_NOTIFICATIONS_CLOSE_BTN.click()


    def test_create_personal_account_with_related_persons(self):
        self.personal_account_page.click_create_customer(type_customer='organisation')
        self.personal_account_page.dynamic_elements.INN.wait_to_be_visible()

        self.organization_create_form.fill_data_for_organization_client()
        self.personal_account_page.dynamic_form.SAVE_BTN.click()
        self.personal_account_page.notifications.SUCCESS_CREATE_CLIENT.wait_to_be_visible()

        self.personal_account_page.notifications.SUCCESS_NOTIFICATIONS_CLOSE_BTN.click()
        self.personal_account_page.locators.CREATE_AGREEMENT_BTN.click()
        self.personal_account_page.dynamic_elements.CONTRACT_NUM.wait_to_be_visible()

        self.personal_account_page.fill_data_create_agreement(type_client='organisation')
        self.personal_account_page.dynamic_form.CREATE_BTN.click()
        self.personal_account_page.notifications.SUCCESS_CREATE_CLIENT.wait_to_be_visible()

        self.personal_account_page.notifications.SUCCESS_NOTIFICATIONS_CLOSE_BTN.click()
        self.personal_account_page.locators.RELATED_PERSONS_TAB.click()
        self.personal_account_page.locators.ADD_RELATED_PERSON_BTN.click()
        self.add_related_person_form.fill_data_for_related_person()

        self.personal_account_page.locators.PERSONAL_ACCOUNTS_AFTER_RELATED_PERSON_TAB.click()
        self.personal_account_page.locators.ADD_PERSONAL_ACCOUNT_BTN.click()
        self.personal_account_page.dynamic_form.CREATE_BTN.click()
        self.personal_account_page.notifications.SUCCESS_CREATE_CLIENT.wait_to_be_visible()

        self.personal_account_page.notifications.SUCCESS_NOTIFICATIONS_CLOSE_BTN.click()
        self.personal_account_page.locators.RELATED_PERSONS_TAB.click()
        self.personal_account_page.locators.ADD_RELATED_PERSON_BTN.click()
        self.add_related_person_form.fill_data_for_related_person()
        self.personal_account_page.check_related_person_by_context(type_context='personal_account')
        self.personal_account_page.check_related_person_by_context(type_context='agreement')
