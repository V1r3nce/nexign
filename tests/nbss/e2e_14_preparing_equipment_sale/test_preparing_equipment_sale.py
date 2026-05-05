import random

import allure
import pytest

from api.lis_requests.directory import DirectoryRequests
from api.rfd_requests.refdata_requests import RefDataRequests
from common.enums.user import User
from common.helpers.data_generator import generate_russian_string
from common.helpers.env_helper import BASE_URL
from common.helpers.time_helpers import delay
from models.address_info import BasicSystemAddress
from models.context import test_context
from pages.locators.nbss.options.points_of_sale import FormAddUserPointsOfSale, FormCreatePointsOfSale, PointsOfSale
from pages.nbss.home_page import HomePage
from pages.nbss.options_page import OptionsPage


@allure.epic("E2E_14 Подготовка оборудования к продаже")
@allure.suite("1. Управление точками продаж")
@pytest.mark.regress
@pytest.mark.influencing
@pytest.mark.nbss_portal
class TestPreparingEquipmentSale:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login) -> None:
        self.home_page = HomePage()
        self.options_page = OptionsPage()
        self.form_create_points_of_sale = FormCreatePointsOfSale()
        self.points_of_sale_page = PointsOfSale()
        self.name = generate_russian_string(10)
        self.code = random.randint(1000, 9999)
        self.status = "Создана"
        self.address = BasicSystemAddress.address
        self.refdata_api = RefDataRequests()
        self.lis_api = DirectoryRequests()
        self.form_add_point = FormAddUserPointsOfSale()

    @pytest.mark.user(User.SELLER_SR_TEST)
    @allure.title('1.01. Сценарий "Создание точки продаж"(clone)')
    @allure.id(825702)
    def test_create_points_sale(self):
        self.options_page.open_points_of_sale_from_menu()
        self.options_page.points_of_sale_page.CREATE_BTN.wait_to_be_enabled(timeout=15000)
        self.options_page.points_of_sale_page.CREATE_BTN.click()
        self.form_create_points_of_sale.INNER_ACCEPT_BTN.wait_to_be_enabled(timeout=15000)
        self.form_create_points_of_sale.INPUT_NAME.fill(self.name)
        self.form_create_points_of_sale.INPUT_CODE.fill(self.code)
        self.form_create_points_of_sale.SELECT_STATUS.select_by_value(self.status)
        self.form_create_points_of_sale.INPUT_ADDRESS.select_address_by_value(self.address, self.address, self.address)
        self.form_create_points_of_sale.INNER_ACCEPT_BTN.click()
        self.options_page.points_of_sale_page.REFRESH_BTN.wait_to_be_enabled(timeout=15000)
        self.options_page.points_of_sale_page.REFRESH_BTN.click()
        self.options_page.points_of_sale_page.FIND_NAME_POINT.fill(self.name)
        self.options_page.points_of_sale_page.POINTS_SALE.to_contain_text_in_any(self.name, timeout=15)
        self.refdata_api.assert_partner_point_exists_by_name(self.name)
        self.lis_api.check_agent_for_resource_exists_by_name(self.name)

    @pytest.mark.user(User.SELLER_SR_TEST)
    @allure.title('1.02. Сценарий "Редактирование точки продаж"(clone)')
    @allure.id(825694)
    def test_edit_points_sale(self):
        status = "Закрыта"
        self.options_page.open_points_of_sale_from_menu()
        self.options_page.points_of_sale_page.CREATE_BTN.wait_to_be_enabled(timeout=15000)
        self.options_page.points_of_sale_page.POINTS_SALE.wait_to_be_visible(timeout=15000)
        name = self.options_page.points_of_sale_page.POINTS_SALE[-1].text
        self.options_page.points_of_sale_page.POINTS_SALE[-1].click(force=True)
        self.options_page.points_of_sale_page.EDIT_BTN.click()
        self.form_create_points_of_sale.INPUT_ADDRESS.select_address_by_value(self.address, self.address, self.address)
        self.form_create_points_of_sale.SELECT_STATUS.select_by_value(status)
        self.form_create_points_of_sale.INPUT_NAME.fill(self.name)
        self.form_create_points_of_sale.INNER_ACCEPT_BTN.click()
        self.options_page.points_of_sale_page.POINTS_SALE.to_contain_text_in_any(name)
        self.refdata_api.assert_partner_point_exists_by_name_and_status(name, status)
        self.lis_api.check_agent_status_by_name(name, status)

    @pytest.mark.user(User.SELLER_SR_TEST)
    @allure.title('1.03. Сценарий "Закрепление точки продаж за пользователем"(clone)')
    @allure.id(825695)
    def test_pin_points_sale(self, create_organization_with_agreement_and_account, cleanup_user_points_of_sale):
        self.home_page.open(
            url=f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/inquiries"
        )
        self.options_page.open_user_points_tab_and_add_points()
        self.options_page.points_of_sale_page.LIST_POINTS_SALE_USER.wait_to_be_visible(timeout=15000)

    @pytest.mark.user(User.SELLER_SR_TEST)
    @allure.title('1.04. Сценарий "Снятие закрепления точки продаж за пользователем"(clone)')
    @allure.id(825696)
    def test_unpin_points_sale(self, create_organization_with_agreement_and_account, cleanup_user_points_of_sale):
        self.home_page.open(
            url=f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/inquiries"
        )
        self.options_page.open_user_points_tab_and_add_points()
        delay(1, "Не успевает выбраться точка продажи, любые другие элементы все еще видны")
        self.options_page.points_of_sale_page.LIST_POINTS_SALE_USER.wait_to_be_visible(timeout=15000)
        self.points_of_sale_page.USERS_VIRTUAL_LIST.select_by_value("SELLER_SR_TEST")
        self.options_page.clear_points_of_sale()
        self.options_page.points_of_sale_page.LIST_POINTS_SALE_USER.wait_not_to_be_visible()

    @pytest.mark.user(User.SELLER_SR_TEST)
    @allure.title('1.05 Сценарий "Автоматический выбор текущей точки продаж пользователя"(clone)')
    @allure.id(825715)
    def test_auto_choose_points_sale(self, create_organization_with_agreement_and_account, cleanup_user_points_of_sale):
        self.home_page.open(
            url=f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/inquiries"
        )
        self.options_page.open_user_points_tab_and_add_points()
        self.options_page.refresh_page(wait="load")
        self.options_page.points_of_sale_page.USER_DROPDOWN_BTN.wait_to_be_visible(timeout=15000)
        self.options_page.points_of_sale_page.USER_DROPDOWN_BTN.click()
        self.options_page.points_of_sale_page.USER_POINTS_SALE.wait_to_be_visible(timeout=30000)

    @pytest.mark.user(User.SELLER_SR_TEST)
    @allure.title('1.06 Сценарий "Изменение текущей точки продаж пользователя"(clone)')
    @allure.id(825716)
    def test_auto_edit_choose_points_sale(
        self, create_organization_with_agreement_and_account, cleanup_user_points_of_sale
    ):
        self.home_page.open(
            url=f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/inquiries"
        )
        self.options_page.open_user_points_tab_and_add_points(0)
        self.options_page.points_of_sale_page.LIST_POINTS_SALE_USER.wait_to_have_count(1, timeout=15000)
        self.options_page.open_user_points_tab_and_add_points(2, need_go_points_sale=False)
        self.options_page.points_of_sale_page.LIST_POINTS_SALE_USER.wait_to_be_visible(timeout=30000)
        self.options_page.refresh_page(wait="load")
        self.options_page.points_of_sale_page.USER_DROPDOWN_BTN.wait_to_be_visible(timeout=15000)
        self.options_page.points_of_sale_page.USER_DROPDOWN_BTN.click()
        self.options_page.points_of_sale_page.EDIT_BTN_POINTS_SALE.wait_to_be_visible(timeout=15000)
        self.options_page.points_of_sale_page.EDIT_BTN_POINTS_SALE.click()
        self.form_add_point.INNER_ACCEPT_BTN.wait_to_be_enabled()
        self.form_add_point.SELECT_POINTS_SALE.select_by_index(1)
        self.form_add_point.INNER_ACCEPT_BTN.click()

    @pytest.mark.user(User.SELLER_SR_TEST)
    @allure.title('1.07 Сценарий "Автоматическое удаление текущей точки продаж у пользователя"(clone)')
    @allure.id(825717)
    def test_auto_delete_choose_points_sale(
        self, create_organization_with_agreement_and_account, cleanup_user_points_of_sale
    ):
        self.home_page.open(
            url=f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/inquiries"
        )
        self.options_page.open_points_of_sale_from_menu()
        self.options_page.open_user_points_tab_and_add_points()
        self.options_page.points_of_sale_page.LIST_POINTS_SALE_USER.wait_to_be_visible(timeout=15000)
        self.points_of_sale_page.USERS_VIRTUAL_LIST.select_by_value("SELLER_SR_TEST")
        self.options_page.clear_points_of_sale()
        self.options_page.points_of_sale_page.LIST_POINTS_SALE_USER.wait_not_to_be_visible()
        self.options_page.refresh_page(wait="load")
        self.options_page.points_of_sale_page.USER_DROPDOWN_BTN.wait_to_be_visible(timeout=15000)
        self.options_page.points_of_sale_page.USER_DROPDOWN_BTN.click()
        self.options_page.points_of_sale_page.EDIT_BTN_POINTS_SALE.not_to_be_visible()
