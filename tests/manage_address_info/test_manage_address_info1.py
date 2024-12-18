import pytest
import allure
from playwright.sync_api import Page, APIRequestContext

from api.requests.client_requests import ClientRequests
from common.time_helpers import delay
from models.address_info import AddressInfo
from pages.base_page import BasePage
from pages.client_profile_page import ClientProfilePage
from pages.locators.dynamic_form_elements import EditAddressInfo


@allure.epic("Управление адресной информацией")
class TestManageAddressInfo1:
    @pytest.fixture(autouse=True)
    def setup(self, page: Page, add_new_address_to_lam: dict, create_user: str):
        self.base_page = BasePage(page)
        self.client_profile_page = ClientProfilePage(page)
        self.edit_address_info = EditAddressInfo(page)
        self.new_address = add_new_address_to_lam["addressString"]
        self.new_client_id = create_user

    @allure.title("Добавление адреса. Ввод всех полей")
    def test_add_address_input_all_fields(self, page: Page, base_url: str):
        allure.id("525413")
        page.goto(f"{base_url}customer-hierarchy-management/customers/{self.new_client_id}/overview")
        short_address = self.new_address.split("ул. ")[1]
        self.client_profile_page.click_client_tab()
        self.client_profile_page.locators.ADDRESSES_TAB.click()
        delay(1, reason="Без ожидания пустой список адресов")
        self.client_profile_page.locators.ADD_BTN.click()
        self.client_profile_page.add_address_element.TITLE.to_contain_text("Добавление адреса")
        self.client_profile_page.add_address_element.ADDRESS_TYPE_FIELD.click()
        self.client_profile_page.choose_option_with_name("Фактический адрес")
        self.client_profile_page.add_address_element.ADDRESS_INPUT.fill(short_address)
        self.client_profile_page.add_address_element.ADDRESS_OPTION.to_contain_text(element_index=0, text=short_address)
        self.client_profile_page.add_address_element.ADDRESS_OPTION.click(element_index=0)
        self.client_profile_page.add_address_element.SAVE_BTN.to_be_enabled()
        self.client_profile_page.add_address_element.MAPS_LINK_INPUT.fill(AddressInfo.map_link)
        self.client_profile_page.add_address_element.SAVE_BTN.click()
        self.client_profile_page.add_address_element.CANCEL_BTN.not_to_be_visible()
        self.client_profile_page.locators.TABLE_LINE.to_contain_text(element_index=2,
                                                                     text=f"Фактический адрес{self.new_address}")
        self.edit_address_info.TABLE_LINE_MAP_BUTTON.wait_elements_visible(element_index=0)

    @allure.title("Добавление адреса. Ввод всех полей")
    def test_add_address_linked_person(self, page: Page, base_url: str, api_request_auth_context: APIRequestContext):
        allure.id("533011")
        client_request_api = ClientRequests(api_request_auth_context)
        linked_person_name = "мать драконов"
        short_address = self.new_address.split("ул. ")[1]
        client_request_api.create_linked_person(client_id=self.new_client_id, name=linked_person_name)
        page.goto(f"{base_url}customer-hierarchy-management/customers/{self.new_client_id}/overview")
        self.client_profile_page.locators.RELATED_PERSONS_TAB.click()
        self.client_profile_page.locators.RELATED_PERSON_NAME.to_have_value(linked_person_name)
        self.client_profile_page.locators.ADDRESSES_EDIT_BTN.click()
        self.edit_address_info.ADD_BUTTON.wait_to_be_visible()
        self.edit_address_info.ADD_BUTTON.click()
        self.client_profile_page.add_address_element.TITLE.to_contain_text("Добавление адреса")
        self.client_profile_page.add_address_element.ADDRESS_TYPE_FIELD.click()
        self.client_profile_page.choose_option_with_name("Адрес регистрации")
        self.client_profile_page.add_address_element.ADDRESS_INPUT.fill(short_address)
        self.client_profile_page.add_address_element.ADDRESS_OPTION.to_contain_text(element_index=0, text=short_address)
        self.client_profile_page.add_address_element.ADDRESS_OPTION.click(element_index=0)
        self.client_profile_page.add_address_element.SAVE_BTN.to_be_enabled()
        self.client_profile_page.add_address_element.MAPS_LINK_INPUT.fill(AddressInfo.map_link)
        self.client_profile_page.add_address_element.SAVE_BTN.click()
        self.edit_address_info.TABLE_LINE.to_contain_text(element_index=1, text=f"Адрес регистрации{self.new_address}")
        self.edit_address_info.TABLE_LINE_MAP_BUTTON.wait_elements_visible(element_index=0)
        self.edit_address_info.CANCEL_BTN.click()
        self.edit_address_info.CANCEL_BTN.not_to_be_visible()
        self.client_profile_page.locators.RELATED_ADDRESS.to_contain_text(self.new_address)

    @allure.title("Добавление адреса. Ввод только обязательных полей")
    def test_add_address_input_required_fields(self, page: Page, base_url: str):
        allure.id("525412")
        page.goto(f"{base_url}customer-hierarchy-management/customers/{self.new_client_id}/overview")
        short_address = self.new_address.split("ул. ")[1]
        self.client_profile_page.click_client_tab()
        self.client_profile_page.locators.ADDRESSES_TAB.click()
        delay(1, reason="Без ожидания пустой список адресов")
        self.client_profile_page.locators.ADD_BTN.click()
        self.client_profile_page.add_address_element.TITLE.to_contain_text("Добавление адреса")
        self.client_profile_page.add_address_element.ADDRESS_TYPE_FIELD.click()
        self.client_profile_page.choose_option_with_name("Фактический адрес")
        self.client_profile_page.add_address_element.ADDRESS_INPUT.fill(short_address)
        self.client_profile_page.add_address_element.ADDRESS_OPTION.to_contain_text(element_index=0, text=short_address)
        self.client_profile_page.add_address_element.ADDRESS_OPTION.click(element_index=0)
        self.client_profile_page.add_address_element.SAVE_BTN.to_be_enabled()
        self.client_profile_page.add_address_element.SAVE_BTN.click()
        self.client_profile_page.add_address_element.CANCEL_BTN.not_to_be_visible()
        self.client_profile_page.locators.TABLE_LINE.to_contain_text(element_index=2,
                                                                     text=f"Фактический адрес{self.new_address}")

    @allure.title("Добавление адреса. Ввод только обязательных полей")
    def test_add_address_linked_person_required_fields(self, page: Page, base_url: str,
                                                       api_request_auth_context: APIRequestContext):
        allure.id("533012")
        client_request_api = ClientRequests(api_request_auth_context)
        linked_person_name = "мать драконов"
        short_address = self.new_address.split("ул. ")[1]
        client_request_api.create_linked_person(client_id=self.new_client_id, name=linked_person_name)
        page.goto(f"{base_url}customer-hierarchy-management/customers/{self.new_client_id}/overview")
        self.client_profile_page.locators.RELATED_PERSONS_TAB.click()
        self.client_profile_page.locators.RELATED_PERSON_NAME.to_have_value(linked_person_name)
        self.client_profile_page.locators.ADDRESSES_EDIT_BTN.click()
        self.edit_address_info.ADD_BUTTON.wait_to_be_visible()
        self.edit_address_info.ADD_BUTTON.click()
        self.client_profile_page.add_address_element.TITLE.to_contain_text("Добавление адреса")
        self.client_profile_page.add_address_element.ADDRESS_TYPE_FIELD.click()
        self.client_profile_page.choose_option_with_name("Адрес регистрации")
        self.client_profile_page.add_address_element.ADDRESS_INPUT.fill(short_address)
        self.client_profile_page.add_address_element.ADDRESS_OPTION.to_contain_text(element_index=0, text=short_address)
        self.client_profile_page.add_address_element.ADDRESS_OPTION.click(element_index=0)
        self.client_profile_page.add_address_element.SAVE_BTN.to_be_enabled()
        self.client_profile_page.add_address_element.SAVE_BTN.click()
        self.edit_address_info.TABLE_LINE.to_contain_text(element_index=1, text=f"Адрес регистрации{self.new_address}")
        self.edit_address_info.CANCEL_BTN.click()
        self.edit_address_info.CANCEL_BTN.not_to_be_visible()
        self.client_profile_page.locators.RELATED_ADDRESS.to_contain_text(self.new_address)
