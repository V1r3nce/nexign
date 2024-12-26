import allure
import pytest
from playwright.sync_api import Page

from pages.locators.dynamic_form_elements import FlCustomerCreate
from pages.personal_account_page import PersonalAccountPage



@allure.epic("Управление лицевым счетом")
@allure.suite("Управление лицевым счетом")
class TestPersonalAccount:

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.personal_account_page = PersonalAccountPage(page)
        self.customer_create_form = FlCustomerCreate(page)

    @allure.title("Создание и редактирование Постоплатного ЛС для ФЛ")
    @allure.id(486083)
    def test_create_personal_account(self):
        self.personal_account_page.home_page.CREATE_CUSTOMER_BTN.click()
        self.personal_account_page.fl_customer_create.LAST_NAME.wait_to_be_visible()

        self.customer_create_form.fill_data_for_individual_client()
        self.personal_account_page.dynamic_form.SAVE_BTN.click()
        self.personal_account_page.notifications.SUCCESS_CREATE_CLIENT.wait_to_be_visible()

        self.personal_account_page.notifications.SUCCESS_NOTIFICATIONS_CLOSE_BTN.click()
        self.personal_account_page.locators.CREATE_AGREEMENT_BTN.click()
        self.personal_account_page.dynamic_elements.CONTRACT_NUM.wait_to_be_visible()

        self.personal_account_page.dynamic_elements.OPERATOR_BANK_DETAILS.click_and_choose(order_value=2)
        self.personal_account_page.dynamic_form.CREATE_BTN.click()
        self.personal_account_page.notifications.SUCCESS_CREATE_CLIENT.wait_to_be_visible()

        self.personal_account_page.notifications.SUCCESS_NOTIFICATIONS_CLOSE_BTN.click()
        self.personal_account_page.locators.PERSONAL_ACCOUNTS_TAB.click()
        self.personal_account_page.locators.ADD_PERSONAL_ACCOUNT_BTN.click()
        self.personal_account_page.dynamic_form.CREATE_BTN.click()
        self.personal_account_page.notifications.SUCCESS_CREATE_CLIENT.wait_to_be_visible()

        self.personal_account_page.notifications.SUCCESS_NOTIFICATIONS_CLOSE_BTN.click()
        self.personal_account_page.locators.EDIT_DETAILS_ACCOUNT_BTN.click()
        self.personal_account_page.locators.PAYMENT_METHOD_FLD.click_and_choose(order_value=1)
        self.personal_account_page.locators.SAVE_BNT.click()
        self.personal_account_page.notifications.SUCCESS_CREATE_CLIENT.wait_to_be_visible()

        self.personal_account_page.notifications.SUCCESS_NOTIFICATIONS_CLOSE_BTN.click()
