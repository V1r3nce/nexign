import allure
import pytest
from playwright.sync_api import Page

from common.helpers.time_helpers import delay
from models.user import IndividualClient, OrganizationClient
from pages.inquiries_page import InquiriesPage
from pages.locators.dynamic_form_elements import CreateOrganization, IndividualCustomerCreate, RequestCreate
from pages.locators.inquiries_elements import ProductEditForm
from pages.locators.select_product_offers_form import SelectProductOffersForm
from pages.personal_account_page import PersonalAccountPage


@allure.epic('E2E_42 Подключение платных "красивых номеров"')
@allure.suite('E2E_42 Подключение платных "красивых номеров"')
@pytest.mark.usefixtures("nexign_ui_stand_login")
class TestSellPaidBeautifulNumber:
    @pytest.fixture(autouse=True)
    def setup(self, page: Page) -> None:
        self.personal_account_page = PersonalAccountPage(page)
        self.customer_create_form = IndividualCustomerCreate(page)
        self.organization_create_form = CreateOrganization(page)
        self.create_request = RequestCreate(page)
        self.inquiries_page = InquiriesPage(page)
        self.product_offer = SelectProductOffersForm(page)
        self.edit_product_form = ProductEditForm(page)

    @allure.title('Подключение платного "красивого номера" (B2B, Продажа)')
    @allure.id(576238)
    @pytest.mark.regress
    def test_connect_beautiful_number_b2b(self, organization_user_data: OrganizationClient) -> None:
        self.personal_account_page.user_data = organization_user_data
        self.personal_account_page.create_customer_with_type("organization")
        self.organization_create_form.SAVE_BTN.click()
        self.personal_account_page.locators.INFO_MESSAGE.wait_to_be_visible()

        self.create_request.CREATE_APPLICATION.click()
        self.create_request.CHOOSE_AGREEMENT_BTN.select_by_value(value="Автоматически")
        self.create_request.SAVE_BTN.click()
        self.inquiries_page.locators.LOAD_SPIN_FIRST.wait_to_be_visible(timeout=8000)
        self.inquiries_page.locators.LOAD_SPIN_FIRST.wait_to_be_visible(timeout=8000)
        self.inquiries_page.locators.LOAD_SPIN_SECOND.not_to_be_visible(timeout=80000)
        self.inquiries_page.locators.LOAD_SPIN_SECOND.not_to_be_visible(timeout=80000)
        self.inquiries_page.locators.LOCATOR_SALE.wait_to_be_visible()

        self.inquiries_page.locators.ADD_SALE_BTN.click()
        self.product_offer.PRODUCT_TYPE.select_by_value("Монопродукт")
        self.product_offer.PRODUCT_CATEGORY.select_by_value("Мобильная связь")
        self.product_offer.SEARCH_BTN.click()
        self.product_offer.PRODUCT_CARD.wait_to_be_visible()
        delay(1, reason="не успевает прогрузиться выдача, нужно это ожидание")
        self.product_offer.PRODUCT_CARD_SELECT_BTN[0].click()
        self.product_offer.ADD_BTN.click()

        self.inquiries_page.locators.ADDED_PRODUCT_EDIT_BTN.wait_elements_visible(element_index=0)
        self.inquiries_page.locators.ADDED_PRODUCT_EDIT_BTN[0].click(force=True)
        self.edit_product_form.COLOR_NUMBER_FORM.select_by_value(value="Платиновый")
        self.edit_product_form.INNER_ACCEPT_BTN.click()

        delay(1, reason="страница не успевает прогружаться")
        self.inquiries_page.locators.ADDED_PRODUCT_EDIT_BTN.wait_elements_visible(element_index=0)
        self.inquiries_page.locators.ADDED_PRODUCT_EDIT_BTN[0].click(force=True)
        self.edit_product_form.RESOURCES_TAB.click()

        self.edit_product_form.BOOK_RESOURCES.wait_to_be_enabled(timeout=8000)
        self.edit_product_form.BOOK_RESOURCES.click()
        self.inquiries_page.locators.LOAD_SPIN_FIRST.not_to_be_visible(timeout=8000)
        self.edit_product_form.INNER_CANCEL_BTN.click()

        self.inquiries_page.locators.CHECK_CONFIGURATION_BTN.click()
        self.inquiries_page.locators.LOAD_SPIN_FIRST.not_to_be_visible(timeout=80000)
        self.inquiries_page.locators.SUCCESS_SETUP.wait_to_be_visible()

        self.inquiries_page.locators.NEXT_STEP_BTN.click()
        self.inquiries_page.locators.LOAD_SPIN_FIRST.not_to_be_visible(timeout=80000)
        self.inquiries_page.locators.AUTOMATIC_CREATE_CONTRACT_BTN.click()
        self.inquiries_page.locators.LOAD_SPIN_FIRST.wait_to_be_visible()
        self.inquiries_page.locators.LOAD_SPIN_FIRST.not_to_be_visible(timeout=1000000)

        self.inquiries_page.locators.SUCCESS_SETUP.wait_to_be_visible()
        self.inquiries_page.locators.PRODUCT_PROFILE_BTN.click()
        self.personal_account_page.locators.PRODUCTS_DETAILS_OPEN_BTN.click(force=True)
        self.personal_account_page.locators.PRODUCTS_DETAILS_BTN.click(force=True)

    @allure.title('Подключение платного "красивого номера" (B2C, Продажа)')
    @allure.id(577147)
    @pytest.mark.regress
    def test_connect_beautiful_number_b2c(self, individual_user_data: IndividualClient) -> None:
        self.personal_account_page.user_data = individual_user_data
        self.personal_account_page.create_customer_with_type("individual")
        self.personal_account_page.dynamic_form.SAVE_BTN.click()
        self.personal_account_page.locators.INFO_MESSAGE.wait_to_be_visible()

        self.create_request.CREATE_APPLICATION.click()
        self.create_request.CHOOSE_AGREEMENT_BTN.select_by_value(value="Автоматически")
        self.create_request.SAVE_BTN.click()
        self.inquiries_page.locators.LOAD_SPIN_FIRST.wait_to_be_visible(timeout=8000)
        self.inquiries_page.locators.LOAD_SPIN_FIRST.wait_to_be_visible(timeout=8000)
        self.inquiries_page.locators.LOAD_SPIN_SECOND.not_to_be_visible(timeout=80000)
        self.inquiries_page.locators.LOAD_SPIN_SECOND.not_to_be_visible(timeout=80000)
        self.inquiries_page.locators.LOCATOR_SALE.wait_to_be_visible()

        self.inquiries_page.locators.ADD_SALE_BTN.click()
        self.product_offer.PRODUCT_TYPE.select_by_value("Монопродукт")
        self.product_offer.PRODUCT_CATEGORY.select_by_value("Мобильная связь")
        self.product_offer.SEARCH_BTN.click()
        self.product_offer.PRODUCT_CARD.wait_to_be_visible()
        self.product_offer.PRODUCT_CARD_SELECT_BTN[0].click()
        self.product_offer.ADD_BTN.click()

        self.inquiries_page.locators.ADDED_PRODUCT_EDIT_BTN.wait_elements_visible(element_index=0)
        self.inquiries_page.locators.ADDED_PRODUCT_EDIT_BTN[0].click(force=True)
        self.edit_product_form.COLOR_NUMBER_FORM.select_by_value(value="Платиновый")
        self.edit_product_form.INNER_ACCEPT_BTN.click()

        delay(1, reason="страница не успевает прогружаться")
        self.inquiries_page.locators.ADDED_PRODUCT_EDIT_BTN.wait_elements_visible(element_index=0)
        self.inquiries_page.locators.ADDED_PRODUCT_EDIT_BTN[0].click(force=True)
        self.edit_product_form.RESOURCES_TAB.click()

        self.edit_product_form.BOOK_RESOURCES.wait_to_be_enabled(timeout=8000)
        self.edit_product_form.BOOK_RESOURCES.click()
        self.inquiries_page.locators.LOAD_SPIN_FIRST.not_to_be_visible(timeout=8000)
        self.edit_product_form.INNER_CANCEL_BTN.click()

        self.inquiries_page.locators.CHECK_CONFIGURATION_BTN.click()
        self.inquiries_page.locators.LOAD_SPIN_FIRST.not_to_be_visible(timeout=80000)
        self.inquiries_page.locators.SUCCESS_SETUP.wait_to_be_visible()

        self.inquiries_page.locators.NEXT_STEP_BTN.click()
        self.inquiries_page.locators.LOAD_SPIN_FIRST.wait_to_be_visible()
        self.inquiries_page.locators.LOAD_SPIN_FIRST.not_to_be_visible(timeout=1000000)

        self.inquiries_page.locators.SUCCESS_SETUP.wait_to_be_visible()
        self.inquiries_page.locators.PRODUCT_PROFILE_BTN.click()
        self.personal_account_page.locators.PRODUCTS_DETAILS_OPEN_BTN.click(force=True)
        self.personal_account_page.locators.PRODUCTS_DETAILS_BTN.click(force=True)
