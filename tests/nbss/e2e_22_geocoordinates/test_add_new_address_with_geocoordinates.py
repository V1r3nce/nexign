import random

import allure
import pytest

from common.helpers.data_generator import generate_random_number
from common.helpers.env_helper import BASE_URL
from models.address_info import AddressInfo
from models.client import OrganizationClient
from models.context import test_context
from pages.base_page import BasePage
from pages.nbss.client.client_profile_page import ClientProfilePage


@allure.epic("E2E_22 Управление адресной информацией")
@allure.suite("E2E_22 Управление адресной информацией_Поддержка геокоординат (Этап 0)")
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestAddNewAddressWithGeocoordinates:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login) -> None:
        self.base_page = BasePage()
        self.client_profile = ClientProfilePage()

        self.address = AddressInfo()
        self.building_number = generate_random_number(3)
        self.flat_number = generate_random_number(2)
        self.latitude = f"{random.randint(0, 90)}.{random.randint(100000, 999999)}"
        self.longitude = f"{random.randint(0, 180)}.{random.randint(100000, 999999)}"
        self.connection_address = (
            f"{self.address.country}, {self.address.region}, {self.address.city}, "
            f"{self.address.street}, д. {self.building_number}, кв. {self.flat_number};"
            f"{self.latitude.rstrip('0')};{self.longitude.rstrip('0')}"
        )
        self.connection_address_type = "Адрес подключения"

    @allure.title("Создание нового адреса с геокоординатами.")
    @allure.id(838874)
    def test_add_new_address_with_geocoordinates(self, create_organization: OrganizationClient) -> None:
        with allure.step("Перейти в карточку клиента"):
            self.base_page.open(
                f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/customer"
            )
            self.client_profile.locators.CLIENT_FIO.wait_to_be_visible(timeout=15000)

        with allure.step("В вертикальном меню выбрать пункт 'Адреса', нажать кнопку '+Добавить'"):
            self.client_profile.locators.ADDRESSES_TAB.click()
            self.client_profile.locators.ADD_BTN.wait_to_be_visible()
            self.client_profile.locators.ADD_BTN.click()

        with allure.step("Выбрать тип адреса, ввести адрес, нажать Добавить адрес в справочник"):
            self.client_profile.add_address_form.TITLE.to_contain_text("Добавление адреса")
            self.client_profile.add_address_form.ADDRESS_TYPE_FIELD.select_by_value(self.connection_address_type)
            self.client_profile.add_address_form.ADDRESS_INPUT.fill(self.address.address)
            self.client_profile.add_address_form.ADD_ADDRESS_TO_CATALOG.to_contain_text("Добавить адрес в справочник")
            self.client_profile.add_address_form.ADD_ADDRESS_TO_CATALOG.click()

        with allure.step("Заполнить поля для добавления адреса в справочник"):
            self.client_profile.fill_required_fields_client_new_address(
                country=self.address.country,
                region=self.address.region,
                city=self.address.city,
                street=self.address.street,
                building_number=self.building_number,
                flat_number=self.flat_number,
            )
            self.client_profile.create_address_form.ADD_ADDRESS_OBJECT_BTN.not_to_be_visible()

        with allure.step("Нажать кнопку Создать"):
            self.client_profile.create_address_form.CREATE_BTN.click()
            self.client_profile.create_address_form.TITLE.not_to_be_visible()
            self.client_profile.add_address_form.TITLE.wait_to_be_visible()

        with allure.step("Заполнить поля широты и долготы"):
            self.client_profile.add_address_form.LATITUDE_INPUT.fill(self.latitude)
            self.client_profile.add_address_form.LONGITUDE_INPUT.fill(self.longitude)

        with allure.step("Нажать кнопку Добавить"):
            self.client_profile.add_address_form.SAVE_BTN.click()
            self.client_profile.add_address_form.CANCEL_BTN.not_to_be_visible(timeout=10000)

        with allure.step("Проверить значение нового адреса в таблице"):
            self.client_profile.locators.TABLE_ADDRESSES.wait_to_be_visible()
            self.client_profile.locators.TABLE_ADDRESSES.get_element_by_text(self.connection_address).wait_to_have_text(
                self.connection_address
            )
