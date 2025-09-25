import re

import allure
import pytest
from playwright.sync_api import APIRequestContext, Page

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from api.nbss.finances.payments_requests import PaymentsRequests
from api.nbss.personal_account_requests import PersonalAccountRequests
from common.helpers.time_helpers import delay
from models.user import IndividualClient, OrganizationClient
from pages.inquiries_page import InquiriesPage
from pages.locators.dynamic_form_elements import AddOptionsForm, CreateSalesAndServiceManagement
from pages.personal_account_page import PersonalAccountPage


@allure.epic("E2E_47 Подключение дополнительных ПП")
@allure.suite("E2E_47 Подключение дополнительных ПП")
@pytest.mark.regress
class TestAddOptionsProductProfile:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_ui_stand_login: Page, api_request_auth_context: APIRequestContext) -> None:
        self.personal_account_page = PersonalAccountPage(nexign_ui_stand_login)
        self.inquiries_page = InquiriesPage(nexign_ui_stand_login)
        self.add_options_form = AddOptionsForm(nexign_ui_stand_login)
        self.create_request_form = CreateSalesAndServiceManagement(nexign_ui_stand_login)
        self.client_api = ClientInquiriesRequests(api_request_auth_context)
        self.payment_api = PaymentsRequests(api_request_auth_context)
        self.personal_account_api = PersonalAccountRequests(api_request_auth_context)
        self.balance = 10.0
        self.option_name = "+2 ГБ"

    @allure.title("Отмена добавления доп. опций в продуктовом профиле клиента")
    @allure.id(538607)
    def test_cancel_add_additional_options_customer_product_profile(
        self, base_url: str, create_individual_user: IndividualClient
    ) -> None:
        with allure.step("Выполнение предусловий"):
            client = create_individual_user
            client, product = self.client_api.product_sale(client.user_id)
            self.payment_api.create_default_payment(
                client.agreements[0].accounts[0].id,
                product.one_time_payment + product.subscription_fee + self.balance,
            )
            self.personal_account_api.wait_check_current_main_balance(client.agreements[0].accounts[0].id, self.balance)

        self.personal_account_page.open(f"{base_url}customer-hierarchy-management/customers/{client.user_id}/overview")
        self.personal_account_page.locators.PRODUCTS_TAB.click(timeout=10000)
        self.personal_account_page.locators.PRODUCT_LIMIT.wait_to_be_visible()
        self.personal_account_page.locators.PRODUCTS_STATUS_COLOR[0].element_have_css_color("background-color", "green")
        self.personal_account_page.locators.PRODUCTS_OPTIONS_OPEN_BTN[0].click()
        self.personal_account_page.locators.PRODUCTS_OPTIONS_ADD_BTN.wait_to_be_visible(timeout=8000)
        self.personal_account_page.locators.PRODUCTS_OPTIONS_ADD_BTN.click()

        self.add_options_form.SEARCH_OPTIONS_FLD.fill(self.option_name)
        self.add_options_form.SEARCH_BTN.click()
        self.inquiries_page.choose_product_offer_with_name(self.option_name)
        self.add_options_form.SHOW_ONLY_CHOSEN_BTN.click()
        self.add_options_form.OPTION_CARD.wait_to_have_count(1)

        self.add_options_form.INNER_CANCEL_BTN.click()
        self.add_options_form.OPTION_CARD.not_to_be_visible()
        self.personal_account_page.locators.PRODUCTS_UPDATE_BTN.wait_to_be_visible()
        self.personal_account_page.locators.OPEN_PRODUCT_BTN.click(0)
        self.personal_account_page.locators.PRODUCT_LIMIT.wait_to_be_visible()
        self.personal_account_page.locators.OPEN_OPTIONS_BTN.not_to_be_visible()
        self.personal_account_page.locators.CURRENT_OPTION_PRODUCT.not_to_be_visible()

    @allure.title("Добавление доп. опций для монопродукта в продуктовом профиле клиента")
    @allure.id(534773)
    def test_add_options_mono_product_customer_product_profile(
        self, base_url: str, create_individual_user: IndividualClient
    ):
        with allure.step("Выполнение предусловий"):
            client = create_individual_user
            client, product = self.client_api.product_sale(client.user_id)
            self.payment_api.create_default_payment(
                client.agreements[0].accounts[0].id, product.one_time_payment + product.subscription_fee + self.balance
            )
            self.personal_account_api.wait_check_current_main_balance(client.agreements[0].accounts[0].id, self.balance)

        self.personal_account_page.open(f"{base_url}customer-hierarchy-management/customers/{client.user_id}/overview")
        self.personal_account_page.locators.PRODUCTS_TAB.click(timeout=10000)
        self.personal_account_page.locators.PRODUCT_LIMIT.wait_to_be_visible(timeout=10000)
        self.personal_account_page.locators.PRODUCTS_STATUS_COLOR[0].element_have_css_color("background-color", "green")
        self.personal_account_page.locators.PRODUCTS_OPTIONS_OPEN_BTN[0].click()
        self.personal_account_page.locators.PRODUCTS_OPTIONS_ADD_BTN.wait_to_be_visible(timeout=10000)
        self.personal_account_page.locators.PRODUCTS_OPTIONS_ADD_BTN.click()

        self.add_options_form.SEARCH_OPTIONS_FLD.fill(self.option_name)
        self.add_options_form.SEARCH_BTN.click()
        option = self.inquiries_page.choose_product_offer_with_name(self.option_name)
        self.add_options_form.SHOW_ONLY_CHOSEN_BTN.click()
        self.add_options_form.OPTION_CARD.wait_to_have_count(1)

        self.add_options_form.INNER_ACCEPT_BTN.click()
        self.create_request_form.NEED_SPD.wait_to_be_visible(timeout=15000)
        self.create_request_form.FILL_AGREEMENT_INPUT.to_contain_text(client.agreements[0].number)
        self.create_request_form.SAVE_BTN.click()
        self.inquiries_page.locators.INQUIRY_NAME.wait_to_have_text(
            re.compile(r"\d\. Продажа и управление услугами"), timeout=10000
        )
        self.inquiries_page.locators.INQUIRY_STATUS.wait_to_have_text("Обрабатывается")
        self.inquiries_page.locators.LOAD_SPIN_FIRST.not_to_be_visible(timeout=60000)
        self.inquiries_page.locators.ADDED_MONOPRODUCT.wait_to_have_count(1, timeout=25000)
        self.inquiries_page.locators.ADDED_OPTION.wait_to_have_count(1)

        self.inquiries_page.locators.NEXT_STEP_BTN.click()
        self.inquiries_page.wait_connect_package_offers_and_close_inquiry(generate_documents=False)
        self.inquiries_page.locators.TABS[0].wait_to_have_text("Активный шаг")

        self.inquiries_page.click_tab("Элементы заказа")
        self.inquiries_page.locators.PRODUCTS.wait_to_have_count(2, timeout=80000)
        self.inquiries_page.locators.PRODUCTS_NAME[0].wait_to_have_text(product.product_name)
        self.inquiries_page.locators.PRODUCTS_NAME[1].wait_to_have_text(self.option_name)
        self.inquiries_page.locators.PRODUCTS_CONTRACT_NUM.to_contain_text_in_all(client.agreements[0].number)
        self.inquiries_page.locators.PRODUCTS_PERSONAL_ACCOUNT_NUM.to_contain_text_in_all(
            client.agreements[0].accounts[0].number
        )

        self.inquiries_page.click_tab("Карточка продажи")
        self.inquiries_page.locators.SALE_ACCOUNT.wait_to_have_text(client.agreements[0].accounts[0].number)
        self.inquiries_page.locators.SALE_AGREEMENT.to_contain_text(client.agreements[0].number)
        self.inquiries_page.locators.SALE_NEED_SPD.wait_to_have_text("Не формировать")
        self.inquiries_page.locators.SALE_ADD_AGREEMENT_ADD.wait_to_have_text("Не формировать документ")

        self.inquiries_page.click_tab("Текущее состояние")
        self.inquiries_page.locators.PROCESSING_STEP.wait_to_be_visible()
        self.inquiries_page.locators.PROCESSING_STEP.to_contain_text_in_any("Выполнено успешно")

        self.inquiries_page.click_tab("История обработки")
        self.inquiries_page.locators.HISTORY_STEPS.wait_to_be_visible(timeout=10000)
        self.inquiries_page.locators.HISTORY_STEPS[-1].to_contain_text("Завершение продажи")

        self.inquiries_page.click_tab("Технические заказы")
        self.inquiries_page.locators.TECHNICAL_OFFERS.wait_to_have_count(1)
        self.inquiries_page.locators.TECHNICAL_OFFERS_ACTION[0].wait_to_have_text("Управление продуктами клиента")

        self.inquiries_page.click_tab("Документы")
        self.inquiries_page.locators.NO_ELEMENTS.wait_to_be_visible()
        self.personal_account_page.locators.LINK_IN_CONTEXT.click(0)

        self.payment_api.create_default_payment(
            client.agreements[0].accounts[0].id, option.one_time_payment + option.subscription_fee
        )
        self.personal_account_api.wait_check_current_main_balance(
            client.agreements[0].accounts[0].id, option.one_time_payment + option.subscription_fee + self.balance
        )
        self.personal_account_api.wait_check_current_main_balance(client.agreements[0].accounts[0].id, self.balance)

        self.personal_account_page.locators.PRODUCTS_TAB.click(timeout=10000)
        self.personal_account_page.locators.PRODUCT_LIMIT.wait_to_be_visible(timeout=10000)
        self.personal_account_page.locators.OPEN_OPTIONS_BTN[0].click()
        self.personal_account_page.locators.CURRENT_OPTION_PRODUCT.wait_to_be_visible()

        self.personal_account_page.locators.OPTION_STATUS_COLOR[0].element_have_css_color("background-color", "green")
        self.personal_account_page.locators.PRODUCT_ONE_TIME_PAYMENT[1].to_contain_text(f"{option.one_time_payment:.2f}")
        self.personal_account_page.locators.PRODUCTS_SUBSCRIPTION_FEE[1].to_contain_text(
            f"{option.subscription_fee:.2f}"
        )

    @allure.title("Добавление нескольких доп. опций для бандла в продуктовом профиле клиента")
    @allure.description(
        "Проверка возможности подключения опций для пакетного предложения через продуктовый профиль клиента"
    )
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=641863668",
        name="КР [UDS] Допродажа и управление услугами клиента. Подключение дополнительных продуктов.",
    )
    @allure.id(586001)
    def test_add_options_bandl_product_customer_product_profile(
        self, base_url: str, create_organization: OrganizationClient
    ):
        client = create_organization

        self.personal_account_page.open(f"{base_url}customer-hierarchy-management/customers/{client.user_id}/overview")
        bundle = self.inquiries_page.sale_bundle()
        self.payment_api.create_default_payment(
            client.agreements[0].accounts[0].id, bundle.one_time_payment + bundle.subscription_fee + self.balance
        )
        self.personal_account_api.wait_check_current_main_balance(client.agreements[0].accounts[0].id, self.balance)

        self.personal_account_page.locators.PRODUCTS_TAB.click(timeout=10000)

        self.personal_account_page.locators.wait_to_be_enabled(type_offer="product")
        self.personal_account_page.locators.PRODUCTS_UPDATE_BTN.click()
        self.personal_account_page.locators.PRODUCTS_OPTIONS_OPEN_BTN[0].click()
        self.inquiries_page.locators.LOAD_SPIN_SECOND.not_to_be_visible(timeout=8000)
        self.personal_account_page.locators.PRODUCTS_OPTIONS_ADD_BTN.wait_to_be_visible()
        self.personal_account_page.locators.PRODUCTS_OPTIONS_ADD_BTN.click()

        self.add_options_form.SEARCH_OPTIONS_FLD.fill(self.option_name)
        self.add_options_form.SEARCH_BTN.click()
        self.add_options_form.CHOSE_OPTION_BTN.wait_elements_visible(element_index=1)
        self.add_options_form.CHOSE_OPTION_BTN[1].click()
        self.add_options_form.CHOSE_OPTION_BTN.wait_elements_visible(element_index=3)
        self.add_options_form.CHOSE_OPTION_BTN[3].click()
        self.add_options_form.SHOW_ONLY_CHOSEN_BTN.wait_to_be_visible(timeout=8000)
        self.add_options_form.SHOW_ONLY_CHOSEN_BTN.click()
        self.add_options_form.INNER_ACCEPT_BTN.click()

        self.personal_account_page.locators.PRODUCTS_UPDATE_BTN.wait_to_be_visible()

        self.personal_account_page.locators.REQUESTS_TAB.click()
        self.inquiries_page.locators.LOAD_SPIN_SECOND.not_to_be_visible(timeout=80000)
        self.personal_account_page.locators.REQUEST_NUMBER[1].wait_to_be_visible()
        self.personal_account_page.locators.REQUEST_NUMBER[1].click()
        self.inquiries_page.locators.LOAD_SPIN_SECOND.not_to_be_visible(timeout=80000)

        self.inquiries_page.locators.SUCCESS_SETUP.wait_to_be_visible()

        self.inquiries_page.locators.TABS[1].wait_to_be_visible(timeout=80000)
        self.inquiries_page.locators.TABS[1].click()
        self.inquiries_page.locators.PRODUCTS[1].wait_to_be_visible(timeout=80000)

        self.inquiries_page.locators.TABS[2].click()
        self.inquiries_page.locators.DATA_SALE.wait_to_be_visible(timeout=80000)

        self.inquiries_page.locators.TABS[3].click()
        self.inquiries_page.locators.PROCESSING_STEP[0].wait_to_be_visible(timeout=80000)

        self.inquiries_page.locators.TABS[4].click()
        self.inquiries_page.locators.HISTORY_STEPS[0].wait_to_be_visible(timeout=80000)

        self.inquiries_page.locators.TABS[5].click()
        self.inquiries_page.locators.TECHNICAL_OFFERS[0].wait_to_be_visible(timeout=80000)

        self.inquiries_page.locators.TABS[6].click()
        self.personal_account_page.locators.CURRENT_CLIENT_LINK.wait_to_be_visible()
        self.personal_account_page.locators.CURRENT_CLIENT_LINK.click()

        self.personal_account_page.locators.PRODUCTS_TAB.click()
        self.personal_account_page.locators.OPEN_OPTIONS_BTN[0].wait_to_be_visible(timeout=80000)

        delay(1, reason="не успевает прогрузиться список подключенных опций")
        self.personal_account_page.locators.OPEN_OPTIONS_BTN[0].click()
        self.personal_account_page.locators.CURRENT_OPTION_PRODUCT.wait_elements_visible(element_index=0)
        self.personal_account_page.locators.CURRENT_OPTION_PRODUCT.wait_elements_visible(element_index=1)

        self.personal_account_page.locators.wait_to_be_enabled(type_offer="option")
