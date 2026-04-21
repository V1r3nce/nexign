import allure
import pytest

from api.nbss.address_requests import AddressRequests
from api.nbss.client_requests.client_requests import ClientRequests
from common.helpers.data_generator import generate_random_number
from common.helpers.time_helpers import delay
from models.address_info import AddressInfo, BasicSystemAddress
from models.client import OrganizationClient
from models.context import test_context
from pages.base_page import BasePage
from pages.locators.nbss.dynamic_form_elements import AddressCreate, EditAddress, EditAddressInfo, EditDynamicElements
from pages.nbss.client.client_profile_page import ClientProfilePage


@allure.epic("E2E_22 Управление адресной информацией")
@allure.suite("E2E_22 Управление адресной информацией")
@allure.link(url="jira.nexign.com/browse/TUDS-1144", name="TUDS-1144")
@allure.link(
    url="confluence.nexign.com/pages/viewpage.action?pageId=585630877", name="ФС Форма Адреса на карточках клиента"
)
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestManageAddressInfo4:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login, create_organization: OrganizationClient) -> None:
        self.base_page = BasePage()
        self.client_profile_page = ClientProfilePage()
        self.edit_address_info = EditAddressInfo()
        self.edit_address_form = EditAddress()
        self.edit_dynamic_elements = EditDynamicElements()
        self.create_address_form = AddressCreate()
        self.client_request_api = ClientRequests()
        self.address_request_api = AddressRequests()
        self.address = AddressInfo()

    @allure.title("Создание нового адреса. Введен уже созданный адресный объект")
    @allure.id(532929)
    @allure.description("Выполняется проверка игнорирования создания адресного объекта при вводе уже существующего")
    def test_create_new_available_address(self, base_url: str) -> None:
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")
        self.client_profile_page.locators.CLIENT_FIO.wait_to_be_visible(timeout=15000)
        self.client_profile_page.locators.LOAD_SPINS.wait_not_to_be_visible()

        building_number = generate_random_number(3)
        flat_number = generate_random_number(2)
        new_address = f"{self.address.country}, {self.address.region}, {self.address.city}, {self.address.street}, д. {building_number}, кв. {flat_number}"
        self.client_profile_page.locators.CLIENT_TAB.click()
        self.client_profile_page.locators.ADDRESSES_TAB.click()
        self.client_profile_page.locators.ADD_BTN.wait_to_be_visible()
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

    @allure.title("Создание нового адреса. Макс. заполнение адресных объектов (ввод всех данных)")
    @allure.id(532933)
    @allure.description(
        "Выполняется проверка создания адресного объекта при заполнении всех возможных типов адресных"
        " объектов и всех полей ввода для них"
    )
    def test_create_new_address_all_fields(self, base_url: str) -> None:
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")
        self.client_profile_page.locators.CLIENT_FIO.wait_to_be_visible(timeout=15000)
        self.client_profile_page.locators.LOAD_SPINS.wait_not_to_be_visible()

        building_number = generate_random_number(3)
        flat_number = generate_random_number(2)
        gar = "380"
        block = "7"
        building = "8"
        local_index = "443000"
        new_address = f"{self.address.country}, {self.address.region}, {self.address.city}, {self.address.street}, д. {building_number}, к. {block}, к. {building}, кв. {flat_number}"
        self.client_profile_page.locators.CLIENT_TAB.click()
        self.client_profile_page.locators.ADDRESSES_TAB.click()
        self.client_profile_page.locators.ADD_BTN.wait_to_be_visible()
        self.client_profile_page.locators.ADD_BTN.click()

        self.client_profile_page.add_address_form.TITLE.to_contain_text("Добавление адреса")
        self.client_profile_page.add_address_form.ADDRESS_TYPE_FIELD.select_by_value("Фактический адрес")
        self.client_profile_page.add_address_form.ADDRESS_INPUT.fill(new_address)
        self.client_profile_page.add_address_form.ADD_ADDRESS_TO_CATALOG.to_contain_text("Добавить адрес в справочник")
        self.client_profile_page.add_address_form.ADD_ADDRESS_TO_CATALOG.click()

        self.client_profile_page.fill_all_fields_client_new_address(
            country=self.address.country,
            region=self.address.region,
            city=self.address.city,
            street=self.address.street,
            building_number=building_number,
            flat_number=flat_number,
            gar=gar,
            block=block,
            building=building,
            address_index=local_index,
        )

        self.client_profile_page.create_address_form.ADD_ADDRESS_OBJECT_BTN.not_to_be_visible()
        self.client_profile_page.create_address_form.CREATE_BTN.click()
        self.client_profile_page.create_address_form.TITLE.not_to_be_visible()
        self.client_profile_page.add_address_form.TITLE.wait_to_be_visible()
        self.client_profile_page.add_address_form.ADDRESS_INPUT.to_have_value(new_address)

        self.client_profile_page.add_address_form.SAVE_BTN.click()
        self.client_profile_page.add_address_form.CANCEL_BTN.not_to_be_visible()

        self.client_profile_page.locators.TABLE_ADDRESSES.wait_to_have_count(2)
        self.client_profile_page.locators.TABLE_ADDRESSES[1].wait_to_have_text(new_address)
        self.client_profile_page.locators.TABLE_LINE_MAP_BUTTON.not_to_be_visible()

    @allure.title("Создание нового адреса. Мин. заполнение адресных объектов (ввод только обяз. данных)")
    @allure.id(532947)
    @allure.description(
        "Выполняется проверка создания адресного объекта при заполнении всех возможных типов адресных "
        "объектов и только обязательных полей ввода для них"
    )
    def test_create_new_address_fill_required_fields(self, base_url: str) -> None:
        self.base_page.open(
            f"{base_url}customer-hierarchy-management/customers/{test_context.client.user_id}/overview",
            wait="domcontentloaded",
        )
        self.client_profile_page.locators.CLIENT_FIO.wait_to_be_visible(timeout=15000)
        self.client_profile_page.locators.LOAD_SPINS.wait_not_to_be_visible()

        building_number = generate_random_number(3)
        flat_number = generate_random_number(2)
        new_address = f"{self.address.country}, {self.address.region}, {self.address.city}, {self.address.street}, д. {building_number}, кв. {flat_number}"
        self.client_profile_page.locators.CLIENT_TAB.click()
        self.client_profile_page.locators.ADDRESSES_TAB.click()
        self.client_profile_page.locators.ADD_BTN.wait_to_be_visible()
        self.client_profile_page.locators.ADD_BTN.click()

        self.client_profile_page.add_address_form.TITLE.to_contain_text("Добавление адреса")
        self.client_profile_page.add_address_form.ADDRESS_TYPE_FIELD.select_by_value("Фактический адрес")
        self.client_profile_page.add_address_form.ADDRESS_INPUT.fill(new_address)
        self.client_profile_page.add_address_form.ADD_ADDRESS_TO_CATALOG.to_contain_text("Добавить адрес в справочник")
        self.client_profile_page.add_address_form.ADD_ADDRESS_TO_CATALOG.click()

        self.client_profile_page.fill_required_fields_client_new_address(
            country=self.address.country,
            region=self.address.region,
            city=self.address.city,
            street=self.address.street,
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

        self.client_profile_page.locators.TABLE_ADDRESSES.wait_to_have_count(2)
        self.client_profile_page.locators.TABLE_ADDRESSES.to_contain_text_in_any(expected_text=new_address)
        self.client_profile_page.locators.TABLE_LINE_MAP_BUTTON.not_to_be_visible()

    @allure.title("Создание нового адреса. Отмена создания адреса")
    @allure.id(532948)
    @allure.description("Отмена при создании адресного объекта")
    def test_add_new_address_reject_button(self, base_url: str) -> None:
        self.base_page.open(
            f"{base_url}customer-hierarchy-management/customers/{test_context.client.user_id}/overview",
            wait="domcontentloaded",
        )
        self.client_profile_page.locators.CLIENT_FIO.wait_to_be_visible(timeout=15000)
        self.client_profile_page.locators.LOAD_SPINS.wait_not_to_be_visible()

        building_number = generate_random_number(3)
        flat_number = generate_random_number(2)
        new_address = f"{self.address.country}, {self.address.region}, {self.address.city}, {self.address.street}, д. {building_number}, кв. {flat_number}"
        self.client_profile_page.locators.CLIENT_TAB.click()
        self.client_profile_page.locators.ADDRESSES_TAB.click()
        self.client_profile_page.locators.ADD_BTN.wait_to_be_visible()
        self.client_profile_page.locators.ADD_BTN.click()

        self.client_profile_page.add_address_form.TITLE.to_contain_text("Добавление адреса")
        self.client_profile_page.add_address_form.ADDRESS_TYPE_FIELD.select_by_value("Фактический адрес")
        self.client_profile_page.add_address_form.ADDRESS_INPUT.fill(new_address)
        self.client_profile_page.add_address_form.ADD_ADDRESS_TO_CATALOG.to_contain_text("Добавить адрес в справочник")
        self.client_profile_page.add_address_form.ADD_ADDRESS_TO_CATALOG.click()

        self.client_profile_page.fill_client_new_address(
            country=self.address.country,
            region=self.address.region,
            city=self.address.city,
            street=self.address.street,
            building_number=building_number,
            flat_number=flat_number,
        )

        self.client_profile_page.create_address_form.ADD_ADDRESS_OBJECT_BTN.not_to_be_visible()
        self.client_profile_page.create_address_form.CANCEL_BTN.click()
        self.client_profile_page.create_address_form.TITLE.not_to_be_visible()
        self.client_profile_page.add_address_form.TITLE.wait_to_be_visible()
        self.client_profile_page.add_address_form.ADDRESS_INPUT.to_have_value(new_address)

    @allure.title("Создание нового адреса. Редактирование адресного объекта в процессе создания")
    @allure.id(533068)
    @allure.description("Выполняется проверка редактирования адресного объекта в процессе создания")
    def test_create_new_address_update_fields(self, base_url: str) -> None:
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")
        self.client_profile_page.locators.CLIENT_FIO.wait_to_be_visible(timeout=15000)
        self.client_profile_page.locators.LOAD_SPINS.wait_not_to_be_visible()

        building_number = generate_random_number(3)
        flat_number = generate_random_number(2)
        updated_address = f"{self.address.country}, {self.address.region}, {self.address.city}, {self.address.street}, д. {building_number * 2}, кв. {flat_number * 2}"
        self.client_profile_page.locators.CLIENT_TAB.click()
        self.client_profile_page.locators.ADDRESSES_TAB.click()
        self.client_profile_page.locators.ADD_BTN.wait_to_be_visible()
        self.client_profile_page.locators.ADD_BTN.click()

        self.client_profile_page.add_address_form.TITLE.to_contain_text("Добавление адреса")
        self.client_profile_page.add_address_form.ADDRESS_TYPE_FIELD.select_by_value("Фактический адрес")
        self.client_profile_page.add_address_form.ADDRESS_INPUT.click()
        self.client_profile_page.add_address_form.ADD_ADDRESS_TO_CATALOG.to_contain_text("Добавить адрес в справочник")
        self.client_profile_page.add_address_form.ADD_ADDRESS_TO_CATALOG.click()

        self.client_profile_page.fill_and_update_address_data(
            country="Беларусь",
            new_country="Россия",
            region="Свердловская обл.",
            new_region="Самарская обл.",
            city="г. Тольятти",
            new_city="г. Самара",
            street="ш. Московское",
            building_number=building_number,
            flat_number=flat_number,
        )

        self.client_profile_page.create_address_form.ADD_ADDRESS_OBJECT_BTN.not_to_be_visible()
        self.client_profile_page.create_address_form.CREATE_BTN.click()
        self.client_profile_page.create_address_form.TITLE.not_to_be_visible()
        self.client_profile_page.add_address_form.TITLE.wait_to_be_visible()
        self.client_profile_page.add_address_form.ADDRESS_INPUT.to_have_value(updated_address)

    @allure.title("Создание нового адреса. Удаление адресного объекта в процессе создания")
    @allure.id(533070)
    @allure.description("Выполняется проверка удаления адресного объекта в процессе создания")
    def test_create_new_address_remove_attribute_object(self, base_url: str) -> None:
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")
        self.client_profile_page.locators.CLIENT_FIO.wait_to_be_visible(timeout=15000)
        self.client_profile_page.locators.LOAD_SPINS.wait_not_to_be_visible()

        building_number = generate_random_number(3)
        flat_number = generate_random_number(2)
        new_address = f"{self.address.country}, {self.address.region}, {self.address.city}, {self.address.street}, д. {building_number}, кв. {flat_number}"
        updated_address = f"{self.address.country}, {self.address.region}, {self.address.city}, {self.address.street}, д. {building_number}"
        self.client_profile_page.locators.CLIENT_TAB.click()
        self.client_profile_page.locators.ADDRESSES_TAB.click()
        self.client_profile_page.locators.ADD_BTN.wait_to_be_visible()
        self.client_profile_page.locators.ADD_BTN.click()

        self.client_profile_page.add_address_form.TITLE.to_contain_text("Добавление адреса")
        self.client_profile_page.add_address_form.ADDRESS_TYPE_FIELD.select_by_value("Фактический адрес")
        self.client_profile_page.add_address_form.ADDRESS_INPUT.fill(new_address)
        self.client_profile_page.add_address_form.ADD_ADDRESS_TO_CATALOG.to_contain_text("Добавить адрес в справочник")
        self.client_profile_page.add_address_form.ADD_ADDRESS_TO_CATALOG.click()

        self.client_profile_page.fill_required_fields_client_new_address(
            country=self.address.country,
            region=self.address.region,
            city=self.address.city,
            street=self.address.street,
            building_number=building_number,
            flat_number=flat_number,
        )

        self.client_profile_page.create_address_form.ADD_ADDRESS_OBJECT_BTN.not_to_be_visible()
        self.client_profile_page.create_address_form.ADDED_CARD_DELETE_BTN[-1].click()
        self.create_address_form.ATTRIBUTE_HEADER[-1].click()
        self.create_address_form.ATTRIBUTE_FIELDS[-1].to_have_value("—")
        self.create_address_form.ATTRIBUTE_FIELDS[-7].to_have_value(str(building_number))
        self.client_profile_page.create_address_form.CREATE_BTN.click()
        self.client_profile_page.create_address_form.TITLE.not_to_be_visible()
        self.client_profile_page.add_address_form.TITLE.wait_to_be_visible()
        self.client_profile_page.add_address_form.ADDRESS_INPUT.to_have_value(updated_address)

    @allure.title("Удаление адреса. Выбран тип адреса отличный от Адрес регистрации")
    @allure.id(525422)
    @allure.description("Проверка удаления адреса клиента при выборе типа, отличного от Адрес регистрации")
    def test_remove_second_address(self, base_url: str) -> None:
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")
        self.client_profile_page.locators.CLIENT_FIO.wait_to_be_visible(timeout=15000)
        self.client_profile_page.locators.LOAD_SPINS.wait_not_to_be_visible()

        self.client_profile_page.locators.CLIENT_TAB.wait_to_be_visible(timeout=30000)
        self.client_profile_page.locators.CLIENT_TAB.click()
        self.client_profile_page.locators.ADDRESSES_TAB.wait_to_be_visible(timeout=15000)
        self.client_profile_page.locators.ADDRESSES_TAB.click()
        self.client_profile_page.locators.TABLE_ADDRESSES.wait_to_have_count(1, timeout=15000)
        self.client_profile_page.locators.ADD_BTN.wait_to_be_visible(timeout=10000)
        self.client_profile_page.locators.ADD_BTN.click()
        self.client_profile_page.add_address_form.TITLE.to_contain_text("Добавление адреса")
        self.client_profile_page.add_address_form.ADDRESS_TYPE_FIELD.select_by_value("Фактический адрес")
        self.client_profile_page.add_address_form.ADDRESS_FIELD.select_by_value(
            BasicSystemAddress.address, include_last_symbol=True
        )
        self.client_profile_page.add_address_form.SAVE_BTN.to_be_enabled()
        self.client_profile_page.add_address_form.SAVE_BTN.click()
        self.client_profile_page.locators.TABLE_ADDRESSES.wait_to_have_count(2, timeout=15000)

        self.client_profile_page.locators.TABLE_ADDRESS_TYPES.wait_to_be_visible()
        delete_address = self.client_profile_page.locators.TABLE_ADDRESS_TYPES.get_element_by_text(
            text="Фактический адрес"
        )
        delete_address.click()
        self.client_profile_page.locators.DELETE_ADDRESS.wait_to_be_visible(timeout=10000)
        self.client_profile_page.locators.DELETE_ADDRESS.to_be_enabled()
        self.client_profile_page.locators.DELETE_ADDRESS.click()

        self.client_profile_page.base_elements.MODAL.wait_to_have_count(1, timeout=10000)
        self.client_profile_page.base_elements.MODAL_TITLE[0].to_contain_text("Удаление адреса")
        self.client_profile_page.base_elements.MODAL_TITLE[0].to_contain_text(
            f'Вы действительно хотите удалить "Фактический адрес: {BasicSystemAddress.address}"?'
        )
        self.client_profile_page.base_elements.MODAL_FIRST_BTN.to_contain_text("Отмена")
        self.client_profile_page.base_elements.MODAL_SECOND_BTN.to_contain_text("Удалить")
        self.client_profile_page.base_elements.MODAL_SECOND_BTN.click()

        self.client_profile_page.locators.TABLE_ADDRESSES.wait_to_have_count(1, timeout=15000)
        self.client_profile_page.locators.TABLE_ADDRESS_TYPES[0].to_contain_text(text="Адрес регистрации")

    @allure.title("Удаление адреса. Выбран тип Адрес регистрации клиента")
    @allure.id(525410)
    @allure.description("Получение ошибки при удалении адреса с типом Адрес регистрации")
    def test_remove_address_choose_main_address(self, base_url: str) -> None:
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")
        self.client_profile_page.locators.CLIENT_FIO.wait_to_be_visible(timeout=15000)
        self.client_profile_page.locators.LOAD_SPINS.wait_not_to_be_visible()

        self.client_profile_page.locators.CLIENT_TAB.click()
        self.client_profile_page.locators.ADDRESSES_TAB.click()
        self.client_profile_page.locators.TABLE_ADDRESSES.wait_to_have_count(1)

        self.client_profile_page.locators.TABLE_ADDRESS_TYPES[0].click()
        self.client_profile_page.locators.DELETE_ADDRESS.not_to_be_enabled()
        self.client_profile_page.locators.DELETE_ADDRESS.hover()
        self.client_profile_page.locators.TOOLTIP_MESSAGE.wait_to_have_text(
            "Удаление адреса недоступно, так как для объекта иерархии добавлено минимально допустимое количество адресов выбранного типа"
        )

    @allure.title("Удаление адреса. Отмена удаления")
    @allure.id(526073)
    @allure.description("При подтверждения операции удаления адреса пользователь отменил операцию")
    def test_reject_remove_address(self, base_url: str) -> None:
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")
        self.client_profile_page.locators.CLIENT_FIO.wait_to_be_visible(timeout=15000)
        self.client_profile_page.locators.LOAD_SPINS.wait_not_to_be_visible()

        self.client_profile_page.locators.CLIENT_TAB.click()
        self.client_profile_page.locators.ADDRESSES_TAB.click()
        self.client_profile_page.locators.ADD_BTN.wait_to_be_visible()
        self.client_profile_page.locators.ADD_BTN.click()
        self.client_profile_page.add_address_form.TITLE.to_contain_text("Добавление адреса")
        self.client_profile_page.add_address_form.ADDRESS_TYPE_FIELD.select_by_value("Фактический адрес")
        self.client_profile_page.add_address_form.ADDRESS_FIELD.select_by_value(
            BasicSystemAddress.address, include_last_symbol=True
        )
        self.client_profile_page.add_address_form.SAVE_BTN.to_be_enabled()
        self.client_profile_page.add_address_form.SAVE_BTN.click()
        self.client_profile_page.locators.TABLE_ADDRESSES.wait_to_have_count(2)

        self.client_profile_page.locators.TABLE_ADDRESS_TYPES[1].click()
        self.client_profile_page.locators.DELETE_ADDRESS.click()

        self.client_profile_page.base_elements.MODAL.wait_to_have_count(1)
        self.client_profile_page.base_elements.MODAL_TITLE[0].to_contain_text("Удаление адреса")
        self.client_profile_page.base_elements.MODAL_TITLE[0].to_contain_text(
            f'Вы действительно хотите удалить "Фактический адрес: {BasicSystemAddress.address}"?'
        )
        self.client_profile_page.base_elements.MODAL_FIRST_BTN.to_contain_text("Отмена")
        self.client_profile_page.base_elements.MODAL_SECOND_BTN.to_contain_text("Удалить")
        self.client_profile_page.base_elements.MODAL_FIRST_BTN.click()

        self.client_profile_page.locators.TABLE_ADDRESS_TYPES[1].to_contain_text(text="Фактический адрес")
        self.client_profile_page.locators.TABLE_ADDRESSES.wait_to_have_count(2)

    @allure.title("Просмотр адреса по ссылке на карту")
    @allure.id(533014)
    @allure.description("Просмотр адреса связанного лица при переходе по ссылке на карту")
    def test_check_map_link_linked_person(self, base_url: str) -> None:
        linked_person_name = "мать драконов"
        linked_person_id = self.client_request_api.create_linked_person_with_registration_address(
            client_id=test_context.client.user_id, name=linked_person_name
        )
        addresses = self.address_request_api.get_linked_person_addresses(linked_person_id)
        self.address_request_api.update_client_address(
            place_id=addresses.json()["items"][0]["placeId"],
            address=BasicSystemAddress.address,
            address_url=AddressInfo.available_link,
            external_address_id=BasicSystemAddress.external_address_id,
        )

        self.base_page.open(
            f"{base_url}customer-hierarchy-management/customers/{test_context.client.user_id}/overview",
            wait="domcontentloaded",
        )
        self.client_profile_page.locators.CLIENT_FIO.wait_to_be_visible(timeout=15000)
        self.client_profile_page.locators.LOAD_SPINS.wait_not_to_be_visible()

        self.client_profile_page.locators.RELATED_PERSONS_TAB.click()
        self.client_profile_page.locators.RELATED_PERSON_NAME.wait_to_have_text(linked_person_name)
        self.client_profile_page.locators.ADDRESSES_EDIT_BTN.click()

        self.edit_address_info.TABLE_LINE_MAP_BUTTON.wait_to_have_count(1)

        context = test_context.page.context
        with context.expect_page() as new_page_info:
            self.edit_address_info.TABLE_LINE_MAP_BUTTON[0].click()
            new_page = new_page_info.value
        assert AddressInfo.available_link in new_page.url, (
            f"Некорректный адрес {new_page.url} открывшейся карты, ожидаемый адрес {AddressInfo.available_link}"
        )

    @allure.title("Редактирование адреса. Ввод всех полей")
    @allure.id(533051)
    @allure.description("Выполняется проверка редактирования данных адреса связанного лица с изменением всех полей")
    def test_edit_address_linked_person_all_fields(self, base_url: str, add_new_address_to_lam: dict) -> None:
        linked_person_name = "мать драконов"
        self.client_request_api.create_linked_person_with_registration_address(
            client_id=test_context.client.user_id, name=linked_person_name
        )
        new_address = add_new_address_to_lam["addressString"]
        short_address = new_address.split("ул. ")[1]

        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")
        self.client_profile_page.locators.CLIENT_FIO.wait_to_be_visible(timeout=15000)
        self.client_profile_page.locators.LOAD_SPINS.wait_not_to_be_visible()

        self.client_profile_page.locators.RELATED_PERSONS_TAB.click()
        self.client_profile_page.locators.RELATED_PERSON_NAME.wait_to_have_text(linked_person_name)
        self.client_profile_page.locators.ADDRESSES_EDIT_BTN.click()

        self.edit_address_info.TABLE_ADDRESS_TYPES.wait_to_have_count(1)
        self.edit_address_info.TABLE_ADDRESS_TYPES[0].click()
        self.edit_address_info.EDIT_ADDRESS.click()

        self.edit_address_form.TITLE.to_contain_text("Редактирование адреса")
        self.edit_address_form.ADDRESS_INPUT.fill("Россия, " + short_address)
        self.edit_address_form.ADDRESS_OPTION.wait_elements_visible(0)
        self.edit_address_form.ADDRESS_OPTION[0].to_contain_text(text=short_address)
        self.edit_address_form.ADDRESS_OPTION[0].click()
        self.edit_address_form.CANCEL_BTN.to_be_enabled()
        self.edit_address_form.SAVE_BTN.to_be_enabled()
        self.edit_address_form.MAPS_LINK_INPUT.fill(AddressInfo.map_link)
        self.edit_address_form.SAVE_BTN.click()
        self.edit_address_form.CANCEL_BTN.not_to_be_visible()

        self.edit_address_info.TABLE_ADDRESSES[0].wait_to_have_text(new_address)
        self.edit_address_info.TABLE_LINE_MAP_BUTTON[0].wait_to_be_visible()
        self.edit_address_info.CANCEL_BTN.click()

        self.edit_address_info.CANCEL_BTN.not_to_be_visible()
        self.client_profile_page.locators.EXPAND_RELATED_ADDRESS_BTN.click()
        self.client_profile_page.locators.RELATED_ADDRESS.to_contain_text(new_address)

    @allure.title("Редактирование адреса. Ввод только обязательных полей")
    @allure.id(533050)
    @allure.description(
        "Выполняется проверка редактирования данных адреса связанного лица с изменением только обязательных полей"
    )
    def test_edit_address_linked_person_required_fields(self, base_url: str, add_new_address_to_lam: dict) -> None:
        linked_person_name = "мать драконов"
        self.client_request_api.create_linked_person_with_registration_address(
            client_id=test_context.client.user_id, name=linked_person_name
        )
        new_address = add_new_address_to_lam["addressString"]
        short_address = new_address.split("ул. ")[1]

        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")
        self.client_profile_page.locators.CLIENT_FIO.wait_to_be_visible(timeout=15000)
        self.client_profile_page.locators.LOAD_SPINS.wait_not_to_be_visible()

        self.client_profile_page.locators.RELATED_PERSONS_TAB.click()
        self.client_profile_page.locators.RELATED_PERSON_NAME.wait_to_have_text(linked_person_name)
        self.client_profile_page.locators.ADDRESSES_EDIT_BTN.click()

        self.edit_address_info.TABLE_ADDRESS_TYPES.wait_to_have_count(1)
        self.edit_address_info.TABLE_ADDRESS_TYPES[0].click()
        self.edit_address_info.EDIT_ADDRESS.click()

        self.edit_address_form.TITLE.to_contain_text("Редактирование адреса")
        self.edit_address_form.ADDRESS_INPUT.fill("Россия, " + short_address)
        self.edit_address_form.ADDRESS_OPTION.wait_elements_visible(0)
        self.edit_address_form.ADDRESS_OPTION[0].to_contain_text(text=short_address)
        self.edit_address_form.ADDRESS_OPTION[0].click()
        self.edit_address_form.CANCEL_BTN.to_be_enabled()
        self.edit_address_form.SAVE_BTN.to_be_enabled()
        self.edit_address_form.SAVE_BTN.click()
        self.edit_address_form.CANCEL_BTN.not_to_be_visible()

        self.edit_address_info.TABLE_ADDRESSES[0].wait_to_have_text(new_address)
        self.edit_address_info.TABLE_LINE_MAP_BUTTON.wait_to_have_count(0)
        self.edit_address_info.CANCEL_BTN.click()

        self.edit_address_info.CANCEL_BTN.not_to_be_visible()
        self.client_profile_page.locators.EXPAND_RELATED_ADDRESS_BTN.click()
        self.client_profile_page.locators.RELATED_ADDRESS.to_contain_text(new_address)

    @allure.title("Редактирование адреса. Отмена редактирования адреса")
    @allure.id(533052)
    @allure.description("Проверка закрытия формы редактирования адреса связанного лица без сохранения при отмене")
    def test_address_edit_reject_button_linked_person(self, base_url: str, add_new_address_to_lam: dict) -> None:
        linked_person_name = "мать драконов"
        self.client_request_api.create_linked_person_with_registration_address(
            client_id=test_context.client.user_id, name=linked_person_name
        )
        new_address = add_new_address_to_lam["addressString"]
        short_address = new_address.split("ул. ")[1]

        self.base_page.open(
            f"{base_url}customer-hierarchy-management/customers/{test_context.client.user_id}/overview",
            wait="domcontentloaded",
        )
        self.client_profile_page.locators.CLIENT_FIO.wait_to_be_visible(timeout=15000)
        self.client_profile_page.locators.LOAD_SPINS.wait_not_to_be_visible()

        self.client_profile_page.locators.RELATED_PERSONS_TAB.click()
        self.client_profile_page.locators.RELATED_PERSON_NAME.wait_to_have_text(linked_person_name)
        self.client_profile_page.locators.ADDRESSES_EDIT_BTN.click()

        self.edit_address_info.TABLE_ADDRESS_TYPES.wait_to_have_count(1)
        self.edit_address_info.TABLE_ADDRESS_TYPES[0].click()
        self.edit_address_info.EDIT_ADDRESS.click()

        self.edit_address_form.TITLE.to_contain_text("Редактирование адреса")
        self.edit_address_form.ADDRESS_INPUT.fill("Россия, " + short_address)
        self.edit_address_form.ADDRESS_OPTION.wait_elements_visible(0)
        self.edit_address_form.ADDRESS_OPTION[0].to_contain_text(text=short_address)
        self.edit_address_form.ADDRESS_OPTION[0].click()
        self.edit_address_form.CANCEL_BTN.to_be_enabled()
        self.edit_address_form.SAVE_BTN.to_be_enabled()
        self.edit_address_form.CANCEL_BTN.click()
        self.edit_address_form.CANCEL_BTN.not_to_be_visible()

        self.edit_address_info.TABLE_ADDRESSES[0].wait_to_have_text(BasicSystemAddress.address)
        self.edit_address_info.TABLE_LINE_MAP_BUTTON.wait_to_have_count(0)
        self.edit_address_info.CANCEL_BTN.click()

        self.edit_address_info.CANCEL_BTN.not_to_be_visible()
        self.client_profile_page.locators.EXPAND_RELATED_ADDRESS_BTN.click()
        self.client_profile_page.locators.RELATED_ADDRESS.to_contain_text(BasicSystemAddress.address)

    @allure.title("Редактирование адреса. Создание нового полного корректного адреса")
    @allure.id(533049)
    @allure.description(
        "Выполняется проверка редактирования адреса связанного лица с созданием нового полного"
        " корректного адреса в справочнике адресов"
    )
    def test_address_edit_create_new_addresses_linked_person(self, base_url: str) -> None:
        linked_person_name = "мать драконов"
        self.client_request_api.create_linked_person_with_registration_address(
            client_id=test_context.client.user_id, name=linked_person_name
        )
        building_number = generate_random_number(3)
        flat_number = generate_random_number(2)
        new_address = f"{self.address.country}, {self.address.region}, {self.address.city}, {self.address.street}, д. {building_number}, кв. {flat_number}"

        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")
        self.client_profile_page.locators.CLIENT_FIO.wait_to_be_visible(timeout=15000)
        self.client_profile_page.locators.LOAD_SPINS.wait_not_to_be_visible()

        self.client_profile_page.locators.RELATED_PERSONS_TAB.click()
        self.client_profile_page.locators.RELATED_PERSON_NAME.wait_to_have_text(linked_person_name)
        self.client_profile_page.locators.ADDRESSES_EDIT_BTN.click()

        self.edit_address_info.TABLE_ADDRESS_TYPES.wait_to_have_count(1)
        self.edit_address_info.TABLE_ADDRESS_TYPES[0].click()
        self.edit_address_info.EDIT_ADDRESS.click()

        self.edit_address_form.TITLE.to_contain_text("Редактирование адреса")
        delay(1, reason="Если раньше ввести строку, зависает UI")
        self.edit_address_form.ADDRESS_INPUT.fill(new_address)
        self.edit_address_form.ADD_ADDRESS_TO_CATALOG.click()

        self.client_profile_page.fill_client_new_address(
            country=self.address.country,
            region=self.address.region,
            city=self.address.city,
            street=self.address.street,
            building_number=building_number,
            flat_number=flat_number,
        )

        self.client_profile_page.create_address_form.ADD_ADDRESS_OBJECT_BTN.not_to_be_visible()
        self.edit_dynamic_elements.CREATE_BTN.click()
        self.client_profile_page.create_address_form.TITLE.not_to_be_visible()
        self.edit_address_form.TITLE.wait_to_be_visible()
        self.edit_address_form.ADDRESS_INPUT.to_have_value(new_address)

        self.edit_address_form.SAVE_BTN.click()
        self.edit_address_form.CANCEL_BTN.not_to_be_visible()

        self.edit_address_info.TABLE_ADDRESSES[0].wait_to_have_text(new_address)
        self.edit_address_info.CANCEL_BTN.click()

        self.edit_address_info.CANCEL_BTN.not_to_be_visible()
        self.client_profile_page.locators.EXPAND_RELATED_ADDRESS_BTN.click()
        self.client_profile_page.locators.RELATED_ADDRESS.to_contain_text(new_address)

    @allure.title("Удаление адреса. Выбран тип Адрес регистрации клиента")
    @allure.id(533035)
    @allure.description("Получение ошибки при удалении адреса с типом Адрес регистрации связанного лица")
    def test_remove_address_linked_person_choose_main_address(self, base_url: str) -> None:
        linked_person_name = "мать драконов"
        self.client_request_api.create_linked_person_with_registration_address(
            client_id=test_context.client.user_id, name=linked_person_name
        )

        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")
        self.client_profile_page.locators.CLIENT_FIO.wait_to_be_visible(timeout=15000)
        self.client_profile_page.locators.LOAD_SPINS.wait_not_to_be_visible()

        self.client_profile_page.locators.RELATED_PERSONS_TAB.click()
        self.client_profile_page.locators.RELATED_PERSON_NAME.wait_to_have_text(linked_person_name)
        self.client_profile_page.locators.ADDRESSES_EDIT_BTN.click()

        self.edit_address_info.TABLE_ADDRESS_TYPES.wait_to_have_count(1)
        self.edit_address_info.TABLE_ADDRESS_TYPES[0].click()
        self.client_profile_page.locators.DELETE_ADDRESS.not_to_be_enabled()
        self.client_profile_page.locators.DELETE_ADDRESS.hover()
        self.client_profile_page.locators.TOOLTIP_MESSAGE.wait_to_have_text(
            "Удаление адреса недоступно, так как для объекта иерархии добавлено минимально допустимое количество адресов выбранного типа"
        )
