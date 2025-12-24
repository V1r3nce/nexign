import allure
import pytest

from api.nbss.address_requests import AddressRequests
from api.nbss.client_requests.client_requests import ClientRequests
from common.helpers.checker import assert_that
from common.helpers.data_generator import generate_random_number
from common.helpers.time_helpers import delay
from models.address_info import AddressInfo, BasicSystemAddress
from models.client import OrganizationClient
from models.context import test_context
from pages.base_page import BasePage
from pages.locators.nbss.dynamic_form_elements import EditAddressInfo
from pages.nbss.client.client_profile_page import ClientProfilePage


@allure.epic("E2E_22 Управление адресной информацией")
@allure.suite("E2E_22 Управление адресной информацией")
@allure.link(url="jira.nexign.com/browse/TUDS-1144", name="TUDS-1144")
@allure.link(
    url="confluence.nexign.com/pages/viewpage.action?pageId=585630877", name="ФС Форма Адреса на карточках клиента"
)
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestManageAddressInfo1:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login, add_new_address_to_lam: dict, create_organization: OrganizationClient) -> None:
        self.base_page = BasePage()
        self.client_profile_page = ClientProfilePage()
        self.edit_address_info = EditAddressInfo()
        self.client_request_api = ClientRequests()
        self.new_address = add_new_address_to_lam["addressString"]

    @allure.title("Добавление адреса. Ввод всех полей")
    @allure.id(525413)
    @allure.description("Добавление адреса. Ввод всех полей для Клиента")
    def test_add_address_input_all_fields(self, base_url: str) -> None:
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")
        self.client_profile_page.locators.OVERVIEW_TAB.wait_to_be_visible(timeout=15000)
        short_address = self.new_address.split("ул. ")[1]

        self.client_profile_page.locators.CLIENT_TAB.click()
        self.client_profile_page.locators.ADDRESSES_TAB.click()
        delay(1, reason="Без ожидания пустой список адресов")
        self.client_profile_page.locators.ADD_BTN.click()
        self.client_profile_page.add_address_form.TITLE.to_contain_text("Добавление адреса")
        self.client_profile_page.add_address_form.ADDRESS_TYPE_FIELD.select_by_value("Фактический адрес")
        self.client_profile_page.add_address_form.ADDRESS_INPUT.fill("Россия, " + short_address)
        self.client_profile_page.add_address_form.ADDRESS_OPTION.wait_elements_visible(0)
        self.client_profile_page.add_address_form.ADDRESS_OPTION[0].to_contain_text(text=short_address)
        self.client_profile_page.add_address_form.ADDRESS_OPTION[0].click()
        self.client_profile_page.add_address_form.SAVE_BTN.to_be_enabled()
        self.client_profile_page.add_address_form.MAPS_LINK_INPUT.fill(AddressInfo.map_link)
        self.client_profile_page.add_address_form.SAVE_BTN.click()
        self.client_profile_page.add_address_form.CANCEL_BTN.not_to_be_visible()

        self.client_profile_page.locators.TABLE_LINE.wait_to_have_count(2)
        self.client_profile_page.locators.TABLE_LINE[1].to_contain_text(text=f"Фактический адрес{self.new_address}")
        self.edit_address_info.TABLE_LINE_MAP_BUTTON[0].wait_to_be_visible()

    @allure.title("Добавление адреса. Ввод всех полей")
    @allure.id(533011)
    @allure.description("Добавление адреса. Ввод всех полей для связанного лица")
    def test_add_address_linked_person(self, base_url: str) -> None:
        linked_person_name = "мать драконов"
        short_address = self.new_address.split("ул. ")[1]
        self.client_request_api.create_linked_person(client_id=test_context.client.user_id, name=linked_person_name)

        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")
        self.client_profile_page.locators.RELATED_PERSONS_TAB.click()
        self.client_profile_page.locators.RELATED_PERSON_NAME.wait_to_have_text(linked_person_name)
        self.client_profile_page.locators.ADDRESSES_EDIT_BTN.click()

        self.edit_address_info.ADD_BUTTON.wait_to_be_visible()
        self.edit_address_info.ADD_BUTTON.click()

        self.client_profile_page.add_address_form.TITLE.to_contain_text("Добавление адреса")
        self.client_profile_page.add_address_form.SAVE_BTN.wait_to_be_visible()
        self.client_profile_page.add_address_form.ADDRESS_TYPE_FIELD.select_by_value("Адрес регистрации")
        self.client_profile_page.add_address_form.ADDRESS_INPUT.fill("Россия, " + short_address)
        self.client_profile_page.add_address_form.ADDRESS_OPTION.wait_elements_visible(0)
        self.client_profile_page.add_address_form.ADDRESS_OPTION[0].to_contain_text(text=short_address)
        self.client_profile_page.add_address_form.ADDRESS_OPTION[0].click()
        self.client_profile_page.add_address_form.SAVE_BTN.to_be_enabled()
        self.client_profile_page.add_address_form.MAPS_LINK_INPUT.fill(AddressInfo.map_link)
        self.client_profile_page.add_address_form.SAVE_BTN.click()

        self.edit_address_info.TABLE_ADDRESS_TYPES.wait_to_have_count(1)
        self.edit_address_info.TABLE_ADDRESS_TYPES[0].wait_to_have_text("Адрес регистрации")
        self.edit_address_info.TABLE_ADDRESSES[0].wait_to_have_text(self.new_address)
        self.edit_address_info.TABLE_LINE_MAP_BUTTON[0].wait_to_be_visible()
        self.edit_address_info.CANCEL_BTN.click()

        self.edit_address_info.CANCEL_BTN.not_to_be_visible()
        self.client_profile_page.locators.EXPAND_RELATED_ADDRESS_BTN.click()
        self.client_profile_page.locators.RELATED_ADDRESS.to_contain_text(self.new_address)

    @allure.title("Добавление адреса. Ввод только обязательных полей")
    @allure.id(525412)
    @allure.description("Добавление адреса. Ввод только обязательных полей для Клиента")
    def test_add_address_input_required_fields(self, base_url: str) -> None:
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")
        short_address = self.new_address.split("ул. ")[1]

        self.client_profile_page.locators.CLIENT_TAB.click()
        self.client_profile_page.locators.ADDRESSES_TAB.click()
        delay(1, reason="Без ожидания пустой список адресов")
        self.client_profile_page.locators.ADD_BTN.click()
        self.client_profile_page.add_address_form.TITLE.to_contain_text("Добавление адреса")
        self.client_profile_page.add_address_form.ADDRESS_TYPE_FIELD.select_by_value("Фактический адрес")
        self.client_profile_page.add_address_form.ADDRESS_INPUT.fill("Россия, " + short_address)
        self.client_profile_page.add_address_form.ADDRESS_OPTION.wait_elements_visible(0)
        self.client_profile_page.add_address_form.ADDRESS_OPTION[0].to_contain_text(text=short_address)
        self.client_profile_page.add_address_form.ADDRESS_OPTION[0].click()
        self.client_profile_page.add_address_form.SAVE_BTN.to_be_enabled()
        self.client_profile_page.add_address_form.SAVE_BTN.click()

        self.client_profile_page.add_address_form.CANCEL_BTN.not_to_be_visible()
        self.client_profile_page.locators.TABLE_LINE.wait_to_have_count(2)
        self.client_profile_page.locators.TABLE_LINE[1].to_contain_text(text=f"Фактический адрес{self.new_address}")

    @allure.title("Добавление адреса. Ввод только обязательных полей")
    @allure.id(533012)
    @allure.description("Добавление адреса. Ввод только обязательных полей для связанного Клиента")
    def test_add_address_linked_person_required_fields(self, base_url: str) -> None:
        linked_person_name = "мать драконов"
        short_address = self.new_address.split("ул. ")[1]
        self.client_request_api.create_linked_person(client_id=test_context.client.user_id, name=linked_person_name)

        self.base_page.open(
            f"{base_url}customer-hierarchy-management/customers/{test_context.client.user_id}/overview",
            wait="domcontentloaded",
        )
        self.client_profile_page.locators.CUSTOMER_NAME.wait_to_be_visible(timeout=10000)
        self.client_profile_page.locators.RELATED_PERSONS_TAB.click()
        self.client_profile_page.locators.RELATED_PERSON_NAME.wait_to_have_text(linked_person_name)
        self.client_profile_page.locators.ADDRESSES_EDIT_BTN.click()

        self.edit_address_info.ADD_BUTTON.wait_to_be_visible()
        self.edit_address_info.ADD_BUTTON.click()

        self.client_profile_page.add_address_form.TITLE.to_contain_text("Добавление адреса")
        self.client_profile_page.add_address_form.SAVE_BTN.wait_to_be_visible()
        self.client_profile_page.add_address_form.ADDRESS_TYPE_FIELD.select_by_value("Адрес регистрации")
        self.client_profile_page.add_address_form.ADDRESS_INPUT.fill("Россия, " + short_address)
        # self.client_profile_page.add_address_form.ADDRESS_OPTION.wait_elements_visible(0)
        self.client_profile_page.add_address_form.ADDRESS_OPTION[0].to_contain_text(text=short_address)
        self.client_profile_page.add_address_form.ADDRESS_OPTION[0].click()
        self.client_profile_page.add_address_form.SAVE_BTN.to_be_enabled()
        self.client_profile_page.add_address_form.SAVE_BTN.click()

        self.edit_address_info.TABLE_LINE.wait_to_have_count(1)
        self.edit_address_info.TABLE_LINE[0].wait_to_have_text(f"Адрес регистрации{self.new_address}")
        self.edit_address_info.CANCEL_BTN.click()

        self.edit_address_info.CANCEL_BTN.not_to_be_visible()
        self.client_profile_page.locators.EXPAND_RELATED_ADDRESS_BTN.click()
        self.client_profile_page.locators.RELATED_ADDRESS.to_contain_text(self.new_address)


@allure.epic("E2E_22 Управление адресной информацией")
@allure.suite("E2E_22 Управление адресной информацией")
@allure.link(url="jira.nexign.com/browse/TUDS-1144", name="TUDS-1144")
@allure.link(
    url="confluence.nexign.com/pages/viewpage.action?pageId=585630877", name="ФС Форма Адреса на карточках клиента"
)
@pytest.mark.regress
class TestManageAddressInfo2:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login, create_organization: OrganizationClient) -> None:
        self.base_page = BasePage()
        self.client_profile_page = ClientProfilePage()
        self.edit_address_info = EditAddressInfo()
        self.client_request_api = ClientRequests()
        self.api_addresses = AddressRequests()

    @allure.title("Добавление адреса. Ввод уже существующего типа адреса")
    @allure.id(525415)
    @allure.description("Добавление адреса. Ввод уже существующего типа адреса для Клиента")
    def test_add_address_doubled_address_type(self, base_url: str) -> None:
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")

        self.client_profile_page.locators.CLIENT_TAB.click(timeout=10000)
        self.client_profile_page.locators.ADDRESSES_TAB.click()
        delay(1, reason="Без ожидания пустой список адресов")
        self.client_profile_page.locators.ADD_BTN.click()
        self.client_profile_page.add_address_form.TITLE.to_contain_text("Добавление адреса")
        self.client_profile_page.add_address_form.ADDRESS_TYPE_FIELD.open_dropdown()
        address_types = self.client_profile_page.add_address_form.ADDRESS_TYPE_FIELD.options
        with allure.step("Проверить, что нет возможности добавить второй 'Адрес регистрации'"):
            assert_that(
                lambda: "Адрес регистрации" not in address_types.keys(),
                "Присутствует возможность добавить второй 'Адрес регистрации'",
            )

    @allure.title("Добавление адреса. Ввод уже существующего типа адреса")
    @allure.id(533008)
    @allure.description("Добавление адреса. Ввод уже существующего типа адреса для связанного лица")
    def test_add_address_linked_person_doubled_address_type(self, base_url: str) -> None:
        linked_person_name = "мать драконов"
        self.client_request_api.create_linked_person_with_registration_address(
            client_id=test_context.client.user_id, name=linked_person_name
        )

        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")
        self.client_profile_page.locators.RELATED_PERSONS_TAB.click(timeout=10000)
        self.client_profile_page.locators.RELATED_PERSON_NAME.wait_to_have_text(linked_person_name)
        self.client_profile_page.locators.ADDRESSES_EDIT_BTN.click()

        self.edit_address_info.ADD_BUTTON.wait_to_be_visible()
        self.edit_address_info.ADD_BUTTON.click()

        self.client_profile_page.add_address_form.TITLE.to_contain_text("Добавление адреса")
        self.client_profile_page.add_address_form.SAVE_BTN.wait_to_be_visible()
        self.client_profile_page.add_address_form.ADDRESS_TYPE_FIELD.open_dropdown()
        address_types = self.client_profile_page.add_address_form.ADDRESS_TYPE_FIELD.options
        with allure.step("Проверить, что нет возможности добавить второй 'Адрес регистрации'"):
            assert_that(
                lambda: "Адрес регистрации" not in address_types.keys(),
                "Присутствует возможность добавить второй 'Адрес регистрации'",
            )

    @allure.title("Добавление адреса. Отмена добавления")
    @allure.id(525414)
    @allure.description("Добавление адреса. Отмена добавления для Клиента")
    def test_add_address_reject(self, base_url: str) -> None:
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")

        self.client_profile_page.locators.CLIENT_TAB.click(timeout=10000)
        self.client_profile_page.locators.ADDRESSES_TAB.click()
        delay(1, reason="Без ожидания пустой список адресов")
        self.client_profile_page.locators.ADD_BTN.click()
        self.client_profile_page.add_address_form.TITLE.to_contain_text("Добавление адреса")
        self.client_profile_page.add_address_form.ADDRESS_TYPE_FIELD.select_by_value("Фактический адрес")
        self.client_profile_page.add_address_form.ADDRESS_FIELD.select_by_value(BasicSystemAddress.address)
        self.client_profile_page.add_address_form.SAVE_BTN.to_be_enabled()
        self.client_profile_page.add_address_form.MAPS_LINK_INPUT.fill(AddressInfo.map_link)
        self.client_profile_page.add_address_form.CANCEL_BTN.click()
        self.client_profile_page.add_address_form.CANCEL_BTN.not_to_be_visible()

        self.client_profile_page.locators.TABLE_LINE[-1].to_contain_text(
            text=f"Адрес регистрации{BasicSystemAddress.address}"
        )
        assert self.client_profile_page.locators.TABLE_LINE.elements_len() == 1, "Добавилась строка с адресом"

    @allure.title("Добавление адреса. Отмена добавления")
    @allure.id(533010)
    @allure.description("Добавление адреса. Отмена добавления для связанного лица")
    def test_add_address_linked_person_reject(self, base_url: str) -> None:
        linked_person_name = "мать драконов"
        self.client_request_api.create_linked_person(client_id=test_context.client.user_id, name=linked_person_name)

        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")
        self.client_profile_page.locators.RELATED_PERSONS_TAB.click(timeout=10000)
        self.client_profile_page.locators.RELATED_PERSON_NAME.wait_to_have_text(linked_person_name)
        self.client_profile_page.locators.ADDRESSES_EDIT_BTN.click()

        self.edit_address_info.ADD_BUTTON.wait_to_be_visible()
        self.edit_address_info.ADD_BUTTON.click()

        self.client_profile_page.add_address_form.TITLE.to_contain_text("Добавление адреса")
        self.client_profile_page.add_address_form.SAVE_BTN.wait_to_be_visible()
        self.client_profile_page.add_address_form.ADDRESS_TYPE_FIELD.select_by_value("Адрес регистрации")
        self.client_profile_page.add_address_form.ADDRESS_FIELD.select_by_value(BasicSystemAddress.address)
        self.client_profile_page.add_address_form.SAVE_BTN.to_be_enabled()
        self.client_profile_page.add_address_form.MAPS_LINK_INPUT.fill(AddressInfo.map_link)
        self.client_profile_page.add_address_form.CANCEL_BTN.click()

        self.client_profile_page.add_address_form.CANCEL_BTN.not_to_be_visible()
        self.edit_address_info.TABLE_ADDRESSES.wait_to_have_count(0)

        self.edit_address_info.CANCEL_BTN.click()
        self.edit_address_info.CANCEL_BTN.not_to_be_visible()
        self.client_profile_page.locators.EXPAND_RELATED_ADDRESS_BTN.click()
        self.client_profile_page.locators.RELATED_ADDRESS.not_to_be_visible()

    @allure.title("Добавление адреса. Создание нового полного корректного адреса")
    @allure.id(532936)
    @allure.description("Добавление адреса. Создание нового полного корректного адреса для Клиента")
    def test_add_new_full_address(self, base_url: str) -> None:
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")
        building_number = generate_random_number(3)
        flat_number = generate_random_number(2)
        new_address = f"Россия, Самарская обл., г. Самара, ул. Осипенко, д. {building_number}, кв. {flat_number}"
        self.client_profile_page.locators.OVERVIEW_TAB.wait_to_be_visible(timeout=15000)
        self.client_profile_page.locators.CLIENT_TAB.click(timeout=10000)
        self.client_profile_page.locators.ADDRESSES_TAB.click()
        delay(1, reason="Без ожидания пустой список адресов")
        self.client_profile_page.locators.ADD_BTN.click()

        self.client_profile_page.add_address_form.TITLE.to_contain_text("Добавление адреса")
        self.client_profile_page.add_address_form.ADDRESS_TYPE_FIELD.select_by_value("Фактический адрес")
        self.client_profile_page.add_address_form.ADDRESS_INPUT.fill(new_address)
        self.client_profile_page.add_address_form.ADD_ADDRESS_TO_CATALOG.to_contain_text("Добавить адрес в справочник")
        self.client_profile_page.add_address_form.ADD_ADDRESS_TO_CATALOG.click()

        self.client_profile_page.fill_client_new_address(
            country="Россия",
            region="Самарская",
            city="Самара",
            street="Осипенко",
            building_number=building_number,
            flat_number=flat_number,
        )

        self.client_profile_page.create_address_form.ADD_ADDRESS_OBJECT_BTN.not_to_be_visible()
        self.client_profile_page.create_address_form.CREATE_BTN.click()
        self.client_profile_page.create_address_form.TITLE.not_to_be_visible()
        self.client_profile_page.add_address_form.TITLE.wait_to_be_visible()
        self.client_profile_page.add_address_form.ADDRESS_INPUT.to_have_value(new_address)
        self.client_profile_page.add_address_form.SAVE_BTN.click()
        self.client_profile_page.add_address_form.CANCEL_BTN.not_to_be_visible()
        self.client_profile_page.locators.TABLE_LINE.wait_to_have_count(2)
        self.client_profile_page.locators.TABLE_LINE[1].to_contain_text(text=f"Фактический адрес{new_address}")

    @allure.title("Добавление адреса. Создание нового полного корректного адреса")
    @allure.id(533009)
    @allure.description("Добавление адреса. Создание нового полного корректного адреса для связанного лица")
    def test_add_new_full_address_linked_person(self, base_url: str) -> None:
        linked_person_name = "мать драконов"
        self.client_request_api.create_linked_person(client_id=test_context.client.user_id, name=linked_person_name)
        building_number = generate_random_number(3)
        flat_number = generate_random_number(2)
        new_address = f"Россия, Самарская обл., г. Самара, ул. Осипенко, д. {building_number}, кв. {flat_number}"

        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")
        self.client_profile_page.locators.RELATED_PERSONS_TAB.click(timeout=10000)
        self.client_profile_page.locators.RELATED_PERSON_NAME.wait_to_have_text(linked_person_name)
        self.client_profile_page.locators.ADDRESSES_EDIT_BTN.click()

        self.edit_address_info.ADD_BUTTON.wait_to_be_visible()
        delay(1, reason="Без ожидания пустой список адресов")
        self.edit_address_info.ADD_BUTTON.click()

        self.client_profile_page.add_address_form.TITLE.to_contain_text("Добавление адреса")
        self.client_profile_page.add_address_form.SAVE_BTN.wait_to_be_visible()
        self.client_profile_page.add_address_form.ADDRESS_TYPE_FIELD.select_by_value("Адрес регистрации")
        self.client_profile_page.add_address_form.ADDRESS_INPUT.type(new_address)
        self.client_profile_page.add_address_form.ADD_ADDRESS_TO_CATALOG.to_contain_text("Добавить адрес в справочник")
        self.client_profile_page.add_address_form.ADD_ADDRESS_TO_CATALOG.click()

        self.client_profile_page.fill_client_new_address(
            country="Россия",
            region="Самарская",
            city="Самара",
            street="Осипенко",
            building_number=building_number,
            flat_number=flat_number,
        )

        self.client_profile_page.create_address_form.ADD_ADDRESS_OBJECT_BTN.not_to_be_visible()
        self.client_profile_page.create_address_form.CREATE_BTN.click()
        self.client_profile_page.create_address_form.TITLE.not_to_be_visible()
        self.client_profile_page.add_address_form.TITLE.wait_to_be_visible()
        self.client_profile_page.add_address_form.ADDRESS_INPUT.to_have_value(new_address)
        self.client_profile_page.add_address_form.SAVE_BTN.click()
        self.client_profile_page.add_address_form.CANCEL_BTN.not_to_be_visible()

        self.edit_address_info.TABLE_LINE.wait_to_have_count(1)
        self.edit_address_info.TABLE_LINE[0].to_contain_text(text=f"Адрес регистрации{new_address}")
        self.edit_address_info.CANCEL_BTN.click()

        self.edit_address_info.CANCEL_BTN.not_to_be_visible()
        self.client_profile_page.locators.EXPAND_RELATED_ADDRESS_BTN.click()
        self.client_profile_page.locators.RELATED_ADDRESS.to_contain_text(new_address)

    @allure.title("Настройка колонок. Выбран только 'Ccылка на карту'")
    @allure.id(525433)
    @allure.description(
        "Проверка отображения адресов в таблице при выборе колонки без наименования атрибута (Ссылка на карту)"
    )
    def test_columns_only_map(self, base_url: str) -> None:
        addresses = self.api_addresses.get_client_addresses(test_context.client.user_id)
        self.api_addresses.update_client_address(
            place_id=addresses.json()["items"][0]["placeId"],
            address=BasicSystemAddress.address,
            address_url=AddressInfo.map_link,
            external_address_id=BasicSystemAddress.external_address_id,
        )
        current_address = addresses.json()["items"][0]["addressString"]

        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")
        self.client_profile_page.locators.CLIENT_TAB.click(timeout=10000)
        self.client_profile_page.locators.ADDRESSES_TAB.click()
        self.client_profile_page.locators.SETTING_BTN.click()
        self.client_profile_page.locators.SETTING_OPTIONS[0].click()
        self.client_profile_page.locators.SETTING_OPTIONS[1].click()
        self.client_profile_page.locators.SETTING_BTN.click()

        self.client_profile_page.locators.TABLE_LINE[0].not_to_contain_text(text=f"Адрес регистрации{current_address}")
        self.client_profile_page.locators.TABLE_LINE_MAP_BUTTON[0].wait_to_be_visible()

    @allure.title("Настройка колонок. Выбран только 'Ccылка на карту'")
    @allure.id(533017)
    @allure.description(
        "Проверка отображения адресов в таблице при выборе колонки без наименования атрибута (Ссылка на карту)"
    )
    def test_columns_only_map_linked_person(self, base_url: str) -> None:
        linked_person_name = "мать драконов"
        self.client_request_api.create_linked_person(client_id=test_context.client.user_id, name=linked_person_name)

        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")
        self.client_profile_page.locators.RELATED_PERSONS_TAB.click(timeout=10000)
        self.client_profile_page.locators.RELATED_PERSON_NAME.wait_to_have_text(linked_person_name)
        self.client_profile_page.locators.ADDRESSES_EDIT_BTN.click()

        self.edit_address_info.ADD_BUTTON.wait_to_be_visible()
        self.edit_address_info.ADD_BUTTON.click()

        self.client_profile_page.add_address_form.TITLE.to_contain_text("Добавление адреса")
        self.client_profile_page.add_address_form.SAVE_BTN.wait_to_be_visible()
        self.client_profile_page.add_address_form.ADDRESS_TYPE_FIELD.select_by_value("Адрес регистрации")
        self.client_profile_page.add_address_form.ADDRESS_FIELD.select_by_value(BasicSystemAddress.address)
        self.client_profile_page.add_address_form.MAPS_LINK_INPUT.fill(AddressInfo.map_link)
        self.client_profile_page.add_address_form.SAVE_BTN.click()

        self.edit_address_info.SETTING_BTN.click()
        self.edit_address_info.SETTING_OPTIONS[0].click()
        self.edit_address_info.SETTING_OPTIONS[1].click()
        self.edit_address_info.SETTING_BTN.click()

        self.edit_address_info.TABLE_LINE[0].not_to_contain_text(text="Адрес регистрации")
        self.edit_address_info.TABLE_LINE_MAP_BUTTON[0].wait_to_be_visible()
