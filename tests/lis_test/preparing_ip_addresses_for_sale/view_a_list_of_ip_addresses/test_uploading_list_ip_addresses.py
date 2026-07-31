import allure
import pytest

from common.helpers.download_helper import CheckFile
from common.helpers.time_helpers import delay
from models.context import test_context
from pages.base_page import BasePage
from pages.lis_pages.ip_addresses_page import IPAddressPage
from pages.locators.lis_locators.home_elements_lis import HomeLisElements


class TestUploadingListIPAddresses:
    @pytest.fixture(autouse=True)
    def setup(self, stand_login_lis) -> None:
        self.base_page = BasePage()
        self.ip_addresses_page = IPAddressPage()
        self.home_page_lis = HomeLisElements()

    @allure.suite("E2E_16 Подготовка IP-адресов к продаже")
    @allure.title("Выгрузка списка IP-адресов")
    @allure.id(583575)
    @pytest.mark.regress
    @pytest.mark.lis
    @pytest.mark.nbss_portal
    def test_uploading_list_ip_addresses(self, base_url: str, remove_file_from_download_folder: list) -> None:
        with allure.step('Открыть окно "IP-адреса"'):
            self.home_page_lis.IP_ADDRESSES_BTN.wait_to_be_visible()
            delay(0.2, reason="Кнопке нужно время даже после того, как она стала доступной")
            self.home_page_lis.IP_ADDRESSES_BTN.click()
            self.ip_addresses_page.locators.ADDRESS_REFRESH.click()
            self.ip_addresses_page.locators.IP_RESULT_VIEW.wait_to_be_visible()
            self.ip_addresses_page.locators.ADD_ADDRESS_BTN.wait_to_be_visible()
            self.ip_addresses_page.locators.ADDRESS_REFRESH.wait_to_be_visible()
            self.ip_addresses_page.locators.SEARCH_BTN.wait_to_be_visible()
            self.ip_addresses_page.locators.CLEAR_FILTERS_BTN.wait_to_be_visible()
            self.ip_addresses_page.locators.CHOOSE_TEMPLATE_BTN.wait_to_be_visible()
            self.ip_addresses_page.locators.SAVE_TEMPLATE_BTN.wait_to_be_visible()
            ip_list = [self.ip_addresses_page.locators.IP_LIST[i].text for i in range(0, 15)]

        with allure.step('Выбрать все IP-адреса с помощью чекбокса и нажать на кнопку "Выгрузить в файл"'):
            self.ip_addresses_page.locators.ALL_CHECKBOX.click()
            self.ip_addresses_page.locators.DOWNLOAD_BTN.wait_to_be_visible()
            self.ip_addresses_page.locators.DOWNLOAD_BTN.wait_to_be_enabled()
            delay(0.2, reason="Кнопке нужно время даже после того, как она стала доступной")
            self.ip_addresses_page.locators.DOWNLOAD_BTN.click()
            self.ip_addresses_page.locators.MODAL_TITLE.wait_to_be_visible()

            with test_context.page.expect_download() as download_info:
                self.ip_addresses_page.locators.FIRST_BTN_CONFIRMATION.click()
            download = download_info.value
            file_name = download.suggested_filename

            self.file_check = CheckFile(file_name)
            download.save_as(self.file_check.path)
            remove_file_from_download_folder.append(file_name)
            self.file_check.check_excel_file_group_of_fields_contains(
                fields=[[i, 1] for i in range(1, 16)], expected_values=ip_list
            )
