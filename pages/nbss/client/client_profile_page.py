import allure

from api.nbss.client_requests.client_requests import MainProduct
from common.helpers.checker import assert_that
from common.helpers.time_helpers import delay
from models.user import IndividualClient, OrganizationClient
from pages.base_page import BasePage
from pages.locators.nbss.client.client_profile import (
    ClientProfile,
    ClientProfileEndUser,
    EditClientProfile,
    PersonalAccountForm,
)
from pages.locators.nbss.client.client_search import ClientSearch
from pages.locators.nbss.dynamic_form_elements import (
    AddAddress,
    AddOptionsForm,
    AddressCreate,
    ChangeMainProductForm,
    CreateSalesAndServiceManagement,
)
from pages.locators.nbss.home_page_elements import HomePage


class ClientProfilePage(BasePage):
    def __init__(self) -> None:
        super().__init__()

        self.locators = ClientProfile()
        self.add_address_form = AddAddress()
        self.create_address_form = AddressCreate()
        self.end_user_form = ClientProfileEndUser()
        self.edit_client_form = EditClientProfile()
        self.personal_account = PersonalAccountForm()
        self.add_options_form = AddOptionsForm()
        self.home_page = HomePage()
        self.client_search_page = ClientSearch()
        self.change_product_form = ChangeMainProductForm()
        self.create_request_form = CreateSalesAndServiceManagement()

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

    def fill_country_attribute(self, country: str) -> None:
        self.create_address_form.OBJECT_TYPE.select_by_value("Страна")
        self.create_address_form.OBJECT_NAME_AUTOCOMPLETE.select_by_value(country)
        self.create_address_form.ADD_ADDRESS_OBJECT_BTN.not_to_be_enabled()
        self.create_address_form.APPLY_BTN.click()

    def fill_region_attribute(self, region: str) -> None:
        self.create_address_form.ADD_ADDRESS_OBJECT_BTN.click()
        self.create_address_form.OBJECT_TYPE.select_by_value("Регион")
        self.create_address_form.OBJECT_NAME_AUTOCOMPLETE.fill(region)
        self.create_address_form.REGION_TYPE_DROPDOWN.select_by_value("Область")
        self.create_address_form.APPLY_BTN.click()

    def fill_city_attribute(self, city: str) -> None:
        self.create_address_form.ADD_ADDRESS_OBJECT_BTN.click()
        self.create_address_form.OBJECT_TYPE.select_by_value("Город")
        self.create_address_form.OBJECT_NAME_AUTOCOMPLETE.fill(city)
        self.create_address_form.CITY_TYPE_DROPDOWN.select_by_value("Город")
        self.create_address_form.APPLY_BTN.click()

    def fill_street_attribute(self, street: str) -> None:
        self.create_address_form.ADD_ADDRESS_OBJECT_BTN.click()
        self.create_address_form.OBJECT_TYPE.select_by_value("Улица")
        self.create_address_form.OBJECT_NAME_AUTOCOMPLETE.fill(street)
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
        self.create_address_form.OBJECT_TYPE.select_by_value("Жилое помещение")
        self.create_address_form.APARTMENT_TYPE_DROPDOWN.select_by_value("Квартира")
        self.create_address_form.OBJECT_NUM.fill(str(flat_number))
        self.create_address_form.APPLY_BTN.click()

    @allure.step("Заполнить форму создания нового адреса для Клиента")
    def fill_client_new_address(
        self, country: str, region: str, city: str, street: str, building_number: int, flat_number: int
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
        self.create_address_form.OBJECT_NAME_AUTOCOMPLETE.fill(region)
        self.create_address_form.REGION_TYPE_DROPDOWN.select_by_value("Область")
        self.create_address_form.OBJECT_GAR[-1].fill(gar)
        self.create_address_form.APPLY_BTN.click()
        self.create_address_form.ATTRIBUTE_HEADER[-1].click()
        self.create_address_form.ATTRIBUTE_FIELDS[-3].to_have_value(region, 10000)
        self.create_address_form.ATTRIBUTE_FIELDS[-1].to_have_value(gar)

        self.create_address_form.ADD_ADDRESS_OBJECT_BTN.click()
        self.create_address_form.OBJECT_TYPE.select_by_value("Город")
        self.create_address_form.OBJECT_NAME_AUTOCOMPLETE.fill(city)
        self.create_address_form.CITY_TYPE_DROPDOWN.select_by_value("Город")
        self.create_address_form.OBJECT_GAR[-1].fill(gar)
        self.create_address_form.APPLY_BTN.click()
        self.create_address_form.ATTRIBUTE_HEADER[-1].click()
        self.create_address_form.ATTRIBUTE_FIELDS[-3].to_have_value(city, 10000)
        self.create_address_form.ATTRIBUTE_FIELDS[-1].to_have_value(gar)

        self.create_address_form.ADD_ADDRESS_OBJECT_BTN.click()
        self.create_address_form.OBJECT_TYPE.select_by_value("Улица")
        self.create_address_form.OBJECT_NAME_AUTOCOMPLETE.fill(street)
        self.create_address_form.STREET_TYPE_DROPDOWN.select_by_value("Улица")
        self.create_address_form.OBJECT_GAR[-1].fill(gar)
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
        self, country: str, region: str, city: str, street: str, building_number: int, flat_number: int
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

    def edit_attribute_and_check_value_for_field_with_index(
        self, field_index: int, value: str, value_type: str = "name"
    ) -> None:
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
        self.fill_country_attribute(country)
        self.edit_attribute_and_check_value_for_field_with_index(field_index=0, value=new_country)

        self.fill_region_attribute(region)
        self.edit_attribute_and_check_value_for_field_with_index(field_index=-3, value=new_region)

        self.fill_city_attribute(city)
        self.edit_attribute_and_check_value_for_field_with_index(field_index=-3, value=new_city)

        self.fill_street_attribute(street)
        self.edit_attribute_and_check_value_for_field_with_index(field_index=-3, value=f"{street}тест")

        self.fill_building_number_attribute(building_number)
        self.edit_attribute_and_check_value_for_field_with_index(
            field_index=-7, value=str(building_number * 2), value_type="num"
        )

        self.fill_flat_number_attribute(flat_number)
        self.edit_attribute_and_check_value_for_field_with_index(
            field_index=-1, value=str(flat_number * 2), value_type="num"
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
        for i in range(self.locators.PRODUCTS_LIST.elements_len()):
            if (
                self.page.locator(self.locators.PRODUCTS_HEADER_LIST.path).nth(i).get_attribute("aria-expanded")
                == "false"
            ):
                self.locators.PRODUCTS_HEADER_LIST[i].click()
                self.locators.PRODUCTS.wait_to_have_count(i + 1)

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
        self.end_user_form.REGISTRATION_ADDRESS_INPUT.select_by_value(user_data.registration_address)
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
    def check_end_user_form(self, user_data: IndividualClient) -> None:
        self.end_user_form.LOADER.not_to_be_visible(timeout=10000)
        self.end_user_form.FIO.to_contain_text(f"{user_data.sur_name} {user_data.first_name} {user_data.patronymic}")
        self.end_user_form.GENDER.to_contain_text(user_data.gender)
        self.end_user_form.DOCUMENT_TYPE.to_contain_text(user_data.document_type)
        self.end_user_form.DOCUMENT_SERIES_AND_NUMBER.to_contain_text(
            f"{user_data.document_serial} {user_data.document_num}"
        )
        self.end_user_form.DOCUMENT_PROVIDE_BY.to_contain_text(user_data.document_provide_by)
        self.end_user_form.SUBDIVISION_CODE.to_contain_text(user_data.document_division_code)
        self.end_user_form.DATE_OF_ISSUE.to_contain_text(user_data.issue_date)
        self.end_user_form.DOCUMENT_VALID_FOR.to_contain_text(user_data.document_valid_date)
        self.end_user_form.PLACE_OF_BIRTH.to_contain_text(user_data.birth_place)
        self.end_user_form.BIRTH_DATE.to_contain_text(user_data.birth_date)
        self.end_user_form.COUNTRY.to_contain_text(user_data.nationality)
        self.end_user_form.LANGUAGE.to_contain_text(user_data.speaking_language)
        self.end_user_form.REGISTRATION_ADDRESS.to_contain_text(user_data.registration_address)
        self.end_user_form.IS_PUBLIC.to_contain_text(user_data.is_public)
        self.end_user_form.IS_RESIDENT.to_contain_text(user_data.is_resident)

    @allure.step("Проверить форму связанных лиц")
    def check_related_person(self, user_data: IndividualClient) -> None:
        self.locators.RELATED_PERSON_TABLE_NAME.wait_to_be_visible(timeout=10000)
        self.locators.RELATED_PERSON_TABLE_NAME.to_contain_text(
            f"{user_data.sur_name} {user_data.first_name} {user_data.patronymic}"
        )
        self.locators.RELATED_PERSON_GENDER.to_contain_text(user_data.gender)
        self.locators.RELATED_PERSON_TYPE_OF_DOCUMENT.to_contain_text(user_data.document_type)
        self.locators.RELATED_PERSON_DOCUMENT_NUMBER.to_contain_text(
            f"{user_data.document_serial} {user_data.document_num}"
        )
        self.locators.RELATED_PERSON_DOCUMENT_PROVIDE_BY.to_contain_text(user_data.document_provide_by)
        self.locators.RELATED_PERSON_SUBDIVISION_CODE.to_contain_text(user_data.document_division_code)
        self.locators.RELATED_PERSON_DATE_OF_ISSUE.to_contain_text(user_data.issue_date)
        self.locators.RELATED_PERSON_VALID_FOR.to_contain_text(user_data.document_valid_date)
        self.locators.RELATED_PERSON_BIRTH_PLACE.to_contain_text(user_data.birth_place)
        self.locators.RELATED_PERSON_BIRTH_DATE.to_contain_text(user_data.birth_date)
        self.locators.RELATED_PERSON_COUNTRY.to_contain_text(user_data.nationality)
        self.locators.RELATED_SPEAKING_LANGUAGE.to_contain_text(user_data.speaking_language)
        self.locators.RELATED_PERSON_IS_PUBLIC.to_contain_text(user_data.is_public)
        self.locators.RELATED_PERSON_IS_RESIDENT.to_contain_text(user_data.is_resident)

        self.locators.RELATED_PERSON_INN.to_contain_text(user_data.inn)

        self.locators.RELATED_PERSON_CLIENT_FL.to_contain_text(
            f"{user_data.sur_name} {user_data.first_name} {user_data.patronymic}"
        )
        self.locators.RELATED_PERSON_END_USER.to_contain_text("—")

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
            self.locators.LOAD_SPIN.not_to_be_visible(timeout=8000)
            self.locators.PRODUCTS_OPTIONS_ADD_BTN.wait_to_be_visible()
            self.locators.PRODUCTS_OPTIONS_ADD_BTN.click()

        with allure.step(f"Выбрать дополнительный продукт {product_name}"):
            self.add_options_form.SEARCH_OPTIONS_FLD.fill(product_name)
            self.add_options_form.SEARCH_BTN.click()
            self.add_options_form.CHOSE_OPTION_BTN.wait_elements_visible(element_index=0)
            self.add_options_form.CHOSE_OPTION_BTN[0].click()
            self.add_options_form.INNER_ACCEPT_BTN.click()

    def navigate_to_client_search(self) -> None:
        self.home_page.HEADER_SEARCH_BTN.click()

    def go_to_search_and_clear_filters(self) -> None:
        self.navigate_to_client_search()
        self.clear_all_filters()

    @allure.step("Поиск с главной страницы")
    def search_from_main_page(
        self,
        customer_name: str = None,
        inn: str = None,
        account_number: str | int = None,
        subscriber: str = None,
        clear_and_research: bool = True,
    ) -> None:
        """
        Выполняет поиск с главной страницы, заполняет соответствующие поля,
        нажимает поиск, ждет загрузки страницы поиска.
        Если clear_and_research=True, очищает фильтры и повторно выполняет поиск.
        """
        with allure.step("Проверка отображения полей на главной странице"):
            self.home_page.HEADER_SEARCH_BTN.wait_to_be_visible()

        search_values = []
        with allure.step("Заполнение полей поиска на главной странице"):
            if customer_name:
                self.home_page.CUSTOMER_NAME.wait_to_be_visible()
                self.home_page.CUSTOMER_NAME.fill(customer_name)
                search_values.append(f"Клиент: '{customer_name}'")
            if inn:
                self.home_page.INN.wait_to_be_visible()
                self.home_page.INN.fill(inn)
                search_values.append(f"ИНН: '{inn}'")
            if account_number:
                self.home_page.HEADER_ACCOUNT_NUM.wait_to_be_visible()
                self.home_page.HEADER_ACCOUNT_NUM.fill(str(account_number))
                search_values.append(f"Лицевой счет: '{account_number}'")
            if subscriber:
                self.home_page.HEADER_SUBSCRIBER.wait_to_be_visible()
                self.home_page.HEADER_SUBSCRIBER.fill(subscriber)
                search_values.append(f"Абонент: '{subscriber}'")

        with allure.step(f"Выполнение поиска с главной страницы ({', '.join(search_values)})"):
            self.home_page.HEADER_SEARCH_BTN.click()

        with allure.step("Проверка перехода на форму расширенного поиска"):
            self.client_search_page.TITLE.wait_to_have_text("Поиск клиента", timeout=10000)
            self.client_search_page.CUSTOMER_NAME_INPUT.wait_to_be_visible()

        if clear_and_research:
            with allure.step("Очистка предзаполненных фильтров и выполнение поиска"):
                self.clear_all_filters()
                self.client_search_page.SEARCH_BTN.click()

    def clear_all_filters(self) -> None:
        self.client_search_page.TITLE.wait_to_be_visible()
        self.client_search_page.CUSTOMER_NAME_INPUT.wait_to_be_visible()
        self.client_search_page.CUSTOMER_STATUSES.clear_select()
        self.client_search_page.ACCOUNT_STATUSES.clear_select()
        self.client_search_page.CONTRACT_STATUS.clear_select()

    @allure.step("Поиск клиента")
    def search_client(
        self,
        customer_name: str = None,
        inn: str = None,
        account_number: str = None,
        agreement_number: str = None,
        document_series: str = None,
        document_number: str = None,
        customer_status: str = None,
        account_status: str = None,
        contract_status: str = None,
    ) -> None:
        self.clear_all_filters()
        if customer_name:
            self.client_search_page.CUSTOMER_NAME_INPUT.fill(customer_name)
        if inn:
            self.client_search_page.INN_INPUT.fill(inn)
        if account_number:
            self.client_search_page.ACCOUNT_NUM.fill(account_number)
        if agreement_number:
            self.client_search_page.CONTRACT_NUM.fill(agreement_number)
        if document_series:
            self.client_search_page.ID_DOCUMENT_SERIAL.fill(document_series)
        if document_number:
            self.client_search_page.ID_DOCUMENT_NUM.fill(document_number)
        if customer_status:
            self.client_search_page.CUSTOMER_STATUSES.select_by_value(customer_status, check=False)
        if account_status:
            self.client_search_page.ACCOUNT_STATUSES.select_by_value(account_status, check=False)
        if contract_status:
            self.client_search_page.CONTRACT_STATUS.select_by_value(contract_status, check=False)

        self.client_search_page.SEARCH_BTN.click()

    @allure.step("Проверка, что клиент не найден")
    def verify_client_not_found(self) -> None:
        self.client_search_page.FOUNDED_CLIENTS.not_to_be_visible(timeout=5000)

    def _verify_client_found(self, client: IndividualClient | OrganizationClient) -> None:
        if isinstance(client, IndividualClient):
            client_name = f"{client.sur_name} {client.first_name}"
            with allure.step(f"Проверка найденного клиента: {client_name}"):
                self.client_search_page.FOUNDED_CLIENTS.wait_to_be_visible(timeout=15000)
                self.client_search_page.FOUNDED_FIO[0].to_contain_text(client.sur_name)
                self.client_search_page.FOUNDED_FIO[0].to_contain_text(client.first_name)
                self.client_search_page.FOUNDED_CUSTOMER_TYPE[0].wait_to_have_text(client.type)
        else:
            with allure.step(f"Проверка найденного клиента: {client.customer_name}"):
                self.client_search_page.FOUNDED_CLIENTS.wait_to_be_visible(timeout=15000)
                self.client_search_page.FOUNDED_FIO[0].to_contain_text(client.customer_name)
                self.client_search_page.FOUNDED_CUSTOMER_TYPE[0].wait_to_have_text(client.type)

    @allure.step("Сменить ПП с формированием договора")
    def change_product_offer_with_contract(self, auto_contract: bool = True) -> None:
        with allure.step("Инициировать смену продукта"):
            self.locators.PRODUCTS_OPTIONS_OPEN_BTN[0].wait_to_be_enabled()
            self.locators.PRODUCTS_OPTIONS_OPEN_BTN[0].click()
            self.locators.LOAD_SPIN.not_to_be_visible(timeout=8000)
            self.locators.PRODUCTS_OPTIONS_CHANGE_MAIN_RODUCT_BTN.click()

        with allure.step("Выбрать продукт для замены"):
            self.change_product_form.SEARCH_BTN.wait_to_be_enabled()
            self.change_product_form.CHOSE_PRODUCT_BTN[0].click()
            self.change_product_form.CHOSE_PRODUCT_BTN[0].wait_to_be_enabled(timeout=8000)
            self.change_product_form.ADD_PRODUCT_BTN.click()

        with allure.step("Изменить данные формирования договора"):
            self.create_request_form.CHOOSE_AGREEMENT_BTN.wait_to_be_enabled(timeout=30000)
            self.create_request_form.CHOOSE_AGREEMENT_BTN.select_by_value(
                "Сформировать, факт согласования автоматически"
                if auto_contract
                else "Сформировать, факт согласования вручную"
            )
            self.create_request_form.SAVE_BTN.click()
