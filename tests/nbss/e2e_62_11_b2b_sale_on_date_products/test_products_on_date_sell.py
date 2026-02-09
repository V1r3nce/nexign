import allure
import pytest

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from api.nbss.client_requests.client_requests import ClientRequests
from common.helpers.env_helper import BASE_URL
from common.helpers.time_helpers import get_shifted_datetime
from models.client import OrganizationClient
from models.context import test_context
from models.inquiry import prepare_inquiries
from pages.base_page import BasePage
from pages.locators.base_elements import BaseElements
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
        self.product_category = "satellite_rent"
        self.additional_product = "Корпоративный доступ к VPN(L3)"

    @allure.title("02. Неудачная смена даты активации (превышение лимита 90 дней)")
    @allure.id(666867)
    def test_date_more_than_limit_range(self, base_url: str) -> None:
        activation_date = get_shifted_datetime("+91d").strftime("%d.%m.%Y")
        with allure.step(
            f"Продажа продукта с типом активации = ON_DATE, {self.product_category}, {self.additional_product}"
        ):
            self.client_requests.add_apn_and_add_customer_lock()
            self.client_request_api.product_sale(
                inquiry=prepare_inquiries(self.product_category, additional_product=self.additional_product),
            )
        with allure.step("Выбрать некорректную дату активации, превышающую срок в 90 дней"):
            self.base_page.open(f"{BASE_URL}inquiries/{test_context.client.inquiry.id}")
            self.inquiries_page.activation_date_fill(activation_date)
            self.inquiries_page.locators.ACTIVATION_DATE_MESSAGE.to_contain_text(
                "Дата активации не может быть отнесена дальше, чем на 90 дней", timeout_sec=15
            )

    @allure.title("03. Неудачная смена даты активации (дата меньше минимальной)")
    @allure.id(666869)
    def test_less_than_limit_range(self, base_url: str) -> None:
        activation_date = get_shifted_datetime("-1d").strftime("%d.%m.%Y")
        with allure.step(
            f"Продажа продукта с типом активации = ON_DATE, {self.product_category}, {self.additional_product}"
        ):
            self.client_requests.add_apn_and_add_customer_lock()
            self.client_request_api.product_sale(
                inquiry=prepare_inquiries(self.product_category, additional_product=self.additional_product),
            )
        with allure.step("Выбрать некорректную дату активации, превышающую срок в 90 дней"):
            self.base_page.open(f"{BASE_URL}inquiries/{test_context.client.inquiry.id}")
            self.inquiries_page.activation_date_fill(activation_date)
            self.inquiries_page.locators.ACTIVATION_DATE_MESSAGE.to_contain_text(
                "Дата активации не может быть меньше завтрашнего дня", timeout_sec=15000
            )

    @allure.title("05. Успешная смена даты активации (без проверок)")
    @allure.id(763976)
    def test_success_limit_range_change(self, base_url: str) -> None:
        activation_date = get_shifted_datetime("+1d").strftime("%d.%m.%Y")
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
        with allure.step("Проверить состояние Активного шага после изменения даты активации"):
            self.inquiries_page.locators.AGREEMENT_BTN[2].wait_to_be_visible(timeout=20000)
            self.inquiries_page.locators.NEXT_STEP_BTN.to_be_enabled()
            self.inquiries_page.locators.ACTIVATE_DATE[0].to_contain_text(activation_date, timeout_sec=20)
            self.base_page.refresh_page(wait="load")
            self.inquiries_page.locators.PRODUCT_CHECK_STATUS[0].to_contain_text(
                "Технический заказ на изменение даты активации продукта клиента успешно выполнен. Можете завершить продажу",
                timeout_sec=15,
            )
