import pytest
import allure
from playwright.sync_api import Page
from common.helpers.data_generator import generate_random_number
from common.helpers.time_helpers import delay
from pages.base_page import BasePage
from pages.client_profile_page import ClientProfilePage
from pages.locators.dynamic_form_elements import EditAddressInfo, EditAddress, AddressCreate


@allure.epic("Управление адресной информацией")
@allure.suite("Управление адресной информацией")
class TestManageAddressInfo3:
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.base_page = BasePage(page)
        self.client_profile_page = ClientProfilePage(page)
        self.client_edit_address_form = EditAddress(page)
        self.edit_address_info = EditAddressInfo(page)
        self.create_address_form = AddressCreate(page)

    @allure.title("Создание нового адреса. Введен уже созданный адресный объект")
    @allure.id(532929)
    @allure.description("Выполняется проверка игнорирования создания адресного объекта при вводе уже существующего")
    @allure.link(url="jira.nexign.com/browse/TUDS-1144", name="TUDS-1144")
    @allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=585630877",
                 name="ФС Форма Адреса на карточках клиента")
    @allure.tag("can_auth", "success")
    def test_create_new_available_address(self, base_url: str, create_user: int):
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{create_user}/overview")
        building_number = generate_random_number(3)
        flat_number = generate_random_number(2)
        new_address = (f"Россия, Самарская обл., г. Самара, ул. Осипенко, д. {building_number},"
                       f" кв. {flat_number}")
        self.client_profile_page.click_client_tab()
        self.client_profile_page.locators.ADDRESSES_TAB.click()
        delay(1, reason="Без ожидания пустой список адресов")
        self.client_profile_page.locators.ADD_BTN.click()

        self.client_profile_page.add_address_form.TITLE.to_contain_text("Добавление адреса")
        self.client_profile_page.add_address_form.ADDRESS_TYPE_FIELD.select_by_value("Фактический адрес")
        self.client_profile_page.add_address_form.ADDRESS_INPUT.fill(new_address)
        self.client_profile_page.add_address_form.ADD_ADDRESS_TO_CATALOG.to_contain_text("Добавить адрес в справочник")
        self.client_profile_page.add_address_form.ADD_ADDRESS_TO_CATALOG.click()

        self.client_profile_page.create_address_form.TITLE.to_contain_text("Создание нового адреса")
        self.create_address_form.OBJECT_TYPE.select_by_value("Страна")
        self.create_address_form.OBJECT_NAME_AUTOCOMPLETE.fill("Россия")
        self.create_address_form.ADD_ADDRESS_OBJECT_BTN.not_to_be_enabled()
        self.create_address_form.APPLY_BTN.click()

        self.create_address_form.ADDED_CARD[0].wait_to_be_visible()
        self.create_address_form.ATTRIBUTE_HEADER[0].to_contain_text(text="Атрибуты")
        self.create_address_form.ADDED_CARD_EDIT_BTN[0].wait_to_be_visible()
        self.create_address_form.ADDED_CARD_DELETE_BTN[0].wait_to_be_visible()

        self.client_profile_page.create_address_form.CREATE_BTN.click()
        self.client_profile_page.create_address_form.TITLE.not_to_be_visible()
        self.client_profile_page.add_address_form.TITLE.wait_to_be_visible()
        self.client_profile_page.add_address_form.ADDRESS_INPUT.to_have_value("Россия")
