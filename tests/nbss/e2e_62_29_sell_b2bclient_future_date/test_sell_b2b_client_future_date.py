import allure
import pytest

from common.helpers.env_helper import BASE_URL
from models.client import OrganizationClient
from models.context import test_context
from pages.base_page import BasePage
from pages.locators.nbss.inquiries_elements import ProductEditForm
from pages.locators.nbss.select_product_offers_form import SelectProductOffersFormElements
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.inquiries_page import InquiriesPage


@allure.epic("E2E_62_11 Продвжв кликнту B2B")
@allure.suite("E2E_62_11 Продажа клиенту B2B (Активация продуктов с даты, зафиксированной с клиентом)")
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestOnDateActivation:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login, create_organization: OrganizationClient) -> None:
        self.base_page = BasePage()
        self.client_profile = ClientProfilePage()
        self.inquiries_page = InquiriesPage()
        self.product_offer_form = SelectProductOffersFormElements()
        self.product_edit_form = ProductEditForm()

    def test_create_inquiry_join_product_current_date(self):
        self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")
        self.inquiries_page.sale_initialization(add_kp="auto")
        self.inquiries_page.locators.ADD_SALE_BTN.click()
        self.inquiries_page.search_and_select_product(
            product_offer_name="Бизнес на связи", product_category_name="Мобильная связь"
        )
        self.product_offer_form.ADD_BTN.click()
        self.product_offer_form.ADD_BTN.not_to_be_visible(timeout=10000)

        self.inquiries_page.locators.ADDED_PRODUCT.wait_to_have_count(1, timeout=10000)
        self.inquiries_page.locators.STEP_TITLE.wait_to_have_text("Наполнение и уточнение коммерческого заказа")
        self.inquiries_page.locators.INQUIRY_STATUS.wait_to_have_text("Обрабатывается")
        self.inquiries_page.locators.INQUIRY_STEP.wait_to_have_text("Управление составом заказа")
        self.inquiries_page.locators.TABS[0].check_attribute_by_value("aria-selected", "true")
        self.inquiries_page.locators.CHECK_CONFIGURATION_BTN.wait_to_be_enabled()

        self.inquiries_page.locators.ADDED_PRODUCT_EDIT_BTN[0].click(force=True)
        self.product_edit_form.RESOURCES_TAB.click()
        self.inquiries_page.auto_reserve_phone_number_resources()
        self.product_edit_form.INNER_ACCEPT_BTN.click()
        self.product_edit_form.RESOURCES_TAB.not_to_be_visible()
        self.inquiries_page.check_configuration()
        self.inquiries_page.locators.NEXT_STEP_BTN.click()
        self.inquiries_page.locators.SUCCESS_COMPLITED.wait_to_be_visible(timeout=300000)
        with allure.step("Проверка вкладки 'Элементы заказа'"):
            self.inquiries_page.locators.TABS[1].click()
            self.inquiries_page.locators.TABS[1].check_attribute_by_value("aria-selected", "true")
            self.inquiries_page.locators.LOAD_SPIN_FIRST.not_to_be_visible(timeout=10000)
            self.inquiries_page.locators.PRODUCTS_CONTRACT_NUM.wait_to_be_visible()
            self.inquiries_page.locators.PRODUCTS_NAME.wait_to_be_visible()

    def test_create_inquiry_join_product_future_date(self):
        self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")
        self.inquiries_page.sale_initialization(add_kp="auto", future_date=True)
        self.inquiries_page.locators.ADD_SALE_BTN.click()
        self.inquiries_page.search_and_select_product(
            product_offer_name="Бизнес на связи", product_category_name="Мобильная связь"
        )
        self.product_offer_form.ADD_BTN.click()
        self.product_offer_form.ADD_BTN.not_to_be_visible(timeout=10000)

        self.inquiries_page.locators.ADDED_PRODUCT.wait_to_have_count(1, timeout=10000)
        self.inquiries_page.locators.STEP_TITLE.wait_to_have_text("Наполнение и уточнение коммерческого заказа")
        self.inquiries_page.locators.INQUIRY_STATUS.wait_to_have_text("Обрабатывается")
        self.inquiries_page.locators.INQUIRY_STEP.wait_to_have_text("Управление составом заказа")
        self.inquiries_page.locators.TABS[0].check_attribute_by_value("aria-selected", "true")
        self.inquiries_page.locators.CHECK_CONFIGURATION_BTN.wait_to_be_enabled()

        self.inquiries_page.locators.ADDED_PRODUCT_EDIT_BTN[0].click(force=True)
        self.product_edit_form.RESOURCES_TAB.click()
        self.inquiries_page.auto_reserve_phone_number_resources()
        self.product_edit_form.INNER_ACCEPT_BTN.click()
        self.product_edit_form.RESOURCES_TAB.not_to_be_visible()
        self.inquiries_page.check_configuration()
        self.inquiries_page.locators.NEXT_STEP_BTN.click()
        self.inquiries_page.locators.SUCCESS_COMPLITED.wait_to_be_visible(timeout=300000)
        with allure.step("Проверка вкладки 'Элементы заказа'"):
            self.inquiries_page.locators.TABS[1].click()
            self.inquiries_page.locators.TABS[1].check_attribute_by_value("aria-selected", "true")
            self.inquiries_page.locators.LOAD_SPIN_FIRST.not_to_be_visible(timeout=10000)
            self.inquiries_page.locators.PRODUCTS_CONTRACT_NUM.wait_to_be_visible()
            self.inquiries_page.locators.PRODUCTS_NAME.wait_to_be_visible()
