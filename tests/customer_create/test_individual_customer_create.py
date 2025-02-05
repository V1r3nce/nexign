import datetime
import re
import time

import pytest
import allure
from playwright.sync_api import Page

from common.helpers.data_generator import generate_random_number, faker_ru, get_shifted_datetime
from common.helpers.time_helpers import delay
from models.address_info import BasicSystemAddress
from pages.locators.client_profile import ClientProfile
from pages.locators.client_search import ClientSearch
from pages.locators.dynamic_form_elements import IndividualCustomerCreate, CreateSalesAndServiceManagement, ClientChoice
from pages.locators.home_page_elements import HomePage
from pages.locators.inquiries_page import InquiriesPage, ProductEditForm
from pages.locators.select_product_offers_form import SelectProductOffersForm


@pytest.mark.usefixtures("nexign_ui_stand_login")
class TestIndividualCustomerCreate:
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.home_page = HomePage(page)
        self.customer_create_form = IndividualCustomerCreate(page)
        self.client_search_page = ClientSearch(page)
        self.create_request_form = CreateSalesAndServiceManagement(page)
        self.client_choice = ClientChoice(page)
        self.client_profile = ClientProfile(page)
        self.inquiries_page = InquiriesPage(page)
        self.product_offer_form = SelectProductOffersForm(page)
        self.product_edit_form = ProductEditForm(page)

    @allure.suite("E2E_64 Создание и управление клиентом и его иерархиями")
    @allure.title("Создание ФЛ клиента, заполнены все поля")
    @allure.tag("CAN_AUTH", "SUCCESS")
    @allure.description("Сценарий регистрация клиента B2C - ФЛ")
    @allure.id(484399)
    def test_individual_customer_create(self, base_url: str):
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

        with allure.step('Пользователь нажимает на "Создать клиента ФЛ"'):
            self.home_page.CREATE_CUSTOMER_BTN.click()
            self.customer_create_form.LAST_NAME.wait_to_be_visible()
        with allure.step('В открывшейся форме пользователь вводит данные клиента'):
            self.customer_create_form.fill_data_for_individual_client(
                last_name=last_name,
                first_name=first_name,
                document_serial=document_serial,
                document_num=document_num,
                document_division_code=document_division_code,
                document_date=document_date,
                document_valid_date=document_valid_date,
                birth_date=birth_date,
                birth_place=birth_place,
                inn=inn,
                snils=snils,
                contact_phone=contact_phone,
                contact_email=contact_email
            )
        with allure.step('Сохранить клиента'):
            allure.description("Форма заполнения данных закрывается, открывается форму клиентской карточки")
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

        with allure.step('Ищем клиента'):
            self.home_page.HOME_BTN.click()
            self.home_page.INN.fill(inn)
            self.home_page.HEADER_SEARCH_BTN.click()

            self.client_search_page.FOUNDED_CLIENTS.not_to_be_visible()
            self.client_search_page.ACCOUNT_STATUSES.select_by_value("Действующий")
            delay(2, "Не успевает примениться фильтр")
            self.client_search_page.SEARCH_BTN.click()
            self.client_search_page.FOUNDED_CLIENTS.wait_to_be_visible()

        with allure.step('Открываем форму продажи'):
            self.home_page.RIGHT_SIDE_BTN.wait_to_have_count(5)
            self.home_page.RIGHT_SIDE_BTN.click(1)
            self.create_request_form.SELECT_CLIENT_BTN.select_by_value("Выбрать клиента")

            self.client_choice.INN.fill(inn)
            self.client_choice.FIND_BTN.click()

            self.client_choice.FOUNDED_CUSTOMER.wait_elements_visible(0, timeout=10000)
            self.client_choice.FOUNDED_CUSTOMER.click(0)
            self.client_choice.INNER_ACCEPT_BTN.click()

        with allure.step('Проверка связанного лица'):
            self.create_request_form.CLIENT.click()
            self.client_profile.RELATED_PERSONS_TAB.click()
            self.client_profile.RELATED_PERSONS.wait_elements_visible(0)
            self.client_profile.RELATED_PERSONS.to_contain_text(0, "Автотестович")
            self.client_profile.RELATED_MOBILE_PHONE.to_contain_text(contact_phone, clear_phone=True)
            self.client_profile.RELATED_EMAIL.to_contain_text(contact_email)

    @allure.suite("E2E_64 Создание и управление клиентом и его иерархиями")
    @allure.title("Создание ФЛ клиента, заполняя только обязательные поля")
    @allure.tag("CAN_AUTH", "SUCCESS")
    @allure.description("Сценарий регистрация клиента B2C - ФЛ")
    @allure.id(484387)
    def test_individual_customer_create_only_required_fields(self, base_url: str):
        last_name = f'автотесты-{faker_ru.last_name()}'
        first_name = f'автотесты-{faker_ru.first_name()}'
        document_num = str(generate_random_number(6))
        birth_date = faker_ru.date_of_birth().strftime('%d.%m.%Y')
        document_serial = str(generate_random_number(4))

        with allure.step('Пользователь нажимает на "Создать клиента ФЛ"'):
            self.home_page.CREATE_CUSTOMER_BTN.click()
            self.customer_create_form.LAST_NAME.wait_to_be_visible()
        with allure.step('В открывшейся форме пользователь вводит данные клиента'):
            self.customer_create_form.fill_data_for_individual_client(
                only_required_fields=True,
                last_name=last_name,
                first_name=first_name,
                document_serial=document_serial,
                document_num=document_num,
                birth_date=birth_date,
            )
        with allure.step('Сохранить клиента'):
            allure.description("Форма заполнения данных закрывается, открывается форму клиентской карточки")
            self.customer_create_form.SAVE_BTN.click()
            self.customer_create_form.LAST_NAME.not_to_be_visible()

            self.client_profile.CLIENT_TAB.click()
            self.client_profile.CLIENT_FIO.to_contain_text('Автотестович')
            self.client_profile.GENDER.to_contain_text("Мужской")
            self.client_profile.DOCUMENT_TYPE.to_contain_text('Паспорт гражданина РФ')
            self.client_profile.DOCUMENT_NUM.to_contain_text(document_num)
            self.client_profile.DOCUMENT_PROVIDE_BY.wait_to_have_text('')
            self.client_profile.DOCUMENT_DIVISION_CODE.wait_to_have_text('')
            self.client_profile.DOCUMENT_DATE.wait_to_have_text('')
            self.client_profile.DOCUMENT_VALID_DATE.wait_to_have_text('')
            self.client_profile.BIRTH_DATE.to_contain_text(birth_date)
            self.client_profile.BIRTH_PLACE.wait_to_have_text('')
            self.client_profile.REGISTRATION_ADDRESS.to_contain_text(BasicSystemAddress.address)
            self.client_profile.INN.wait_to_have_text('')
            self.client_profile.SNILS.wait_to_have_text('')

            self.client_profile.RELATED_PERSONS_TAB.click()
            self.client_profile.RELATED_PERSONS.wait_elements_visible(0)
            self.client_profile.RELATED_PERSONS.to_contain_text(0, "Попробуйте уточнить запрос")

        with allure.step('Ищем клиента'):
            self.home_page.HOME_BTN.click()
            self.home_page.CUSTOMER_NAME.fill(last_name)
            self.home_page.HEADER_SEARCH_BTN.click()

            self.client_search_page.FOUNDED_CLIENTS.not_to_be_visible()
            self.client_search_page.ACCOUNT_STATUSES.select_by_value("Действующий")
            delay(2, "Не успевает примениться фильтр")
            self.client_search_page.SEARCH_BTN.click()
            self.client_search_page.FOUNDED_CLIENTS.wait_to_be_visible()

        with allure.step('Открываем форму продажи'):
            self.home_page.RIGHT_SIDE_BTN[0].wait_to_be_visible()
            self.home_page.RIGHT_SIDE_BTN.wait_to_have_count(5)
            self.home_page.RIGHT_SIDE_BTN.click(1)
            self.create_request_form.SELECT_CLIENT_BTN.select_by_value("Выбрать клиента")

            self.client_choice.CUSTOMER_NAME.fill(last_name)
            self.client_choice.FIND_BTN.click()

            self.client_choice.FOUNDED_CUSTOMER.wait_elements_visible(0, timeout=10000)
            self.client_choice.FOUNDED_CUSTOMER.click(0)
            self.client_choice.INNER_ACCEPT_BTN.click()

            self.create_request_form.EMAIL.wait_to_have_text('')
            self.create_request_form.PHONE.wait_to_have_text('')

        with allure.step('Проверка связанного лица'):
            self.create_request_form.CLIENT.click()
            self.client_profile.RELATED_PERSONS_TAB.click()
            self.client_profile.RELATED_PERSONS.wait_elements_visible(0)
            self.client_profile.RELATED_PERSONS.to_contain_text(0, "Попробуйте уточнить запрос")

    @allure.suite("E2E_64 Создание и управление клиентом и его иерархиями")
    @allure.title("Создание клиента документ регистрации клиента просрочен")
    @allure.tag("CAN_AUTH", "SUCCESS")
    @allure.description("Сценарий регистрация клиента B2C - ввод некорректных данных документа регистрации "
                        "(дата окончания в прошлом) клиент не может быть создан")
    @allure.id(484808)
    def test_individual_customer_create_document_out_of_date(self, base_url: str):
        last_name = f'автотесты-{faker_ru.last_name()}'
        first_name = f'автотесты-{faker_ru.first_name()}'
        document_num = str(generate_random_number(6))
        birth_date = faker_ru.date_of_birth().strftime('%d.%m.%Y')
        document_invalid_date = get_shifted_datetime("-1d").strftime('%d.%m.%Y')

        with allure.step('Пользователь нажимает на "Создать клиента ФЛ"'):
            self.home_page.CREATE_CUSTOMER_BTN.click()
            self.customer_create_form.LAST_NAME.wait_to_be_visible()
        with allure.step('В открывшейся форме пользователь вводит данные клиента'):
            self.customer_create_form.fill_data_for_individual_client(
                only_required_fields=True,
                last_name=last_name,
                first_name=first_name,
                document_num=document_num,
                birth_date=birth_date,
            )
            self.customer_create_form.DOCUMENT_VALID_DATE.fill(document_invalid_date)
        with allure.step('Сохранить клиента'):
            allure.description("Форма заполнения данных закрывается, открывается форму клиентской карточки")
            self.customer_create_form.SAVE_BTN.click()
            self.customer_create_form.MODAL.wait_to_have_count(1)
            self.customer_create_form.MODAL_TITLE[0].to_contain_text("Ошибка")
            self.customer_create_form.MODAL_BODY_TEXT[0].to_contain_text("Невозможно установить дату в прошлом")

    @allure.suite("E2E_64 Создание и управление клиентом и его иерархиями")
    @allure.title("Создание В2С ФЛ клиента заполняя все поля + продажа")
    @allure.tag("CAN_AUTH", "SUCCESS")
    @allure.description("Сценарий создания клиента ФЛ из процесса продажи (быстрое создание клиента)")
    @allure.id(479467)
    def test_create_individual_customer_from_process_sale(self, base_url: str):
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

        with allure.step('Пользователь нажал на кнопку создание продажи'):
            self.home_page.RIGHT_SIDE_BTN.wait_to_have_count(3, timeout=10000)
            self.home_page.RIGHT_SIDE_BTN.click(1)

        self.create_request_form.SELECT_CLIENT_BTN.select_by_value("Создать ФЛ")

        with allure.step('В открывшейся форме пользователь вводит данные клиента'):
            self.customer_create_form.fill_data_for_individual_client(
                last_name=last_name,
                first_name=first_name,
                document_serial=document_serial,
                document_num=document_num,
                document_division_code=document_division_code,
                document_date=document_date,
                document_valid_date=document_valid_date,
                birth_date=birth_date,
                birth_place=birth_place,
                inn=inn,
                snils=snils,
                contact_phone=contact_phone,
                contact_email=contact_email
            )
        with allure.step('Сохранить клиента'):
            self.customer_create_form.SAVE_BTN.click()
            self.customer_create_form.CUSTOMER_NAME.not_to_be_visible()

            self.create_request_form.CLIENT.to_contain_text(first_name)

        with allure.step('Заполнить контактные данные нажать на кнопку "сохранить"'):
            self.create_request_form.EMAIL.fill(contact_email)
            self.create_request_form.PHONE.fill(contact_phone)
            self.create_request_form.PRIORITY.select_by_value("Высокий")
            self.create_request_form.ADD_SALE_TYPE.select_by_value("Автоматически")

            self.create_request_form.SAVE_BTN.click()

        with allure.step('Создание продажи'):
            self.inquiries_page.INQUIRY_NAME.wait_to_have_text(re.compile(r"\d\. Продажа и управление услугами"))
            self.inquiries_page.INQUIRY_STATUS.wait_to_have_text("Обрабатывается")

            self.inquiries_page.LOAD_SPIN.not_to_be_visible(timeout=60000)
            self.inquiries_page.LOCATOR_SALE.wait_to_be_visible()

            self.inquiries_page.ADD_SALE_BTN.click()
            self.product_offer_form.PRODUCT_TYPE.select_by_value("Монопродукт")
            self.product_offer_form.PRODUCT_CATEGORY.select_by_value("Интернет")  # у ФЛ это мультичекбоксы
            self.product_offer_form.SEARCH_BTN.click()

            self.product_offer_form.PRODUCT_CARD.wait_to_have_count(1)
            self.product_offer_form.PRODUCT_CARD[0].to_contain_text("Скоростной Уют")
            self.product_offer_form.PRODUCT_CARD_SELECT_BTN[0].click()
            self.product_offer_form.ADD_BTN.click()

            self.inquiries_page.ADDED_PRODUCT.wait_to_have_count(1)
            self.inquiries_page.ADDED_PRODUCT[0].to_contain_text("Скоростной Уют")

            self.inquiries_page.ADDED_PRODUCT_ONE_TIME_PAYMENT[0].wait_to_be_visible()
            self.inquiries_page.ADDED_PRODUCT_SUBSCRIPTION_FEE[0].wait_to_be_visible()
            self.inquiries_page.INQUIRY_STATUS.wait_to_have_text("Обрабатывается")

            self.inquiries_page.ADDED_PRODUCT_EDIT_BTN[0].click(force=True)
            self.product_edit_form.SPECIFICATION_TAB.to_have_class(re.compile(r".+active"))
            self.product_edit_form.SPECIFICATION.wait_to_be_visible()

            self.product_edit_form.SERVICES_TAB.click()
            self.product_edit_form.SERVICES_TAB.to_have_class(re.compile(r".+active"))
            self.product_edit_form.SERVICES.wait_to_be_visible()

            self.product_edit_form.INNER_CANCEL_BTN.click()

            self.inquiries_page.CHECK_CONFIGURATION_BTN.click()
            self.inquiries_page.LOAD_SPIN.not_to_be_visible(timeout=60000)
            self.inquiries_page.PRODUCT_CHECK_STATUS.wait_to_be_visible(timeout=10000)
            self.inquiries_page.PRODUCT_CHECK_STATUS.wait_to_have_text('Продукты заказа настроены корректно.')

            self.inquiries_page.CHECK_TECHNICAL_FEASIBILITY_BTN.click()
            self.inquiries_page.LOAD_SPIN.not_to_be_visible(timeout=60000)
            self.inquiries_page.PRODUCT_CHECK_STATUS.wait_to_be_visible(timeout=10000)
            self.inquiries_page.PRODUCT_CHECK_STATUS.wait_to_have_text('Для всех продуктов заказа есть техническая возможность подключения. Для продолжения оформления продажи перейдите на следующий шаг, нажав на кнопку "Далее".')

            self.inquiries_page.REFRESH_BTN.click()
            self.inquiries_page.PRODUCT_CHECK_STATUS.wait_to_be_visible(timeout=10000)
            self.inquiries_page.PRODUCT_CHECK_STATUS.wait_to_have_text('Для всех продуктов заказа есть техническая возможность подключения. Для продолжения оформления продажи перейдите на следующий шаг, нажав на кнопку "Далее".')

            self.inquiries_page.NEXT_STEP_BTN.click()
            self.inquiries_page.LOAD_SPIN.not_to_be_visible(timeout=240000)

            self.inquiries_page.PRODUCT_INFO_STATUS.wait_to_have_text("Продажа успешно завершена", timeout=10000)

        with allure.step('Переходим на вкладку "Клиент" клиентской карточки'):
            self.inquiries_page.CLIENT.click()

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

        with allure.step('Ищем клиента'):
            self.home_page.HOME_BTN.click()
            self.home_page.INN.fill(inn)
            self.home_page.HEADER_SEARCH_BTN.click()

            self.client_search_page.FOUNDED_CLIENTS.not_to_be_visible()
            self.client_search_page.ACCOUNT_STATUSES.select_by_value("Действующий")
            delay(2, "Не успевает примениться фильтр")
            self.client_search_page.SEARCH_BTN.click()
            self.client_search_page.FOUNDED_CLIENTS.wait_to_be_visible()

        with allure.step('Открываем форму продажи'):
            self.home_page.RIGHT_SIDE_BTN.wait_to_have_count(5)
            self.home_page.RIGHT_SIDE_BTN.click(1)
            self.create_request_form.SELECT_CLIENT_BTN.select_by_value("Выбрать клиента")

            self.client_choice.INN.fill(inn)
            self.client_choice.FIND_BTN.click()

            self.client_choice.FOUNDED_CUSTOMER.wait_elements_visible(0, timeout=10000)
            self.client_choice.FOUNDED_CUSTOMER.click(0)
            self.client_choice.FOUNDED_FIO[0].to_contain_text(last_name)
            self.client_choice.INNER_ACCEPT_BTN.click()