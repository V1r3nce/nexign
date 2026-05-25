import random

import allure
import pytest

from common.helpers.env_helper import BASE_URL
from models.client import OrganizationClient
from models.context import test_context
from pages.base_page import BasePage
from pages.nbss.client.client_profile_page import ClientProfilePage


@allure.epic("E2E_22 Управление адресной информацией")
@allure.suite("E2E_22 Управление адресной информацией_Поддержка геокоординат (Этап 0)")
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestAddNewAddressWithGeocoordinatesWithErrors:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login) -> None:
        self.base_page = BasePage()
        self.client_profile = ClientProfilePage()

        self.latitude = f"{random.randint(0, 90)}.{random.randint(100000, 999999)}"
        self.longitude = f"{random.randint(0, 180)}.{random.randint(100000, 999999)}"
        self.connection_address = f"{self.latitude.rstrip('0')};{self.longitude.rstrip('0')}"
        self.connection_address_type = "Адрес подключения"

    @allure.title("Добавление нового адреса с геокоординатами(ошибка ввода)")
    @allure.id(839324)
    def test_add_new_address_with_geocoordinates_with_errors(self, create_organization: OrganizationClient) -> None:
        with allure.step("Перейти в карточку клиента"):
            self.base_page.open(
                f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/customer"
            )
            self.client_profile.locators.CLIENT_FIO.wait_to_be_visible(timeout=15000)

        with allure.step("В вертикальном меню выбрать пункт 'Адреса', нажать кнопку '+Добавить'"):
            self.client_profile.locators.ADDRESSES_TAB.click()
            self.client_profile.locators.ADD_BTN.wait_to_be_visible()
            self.client_profile.locators.ADD_BTN.click()

        with allure.step("Выбрать тип адреса, ввести широту, нажать Сохранить"):
            self.client_profile.add_address_form.TITLE.to_contain_text("Добавление адреса")
            self.client_profile.add_address_form.ADDRESS_TYPE_FIELD.select_by_value(self.connection_address_type)
            self.client_profile.add_address_form.LATITUDE_INPUT.fill(self.latitude)
            self.client_profile.add_address_form.SAVE_BTN.to_be_enabled()
            self.client_profile.add_address_form.SAVE_BTN.click()

            self.client_profile.add_address_form.ERROR_MESSAGE.wait_to_have_text(
                "Необходимо указать хотя бы адрес или координаты. При заполнении координат необходимо заполнить оба поля: и широту, и долготу."
            )

        with allure.step("Ввести долготу и нажать Добавить"):
            self.client_profile.add_address_form.LONGITUDE_INPUT.fill(self.longitude)

            self.client_profile.add_address_form.SAVE_BTN.click()
            self.client_profile.add_address_form.CANCEL_BTN.not_to_be_visible()

        with allure.step("Проверить значение нового адреса в таблице"):
            self.client_profile.locators.TABLE_ADDRESSES.wait_to_be_visible()
            self.client_profile.locators.TABLE_ADDRESS_LINES.wait_to_have_count(2)
            self.client_profile.locators.TABLE_ADDRESSES.get_element_by_text(self.connection_address).wait_to_have_text(
                self.connection_address
            )
