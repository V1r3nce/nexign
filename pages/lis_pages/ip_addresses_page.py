from playwright.sync_api import Page

from pages.ui_elements import Element, ElementsList
from pages.base_page import BasePage
from pages.locators.lis_locators.ip_addresses_elements import IpAdressesElementsLis


class IPAddressPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        self.locators = IpAdressesElementsLis(page)

    def check_into_out_service(self, expected_ip: str | list, is_in_service: bool):
        first_elements = 15
        self.locators.IP_LIST.wait_elements_visible(first_elements)
        
        ip_list = self.locators.IP_LIST
        status_list = self.locators.STATUS_LIST
        state_list = self.locators.STATE_LIST

        for i in range(0,15):
            for ip in expected_ip:
                if ip_list[i].text == ip:
                    if is_in_service:
                        status_list[i].to_contain_text("Свободен")
                        state_list[i].to_contain_text("Открыт для использования") 
                    else:
                        status_list[i].to_contain_text("Недоступен")
                        state_list[i].to_contain_text("Закрыт для использования")
                    return

        raise AssertionError(f"Ip со значением '{expected_ip}' не найден в списке")

    def click_template_in_list(self, temp_name_list: ElementsList, template_name: str) -> None:
        for i, temp_name in enumerate(temp_name_list):
            if temp_name.text == template_name:
                temp_name_list[i].click()
                break
        else:
            raise AssertionError(f"Шаблон с именем '{temp_name}' не найден в списке")
        
    def check_ip_types_list(self, addresses_count: int, type_value: str) -> None:
        for i in range(addresses_count):
            self.locators.IP_TYPE_LIST[i].to_contain_text(type_value)