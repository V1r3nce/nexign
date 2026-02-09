import allure
import pytest
from playwright.sync_api import APIRequestContext

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from models.client import OrganizationClient
from models.context import test_context
from models.inquiry import prepare_inquiries
from pages.nbss.client.client_profile_page import ClientProfilePage


@pytest.mark.regress
@pytest.mark.nbss_portal
@allure.epic("E2E_34 Поиск клиента/абонента")
@allure.suite("E2E_34 Поиск клиента/абонента")
@allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=674672853", name="Поиск клиента/абонента")
class TestSearchProductProfileByIp:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login, api_request_context: APIRequestContext, base_url: str) -> None:
        self.page = nexign_stand_login
        self.client_profile_page = ClientProfilePage()
        self.client_inquiries = ClientInquiriesRequests()
        self.base_url = base_url

    @allure.title("06. Поиск ресурсов по продуктовому профилю (ip адрес)")
    @allure.id(637217)
    def test_search_resources_by_product_profile_ip(
        self, create_organization_with_agreement_and_account: OrganizationClient
    ) -> None:
        with allure.step("Подготовка предусловия: продажа интернет-продукта со статическим IP клиенту через API"):
            self.client_inquiries.product_sale(
                inquiry=prepare_inquiries("internet", additional_product="Статический IP")
            )

        with allure.step("Открыть профиль клиента и перейти во вкладку 'Продукты'"):
            self.client_profile_page.open(
                f"{self.base_url}customer-hierarchy-management/customers/{test_context.client.user_id}/overview"
            )
            self.client_profile_page.locators.PRODUCTS_TAB.wait_to_be_visible(timeout=15000)
            self.client_profile_page.locators.PRODUCTS_TAB.click()

        with allure.step("Открыть форму 'Настройки ресурсов'"):
            self.client_profile_page.locators.PRODUCTS_FILTER_SETTINGS_BTN.wait_to_be_visible(timeout=15000)
            self.client_profile_page.locators.PRODUCTS_FILTER_SETTINGS_BTN.click()

        with allure.step("Ввести IP-адрес ресурса и выполнить поиск"):
            self.client_profile_page.locators.PRODUCTS_FILTER_IP_INPUT.wait_to_be_visible(timeout=15000)
            self.client_profile_page.locators.PRODUCTS_FILTER_IP_INPUT.fill(
                test_context.client.inquiry.product.additional_product.ip_address.address
            )

            self.client_profile_page.locators.SAVE_BTN.click()

        with allure.step("Проверка результатов поиска в продуктовом профиле"):
            self.client_profile_page.locators.PRODUCTS_LIST.wait_to_be_visible(timeout=15000)
