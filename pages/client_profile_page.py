import allure
from playwright.sync_api import Page

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

    @allure.step("Выбрать Тип адреса c названием {name}")
    def choose_option_with_name(self, name: str):
        self.add_address_form.ADDRESS_TYPE_OPTIONS.wait_elements_visible(element_index=0)
        for item in range(self.add_address_form.ADDRESS_TYPE_OPTIONS.elements_len()):
            if self.add_address_form.ADDRESS_TYPE_OPTIONS.get_text(element_index=item) == name:
                self.add_address_form.ADDRESS_TYPE_OPTIONS.click(element_index=item)
                break

    @allure.step("Заполнить форму создания нового адреса для Клиента")
    def fill_client_new_address(self, country: str, region: str, city: str, street: str, building_number: int,
                                flat_number: int):
        self.create_address_form.TITLE.to_contain_text("Создание нового адреса")
        self.create_address_form.OBJECT_TYPE.select_by_value("Страна")
        self.create_address_form.OBJECT_NAME_AUTOCOMPLETE.fill(country)
        self.create_address_form.ADD_ADDRESS_OBJECT_BTN.not_to_be_enabled()
        self.create_address_form.APPLY_BTN.click()

        self.create_address_form.ADDED_CARD.wait_elements_visible(element_index=0)
        self.create_address_form.ATTRIBUTE_HEADER.to_contain_text(element_index=0, text="Атрибуты")
        self.create_address_form.ADDED_CARD_EDIT_BTN.wait_elements_visible(element_index=0)
        self.create_address_form.ADDED_CARD_DELETE_BTN.wait_elements_visible(element_index=0)
        self.create_address_form.ADD_ADDRESS_OBJECT_BTN.to_be_enabled()

        self.create_address_form.ADD_ADDRESS_OBJECT_BTN.click()
        self.create_address_form.OBJECT_TYPE.select_by_value("Регион")
        self.create_address_form.OBJECT_NAME_AUTOCOMPLETE.fill(region)
        self.create_address_form.REGION_TYPE_DROPDOWN.select_by_value("Область")
        self.create_address_form.APPLY_BTN.click()

        self.create_address_form.ADD_ADDRESS_OBJECT_BTN.click()
        self.create_address_form.OBJECT_TYPE.select_by_value("Город")
        self.create_address_form.OBJECT_NAME_AUTOCOMPLETE.fill(city)
        self.create_address_form.CITY_TYPE_DROPDOWN.select_by_value("Город")
        self.create_address_form.APPLY_BTN.click()

        self.create_address_form.ADD_ADDRESS_OBJECT_BTN.click()
        self.create_address_form.OBJECT_TYPE.select_by_value("Улица")
        self.create_address_form.OBJECT_NAME_AUTOCOMPLETE.fill(street)
        self.create_address_form.STREET_TYPE_DROPDOWN.select_by_value("Улица")
        self.create_address_form.APPLY_BTN.click()

        self.create_address_form.ADD_ADDRESS_OBJECT_BTN.click()
        self.create_address_form.OBJECT_TYPE.select_by_value("Дом")
        self.create_address_form.HOUSE_TYPE_DROPDOWN.select_by_value("Дом")
        self.create_address_form.OBJECT_NUM.fill(str(building_number))
        self.create_address_form.APPLY_BTN.click()

        self.create_address_form.ADD_ADDRESS_OBJECT_BTN.click()
        self.create_address_form.OBJECT_TYPE.select_by_value("Жилое помещение")
        self.create_address_form.APARTMENT_TYPE_DROPDOWN.select_by_value("Квартира")
        self.create_address_form.OBJECT_NUM.fill(str(flat_number))
        self.create_address_form.APPLY_BTN.click()
