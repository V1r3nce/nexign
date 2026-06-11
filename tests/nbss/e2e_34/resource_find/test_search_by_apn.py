import allure
import pytest
from playwright.sync_api import Page

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from api.nbss.client_requests.client_requests import ClientRequests
from common.enums.user import User
from models.client import OrganizationClient
from models.context import test_context
from models.inquiry import prepare_inquiries
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.home_page import HomePage


@pytest.mark.regress
@pytest.mark.nbss_portal
@allure.epic("E2E_34 Поиск клиента/абонента")
@allure.suite("E2E_34 Поиск клиента/абонента")
class TestSearchByApn:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login: Page) -> None:
        self.home_page = HomePage()
        self.client_profile_page = ClientProfilePage()
        self.client_inquiries_api = ClientInquiriesRequests()
        self.client_api = ClientRequests()

    @allure.title("02. Расширенный поиск абонента по APN опции продукта")
    @allure.id(866818)
    def test_search_client_by_apn_option(
        self, create_organization_with_agreement_and_account: OrganizationClient
    ) -> None:
        with allure.step("Подготовка APN, закрепление клиента за APN, продажа продукта с опцией с APN"):
            self.client_api.add_apn_and_add_customer_lock()
            self.client_inquiries_api.product_sale(
                inquiry=prepare_inquiries("satellite_rent", additional_product="Корпоративный доступ к VPN(L3)")
            )

        with allure.step("Переход на страницу расширенного поиска и очистка фильтров"):
            self.home_page.go_to_search_and_clear_filters()

        with allure.step("Валидация полей на форме расширенного поиска"):
            self.home_page.verify_input_parametrs()

        with allure.step("Выполнить поиск клиента по APN"):
            self.home_page.search_client(apn=test_context.client.apn.name)

        with allure.step("Проверка найденного клиента"):
            self.home_page.verify_client_found(test_context.client)

    @allure.title("03. Расширенный поиск абонента по APN и IP адресу опции (оборудования)")
    @allure.id(866935)
    def test_search_client_by_apn_and_ip_address_option(
        self, create_organization_with_agreement_and_account: OrganizationClient
    ) -> None:
        with allure.step("Подготовка APN, закрепление клиента за APN, продажа продукта с опцией с APN"):
            self.client_api.add_apn_and_add_customer_lock()
            self.client_inquiries_api.product_sale(
                inquiry=prepare_inquiries("satellite_sale", additional_product="Корпоративный доступ к VPN(L3)")
            )

        with allure.step("Переход на страницу расширенного поиска и очистка фильтров"):
            self.home_page.go_to_search_and_clear_filters()

        with allure.step("Валидация полей на форме расширенного поиска"):
            self.home_page.verify_input_parametrs()

        with allure.step("Выполнить поиск клиента по APN и IP-адресу"):
            self.home_page.search_client(
                apn=test_context.client.apn.name,
                ip_adress=test_context.client.inquiry.product.additional_product.ip_address.address,
            )

        with allure.step("Проверка найденного клиента"):
            self.home_page.verify_client_found(test_context.client)

    @allure.title("04. Расширенный поиск абонента по APN продукта без роли")
    @allure.id(866790)
    @pytest.mark.user(User.FINANCE_TEST)
    def test_search_client_by_apn_no_role(self):
        with allure.step("Экранная форма расширенного поиска клиента/абонента недоступна"):
            self.home_page.locators.SETTINGS_BTN.wait_to_be_visible(timeout=25000)
            self.home_page.locators.HEADER_SEARCH_BTN.not_to_be_visible()
