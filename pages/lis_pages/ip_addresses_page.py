import allure

from pages.base_page import BasePage
from pages.locators.lis_locators.ip_addresses_elements import IpAdressesLisElements
from pages.ui_elements import Element


class IPAddressPage(BasePage):
    def __init__(self) -> None:
        super().__init__()

        self.locators = IpAdressesLisElements()

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

    @allure.step("Выбрать ip адреса")
    def choose_ip(self, expected_ip: str | list) -> None:
        expected_ip = [expected_ip] if isinstance(expected_ip, str) else expected_ip
        self.locators.IP_LIST.wait_elements_visible(len(expected_ip))
        for ip in expected_ip:
            self.locators.IP_LIST.wait_for_text_in_all([ip])
            ip_index = self.locators.IP_LIST.text_list.index(ip)
            self.locators.CHECKBOX_LIST.click(ip_index)

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
