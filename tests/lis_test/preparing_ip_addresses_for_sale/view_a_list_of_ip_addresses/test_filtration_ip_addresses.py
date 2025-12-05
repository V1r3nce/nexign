import allure
import pytest

from common.helpers.time_helpers import delay
from pages.base_page import BasePage
from pages.lis_pages.ip_addresses_page import IPAddressPage
from pages.locators.lis_locators.home_elements_lis import HomeElementsLis


class TestFiltrationIPAddresses:
    @pytest.fixture(autouse=True)
    def setup(self, stand_login_lis) -> None:
        self.base_page = BasePage()
        self.ip_addresses_page = IPAddressPage()
        self.home_page_lis = HomeElementsLis()

    @allure.suite("E2E_16 Подготовка IP-адресов к продаже")
    @allure.title("Просмотр списка IP-адресов(фильтрация)")
    @allure.id(583576)
    @pytest.mark.regress
    @pytest.mark.lis
    @pytest.mark.nbss_portal
    def test_filtration_ip_addresses(self, base_url: str) -> None:
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

        with allure.step('Задать необходимый параметр поиска и нажать кнопку "Найти"'):
            self.ip_addresses_page.locators.IP_TYPE_FILTER_BTN.click()
            self.ip_addresses_page.locators.IP_TYPE_OPTION_EXTERNAL.click()
            self.ip_addresses_page.locators.IP_TYPE_SELECTED_OPTION.to_contain_text("Внешний")
            self.ip_addresses_page.locators.SEARCH_BTN.click()

            first_ip_addresses = 15
            self.ip_addresses_page.locators.IP_TYPE_LIST.wait_elements_visible(first_ip_addresses)
            self.ip_addresses_page.check_ip_types_list(first_ip_addresses, "Внешний")

        with allure.step('Нажать кнопку "Обновить", проверить сохранность фильтра и затем нажать кнопку "Найти"'):
            self.ip_addresses_page.locators.ADDRESS_REFRESH.click()
            self.ip_addresses_page.locators.IP_TYPE_SELECTED_OPTION.to_contain_text("Внешний")

            self.ip_addresses_page.locators.IP_TYPE_FILTER_BTN.click()
            self.ip_addresses_page.locators.IP_TYPE_SELECTED_OPTION.to_contain_text("Внешний")
            self.ip_addresses_page.locators.SEARCH_BTN.click()

            self.ip_addresses_page.locators.IP_TYPE_LIST.wait_elements_visible(first_ip_addresses)
            self.ip_addresses_page.check_ip_types_list(first_ip_addresses, "Внешний")

        with allure.step('Нажать на кнопку "Очистить фильтры"'):
            self.ip_addresses_page.locators.CLEAR_FILTERS_BTN.click()
            self.ip_addresses_page.locators.IP_TYPE_SELECTED_OPTION.not_to_be_visible()
