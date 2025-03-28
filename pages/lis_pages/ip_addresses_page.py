from playwright.sync_api import Page

from pages.base_page import BasePage
from pages.locators.lis_locators.ip_addresses_elements import IpAdressesElementsLis
from pages.ui_elements import Element


class IPAddressPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        self.locators = IpAdressesElementsLis(page)

    def check_into_out_service(self, expected_ip: str | list, is_in_service: bool) -> None:
        first_elements = 15
        self.locators.IP_LIST.wait_elements_visible(first_elements)

        ip_list = self.locators.IP_LIST
        status_list = self.locators.STATUS_LIST
        state_list = self.locators.STATE_LIST

        expected_ip = [expected_ip] if isinstance(expected_ip, str) else expected_ip

        for i in range(15):
            if ip_list[i].text in expected_ip:
                status = "Свободен" if is_in_service else "Недоступен"
                state = "Открыт для использования" if is_in_service else "Закрыт для использования"

                status_list[i].to_contain_text(status)
                state_list[i].to_contain_text(state)
                return

        raise AssertionError(f"Ip со значением '{expected_ip}' не найден в списке")

    @staticmethod
    def click_template_in_list(temp_name_list: list[Element], template_name: str) -> None:
        for i, temp_name in enumerate(temp_name_list):
            if temp_name.text == template_name:
                temp_name_list[i].click()
                break
        else:
            raise AssertionError(f"Шаблон с именем '{temp_name_list}' не найден в списке")

    def check_ip_types_list(self, addresses_count: int, type_value: str) -> None:
        for i in range(addresses_count):
            self.locators.IP_TYPE_LIST[i].to_contain_text(type_value)
