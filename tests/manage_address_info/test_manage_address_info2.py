import pytest
import allure
from playwright.sync_api import Page, APIRequestContext

from api.requests.address_requests import AddressRequests
from api.requests.client_requests import ClientRequests
from common.helpers.data_generator import generate_random_number
from common.helpers.time_helpers import delay
from models.address_info import AddressInfo, BasicSystemAddress
from pages.base_page import BasePage
from pages.client_profile_page import ClientProfilePage
from pages.locators.dynamic_form_elements import EditAddressInfo, EditAddress, EditDynamicElements


@allure.epic("Управление адресной информацией")
@allure.suite("Управление адресной информацией")
class TestManageAddressInfo3:
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.base_page = BasePage(page)
        self.client_profile_page = ClientProfilePage(page)
        self.client_edit_address_form = EditAddress(page)
        self.edit_address_info = EditAddressInfo(page)
        self.edit_dynamic_elements = EditDynamicElements(page)

    @allure.title("Настройка колонок. Выбран только 'Адрес'")
    @allure.id(525432)
    @allure.description("Проверка отображения адресов в таблице при выборе колонки 'Адрес'")
    @allure.link(url="jira.nexign.com/browse/TUDS-1144", name="TUDS-1144")
    @allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=585630877",
                 name="ФС Форма Адреса на карточках клиента")
    @allure.tag("can_auth", "success")
    def test_columns_only_address(self, base_url: str, api_request_auth_context: APIRequestContext, create_user: int):
        user_id = create_user
        api_addresses = AddressRequests(api_request_auth_context)
        addresses = api_addresses.get_client_addresses(user_id)
        api_addresses.update_client_address(place_id=addresses.json()['items'][0]['placeId'],
                                            address=BasicSystemAddress.address,
                                            address_url=AddressInfo.map_link,
                                            external_address_id=BasicSystemAddress.external_address_id)
        current_address = addresses.json()['items'][0]['addressString']

        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{user_id}/overview")
        self.client_profile_page.click_client_tab()
        self.client_profile_page.locators.ADDRESSES_TAB.click()
        self.client_profile_page.locators.SETTING_BTN.click()
        self.client_profile_page.locators.SETTING_OPTIONS[0].click()
        self.client_profile_page.locators.SETTING_OPTIONS[2].click()
        self.client_profile_page.locators.SETTING_BTN.click()

        self.client_profile_page.locators.TABLE_LINE[1].not_to_contain_text(text="Адрес регистрации")
        self.client_profile_page.locators.TABLE_LINE[1].to_contain_text(text=current_address)
        self.client_profile_page.locators.TABLE_LINE_MAP_BUTTON.not_to_be_visible()

    @allure.title("Настройка колонок. Выбран только 'Адрес'")
    @allure.id(533015)
    @allure.description("Проверка отображения адресов связанного лица в таблице при выборе колонки 'Адрес'")
    @allure.link(url="jira.nexign.com/browse/TUDS-1144", name="TUDS-1144")
    @allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=585630877",
                 name="ФС Форма Адреса на карточках клиента")
    @allure.tag("can_auth", "success")
    def test_columns_only_address_linked_person(self, base_url: str, api_request_auth_context: APIRequestContext,
                                                create_user: int):
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
        self.client_profile_page.add_address_form.ADDRESS_TYPE_FIELD.select_by_value("Адрес регистрации")
        self.client_profile_page.add_address_form.ADDRESS_INPUT.fill(short_address)
        self.client_profile_page.add_address_form.ADDRESS_OPTION.wait_to_be_visible()
        self.client_profile_page.add_address_form.ADDRESS_OPTION[0]. \
            to_contain_text(text=BasicSystemAddress.add_address_name)
        self.client_profile_page.add_address_form.ADDRESS_OPTION[0].click()
        self.client_profile_page.add_address_form.MAPS_LINK_INPUT.fill(AddressInfo.map_link)
        self.client_profile_page.add_address_form.SAVE_BTN.click()

        self.edit_address_info.SETTING_BTN.click()
        self.edit_address_info.SETTING_OPTIONS[0].click()
        self.edit_address_info.SETTING_OPTIONS[2].click()
        self.edit_address_info.SETTING_BTN.click()

        self.edit_address_info.TABLE_LINE[1].not_to_contain_text(text="Адрес регистрации")
        self.edit_address_info.TABLE_LINE[1].to_contain_text(text=BasicSystemAddress.address)
        self.edit_address_info.TABLE_LINE_MAP_BUTTON.not_to_be_visible()

    @allure.title("Настройка колонок. Выбран только 'Тип'")
    @allure.id(525431)
    @allure.description("Проверка отображения адресов в таблице при выборе колонки 'Тип'")
    @allure.link(url="jira.nexign.com/browse/TUDS-1144", name="TUDS-1144")
    @allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=585630877",
                 name="ФС Форма Адреса на карточках клиента")
    @allure.tag("can_auth", "success")
    def test_columns_only_type(self, base_url: str, api_request_auth_context: APIRequestContext, create_user: int):
        user_id = create_user
        api_addresses = AddressRequests(api_request_auth_context)
        addresses = api_addresses.get_client_addresses(user_id)
        api_addresses.update_client_address(place_id=addresses.json()['items'][0]['placeId'],
                                            address=BasicSystemAddress.address,
                                            address_url=AddressInfo.map_link,
                                            external_address_id=BasicSystemAddress.external_address_id)
        current_address = addresses.json()['items'][0]['addressString']

        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{user_id}/overview")
        self.client_profile_page.click_client_tab()
        self.client_profile_page.locators.ADDRESSES_TAB.click()
        self.client_profile_page.locators.SETTING_BTN.click()
        self.client_profile_page.locators.SETTING_OPTIONS[1].click()
        self.client_profile_page.locators.SETTING_OPTIONS[2].click()
        self.client_profile_page.locators.SETTING_BTN.click()

        self.client_profile_page.locators.TABLE_LINE[1].to_contain_text(text="Адрес регистрации")
        self.client_profile_page.locators.TABLE_LINE[1].not_to_contain_text(text=current_address)
        self.client_profile_page.locators.TABLE_LINE_MAP_BUTTON.not_to_be_visible()

    @allure.title("Настройка колонок. Выбран только 'Тип'")
    @allure.id(533018)
    @allure.description("Проверка отображения адресов связанного лица в таблице при выборе колонки 'Тип'")
    @allure.link(url="jira.nexign.com/browse/TUDS-1144", name="TUDS-1144")
    @allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=585630877",
                 name="ФС Форма Адреса на карточках клиента")
    @allure.tag("can_auth", "success")
    def test_columns_only_type_linked_person(self, base_url: str, api_request_auth_context: APIRequestContext,
                                             create_user: int):
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
        self.client_profile_page.add_address_form.ADDRESS_TYPE_FIELD.select_by_value("Адрес регистрации")
        self.client_profile_page.add_address_form.ADDRESS_INPUT.fill(short_address)
        self.client_profile_page.add_address_form.ADDRESS_OPTION.wait_to_be_visible()
        self.client_profile_page.add_address_form.ADDRESS_OPTION[0]. \
            to_contain_text(text=BasicSystemAddress.add_address_name)
        self.client_profile_page.add_address_form.ADDRESS_OPTION[0].click()
        self.client_profile_page.add_address_form.MAPS_LINK_INPUT.fill(AddressInfo.map_link)
        self.client_profile_page.add_address_form.SAVE_BTN.click()

        self.edit_address_info.SETTING_BTN.click()
        self.edit_address_info.SETTING_OPTIONS[1].click()
        self.edit_address_info.SETTING_OPTIONS[2].click()
        self.edit_address_info.SETTING_BTN.click()

        self.edit_address_info.TABLE_LINE[1].to_contain_text(text="Адрес регистрации")
        self.edit_address_info.TABLE_LINE[1].not_to_contain_text(text="ул")
        self.edit_address_info.TABLE_LINE_MAP_BUTTON.not_to_be_visible()

    @allure.title("Настройка колонок. Выбраны все столбцы")
    @allure.id(525434)
    @allure.description("Проверка отображения адресов в таблице при выборе всех колонок")
    @allure.link(url="jira.nexign.com/browse/TUDS-1144", name="TUDS-1144")
    @allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=585630877",
                 name="ФС Форма Адреса на карточках клиента")
    @allure.tag("can_auth", "success")
    def test_columns_setting_all_in(self, base_url: str, api_request_auth_context: APIRequestContext, create_user: int):
        user_id = create_user
        api_addresses = AddressRequests(api_request_auth_context)
        addresses = api_addresses.get_client_addresses(user_id)
        api_addresses.update_client_address(place_id=addresses.json()['items'][0]['placeId'],
                                            address=BasicSystemAddress.address,
                                            address_url=AddressInfo.map_link,
                                            external_address_id=BasicSystemAddress.external_address_id)
        current_address = addresses.json()['items'][0]['addressString']

        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{user_id}/overview")
        self.client_profile_page.click_client_tab()
        self.client_profile_page.locators.ADDRESSES_TAB.click()
        self.client_profile_page.locators.SETTING_BTN.click()
        self.client_profile_page.locators.SETTING_OPTIONS[0].click()
        self.client_profile_page.locators.SETTING_OPTIONS[1].click()
        self.client_profile_page.locators.SETTING_BTN.click()

        self.client_profile_page.locators.TABLE_LINE[1].not_to_contain_text(text=f"Адрес регистрации{current_address}")
        self.client_profile_page.locators.ADDRESSES_TAB.click()
        self.client_profile_page.locators.SETTING_BTN.click()
        self.client_profile_page.locators.SETTING_OPTIONS[0].click()
        self.client_profile_page.locators.SETTING_OPTIONS[1].click()
        self.client_profile_page.locators.SETTING_BTN.click()
        self.client_profile_page.locators.TABLE_ADDRESS_TYPES[0].wait_to_be_visible()
        self.client_profile_page.locators.TABLE_ADDRESS_TYPES[0].to_contain_text(text="Адрес регистрации")
        self.client_profile_page.locators.TABLE_ADDRESSES[0].to_contain_text(text=current_address)
        assert "button" in self.client_profile_page.locators.TABLE_MAP_CELLS[0].inner_html(), \
            "Отсутствует ссылка на карту для адреса"

    @allure.title("Настройка колонок. Выбраны все столбцы")
    @allure.id(533019)
    @allure.description("Проверка отображения адресов связанного лица в таблице при выборе всех колонок")
    @allure.link(url="jira.nexign.com/browse/TUDS-1144", name="TUDS-1144")
    @allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=585630877",
                 name="ФС Форма Адреса на карточках клиента")
    @allure.tag("can_auth", "success")
    def test_columns_setting_all_in_linked_person(self, base_url: str, api_request_auth_context: APIRequestContext,
                                                  create_user: int):
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
        self.client_profile_page.add_address_form.ADDRESS_TYPE_FIELD.select_by_value("Адрес регистрации")
        self.client_profile_page.add_address_form.ADDRESS_INPUT.fill(short_address)
        self.client_profile_page.add_address_form.ADDRESS_OPTION[0]. \
            to_contain_text(text=BasicSystemAddress.add_address_name)
        self.client_profile_page.add_address_form.ADDRESS_OPTION[0].click()
        self.client_profile_page.add_address_form.MAPS_LINK_INPUT.fill(AddressInfo.map_link)
        self.client_profile_page.add_address_form.SAVE_BTN.click()

        self.edit_address_info.SETTING_BTN.click()
        self.edit_address_info.SETTING_OPTIONS[0].click()
        self.edit_address_info.SETTING_OPTIONS[1].click()
        self.edit_address_info.SETTING_BTN.click()
        self.edit_address_info.TABLE_LINE[1].not_to_contain_text(text="Адрес регистрации")

        self.edit_address_info.SETTING_BTN.click()
        self.edit_address_info.SETTING_OPTIONS[0].click()
        self.edit_address_info.SETTING_OPTIONS[1].click()
        self.edit_address_info.SETTING_BTN.click()

        self.edit_address_info.TABLE_ADDRESS_TYPES[0].to_contain_text(text="Адрес регистрации")
        self.edit_address_info.TABLE_ADDRESSES[0].to_contain_text(text="ул")
        assert "button" in self.edit_address_info.TABLE_MAP_CELLS[0].inner_html(), \
            "Отсутствует ссылка на карту для адреса"

    @allure.title("Отображение адреса. Сортировка по столбцу 'Тип'")
    @allure.id(525429)
    @allure.description("Проверка сортировки адресов в таблице по столбцу 'Тип'")
    @allure.link(url="jira.nexign.com/browse/TUDS-1144", name="TUDS-1144")
    @allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=585630877",
                 name="ФС Форма Адреса на карточках клиента")
    @allure.tag("can_auth", "success")
    def test_sorting_by_type(self, base_url: str, create_user: int):
        user_id = create_user
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{user_id}/overview")
        self.client_profile_page.click_client_tab()
        self.client_profile_page.locators.ADDRESSES_TAB.click()
        delay(1, reason="Без ожидания пустой список адресов")
        self.client_profile_page.locators.ADD_BTN.click()
        self.client_profile_page.add_address_form.TITLE.to_contain_text("Добавление адреса")
        self.client_profile_page.add_address_form.ADDRESS_TYPE_FIELD.select_by_value("Фактический адрес")
        self.client_profile_page.add_address_form.ADDRESS_INPUT.fill(BasicSystemAddress.add_address_name)
        self.client_profile_page.add_address_form.ADDRESS_OPTION.wait_to_be_visible()
        self.client_profile_page.add_address_form.ADDRESS_OPTION[0]. \
            to_contain_text(text=BasicSystemAddress.add_address_name)
        self.client_profile_page.add_address_form.ADDRESS_OPTION[0].click()
        self.client_profile_page.add_address_form.SAVE_BTN.to_be_enabled()
        self.client_profile_page.add_address_form.MAPS_LINK_INPUT.fill(AddressInfo.map_link)
        self.client_profile_page.add_address_form.SAVE_BTN.click()
        self.client_profile_page.add_address_form.CANCEL_BTN.not_to_be_visible()
        self.client_profile_page.locators.TABLE_LINE.wait_to_have_count(3)
        self.client_profile_page.locators.TYPE_SORT_BTN.click()
        self.client_profile_page.locators.TABLE_ADDRESS_TYPES[0].wait_to_have_text("Фактический адрес", timeout=10000)
        assert [self.client_profile_page.locators.TABLE_ADDRESS_TYPES[0].text,
                self.client_profile_page.locators.TABLE_ADDRESS_TYPES[1].text] == ["Фактический адрес",
                                                                                   "Адрес регистрации"], \
            "Некорректная сортировка по 'Тип'"
        self.client_profile_page.locators.TYPE_SORT_BTN.click()
        self.client_profile_page.locators.TABLE_ADDRESS_TYPES[0].wait_to_have_text("Адрес регистрации", timeout=10000)
        assert [self.client_profile_page.locators.TABLE_ADDRESS_TYPES[0].text,
                self.client_profile_page.locators.TABLE_ADDRESS_TYPES[1].text] == ["Адрес регистрации",
                                                                                   "Фактический адрес"], \
            "Некорректная сортировка по 'Тип'"

    @allure.title("Отображение адреса. Фильтрация по столбцу 'Адрес'")
    @allure.id(525430)
    @allure.description("Проверка фильтрации в таблице с адресами по столбцу 'Адрес'")
    @allure.link(url="jira.nexign.com/browse/TUDS-1144", name="TUDS-1144")
    @allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=585630877",
                 name="ФС Форма Адреса на карточках клиента")
    @allure.tag("can_auth", "success")
    def test_filter_address_fields(self, base_url: str, add_new_address_to_lam: dict, create_user: int):
        user_id = create_user
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{user_id}/overview")
        new_address = add_new_address_to_lam["addressString"]
        short_address = new_address.split("ул. ")[1]

        self.client_profile_page.click_client_tab()
        self.client_profile_page.locators.ADDRESSES_TAB.click()
        delay(1, reason="Без ожидания пустой список адресов")
        self.client_profile_page.locators.ADD_BTN.click()
        self.client_profile_page.add_address_form.TITLE.to_contain_text("Добавление адреса")
        self.client_profile_page.add_address_form.ADDRESS_TYPE_FIELD.select_by_value("Фактический адрес")
        self.client_profile_page.add_address_form.ADDRESS_INPUT.fill("Россия, " + short_address)
        self.client_profile_page.add_address_form.ADDRESS_OPTION.wait_to_be_visible()
        self.client_profile_page.add_address_form.ADDRESS_OPTION[0].to_contain_text(text=short_address)
        self.client_profile_page.add_address_form.ADDRESS_OPTION[0].click()
        self.client_profile_page.add_address_form.SAVE_BTN.to_be_enabled()
        self.client_profile_page.add_address_form.MAPS_LINK_INPUT.fill(AddressInfo.map_link)
        self.client_profile_page.add_address_form.SAVE_BTN.click()
        self.client_profile_page.add_address_form.CANCEL_BTN.not_to_be_visible()

        self.client_profile_page.locators.TABLE_ADDRESSES.wait_to_have_count(2)
        self.client_profile_page.locators.TABLE_ADDRESSES[1].to_contain_text(text=new_address)
        self.client_profile_page.locators.SEARCH_ADDRESS_INPUT.fill("Полевая")
        self.client_profile_page.locators.TABLE_ADDRESSES.wait_to_have_count(1)
        self.client_profile_page.locators.TABLE_ADDRESSES[0].to_contain_text(text=new_address)

    @allure.title("Отображение адреса. Фильтрация по столбцу 'Тип'")
    @allure.id(525409)
    @allure.description("Проверка множественной фильтрации в таблице с адресами по столбцу 'Тип'")
    @allure.link(url="jira.nexign.com/browse/TUDS-1144", name="TUDS-1144")
    @allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=585630877",
                 name="ФС Форма Адреса на карточках клиента")
    @allure.tag("can_auth", "success")
    def test_filter_by_type(self, base_url: str, create_user: int):
        user_id = create_user
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{user_id}/overview")
        self.client_profile_page.click_client_tab()
        self.client_profile_page.locators.ADDRESSES_TAB.click()
        delay(1, reason="Без ожидания пустой список адресов")
        self.client_profile_page.locators.ADD_BTN.click()
        self.client_profile_page.add_address_form.TITLE.to_contain_text("Добавление адреса")
        self.client_profile_page.add_address_form.ADDRESS_TYPE_FIELD.select_by_value("Фактический адрес")
        self.client_profile_page.add_address_form.ADDRESS_INPUT.fill(BasicSystemAddress.add_address_name)
        self.client_profile_page.add_address_form.ADDRESS_OPTION.wait_to_be_visible()
        self.client_profile_page.add_address_form.ADDRESS_OPTION[0]. \
            to_contain_text(text=BasicSystemAddress.add_address_name)
        self.client_profile_page.add_address_form.ADDRESS_OPTION[0].click()
        self.client_profile_page.add_address_form.SAVE_BTN.to_be_enabled()
        self.client_profile_page.add_address_form.MAPS_LINK_INPUT.fill(AddressInfo.map_link)
        self.client_profile_page.add_address_form.SAVE_BTN.click()

        self.client_profile_page.locators.TABLE_ADDRESSES.wait_to_have_count(2)
        self.client_profile_page.locators.TYPE_FILTER_DROPDOWN_BTN.click()
        self.client_profile_page.choose_address_type_with_name("Фактический адрес")
        self.client_profile_page.locators.TABLE_ADDRESSES.wait_to_have_count(1)
        self.client_profile_page.locators.TABLE_ADDRESS_TYPES[0].to_contain_text(text="Фактический адрес")

        self.client_profile_page.locators.TYPE_FILTER_CHOOSE_ALL_BTN.click()
        self.client_profile_page.locators.TABLE_ADDRESSES.wait_to_have_count(2)

    @allure.title("Просмотр адреса по ссылке на карту")
    @allure.id(532939)
    @allure.description("Просмотр адреса при переходе по ссылке на карту")
    @allure.link(url="jira.nexign.com/browse/TUDS-1144", name="TUDS-1144")
    @allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=585630877",
                 name="ФС Форма Адреса на карточках клиента")
    @allure.tag("can_auth", "success")
    def test_check_map_link(self, base_url: str, api_request_auth_context: APIRequestContext, create_user: int):
        user_id = create_user
        api_addresses = AddressRequests(api_request_auth_context)
        addresses = api_addresses.get_client_addresses(user_id)
        api_addresses.update_client_address(place_id=addresses.json()['items'][0]['placeId'],
                                            address=BasicSystemAddress.address,
                                            address_url=AddressInfo.map_link,
                                            external_address_id=BasicSystemAddress.external_address_id)

        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{user_id}/overview")
        self.client_profile_page.click_client_tab()
        self.client_profile_page.locators.ADDRESSES_TAB.click()
        self.client_profile_page.locators.TABLE_LINE_MAP_BUTTON.wait_to_have_count(1)
        self.client_profile_page.locators.TABLE_LINE_MAP_BUTTON[0].click()

        context = self.client_profile_page.page.context
        with context.expect_page() as new_page_info:
            new_page = new_page_info.value
        assert AddressInfo.map_link in new_page.url, "Некорректный адрес открывшейся карты "

    @allure.title("Редактирование адреса. Ввод всех полей")
    @allure.id(525417)
    @allure.description("Выполняется проверка редактирования данных адреса с изменением всех полей")
    @allure.link(url="jira.nexign.com/browse/TUDS-1144", name="TUDS-1144")
    @allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=585630877",
                 name="ФС Форма Адреса на карточках клиента")
    @allure.tag("can_auth", "success")
    def test_address_edit(self, base_url: str, add_new_address_to_lam: dict, create_user: int):
        user_id = create_user
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{user_id}/overview")
        new_address = add_new_address_to_lam["addressString"]
        short_address = new_address.split("ул. ")[1]
        self.client_profile_page.click_client_tab()
        self.client_profile_page.locators.ADDRESSES_TAB.click()
        self.client_profile_page.locators.TABLE_ADDRESS_TYPES.wait_to_have_count(1)
        self.client_profile_page.locators.TABLE_ADDRESS_TYPES[0].click()
        self.client_profile_page.locators.EDIT_ADDRESS.click()

        self.client_edit_address_form.TITLE.to_contain_text("Редактирование адреса")
        self.client_edit_address_form.ADDRESS_INPUT.fill("Россия, " + short_address)
        self.client_edit_address_form.ADDRESS_OPTION.wait_to_be_visible()
        self.client_edit_address_form.ADDRESS_OPTION[0].to_contain_text(text=short_address)
        self.client_edit_address_form.ADDRESS_OPTION[0].click()
        self.client_edit_address_form.CANCEL_BTN.to_be_enabled()
        self.client_edit_address_form.SAVE_BTN.to_be_enabled()
        self.client_edit_address_form.MAPS_LINK_INPUT.fill(AddressInfo.map_link)
        self.client_edit_address_form.SAVE_BTN.click()
        self.client_edit_address_form.CANCEL_BTN.not_to_be_visible()

        self.client_profile_page.locators.TABLE_ADDRESSES[0].wait_to_have_text(new_address)
        self.client_profile_page.locators.TABLE_LINE_MAP_BUTTON[0].wait_to_be_visible()

    @allure.title("Редактирование адреса. Ввод только обязательных полей")
    @allure.id(525416)
    @allure.description("Выполняется проверка редактирования данных адреса с изменением только обязательных полей")
    @allure.link(url="jira.nexign.com/browse/TUDS-1144", name="TUDS-1144")
    @allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=585630877",
                 name="ФС Форма Адреса на карточках клиента")
    @allure.tag("can_auth", "success")
    def test_address_edit_only_required_fields(self, base_url: str, add_new_address_to_lam: dict, create_user: int):
        user_id = create_user
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{user_id}/overview")
        new_address = add_new_address_to_lam["addressString"]
        short_address = new_address.split("ул. ")[1]
        self.client_profile_page.click_client_tab()
        self.client_profile_page.locators.ADDRESSES_TAB.click()
        self.client_profile_page.locators.TABLE_ADDRESS_TYPES.wait_to_have_count(1)
        self.client_profile_page.locators.TABLE_ADDRESS_TYPES[0].click()
        self.client_profile_page.locators.EDIT_ADDRESS.click()

        self.client_edit_address_form.TITLE.to_contain_text("Редактирование адреса")
        self.client_edit_address_form.ADDRESS_INPUT.fill("Россия, " + short_address)
        self.client_edit_address_form.ADDRESS_OPTION.wait_to_be_visible()
        self.client_edit_address_form.ADDRESS_OPTION[0].to_contain_text(text=short_address)
        self.client_edit_address_form.ADDRESS_OPTION[0].click()
        self.client_edit_address_form.MAPS_LINK_INPUT.to_be_enabled()
        self.client_edit_address_form.CANCEL_BTN.to_be_enabled()
        self.client_edit_address_form.SAVE_BTN.to_be_enabled()
        self.client_edit_address_form.SAVE_BTN.click()
        self.client_edit_address_form.CANCEL_BTN.not_to_be_visible()

        self.client_profile_page.locators.TABLE_ADDRESSES[0].wait_to_have_text(new_address)
        self.client_profile_page.locators.TABLE_LINE_MAP_BUTTON.not_to_be_visible()

    @allure.title("Редактирование адреса. Отмена редактирования адреса")
    @allure.id(532274)
    @allure.description("Проверка закрытия формы редактирования адреса без сохранения при отмене")
    @allure.link(url="jira.nexign.com/browse/TUDS-1144", name="TUDS-1144")
    @allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=585630877",
                 name="ФС Форма Адреса на карточках клиента")
    @allure.tag("can_auth", "success")
    def test_address_edit_reject_button(self, base_url: str, add_new_address_to_lam: dict, create_user: int):
        user_id = create_user
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{user_id}/overview")
        new_address = add_new_address_to_lam["addressString"]
        short_address = new_address.split("ул. ")[1]
        self.client_profile_page.click_client_tab()
        self.client_profile_page.locators.ADDRESSES_TAB.click()
        self.client_profile_page.locators.TABLE_ADDRESS_TYPES.wait_to_have_count(1)
        self.client_profile_page.locators.TABLE_ADDRESS_TYPES[0].click()
        self.client_profile_page.locators.EDIT_ADDRESS.click()

        self.client_edit_address_form.TITLE.to_contain_text("Редактирование адреса")
        self.client_edit_address_form.ADDRESS_INPUT.fill("Россия, " + short_address)
        self.client_edit_address_form.ADDRESS_OPTION.wait_to_be_visible()
        self.client_edit_address_form.ADDRESS_OPTION[0].to_contain_text(text=short_address)
        self.client_edit_address_form.ADDRESS_OPTION[0].click()
        self.client_edit_address_form.MAPS_LINK_INPUT.to_be_enabled()
        self.client_edit_address_form.CANCEL_BTN.to_be_enabled()
        self.client_edit_address_form.SAVE_BTN.to_be_enabled()
        self.client_edit_address_form.CANCEL_BTN.click()
        self.client_edit_address_form.CANCEL_BTN.not_to_be_visible()

        self.client_profile_page.locators.TABLE_ADDRESSES[0].wait_to_have_text(BasicSystemAddress.address)
        self.client_profile_page.locators.TABLE_LINE_MAP_BUTTON.not_to_be_visible()

    @allure.title("Редактирование адреса. Создание нового полного корректного адреса")
    @allure.id(532942)
    @allure.description("Выполняется проверка редактирования адреса с созданием нового полного корректного адреса"
                        " в справочнике адресов")
    @allure.link(url="jira.nexign.com/browse/TUDS-1144", name="TUDS-1144")
    @allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=585630877",
                 name="ФС Форма Адреса на карточках клиента")
    @allure.tag("can_auth", "success")
    def test_address_edit_create_new_addresses(self, base_url: str, create_user: int):
        user_id = create_user
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{user_id}/overview")
        building_number = generate_random_number(3)
        flat_number = generate_random_number(2)
        new_address = (f"Россия, Самарская обл., г. Самара, ул. Осипенко, д. {building_number},"
                       f" кв. {flat_number}")
        self.client_profile_page.click_client_tab()
        self.client_profile_page.locators.ADDRESSES_TAB.click()
        self.client_profile_page.locators.TABLE_ADDRESS_TYPES.wait_to_have_count(1)
        self.client_profile_page.locators.TABLE_ADDRESS_TYPES[0].click()
        self.client_profile_page.locators.EDIT_ADDRESS.click()

        self.client_edit_address_form.TITLE.to_contain_text("Редактирование адреса")
        self.client_edit_address_form.MAPS_LINK_INPUT.to_be_enabled()
        self.client_edit_address_form.CANCEL_BTN.to_be_enabled()
        self.client_edit_address_form.SAVE_BTN.to_be_enabled()

        delay(1, reason="Если раньше ввести строку, зависает UI")
        self.client_edit_address_form.ADDRESS_INPUT.fill(new_address)
        self.client_edit_address_form.ADD_ADDRESS_TO_CATALOG.to_contain_text("Добавить адрес в справочник")
        self.client_profile_page.add_address_form.ADD_ADDRESS_TO_CATALOG.click()

        self.client_profile_page.fill_client_new_address(country="Россия", region="Самарская", city="Самара",
                                                         street="Осипенко", building_number=building_number,
                                                         flat_number=flat_number)

        self.client_profile_page.create_address_form.ADD_ADDRESS_OBJECT_BTN.not_to_be_visible()
        self.edit_dynamic_elements.CREATE_BTN.click()
        self.client_profile_page.create_address_form.TITLE.not_to_be_visible()
        self.client_edit_address_form.TITLE.wait_to_be_visible()
        self.client_edit_address_form.ADDRESS_INPUT.to_have_value(new_address)

        self.client_edit_address_form.SAVE_BTN.click()
        self.client_edit_address_form.CANCEL_BTN.not_to_be_visible()

        self.client_profile_page.locators.TABLE_ADDRESSES[0].wait_to_have_text(new_address)
        self.client_profile_page.locators.TABLE_LINE_MAP_BUTTON.not_to_be_visible()
