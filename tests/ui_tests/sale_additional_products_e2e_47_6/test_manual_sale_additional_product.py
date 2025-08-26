import re

import allure
import pytest
from playwright.sync_api import Page

from api.requests.client_requests import ClientRequests
from models.user import IndividualClient, OrganizationClient
from pages.client_profile_page import ClientProfilePage
from pages.inquiries_page import InquiriesPage
from pages.locators.dynamic_form_elements import (
    AddOptionsForm,
    CreateSalesAndServiceManagement,
)
from pages.locators.inquiries_elements import ProductEditForm


@allure.epic("E2E_47_6 Продажа дополнительных ПП (Допродажа этап 2)")
@allure.suite("E2E_47_6 Продажа дополнительных ПП (Допродажа этап 2)")
@pytest.mark.regress
class TestManualSaleAdditionalProduct:
    @pytest.fixture(autouse=True)
    def setup(
        self, page: Page, organization_user_data: OrganizationClient, nexign_ui_stand_login, api_request_auth_context
    ) -> None:
        self.client_profile = ClientProfilePage(nexign_ui_stand_login)
        self.client_request_api = ClientRequests(api_request_auth_context)
        self.add_options_form = AddOptionsForm(page)
        self.create_request_form = CreateSalesAndServiceManagement(nexign_ui_stand_login)
        self.inquiries_page = InquiriesPage(nexign_ui_stand_login)
        self.product_edit_form = ProductEditForm(page)

    @allure.title(
        "Продажа дополнительного продукта к основному продукту с ручным формированием и согласованием документов"
    )
    @allure.id(639173)
    @pytest.mark.regress
    def test_manual_sale_additional_product(self, create_individual_user: IndividualClient, base_url) -> None:
        client, product = self.client_request_api.product_sale(create_individual_user.user_id)
        self.client_profile.open(f"{base_url}customer-hierarchy-management/customers/{client.user_id}/overview")
        self.client_profile.locators.PRODUCTS_TAB.click()

        with allure.step('Нажать "..." -> "Добавить опцию".'):
            self.client_profile.locators.PRODUCTS_UPDATE_BTN.click()
            self.client_profile.locators.PRODUCTS_OPTIONS_OPEN_BTN[0].click()
            self.inquiries_page.locators.LOAD_SPIN_SECOND.not_to_be_visible(timeout=8000)
            self.client_profile.locators.PRODUCTS_OPTIONS_ADD_BTN.wait_to_be_visible()
            self.client_profile.locators.PRODUCTS_OPTIONS_ADD_BTN.click()

        with allure.step("Выбрать дополнительный продукт"):
            self.add_options_form.SEARCH_OPTIONS_FLD.fill("+2 ГБ")
            self.add_options_form.SEARCH_BTN.click()
            self.add_options_form.CHOSE_OPTION_BTN.wait_elements_visible(element_index=0)
            self.add_options_form.CHOSE_OPTION_BTN[0].click()
            self.add_options_form.INNER_ACCEPT_BTN.click()

        with allure.step("Указать согласование вручную"):
            self.create_request_form.TITLE.wait_to_have_text("Создание продажи и управление услугами", timeout=10000)
            self.create_request_form.CHOOSE_AGREEMENT_BTN.select_by_value(
                value="Сформировать, факт согласования вручную"
            )
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

        self.inquiries_page.manual_agree_document()

        self.inquiries_page.locators.NEXT_STEP_BTN.click()
        self.inquiries_page.wait_close_inquiry()

        with allure.step("Перейти в продуктовый профиль и проверить наличие доп. опций"):
            self.inquiries_page.locators.PRODUCT_PROFILE_BTN.click()

            self.client_profile.locators.PRODUCTS_LIST.wait_to_have_count(1)
            self.client_profile.locators.SUBSCRIBER[0].wait_to_have_text(product.phone_number)
            self.client_profile.locators.OPEN_OPTIONS_BTN[0].click()

            self.client_profile.locators.CURRENT_OPTION_PRODUCT.wait_to_be_visible(timeout=80000)
            self.client_profile.locators.OPTION_NAME[0].wait_to_have_text("+2 ГБ")
