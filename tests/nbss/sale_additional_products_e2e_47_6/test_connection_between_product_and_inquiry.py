import re

import allure
import pytest
from playwright.sync_api import Page

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from api.nbss.client_requests.client_requests import ClientRequests
from api.nbss.finances.payments_requests import PaymentsRequests
from api.nbss.personal_account_requests import PersonalAccountRequests
from common.helpers.time_helpers import delay
from models.user import IndividualClient
from pages.locators.nbss.dynamic_form_elements import (
    AddOptionsForm,
    ClientChoice,
    CreateSalesAndServiceManagement,
)
from pages.locators.nbss.inquiries_elements import EditContactInfoForm, ProductEditForm
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.inquiries_page import InquiriesPage


@allure.epic("E2E_47_6 Продажа дополнительных ПП (Допродажа этап 2)")
@allure.suite("E2E_47_6 Продажа дополнительных ПП (Допродажа этап 2)")
@pytest.mark.regress
class TestConnectionBetweenProductAndInquiry:
    @pytest.fixture(autouse=True)
    def setup(self, page: Page, nexign_ui_stand_login, api_request_context) -> None:
        self.client_profile = ClientProfilePage(nexign_ui_stand_login)
        self.client_request_api = ClientInquiriesRequests(api_request_context)
        self.add_options_form = AddOptionsForm(page)
        self.create_request_form = CreateSalesAndServiceManagement(nexign_ui_stand_login)
        self.inquiries_page = InquiriesPage(nexign_ui_stand_login)
        self.product_edit_form = ProductEditForm(page)
        self.payment_api = PaymentsRequests(api_request_context)
        self.personal_account_api = PersonalAccountRequests(api_request_context)
        self.client_choice = ClientChoice(page)
        self.edit_contact_form = EditContactInfoForm(page)
        self.client_api = ClientRequests(api_request_context)

        self.balance = 1000

    @allure.title("Просмотр заявок из продуктового профиля клиента")
    @allure.id(669927)
    def test_inquires_view_from_client_product_profile(self, individual_user_data: IndividualClient, base_url) -> None:
        individual_user = self.client_api.create_client_with_payment(individual_user_data, self.balance)

        client, product = self.client_request_api.product_sale(
            individual_user.user_id,
            agreement_id=individual_user.agreements[0].id,
            account_id=individual_user.agreements[0].accounts[0].id,
        )
        self.client_profile.open(f"{base_url}customer-hierarchy-management/customers/{client.user_id}/overview")

        with allure.step("Проверка активации продукта"):
            self.client_profile.locators.PRODUCTS_TAB.click()
            self.client_profile.locators.PRODUCTS.wait_to_be_visible()
            self.client_profile.locators.PRODUCTS_STATUS_COLOR[0].element_have_css_color("background-color", "green")

        self.client_profile.add_adoption_product("+2 ГБ")

        with allure.step("Создать заявку"):
            self.create_request_form.TITLE.wait_to_have_text("Создание продажи и управление услугами", timeout=10000)
            self.create_request_form.EMAIL.wait_to_have_text("")
            self.create_request_form.PHONE.wait_to_have_text("")
            self.create_request_form.FILL_AGREEMENT_INPUT.to_contain_text(client.agreements[0].number)
            self.create_request_form.CREATE_ADD_AGREEMENT.to_contain_text("Не формировать документ")
            self.create_request_form.CURRENT_PRODUCT.to_contain_text(product.product_name)

            self.create_request_form.SAVE_BTN.click()
            self.inquiries_page.locators.INQUIRY_NAME.wait_to_have_text(
                re.compile(r"\d\. Продажа и управление услугами"), timeout=10000
            )

        with allure.step("Проверка этапов продажи"):
            self.inquiries_page.check_open_sale_inquiry(check_info_status=False)
            self.inquiries_page.check_first_step_sale_titles(product_count=2)
            self.inquiries_page.locators.INQUIRY_STATUS.wait_to_have_text("Обрабатывается")
            self.inquiries_page.locators.ADDED_PRODUCT_ONE_TIME_PAYMENT[0].wait_to_be_visible()
            self.inquiries_page.locators.ADDED_PRODUCT_SUBSCRIPTION_FEE[0].wait_to_be_visible()

        with allure.step("Проверка доп ПП"):
            self.inquiries_page.locators.LOAD_SPIN_THIRD.not_to_be_visible()
            self.inquiries_page.locators.ADDED_PRODUCT_VISIBLE_BTN[1].scroll_into_view_if_needed()
            self.inquiries_page.locators.SCROLLABLE_PRODUCT_BLOCK.scroll_scrollable_platform(80)
            self.inquiries_page.locators.ADDED_PRODUCT_VISIBLE_BTN[1].click(force=True)
            self.product_edit_form.VOLUMES[0].to_contain_text("2 ГБ", timeout=5000)
            self.product_edit_form.INNER_CANCEL_BTN.click()

        with allure.step("Перейти в продуктовый профиль и проверить наличие доп. опций"):
            self.inquiries_page.locators.PRODUCT_PROFILE_BTN.click()

            self.client_profile.locators.PRODUCTS_LIST.wait_to_have_count(1)
            self.client_profile.locators.SUBSCRIBER[0].wait_to_have_text(product.phone_number)
            self.client_profile.locators.OPEN_OPTIONS_BTN[0].click()

            self.client_profile.locators.CURRENT_OPTION_PRODUCT.wait_to_be_visible(timeout=80000)
            self.client_profile.locators.OPTION_NAME[0].wait_to_have_text("+2 ГБ")

    @allure.title("Просмотр карточки заявки")
    @allure.id(669942)
    def test_inquires_view(self, individual_user_data: IndividualClient, base_url) -> None:
        individual_user = self.client_api.create_client_with_payment(individual_user_data, self.balance)
        second_user = IndividualClient()
        self.client_api.create_individual_client(second_user)

        client, product = self.client_request_api.product_sale(
            individual_user.user_id,
            agreement_id=individual_user.agreements[0].id,
            account_id=individual_user.agreements[0].accounts[0].id,
        )
        self.client_profile.open(f"{base_url}customer-hierarchy-management/customers/{client.user_id}/overview")

        with allure.step("Проверка активации продукта"):
            self.client_profile.locators.PRODUCTS_TAB.click()
            self.client_profile.locators.PRODUCTS.wait_to_be_visible()
            self.client_profile.locators.PRODUCTS_STATUS_COLOR[0].element_have_css_color("background-color", "green")

        self.client_profile.add_adoption_product("+2 ГБ")

        with allure.step("Создать заявку"):
            self.create_request_form.TITLE.wait_to_have_text("Создание продажи и управление услугами", timeout=10000)
            self.create_request_form.EMAIL.wait_to_have_text("")
            self.create_request_form.PHONE.wait_to_have_text("")
            self.create_request_form.FILL_AGREEMENT_INPUT.to_contain_text(client.agreements[0].number)
            self.create_request_form.CREATE_ADD_AGREEMENT.to_contain_text("Не формировать документ")
            self.create_request_form.CURRENT_PRODUCT.to_contain_text(product.product_name)

            self.create_request_form.SAVE_BTN.click()
            self.inquiries_page.locators.INQUIRY_NAME.wait_to_have_text(
                re.compile(r"\d\. Продажа и управление услугами"), timeout=10000
            )

        with allure.step("Проверка этапов продажи"):
            self.inquiries_page.check_open_sale_inquiry(check_info_status=False)
            self.inquiries_page.check_first_step_sale_titles(product_count=2)
            self.inquiries_page.locators.INQUIRY_STATUS.wait_to_have_text("Обрабатывается")
            self.inquiries_page.locators.ADDED_PRODUCT_ONE_TIME_PAYMENT[0].wait_to_be_visible()
            self.inquiries_page.locators.ADDED_PRODUCT_SUBSCRIPTION_FEE[0].wait_to_be_visible()

        with allure.step("Проверка доп ПП"):
            self.inquiries_page.locators.LOAD_SPIN_THIRD.not_to_be_visible()
            self.inquiries_page.locators.ADDED_PRODUCT_VISIBLE_BTN[1].scroll_into_view_if_needed()
            self.inquiries_page.locators.SCROLLABLE_PRODUCT_BLOCK.scroll_scrollable_platform(80)
            self.inquiries_page.locators.ADDED_PRODUCT_VISIBLE_BTN[1].click(force=True)
            self.product_edit_form.VOLUMES[0].to_contain_text("2 ГБ", timeout=5000)
            self.product_edit_form.INNER_CANCEL_BTN.click()

        with allure.step("Перейти в Контактные данные"):
            self.inquiries_page.locators.TABS.wait_to_have_count(10)
            delay(1, "Для стабильности выбора таба")
            self.inquiries_page.locators.TABS.click(3)
            self.inquiries_page.locators.TABS[3].wait_to_have_text("Контактные данные")
            self.inquiries_page.locators.TABS[3].check_attribute_by_value("aria-selected", "true")

            self.inquiries_page.locators.CONTACT_EDIT_BTN.wait_to_be_visible()
            self.inquiries_page.locators.CONTACT_CLIENT.wait_to_be_visible()
            self.inquiries_page.locators.CONTACT_CLIENT.to_contain_text(individual_user.first_name)
            self.inquiries_page.locators.CONTACT_PERSON.wait_to_be_visible()
            self.inquiries_page.locators.CONTACT_EMAIL.wait_to_be_visible()
            self.inquiries_page.locators.CONTACT_PHONE.wait_to_be_visible()

        with allure.step("Редактировать контактные данные"):
            self.inquiries_page.locators.CONTACT_EDIT_BTN.click()

            self.edit_contact_form.CLIENT.wait_to_be_visible()
            self.edit_contact_form.EMAIL.wait_to_be_visible()
            self.edit_contact_form.PHONE.wait_to_be_visible()
            self.edit_contact_form.LINKED_PERSON.wait_to_be_visible()
            self.edit_contact_form.CLIENT.click()

        with allure.step("Поиск и выбор другого клиента"):
            self.client_choice.INN.fill(second_user.inn)
            self.client_choice.FIND_BTN.click()

            self.client_choice.FOUNDED_CUSTOMER.wait_elements_visible(0, timeout=10000)
            self.client_choice.FOUNDED_CUSTOMER.click(0)
            self.client_choice.INNER_ACCEPT_BTN[1].click()

            self.edit_contact_form.CLIENT.to_contain_text(second_user.first_name)

    @allure.title('Создание заявки "Продажа и управение услугами" (Допродажа) с продуктового профиля клиента')
    @allure.id(669928)
    def test_create_inquiry_from_client_product_profile(self, individual_user_data: IndividualClient, base_url) -> None:
        individual_user = self.client_api.create_client_with_payment(individual_user_data, self.balance)
        second_user = IndividualClient()
        self.client_api.create_individual_client(second_user)

        client, product = self.client_request_api.product_sale(
            individual_user.user_id,
            agreement_id=individual_user.agreements[0].id,
            account_id=individual_user.agreements[0].accounts[0].id,
        )

        self.client_profile.open(f"{base_url}customer-hierarchy-management/customers/{client.user_id}/overview")

        with allure.step("Проверка активации продукта"):
            self.client_profile.locators.PRODUCTS_TAB.click()
            self.client_profile.locators.PRODUCTS.wait_to_be_visible()
            self.client_profile.locators.PRODUCTS_STATUS_COLOR[0].element_have_css_color("background-color", "green")

        self.client_profile.add_adoption_product("+2 ГБ")

        with allure.step("Открыть форму создания заявки проверить и закрыть"):
            self.create_request_form.TITLE.wait_to_have_text("Создание продажи и управление услугами", timeout=10000)
            self.create_request_form.CANCEL_BTN.click()
            self.create_request_form.MODAL_SECOND_BTN.click()

        self.client_profile.add_adoption_product("+2 ГБ")

        with allure.step("Создать заявку"):
            self.create_request_form.TITLE.wait_to_have_text("Создание продажи и управление услугами", timeout=10000)
            self.create_request_form.EMAIL.wait_to_have_text("")
            self.create_request_form.PHONE.wait_to_have_text("")
            self.create_request_form.FILL_AGREEMENT_INPUT.to_contain_text(client.agreements[0].number)
            self.create_request_form.CREATE_ADD_AGREEMENT.to_contain_text("Не формировать документ")
            self.create_request_form.CURRENT_PRODUCT.to_contain_text(product.product_name)

            self.create_request_form.SELECT_CLIENT_BTN.select_by_value("Выбрать клиента")

        with allure.step("Поиск и выбор другого клиента"):
            self.client_choice.INN.fill(second_user.inn)
            self.client_choice.FIND_BTN.click()

            self.client_choice.FOUNDED_CUSTOMER.wait_elements_visible(0, timeout=10000)
            self.client_choice.FOUNDED_CUSTOMER.click(0)
            self.client_choice.INNER_ACCEPT_BTN[0].click()

            self.create_request_form.CLIENT.to_contain_text(second_user.first_name)
