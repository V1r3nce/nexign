import allure
from playwright.sync_api import Page

from api.requests.client_requests import InfoAboutProduct
from common.helpers.checker import assert_that
from common.helpers.time_helpers import delay
from pages.base_page import BasePage
from pages.locators.client_profile import ClientProfile, ClientProfileEndUser, EditClientProfile, PersonalAccountForm
from pages.locators.dynamic_form_elements import (
    AddAddress,
    AddressCreate,
)


class ClientProfilePage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        self.locators = ClientProfile(page)
        self.add_address_form = AddAddress(page)
        self.create_address_form = AddressCreate(page)
        self.end_user_form = ClientProfileEndUser(page)
        self.edit_client_form = EditClientProfile(page)
        self.personal_account = PersonalAccountForm(page)

    @allure.step("Проверить, что баланс {index} ЛС равен {money} {currency}")
    def check_balance(self, index: int, money: float = 0.00, currency: str = "RUB") -> None:
        balance = f"{money:.2f} {currency}"
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
    def click_first_product(self, subscriber: str, product_name: str) -> None:
        self.locators.PRODUCTS_LIST.wait_elements_visible(0)
        self.locators.SUBSCRIBER[0].wait_to_have_text(subscriber)
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
    def check_all_products(self, products: list[InfoAboutProduct]) -> None:
        products_count = len(products)
        self.expand_all_products()
        self.locators.PRODUCTS.wait_to_have_count(products_count)
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
        self.locators.PRODUCTS_STATUS_COLOR.to_have_css_color("background-color", "green")

    @allure.step("Получить количество лимитов опций {index} продукта")
    def get_option_limit_count(self, index: int) -> int:
        return len(
            self.page.locator(self.locators.PRODUCTS.path).nth(index).locator(self.locators.OPTION_LIMIT_ICON.path).all()
        )

    @allure.step("Добавить конечного пользователя которого нет в системе")
    def add_non_existing_end_user(
        self,
        passport_series: str,
        passport_number: str,
        surname: str,
        name: str,
        patronymic: str,
        subdivision_code: str,
        document_date_of_issue: str,
        document_valid_for: str,
        birth_date: str,
    ) -> None:
        self.end_user_form.ADD_END_USER_BUTTON.click()
        self.end_user_form.DOCUMENT_TYPE_DROPDOWN.wait_to_be_visible()
        self.end_user_form.DOCUMENT_TYPE_DROPDOWN.select_by_value("Паспорт гражданина РФ")
        self.end_user_form.DOCUMENT_SERIES.fill(passport_series)
        self.end_user_form.DOCUMENT_NUMBER.fill(passport_number)
        self.end_user_form.ADD_END_USER_NEXT_BUTTON.click()

        self.end_user_form.SURNAME_INPUT.wait_to_be_visible()
        self.end_user_form.LOADER.not_to_be_visible()
        self.end_user_form.SURNAME_INPUT.fill(surname)
        self.end_user_form.NAME_INPUT.fill(name)
        self.end_user_form.PATRONYMIC_INPUT.fill(patronymic)
        self.end_user_form.GENDER_DROPDOWN.select_by_value("Мужской")
        self.end_user_form.WHO_ISSUED_THE_DOCUMENT_INPUT.fill("ГУ МВД РОССИИ")
        self.end_user_form.SUBDIVISION_CODE_INPUT.fill(subdivision_code)
        self.end_user_form.DATE_OF_ISSUE_INPUT.type(document_date_of_issue)
        self.press_keyboard_button("Enter")
        self.end_user_form.DOCUMENT_VALID_FOR_INPUT.type(document_valid_for)
        self.press_keyboard_button("Enter")
        self.end_user_form.PLACE_OF_BIRTH_INPUT.fill("Москва")
        self.end_user_form.BIRTHDAY_INPUT.type(birth_date)
        self.press_keyboard_button("Enter")
        self.end_user_form.REGISTRATION_ADDRESS_INPUT.select_by_value("Россия, Санкт-Петербург г., ул. Уральская")
        self.end_user_form.ADD_END_USER_NEXT_BUTTON.click()

    @allure.step("Добавить существующего конечного пользователя")
    def add_existing_end_user(self, passport_series: str, passport_number: str) -> None:
        self.end_user_form.ADD_END_USER_BUTTON.click()
        self.end_user_form.DOCUMENT_TYPE_DROPDOWN.wait_to_be_visible()
        self.end_user_form.DOCUMENT_TYPE_DROPDOWN.select_by_value("Паспорт гражданина РФ")
        self.end_user_form.DOCUMENT_SERIES.fill(passport_series)
        self.end_user_form.DOCUMENT_NUMBER.fill(passport_number)
        self.end_user_form.ADD_END_USER_NEXT_BUTTON.click()

        self.end_user_form.EXISTING_CLIENT_FOUND_TITLE.wait_to_be_visible()
        self.end_user_form.EXISTING_CLIENT_FOUND_TITLE.wait_to_have_text("Найден существующий клиент")
        self.end_user_form.CLIENT.click(0)
        self.end_user_form.ADD_END_USER_NEXT_BUTTON.click()
        self.end_user_form.DATA_TITLE.wait_to_have_text("Данные конечного пользователя")

    @allure.step("Проверить форму конечного пользователя")
    def check_end_user_form(
        self,
        surname: str,
        name: str,
        patronymic: str,
        gender: str,
        passport_series: str,
        passport_number: str,
        who_issued_the_document: str,
        subdivision_code: str,
        document_date_of_issue: str,
        document_valid_for: str,
        birth_date: str,
        country: str = "Россия",
        language: str = "Русский",
        is_public: str = "Нет",
        is_resident: str = "Да",
        place_of_birth: str = "Москва",
    ) -> None:
        self.end_user_form.LOADER.not_to_be_visible()
        self.end_user_form.FIO.to_contain_text(f"{surname} {name} {patronymic}")
        self.end_user_form.GENDER.to_contain_text(gender)
        self.end_user_form.DOCUMENT_TYPE.to_contain_text("Паспорт гражданина РФ")
        self.end_user_form.DOCUMENT_SERIES_AND_NUMBER.to_contain_text(f"{passport_series} {passport_number}")
        self.end_user_form.WHO_ISSUED_THE_DOCUMENT.to_contain_text(who_issued_the_document)
        self.end_user_form.SUBDIVISION_CODE.to_contain_text(subdivision_code)
        self.end_user_form.DATE_OF_ISSUE.to_contain_text(document_date_of_issue)
        self.end_user_form.DOCUMENT_VALID_FOR.to_contain_text(document_valid_for)
        self.end_user_form.PLACE_OF_BIRTH.to_contain_text(place_of_birth)
        self.end_user_form.BIRTH_DATE.to_contain_text(birth_date)
        self.end_user_form.COUNTRY.to_contain_text(country)
        self.end_user_form.LANGUAGE.to_contain_text(language)
        self.end_user_form.REGISTRATION_ADDRESS.to_contain_text("Россия, Санкт-Петербург г., ул. Уральская")
        self.end_user_form.IS_PUBLIC.to_contain_text(is_public)
        self.end_user_form.IS_RESIDENT.to_contain_text(is_resident)

    @allure.step("Проверить форму связанных лиц")
    def check_related_person(
        self,
        surname: str,
        name: str,
        patronymic: str,
        gender: str,
        passport_series: str,
        passport_number: str,
        who_issued_the_document: str,
        subdivision_code: str,
        document_date_of_issue: str,
        document_valid_for: str,
        birth_date: str,
        country: str = "Россия",
        language: str = "Русский",
        is_public: str = "Нет",
        is_resident: str = "Да",
        place_of_birth: str = "Москва",
        inn: str = "",
    ) -> None:
        self.locators.RELATED_PERSON_TABLE_NAME.to_contain_text(f"{surname} {name} {patronymic}")
        self.locators.RELATED_PERSON_GENDER.to_contain_text(gender)
        self.locators.RELATED_PERSON_TYPE_OF_DOCUMENT.to_contain_text("Паспорт гражданина РФ")
        self.locators.RELATED_PERSON_DOCUMENT_NUMBER.to_contain_text(f"{passport_series} {passport_number}")
        self.locators.RELATED_PERSON_WHO_ISSUED_THE_DOCUMENT.to_contain_text(who_issued_the_document)
        self.locators.RELATED_PERSON_SUBDIVISION_CODE.to_contain_text(subdivision_code)
        self.locators.RELATED_PERSON_DATE_OF_ISSUE.to_contain_text(document_date_of_issue)
        self.locators.RELATED_PERSON_VALID_FOR.to_contain_text(document_valid_for)
        self.locators.RELATED_PERSON_BIRTH_PLACE.to_contain_text(place_of_birth)
        self.locators.RELATED_PERSON_BIRTH_DATE.to_contain_text(birth_date)
        self.locators.RELATED_PERSON_COUNTRY.to_contain_text(country)
        self.locators.RELATED_SPEAKING_LANGUAGE.to_contain_text(language)
        self.locators.RELATED_PERSON_IS_PUBLIC.to_contain_text(is_public)
        self.locators.RELATED_PERSON_IS_RESIDENT.to_contain_text(is_resident)

        self.locators.RELATED_PERSON_INN.to_contain_text(inn)

        self.locators.RELATED_PERSON_CLIENT_FL.to_contain_text(f"{surname} {name} {patronymic}")
        self.locators.RELATED_PERSON_END_USER.to_contain_text("—")
