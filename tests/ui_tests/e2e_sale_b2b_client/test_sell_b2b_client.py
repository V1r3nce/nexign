import allure
import pytest
from playwright.sync_api import Page

from common.helpers.time_helpers import delay
from pages.locators.base_elements import BaseElements
from pages.locators.client_search import ClientSearch
from pages.locators.dynamic_form_elements import CreateOrganization, ProductOffer, \
    AddRelatedPersonForms, RequestCreate
from pages.locators.inquiries_page import InquiriesPage
from pages.locators.home_page_elements import HomePage
from pages.personal_account_page import PersonalAccountPage

@allure.epic("E2E_62 Продажа клиенту B2B")
@allure.suite("E2E_62 Продажа клиенту B2B")
@pytest.mark.usefixtures("nexign_ui_stand_login")
class TestSellB2BClient:

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.personal_account_page = PersonalAccountPage(page)
        self.home_page = HomePage(page)
        self.client_search = ClientSearch(page)
        self.organization_create_form = CreateOrganization(page)
        self.add_related_person_form = AddRelatedPersonForms(page)
        self.base_elements = BaseElements(page)
        self.create_request = RequestCreate(page)
        self.inquiries_page = InquiriesPage(page)
        self.product_offer = ProductOffer(page)

    @allure.title('Продажа "бандл" продукта B2B клиенту с ручным созданием договора и ЛС')
    @allure.id(533492)
    def test_selling_bundle_b2b_product_client_manual_creation_agreement(self):
        self.personal_account_page.click_create_customer(type_customer='organisation')
        self.personal_account_page.dynamic_elements.INN.wait_to_be_visible()
        self.organization_create_form.fill_data_for_organization_client()
        self.personal_account_page.dynamic_form.SAVE_BTN.click()
        self.personal_account_page.notifications.SUCCESS_CREATE_CLIENT.wait_to_be_visible()

        self.personal_account_page.locators.RELATED_PERSONS_TAB.click()
        self.personal_account_page.locators.ADD_RELATED_PERSON_BTN.click()
        self.add_related_person_form.fill_data_for_related_person()

        self.base_elements.CREATE_APPLICATION.click()
        self.create_request.CHOOSE_AGREEMENT_BTN.select_by_value(value='Вручную')
        self.create_request.CHOOSE_PRIORITY_BTN.select_by_value(value='Низкий')
        self.create_request.SAVE_BTN.click()
        delay(3, reason='просто падает если не подождать дополнительно, лоадер не сразу появляется')
        self.inquiries_page.LOAD_SPIN_FIRST.not_to_be_visible(timeout=60000)
        self.inquiries_page.PRODUCT_INFO_STATUS.wait_to_be_visible()

        self.inquiries_page.ADD_SALE_BTN.click()
        self.product_offer.TYPE_PACKAGE_OFFER.click()
        self.product_offer.CATEGORY_MOBILE.click()
        self.product_offer.FOUND_BTN.click()
        self.product_offer.CHOOSE_PACKAGE_BTN.click()
        self.product_offer.ADD_BTN.click()

    @allure.title('Продажа "моно" продукта B2B клиенту с ручным созданием договора и ЛС')
    @allure.id(539223)
    def test_selling_mono_b2b_product_client_manual_creation_agreement(self):
        self.personal_account_page.click_create_customer(type_customer='organisation')
        self.personal_account_page.dynamic_elements.INN.wait_to_be_visible()
        self.organization_create_form.fill_data_for_organization_client()
        self.personal_account_page.dynamic_form.SAVE_BTN.click()
        self.personal_account_page.notifications.SUCCESS_CREATE_CLIENT.wait_to_be_visible()

        self.personal_account_page.locators.RELATED_PERSONS_TAB.click()
        self.personal_account_page.locators.ADD_RELATED_PERSON_BTN.click()
        self.add_related_person_form.fill_data_for_related_person()

        self.base_elements.CREATE_APPLICATION.click()
        self.create_request.CHOOSE_AGREEMENT_BTN.select_by_value(value='Вручную')
        self.create_request.CHOOSE_PRIORITY_BTN.select_by_value(value='Низкий')
        self.create_request.SAVE_BTN.click()
        delay(3, reason='просто падает если не подождать дополнительно, лоадер не сразу появляется')
        self.inquiries_page.LOAD_SPIN_FIRST.not_to_be_visible(timeout=60000)
        self.inquiries_page.PRODUCT_INFO_STATUS.wait_to_be_visible()

        self.inquiries_page.ADD_SALE_BTN.click()

        self.product_offer.TYPE_MONO_PRODUCT.click()
        self.product_offer.CATEGORY_ETHERNET.click()
        self.product_offer.FOUND_BTN.click()
        self.product_offer.CHOOSE_MONO_BTN.click()
        self.product_offer.ADD_BTN.click()

