import re

import allure
from playwright.sync_api import Locator

from api.nbss.client_requests.client_requests import MainProduct
from common.helpers.checker import assert_that, wait_that
from common.helpers.string_helper import get_price_and_currency
from common.helpers.time_helpers import delay
from models.client import IndividualClient, OrganizationClient
from models.context import test_context
from models.product import AdditionalProduct
from pages.base_page import BasePage
from pages.locators.nbss.client.client_profile import (
    ClientProfileElements,
    ClientProfileEndUser,
    EditClientProfile,
    PersonalAccountForm,
)
from pages.locators.nbss.client.client_search import ClientSearchElements
from pages.locators.nbss.dynamic_form_elements import (
    AddAddress,
    AddOptionsForm,
    AddressCreate,
    ChangeMainProductForm,
    CreateSalesAndServiceManagement,
)
from pages.locators.nbss.home_page_elements import HomePageElements
from pages.locators.nbss.select_product_offers_form import SelectProductOffersFormElements


class ClientProfilePage(BasePage):
    def __init__(self) -> None:
        super().__init__()

        self.locators = ClientProfileElements()
        self.add_address_form = AddAddress()
        self.create_address_form = AddressCreate()
        self.end_user_form = ClientProfileEndUser()
        self.edit_client_form = EditClientProfile()
        self.personal_account = PersonalAccountForm()
        self.add_options_form = AddOptionsForm()
        self.home_page = HomePageElements()
        self.client_search_page = ClientSearchElements()
        self.change_product_form = ChangeMainProductForm()
        self.create_request_form = CreateSalesAndServiceManagement()
        self.select_product_offers_form = SelectProductOffersFormElements()

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
        self.create_address_form.OBJECT_TYPE.select_by_value("Жилое помещение")
        self.create_address_form.APARTMENT_TYPE_DROPDOWN.select_by_value("Квартира")
        self.create_address_form.OBJECT_NUM.fill(str(flat_number))
        self.create_address_form.APPLY_BTN.click()
        self.create_address_form.ATTRIBUTE_HEADER[-1].click()
        self.create_address_form.ATTRIBUTE_FIELDS_BLOCK[-2].wait_to_have_text("Квартира")
        self.create_address_form.ATTRIBUTE_FIELDS[-1].to_have_value(str(flat_number))

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
            field_index=-1, input_value=str(flat_number * 2), value_type="num"
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

    @allure.step("Кликнуть на первый продукт")
    def click_first_product(self, subscriber: str, product_name: str, product_active: bool = True) -> None:
        self.locators.PRODUCTS_LIST.wait_elements_visible(0)
        self.locators.SUBSCRIBER[0].wait_to_have_text(subscriber)
        if product_active:
            self.locators.PRODUCT_LIMIT.wait_to_be_visible()
        self.locators.PRODUCT_NAME.wait_elements_visible(0)
        self.locators.PRODUCT_NAME[0].wait_to_have_text(product_name)
        self.locators.PRODUCT_NAME[0].click(force=True)

    @allure.step("Развернуть все продукты клиента")
    def expand_all_products(self) -> None:
        """
        Раскрывает все свернутые продукты клиента на странице продуктов.

        Метод проходит по всем продуктам и раскрывает те, которые свернуты (aria-expanded="false").
        Ждет появления каждого раскрытого продукта перед переходом к следующему.
        Может раскрыться несколько продуктов одновременно от одного клика.
        """
        self.locators.PRODUCTS_HEADER_LIST.wait_to_be_visible()
        for i in range(self.locators.PRODUCTS_LIST.elements_len()):
            header = self.locators.PRODUCTS_HEADER_LIST[i]

            if header.locator.is_visible(timeout=1000):
                aria_expanded = header.get_attribute("aria-expanded")
                if aria_expanded == "false":
                    header.scroll_into_view_if_needed()
                    delay(0.3, "Ожидание прокрутки к элементу")

                    current_opened = self.locators.PRODUCTS.elements_len()
                    header.click(force=True)

                    wait_that(
                        lambda: self.locators.PRODUCTS.elements_len() > current_opened,
                        timeout=15,
                        sleep_seconds=0.5,
                        exception=AssertionError,
                        message=f"Количество открытых продуктов не увеличилось после клика на продукт {i}",
                    )

    @allure.step("Проверить что все продукты и абоненты отображаются и активированы")
    def check_all_products(self, products: list[MainProduct], is_activated: bool = True) -> None:
        products_count = len(products)
        self.expand_all_products()
        self.locators.PRODUCTS.wait_to_have_count(products_count, timeout=15000)
        for i in range(products_count):
            subscriber = self.locators.SUBSCRIBER[i].text
            name = self.locators.PRODUCT_NAME[i].text
            for product in products:
                if subscriber == product.phone_number or subscriber == product.internet_number:
                    assert_that(
                        lambda: name == product.product_name,
                        f"У абонента {subscriber} название продукта {name} не совпадает с {product.product_name}",
                    )
                    break
        if is_activated:
            self.locators.PRODUCTS_STATUS_COLOR.to_have_css_color("background-color", "green")

    @allure.step("Получить количество лимитов опций {index} продукта")
    def get_option_limit_count(self, index: int) -> int:
        return len(
            self.page.locator(self.locators.PRODUCTS.path).nth(index).locator(self.locators.OPTION_LIMIT_ICON.path).all()
        )

    @allure.step("Добавить конечного пользователя которого нет в системе")
    def add_non_existing_end_user(self, user_data: IndividualClient) -> None:
        self.end_user_form.ADD_END_USER_BUTTON.click()
        self.end_user_form.DOCUMENT_TYPE_DROPDOWN.wait_to_be_visible()
        self.end_user_form.DOCUMENT_TYPE_DROPDOWN.select_by_value(user_data.document_type)
        self.end_user_form.DOCUMENT_SERIES.fill(user_data.document_serial)
        self.end_user_form.DOCUMENT_NUMBER.fill(user_data.document_num)
        self.end_user_form.ADD_END_USER_NEXT_BUTTON.click()

        self.end_user_form.SURNAME_INPUT.wait_to_be_visible()
        self.end_user_form.LOADER.not_to_be_visible()
        self.end_user_form.SURNAME_INPUT.fill(user_data.sur_name)
        self.end_user_form.NAME_INPUT.fill(user_data.first_name)
        self.end_user_form.PATRONYMIC_INPUT.fill(user_data.patronymic)
        self.end_user_form.GENDER_DROPDOWN.select_by_value(user_data.gender)
        self.end_user_form.WHO_ISSUED_THE_DOCUMENT_INPUT.fill(user_data.document_provide_by)
        self.end_user_form.SUBDIVISION_CODE_INPUT.fill(user_data.document_division_code)
        self.end_user_form.DATE_OF_ISSUE_INPUT.type(user_data.issue_date)
        self.press_keyboard_button("Enter")
        self.end_user_form.DOCUMENT_VALID_FOR_INPUT.fill(user_data.document_valid_date)
        delay(0.5, "Чтобы календарь успел отобразить изменения")
        self.end_user_form.BIRTHDAY_INPUT.type(user_data.birth_date)
        self.press_keyboard_button("Enter")
        self.end_user_form.PLACE_OF_BIRTH_INPUT.fill(user_data.birth_place)
        self.end_user_form.REGISTRATION_ADDRESS_INPUT.select_by_value(
            user_data.registration_address, include_last_symbol=True
        )
        self.end_user_form.ADD_END_USER_NEXT_BUTTON.click()

    @allure.step("Добавить существующего конечного пользователя")
    def add_existing_end_user(self, user_data: IndividualClient) -> None:
        self.end_user_form.ADD_END_USER_BUTTON.click()
        self.end_user_form.DOCUMENT_TYPE_DROPDOWN.wait_to_be_visible()
        self.end_user_form.DOCUMENT_TYPE_DROPDOWN.select_by_value(user_data.document_type)
        self.end_user_form.DOCUMENT_SERIES.fill(user_data.document_serial)
        self.end_user_form.DOCUMENT_NUMBER.fill(user_data.document_num)
        self.end_user_form.ADD_END_USER_NEXT_BUTTON.click()

        self.end_user_form.EXISTING_CLIENT_FOUND_TITLE.wait_to_be_visible(timeout=10000)
        self.end_user_form.EXISTING_CLIENT_FOUND_TITLE.wait_to_have_text("Найден существующий клиент")
        self.end_user_form.CLIENT.wait_to_be_visible()
        self.end_user_form.CLIENT.click(0)
        self.end_user_form.ADD_END_USER_NEXT_BUTTON.wait_to_be_enabled()
        self.end_user_form.ADD_END_USER_NEXT_BUTTON.click()
        self.end_user_form.DATA_TITLE.wait_to_have_text("Данные конечного пользователя")

    @allure.step("Заменить конечного пользователя на существующего")
    def replace_existing_end_user(self, user_data: IndividualClient) -> None:
        self.end_user_form.DOCUMENT_TYPE_DROPDOWN.wait_to_be_visible()
        self.end_user_form.DOCUMENT_TYPE_DROPDOWN.select_by_value(user_data.document_type)
        self.end_user_form.DOCUMENT_SERIES.fill(user_data.document_serial)
        self.end_user_form.DOCUMENT_NUMBER.fill(user_data.document_num)
        self.end_user_form.ADD_END_USER_NEXT_BUTTON.click()

        self.end_user_form.EXISTING_CLIENT_FOUND_TITLE.wait_to_be_visible(timeout=10000)
        self.end_user_form.EXISTING_CLIENT_FOUND_TITLE.wait_to_have_text("Найден существующий клиент")
        self.end_user_form.CLIENT.click(0)
        self.end_user_form.ADD_END_USER_NEXT_BUTTON.click()
        self.end_user_form.DATA_TITLE.wait_to_have_text("Данные конечного пользователя")

    @allure.step("Проверить форму конечного пользователя")
    def check_end_user_form(self, user_data: IndividualClient, masked: bool = False) -> None:
        self.end_user_form.LOADER.not_to_be_visible(timeout=10000)
        self.end_user_form.FIO.to_contain_text(f"{user_data.sur_name} {user_data.first_name} {user_data.patronymic}")
        self.end_user_form.GENDER.to_contain_text(user_data.gender)
        self.end_user_form.DOCUMENT_TYPE.to_contain_text(user_data.document_type)
        self.end_user_form.DOCUMENT_SERIES_AND_NUMBER.to_contain_text(
            f"{user_data.document_serial} {user_data.document_num}" if not masked else "*** ***"
        )
        self.end_user_form.DOCUMENT_PROVIDE_BY.to_contain_text(user_data.document_provide_by) if not masked else "***"
        self.end_user_form.SUBDIVISION_CODE.to_contain_text(user_data.document_division_code if not masked else "***")
        self.end_user_form.DATE_OF_ISSUE.to_contain_text(user_data.issue_date if not masked else "01.01.1100")
        self.end_user_form.DOCUMENT_VALID_FOR.to_contain_text(
            user_data.document_valid_date if not masked else "01.01.1100"
        )
        self.end_user_form.PLACE_OF_BIRTH.to_contain_text(user_data.birth_place if not masked else "***")
        self.end_user_form.BIRTH_DATE.to_contain_text(user_data.birth_date if not masked else "01.01.1100")
        self.end_user_form.COUNTRY.to_contain_text(user_data.nationality)
        self.end_user_form.LANGUAGE.to_contain_text(user_data.speaking_language)
        self.end_user_form.REGISTRATION_ADDRESS.to_contain_text(user_data.registration_address)
        self.end_user_form.IS_PUBLIC.to_contain_text(user_data.is_public)
        self.end_user_form.IS_RESIDENT.to_contain_text(user_data.is_resident)

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

    @allure.step("Добавить дополнительное продуктовое предложение {product_name} через опции")
    def add_adoption_product(self, product_name: str) -> None:
        """Добавление дополнительного продуктового предложения
        :param product_name: Название дополнительного продукта"""

        with allure.step('Нажать "..." -> "Добавить опцию".'):
            self.locators.PRODUCTS_UPDATE_BTN.click()
            self.locators.PRODUCTS_OPTIONS_OPEN_BTN[0].click()
            self.locators.LOAD_SPINS.not_to_be_visible(timeout=8000)
            self.locators.PRODUCTS_OPTIONS_ADD_BTN.wait_to_be_visible()
            self.locators.PRODUCTS_OPTIONS_ADD_BTN.click()

        with allure.step(f"Выбрать дополнительный продукт {product_name}"):
            self.add_options_form.SEARCH_OPTIONS_FLD.fill(product_name)
            self.add_options_form.SEARCH_BTN.click()
            self.add_options_form.CHOSE_OPTION_BTN.wait_elements_visible(element_index=0)
            self.add_options_form.CHOSE_OPTION_BTN[0].click()
            self.add_options_form.INNER_ACCEPT_BTN.click()

    @allure.step("Сменить ПП с формированием договора")
    def change_product_offer_with_contract(
        self,
        auto_contract: bool = True,
        product_number: int = 1,
        product_name: str | None = None,
    ) -> str:
        """
        :param auto_contract: автоматическое / ручное согласование договора
        :param product_number: номер продукта в списке (1-й, 2-й, 3-й и т.д.)
        :param product_name: название ПП. Если указано - в первую очередь будет искать по нему
        :return: имя выбранного продукта
        """
        self.locators.PRODUCT_NAME.wait_to_be_visible(timeout=15000)
        self.locators.PRODUCTS_UPDATE_BTN.click()
        tech_product_index = product_number - 1

        with allure.step("Инициировать смену продукта"):
            self.locators.PRODUCTS_STATUS_COLOR.to_have_css_color("background-color", "green")
            self.locators.PRODUCTS_OPTIONS_OPEN_BTN[0].wait_to_be_enabled()
            self.locators.PRODUCTS_OPTIONS_OPEN_BTN[0].click()
            self.locators.LOAD_SPINS.not_to_be_visible(timeout=8000)
            self.locators.PRODUCTS_OPTIONS_CHANGE_MAIN_RODUCT_BTN.click()

        with allure.step(f"Выбрать продукт №{product_number} для замены"):
            self.change_product_form.SEARCH_BTN.wait_to_be_enabled()
            self.select_product_offers_form.PRODUCT_CARD_NAME.wait_to_be_visible(timeout=15000)

            chose_product_buttons = self.change_product_form.CHOSE_PRODUCT_BTN
            text_products = self.select_product_offers_form.PRODUCT_CARD_NAME
            target_product = None

            if product_name is not None:
                for i in range(text_products.elements_len()):
                    if text_products[i].text == product_name:
                        target_product = text_products[i]
                        tech_product_index = i
                        break
            else:
                target_product = text_products[tech_product_index]
            name_product = target_product.text
            assert name_product, "Имя продукта не найдено в форме смены ПП"

            try:
                choose_btn = chose_product_buttons[tech_product_index]
            except IndexError:
                raise AssertionError(
                    f"В форме смены ПП нет кнопки выбора ПП с индексом {tech_product_index} "
                    f"для продукта №{product_number}"
                )

            choose_btn.wait_to_be_enabled(timeout=8000)
            choose_btn.click()

            self.change_product_form.ADD_PRODUCT_BTN.click()

        with allure.step("Изменить данные формирования договора"):
            self.create_request_form.CHOOSE_AGREEMENT_BTN.wait_to_be_enabled(timeout=30000)
            self.create_request_form.CHOOSE_AGREEMENT_BTN.select_by_value(
                "Сформировать, факт согласования автоматически"
                if auto_contract
                else "Сформировать, факт согласования вручную"
            )
            self.create_request_form.SAVE_BTN.click()

        return name_product

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

    @allure.step("Проверить, что основной продукт изменён на '{expected_name}'")
    def check_main_product_changed(self, expected_name: str) -> None:
        self.locators.SUBSCRIBER.wait_to_be_visible(timeout=15000)
        self.locators.PRODUCT_NAME[0].wait_to_have_text(expected_name, timeout=15000)

    @allure.step("Открыть персональный договор клиента")
    def open_personal_agreement(self) -> None:
        self.locators.PERSONAL_AGREEMENT_LINK.wait_to_be_visible()
        self.locators.PERSONAL_AGREEMENT_LINK.click()

    @allure.step("Перейти в раздел 'Финансы > Платежи' текущего ЛС")
    def open_payments_for_current_account(self) -> None:
        self.locators.PERSONAL_ACCOUNTS_TAB.click()
        self.locators.CURRENT_PERSONAL_ACCOUNT_LINK.wait_to_be_enabled()
        self.locators.CURRENT_PERSONAL_ACCOUNT_LINK.click()
        self.locators.BURGER_MENU.select_by_value("Финансы > Платежи")

    @allure.step("Извлечение цен из элементов")
    def _extract_prices(self, nodes: Locator) -> list[float]:
        """
        Извлекает уникальные цены из коллекции элементов.

        Args:
            nodes: Локатор коллекции элементов, содержащих тексты с ценами

        Returns:
            Список уникальных цен (float)
        """
        prices: list[float] = []
        for i in range(nodes.count()):
            txt = nodes.nth(i).inner_text()
            if not txt:
                continue
            txt = txt.strip()
            if not txt or txt in ["/Месяц", "/месяц", "—", "-", "–"]:
                continue
            try:
                value, _ = get_price_and_currency(txt)
            except ValueError:
                continue
            if value and value not in prices:
                prices.append(value)
        return prices

    @allure.step("Проверка: На продукте отображается индивидуализированная цена")
    def check_individualized_subscription_fee_on_products_page(
        self,
        expected_price: float,
        original_price: float,
        product_index: int = 0,
    ) -> None:
        """
        Универсальная проверка индивидуализации:
        - индивидуализация может быть либо в абонплате (старая+новая, а разовый = —),
          либо в разовом (старая+новая, а абонплата = —).
        """
        delay(2, "Ожидание обновления цены на странице продуктов")

        name_el = self.locators.PRODUCT_NAME[product_index]
        name_locator = name_el.locator or self.page.locator(name_el.path)

        product_container = name_locator.locator(self.locators.PRODUCT_CONTAINER_FROM_NAME)
        product_container.wait_for(state="visible", timeout=10000)

        product_text = product_container.inner_text()

        subscription_xpath = self.locators.PRODUCTS_SUBSCRIPTION_FEE.path.replace("//", ".//", 1)
        one_time_xpath = self.locators.PRODUCT_ONE_TIME_PAYMENT.path.replace("//", ".//", 1)
        sub_nodes = product_container.locator(f"xpath={subscription_xpath}")
        one_nodes = product_container.locator(f"xpath={one_time_xpath}")

        subscription_prices = self._extract_prices(sub_nodes)
        one_time_prices = self._extract_prices(one_nodes)

        subscription_has_ind = len(subscription_prices) >= 2
        one_time_has_ind = len(one_time_prices) >= 2

        assert not (subscription_has_ind and one_time_has_ind), (
            f"Неожиданно: и абонплата, и разовый платёж имеют по 2+ цены у продукта #{product_index}.\n"
            f"Текст:\n{product_text}"
        )
        assert subscription_has_ind or one_time_has_ind, (
            f"Не найдена пара цен (старая+новая) ни в абонплате, ни в разовом платеже у продукта #{product_index}.\n"
            f"Текст:\n{product_text}"
        )

        actual_prices = subscription_prices if subscription_has_ind else one_time_prices
        context = "Абонентская плата" if subscription_has_ind else "Разовый платёж"

        self.check_prices_match(
            expected_prices=expected_price,
            actual_prices=actual_prices,
            original_prices=original_price,
            check_old_price=True,
            context_name=f"на продукте #{product_index} ({context})",
        )

    @allure.step("Открыть заявку по названию типа: {type_name}")
    def open_request_by_type_name(self, type_name: str = "Продажа и управление услугами") -> None:
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
        self.locators.ADD_BTN.click()

    @allure.step("Создать заявку на редактирование продукта")
    def create_product_edit_inquiry(self) -> None:
        self.locators.PRODUCTS_DETAILS_OPEN_BTN.wait_to_be_visible()
        delay(1, "Чтобы кнопка стала активной")
        self.locators.PRODUCTS_DETAILS_OPEN_BTN.click(force=True)
        self.locators.PRODUCT_EDIT_BTN.wait_to_be_visible(timeout=25000)
        self.locators.PRODUCT_EDIT_BTN.click(force=True)

        self.create_request_form.TITLE.wait_to_have_text("Создание продажи и управление услугами", timeout=15000)
        self.create_request_form.SAVE_BTN.wait_to_be_enabled()
        self.create_request_form.SAVE_BTN.click()

    @allure.step("Создать заявку на редактирование продукта")
    def create_product_disconnect_inquiry(self, product: MainProduct | AdditionalProduct) -> None:
        create_inquiry_form = CreateSalesAndServiceManagement()
        self.locators.PRODUCT_NAME.wait_to_be_visible(timeout=15000)

        with allure.step("Инициировать отключение продукта"):
            self.locators.PRODUCTS_STATUS_COLOR.to_have_css_color("background-color", "green")
            self.locators.PRODUCTS_DETAILS_OPEN_BTN.wait_to_be_visible()
            delay(1, "Чтобы кнопка стала активной")
            self.locators.PRODUCTS_DETAILS_OPEN_BTN.click(force=True)
            self.locators.TURN_OFF_BTN.wait_to_be_visible(timeout=25000)
            delay(2, "Чтобы опции успели раскрыться и кнопка отключения стала активной")
            self.locators.TURN_OFF_BTN.click(force=True)

        self.create_request_form.TITLE.wait_to_have_text("Создание продажи и управление услугами", timeout=25000)
        if "satellite" in product.category:
            create_inquiry_form.EQUIPMENT_RETURNED_ACTION.wait_to_be_visible()
            create_inquiry_form.EQUIPMENT_RETURNED_ACTION.select_by_value("Передать на склад для оценки состояния")
        self.create_request_form.SAVE_BTN.wait_to_be_enabled()
        self.create_request_form.SAVE_BTN.click()
