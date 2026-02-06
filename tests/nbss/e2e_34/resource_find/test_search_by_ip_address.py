import allure
import pytest
from playwright.sync_api import APIRequestContext, Page

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from api.nbss.client_requests.client_requests import ClientRequests
from models.client import OrganizationClient
from models.context import test_context
from models.inquiry import prepare_inquiries
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.home_page import HomePage


@pytest.mark.regress
@pytest.mark.nbss_portal
@allure.epic("E2E_34 Поиск клиента/абонента")
@allure.suite("E2E_34 Поиск клиента/абонента")
@allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=674672853", name="Поиск клиента/абонента")
class TestSearchByIpAddress:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login: Page, api_request_context: APIRequestContext) -> None:
        self.home_page = HomePage()
        self.client_profile_page = ClientProfilePage()
        self.client_inquiries_api = ClientInquiriesRequests()
        self.client_api = ClientRequests()

    @allure.title("Поиск по IP-адресу ресурса (ipAddress)")
    @allure.id(623050)
    def test_search_client_by_ip_address(
        self, create_organization_with_agreement_and_account: OrganizationClient
    ) -> None:
        with allure.step("Подготовка APN и IP-адресов, закрепление клиента за APN"):
            self.client_api.add_apn_and_add_customer_lock()
            self.client_inquiries_api.product_sale(
                inquiry=prepare_inquiries("satellite_sale", additional_product="Корпоративный доступ к VPN(L3)")
            )

        with allure.step("Переход на страницу расширенного поиска и очистка фильтров"):
            self.home_page.go_to_search_and_clear_filters()

        with allure.step("Выполнить поиск клиента по IP-адресу"):
            self.client_profile_page.client_search_page.IP_ADDRESS.fill(
                test_context.client.inquiry.product.additional_product.ip_address.address
            )
            self.client_profile_page.client_search_page.SEARCH_BTN.click()

        with allure.step("Проверка найденного клиента"):
            self.home_page.verify_client_found(test_context.client)

        with allure.step("Статус найденного клиента — действующий"):
            self.client_profile_page.client_search_page.FOUNDED_CUSTOMER_STATUS[0].to_contain_text("Действующий")
