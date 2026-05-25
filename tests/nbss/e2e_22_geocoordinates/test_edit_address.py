import allure
import pytest

from api.zookeeper_requests.zookeeper_requests import ZookeeperRequests
from common.helpers.env_helper import BASE_URL
from models.address_info import AlternativeAddress, BasicSystemAddress
from models.client import OrganizationClient
from models.context import test_context
from pages.base_page import BasePage
from pages.nbss.client.client_profile_page import ClientProfilePage


@allure.epic("E2E_22 Управление адресной информацией")
@allure.suite("E2E_22 Управление адресной информацией_Поддержка геокоординат (Этап 0)")
@pytest.mark.extended_regress
@pytest.mark.nbss_portal
class TestEditAddress:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login) -> None:
        self.base_page = BasePage()
        self.client_profile = ClientProfilePage()

        self.address = BasicSystemAddress().address
        self.new_address = AlternativeAddress().address
        self.connection_address_type = "Адрес подключения"
        self.registration_address_type = "Адрес регистрации"

        self.zookeeper_requests = ZookeeperRequests()
        self.zookeeper_requests.check_node_value(ZookeeperRequests.PRAIM_GEOCOORDINATES_PATH_PARTS, "true")
        self.zookeeper_requests.check_node_value(ZookeeperRequests.CSM_GEOCOORDINATES_PATH_PARTS, "PRAIM")
        self.zookeeper_requests.check_node_value(ZookeeperRequests.CFG_GEOCOORDINATES_PATH_PARTS, "1")

    @allure.title("Редактирование адреса")
    @allure.id(824219)
    def test_edit_address(self, create_organization: OrganizationClient) -> None:
        with allure.step("Перейти в карточку клиента"):
            self.base_page.open(
                f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/customer"
            )
            self.client_profile.locators.CLIENT_FIO.wait_to_be_visible(timeout=15000)

        with allure.step("В вертикальном меню выбрать пункт 'Адреса'"):
            self.client_profile.locators.ADDRESSES_TAB.click()

        with allure.step("Добавить адрес из справочника"):
            self.client_profile.add_address(address_type=self.connection_address_type, address=self.address)

        with allure.step("Проверить недоступность редактирования адреса с типом 'Адрес подключения'"):
            self.client_profile.locators.TABLE_ADDRESSES.wait_to_be_visible()
            self.client_profile.locators.TABLE_ADDRESS_LINES.get_element_by_text(self.connection_address_type).click()
            self.client_profile.locators.EDIT_ADDRESS.wait_to_be_visible()
            self.client_profile.locators.EDIT_ADDRESS.not_to_be_enabled()

        with allure.step("Отредактировать адрес с типом 'Адрес регистрации' и сохранить"):
            self.client_profile.locators.TABLE_ADDRESS_LINES.get_element_by_text(self.registration_address_type).click()
            self.client_profile.edit_address(address=self.new_address)

        with allure.step("Проверить отображение отредактированного адреса в таблице"):
            self.client_profile.locators.TABLE_ADDRESSES.wait_to_be_visible()
            self.client_profile.locators.TABLE_ADDRESS_LINES.get_element_by_text(
                self.registration_address_type
            ).to_contain_text(self.new_address)

        with allure.step("Проверить отображение изменения адреса на форме История изменения атрибутов"):
            self.client_profile.locators.HISTORY_BTN.wait_to_be_visible()
            self.client_profile.locators.HISTORY_BTN.click()
            self.client_profile.locators.HISTORY_TABLE_ROWS.wait_to_be_visible()
            self.client_profile.locators.HISTORY_TABLE_ROWS[0].to_contain_text(self.address)
            self.client_profile.locators.HISTORY_TABLE_ROWS[0].to_contain_text(self.new_address)
