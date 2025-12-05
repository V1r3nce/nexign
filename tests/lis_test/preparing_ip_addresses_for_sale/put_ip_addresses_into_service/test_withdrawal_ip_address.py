import allure
import pytest

from common.helpers.checker import assert_that
from common.helpers.time_helpers import delay
from pages.base_page import BasePage
from pages.lis_pages.ip_addresses_page import IPAddressPage
from pages.locators.lis_locators.home_elements_lis import HomeElementsLis


@pytest.mark.parametrize("add_new_ip_addresses_to_lis", [1], indirect=True)
class TestWithdrawalIpAddress:
    @pytest.fixture(autouse=True)
    def setup(self, stand_login_lis) -> None:
        self.base_page = BasePage()
        self.ip_addresses_page = IPAddressPage()
        self.home_page_lis = HomeElementsLis()

    @allure.suite("E2E_16 Подготовка IP-адресов к продаже")
    @allure.title("Изъятие IP-адресов (1 адрес)")
    @allure.id(583583)
    @pytest.mark.regress
    @pytest.mark.lis
    @pytest.mark.nbss_portal
    def test_withdrawal_ip_address(self, base_url: str, add_new_ip_addresses_to_lis: list) -> None:
        ip_address = add_new_ip_addresses_to_lis

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

        with allure.step('Выбрать IP-адрес, нажав чекбокс и нажать кнопку "Изъять"'):
            self.ip_addresses_page.locators.IP_STATUS_BTN.click()
            self.ip_addresses_page.locators.IP_STATUS_OPTION_UNAVAILABLE.click()
            self.ip_addresses_page.locators.IP_STATUS_SELECTED_OPTION.to_contain_text("Недоступен")
            self.ip_addresses_page.locators.IP_STATUS_BTN.click()
            self.ip_addresses_page.locators.SEARCH_BTN.click()

            self.ip_addresses_page.locators.DATE_STATUS_CHANGED.click()
            self.ip_addresses_page.locators.DATE_STATUS_CHANGED.wait_to_be_visible()
            self.ip_addresses_page.locators.DATE_STATUS_CHANGED.click()
            self.ip_addresses_page.locators.IP_LIST.wait_elements_visible(0)
            self.ip_addresses_page.locators.CHECKBOX_LIST[0].click()
            ip = self.ip_addresses_page.locators.IP_LIST[0].text
            assert_that(
                lambda: ip == ip_address, f"Созданный ip-адрес '{ip_address}' отличается от выбранного ip-адреса '{ip}'"
            )
            self.ip_addresses_page.locators.WITHDRAWAL_BTN.wait_to_be_enabled()
            delay(0.2, reason="Кнопке нужно время после того, как она стала доступной")
            self.ip_addresses_page.locators.WITHDRAWAL_BTN.click()

        with allure.step('Нажать кнопку "Да" и затем нажать кнопку "Обновить"'):
            self.ip_addresses_page.locators.MODAL_TITLE.wait_to_be_visible()
            self.ip_addresses_page.locators.FIRST_BTN_CONFIRMATION.wait_to_be_visible()
            self.ip_addresses_page.locators.FIRST_BTN_CONFIRMATION.click()

            self.ip_addresses_page.locators.CLEAR_FILTERS_BTN.wait_to_be_visible()
            self.ip_addresses_page.locators.CLEAR_FILTERS_BTN.click()
            self.ip_addresses_page.locators.DATE_STATUS_CHANGED.click()
            self.ip_addresses_page.locators.DATE_STATUS_CHANGED.wait_to_be_visible()
            self.ip_addresses_page.locators.DATE_STATUS_CHANGED.click()
            self.ip_addresses_page.locators.IP_LIST.wait_elements_visible(15)
            self.ip_addresses_page.locators.IP_LIST.not_to_contain_text_in_any(ip)
