import allure
import pytest

from common.helpers.env_helper import BASE_URL
from models.address_info import BasicSystemAddress
from models.client import OrganizationClient
from models.context import test_context
from models.product import B2BProducts, B2CProducts, UnsegmentedProducts, product_names_map
from pages.base_page import BasePage
from pages.locators.base_elements import BaseElements
from pages.locators.nbss.dynamic_form_elements import (
    EditSegmentsForm,
    TechConnectCheckForm,
)
from pages.locators.nbss.select_product_offers_form import SelectProductOffersFormElements
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.inquiries_page import InquiriesPage


@allure.epic("E2E_62_9 Продажа клиенту B2B")
@allure.suite("E2E_62_9 Продажа клиенту B2B (Подбор ресурсов с учетом совместимости)")
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestSaleWithSegmentationCheck:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login, create_organization: OrganizationClient) -> None:
        self.base_page = BasePage()
        self.client_profile = ClientProfilePage()
        self.base_elements = BaseElements()
        self.inquiries_page = InquiriesPage()
        self.product_offer_form = SelectProductOffersFormElements()
        self.tech_connect_check_form = TechConnectCheckForm()
        self.edit_segments_form = EditSegmentsForm()

    @allure.title("11 Доступность ПП если контекст клиента не определен")
    @allure.id(841530)
    def test_sale_without_client_context(self) -> None:
        with allure.step("Создание продажи через быстрый доступ 'Экспресс ПТВ'"):
            self.base_elements.HELP_NETWORK.click()
            self.tech_connect_check_form.TITLE.wait_to_have_text("Проверка технической возможности подключения")
            self.tech_connect_check_form.ADDRESS_OPTIONS.select_address_by_value(
                input_value=BasicSystemAddress.address,
                select_value=BasicSystemAddress.address,
                field_value=BasicSystemAddress.address,
            )
            self.tech_connect_check_form.SELECT_PRODUCTS_BTN.wait_to_be_enabled(timeout=15000)
            self.tech_connect_check_form.SELECT_PRODUCTS_BTN.click()
            self.product_offer_form.SEGMENT_HEADER_ALERT.wait_to_be_visible()

        with allure.step("Проверка сегмента в форме выбора продуктов"):
            self.product_offer_form.SEGMENT_HEADER.click()
            self.product_offer_form.SEGMENT_CONTENT.to_contain_text("Сегмент не определен")
            self.product_offer_form.SEGMENT_CONTENT.to_contain_text("Доступны продукты, не связанные с сегментами")

        with allure.step("Поиск продуктов"):
            self.inquiries_page.search_products_in_form(product_category_name="Интернет", product_type="Монопродукт")
            self.product_offer_form.PRODUCT_CARD.wait_to_have_count(0)

    @allure.title("12 Доступность ПП если сегмент клиента не определен")
    @pytest.mark.skip(reason="На данный момент при фильтрации используется не значение сегмента, а юр. тип клиента")
    @allure.id(841529)
    def test_sale_with_undefined_segment(self) -> None:
        self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/customer")

        with allure.step("Установка сегмента 'Не определен' клиенту"):
            self.client_profile.locators.SEGMENTS_TAB.wait_to_be_enabled(timeout=15000)
            self.client_profile.locators.SEGMENTS_TAB.click()
            self.client_profile.locators.SEGMENTS_MANAGEMENT_BTN.wait_to_be_enabled(timeout=15000)
            self.client_profile.locators.SEGMENTS_MANAGEMENT_BTN.click()
            self.edit_segments_form.SEARCH_SEGMENTS_VALUE_FLD.select_by_value("Cегмент клиента не определен")
            self.edit_segments_form.SAVE_SEGMENT_BTN.click()

        with allure.step("Создание продажи"):
            self.inquiries_page.sale_initialization(
                test_context.client, need_contact_data=False, priority="Высокий", add_kp="no"
            )
            self.inquiries_page.locators.ADD_SALE_BTN.click()
            self.product_offer_form.SEGMENT_HEADER_ALERT.wait_to_be_visible()

        with allure.step("Проверка сегмента в форме выбора продуктов"):
            self.product_offer_form.SEGMENT_HEADER.click()
            self.product_offer_form.SEGMENT_CONTENT.to_contain_text("Сегмент не определен")
            self.product_offer_form.SEGMENT_CONTENT.to_contain_text("Доступны продукты, не связанные с сегментами")

        with allure.step("Поиск продуктов"):
            self.inquiries_page.search_products_in_form(product_category_name="Интернет", product_type="Монопродукт")
            self.product_offer_form.PRODUCT_CARD.wait_to_have_count(0)

    @allure.title("13 Доступность ПП по сегменту клиента")
    @allure.id(841527)
    def test_sale_with_b2b_segment(self) -> None:
        self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")

        with allure.step("Создание продажи"):
            self.inquiries_page.sale_initialization(
                test_context.client, need_contact_data=False, priority="Высокий", add_kp="no"
            )
            self.inquiries_page.locators.ADD_SALE_BTN.click()

        with allure.step("Проверка сегмента в форме выбора продуктов"):
            self.product_offer_form.SEGMENT_HEADER.click()
            self.product_offer_form.SEGMENT_CONTENT.to_contain_text("B2B обычный")

        with allure.step("Поиск продуктов"):
            self.inquiries_page.search_products_in_form(product_category_name="Интернет", product_type="Монопродукт")
            self.product_offer_form.PRODUCT_CARD.not_to_contain_text_in_any(product_names_map[B2CProducts.internet])

    @allure.title("14 Недоступность ПП по сегменту клиента")
    @allure.id(841534)
    def test_unavailable_product_for_b2b_segment(self) -> None:
        self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")

        with allure.step("Создание продажи"):
            self.inquiries_page.sale_initialization(
                test_context.client, need_contact_data=False, priority="Высокий", add_kp="no"
            )
            self.inquiries_page.locators.ADD_SALE_BTN.click()

        with allure.step("Проверка сегмента в форме выбора продуктов"):
            self.product_offer_form.SEGMENT_HEADER.click()
            self.product_offer_form.SEGMENT_CONTENT.to_contain_text("B2B обычный")

        with allure.step("Поиск продуктов"):
            self.inquiries_page.search_products_in_form(product_category_name="Интернет", product_type="Монопродукт")
            self.product_offer_form.PRODUCT_CARD.not_to_contain_text_in_any(product_names_map[B2CProducts.internet])
            self.product_offer_form.PRODUCT_CARD.to_contain_text_in_any(product_names_map[B2BProducts.internet])
            self.inquiries_page.search_products_in_form(
                product_category_name="Технические услуги", product_type="Монопродукт"
            )
            self.product_offer_form.PRODUCT_CARD.to_contain_text_in_any(
                product_names_map[UnsegmentedProducts.technical_service]
            )
