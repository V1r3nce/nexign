import datetime

import pytest
import allure
from playwright.sync_api import Page

from common.helpers.data_generator import generate_random_number, faker_ru, get_shifted_datetime
from common.time_helpers import delay
from models.address_info import BasicSystemAddress
from pages.locators.client_profile import ClientProfile
from pages.locators.client_search import ClientSearch
from pages.locators.dynamic_form_elements import FlCustomerCreate, CreateSalesAndServiceManagement, ClientChoice
from pages.locators.home_page_elements import HomePage


class TestManageAddressInfo1:
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.home_page = HomePage(page)
        self.customer_create_form = FlCustomerCreate(page)
        self.client_search_page = ClientSearch(page)
        self.create_request_form = CreateSalesAndServiceManagement(page)
        self.client_choice = ClientChoice(page)
        self.client_profile = ClientProfile(page)

    @allure.suite("E2E_64 Создание и управление клиентом и его иерархиями")
    @allure.title("Создание ФЛ клиента, заполнены все поля")
    @allure.id(484399)
    def test_fl_customer_create(self, base_url: str):
        start_date = datetime.date(1990, 1, 1)
        end_date = datetime.date(2020, 12, 31)

        last_name = f'автотесты-{faker_ru.last_name()}'
        first_name = f'автотесты-{faker_ru.first_name()}'
        document_serial = str(generate_random_number(4))
        document_num = str(generate_random_number(6))
        document_division_code = f"{generate_random_number(3)}-{generate_random_number(3)}"
        document_date = faker_ru.date_between(start_date, end_date).strftime('%d.%m.%Y')
        document_valid_date = faker_ru.date_between(datetime.datetime.today(),
                                                                   get_shifted_datetime("+500d")).strftime('%d.%m.%Y')
        birth_date = faker_ru.date_of_birth().strftime('%d.%m.%Y')
        birth_place = faker_ru.city()
        inn = str(generate_random_number(12))
        snils = str(generate_random_number(11))
        contact_phone = faker_ru.phone_number()
        contact_email = faker_ru.email()

        self.home_page.CREATE_CUSTOMER_BTN.click()
        self.customer_create_form.LAST_NAME.wait_to_be_visible()
        self.customer_create_form.fill_data_for_individual_client(last_name=last_name, first_name=first_name, document_serial=document_serial, document_num=document_num, document_division_code=document_division_code, document_date=document_date, document_valid_date=document_valid_date, birth_date=birth_date, birth_place=birth_place, inn=inn, snils=snils, contact_phone=contact_phone, contact_email=contact_email)
        self.customer_create_form.SAVE_BTN.click()
        self.customer_create_form.LAST_NAME.not_to_be_visible()

        self.client_profile.CLIENT_TAB.click()
        self.client_profile.CLIENT_FIO.to_contain_text('Автотестович')
        self.client_profile.GENDER.to_contain_text("Мужской")
        self.client_profile.DOCUMENT_TYPE.to_contain_text('Паспорт гражданина РФ')
        self.client_profile.DOCUMENT_SERIAL.to_contain_text(document_serial)
        self.client_profile.DOCUMENT_NUM.to_contain_text(document_num)
        self.client_profile.DOCUMENT_PROVIDE_BY.to_contain_text('ГУ МВД РОССИИ')
        self.client_profile.DOCUMENT_DIVISION_CODE.to_contain_text(document_division_code)
        self.client_profile.DOCUMENT_DATE.to_contain_text(document_date)
        self.client_profile.DOCUMENT_VALID_DATE.to_contain_text(document_valid_date)
        self.client_profile.BIRTH_DATE.to_contain_text(birth_date)
        self.client_profile.BIRTH_PLACE.to_contain_text(birth_place)
        self.client_profile.REGISTRATION_ADDRESS.to_contain_text(BasicSystemAddress.address)
        self.client_profile.INN.to_contain_text(inn)
        self.client_profile.SNILS.to_contain_text(snils)

        self.client_profile.RELATED_PERSONS_TAB.click()
        self.client_profile.RELATED_PERSONS.wait_elements_visible(0)
        self.client_profile.RELATED_PERSONS.to_contain_text(0, "Автотестович")
        self.client_profile.RELATED_MOBILE_PHONE.to_contain_text(contact_phone, clear_phone=True)
        self.client_profile.RELATED_EMAIL.to_contain_text(contact_email)

        self.home_page.HOME_BTN.click()
        self.home_page.INN.fill(inn)
        self.home_page.HEADER_SEARCH_BTN.click()

        self.client_search_page.FOUNDED_CLIENTS.not_to_be_visible()
        self.client_search_page.ACCOUNT_STATUSES.select_by_value("Действующий")
        delay(2, "Не успевает примениться фильтр")
        self.client_search_page.SEARCH_BTN.click()
        self.client_search_page.FOUNDED_CLIENTS.wait_to_be_visible()
        self.home_page.RIGHT_SIDE_BTN.to_have_count(5)
        self.home_page.RIGHT_SIDE_BTN.click(1)
        self.create_request_form.SELECT_CLIENT_BTN.select_by_value("Выбрать клиента")

        self.client_choice.INN.fill(inn)
        self.client_choice.FIND_BTN.click()

        self.client_choice.FOUNDED_CUSTOMER.wait_elements_visible(0)
        self.client_choice.FOUNDED_CUSTOMER.click(0)
        self.client_choice.INNER_ACCEPT_BTN.click()

        self.create_request_form.CLIENT.click()
        self.client_profile.RELATED_PERSONS_TAB.click()
        self.client_profile.RELATED_PERSONS.wait_elements_visible(0)
        self.client_profile.RELATED_PERSONS.to_contain_text(0, "Автотестович")
        self.client_profile.RELATED_MOBILE_PHONE.to_contain_text(contact_phone, clear_phone=True)
        self.client_profile.RELATED_EMAIL.to_contain_text(contact_email)
