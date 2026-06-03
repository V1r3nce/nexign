import re

import allure
import pytest

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from api.nbss.client_requests.client_requests import ClientRequests
from common.helpers.data_generator import get_shifted_datetime_string
from common.helpers.env_helper import BASE_URL
from common.helpers.string_helper import check_price
from models.client import OrganizationClient
from models.context import test_context
from models.inquiry import prepare_inquiries
from pages.base_page import BasePage
from pages.locators.base_elements import BaseElements
from pages.locators.nbss.inquiries_elements import ProductEditForm
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.inquiries_page import InquiriesPage


@allure.epic("E2E_62_11 Продвжв кликнту B2B")
@allure.suite("E2E_62_11 Продажа клиенту B2B (Активация продуктов с даты, зафиксированной с клиентом)")
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestOnDateActivation:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login, create_organization_with_agreement_and_account: OrganizationClient) -> None:
        self.base_page = BasePage()
        self.client_profile = ClientProfilePage()
        self.client_requests = ClientRequests()
        self.client_request_api = ClientInquiriesRequests()
        self.base_elements = BaseElements()
        self.inquiries_page = InquiriesPage()
        self.product_edit_form = ProductEditForm()

        self.product_category = "satellite_rent"
        self.additional_product = "Корпоративный доступ к VPN(L3)"

    @allure.title("04. Проверка даты активации (минимальное, максимальное значение)")
    @allure.id(883963)
    def test_date_more_adn_less_than_limit_range(self, base_url: str) -> None:
        activation_date_less = get_shifted_datetime_string("-1d", False)
        activation_date_more = get_shifted_datetime_string("+100d", False)
        text_for_check = re.compile(
            r"Дата активации не входит в валидный вычисляемый период "
            r"\(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2} - "
            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\)\."
        )

        with allure.step(
            f"Продажа продукта с типом активации = ON_DATE, {self.product_category}, {self.additional_product}"
        ):
            self.client_requests.add_apn_and_add_customer_lock()
            self.client_request_api.product_sale(
                inquiry=prepare_inquiries(self.product_category, additional_product=self.additional_product),
            )
        with allure.step("Выбрать некорректную дату активации, меньше завтрашнего дня"):
            self.base_page.open(f"{BASE_URL}inquiries/{test_context.client.inquiry.id}")
            self.inquiries_page.activation_date_fill(activation_date=activation_date_less, inquiry_finish_need=False)
            self.inquiries_page.locators.ACTIVATION_DATE_MESSAGE.to_contain_text(
                text_for_check,
                timeout_sec=15,
            )
        self.inquiries_page.product_edit_form.INNER_CANCEL_BTN.click()
        with allure.step("Выбрать некорректную дату активации, превышающую срок в 90 дней"):
            self.base_page.open(f"{BASE_URL}inquiries/{test_context.client.inquiry.id}")
            self.inquiries_page.activation_date_fill(activation_date=activation_date_more, inquiry_finish_need=False)
            self.inquiries_page.locators.ACTIVATION_DATE_MESSAGE.to_contain_text(
                text_for_check,
                timeout_sec=15,
            )

    @allure.title("02. Отложенная активация. Ручная смена даты активации (единичное изменение)")
    @allure.id(883964)
    def test_success_limit_range_change_single(self, base_url: str) -> None:
        activation_date = get_shifted_datetime_string("+1d", False)
        with allure.step(
            f"Продажа продукта с типом активации = ON_DATE, {self.product_category}, {self.additional_product}"
        ):
            self.client_requests.add_apn_and_add_customer_lock()
            self.client_request_api.product_sale(
                inquiry=prepare_inquiries(self.product_category, additional_product=self.additional_product),
            )
        with allure.step("Выбрать корректную дату активации, не превышающую срок в 90 дней"):
            self.base_page.open(f"{BASE_URL}inquiries/{test_context.client.inquiry.id}")
            self.inquiries_page.activation_date_fill(activation_date)
        with allure.step("Перейти в 'Продукты' клиента и проверить изменения"):
            self.base_page.open(
                f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/products"
            )
            self.inquiries_page.locators.ORDER_DESCRIPTION.to_contain_text_in_any(
                f"Ожидает активации с {activation_date}",
                timeout=30,
            )

    @allure.title("01. Отложенная активация. Ручная смена даты активации (массовое изменение)")
    @allure.id(883965)
    def test_success_limit_range_change_multiple(self, base_url: str) -> None:
        activation_date = get_shifted_datetime_string("+1d", False)
        with allure.step(
            f"Продажа продукта с типом активации = ON_DATE, {self.product_category}, {self.additional_product}"
        ):
            self.client_requests.add_apn_and_add_customer_lock()
            self.client_requests.add_apn_and_add_customer_lock()

            self.client_request_api.product_sale(
                inquiry=prepare_inquiries(
                    [self.product_category, self.product_category],
                    additional_product=[self.additional_product, self.additional_product],
                    as_list=False,
                )
            )

        with allure.step("Выбрать корректную дату активации, не превышающую срок в 90 дней"):
            self.base_page.open(f"{BASE_URL}inquiries/{test_context.client.inquiry.id}")
            self.inquiries_page.activation_date_fill(activation_date)
        with allure.step("Перейти в 'Продукты' клиента и проверить изменения"):
            self.base_page.open(
                f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/products"
            )
            self.inquiries_page.locators.ORDER_DESCRIPTION.to_contain_text_in_any(
                f"Ожидает активации с {activation_date}",
                timeout=30,
            )

    @allure.title(
        "03. Отложенная активация. Ручная смена даты активации (единичное изменение) (с индивидуализацией цены)"
    )
    @allure.id(883966)
    def test_success_limit_range_change_single_price_individualization(self, base_url: str) -> None:
        activation_date = get_shifted_datetime_string("+1d", False)
        with allure.step(
            f"Продажа продукта с типом активации = ON_DATE, {self.product_category}, {self.additional_product}"
        ):
            self.client_requests.add_apn_and_add_customer_lock()
            self.client_request_api.product_sale(
                inquiry=prepare_inquiries(
                    self.product_category, additional_product=self.additional_product, individualized_subs_fee=30000
                ),
            )
        with allure.step("Выбрать корректную дату активации, не превышающую срок в 90 дней"):
            self.base_page.open(f"{BASE_URL}inquiries/{test_context.client.inquiry.id}")
            self.inquiries_page.activation_date_fill(activation_date)
        with allure.step("Перейти в 'Продукты' клиента и проверить изменения"):
            self.base_page.open(
                f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/products"
            )
            self.inquiries_page.locators.ORDER_DESCRIPTION.to_contain_text_in_any(
                f"Ожидает активации с {activation_date}",
                timeout=30,
            )
            check_price(
                self.inquiries_page.locators.PRICE_AFTER_PRICE_CHANGE[0],
                test_context.client.inquiry.product.individualized_subs_fee,
            )
