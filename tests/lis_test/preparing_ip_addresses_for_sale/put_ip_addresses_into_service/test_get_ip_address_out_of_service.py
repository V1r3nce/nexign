import allure
import pytest

from api.lis_requests.table_requests import TableRequests
from common.helpers.checker import assert_that
from common.helpers.env_helper import BASE_URL_API
from common.helpers.time_helpers import delay
from pages.base_page import BasePage
from pages.lis_pages.ip_addresses_page import IPAddressPage
from pages.locators.lis_locators.home_elements_lis import HomeLisElements


@pytest.mark.lis
@pytest.mark.parametrize("add_new_ip_addresses_to_lis", [1], indirect=True)
class TestGetIPAddressOutOfService:
    @pytest.fixture(autouse=True)
    def setup(self, stand_login_lis) -> None:
        self.base_page = BasePage()
        self.ip_addresses_page = IPAddressPage()
        self.home_page_lis = HomeLisElements()

    @allure.suite("E2E_16 Подготовка IP-адресов к продаже")
    @allure.title("Вывод IP-адресов из эксплуатации (1 адрес)")
    @allure.id(583582)
    @pytest.mark.regress
    def test_get_ip_address_out_of_service(self, base_url: str, add_new_ip_addresses_to_lis: str) -> None:
        table_requests = TableRequests()
        ip_list, id_list = table_requests.get_table_by_reverse_status(base_url_api=BASE_URL_API)
        table_requests.put_ip_addresses_into_service(BASE_URL_API, ip_address_id=id_list[0])

        with allure.step('Открыть окно "IP-адреса"'):
            self.home_page_lis.IP_ADDRESSES_BTN.wait_to_be_visible()
            delay(0.2, reason="Кнопке нужно время даже после того, как она стала доступной")
            self.home_page_lis.IP_ADDRESSES_BTN.click()
            self.ip_addresses_page.locators.IP_RESULT_VIEW.wait_to_be_visible()
            self.ip_addresses_page.locators.ADD_ADDRESS_BTN.wait_to_be_visible()
            self.ip_addresses_page.locators.ADDRESS_REFRESH.wait_to_be_visible()
            self.ip_addresses_page.locators.SEARCH_BTN.wait_to_be_visible()
            self.ip_addresses_page.locators.CLEAR_FILTERS_BTN.wait_to_be_visible()
            self.ip_addresses_page.locators.CHOOSE_TEMPLATE_BTN.wait_to_be_visible()
            self.ip_addresses_page.locators.SAVE_TEMPLATE_BTN.wait_to_be_visible()

        with allure.step('Выбрать IP-адрес, нажав чекбокс и нажать кнопку "Исключить"'):
            self.ip_addresses_page.locators.IP_STATUS_BTN.click()
            self.ip_addresses_page.locators.IP_STATUS_OPTION_AVAILABLE.click()
            self.ip_addresses_page.locators.IP_STATUS_SELECTED_OPTION.to_contain_text("Свободен")
            self.ip_addresses_page.locators.IP_STATUS_BTN.click()
            self.ip_addresses_page.locators.SEARCH_BTN.click()

            self.ip_addresses_page.locators.DATE_STATUS_CHANGED.click()
            self.ip_addresses_page.locators.DATE_STATUS_CHANGED.wait_to_be_enabled()
            self.ip_addresses_page.locators.DATE_STATUS_CHANGED.click()
            self.ip_addresses_page.locators.IP_LIST.wait_elements_visible(15)
            self.ip_addresses_page.locators.CHECKBOX_LIST[0].click()
            ip = self.ip_addresses_page.locators.IP_LIST[0].text
            assert_that(
                lambda: ip == ip_list[0],
                f"Выбранный ip '{ip}' и введенный в эксплуатацию ip '{ip_list[0]}' не совпадают",
            )
            self.ip_addresses_page.locators.OUT_OF_SERVICE_BTN.wait_to_be_enabled()
            delay(0.2, reason="Кнопке нужно время даже после того, как она стала доступной")
            self.ip_addresses_page.locators.OUT_OF_SERVICE_BTN.click()

        with allure.step('Нажать кнопку "Да" и затем нажать кнопку "Обновить"'):
            self.ip_addresses_page.locators.MODAL_TITLE.wait_to_be_visible()
            self.ip_addresses_page.locators.FIRST_BTN_CONFIRMATION.wait_to_be_visible()
            self.ip_addresses_page.locators.FIRST_BTN_CONFIRMATION.click()

            self.ip_addresses_page.locators.CLEAR_FILTERS_BTN.wait_to_be_enabled()
            self.ip_addresses_page.locators.CLEAR_FILTERS_BTN.click()
            self.ip_addresses_page.locators.DATE_STATUS_CHANGED.click()
            self.ip_addresses_page.locators.DATE_STATUS_CHANGED.wait_to_be_enabled()
            self.ip_addresses_page.locators.DATE_STATUS_CHANGED.click()
            self.ip_addresses_page.check_into_out_service(ip, False)
