import pytest
import allure
from playwright.sync_api import Page

from common.helpers.time_helpers import delay
from pages.base_page import BasePage
from pages.lis_pages.ip_addresses_page import IPAddressPage
from pages.lis_pages.operation_monitor import OperationMonitorPage
from pages.locators.lis_locators.home_elements_lis import HomeElementsLis

class TestPreparingSameIPAddresses:
    @pytest.fixture(autouse=True)
    def setup(self, stand_login_lis: Page):
        self.base_page = BasePage(stand_login_lis)
        self.ip_addresses_page = IPAddressPage(stand_login_lis)
        self.operation_monitor_page = OperationMonitorPage(stand_login_lis)
        self.home_page_lis = HomeElementsLis(stand_login_lis)

    @allure.suite("E2E_16 Подготовка IP-адресов к продаже")
    @allure.title("Добавление IP-адресов (неуспешное добавление, повторное значение)")
    @allure.id(583306)
    def test_preparing_same_ip_address(self, page: Page, base_url: str):
        
        with allure.step('Открыть окно "IP-адреса"'):
            self.home_page_lis.MENU_LINK_LIST.wait_elements_visible(11)
            self.home_page_lis.IP_ADDRESSES_BTN.wait_to_be_visible()
            self.home_page_lis.IP_ADDRESSES_BTN.to_be_enabled()
            delay(.2, reason="Кнопке нужно время даже после того, как она стала доступной")
            self.home_page_lis.IP_ADDRESSES_BTN.click()
            self.ip_addresses_page.locators.IP_RESULT_VIEW.wait_to_be_visible()
            self.ip_addresses_page.locators.ADDRESS_REFRESH.click()
            self.ip_addresses_page.locators.IP_LIST.wait_elements_visible(1)
            ip = self.ip_addresses_page.locators.IP_LIST[0].inner_html()

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

        with allure.step('В блоке "Диапазон IP-адресов" ввести уже имеющийся в системе IP-адрес в поля "Начальное значение" и "Конечное значение" и нажать "Добавить"'):
            self.ip_addresses_page.locators.IP_INITIAL_VALUE.fill(ip)
            self.ip_addresses_page.locators.IP_FINAL_VALUE.fill(ip)
            self.ip_addresses_page.locators.ADD_IP_BTN.click()
            self.ip_addresses_page.locators.CONFIRMATION_IP_MSG.wait_to_be_visible()

        with allure.step('Нажать кнопку "Да" и после нажать кнопку "ОК"'):
            self.ip_addresses_page.locators.FIRST_BTN_CONFIRMATION.click()
            delay(.3, reason="Кнопке нужно время даже после того, как она стала доступной")

            self.ip_addresses_page.locators.INFORMATION_OK_BTN.click()
            delay(3, reason="Время создания адреса")

        with allure.step("Открыть окно 'Монитор операций'"):
            self.home_page_lis.OPERATION_MONITOR_BTN.click()
            self.operation_monitor_page.locators.STATE_LIST.to_contain_text(0, "Ошибка")

        with allure.step("Дважды щелкнуть в любом месте строки первой записи"):
            self.home_page_lis.OPERATION_MONITOR_BTN.click(click_count = 2)
            self.operation_monitor_page.locators.STATE_LIST[0].click(click_count = 2)
            self.operation_monitor_page.locators.MODAL_TITLE.wait_elements_visible(-1)
            self.operation_monitor_page.locators.MODAL_TITLE[-1].to_contain_text("Информация по операции")
            self.operation_monitor_page.locators.MODAL_RESPONSE_BTN.click()
            self.operation_monitor_page.locators.RESPONSE_ERROR_TEXT.wait_to_be_visible()
            err_text = f'{{"conflicts":[{{"code":null,"type":"ERROR","message":"Resource (IP address) cant be created because of unique constraints","fieldName":"IPAddress","fieldValue":"{ip}"}}]}}'
            self.operation_monitor_page.locators.RESPONSE_ERROR_TEXT.to_contain_text(err_text)
