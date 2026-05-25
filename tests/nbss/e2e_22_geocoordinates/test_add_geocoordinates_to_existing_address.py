import random

import allure
import pytest

from common.helpers.env_helper import BASE_URL
from models.address_info import BasicSystemAddress
from models.client import OrganizationClient
from models.context import test_context
from pages.base_page import BasePage
from pages.nbss.client.client_profile_page import ClientProfilePage


@allure.epic("E2E_22 Управление адресной информацией")
@allure.suite("E2E_22 Управление адресной информацией_Поддержка геокоординат (Этап 0)")
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestAddGeocoordinatesToExistingAddress:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login) -> None:
        self.base_page = BasePage()
        self.client_profile = ClientProfilePage()

        self.address = BasicSystemAddress()
        self.latitude = f"{random.randint(0, 90)}.{random.randint(100000, 999999)}"
        self.longitude = f"{random.randint(0, 180)}.{random.randint(100000, 999999)}"
        self.connection_address = f"{self.address.address};{self.latitude.rstrip('0')};{self.longitude.rstrip('0')}"
        self.connection_address_type = "Адрес подключения"

    @allure.title("Добавление геокоординат к существующему адресу")
    @allure.id(867266)
    def test_add_geocoordinates_to_existing_address(self, create_organization: OrganizationClient) -> None:
        with allure.step("Перейти в карточку клиента"):
            self.base_page.open(
                f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/customer"
            )
            self.client_profile.locators.CLIENT_FIO.wait_to_be_visible(timeout=15000)

        with allure.step("В вертикальном меню выбрать пункт 'Адреса'"):
            self.client_profile.locators.ADDRESSES_TAB.click()

        with allure.step("Добавить адрес, выбрать тип адреса, ввести широту и долготу, нажать Сохранить"):
            self.client_profile.add_address(
                address_type=self.connection_address_type,
                address=self.address.address,
                latitude=self.latitude,
                longitude=self.longitude,
            )

        with allure.step("Проверить значение нового адреса в таблице"):
            self.client_profile.locators.TABLE_ADDRESSES.wait_to_be_visible()
            self.client_profile.locators.TABLE_ADDRESS_LINES.wait_to_have_count(2)
            self.client_profile.locators.TABLE_ADDRESSES.get_element_by_text(self.connection_address).wait_to_have_text(
                self.connection_address
            )
