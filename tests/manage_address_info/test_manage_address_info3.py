import pytest
import allure
from playwright.sync_api import Page
from common.helpers.data_generator import generate_random_number
from common.helpers.time_helpers import delay
from models.address_info import BasicSystemAddress
from pages.base_page import BasePage
from pages.client_profile_page import ClientProfilePage
from pages.locators.dynamic_form_elements import EditAddressInfo, EditAddress, AddressCreate, EditDynamicElements


@allure.epic("Управление адресной информацией")
@allure.suite("Управление адресной информацией")
class TestManageAddressInfo4:
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.base_page = BasePage(page)
        self.client_profile_page = ClientProfilePage(page)
        self.client_edit_address_form = EditAddress(page)
        self.edit_address_info = EditAddressInfo(page)
        self.create_address_form = AddressCreate(page)
        self.edit_dynamic_elements = EditDynamicElements(page)

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

    @allure.title("Создание нового адреса. Макс. заполнение адресных объектов (ввод всех данных)")
    @allure.id(532933)
    @allure.description("Выполняется проверка создания адресного объекта при заполнении всех возможных типов адресных"
                        " объектов и всех полей ввода для них")
    @allure.link(url="jira.nexign.com/browse/TUDS-1144", name="TUDS-1144")
    @allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=585630877",
                 name="ФС Форма Адреса на карточках клиента")
    @allure.tag("can_auth", "success")
    def test_create_new_address_all_fields(self, base_url: str, create_user: int):
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{create_user}/overview")
        building_number = generate_random_number(3)
        flat_number = generate_random_number(2)
        gar = "380"
        block = "7"
        building = "8"
        local_index = "443000"
        new_address = (f"Россия, Самарская обл., г. Самара, ул. Осипенко, д. {building_number}, к. {block}, к. "
                       f"{building}, кв. {flat_number}")
        self.client_profile_page.click_client_tab()
        self.client_profile_page.locators.ADDRESSES_TAB.click()
        delay(1, reason="Без ожидания пустой список адресов")
        self.client_profile_page.locators.ADD_BTN.click()

        self.client_profile_page.add_address_form.TITLE.to_contain_text("Добавление адреса")
        self.client_profile_page.add_address_form.ADDRESS_TYPE_FIELD.select_by_value("Фактический адрес")
        self.client_profile_page.add_address_form.ADDRESS_INPUT.fill(new_address)
        self.client_profile_page.add_address_form.ADD_ADDRESS_TO_CATALOG.to_contain_text("Добавить адрес в справочник")
        self.client_profile_page.add_address_form.ADD_ADDRESS_TO_CATALOG.click()

        self.client_profile_page.fill_all_fields_client_new_address(country="Россия", region="Самарская", city="Самара",
                                                                    street="Осипенко", building_number=building_number,
                                                                    flat_number=flat_number, gar=gar, block=block,
                                                                    building=building, address_index=local_index)

        self.client_profile_page.create_address_form.ADD_ADDRESS_OBJECT_BTN.not_to_be_visible()
        self.client_profile_page.create_address_form.CREATE_BTN.click()
        self.client_profile_page.create_address_form.TITLE.not_to_be_visible()
        self.client_profile_page.add_address_form.TITLE.wait_to_be_visible()
        self.client_profile_page.add_address_form.ADDRESS_INPUT.to_have_value(new_address)

        self.client_profile_page.add_address_form.SAVE_BTN.click()
        self.client_profile_page.add_address_form.CANCEL_BTN.not_to_be_visible()

        self.client_profile_page.locators.TABLE_ADDRESSES[1].wait_to_have_text(new_address)
        self.client_profile_page.locators.TABLE_LINE_MAP_BUTTON.not_to_be_visible()

    @allure.title("Создание нового адреса. Мин. заполнение адресных объектов (ввод только обяз. данных)")
    @allure.id(532947)
    @allure.description("Выполняется проверка создания адресного объекта при заполнении всех возможных типов адресных "
                        "объектов и только обязательных полей ввода для них")
    @allure.link(url="jira.nexign.com/browse/TUDS-1144", name="TUDS-1144")
    @allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=585630877",
                 name="ФС Форма Адреса на карточках клиента")
    @allure.tag("can_auth", "success")
    def test_create_new_address_fill_required_fields(self, base_url: str, create_user: int):
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

        self.client_profile_page.fill_required_fields_client_new_address(country="Россия", region="Самарская",
                                                                         city="Самара", street="Осипенко",
                                                                         building_number=building_number,
                                                                         flat_number=flat_number)

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

    @allure.title("Создание нового адреса. Отмена создания адреса")
    @allure.id(532948)
    @allure.description("Отмена при создании адресного объекта")
    @allure.link(url="jira.nexign.com/browse/TUDS-1144", name="TUDS-1144")
    @allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=585630877",
                 name="ФС Форма Адреса на карточках клиента")
    @allure.tag("can_auth", "success")
    def test_add_new_address_reject_button(self, base_url: str, create_user: int):
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

        self.client_profile_page.fill_client_new_address(country="Россия", region="Самарская", city="Самара",
                                                         street="Осипенко", building_number=building_number,
                                                         flat_number=flat_number)

        self.client_profile_page.create_address_form.ADD_ADDRESS_OBJECT_BTN.not_to_be_visible()
        self.client_profile_page.create_address_form.CANCEL_BTN.click()
        self.client_profile_page.create_address_form.TITLE.not_to_be_visible()
        self.client_profile_page.add_address_form.TITLE.wait_to_be_visible()
        self.client_profile_page.add_address_form.ADDRESS_INPUT.to_have_value("")

    @allure.title("Создание нового адреса. Редактирование адресного объекта в процессе создания")
    @allure.id(533068)
    @allure.description("Выполняется проверка редактирования адресного объекта в процессе создания")
    @allure.link(url="jira.nexign.com/browse/TUDS-1144", name="TUDS-1144")
    @allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=585630877",
                 name="ФС Форма Адреса на карточках клиента")
    @allure.tag("can_auth", "success")
    def test_create_new_address_update_fields(self, base_url: str, create_user: int):
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{create_user}/overview")
        building_number = generate_random_number(3)
        flat_number = generate_random_number(2)
        updated_address = (f"Тайланд, Пхукетская обл., г. Чалонг, ул. Осипенкотест, д. {building_number*2},"
                           f" кв. {flat_number*2}")
        self.client_profile_page.click_client_tab()
        self.client_profile_page.locators.ADDRESSES_TAB.click()
        delay(1, reason="Без ожидания пустой список адресов")
        self.client_profile_page.locators.ADD_BTN.click()

        self.client_profile_page.add_address_form.TITLE.to_contain_text("Добавление адреса")
        self.client_profile_page.add_address_form.ADDRESS_TYPE_FIELD.select_by_value("Фактический адрес")
        self.client_profile_page.add_address_form.ADDRESS_INPUT.click()
        self.client_profile_page.add_address_form.ADD_ADDRESS_TO_CATALOG.to_contain_text("Добавить адрес в справочник")
        self.client_profile_page.add_address_form.ADD_ADDRESS_TO_CATALOG.click()

        self.client_profile_page.fill_and_update_address_data(country="Россия", new_country="Тайланд",
                                                              region="Самарская", new_region="Пхукетская",
                                                              city="Самара", new_city="Чалонг", street="Осипенко",
                                                              building_number=building_number,
                                                              flat_number=flat_number)

        self.client_profile_page.create_address_form.ADD_ADDRESS_OBJECT_BTN.not_to_be_visible()
        self.client_profile_page.create_address_form.CREATE_BTN.click()
        self.client_profile_page.create_address_form.TITLE.not_to_be_visible()
        self.client_profile_page.add_address_form.TITLE.wait_to_be_visible()
        self.client_profile_page.add_address_form.ADDRESS_INPUT.to_have_value(updated_address)

    @allure.title("Создание нового адреса. Удаление адресного объекта в процессе создания")
    @allure.id(533070)
    @allure.description("Выполняется проверка удаления адресного объекта в процессе создания")
    @allure.link(url="jira.nexign.com/browse/TUDS-1144", name="TUDS-1144")
    @allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=585630877",
                 name="ФС Форма Адреса на карточках клиента")
    @allure.tag("can_auth", "success")
    def test_create_new_address_remove_attribute_object(self, base_url: str, create_user: int):
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{create_user}/overview")
        building_number = generate_random_number(3)
        flat_number = generate_random_number(2)
        new_address = (f"Россия, Самарская обл., г. Самара, ул. Осипенко, д. {building_number},"
                       f" кв. {flat_number}")
        updated_address = f"Россия, Самарская обл., г. Самара, ул. Осипенко, д. {building_number}"
        self.client_profile_page.click_client_tab()
        self.client_profile_page.locators.ADDRESSES_TAB.click()
        delay(1, reason="Без ожидания пустой список адресов")
        self.client_profile_page.locators.ADD_BTN.click()

        self.client_profile_page.add_address_form.TITLE.to_contain_text("Добавление адреса")
        self.client_profile_page.add_address_form.ADDRESS_TYPE_FIELD.select_by_value("Фактический адрес")
        self.client_profile_page.add_address_form.ADDRESS_INPUT.fill(new_address)
        self.client_profile_page.add_address_form.ADD_ADDRESS_TO_CATALOG.to_contain_text("Добавить адрес в справочник")
        self.client_profile_page.add_address_form.ADD_ADDRESS_TO_CATALOG.click()

        self.client_profile_page.fill_required_fields_client_new_address(country="Россия", region="Самарская",
                                                                         city="Самара", street="Осипенко",
                                                                         building_number=building_number,
                                                                         flat_number=flat_number)

        self.client_profile_page.create_address_form.ADD_ADDRESS_OBJECT_BTN.not_to_be_visible()
        self.client_profile_page.create_address_form.ADDED_CARD_DELETE_BTN[-1].click()
        self.create_address_form.ATTRIBUTE_HEADER[-1].click()
        self.create_address_form.ATTRIBUTE_FIELDS[-1].to_have_value("—")
        self.client_profile_page.create_address_form.CREATE_BTN.click()
        self.client_profile_page.create_address_form.TITLE.not_to_be_visible()
        self.client_profile_page.add_address_form.TITLE.wait_to_be_visible()
        self.client_profile_page.add_address_form.ADDRESS_INPUT.to_have_value(updated_address)

    @allure.title("Удаление адреса. Выбран тип адреса отличный от Адрес регистрации")
    @allure.id(525422)
    @allure.description("Проверка удаления адреса клиента при выборе типа, отличного от Адрес регистрации")
    @allure.link(url="jira.nexign.com/browse/TUDS-1144", name="TUDS-1144")
    @allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=585630877",
                 name="ФС Форма Адреса на карточках клиента")
    @allure.tag("can_auth", "success")
    def test_remove_second_address(self, base_url: str, create_user: int):
        user_id = create_user
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{user_id}/overview")
        self.client_profile_page.click_client_tab()
        self.client_profile_page.locators.ADDRESSES_TAB.click()
        delay(1, reason="Без ожидания пустой список адресов")
        self.client_profile_page.locators.ADD_BTN.click()
        self.client_profile_page.add_address_form.TITLE.to_contain_text("Добавление адреса")
        self.client_profile_page.add_address_form.ADDRESS_TYPE_FIELD.select_by_value("Фактический адрес")
        self.client_profile_page.add_address_form.ADDRESS_INPUT.fill(BasicSystemAddress.add_address_name)
        self.client_profile_page.add_address_form.ADDRESS_OPTION.wait_elements_visible(0)
        self.client_profile_page.add_address_form.ADDRESS_OPTION[0]. \
            to_contain_text(text=BasicSystemAddress.add_address_name)
        self.client_profile_page.add_address_form.ADDRESS_OPTION[0].click()
        self.client_profile_page.add_address_form.SAVE_BTN.to_be_enabled()
        self.client_profile_page.add_address_form.SAVE_BTN.click()
        self.client_profile_page.locators.TABLE_ADDRESSES.wait_to_have_count(2)

        self.client_profile_page.locators.TABLE_ADDRESS_TYPES[1].click()
        self.client_profile_page.locators.DELETE_ADDRESS.click()

        self.client_profile_page.base_elements.MODAL.wait_to_have_count(1)
        self.client_profile_page.base_elements.MODAL_TITLE[0].to_contain_text("Удаление адреса")
        (self.client_profile_page.base_elements.MODAL_TITLE[0].
         to_contain_text(f'Вы действительно хотите удалить \n           '
                         f'"Фактический адрес: ул Уральская, Россия, Санкт-Петербург г, ул Уральская г."?'))
        self.client_profile_page.base_elements.FIRST_BTN.to_contain_text("Отмена")
        self.client_profile_page.base_elements.SECOND_BTN.to_contain_text("Удалить")
        self.client_profile_page.base_elements.SECOND_BTN.click()

        self.client_profile_page.locators.TABLE_ADDRESS_TYPES[0].to_contain_text(text="Адрес регистрации")
        self.client_profile_page.locators.TABLE_ADDRESSES.wait_to_have_count(1)

    @allure.title("Удаление адреса. Выбран тип Адрес регистрации клиента")
    @allure.id(525410)
    @allure.description("Получение ошибки при удалении адреса с типом Адрес регистрации")
    @allure.link(url="jira.nexign.com/browse/TUDS-1144", name="TUDS-1144")
    @allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=585630877",
                 name="ФС Форма Адреса на карточках клиента")
    @allure.tag("can_auth", "success")
    def test_remove_address_choose_main_address(self, base_url: str, create_user: int):
        user_id = create_user
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{user_id}/overview")
        self.client_profile_page.click_client_tab()
        self.client_profile_page.locators.ADDRESSES_TAB.click()
        self.client_profile_page.locators.TABLE_ADDRESSES.wait_to_have_count(1)

        self.client_profile_page.locators.TABLE_ADDRESS_TYPES[0].click()
        self.client_profile_page.locators.DELETE_ADDRESS.click()

        self.client_profile_page.base_elements.MODAL[0].wait_to_be_visible()
        self.client_profile_page.base_elements.MODAL_TITLE[0].to_contain_text("Удаление адреса")
        (self.client_profile_page.base_elements.MODAL_TITLE[0].
         to_contain_text(f'Вы действительно хотите удалить \n           '
                         f'"Адрес регистрации: ул Уральская, Россия, Санкт-Петербург г, ул Уральская г."?'))
        self.client_profile_page.base_elements.FIRST_BTN.to_contain_text("Отмена")
        self.client_profile_page.base_elements.SECOND_BTN.to_contain_text("Удалить")
        self.client_profile_page.base_elements.SECOND_BTN.click()

        self.client_profile_page.base_elements.MODAL.wait_to_have_count(2)
        self.client_profile_page.base_elements.MODAL_TITLE[1].wait_to_have_text("Ошибка")
        (self.client_profile_page.base_elements.MODAL_BODY_TEXT[1].
         to_contain_text("Удаление адреса недоступно, так как для объекта иерархии добавлено минимально допустимое"
                         " количество адресов выбранного типа"))
        self.client_profile_page.base_elements.MODAL_CLOSE_BTN.to_contain_text("Закрыть")
        self.client_profile_page.base_elements.MODAL_CLOSE_BTN.click()
        self.client_profile_page.base_elements.MODAL_CLOSE_BTN.not_to_be_visible()

        self.client_profile_page.locators.TABLE_ADDRESS_TYPES[0].to_contain_text(text="Адрес регистрации")
        self.client_profile_page.locators.TABLE_ADDRESSES.wait_to_have_count(1)

    @allure.title("Удаление адреса. Отмена удаления")
    @allure.id(526073)
    @allure.description("При подтверждения операции удаления адреса пользователь отменил операцию")
    @allure.link(url="jira.nexign.com/browse/TUDS-1144", name="TUDS-1144")
    @allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=585630877",
                 name="ФС Форма Адреса на карточках клиента")
    @allure.tag("can_auth", "success")
    def test_reject_remove_address(self, base_url: str, create_user: int):
        user_id = create_user
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{user_id}/overview")
        self.client_profile_page.click_client_tab()
        self.client_profile_page.locators.ADDRESSES_TAB.click()
        delay(1, reason="Без ожидания пустой список адресов")
        self.client_profile_page.locators.ADD_BTN.click()
        self.client_profile_page.add_address_form.TITLE.to_contain_text("Добавление адреса")
        self.client_profile_page.add_address_form.ADDRESS_TYPE_FIELD.select_by_value("Фактический адрес")
        self.client_profile_page.add_address_form.ADDRESS_INPUT.fill(BasicSystemAddress.add_address_name)
        self.client_profile_page.add_address_form.ADDRESS_OPTION.wait_elements_visible(0)
        self.client_profile_page.add_address_form.ADDRESS_OPTION[0]. \
            to_contain_text(text=BasicSystemAddress.add_address_name)
        self.client_profile_page.add_address_form.ADDRESS_OPTION[0].click()
        self.client_profile_page.add_address_form.SAVE_BTN.to_be_enabled()
        self.client_profile_page.add_address_form.SAVE_BTN.click()
        self.client_profile_page.locators.TABLE_ADDRESSES.wait_to_have_count(2)

        self.client_profile_page.locators.TABLE_ADDRESS_TYPES[1].click()
        self.client_profile_page.locators.DELETE_ADDRESS.click()

        self.client_profile_page.base_elements.MODAL.wait_to_have_count(1)
        self.client_profile_page.base_elements.MODAL_TITLE[0].to_contain_text("Удаление адреса")
        (self.client_profile_page.base_elements.MODAL_TITLE[0].
         to_contain_text(f'Вы действительно хотите удалить \n           '
                         f'"Фактический адрес: ул Уральская, Россия, Санкт-Петербург г, ул Уральская г."?'))
        self.client_profile_page.base_elements.FIRST_BTN.to_contain_text("Отмена")
        self.client_profile_page.base_elements.SECOND_BTN.to_contain_text("Удалить")
        self.client_profile_page.base_elements.FIRST_BTN.click()

        self.client_profile_page.locators.TABLE_ADDRESS_TYPES[1].to_contain_text(text="Фактический адрес")
        self.client_profile_page.locators.TABLE_ADDRESSES.wait_to_have_count(2)
