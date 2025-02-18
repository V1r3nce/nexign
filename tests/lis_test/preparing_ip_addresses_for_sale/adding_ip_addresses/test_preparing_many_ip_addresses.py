import pytest
import allure
from playwright.sync_api import Page

from common.helpers.time_helpers import delay
from common.helpers.data_generator import generate_random_ip
from pages.base_page import BasePage
from pages.lis_pages.ip_addresses_page import IPAddressPage
from pages.locators.lis_locators.home_elements_lis import HomeElementsLis

class TestPreparingManyIPAddresses:
    @pytest.fixture(autouse=True)
    def setup(self, stand_login_lis: Page):
        self.base_page = BasePage(stand_login_lis)
        self.ip_addresses_page = IPAddressPage(stand_login_lis)
        self.home_page_lis = HomeElementsLis(stand_login_lis)
    
    @allure.suite("E2E_16 Подготовка IP-адресов к продаже")
    @allure.title("Добавление IP-адресов (успешное добавление, несколько адресов)")
    @allure.id(583300)
    def test_preparing_many_ip_addresses(self, page: Page, base_url: str):

        with allure.step('Открыть окно "IP-адреса"'):
            self.home_page_lis.IP_ADDRESSES_BTN.click()
            self.ip_addresses_page.locators.IP_RESULT_VIEW.wait_to_be_visible()

        with allure.step('Нажать кнопку "Добавить адрес"'):
            self.ip_addresses_page.locators.ADD_ADDRESS_BTN.click()
            self.ip_addresses_page.locators.ADD_ADDRESS_MODAL.wait_to_be_visible()

        with allure.step('В поле "Точка доступа" нажать на кнопку Обзор'):
            self.ip_addresses_page.locators.ACCESS_POINT_MORE_BTN.click()
            self.ip_addresses_page.locators.ACCESS_POINT_MODAL.wait_to_be_visible()

        with allure.step('Выбрать точку доступа в списке и нажмите на кнопку "Выбрать"'):
            access_point_name = self.ip_addresses_page.locators.ACCESS_POINT_NAME.text
            self.ip_addresses_page.locators.ACCESS_POINT_OPTION.click()
            delay(.3, reason="Кнопке нужно время даже после того, как она стала доступной")
            self.ip_addresses_page.locators.CHOOSE_BTN.click()
            self.ip_addresses_page.locators.ADD_ADDRESS_MODAL.wait_to_be_visible()
            self.ip_addresses_page.locators.ACCESS_POINT_FIELD.to_have_value(access_point_name)

        with allure.step('В блоке "Диапазон IP-адресов" ввести уникальные IP-адрес в поля "Начальное значение" и "Конечное значение" (превосходящее предыдущее) и нажать "Добавить"'):
            ip_base = generate_random_ip(3)
            start_ip = f"{ip_base}.100"
            end_ip = f"{ip_base}.104"
            self.ip_addresses_page.locators.IP_INITIAL_VALUE.fill(start_ip)
            self.ip_addresses_page.locators.IP_FINAL_VALUE.fill(end_ip)
            self.ip_addresses_page.locators.ADD_IP_BTN.click()
            self.ip_addresses_page.locators.CONFIRMATION_IP_MSG.wait_to_be_visible()

        with allure.step('Нажать кнопку "Да" и после нажать кнопку "ОК"'):
            self.ip_addresses_page.locators.FIRST_BTN_CONFIRMATION.click()
            delay(.3, reason="Кнопке нужно время даже после того, как она стала доступной")

            self.ip_addresses_page.locators.INFORMATION_OK_BTN.click()
            delay(1, reason="Время создания адреса")

        with allure.step("Нажать кнопку 'Обновить'"):
            self.ip_addresses_page.locators.ADDRESS_REFRESH.wait_to_be_visible()
            self.ip_addresses_page.locators.ADDRESS_REFRESH.click()
            self.ip_addresses_page.locators.IP_LIST.wait_elements_visible(1)
            start_parts = list(map(int, start_ip.split(".")))
            end_parts = list(map(int, end_ip.split(".")))
            ips_range = [f"{ip_base}.{i}" for i in range(start_parts[3], end_parts[3] + 1)]
            
            self.ip_addresses_page.locators.IP_FILTER_BTN.click()
            self.ip_addresses_page.locators.IP_OPTION_INTERVAL.click()
            self.ip_addresses_page.locators.IP_SELECTED_OPTION.to_contain_text("По диапазону")
            self.ip_addresses_page.locators.IP_START_VALUE.fill(start_ip)
            self.ip_addresses_page.locators.IP_END_VALUE.fill(end_ip)
            self.ip_addresses_page.locators.SEARCH_BTN.click()
            self.ip_addresses_page.locators.IP_LIST.wait_elements_visible(4)
            for ip in ips_range:
                self.ip_addresses_page.locators.IP_LIST.to_contain_text_in_any(ip)
            for status in self.ip_addresses_page.locators.STATUS_LIST:
                status.to_contain_text("Недоступен")
            for state in self.ip_addresses_page.locators.STATE_LIST: 
                state.to_contain_text("Закрыт для использования")
