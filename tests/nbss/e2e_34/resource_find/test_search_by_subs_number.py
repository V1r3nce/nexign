import allure
import pytest
from playwright.sync_api import APIRequestContext, Page

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
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
class TestSearchBySubscriberNumber:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login: Page, api_request_context: APIRequestContext) -> None:
        self.home_page = HomePage()
        self.client_profile_page = ClientProfilePage()
        self.client_inquiries = ClientInquiriesRequests()

    @allure.title("Поиск по номеру телефона абонента (defPhoneNumber/abcPhoneNumber)")
    @allure.id(637194)
    def test_search_client_by_subscriber_number(
        self, create_organization_with_agreement_and_account: OrganizationClient
    ) -> None:
        with allure.step("Подготовка предусловия: продажа мобильного продукта клиенту через API"):
            self.client_inquiries.product_sale(inquiry=prepare_inquiries("mobile"))

        with allure.step("Переход на страницу расширенного поиска и очистка фильтров"):
            self.home_page.go_to_search_and_clear_filters()

        with allure.step("Выполнить поиск клиента по номеру телефона"):
            self.client_profile_page.client_search_page.SUBSCRIBER.fill(test_context.client.inquiry.product.phone_number)
            self.client_profile_page.client_search_page.SEARCH_BTN.click()

        with allure.step("Проверка найденного клиента"):
            self.home_page.verify_client_found(test_context.client)

        with allure.step("Статус найденного клиента — действующий"):
            self.client_profile_page.client_search_page.FOUNDED_CUSTOMER_STATUS[0].to_contain_text("Действующий")
