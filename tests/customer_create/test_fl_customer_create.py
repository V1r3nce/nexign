import pytest
import allure
from playwright.sync_api import Page, APIRequestContext

from api.requests.client_requests import ClientRequests
from common.time_helpers import delay
from models.address_info import AddressInfo, BasicSystemAddress
from pages.base_page import BasePage
from pages.client_profile_page import ClientProfilePage
from pages.locators.dynamic_form_elements import EditAddressInfo, FlCustomerCreate, DynamicForms
from pages.locators.home_page_elements import HomePage


class TestManageAddressInfo1:
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.base_page = BasePage(page)
        self.home_page = HomePage(page)
        self.customer_create_form = FlCustomerCreate(page)
        self.client_profile_page = ClientProfilePage(page)
        self.edit_address_info = EditAddressInfo(page)

    @allure.suite("E2E_64 Создание и управление клиентом и его иерархиями")
    @allure.title("Создание ФЛ клиента, заполнены все поля")
    @allure.id(484399)
    def test_fl_customer_create(self, base_url: str):
        self.home_page.CREATE_CUSTOMER_BTN.click()
        self.customer_create_form.LAST_NAME.wait_to_be_visible()
        self.customer_create_form.fill_data_for_individual_client()
        self.customer_create_form.SAVE_BTN.click()

        self.home_page.CUSTOMER_NAME.fill("Тестович")
        self.home_page.HEADER_SEARCH_BTN.click()