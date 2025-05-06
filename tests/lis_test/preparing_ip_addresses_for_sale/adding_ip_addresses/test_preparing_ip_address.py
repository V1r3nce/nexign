import allure
import pytest
from playwright.sync_api import Page

from common.helpers.data_generator import generate_random_ip
from common.helpers.time_helpers import delay
from pages.base_page import BasePage
from pages.lis_pages.ip_addresses_page import IPAddressPage
from pages.locators.lis_locators.home_elements_lis import HomeElementsLis


class TestPreparingIPAddresses:
    @pytest.fixture(autouse=True)
    def setup(self, stand_login_lis: Page) -> None:
        self.base_page = BasePage(stand_login_lis)
        self.ip_addresses_page = IPAddressPage(stand_login_lis)
        self.home_page_lis = HomeElementsLis(stand_login_lis)

    @allure.suite("E2E_16 Подготовка IP-адресов к продаже")
    @allure.title("Добавление IP-адресов (успешное добавление, 1 адрес)")
    @allure.id(583275)
    @pytest.mark.regress
    def test_preparing_ip_addresses(self, page: Page, base_url: str) -> None:
        with allure.step('Открыть окно "IP-адреса"'):
            self.home_page_lis.IP_ADDRESSES_BTN.wait_to_be_visible()
            delay(0.2, reason="Кнопке нужно время даже после того, как она стала доступной")
            self.home_page_lis.IP_ADDRESSES_BTN.click()
            self.ip_addresses_page.locators.IP_RESULT_VIEW.wait_to_be_visible()

        with allure.step('Нажать кнопку "Добавить адрес"'):
            self.ip_addresses_page.locators.ADD_ADDRESS_BTN.wait_to_be_visible()
            self.ip_addresses_page.locators.ADD_ADDRESS_BTN.click()
            self.ip_addresses_page.locators.ADD_ADDRESS_MODAL.wait_to_be_visible()

        with allure.step('В поле "Точка доступа" нажать на кнопку Обзор'):
            self.ip_addresses_page.locators.ACCESS_POINT_MORE_BTN.click()
            self.ip_addresses_page.locators.ACCESS_POINT_MODAL.wait_to_be_visible()

        with allure.step('Выбрать точку доступа в списке и нажмите на кнопку "Выбрать"'):
            access_point_name = self.ip_addresses_page.locators.ACCESS_POINT_NAME.text
            self.ip_addresses_page.locators.ACCESS_POINT_OPTION.click()
            self.ip_addresses_page.locators.CHOOSE_BTN.wait_to_be_visible()
            delay(0.2, reason="Кнопке нужно время даже после того, как она стала доступной")
            self.ip_addresses_page.locators.CHOOSE_BTN.click()
            self.ip_addresses_page.locators.ADD_ADDRESS_MODAL.wait_to_be_visible()
            self.ip_addresses_page.locators.ACCESS_POINT_FIELD.to_have_value(access_point_name)

        with allure.step(
            'В блоке "Диапазон IP-адресов" ввести уникальный IP-адрес в поля "Начальное значение" и "Конечное значение" и нажать "Добавить"'
        ):
            ip = generate_random_ip(4)
            self.ip_addresses_page.locators.IP_INITIAL_VALUE.fill(ip)
            self.ip_addresses_page.locators.IP_FINAL_VALUE.fill(ip)
            self.ip_addresses_page.locators.ADD_IP_BTN.click()
            self.ip_addresses_page.locators.CONFIRMATION_IP_MSG.wait_to_be_visible()

        with allure.step('Нажать кнопку "Да"'):
            self.ip_addresses_page.locators.FIRST_BTN_CONFIRMATION.click()
            delay(0.4, reason="Кнопке нужно время даже после того, как она стала доступной")

        with allure.step('Нажать кнопку "ОК"'):
            self.ip_addresses_page.locators.INFORMATION_OK_BTN.wait_to_be_visible()
            self.ip_addresses_page.locators.INFORMATION_OK_BTN.click()
            delay(1, reason="Время создания адреса")

        with allure.step("Нажать кнопку 'Обновить'"):
            self.ip_addresses_page.locators.ADDRESS_REFRESH.wait_to_be_visible()
            self.ip_addresses_page.locators.ADDRESS_REFRESH.click()
            self.ip_addresses_page.locators.IP_LIST.wait_elements_visible(0)

            self.ip_addresses_page.locators.IP_FILTER_BTN.click()
            self.ip_addresses_page.locators.IP_OPTION_VALUE.wait_to_be_visible()
            self.ip_addresses_page.locators.IP_OPTION_VALUE.click()
            self.ip_addresses_page.locators.IP_SELECTED_OPTION.to_contain_text("Точное значение")
            self.ip_addresses_page.locators.IP_START_VALUE.fill(ip)
            self.ip_addresses_page.locators.SEARCH_BTN.click()
            self.ip_addresses_page.locators.IP_LIST.wait_elements_visible(0)
            self.ip_addresses_page.locators.IP_LIST.to_contain_text_in_any(ip)
            self.ip_addresses_page.locators.STATUS_LIST.to_contain_text(0, "Недоступен")
            self.ip_addresses_page.locators.STATE_LIST.to_contain_text(0, "Закрыт для использования")
