import allure
from playwright.sync_api import Page

from common.helpers.time_helpers import delay
from pages.base_page import BasePage
from pages.locators.client_profile import ClientProfile
from pages.locators.dynamic_form_elements import AddAddress, AddressCreate


class ClientProfilePage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        self.locators = ClientProfile(page)
        self.add_address_form = AddAddress(page)
        self.create_address_form = AddressCreate(page)

    @allure.step("Перейти во вкладку 'Клиент'")
    def click_client_tab(self):
        self.locators.CLIENT_TAB.wait_to_be_visible()
        self.locators.CLIENT_TAB.click()

    def fill_country_attribute(self, country: str):
        self.create_address_form.OBJECT_TYPE.select_by_value("Страна")
        self.create_address_form.OBJECT_NAME_AUTOCOMPLETE.select_by_value(country)
        self.create_address_form.ADD_ADDRESS_OBJECT_BTN.not_to_be_enabled()
        self.create_address_form.APPLY_BTN.click()

    def fill_region_attribute(self, region: str):
        self.create_address_form.ADD_ADDRESS_OBJECT_BTN.click()
        self.create_address_form.OBJECT_TYPE.select_by_value("Регион")
        self.create_address_form.OBJECT_NAME_AUTOCOMPLETE.fill(region)
        self.create_address_form.REGION_TYPE_DROPDOWN.select_by_value("Область")
        self.create_address_form.APPLY_BTN.click()

    def fill_city_attribute(self, city: str):
        self.create_address_form.ADD_ADDRESS_OBJECT_BTN.click()
        self.create_address_form.OBJECT_TYPE.select_by_value("Город")
        self.create_address_form.OBJECT_NAME_AUTOCOMPLETE.fill(city)
        self.create_address_form.CITY_TYPE_DROPDOWN.select_by_value("Город")
        self.create_address_form.APPLY_BTN.click()

    def fill_street_attribute(self, street: str):
        self.create_address_form.ADD_ADDRESS_OBJECT_BTN.click()
        self.create_address_form.OBJECT_TYPE.select_by_value("Улица")
        self.create_address_form.OBJECT_NAME_AUTOCOMPLETE.fill(street)
        self.create_address_form.STREET_TYPE_DROPDOWN.select_by_value("Улица")
        self.create_address_form.APPLY_BTN.click()

    def fill_building_number_attribute(self, building_number: int):
        self.create_address_form.ADD_ADDRESS_OBJECT_BTN.click()
        self.create_address_form.OBJECT_TYPE.select_by_value("Дом")
        self.create_address_form.HOUSE_TYPE_DROPDOWN.select_by_value("Дом")
        self.create_address_form.OBJECT_NUM.fill(str(building_number))
        self.create_address_form.APPLY_BTN.click()

    def fill_flat_number_attribute(self, flat_number: int):
        self.create_address_form.ADD_ADDRESS_OBJECT_BTN.click()
        self.create_address_form.OBJECT_TYPE.select_by_value("Жилое помещение")
        self.create_address_form.APARTMENT_TYPE_DROPDOWN.select_by_value("Квартира")
        self.create_address_form.OBJECT_NUM.fill(str(flat_number))
        self.create_address_form.APPLY_BTN.click()

    @allure.step("Заполнить форму создания нового адреса для Клиента")
    def fill_client_new_address(self, country: str, region: str, city: str, street: str, building_number: int,
                                flat_number: int):
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
    def choose_address_type_with_name(self, name: str):
        for item in self.locators.TYPE_FILTER_OPTIONS:
            if item.text == name:
                item.click()
                break

    @allure.step("Заполнить полностью форму создания нового адреса для Клиента и проверить атрибуты")
    def fill_all_fields_client_new_address(self, country: str, region: str, city: str, street: str,
                                           building_number: int, flat_number: int, gar: str, block: str, building: str,
                                           address_index: str):
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
        self.create_address_form.OBJECT_NAME_AUTOCOMPLETE.fill(region)
        self.create_address_form.REGION_TYPE_DROPDOWN.select_by_value("Область")
        self.create_address_form.OBJECT_GAR.fill(gar)
        self.create_address_form.APPLY_BTN.click()
        self.create_address_form.ATTRIBUTE_HEADER[-1].click()
        self.create_address_form.ATTRIBUTE_FIELDS[-3].to_have_value(region, 10000)
        self.create_address_form.ATTRIBUTE_FIELDS[-1].to_have_value(gar)

        self.create_address_form.ADD_ADDRESS_OBJECT_BTN.click()
        self.create_address_form.OBJECT_TYPE.select_by_value("Город")
        self.create_address_form.OBJECT_NAME_AUTOCOMPLETE.fill(city)
        self.create_address_form.CITY_TYPE_DROPDOWN.select_by_value("Город")
        self.create_address_form.OBJECT_GAR.fill(gar)
        self.create_address_form.APPLY_BTN.click()
        self.create_address_form.ATTRIBUTE_HEADER[-1].click()
        self.create_address_form.ATTRIBUTE_FIELDS[-3].to_have_value(city, 10000)
        self.create_address_form.ATTRIBUTE_FIELDS[-1].to_have_value(gar)

        self.create_address_form.ADD_ADDRESS_OBJECT_BTN.click()
        self.create_address_form.OBJECT_TYPE.select_by_value("Улица")
        self.create_address_form.OBJECT_NAME_AUTOCOMPLETE.fill(street)
        self.create_address_form.STREET_TYPE_DROPDOWN.select_by_value("Улица")
        self.create_address_form.OBJECT_GAR.fill(gar)
        self.create_address_form.APPLY_BTN.click()
        self.create_address_form.ATTRIBUTE_HEADER[-1].click()
        self.create_address_form.ATTRIBUTE_FIELDS[-3].to_have_value(street, 10000)
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
        self.create_address_form.OBJECT_GAR.fill(gar)
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
        self.create_address_form.OBJECT_TYPE.select_by_value("Жилое помещение")
        self.create_address_form.APARTMENT_TYPE_DROPDOWN.select_by_value("Квартира")
        self.create_address_form.OBJECT_NUM.fill(str(flat_number))
        self.create_address_form.APPLY_BTN.click()
        self.create_address_form.ATTRIBUTE_HEADER[-1].click()
        self.create_address_form.ATTRIBUTE_FIELDS_BLOCK[-2].wait_to_have_text("Квартира")
        self.create_address_form.ATTRIBUTE_FIELDS[-1].to_have_value(str(flat_number))

    @allure.step("Заполнить обязательные поля формы создания нового адреса для Клиента и проверить атрибуты")
    def fill_required_fields_client_new_address(self, country: str, region: str, city: str, street: str,
                                                building_number: int, flat_number: int):
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
        self.create_address_form.ATTRIBUTE_FIELDS[-3].to_have_value(region, 10000)

        self.fill_city_attribute(city)
        self.create_address_form.ATTRIBUTE_HEADER[-1].click()
        self.create_address_form.ATTRIBUTE_FIELDS[-3].to_have_value(city, 10000)

        self.fill_street_attribute(street)
        self.create_address_form.ATTRIBUTE_HEADER[-1].click()
        self.create_address_form.ATTRIBUTE_FIELDS[-3].to_have_value(street, 10000)

        self.fill_building_number_attribute(building_number)
        self.create_address_form.ATTRIBUTE_HEADER[-1].click()
        self.create_address_form.ATTRIBUTE_FIELDS_BLOCK[-8].wait_to_have_text("Дом")
        self.create_address_form.ATTRIBUTE_FIELDS[-7].to_have_value(str(building_number))

        self.fill_flat_number_attribute(flat_number)
        self.create_address_form.ATTRIBUTE_HEADER[-1].click()
        self.create_address_form.ATTRIBUTE_FIELDS_BLOCK[-2].wait_to_have_text("Квартира")
        self.create_address_form.ATTRIBUTE_FIELDS[-1].to_have_value(str(flat_number))

    def edit_attribute_and_check_value_for_field_with_index(self, field_index: int, value: str,
                                                            value_type: str = "name"):
        """Отредактировать атрибут адреса и проверить после редактирования значение для поля с индексом field_index
         (у проверяемого поля может быть разный индекс)"""
        self.create_address_form.ADDED_CARD_EDIT_BTN[-1].click()
        if value_type == "name":
            self.create_address_form.OBJECT_NAME_AUTOCOMPLETE.fill(value)
        elif value_type == "num":
            self.create_address_form.OBJECT_NUM.fill(value)
        self.create_address_form.APPLY_BTN.click()

        self.create_address_form.ATTRIBUTE_HEADER[-1].click()
        self.create_address_form.ATTRIBUTE_FIELDS[field_index].to_have_value(value)

    @allure.step("Заполнить обязательные поля формы создания нового адреса для Клиента и проверить атрибуты")
    def fill_and_update_address_data(self, country: str, new_country: str, region: str, new_region: str,
                                     city: str, new_city: str, street: str, building_number: int, flat_number: int):
        self.create_address_form.TITLE.to_contain_text("Создание нового адреса")
        self.fill_country_attribute(country)
        self.edit_attribute_and_check_value_for_field_with_index(field_index=0, value=new_country)

        self.fill_region_attribute(region)
        self.edit_attribute_and_check_value_for_field_with_index(field_index=-3, value=new_region)

        self.fill_city_attribute(city)
        self.edit_attribute_and_check_value_for_field_with_index(field_index=-3, value=new_city)

        self.fill_street_attribute(street)
        self.edit_attribute_and_check_value_for_field_with_index(field_index=-3, value=f"{street}тест")

        self.fill_building_number_attribute(building_number)
        self.edit_attribute_and_check_value_for_field_with_index(field_index=-7, value=str(building_number*2),
                                                                 value_type="num")

        self.fill_flat_number_attribute(flat_number)
        self.edit_attribute_and_check_value_for_field_with_index(field_index=-1, value=str(flat_number * 2),
                                                                 value_type="num")
