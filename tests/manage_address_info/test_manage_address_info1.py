import pytest
import allure
from playwright.sync_api import Page, APIRequestContext

from api.requests.client_requests import ClientRequests
from common.string_helper import generate_random_number
from common.time_helpers import delay
from models.address_info import AddressInfo, BasicSystemAddress
from pages.base_page import BasePage
from pages.client_profile_page import ClientProfilePage
from pages.locators.dynamic_form_elements import EditAddressInfo


@allure.epic("Управление адресной информацией")
@allure.suite("Управление адресной информацией")
class TestManageAddressInfo1:
    @pytest.fixture(autouse=True)
    def setup(self, page: Page, add_new_address_to_lam: dict, create_user: str):
        self.base_page = BasePage(page)
        self.client_profile_page = ClientProfilePage(page)
        self.edit_address_info = EditAddressInfo(page)
        self.new_address = add_new_address_to_lam["addressString"]
        self.new_client_id = create_user

    @allure.title("Добавление адреса. Ввод всех полей")
    @allure.id(525413)
    def test_add_address_input_all_fields(self, base_url: str):
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{self.new_client_id}/overview")
        short_address = self.new_address.split("ул. ")[1]

        self.client_profile_page.click_client_tab()
        self.client_profile_page.locators.ADDRESSES_TAB.click()
        delay(1, reason="Без ожидания пустой список адресов")
        self.client_profile_page.locators.ADD_BTN.click()
        self.client_profile_page.add_address_form.TITLE.to_contain_text("Добавление адреса")
        self.client_profile_page.add_address_form.ADDRESS_TYPE_FIELD.select_by_value("Фактический адрес")
        # self.client_profile_page.choose_option_with_name("Фактический адрес")
        self.client_profile_page.add_address_form.ADDRESS_INPUT.fill(short_address)
        self.client_profile_page.add_address_form.ADDRESS_OPTION.to_contain_text(element_index=0, text=short_address)
        self.client_profile_page.add_address_form.ADDRESS_OPTION.click(element_index=0)
        self.client_profile_page.add_address_form.SAVE_BTN.to_be_enabled()
        self.client_profile_page.add_address_form.MAPS_LINK_INPUT.fill(AddressInfo.map_link)
        self.client_profile_page.add_address_form.SAVE_BTN.click()
        self.client_profile_page.add_address_form.CANCEL_BTN.not_to_be_visible()

        self.client_profile_page.locators.TABLE_LINE.to_contain_text(element_index=2,
                                                                     text=f"Фактический адрес{self.new_address}")
        self.edit_address_info.TABLE_LINE_MAP_BUTTON.wait_elements_visible(element_index=0)

    @allure.title("Добавление адреса. Ввод всех полей")
    @allure.id(533011)
    def test_add_address_linked_person(self, base_url: str, api_request_auth_context: APIRequestContext):
        client_request_api = ClientRequests(api_request_auth_context)
        linked_person_name = "мать драконов"
        short_address = self.new_address.split("ул. ")[1]
        client_request_api.create_linked_person(client_id=self.new_client_id, name=linked_person_name)

        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{self.new_client_id}/overview")
        self.client_profile_page.locators.RELATED_PERSONS_TAB.click()
        self.client_profile_page.locators.RELATED_PERSON_NAME.to_have_value(linked_person_name)
        self.client_profile_page.locators.ADDRESSES_EDIT_BTN.click()

        self.edit_address_info.ADD_BUTTON.wait_to_be_visible()
        self.edit_address_info.ADD_BUTTON.click()

        self.client_profile_page.add_address_form.TITLE.to_contain_text("Добавление адреса")
        self.client_profile_page.add_address_form.SAVE_BTN.wait_to_be_visible()
        self.client_profile_page.add_address_form.ADDRESS_TYPE_FIELD.click()
        self.client_profile_page.choose_option_with_name("Адрес регистрации")
        self.client_profile_page.add_address_form.ADDRESS_INPUT.fill(short_address)
        self.client_profile_page.add_address_form.ADDRESS_OPTION.to_contain_text(element_index=0, text=short_address)
        self.client_profile_page.add_address_form.ADDRESS_OPTION.click(element_index=0)
        self.client_profile_page.add_address_form.SAVE_BTN.to_be_enabled()
        self.client_profile_page.add_address_form.MAPS_LINK_INPUT.fill(AddressInfo.map_link)
        self.client_profile_page.add_address_form.SAVE_BTN.click()

        self.edit_address_info.TABLE_LINE.to_contain_text(element_index=1, text=f"Адрес регистрации{self.new_address}")
        self.edit_address_info.TABLE_LINE_MAP_BUTTON.wait_elements_visible(element_index=0)
        self.edit_address_info.CANCEL_BTN.click()

        self.edit_address_info.CANCEL_BTN.not_to_be_visible()
        self.client_profile_page.locators.RELATED_ADDRESS.to_contain_text(self.new_address)

    @allure.title("Добавление адреса. Ввод только обязательных полей")
    @allure.id(525412)
    def test_add_address_input_required_fields(self, base_url: str):
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{self.new_client_id}/overview")
        short_address = self.new_address.split("ул. ")[1]

        self.client_profile_page.click_client_tab()
        self.client_profile_page.locators.ADDRESSES_TAB.click()
        delay(1, reason="Без ожидания пустой список адресов")
        self.client_profile_page.locators.ADD_BTN.click()
        self.client_profile_page.add_address_form.TITLE.to_contain_text("Добавление адреса")
        self.client_profile_page.add_address_form.ADDRESS_TYPE_FIELD.click()
        self.client_profile_page.choose_option_with_name("Фактический адрес")
        self.client_profile_page.add_address_form.ADDRESS_INPUT.fill(short_address)
        self.client_profile_page.add_address_form.ADDRESS_OPTION.to_contain_text(element_index=0, text=short_address)
        self.client_profile_page.add_address_form.ADDRESS_OPTION.click(element_index=0)
        self.client_profile_page.add_address_form.SAVE_BTN.to_be_enabled()
        self.client_profile_page.add_address_form.SAVE_BTN.click()

        self.client_profile_page.add_address_form.CANCEL_BTN.not_to_be_visible()
        self.client_profile_page.locators.TABLE_LINE.to_contain_text(element_index=2,
                                                                     text=f"Фактический адрес{self.new_address}")

    @allure.title("Добавление адреса. Ввод только обязательных полей")
    @allure.id(533012)
    def test_add_address_linked_person_required_fields(self, base_url: str,
                                                       api_request_auth_context: APIRequestContext):
        client_request_api = ClientRequests(api_request_auth_context)
        linked_person_name = "мать драконов"
        short_address = self.new_address.split("ул. ")[1]
        client_request_api.create_linked_person(client_id=self.new_client_id, name=linked_person_name)

        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{self.new_client_id}/overview")
        self.client_profile_page.locators.RELATED_PERSONS_TAB.click()
        self.client_profile_page.locators.RELATED_PERSON_NAME.to_have_value(linked_person_name)
        self.client_profile_page.locators.ADDRESSES_EDIT_BTN.click()

        self.edit_address_info.ADD_BUTTON.wait_to_be_visible()
        self.edit_address_info.ADD_BUTTON.click()

        self.client_profile_page.add_address_form.TITLE.to_contain_text("Добавление адреса")
        self.client_profile_page.add_address_form.SAVE_BTN.wait_to_be_visible()
        self.client_profile_page.add_address_form.ADDRESS_TYPE_FIELD.click()
        self.client_profile_page.choose_option_with_name("Адрес регистрации")
        self.client_profile_page.add_address_form.ADDRESS_INPUT.fill(short_address)
        self.client_profile_page.add_address_form.ADDRESS_OPTION.to_contain_text(element_index=0, text=short_address)
        self.client_profile_page.add_address_form.ADDRESS_OPTION.click(element_index=0)
        self.client_profile_page.add_address_form.SAVE_BTN.to_be_enabled()
        self.client_profile_page.add_address_form.SAVE_BTN.click()

        self.edit_address_info.TABLE_LINE.to_contain_text(element_index=1, text=f"Адрес регистрации{self.new_address}")
        self.edit_address_info.CANCEL_BTN.click()

        self.edit_address_info.CANCEL_BTN.not_to_be_visible()
        self.client_profile_page.locators.RELATED_ADDRESS.to_contain_text(self.new_address)


@allure.epic("Управление адресной информацией")
@allure.suite("Управление адресной информацией")
class TestManageAddressInfo2:
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.base_page = BasePage(page)
        self.client_profile_page = ClientProfilePage(page)
        self.edit_address_info = EditAddressInfo(page)

    @allure.title("Добавление адреса. Ввод уже существующего типа адреса")
    @allure.id(525415)
    def test_add_address_doubled_address_type(self, base_url: str, create_user: str):
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{create_user}/overview")
        short_address = BasicSystemAddress.short_address

        self.client_profile_page.click_client_tab()
        self.client_profile_page.locators.ADDRESSES_TAB.click()
        delay(1, reason="Без ожидания пустой список адресов")
        self.client_profile_page.locators.ADD_BTN.click()
        self.client_profile_page.add_address_form.TITLE.to_contain_text("Добавление адреса")
        self.client_profile_page.add_address_form.ADDRESS_TYPE_FIELD.click()
        self.client_profile_page.choose_option_with_name("Адрес регистрации")
        self.client_profile_page.add_address_form.ADDRESS_INPUT.fill(short_address)
        self.client_profile_page.add_address_form.ADDRESS_OPTION.to_contain_text(element_index=0,
                                                                                 text=BasicSystemAddress.add_address_name)
        self.client_profile_page.add_address_form.ADDRESS_OPTION.click(element_index=0)
        self.client_profile_page.add_address_form.SAVE_BTN.click()

        self.client_profile_page.base_elements.MODAL.wait_to_be_visible()
        self.client_profile_page.base_elements.MODAL_TITLE.to_contain_text("Ошибка")
        self.client_profile_page.base_elements.MODAL_BODY_TEXT.to_contain_text(
            "Для объекта иерархии превышено максимально допустимое количество адресов с переданным типом")
        self.client_profile_page.base_elements.MODAL_COPY_DETAILS_BTN.wait_to_be_visible()
        self.client_profile_page.base_elements.MODAL_COPY_DETAILS_BTN.to_contain_text("Копировать детали")
        self.client_profile_page.base_elements.MODAL_CLOSE_BTN.to_contain_text("Закрыть")
        self.client_profile_page.base_elements.MODAL_CLOSE_BTN.click()

        self.client_profile_page.base_elements.MODAL.not_to_be_visible()
        self.client_profile_page.add_address_form.TITLE.to_contain_text("Добавление адреса")

    @allure.title("Добавление адреса. Ввод уже существующего типа адреса")
    @allure.id(533008)
    def test_add_address_linked_person_doubled_address_type(self, base_url: str,
                                                            api_request_auth_context: APIRequestContext,
                                                            create_user: str):
        client_request_api = ClientRequests(api_request_auth_context)
        user_id = create_user
        linked_person_name = "мать драконов"
        short_address = BasicSystemAddress.short_address
        client_request_api.create_linked_person_with_registration_address(client_id=user_id,
                                                                          name=linked_person_name)

        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{user_id}/overview")
        self.client_profile_page.locators.RELATED_PERSONS_TAB.click()
        self.client_profile_page.locators.RELATED_PERSON_NAME.to_have_value(linked_person_name)
        self.client_profile_page.locators.ADDRESSES_EDIT_BTN.click()

        self.edit_address_info.ADD_BUTTON.wait_to_be_visible()
        self.edit_address_info.ADD_BUTTON.click()

        self.client_profile_page.add_address_form.TITLE.to_contain_text("Добавление адреса")
        self.client_profile_page.add_address_form.SAVE_BTN.wait_to_be_visible()
        self.client_profile_page.add_address_form.ADDRESS_TYPE_FIELD.click()
        self.client_profile_page.choose_option_with_name("Адрес регистрации")
        self.client_profile_page.add_address_form.ADDRESS_INPUT.fill(short_address)
        self.client_profile_page.add_address_form.ADDRESS_OPTION.to_contain_text(element_index=0,
                                                                                 text=BasicSystemAddress.add_address_name)
        self.client_profile_page.add_address_form.ADDRESS_OPTION.click(element_index=0)
        self.client_profile_page.add_address_form.SAVE_BTN.to_be_enabled()
        self.client_profile_page.add_address_form.SAVE_BTN.click()

        self.client_profile_page.base_elements.MODAL.wait_to_be_visible()
        self.client_profile_page.base_elements.MODAL_TITLE.to_contain_text("Ошибка")
        self.client_profile_page.base_elements.MODAL_BODY_TEXT.to_contain_text(
            "Для объекта иерархии превышено максимально допустимое количество адресов с переданным типом")
        self.client_profile_page.base_elements.MODAL_X_BTN.click()

        self.client_profile_page.base_elements.MODAL.not_to_be_visible()
        self.client_profile_page.add_address_form.TITLE.to_contain_text("Добавление адреса")

    @allure.title("Добавление адреса. Отмена добавления")
    @allure.id(525414)
    def test_add_address_reject(self, base_url: str, create_user: str):
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{create_user}/overview")
        short_address = BasicSystemAddress.short_address

        self.client_profile_page.click_client_tab()
        self.client_profile_page.locators.ADDRESSES_TAB.click()
        delay(1, reason="Без ожидания пустой список адресов")
        self.client_profile_page.locators.ADD_BTN.click()
        self.client_profile_page.add_address_form.TITLE.to_contain_text("Добавление адреса")
        self.client_profile_page.add_address_form.ADDRESS_TYPE_FIELD.click()
        self.client_profile_page.choose_option_with_name("Фактический адрес")
        self.client_profile_page.add_address_form.ADDRESS_INPUT.fill(short_address)
        self.client_profile_page.add_address_form.ADDRESS_OPTION.to_contain_text(element_index=0,
                                                                                 text=BasicSystemAddress.add_address_name)
        self.client_profile_page.add_address_form.ADDRESS_OPTION.click(element_index=0)
        self.client_profile_page.add_address_form.SAVE_BTN.to_be_enabled()
        self.client_profile_page.add_address_form.MAPS_LINK_INPUT.fill(AddressInfo.map_link)
        self.client_profile_page.add_address_form.CANCEL_BTN.click()
        self.client_profile_page.add_address_form.CANCEL_BTN.not_to_be_visible()

        self.client_profile_page.locators.TABLE_LINE.to_contain_text(element_index=-1,
                                                                     text=f"Адрес регистрации{BasicSystemAddress.address}")
        assert self.client_profile_page.locators.TABLE_LINE.elements_len() == 2, "Добавилась строка с адресом"

    @allure.title("Добавление адреса. Отмена добавления")
    @allure.id(533010)
    def test_add_address_linked_person_reject(self, base_url: str, api_request_auth_context: APIRequestContext,
                                              create_user: str):
        client_request_api = ClientRequests(api_request_auth_context)
        user_id = create_user
        linked_person_name = "мать драконов"
        short_address = BasicSystemAddress.short_address
        client_request_api.create_linked_person(client_id=user_id, name=linked_person_name)

        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{user_id}/overview")
        self.client_profile_page.locators.RELATED_PERSONS_TAB.click()
        self.client_profile_page.locators.RELATED_PERSON_NAME.to_have_value(text=linked_person_name, timeout=10000)
        self.client_profile_page.locators.ADDRESSES_EDIT_BTN.click()

        self.edit_address_info.ADD_BUTTON.wait_to_be_visible()
        self.edit_address_info.ADD_BUTTON.click()

        self.client_profile_page.add_address_form.TITLE.to_contain_text("Добавление адреса")
        self.client_profile_page.add_address_form.SAVE_BTN.wait_to_be_visible()
        self.client_profile_page.add_address_form.ADDRESS_TYPE_FIELD.click()
        self.client_profile_page.choose_option_with_name("Адрес регистрации")
        self.client_profile_page.add_address_form.ADDRESS_INPUT.fill(short_address)
        self.client_profile_page.add_address_form.ADDRESS_OPTION.to_contain_text(element_index=0,
                                                                                 text=BasicSystemAddress.add_address_name)
        self.client_profile_page.add_address_form.ADDRESS_OPTION.click(element_index=0)
        self.client_profile_page.add_address_form.SAVE_BTN.to_be_enabled()
        self.client_profile_page.add_address_form.MAPS_LINK_INPUT.fill(AddressInfo.map_link)
        self.client_profile_page.add_address_form.CANCEL_BTN.click()

        self.client_profile_page.add_address_form.CANCEL_BTN.not_to_be_visible()
        self.edit_address_info.TABLE_LINE.to_contain_text(element_index=-1, text="Тип")

        self.edit_address_info.CANCEL_BTN.click()
        self.edit_address_info.CANCEL_BTN.not_to_be_visible()
        self.client_profile_page.locators.RELATED_ADDRESS.not_to_be_visible()

    @allure.title("Добавление адреса. Создание нового полного корректного адреса")
    @allure.id(532936)
    def test_add_new_full_address(self, base_url: str, create_user: str):
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{create_user}/overview")
        building_number = generate_random_number(3)
        flat_number = generate_random_number(2)
        new_address = f"Россия, Самарская область обл., г. Самара, ул. Осипенко, д. {building_number}, кв. {flat_number}"
        self.client_profile_page.click_client_tab()
        self.client_profile_page.locators.ADDRESSES_TAB.click()
        delay(1, reason="Без ожидания пустой список адресов")
        self.client_profile_page.locators.ADD_BTN.click()

        self.client_profile_page.add_address_form.TITLE.to_contain_text("Добавление адреса")
        self.client_profile_page.add_address_form.ADDRESS_TYPE_FIELD.select_by_value("Фактический адрес")
        # self.client_profile_page.choose_option_with_name("Фактический адрес")
        self.client_profile_page.add_address_form.ADDRESS_INPUT.fill(new_address)
        self.client_profile_page.add_address_form.ADD_ADDRESS_TO_CATALOG.to_contain_text("Добавить адрес в справочник")
        self.client_profile_page.add_address_form.ADD_ADDRESS_TO_CATALOG.click()

        self.client_profile_page.fill_client_new_address(country="Россия", region="Самарская область", city="Самара",
                                                         street="Осипенко", building_number=building_number,
                                                         flat_number=flat_number)

        self.client_profile_page.create_address_form.ADD_ADDRESS_OBJECT_BTN.not_to_be_visible()
        self.client_profile_page.create_address_form.CREATE_BTN.click()
        self.client_profile_page.create_address_form.TITLE.not_to_be_visible()
        self.client_profile_page.add_address_form.TITLE.wait_to_be_visible()
        self.client_profile_page.add_address_form.ADDRESS_INPUT.to_have_value(new_address)
        self.client_profile_page.add_address_form.SAVE_BTN.click()
        self.client_profile_page.add_address_form.CANCEL_BTN.not_to_be_visible()
        self.client_profile_page.locators.TABLE_LINE.to_contain_text(element_index=2,
                                                                     text=f"Фактический адрес{new_address}")

    @allure.title("Добавление адреса. Создание нового полного корректного адреса")
    @allure.id(533009)
    def test_add_new_full_address_linked_person(self, base_url: str, api_request_auth_context: APIRequestContext,
                                                create_user: str):
        client_request_api = ClientRequests(api_request_auth_context)
        user_id = create_user
        linked_person_name = "мать драконов"
        short_address = BasicSystemAddress.short_address
        client_request_api.create_linked_person(client_id=user_id, name=linked_person_name)
        building_number = generate_random_number(3)
        flat_number = generate_random_number(2)
        new_address = f"Россия, Самарская область обл., г. Самара, ул. Осипенко, д. {building_number}, кв. {flat_number}"

        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{user_id}/overview")
        self.client_profile_page.locators.RELATED_PERSONS_TAB.click()
        self.client_profile_page.locators.RELATED_PERSON_NAME.to_have_value(text=linked_person_name, timeout=10000)
        self.client_profile_page.locators.ADDRESSES_EDIT_BTN.click()

        self.edit_address_info.ADD_BUTTON.wait_to_be_visible()
        self.edit_address_info.ADD_BUTTON.click()

        self.client_profile_page.add_address_form.TITLE.to_contain_text("Добавление адреса")
        self.client_profile_page.add_address_form.SAVE_BTN.wait_to_be_visible()
        self.client_profile_page.add_address_form.ADDRESS_TYPE_FIELD.click()
        self.client_profile_page.choose_option_with_name("Адрес регистрации")
        self.client_profile_page.add_address_form.ADDRESS_INPUT.fill(short_address)
        self.client_profile_page.add_address_form.ADD_ADDRESS_TO_CATALOG.to_contain_text(
            "Добавить адрес в справочник")
        self.client_profile_page.add_address_form.ADD_ADDRESS_TO_CATALOG.click()

        self.client_profile_page.fill_client_new_address(country="Россия", region="Самарская область", city="Самара",
                                                         street="Осипенко", building_number=building_number,
                                                         flat_number=flat_number)

        self.client_profile_page.create_address_form.ADD_ADDRESS_OBJECT_BTN.not_to_be_visible()
        self.client_profile_page.create_address_form.CREATE_BTN.click()
        self.client_profile_page.create_address_form.TITLE.not_to_be_visible()
        self.client_profile_page.add_address_form.TITLE.wait_to_be_visible()
        self.client_profile_page.add_address_form.ADDRESS_INPUT.to_have_value(new_address)
        self.client_profile_page.add_address_form.SAVE_BTN.click()
        self.client_profile_page.add_address_form.CANCEL_BTN.not_to_be_visible()

        self.edit_address_info.TABLE_LINE.to_contain_text(element_index=1, text=f"Адрес регистрации{new_address}")
        self.edit_address_info.CANCEL_BTN.click()

        self.edit_address_info.CANCEL_BTN.not_to_be_visible()
        self.client_profile_page.locators.RELATED_ADDRESS.to_contain_text(new_address)
