import allure
import pytest
from playwright.sync_api import Page

from common.helpers.data_generator import generate_random_number
from common.helpers.time_helpers import delay
from pages.base_page import BasePage
from pages.lis_pages.ip_addresses_page import IPAddressPage
from pages.locators.lis_locators.home_elements_lis import HomeElementsLis


class TestSearchTemplate:
    @pytest.fixture(autouse=True)
    def setup(self, stand_login_lis: Page) -> None:
        self.base_page = BasePage(stand_login_lis)
        self.ip_addresses_page = IPAddressPage(stand_login_lis)
        self.home_page_lis = HomeElementsLis(stand_login_lis)

    @allure.suite("E2E_16 Подготовка IP-адресов к продаже")
    @allure.title("Просмотр списка IP-адресов(шаблон поиска)")
    @allure.id(583579)
    @pytest.mark.regress
    def test_search_template(self, page: Page, base_url: str) -> None:
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

        with allure.step('Нажать кнопку "Сохранить шаблон поиска" и выбрать"Новый шаблон"'):
            self.ip_addresses_page.locators.SAVE_TEMPLATE_BTN.click()
            self.ip_addresses_page.locators.TEMPLATE_OPTION_NEW.click()
            self.ip_addresses_page.locators.TEMPLATE_TITLE.wait_to_be_visible()

        with allure.step('Ввести наименование шаблона и нажать кнопку "Сохранить"'):
            template_name = "Шаблон " + str(generate_random_number(3))
            self.ip_addresses_page.locators.NEW_TEMPLATE_NAME.fill(template_name)
            self.ip_addresses_page.locators.TEMPLATE_SAVE_BTN.click()

        with allure.step('Нажать на кнопку "Очистить фильтры"'):
            self.ip_addresses_page.locators.CLEAR_FILTERS_BTN.wait_to_be_visible()
            self.ip_addresses_page.locators.CLEAR_FILTERS_BTN.click()
            self.ip_addresses_page.locators.IP_TYPE_SELECTED_OPTION.not_to_be_visible()

        with allure.step('Нажать на кнопку "Выбрать шаблон поиска" и выбрать ранее созданный шаблон'):
            self.ip_addresses_page.locators.CHOOSE_TEMPLATE_BTN.click()
            self.ip_addresses_page.locators.TEMPLATE_NAMES_LIST.wait_to_be_visible()
            temp_name_list = self.ip_addresses_page.locators.TEMPLATE_NAMES_LIST
            self.ip_addresses_page.click_template_in_list(temp_name_list, template_name)

            self.ip_addresses_page.locators.IP_TYPE_SELECTED_OPTION.to_contain_text("Внешний")
            first_ip_addresses = 15
            self.ip_addresses_page.locators.IP_TYPE_LIST.wait_elements_visible(first_ip_addresses)
            self.ip_addresses_page.check_ip_types_list(first_ip_addresses, "Внешний")

        with allure.step('Нажать на кнопку "Удалить текущий шаблон" и подтвердить операцию'):
            self.ip_addresses_page.locators.DELETE_TEMPLATE_BTN.click()
            self.ip_addresses_page.locators.MODAL_TITLE.wait_elements_visible(1)
            self.ip_addresses_page.locators.FIRST_BTN_CONFIRMATION.click()
            self.ip_addresses_page.locators.IP_TYPE_SELECTED_OPTION.not_to_be_visible()
