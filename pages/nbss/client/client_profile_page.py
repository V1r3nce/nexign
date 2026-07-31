import re

import allure

from common.enums.ats import AtsOperations
from common.helpers.checker import assert_that, check_that
from common.helpers.data_generator import calc_price_after_discount
from common.helpers.env_helper import BASE_URL
from common.helpers.string_helper import check_price, get_price_and_currency
from common.helpers.time_helpers import delay
from models.client import EntrepreneurClient, IndividualClient, OrganizationClient
from models.context import test_context
from pages.base_page import BasePage
from pages.locators.nbss.client.client_profile import (
    ClientProfileAttributes,
    ClientProfileElements,
    ClientRelatedPersons,
    PersonalAccountForm,
)
from pages.locators.nbss.client.client_search import ClientSearchElements
from pages.locators.nbss.dynamic_form_elements import (
    AddAddress,
    AddressCreate,
    AddressForm,
    CreateSalesAndServiceManagement,
    EditAddress,
    EditAddressInfo,
    ReplaceResource,
)
from pages.locators.nbss.home_page_elements import HomePageElements
from pages.locators.nbss.inquiries_elements import InquiriesElements


class ClientProfilePage(BasePage):
    def __init__(self) -> None:
        super().__init__()

        self.locators = ClientProfileElements()
        self.address_form = AddressForm()
        self.add_address_form = AddAddress()
        self.edit_address_form = EditAddress()
        self.edit_address_info = EditAddressInfo()
        self.create_address_form = AddressCreate()
        self.client_attributes = ClientProfileAttributes()
        self.client_related_persons = ClientRelatedPersons()
        self.personal_account = PersonalAccountForm()
        self.home_page = HomePageElements()
        self.client_search_page = ClientSearchElements()
        self.create_request_form = CreateSalesAndServiceManagement()
        self.replace_resource_form = ReplaceResource()
        self.inquiries_form = InquiriesElements()

    @allure.step("Открыть карточку клиента")
    def open_client_profile_page(self, client_id: int) -> None:
        self.open(f"{BASE_URL}customer-hierarchy-management/customers/{client_id}/customer")
        self.locators.CLIENT_FIO.wait_to_be_visible(timeout=15000)

    @allure.step("Проверка данных клиента")
    def check_client_data(self, client: IndividualClient | OrganizationClient | EntrepreneurClient) -> None:
        self.locators.CLIENT_TYPE.to_contain_text(client.type)
        self.locators.CLIENT_FIO.to_contain_text(client.customer_name)
        self.locators.RESIDENT.wait_to_have_text(client.is_resident)
        self.locators.SPEAKING_LANGUAGE.to_contain_text(client.speaking_language)
        self.locators.NATIONALITY.to_contain_text(client.nationality)
        self.locators.NOTE.to_contain_text(client.note)
        self.locators.REGISTRATION_DOCUMENT.to_contain_text(client.ogrn)
        self.locators.REGISTRATION_DATE.to_contain_text(client.registration_date)
        self.locators.REGISTRATION_NUM.to_contain_text(client.registration_num)
        self.locators.TAX_SCHEME.to_contain_text(client.tax_scheme)

    @allure.step("Открыть карточку клиента и проверить данные")
    def open_client_data_and_check(self, client: IndividualClient | OrganizationClient | EntrepreneurClient) -> None:
        self.locators.CLIENT_TAB.wait_to_be_visible()
        self.locators.CLIENT_TAB.click()
        self.check_client_data(client=client)

    @allure.step("Проверка контактов связанного лица клиента")
    def check_linked_person_contacts(
        self, client: IndividualClient | OrganizationClient | EntrepreneurClient, check_email: bool = False
    ) -> None:
        self.locators.RELATED_MOBILE_PHONE.to_contain_text(client.contact_phone, separated=True)
        if check_email:
            self.locators.RELATED_EMAIL.to_contain_text(client.contact_email)

    @allure.step("Открытие страницы Персональных данных/Карточка клиента")
    def open_client_overview_page(self, client_id: int) -> None:
        self.open(f"{BASE_URL}customer-hierarchy-management/customers/{client_id}/overview")
        self.locators.OVERVIEW_TAB.wait_to_be_visible(timeout=15000)

    @allure.step("Открытие страницы связанных лиц клиента")
    def open_linked_person_page(self, client_id: int) -> None:
        self.open(f"{BASE_URL}customer-hierarchy-management/customers/{client_id}/linked-persons")
        self.locators.ADD_RELATED_PERSON_BTN.wait_to_be_visible(timeout=15000)

    @allure.step("Редактирование контактов связанного лица")
    def edit_linked_person_contacts(
        self, phone_code: str | None = None, phone_number: str | None = None, contact_email: str | None = None
    ) -> None:
        self.locators.CONTACT_DATA_EDIT_BTN.click()
        if phone_code is not None:
            self.locators.CONTACT_PHONE_CODE.fill(phone_code)
        if phone_number is not None:
            if self.locators.CONTACT_PHONE_CLEAR.is_visible():
                self.locators.CONTACT_PHONE_CLEAR.click()
                self.locators.CONTACT_PHONE.wait_to_have_text("")
                delay(1, "Ожидание очистки поля")
            self.locators.CONTACT_PHONE.fill(phone_number)
        delay(2, "Чтобы UI форма успела подхватить изменения")
        self.locators.ACCEPT_BTN.wait_to_be_enabled()
        self.locators.ACCEPT_BTN.click()
        delay(2, "Запрос успел отправиться")

    @allure.step("Проверить, что баланс {index} ЛС равен {money} {currency}")
    def check_balance(self, index: int, money: float = 0.00, currency: str = "RUB") -> None:
        balance = f"{money:,.2f} {currency}".replace(",", " ")
        for i in range(10):
            self.locators.PERSONAL_ACCOUNT_LOADER.not_to_be_visible()
            self.locators.BALANCE.wait_elements_visible(index)
            if self.locators.BALANCE[index].text == balance:
                break
            delay(1, "Ожидание изменения баланса")
            self.locators.PERSONAL_ACCOUNT_UPDATE_BTN.click()
        self.locators.BALANCE[index].wait_to_have_text(balance)

    @allure.step("Добавить адрес")
    def add_address(
        self,
        address_type: str = None,
        address: str = None,
        select_address: str = None,
        latitude: str = None,
        longitude: str = None,
        map_link: str = None,
    ) -> None:
        self.locators.ADD_BTN.wait_to_be_visible()
        self.locators.ADD_BTN.click()

        self.fill_address_fields(address_type, address, select_address, latitude, longitude, map_link)

        self.address_form.SAVE_BTN.to_be_enabled()
        self.address_form.SAVE_BTN.click()
        self.address_form.CANCEL_BTN.not_to_be_visible()

    @allure.step("Открыть форму добавления адреса и перейти к созданию адреса в справочнике")
    def open_add_address_form(self) -> None:
        self.locators.ADD_BTN.wait_to_be_visible()
        self.locators.ADD_BTN.click()
        self.add_address_form.TITLE.to_contain_text("Добавление адреса")
        self.add_address_form.ADDRESS_INPUT.click()
        self.add_address_form.ADD_ADDRESS_TO_CATALOG.to_contain_text("Добавить адрес в справочник")
        self.add_address_form.ADD_ADDRESS_TO_CATALOG.click()

    @allure.step("Создать новый адрес в справочнике")
    def create_new_address(
        self,
        country: str,
        region: str,
        city: str,
        street: str,
        building_number: int,
        flat_number: int,
        address_object_exists: bool = False,
    ) -> None:
        """
        Заполняет форму 'Создание нового адреса' и создаёт адрес в справочнике.

        :param address_object_exists: True — адресные объекты выбираются из справочника,
                                      False — создаются новые адресные объекты.
        """
        self.create_address_form.TITLE.to_contain_text("Создание нового адреса")
        self.fill_country_attribute(country, address_object_exists)
        self.fill_region_attribute(region, address_object_exists)
        self.fill_city_attribute(city, address_object_exists)
        self.fill_street_attribute(street, address_object_exists)
        self.fill_building_number_attribute(building_number)
        self.fill_flat_number_attribute(flat_number)
        self.create_address_form.ADD_ADDRESS_OBJECT_BTN.not_to_be_visible()
        self.create_address_form.CREATE_BTN.click()
        self.create_address_form.TITLE.not_to_be_visible(timeout=15000)

    @allure.step("Отредактировать адрес")
    def edit_address(
        self,
        address_type: str = None,
        address: str = None,
        select_address: str = None,
        latitude: str = None,
        longitude: str = None,
        map_link: str = None,
    ) -> None:
        self.locators.EDIT_BTN.wait_to_be_visible()
        self.locators.EDIT_BTN.click()

        self.fill_address_fields(address_type, address, select_address, latitude, longitude, map_link)

        self.address_form.SAVE_BTN.to_be_enabled()
        self.address_form.SAVE_BTN.click()
        self.address_form.CANCEL_BTN.not_to_be_visible()

    @allure.step("Добавить адрес связанному лицу")
    def add_linked_person_address(
        self,
        address_type: str = None,
        address: str = None,
        select_address: str = None,
        latitude: str = None,
        longitude: str = None,
        map_link: str = None,
    ) -> None:
        self.edit_address_info.ADD_BUTTON.wait_to_be_visible()
        self.edit_address_info.ADD_BUTTON.click()

        self.fill_address_fields(address_type, address, select_address, latitude, longitude, map_link)

        self.address_form.SAVE_BTN.to_be_enabled()
        self.address_form.SAVE_BTN.click()
        self.address_form.CANCEL_BTN.not_to_be_visible()

    @allure.step("Отредактировать адрес связанному лицу")
    def edit_linked_person_address(
        self,
        address_type: str = None,
        address: str = None,
        select_address: str = None,
        latitude: str = None,
        longitude: str = None,
        map_link: str = None,
    ) -> None:
        self.edit_address_info.EDIT_ADDRESS.wait_to_be_visible()
        self.edit_address_info.EDIT_ADDRESS.click()

        self.fill_address_fields(address_type, address, select_address, latitude, longitude, map_link)

        self.address_form.SAVE_BTN.to_be_enabled()
        self.address_form.SAVE_BTN.click()
        self.address_form.CANCEL_BTN.not_to_be_visible()

    @allure.step("Заполнить поля на форме Добавление/Редактирование адреса")
    def fill_address_fields(
        self,
        address_type: str = None,
        address: str = None,
        select_address: str = None,
        latitude: str = None,
        longitude: str = None,
        map_link: str = None,
    ) -> None:
        self.address_form.TITLE.wait_to_have_text(
            re.compile("(Добавление адреса|Редактирование адреса|Редактирование адресной информации)")
        )

        if address_type:
            self.address_form.ADDRESS_TYPE_FIELD.select_by_value(address_type)
        if address:
            self.address_form.ADDRESS_INPUT.fill(address)
            self.address_form.ADDRESS_OPTION.wait_elements_visible(0)
            if select_address:
                self.address_form.ADDRESS_OPTION[0].to_contain_text(select_address)
            else:
                self.address_form.ADDRESS_OPTION[0].to_contain_text(address)
            self.address_form.ADDRESS_OPTION[0].click()
        if latitude:
            self.address_form.LATITUDE_INPUT.fill(latitude)
        if longitude:
            self.address_form.LONGITUDE_INPUT.fill(longitude)
        if map_link:
            self.address_form.MAPS_LINK_INPUT.fill(map_link)

    def fill_country_attribute(self, country: str, address_object_exists: bool = True) -> None:
        self.create_address_form.OBJECT_TYPE.select_by_value("Страна")
        if address_object_exists:
            self.create_address_form.OBJECT_NAME_AUTOCOMPLETE.select_by_value(value=country)
        elif not address_object_exists:
            self.create_address_form.OBJECT_NAME_AUTOCOMPLETE.type_and_press_enter(country)
        self.create_address_form.ADD_ADDRESS_OBJECT_BTN.not_to_be_enabled()
        self.create_address_form.APPLY_BTN.click()

    def fill_region_attribute(self, region: str, address_object_exists: bool = True) -> None:
        self.create_address_form.ADD_ADDRESS_OBJECT_BTN.click()
        self.create_address_form.OBJECT_TYPE.select_by_value("Регион")
        if address_object_exists:
            self.create_address_form.OBJECT_NAME_AUTOCOMPLETE.select_address_by_value(
                input_value=region.split(" обл.")[0], select_value=region, field_value=region.split(" обл.")[0]
            )
        elif not address_object_exists:
            self.create_address_form.OBJECT_NAME_AUTOCOMPLETE.type_and_press_enter(region)
            self.create_address_form.REGION_TYPE_DROPDOWN.select_by_value("Область")
        self.create_address_form.APPLY_BTN.click()

    def fill_city_attribute(self, city: str, address_object_exists: bool = True) -> None:
        self.create_address_form.ADD_ADDRESS_OBJECT_BTN.click()
        self.create_address_form.OBJECT_TYPE.select_by_value("Город")
        if address_object_exists:
            self.create_address_form.OBJECT_NAME_AUTOCOMPLETE.select_address_by_value(
                input_value=city.split("г. ")[1], select_value=city, field_value=city.split("г. ")[1]
            )
        elif not address_object_exists:
            self.create_address_form.OBJECT_NAME_AUTOCOMPLETE.type_and_press_enter(city)
            self.create_address_form.CITY_TYPE_DROPDOWN.select_by_value("Город")
        self.create_address_form.APPLY_BTN.click()

    def fill_street_attribute(self, street: str, address_object_exists: bool = True) -> None:
        self.create_address_form.ADD_ADDRESS_OBJECT_BTN.click()
        self.create_address_form.OBJECT_TYPE.select_by_value("Улица")
        if address_object_exists:
            self.create_address_form.OBJECT_NAME_AUTOCOMPLETE.select_address_by_value(
                input_value=re.sub(r"(ул|ш). ", "", street),
                select_value=street,
                field_value=re.sub(r"(ул|ш). ", "", street),
            )
        elif not address_object_exists:
            self.create_address_form.OBJECT_NAME_AUTOCOMPLETE.type_and_press_enter(street)
            self.create_address_form.STREET_TYPE_DROPDOWN.select_by_value("Улица")
        self.create_address_form.APPLY_BTN.click()

    def fill_building_number_attribute(self, building_number: int) -> None:
        self.create_address_form.ADD_ADDRESS_OBJECT_BTN.click()
        self.create_address_form.OBJECT_TYPE.select_by_value("Дом")
        self.create_address_form.HOUSE_TYPE_DROPDOWN.select_by_value("Дом")
        self.create_address_form.OBJECT_NUM.fill(str(building_number))
        self.create_address_form.APPLY_BTN.click()

    def fill_flat_number_attribute(self, flat_number: int) -> None:
        self.create_address_form.ADD_ADDRESS_OBJECT_BTN.click()
        self.create_address_form.OBJECT_TYPE.select_by_value("Квартира")
        self.create_address_form.APARTMENT_TYPE_DROPDOWN.select_by_value("Квартира")
        self.create_address_form.OBJECT_NUM.fill(str(flat_number))
        self.create_address_form.APPLY_BTN.click()

    @allure.step("Заполнить форму создания нового адреса для Клиента")
    def fill_client_new_address(
        self,
        country: str,
        region: str,
        city: str,
        street: str,
        building_number: int,
        flat_number: int,
    ) -> None:
        self.create_address_form.TITLE.to_contain_text("Создание нового адреса")
        self.fill_country_attribute(country)

        self.create_address_form.ADDED_CARD[0].wait_to_be_visible()
        self.create_address_form.ATTRIBUTE_HEADER[0].to_contain_text(text="Атрибуты")
        self.create_address_form.ADDED_CARD_EDIT_BTN[0].wait_to_be_visible()
        self.create_address_form.ADDED_CARD_DELETE_BTN[0].wait_to_be_visible()
        self.create_address_form.ADD_ADDRESS_OBJECT_BTN.to_be_enabled()

        self.fill_region_attribute(region)
        self.fill_city_attribute(city)
        self.fill_street_attribute(street)
        self.fill_building_number_attribute(building_number)
        self.fill_flat_number_attribute(flat_number)

    @allure.step("Выбрать тип адреса с названием '{name}'")
    def choose_address_type_with_name(self, name: str) -> None:
        for item in self.locators.TYPE_FILTER_OPTIONS:
            if item.text == name:
                item.click()
                break

    @allure.step("Заполнить полностью форму создания нового адреса для Клиента и проверить атрибуты")
    def fill_all_fields_client_new_address(
        self,
        country: str,
        region: str,
        city: str,
        street: str,
        building_number: int,
        flat_number: int,
        gar: str,
        block: str,
        building: str,
        address_index: str,
    ) -> None:
        self.create_address_form.TITLE.to_contain_text("Создание нового адреса")
        self.create_address_form.OBJECT_TYPE.select_by_value("Страна")
        self.create_address_form.OBJECT_NAME_AUTOCOMPLETE.select_by_value(country)
        self.create_address_form.ADD_ADDRESS_OBJECT_BTN.not_to_be_enabled()
        self.create_address_form.APPLY_BTN.click()

        self.create_address_form.ADDED_CARD[0].wait_to_be_visible()
        self.create_address_form.ATTRIBUTE_HEADER[0].to_contain_text(text="Атрибуты")
        self.create_address_form.ADDED_CARD_EDIT_BTN[0].wait_to_be_visible()
        self.create_address_form.ADDED_CARD_DELETE_BTN[0].wait_to_be_visible()
        self.create_address_form.ATTRIBUTE_HEADER[0].click()
        self.create_address_form.ATTRIBUTE_FIELDS[0].to_have_value(country)
        self.create_address_form.ADD_ADDRESS_OBJECT_BTN.to_be_enabled()

        self.create_address_form.ADD_ADDRESS_OBJECT_BTN.click()
        self.create_address_form.OBJECT_TYPE.select_by_value("Регион")
        self.create_address_form.OBJECT_NAME_AUTOCOMPLETE.select_address_by_value(
            input_value=region.split(" обл.")[0], select_value=region, field_value=region.split(" обл.")[0]
        )
        self.create_address_form.OBJECT_GAR[-1].fill(gar)
        self.create_address_form.APPLY_BTN.click()
        self.create_address_form.ATTRIBUTE_HEADER[-1].click()
        self.create_address_form.ATTRIBUTE_FIELDS[-3].to_have_value(region.split(" обл.")[0], 10000)
        self.create_address_form.ATTRIBUTE_FIELDS[-1].to_have_value(gar)

        self.create_address_form.ADD_ADDRESS_OBJECT_BTN.click()
        self.create_address_form.OBJECT_TYPE.select_by_value("Город")
        self.create_address_form.OBJECT_NAME_AUTOCOMPLETE.select_address_by_value(
            input_value=city.split("г. ")[1], select_value=city, field_value=city.split("г. ")[1]
        )
        self.create_address_form.OBJECT_GAR[-1].fill(gar)
        self.create_address_form.APPLY_BTN.click()
        self.create_address_form.ATTRIBUTE_HEADER[-1].click()
        self.create_address_form.ATTRIBUTE_FIELDS[-3].to_have_value(city.split("г. ")[1], 10000)
        self.create_address_form.ATTRIBUTE_FIELDS[-1].to_have_value(gar)

        self.create_address_form.ADD_ADDRESS_OBJECT_BTN.click()
        self.create_address_form.OBJECT_TYPE.select_by_value("Улица")
        self.create_address_form.OBJECT_NAME_AUTOCOMPLETE.select_address_by_value(
            input_value=re.sub(r"(ул|ш). ", "", street), select_value=street, field_value=re.sub(r"(ул|ш). ", "", street)
        )
        self.create_address_form.OBJECT_GAR[-1].fill(gar)
        self.create_address_form.APPLY_BTN.click()
        self.create_address_form.ATTRIBUTE_HEADER[-1].click()
        self.create_address_form.ATTRIBUTE_FIELDS[-3].to_have_value(re.sub(r"(ул|ш). ", "", street), 10000)
        self.create_address_form.ATTRIBUTE_FIELDS[-1].to_have_value(gar)

        self.create_address_form.ADD_ADDRESS_OBJECT_BTN.click()
        self.create_address_form.OBJECT_TYPE.select_by_value("Дом")
        self.create_address_form.HOUSE_TYPE_DROPDOWN.select_by_value("Дом")
        self.create_address_form.ADDITIONAL_HOUSE_TYPE_DROPDOWN.select_by_value("Корпус")
        self.create_address_form.EXTRA_HOUSE_TYPE_DROPDOWN.select_by_value("Корпус")
        self.create_address_form.OBJECT_NUM.fill(str(building_number))
        self.create_address_form.OBJECT_ADDITIONAL_NUM.fill(block)
        self.create_address_form.OBJECT_EXTRA_NUM.fill(building)
        self.create_address_form.OBJECT_MAIL_INDEX.fill(address_index)
        self.create_address_form.OBJECT_GAR[-1].fill(gar)
        self.create_address_form.APPLY_BTN.click()
        self.create_address_form.ATTRIBUTE_HEADER[-1].click()
        self.create_address_form.ATTRIBUTE_FIELDS_BLOCK[-8].wait_to_have_text("Дом")
        self.create_address_form.ATTRIBUTE_FIELDS[-7].to_have_value(str(building_number))
        self.create_address_form.ATTRIBUTE_FIELDS_BLOCK[-6].to_contain_text("Корпус")
        self.create_address_form.ATTRIBUTE_FIELDS[-5].to_have_value(block)
        self.create_address_form.ATTRIBUTE_FIELDS_BLOCK[-4].to_contain_text("Корпус")
        self.create_address_form.ATTRIBUTE_FIELDS[-3].to_have_value(building)
        self.create_address_form.ATTRIBUTE_FIELDS[-2].to_have_value(address_index)
        self.create_address_form.ATTRIBUTE_FIELDS[-1].to_have_value(gar)

        self.create_address_form.ADD_ADDRESS_OBJECT_BTN.click()
        self.create_address_form.OBJECT_TYPE.select_by_value("Квартира")
        self.create_address_form.APARTMENT_TYPE_DROPDOWN.select_by_value("Квартира")
        self.create_address_form.OBJECT_NUM.fill(str(flat_number))
        self.create_address_form.APPLY_BTN.click()
        self.create_address_form.ATTRIBUTE_HEADER[-1].click()
        self.create_address_form.ATTRIBUTE_FIELDS_BLOCK[-2].wait_to_have_text("Квартира")
        self.create_address_form.ATTRIBUTE_FIELDS[-3].to_have_value(str(flat_number))

    @allure.step("Заполнить обязательные поля формы создания нового адреса для Клиента и проверить атрибуты")
    def fill_required_fields_client_new_address(
        self,
        country: str,
        region: str,
        city: str,
        street: str,
        building_number: int,
        flat_number: int,
    ) -> None:
        self.create_address_form.TITLE.to_contain_text("Создание нового адреса")
        self.fill_country_attribute(country)

        self.create_address_form.ADDED_CARD[0].wait_to_be_visible()
        self.create_address_form.ATTRIBUTE_HEADER[0].to_contain_text(text="Атрибуты")
        self.create_address_form.ADDED_CARD_EDIT_BTN[0].wait_to_be_visible()
        self.create_address_form.ADDED_CARD_DELETE_BTN[0].wait_to_be_visible()
        self.create_address_form.ATTRIBUTE_HEADER[0].click()
        self.create_address_form.ATTRIBUTE_FIELDS[0].to_have_value(country)
        self.create_address_form.ADD_ADDRESS_OBJECT_BTN.to_be_enabled()

        self.fill_region_attribute(region)
        self.create_address_form.ATTRIBUTE_HEADER[-1].click()
        self.create_address_form.ATTRIBUTE_FIELDS[-3].to_have_value(region.split(" обл.")[0], 10000)

        self.fill_city_attribute(city)
        self.create_address_form.ATTRIBUTE_HEADER[-1].click()
        self.create_address_form.ATTRIBUTE_FIELDS[-3].to_have_value(city.split("г. ")[1], 10000)

        self.fill_street_attribute(street)
        self.create_address_form.ATTRIBUTE_HEADER[-1].click()
        self.create_address_form.ATTRIBUTE_FIELDS[-3].to_have_value(re.sub(r"(ул|ш). ", "", street), 10000)

        self.fill_building_number_attribute(building_number)
        self.create_address_form.ATTRIBUTE_HEADER[-1].click()
        self.create_address_form.ATTRIBUTE_FIELDS_BLOCK[-8].wait_to_have_text("Дом")
        self.create_address_form.ATTRIBUTE_FIELDS[-7].to_have_value(str(building_number))

        self.fill_flat_number_attribute(flat_number)
        self.create_address_form.ATTRIBUTE_HEADER[-1].click()
        self.create_address_form.ATTRIBUTE_FIELDS_BLOCK[-2].wait_to_have_text("Квартира")
        self.create_address_form.ATTRIBUTE_FIELDS[-3].to_have_value(str(flat_number))

    def edit_attribute_and_check_value_for_field_with_index(
        self,
        field_index: int,
        input_value: str,
        select_value: str = "",
        field_value: str = "",
        value_type: str = "name",
    ) -> None:
        """Отредактировать атрибут адреса и проверить после редактирования значение для поля с индексом field_index
        (у проверяемого поля может быть разный индекс)"""
        self.create_address_form.ADDED_CARD_EDIT_BTN[-1].click()
        if value_type == "name":
            self.create_address_form.OBJECT_NAME_AUTOCOMPLETE.select_address_by_value(
                input_value, select_value, field_value
            )
            self.create_address_form.APPLY_BTN.click()

            self.create_address_form.ATTRIBUTE_HEADER[-1].click()
            self.create_address_form.ATTRIBUTE_FIELDS[field_index].to_have_value(field_value)
        elif value_type == "num":
            self.create_address_form.OBJECT_NUM.fill(input_value)
            self.create_address_form.APPLY_BTN.click()

            self.create_address_form.ATTRIBUTE_HEADER[-1].click()
            self.create_address_form.ATTRIBUTE_FIELDS[field_index].to_have_value(input_value)

    @allure.step("Заполнить обязательные поля формы создания нового адреса для Клиента и проверить атрибуты")
    def fill_and_update_address_data(
        self,
        country: str,
        new_country: str,
        region: str,
        new_region: str,
        city: str,
        new_city: str,
        street: str,
        building_number: int,
        flat_number: int,
    ) -> None:
        self.create_address_form.TITLE.to_contain_text("Создание нового адреса")

        self.fill_country_attribute(country, address_object_exists=False)
        self.edit_attribute_and_check_value_for_field_with_index(
            field_index=0, input_value=new_country, select_value=new_country, field_value=new_country
        )

        self.fill_region_attribute(region)
        self.edit_attribute_and_check_value_for_field_with_index(
            field_index=-3,
            input_value=new_region.split(" ")[0],
            select_value=new_region,
            field_value=new_region.split(" ")[0],
        )

        self.fill_city_attribute(city, address_object_exists=False)
        self.edit_attribute_and_check_value_for_field_with_index(
            field_index=-3, input_value=new_city.split(" ")[1], select_value=new_city, field_value=new_city.split(" ")[1]
        )

        self.fill_street_attribute(f"{street}тест", address_object_exists=False)
        self.edit_attribute_and_check_value_for_field_with_index(
            field_index=-3, input_value=street.split(" ")[1], select_value=street, field_value=street.split(" ")[1]
        )

        self.fill_building_number_attribute(building_number)
        self.edit_attribute_and_check_value_for_field_with_index(
            field_index=-7, input_value=str(building_number * 2), value_type="num"
        )

        self.fill_flat_number_attribute(flat_number)
        self.edit_attribute_and_check_value_for_field_with_index(
            field_index=-3, input_value=str(flat_number * 2), value_type="num"
        )

    @allure.step("Дождаться, когда {index} заявка перейдёт в статус {status}")
    def wait_request_status(self, index: int, status: str, count_retry: int = 10, wait_time: float = 3) -> None:
        for i in range(count_retry):
            self.locators.REQUEST_STATUS.wait_elements_visible(index)
            if self.locators.REQUEST_STATUS[index].text == status:
                break
            delay(wait_time, "Ожидание изменения статуса заявки")
            self.locators.UPDATE_REQUESTS_BTN.click()
        self.locators.REQUEST_STATUS[index].wait_to_have_text(status)

    @allure.step("Проверить форму связанных лиц")
    def check_related_person(self, user_data: IndividualClient, masked: bool = False, end_user: bool = False) -> None:
        self.locators.RELATED_PERSON_TABLE_NAME.wait_to_be_visible(timeout=10000)
        self.locators.RELATED_PERSON_TABLE_NAME.to_contain_text(
            f"{user_data.sur_name} {user_data.first_name} {user_data.patronymic}"
        )
        self.locators.RELATED_PERSON_GENDER.to_contain_text(user_data.gender)
        self.locators.RELATED_PERSON_TYPE_OF_DOCUMENT.to_contain_text(user_data.document_type)
        self.locators.RELATED_PERSON_DOCUMENT_NUMBER.to_contain_text(
            f"{user_data.document_serial} {user_data.document_num}" if not masked else "*** ***"
        )
        self.locators.RELATED_PERSON_DOCUMENT_PROVIDE_BY.to_contain_text(
            user_data.document_provide_by if not masked else "***"
        )
        self.locators.RELATED_PERSON_SUBDIVISION_CODE.to_contain_text(
            user_data.document_division_code if not masked else "***"
        )
        self.locators.RELATED_PERSON_DATE_OF_ISSUE.to_contain_text(user_data.issue_date if not masked else "01.01.1100")
        self.locators.RELATED_PERSON_VALID_FOR.to_contain_text(
            user_data.document_valid_date if not masked else "01.01.1100"
        )
        self.locators.RELATED_PERSON_BIRTH_PLACE.to_contain_text(user_data.birth_place if not masked else "***")
        self.locators.RELATED_PERSON_BIRTH_DATE.to_contain_text(user_data.birth_date if not masked else "01.01.1100")
        self.locators.RELATED_PERSON_COUNTRY.to_contain_text(user_data.nationality)
        self.locators.RELATED_SPEAKING_LANGUAGE.to_contain_text(user_data.speaking_language)
        self.locators.RELATED_PERSON_IS_PUBLIC.to_contain_text(user_data.is_public)
        self.locators.RELATED_PERSON_IS_RESIDENT.to_contain_text(user_data.is_resident)

        if not end_user:
            self.locators.RELATED_PERSON_INN.to_contain_text(user_data.inn if not masked else "***")

    @allure.step("Проверить информацию о заявке")
    def check_request(
        self,
        request_index: int = 0,
        number: int | None = None,
        request_type: str | None = None,
        status: str | None = None,
        step: str | None = None,
        responsible: str | None = None,
        created_date: str | None = None,
    ) -> None:
        self.locators.REQUESTS.wait_elements_visible(request_index)
        if number:
            self.locators.REQUEST_NUMBER[request_index].wait_to_have_text(number)
        if request_type:
            self.locators.REQUEST_TYPE[request_index].wait_to_have_text(request_type)
        if status:
            self.locators.REQUEST_STATUS[request_index].wait_to_have_text(status)
        if step:
            self.locators.REQUEST_STEP[request_index].wait_to_have_text(step)
        if responsible:
            self.locators.REQUEST_RESPONSIBLE[request_index].wait_to_have_text(responsible)
        if created_date:
            self.locators.REQUEST_CREATE_DATE[request_index].wait_to_have_text(created_date)

    @allure.step("Проверить форму конечного пользователя")
    def check_personal_data_form(
        self, user_data: IndividualClient | OrganizationClient = None, masked: bool = False
    ) -> None:
        user_data = user_data or test_context.client
        if isinstance(user_data, IndividualClient):
            self.locators.FIO.to_contain_text(f"{user_data.sur_name} {user_data.first_name} {user_data.patronymic}")
            self.locators.GENDER.to_contain_text(user_data.gender)
            self.locators.DOCUMENT_TYPE.to_contain_text(user_data.document_type)
            self.locators.DOCUMENT_SERIAL_AND_NUM.to_contain_text(
                f"{user_data.document_serial} {user_data.document_num}" if not masked else "*** ***"
            )
            self.locators.DOCUMENT_PROVIDE_BY.to_contain_text(user_data.document_provide_by if not masked else "***")
            self.locators.DOCUMENT_DIVISION_CODE.to_contain_text(
                user_data.document_division_code if not masked else "***"
            )
            self.locators.DOCUMENT_VALID_DATE.to_contain_text(
                user_data.document_valid_date if not masked else "01.01.1100"
            )
            self.locators.BIRTH_PLACE.to_contain_text(user_data.birth_place if not masked else "***")
            self.locators.BIRTH_DATE.to_contain_text(user_data.birth_date if not masked else "01.01.1100")
            self.locators.PUBLIC_PERSON.to_contain_text(user_data.is_public)
            self.locators.SNILS.to_contain_text(user_data.snils if not masked else "***")
        self.locators.NATIONALITY.to_contain_text(user_data.nationality)
        self.locators.SPEAKING_LANGUAGE.to_contain_text(user_data.speaking_language)
        self.locators.RESIDENT.to_contain_text(user_data.is_resident)
        self.locators.INN.to_contain_text(user_data.inn if not masked else "***")
        if isinstance(user_data, OrganizationClient):
            self.locators.KPP.to_contain_text(user_data.kpp)
            self.locators.AUTHORIZATION_CODE.to_contain_text(user_data.auth_code if not masked else "***")
            self.locators.OGRN.to_contain_text(user_data.ogrn)
            self.locators.OKATO.to_contain_text(user_data.okato)
            self.locators.OKPO.to_contain_text(user_data.okpo)
            self.locators.OKVED.to_contain_text(user_data.okved)

    @allure.step("Открыть персональный договор клиента")
    def open_personal_agreement(self) -> None:
        self.locators.PERSONAL_AGREEMENT_LINK.wait_to_be_visible()
        self.locators.PERSONAL_AGREEMENT_LINK.click()

    @allure.step("Перейти в раздел 'Финансы > Платежи' текущего ЛС")
    def open_payments_for_current_account(self) -> None:
        self.locators.PERSONAL_ACCOUNTS_TAB.wait_to_be_visible()
        self.locators.PERSONAL_ACCOUNTS_TAB.click()
        self.locators.PERSONAL_ACCOUNT_LINKS[-1].wait_to_be_enabled()
        self.locators.PERSONAL_ACCOUNT_LINKS[-1].click()
        self.locators.BURGER_MENU.select_by_value("Финансы > Платежи")

    @allure.step("Перейти в раздел 'Финансы > Биллинговые счета' текущего ЛС")
    def open_bills_for_current_account(self) -> None:
        self.locators.CLIENT_FIO_BTN.click()
        self.locators.PERSONAL_ACCOUNTS_TAB.click()
        self.locators.PERSONAL_ACCOUNT_LINKS[-1].wait_to_be_enabled()
        self.locators.PERSONAL_ACCOUNT_LINKS[-1].click()
        self.locators.BURGER_MENU.select_by_value("Финансы > Биллинговые счета")

    @allure.step("Открыть заявку по названию типа: {type_name}")
    def open_request_by_type_name(
        self, type_name: str = "Продажа и управление услугами", should_check_product_name: bool = True
    ) -> None:
        """
        Открывает первую заявку с таким типом
        :param type_name: Имя типа заявки
        """

        self.locators.UPDATE_REQUESTS_BTN.wait_to_be_enabled()
        self.locators.UPDATE_REQUESTS_BTN.click()
        self.locators.REQUEST_TYPE.wait_to_be_visible()
        self.locators.REQUEST_TYPE.wait_for_text_in_all([type_name])
        index_request = self.locators.REQUEST_TYPE.text_list.index(type_name)
        self.locators.REQUEST_NUMBER[index_request].click()

        self.inquiries_form.LOAD_SPIN_THIRD.not_to_be_visible(timeout=30000)
        if should_check_product_name:
            self.inquiries_form.ADDED_PRODUCT.wait_to_be_visible(timeout=10000)

    @allure.step("Добавить клиента в группу клиентов")
    def add_client_to_client_group(self, client_group_name: str, client_role: str) -> None:
        self.locators.ADD_CLIENT_GROUP_BTN.click()
        self.locators.CLIENT_GROUPS.wait_to_be_visible(timeout=15000)
        self.locators.CLIENT_GROUPS_SEARCH.fill(client_group_name)
        self.locators.CLIENT_GROUPS.wait_to_have_count(1, timeout=15000)
        self.locators.CLIENT_GROUPS[0].wait_to_have_text(client_group_name)
        self.locators.CLIENT_GROUPS.click(0)
        self.locators.NEXT_BTN.click()
        self.locators.CLIENT_ROLE_DROPDOWN.select_by_value(client_role)
        self.create_request_form.CREATE_BTN.click()

    @allure.step("Открыть заявку с индексом {request_index}")
    def open_request(self, request_index: int = 0) -> None:
        self.locators.REQUEST_NUMBER[request_index].wait_to_be_visible(timeout=10000)
        self.locators.REQUEST_NUMBER[request_index].click()

        self.inquiries_form.LOAD_SPIN_THIRD.not_to_be_visible(timeout=30000)
        self.inquiries_form.ADDED_PRODUCT.wait_to_be_visible(timeout=10000)

    @allure.step("Открыть вкладку Заявки")
    def open_requests_tab(self) -> None:
        self.locators.REQUESTS_TAB.wait_to_be_visible(timeout=10000)
        self.locators.REQUESTS_TAB.click()

    @allure.step("Открыть форму Замена ресурса")
    def open_replace_resource_form(self) -> None:
        self.locators.RESOURCE_REPLACE.wait_to_be_visible(timeout=15000)
        self.locators.RESOURCE_REPLACE.click()
        self.replace_resource_form.TITLE.wait_to_be_visible(timeout=10000)

    @allure.step("Заполнить поля формы Замена ресурса")
    def fill_replace_resource_fields(
        self,
        replaceable_resource_serial_number: str,
        for_replace_serial_number: str,
        need_add_agreement: bool,
        need_acceptance_certificate: bool,
        discount: int,
    ) -> None:
        """
        Заполнение полей на форме Замена ресурса
        :param replaceable_resource_serial_number: Серийный номер заменяемого ресурса
        :param for_replace_serial_number: Серийный номер ресурса на замену
        :param need_add_agreement: Флаг необходимости включения чекбокса для формирования дополнительного соглашения
        :param need_acceptance_certificate: Флаг необходимости включения чекбокса для формирования акта приема-передачи
        :param discount: Размер скидки
        """

        self.replace_resource_form.REPLACEABLE_RESOURCE_IDENTIFIER.wait_to_be_visible(timeout=10000)
        self.replace_resource_form.REPLACEABLE_RESOURCE_IDENTIFIER.select_by_value(
            replaceable_resource_serial_number, include_last_symbol=True
        )
        self.replace_resource_form.FOR_REPLACE_FROM_EARLIER_PURCHASED.click()
        self.replace_resource_form.FOR_REPLACE_RESOURCE_IDENTIFIER.fill(for_replace_serial_number)
        if need_add_agreement:
            self.replace_resource_form.ADD_AGREEMENT_CHECKBOX.click()
        if need_acceptance_certificate:
            self.replace_resource_form.ACCEPTANCE_CERTIFICATE_CHECKBOX.click()
        if discount:
            base_price = self.replace_resource_form.REPLACE_SUM.text
            expected_price = calc_price_after_discount(get_price_and_currency(base_price)[0], discount)
            self.replace_resource_form.DISCOUNT_INPUT.fill(discount)
            check_price(self.replace_resource_form.REPLACE_SUM_AFTER_DISCOUNT, expected_price, check_format=False)

    @allure.step("Проверить поля формы Замена ресурса")
    def check_replace_resource_fields(
        self, product_name: str, subscriber: str, nomenclature: str, type_of_sale: str
    ) -> None:
        self.replace_resource_form.REPLACEABLE_RESOURCE_PRODUCT_NAME.wait_to_have_text(product_name)
        self.replace_resource_form.REPLACEABLE_RESOURCE_SUBSCRIBER.wait_to_have_text(subscriber)
        self.replace_resource_form.REPLACEABLE_RESOURCE_NOMENCLATURE_CODE.wait_to_have_text(nomenclature)
        self.replace_resource_form.REPLACEABLE_RESOURCE_TYPE_OF_SALE.wait_to_have_text(type_of_sale)

    @allure.step("Получить id заявки из всплывающего сообщения")
    def get_inquiry_id_from_info_message(self) -> int:
        info_message = self.locators.INFO_MESSAGE.text
        info_message_split = info_message.split()
        if len(info_message_split) > 1:
            if info_message_split[1].isdigit():
                inquiry_id = int(info_message_split[1])
                return inquiry_id
            else:
                raise ValueError(
                    f"Ожидалось число, получено значение типа {type(info_message_split[1])}, isdigit = {info_message_split[1].isdigit()}"
                )
        else:
            raise ValueError("В полученном массиве строк ожидалось больше 1 значения")

    @allure.step("Редактирование данных клиента")
    def edit_individual_client(self, surname: str, tax_scheme: str) -> None:
        self.client_attributes.EDIT_ATTRIBUTES_BTN.wait_to_be_visible(timeout=15000)
        self.client_attributes.EDIT_ATTRIBUTES_BTN.click()
        self.client_attributes.SURNAME_INPUT.fill(surname)
        self.client_attributes.TAX_SCHEME.select_by_value(tax_scheme)
        self.locators.SAVE_BTN.wait_to_be_visible()
        self.locators.SAVE_BTN.click()
        self.locators.SAVE_BTN.not_to_be_visible(timeout=15000)

    @allure.step("Редактирование данных клиента")
    def edit_organization_client(self, ogrn: str, tax_scheme: str) -> None:
        self.client_attributes.EDIT_ATTRIBUTES_BTN.wait_to_be_visible(timeout=15000)
        self.client_attributes.EDIT_ATTRIBUTES_BTN.click()
        self.client_attributes.OGRN.fill(ogrn)
        self.client_attributes.TAX_SCHEME.select_by_value(tax_scheme)
        self.locators.SAVE_BTN.wait_to_be_visible()
        self.locators.SAVE_BTN.click()
        self.locators.SAVE_BTN.not_to_be_visible(timeout=15000)

    @allure.step("Проверка истории изменения атрибутов")
    def check_attributes_history(
        self, attributes: list, old_values: list, new_values: list, values_operations: list | None = None
    ) -> None:
        check_that(
            lambda: len(old_values) == len(new_values) == len(attributes),
            exception=ValueError,
            message="Переданы некорректные значения для проверки",
        )
        list_len = len(old_values)
        if values_operations is None:
            values_operations = [AtsOperations.change] * list_len
        else:
            check_that(
                lambda: list_len == len(values_operations),
                exception=ValueError,
                message="Переданы некорректные значения для проверки",
            )
        self.client_attributes.HISTORY_BTN.wait_to_be_visible(timeout=15000)
        self.client_attributes.HISTORY_BTN.click()
        self.client_attributes.HISTORY_SIDEBAR_TITLE.wait_to_be_visible(timeout=15000)
        self.client_attributes.HISTORY_TABLE_ROWS.wait_to_have_count_or_greater(1, timeout=15000)
        for init_list_index, attribute in enumerate(attributes):
            row_index = [
                row_attribute.text for row_attribute in self.client_attributes.HISTORY_TABLE_ROW_ATTRIBUTE
            ].index(attribute)
            assert_that(lambda: row_index != -1, "Нужный атрибут не найден в истории изменений")
            self.client_attributes.HISTORY_TABLE_ROW_OLD_VALUES[row_index].wait_to_have_text(old_values[init_list_index])
            self.client_attributes.HISTORY_TABLE_ROW_NEW_VALUES[row_index].wait_to_have_text(new_values[init_list_index])
            self.client_attributes.HISTORY_TABLE_ROW_OPERATIONS[row_index].wait_to_have_text(
                values_operations[init_list_index]
            )
        self.client_attributes.HISTORY_SIDEBAR_CLOSE_BTN.wait_to_be_visible()
        self.client_attributes.HISTORY_SIDEBAR_CLOSE_BTN.click()
        self.client_attributes.HISTORY_SIDEBAR_TITLE.not_to_be_visible(timeout=15000)
