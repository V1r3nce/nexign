import datetime
import re

import allure
import pytest
from playwright.sync_api import Page

from common.helpers.data_generator import faker_ru
from common.helpers.time_helpers import delay, get_shifted_datetime
from models.user import IndividualClient
from pages.inquiries_page import InquiriesPage
from pages.locators.client_profile import ClientProfile
from pages.locators.client_search import ClientSearch
from pages.locators.dynamic_form_elements import ClientChoice, CreateSalesAndServiceManagement, IndividualCustomerCreate
from pages.locators.home_page_elements import HomePage
from pages.locators.inquiries_elements import ProductEditForm
from pages.locators.select_product_offers_form import SelectProductOffersForm


@allure.suite("E2E_64 Создание и управление клиентом и его иерархиями")
@pytest.mark.regress
@pytest.mark.usefixtures("nexign_ui_stand_login")
class TestIndividualCustomerCreate:
    @pytest.fixture(autouse=True)
    def setup(self, page: Page, individual_user_data: IndividualClient) -> None:
        self.home_page = HomePage(page)
        self.customer_create_form = IndividualCustomerCreate(page)
        self.client_search_page = ClientSearch(page)
        self.create_request_form = CreateSalesAndServiceManagement(page)
        self.client_choice = ClientChoice(page)
        self.client_profile = ClientProfile(page)
        self.inquiries_page = InquiriesPage(page)
        self.product_offer_form = SelectProductOffersForm(page)
        self.product_edit_form = ProductEditForm(page)
        self.user = individual_user_data
        self.document_date = faker_ru.date_between(datetime.date(1990, 1, 1), datetime.date(2020, 12, 31)).strftime(
            "%d.%m.%Y"
        )
        self.document_valid_date = faker_ru.date_between(
            datetime.datetime.today(), get_shifted_datetime("+500d")
        ).strftime("%d.%m.%Y")

    @allure.title("Создание ФЛ клиента, заполнены все поля")
    @allure.description("Сценарий регистрация клиента B2C - ФЛ")
    @allure.id(484399)
    @pytest.mark.smoke
    def test_individual_customer_create(self, base_url: str) -> None:
        with allure.step('Пользователь нажимает на "Создать клиента ФЛ"'):
            self.home_page.CREATE_CUSTOMER_BTN.click()
            self.customer_create_form.LAST_NAME.wait_to_be_visible()
        with allure.step("В открывшейся форме пользователь вводит данные клиента"):
            self.customer_create_form.fill_data_for_individual_client(self.user)
        with allure.step("Сохранить клиента"):
            allure.description("Форма заполнения данных закрывается, открывается форму клиентской карточки")
            self.customer_create_form.SAVE_BTN.click()
            self.customer_create_form.LAST_NAME.not_to_be_visible()

            self.client_profile.CLIENT_TAB.click()
            self.client_profile.CLIENT_FIO.to_contain_text("Автотестович")
            self.client_profile.GENDER.to_have_value("Мужской")
            self.client_profile.DOCUMENT_TYPE.to_contain_text("Паспорт гражданина РФ")
            self.client_profile.DOCUMENT_SERIAL_AND_NUM.to_contain_text(self.user.document_serial)
            self.client_profile.DOCUMENT_SERIAL_AND_NUM.to_contain_text(self.user.document_num)
            self.client_profile.DOCUMENT_PROVIDE_BY.to_contain_text("ГУ МВД РОССИИ")
            self.client_profile.DOCUMENT_DIVISION_CODE.to_contain_text(self.user.document_division_code)
            self.client_profile.DOCUMENT_DATE.to_contain_text(self.document_date)
            self.client_profile.DOCUMENT_VALID_DATE.to_contain_text(self.document_valid_date)
            self.client_profile.BIRTH_DATE.to_contain_text(self.user.birth_date)
            self.client_profile.BIRTH_PLACE.to_contain_text(self.user.birth_place)
            self.client_profile.INN.to_contain_text(self.user.inn)
            self.client_profile.SNILS.to_contain_text(self.user.snils)

            self.client_profile.RELATED_PERSONS_TAB.click()
            self.client_profile.RELATED_PERSONS.wait_elements_visible(0)
            self.client_profile.RELATED_PERSONS.to_contain_text(0, "Автотестович")
            self.client_profile.RELATED_MOBILE_PHONE.to_contain_text(self.user.contact_phone, clear_phone=True)
            self.client_profile.RELATED_EMAIL.to_contain_text(self.user.contact_email)

        with allure.step("Ищем клиента"):
            self.home_page.HOME_BTN.click()
            self.home_page.INN.fill(self.user.inn)
            self.home_page.HEADER_SEARCH_BTN.click()

            self.client_search_page.FOUNDED_CLIENTS.not_to_be_visible()
            self.client_search_page.ACCOUNT_STATUSES.select_by_value("Действующий")
            self.client_search_page.CONTRACT_STATUS.select_by_value("Оформлен")
            delay(2, "Не успевает примениться фильтр")
            self.client_search_page.SEARCH_BTN.click()
            self.client_search_page.FOUNDED_CLIENTS.wait_to_be_visible()

        with allure.step("Открываем форму продажи"):
            self.home_page.RIGHT_SIDE_BTN.wait_to_have_count(4)
            self.home_page.RIGHT_SIDE_BTN.click(1)
            self.create_request_form.SELECT_CLIENT_BTN.select_by_value("Выбрать клиента")

            self.client_choice.INN.fill(self.user.inn)
            self.client_choice.FIND_BTN.click()

            self.client_choice.FOUNDED_CUSTOMER.wait_elements_visible(0, timeout=10000)
            self.client_choice.FOUNDED_CUSTOMER.click(0)
            self.client_choice.INNER_ACCEPT_BTN.click()

        with allure.step("Проверка связанного лица"):
            self.create_request_form.CLIENT.click()
            self.client_profile.RELATED_PERSONS_TAB.click()
            self.client_profile.RELATED_PERSONS.wait_elements_visible(0)
            self.client_profile.RELATED_PERSONS.to_contain_text(0, "Автотестович")
            self.client_profile.RELATED_MOBILE_PHONE.to_contain_text(self.user.contact_phone, clear_phone=True)
            self.client_profile.RELATED_EMAIL.to_contain_text(self.user.contact_email)

    @allure.title("Создание ФЛ клиента, заполняя только обязательные поля")
    @allure.description("Сценарий регистрация клиента B2C - ФЛ")
    @allure.id(484387)
    def test_individual_customer_create_only_required_fields(self, base_url: str) -> None:
        with allure.step('Пользователь нажимает на "Создать клиента ФЛ"'):
            self.home_page.CREATE_CUSTOMER_BTN.click()
            self.customer_create_form.LAST_NAME.wait_to_be_visible()
        with allure.step("В открывшейся форме пользователь вводит данные клиента"):
            self.customer_create_form.fill_data_for_individual_client(self.user, only_required_fields=True)
        with allure.step("Сохранить клиента"):
            allure.description("Форма заполнения данных закрывается, открывается форму клиентской карточки")
            self.customer_create_form.SAVE_BTN.click()
            self.customer_create_form.LAST_NAME.not_to_be_visible()

            self.client_profile.CLIENT_TAB.click()
            self.client_profile.CLIENT_FIO.to_contain_text("Автотестович")
            self.client_profile.GENDER.to_contain_text("Мужской")
            self.client_profile.DOCUMENT_TYPE.to_contain_text("Паспорт гражданина РФ")
            self.client_profile.DOCUMENT_SERIAL_AND_NUM.to_contain_text(self.user.document_num)
            self.client_profile.DOCUMENT_PROVIDE_BY.wait_to_have_text("")
            self.client_profile.DOCUMENT_DIVISION_CODE.wait_to_have_text("")
            self.client_profile.DOCUMENT_DATE.wait_to_have_text("")
            self.client_profile.DOCUMENT_VALID_DATE.wait_to_have_text("")
            self.client_profile.BIRTH_DATE.to_contain_text(self.user.birth_date)
            self.client_profile.BIRTH_PLACE.wait_to_have_text("")
            self.client_profile.INN.wait_to_have_text("")
            self.client_profile.SNILS.wait_to_have_text("")

            self.client_profile.RELATED_PERSONS_TAB.click()
            self.client_profile.RELATED_PERSONS.wait_elements_visible(0)
            self.client_profile.RELATED_PERSONS.to_contain_text(0, "Попробуйте уточнить запрос")

        with allure.step("Ищем клиента"):
            self.home_page.HOME_BTN.click()
            self.home_page.CUSTOMER_NAME.fill(self.user.sur_name)
            self.home_page.HEADER_SEARCH_BTN.click()

            self.client_search_page.FOUNDED_CLIENTS.not_to_be_visible()
            self.client_search_page.ACCOUNT_STATUSES.select_by_value("Действующий")
            self.client_search_page.CONTRACT_STATUS.select_by_value("Оформлен")
            delay(2, "Не успевает примениться фильтр")
            self.client_search_page.SEARCH_BTN.click()
            self.client_search_page.FOUNDED_CLIENTS.wait_to_be_visible()

        with allure.step("Открываем форму продажи"):
            self.home_page.RIGHT_SIDE_BTN[0].wait_to_be_visible()
            self.home_page.RIGHT_SIDE_BTN.wait_to_have_count(5)
            self.home_page.RIGHT_SIDE_BTN.click(1)
            self.create_request_form.SELECT_CLIENT_BTN.select_by_value("Выбрать клиента")

            self.client_choice.CUSTOMER_NAME.fill(self.user.sur_name)
            self.client_choice.FIND_BTN.click()

            self.client_choice.FOUNDED_CUSTOMER.wait_elements_visible(0, timeout=10000)
            self.client_choice.FOUNDED_CUSTOMER.click(0)
            self.client_choice.INNER_ACCEPT_BTN.click()

            self.create_request_form.EMAIL.wait_to_have_text("")
            self.create_request_form.PHONE.wait_to_have_text("")

        with allure.step("Проверка связанного лица"):
            self.create_request_form.CLIENT.click()
            self.client_profile.RELATED_PERSONS_TAB.click()
            self.client_profile.RELATED_PERSONS.wait_elements_visible(0)
            self.client_profile.RELATED_PERSONS.to_contain_text(0, "Попробуйте уточнить запрос")

    @allure.suite("E2E_64 Создание и управление клиентом и его иерархиями")
    @allure.title("Создание клиента документ регистрации клиента просрочен")
    @allure.tag("CAN_AUTH", "SUCCESS")
    @allure.description(
        "Сценарий регистрация клиента B2C - ввод некорректных данных документа регистрации "
        "(дата окончания в прошлом) клиент не может быть создан"
    )
    @allure.id(484808)
    @pytest.mark.regress
    def test_individual_customer_create_document_out_of_date(self, base_url: str) -> None:
        with allure.step('Пользователь нажимает на "Создать клиента ФЛ"'):
            self.home_page.CREATE_CUSTOMER_BTN.click()
            self.customer_create_form.LAST_NAME.wait_to_be_visible()
        with allure.step("В открывшейся форме пользователь вводит данные клиента"):
            self.customer_create_form.fill_data_for_individual_client(
                only_required_fields=True,
                last_name=self.user.sur_name,
                first_name=self.user.first_name,
                document_num=self.user.document_num,
                birth_date=self.user.birth_date,
            )
            self.customer_create_form.DOCUMENT_VALID_DATE.fill(self.user.document_invalid_date)
        with allure.step("Сохранить клиента"):
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
    @pytest.mark.regress
    def test_create_individual_customer_from_process_sale(self, base_url: str) -> None:
        with allure.step("Пользователь нажал на кнопку создание продажи"):
            self.home_page.RIGHT_SIDE_BTN.wait_to_have_count(3, timeout=10000)
            self.home_page.RIGHT_SIDE_BTN.click(1)

        self.create_request_form.SELECT_CLIENT_BTN.select_by_value("Создать ФЛ")

        with allure.step("В открывшейся форме пользователь вводит данные клиента"):
            self.customer_create_form.fill_data_for_individual_client(
                last_name=self.user.sur_name,
                first_name=self.user.first_name,
                document_serial=self.user.document_serial,
                document_num=self.user.document_num,
                document_division_code=self.user.document_division_code,
                document_date=self.document_date,
                document_valid_date=self.document_valid_date,
                birth_date=self.user.birth_date,
                birth_place=self.user.birth_place,
                inn=self.user.inn,
                snils=self.user.snils,
                contact_phone=self.user.contact_phone,
                contact_email=self.user.contact_email,
            )
        with allure.step("Сохранить клиента"):
            self.customer_create_form.SAVE_BTN.click()
            self.customer_create_form.CUSTOMER_NAME.not_to_be_visible()

            self.create_request_form.CLIENT.to_contain_text(self.user.first_name)

        with allure.step('Заполнить контактные данные нажать на кнопку "сохранить"'):
            self.create_request_form.EMAIL.fill(self.user.contact_email)
            self.create_request_form.PHONE.fill(self.user.contact_phone)
            self.create_request_form.PRIORITY.select_by_value("Высокий")
            self.create_request_form.ADD_SALE_TYPE.select_by_value("Автоматически")

            self.create_request_form.SAVE_BTN.click()

        with allure.step("Создание продажи"):
            self.inquiries_page.locators.INQUIRY_NAME.wait_to_have_text(
                re.compile(r"\d\. Продажа и управление услугами")
            )
            self.inquiries_page.locators.INQUIRY_STATUS.wait_to_have_text("Обрабатывается")

            self.inquiries_page.locators.LOAD_SPIN_FIRST.not_to_be_visible(timeout=60000)
            self.inquiries_page.locators.PRODUCT_INFO_STATUS.wait_to_be_visible()

            self.inquiries_page.locators.ADD_SALE_BTN.click()
            self.product_offer_form.PRODUCT_TYPE.select_by_value("Монопродукт")
            self.product_offer_form.PRODUCT_CATEGORY.select_by_value("Интернет")
            self.product_offer_form.SEARCH_BTN.click()

            self.product_offer_form.PRODUCT_CARD.wait_to_be_visible()
            self.product_offer_form.PRODUCT_CARD_SELECT_BTN[0].click()
            self.product_offer_form.ADD_BTN.click()

            self.inquiries_page.locators.ADDED_PRODUCT.wait_to_have_count(1)
            self.inquiries_page.locators.ADDED_PRODUCT[0].to_contain_text("Скоростной Уют")

            self.inquiries_page.locators.ADDED_PRODUCT_ONE_TIME_PAYMENT[0].wait_to_be_visible()
            self.inquiries_page.locators.ADDED_PRODUCT_SUBSCRIPTION_FEE[0].wait_to_be_visible()
            self.inquiries_page.locators.INQUIRY_STATUS.wait_to_have_text("Обрабатывается")

            self.inquiries_page.locators.ADDED_PRODUCT_EDIT_BTN[0].click(force=True)
            self.product_edit_form.SPECIFICATION_TAB.to_have_class(re.compile(r".+active"))
            self.product_edit_form.SPECIFICATION.wait_to_be_visible()

            self.product_edit_form.SERVICES_TAB.click()
            self.product_edit_form.SERVICES_TAB.to_have_class(re.compile(r".+active"))
            self.product_edit_form.SERVICES.wait_to_be_visible()

            self.product_edit_form.INNER_CANCEL_BTN.click()

            self.inquiries_page.locators.CHECK_CONFIGURATION_BTN.click()
            self.inquiries_page.locators.LOAD_SPIN_FIRST.not_to_be_visible(timeout=60000)
            self.inquiries_page.locators.PRODUCT_CHECK_STATUS.wait_to_be_visible(timeout=10000)
            self.inquiries_page.locators.PRODUCT_CHECK_STATUS.wait_to_have_text("Продукты заказа настроены корректно.")

            self.inquiries_page.locators.CHECK_TECHNICAL_FEASIBILITY_BTN.click()
            self.inquiries_page.locators.LOAD_SPIN_FIRST.not_to_be_visible(timeout=60000)
            self.inquiries_page.locators.PRODUCT_CHECK_STATUS.wait_to_be_visible(timeout=10000)
            self.inquiries_page.locators.PRODUCT_CHECK_STATUS.wait_to_have_text(
                'Для всех продуктов заказа есть техническая возможность подключения. Для продолжения оформления продажи перейдите на следующий шаг, нажав на кнопку "Далее".'
            )

            self.inquiries_page.locators.REFRESH_BTN.click()
            self.inquiries_page.locators.PRODUCT_CHECK_STATUS.wait_to_be_visible(timeout=10000)
            self.inquiries_page.locators.PRODUCT_CHECK_STATUS.wait_to_have_text(
                'Для всех продуктов заказа есть техническая возможность подключения. Для продолжения оформления продажи перейдите на следующий шаг, нажав на кнопку "Далее".'
            )

            self.inquiries_page.locators.NEXT_STEP_BTN.click()
            self.inquiries_page.locators.LOAD_SPIN_FIRST.not_to_be_visible(timeout=240000)

            self.inquiries_page.locators.PRODUCT_INFO_STATUS.wait_to_have_text("Успешно выполнено", timeout=10000)

        with allure.step('Переходим на вкладку "Клиент" клиентской карточки'):
            self.inquiries_page.locators.CLIENT.click()

            self.client_profile.CLIENT_TAB.click()
            self.client_profile.CLIENT_FIO.to_contain_text("Автотестович")
            self.client_profile.GENDER.to_contain_text("Мужской")
            self.client_profile.DOCUMENT_TYPE.to_contain_text("Паспорт гражданина РФ")
            self.client_profile.DOCUMENT_SERIAL_AND_NUM.to_contain_text(self.user.document_serial)
            self.client_profile.DOCUMENT_SERIAL_AND_NUM.to_contain_text(self.user.document_num)
            self.client_profile.DOCUMENT_PROVIDE_BY.to_contain_text("ГУ МВД РОССИИ")
            self.client_profile.DOCUMENT_DIVISION_CODE.to_contain_text(self.user.document_division_code)
            self.client_profile.DOCUMENT_DATE.to_contain_text(self.document_date)
            self.client_profile.DOCUMENT_VALID_DATE.to_contain_text(self.document_valid_date)
            self.client_profile.BIRTH_DATE.to_contain_text(self.user.birth_date)
            self.client_profile.BIRTH_PLACE.to_contain_text(self.user.birth_place)
            self.client_profile.INN.to_contain_text(self.user.inn)
            self.client_profile.SNILS.to_contain_text(self.user.snils)

            self.client_profile.RELATED_PERSONS_TAB.click()
            self.client_profile.RELATED_PERSONS.wait_elements_visible(0)
            self.client_profile.RELATED_PERSONS.to_contain_text(0, "Автотестович")
            self.client_profile.RELATED_MOBILE_PHONE.to_contain_text(self.user.contact_phone, clear_phone=True)
            self.client_profile.RELATED_EMAIL.to_contain_text(self.user.contact_email)

        with allure.step("Ищем клиента"):
            self.home_page.HOME_BTN.click()
            self.home_page.INN.fill(self.user.inn)
            self.home_page.HEADER_SEARCH_BTN.click()

            self.client_search_page.FOUNDED_CLIENTS.not_to_be_visible()
            self.client_search_page.ACCOUNT_STATUSES.select_by_value("Действующий")
            self.client_search_page.CONTRACT_STATUS.select_by_value("Оформлен")
            delay(2, "Не успевает примениться фильтр")
            self.client_search_page.SEARCH_BTN.click()
            self.client_search_page.FOUNDED_CLIENTS.wait_to_be_visible()

        with allure.step("Открываем форму продажи"):
            self.home_page.RIGHT_SIDE_BTN.wait_to_have_count(5)
            self.home_page.RIGHT_SIDE_BTN.click(1)
            self.create_request_form.SELECT_CLIENT_BTN.select_by_value("Выбрать клиента")

            self.client_choice.INN.fill(self.user.inn)
            self.client_choice.FIND_BTN.click()

            self.client_choice.FOUNDED_CUSTOMER.wait_elements_visible(0, timeout=10000)
            self.client_choice.FOUNDED_CUSTOMER.click(0)
            self.client_choice.FOUNDED_FIO[0].to_contain_text(self.user.sur_name)
            self.client_choice.INNER_ACCEPT_BTN.click()
