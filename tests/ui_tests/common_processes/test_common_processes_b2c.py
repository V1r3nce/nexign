import datetime
import re

import allure
import pytest
from playwright.sync_api import APIRequestContext, Page

from api.requests.client_requests import ClientRequests
from api.requests.payments_requests import PaymentInfo, PaymentsRequests
from api.requests.personal_account_requests import PersonalAccountRequests
from common.helpers.data_generator import faker_ru, generate_random_number, get_shifted_datetime
from common.helpers.time_helpers import delay
from models.user import IndividualUser
from pages.base_page import BasePage
from pages.client_profile_page import ClientProfilePage
from pages.inquiries_page import InquiriesPage
from pages.locators.dynamic_form_elements import (
    AddOptionsForm,
    CreateSalesAndServiceManagement,
    IndividualCustomerCreate,
)
from pages.locators.home_page_elements import HomePage
from pages.locators.inquiries_elements import ProductEditForm
from pages.locators.select_product_offers_form import SelectProductOffersForm
from pages.payments_page import PaymentsPage


@allure.epic("Общие бизнес-процессы")
@allure.suite("Общие бизнес-процессы")
class TestCommonBusinessProcessesB2C:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_ui_stand_login: Page, api_request_auth_context: APIRequestContext) -> None:
        self.base_page = BasePage(nexign_ui_stand_login)
        self.home_page = HomePage(nexign_ui_stand_login)
        self.customer_create_form = IndividualCustomerCreate(nexign_ui_stand_login)
        self.client_profile = ClientProfilePage(nexign_ui_stand_login)
        self.inquiries_page = InquiriesPage(nexign_ui_stand_login)
        self.create_request_form = CreateSalesAndServiceManagement(nexign_ui_stand_login)
        self.product_offer_form = SelectProductOffersForm(nexign_ui_stand_login)
        self.product_edit_form = ProductEditForm(nexign_ui_stand_login)
        self.payment_page = PaymentsPage(nexign_ui_stand_login)
        self.add_options_form = AddOptionsForm(nexign_ui_stand_login)
        self.personal_account_api = PersonalAccountRequests(api_request_auth_context)
        self.client_request_api = ClientRequests(api_request_auth_context)
        self.payment_api = PaymentsRequests(api_request_auth_context)
        self.user = IndividualUser

    @allure.title("БП Создание клиента B2C")
    @allure.tag("CAN_AUTH", "SUCCESS")
    @allure.description("Создание клиента B2C - физ. лица с добавлением адреса в справочник")
    @allure.id(584470)
    @pytest.mark.regress
    def test_individual_customer_create(self, base_url: str, add_new_address_to_lam: dict) -> None:
        start_date = datetime.date(1990, 1, 1)
        end_date = datetime.date(2020, 12, 31)
        document_date = faker_ru.date_between(start_date, end_date).strftime("%d.%m.%Y")
        document_valid_date = faker_ru.date_between(datetime.datetime.today(), get_shifted_datetime("+500d")).strftime(
            "%d.%m.%Y"
        )
        new_address = add_new_address_to_lam["addressString"]

        with allure.step('Пользователь нажимает на "Создать клиента ФЛ"'):
            self.home_page.CREATE_CUSTOMER_BTN.click()
            self.customer_create_form.LAST_NAME.wait_to_be_visible()
        with allure.step("В открывшейся форме пользователь вводит данные клиента"):
            self.customer_create_form.fill_data_for_individual_client(
                last_name=self.user.last_name,
                first_name=self.user.first_name,
                document_serial=self.user.document_serial,
                document_num=self.user.document_num,
                document_division_code=self.user.document_division_code,
                document_date=document_date,
                document_valid_date=document_valid_date,
                birth_date=self.user.birth_date,
                birth_place=self.user.birth_place,
                registration_address=new_address,
                inn=self.user.inn,
                snils=self.user.snils,
                contact_phone=self.user.contact_phone,
                contact_email=self.user.contact_email,
            )
        with allure.step("Сохранить клиента"):
            allure.description("Форма заполнения данных закрывается, открывается форму клиентской карточки")
            self.customer_create_form.SAVE_BTN.click()
            self.customer_create_form.LAST_NAME.not_to_be_visible()

            self.client_profile.locators.CLIENT_TAB.click()
            self.client_profile.locators.CLIENT_FIO.to_contain_text(
                f"{self.user.last_name} {self.user.first_name} Автотестович"
            )
            self.client_profile.locators.GENDER.to_have_value("Мужской")
            self.client_profile.locators.DOCUMENT_TYPE.to_contain_text("Паспорт гражданина РФ")
            self.client_profile.locators.DOCUMENT_SERIAL_AND_NUM.to_contain_text(self.user.document_serial)
            self.client_profile.locators.DOCUMENT_SERIAL_AND_NUM.to_contain_text(self.user.document_num)
            self.client_profile.locators.DOCUMENT_PROVIDE_BY.to_contain_text("ГУ МВД РОССИИ")
            self.client_profile.locators.DOCUMENT_DIVISION_CODE.to_contain_text(self.user.document_division_code)
            self.client_profile.locators.DOCUMENT_DATE.to_contain_text(document_date)
            self.client_profile.locators.DOCUMENT_VALID_DATE.to_contain_text(document_valid_date)
            self.client_profile.locators.BIRTH_DATE.to_contain_text(self.user.birth_date)
            self.client_profile.locators.BIRTH_PLACE.to_contain_text(self.user.birth_place)
            self.client_profile.locators.INN.to_contain_text(self.user.inn)
            self.client_profile.locators.SNILS.to_contain_text(self.user.snils)

            self.client_profile.locators.ADDRESSES_TAB.click()
            self.client_profile.locators.TABLE_ADDRESSES.to_contain_text(0, new_address)

    @allure.title("БП Добавление адреса в справочник")
    @allure.tag("CAN_AUTH", "SUCCESS")
    @allure.description("Добавление адреса в справочник в процессе создания клиента")
    @allure.id(584473)
    @pytest.mark.regress
    def test_individual_customer_add_address(self, base_url: str) -> None:
        start_date = datetime.date(1990, 1, 1)
        end_date = datetime.date(2020, 12, 31)
        document_date = faker_ru.date_between(start_date, end_date).strftime("%d.%m.%Y")
        document_valid_date = faker_ru.date_between(datetime.datetime.today(), get_shifted_datetime("+500d")).strftime(
            "%d.%m.%Y"
        )
        building_number = generate_random_number(3)
        flat_number = generate_random_number(2)
        new_address = f"Россия, Самарская обл., г. Самара, ул. Осипенко, д. {building_number}, кв. {flat_number}"

        with allure.step('Пользователь нажимает на "Создать клиента ФЛ"'):
            self.home_page.CREATE_CUSTOMER_BTN.click()
            self.customer_create_form.LAST_NAME.wait_to_be_visible()
        with allure.step("В открывшейся форме пользователь вводит данные клиента"):
            self.customer_create_form.fill_data_for_individual_client(
                last_name=self.user.last_name,
                first_name=self.user.first_name,
                document_serial=self.user.document_serial,
                document_num=self.user.document_num,
                document_division_code=self.user.document_division_code,
                document_date=document_date,
                document_valid_date=document_valid_date,
                birth_date=self.user.birth_date,
                birth_place=self.user.birth_place,
                registration_address="Россия",
                inn=self.user.inn,
                snils=self.user.snils,
                contact_phone=self.user.contact_phone,
                contact_email=self.user.contact_email,
            )
        self.customer_create_form.REGISTRATION_ADDRESS_CROSS.click()
        self.customer_create_form.REGISTRATION_ADDRESS.open_dropdown()
        self.client_profile.add_address_form.ADD_ADDRESS_TO_CATALOG.to_contain_text("Добавить адрес в справочник")
        self.client_profile.add_address_form.ADD_ADDRESS_TO_CATALOG.click()

        self.client_profile.fill_client_new_address(
            country="Россия",
            region="Самарская",
            city="Самара",
            street="Осипенко",
            building_number=building_number,
            flat_number=flat_number,
        )

        self.client_profile.create_address_form.ADD_ADDRESS_OBJECT_BTN.not_to_be_visible()
        self.client_profile.create_address_form.CREATE_BTN.click()
        self.client_profile.create_address_form.TITLE.not_to_be_visible()

        with allure.step("Сохранить клиента"):
            allure.description("Форма заполнения данных закрывается, открывается форму клиентской карточки")
            self.customer_create_form.SAVE_BTN.click()
            self.customer_create_form.LAST_NAME.not_to_be_visible()

            self.client_profile.locators.CLIENT_TAB.click()
            self.client_profile.locators.CLIENT_FIO.to_contain_text(
                f"{self.user.last_name} {self.user.first_name} Автотестович"
            )
            self.client_profile.locators.GENDER.to_have_value("Мужской")
            self.client_profile.locators.DOCUMENT_TYPE.to_contain_text("Паспорт гражданина РФ")
            self.client_profile.locators.DOCUMENT_SERIAL_AND_NUM.to_contain_text(self.user.document_serial)
            self.client_profile.locators.DOCUMENT_SERIAL_AND_NUM.to_contain_text(self.user.document_num)
            self.client_profile.locators.DOCUMENT_PROVIDE_BY.to_contain_text("ГУ МВД РОССИИ")
            self.client_profile.locators.DOCUMENT_DIVISION_CODE.to_contain_text(self.user.document_division_code)
            self.client_profile.locators.DOCUMENT_DATE.to_contain_text(document_date)
            self.client_profile.locators.DOCUMENT_VALID_DATE.to_contain_text(document_valid_date)
            self.client_profile.locators.BIRTH_DATE.to_contain_text(self.user.birth_date)
            self.client_profile.locators.BIRTH_PLACE.to_contain_text(self.user.birth_place)
            self.client_profile.locators.INN.to_contain_text(self.user.inn)
            self.client_profile.locators.SNILS.to_contain_text(self.user.snils)

            self.client_profile.locators.ADDRESSES_TAB.click()
            self.client_profile.locators.TABLE_ADDRESSES.to_contain_text(0, new_address)

    @allure.title("БП Продажа продукта клиенту B2C")
    @allure.tag("CAN_AUTH", "SUCCESS")
    @allure.description("Продажа продуктового предложения клиенту B2C")
    @allure.id(584471)
    @pytest.mark.regress
    def test_b2c_sale(self, base_url: str, create_user: int) -> None:
        new_client_id = create_user

        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{new_client_id}/overview")

        with allure.step("Пользователь нажал на кнопку создание продажи"):
            self.home_page.RIGHT_SIDE_BTN.wait_to_have_count(4, timeout=10000)
            self.home_page.RIGHT_SIDE_BTN.click(1)

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
            self.inquiries_page.locators.PRODUCT_INFO_STATUS.wait_to_be_visible(timeout=10000)

            self.inquiries_page.locators.ADD_SALE_BTN.click()
            self.product_offer_form.PRODUCT_TYPE.select_by_value("Монопродукт")
            self.product_offer_form.PRODUCT_CATEGORY.select_by_value("Мобильная связь")
            self.product_offer_form.SEARCH_BTN.click()

            with allure.step("В появившемся списке монопродуктов нажать кнопку 'Выбрать' у подходящего продукта"):
                self.product_offer_form.PRODUCT_CARD.wait_elements_visible(0)
                product_name = self.product_offer_form.PRODUCT_CARD_NAME[0].text
                product_sum = self.product_offer_form.PRODUCT_CARD_SUMS[0].text.split(".")[0]
                self.product_offer_form.PRODUCT_CARD_SELECT_BTN[0].click()
            self.product_offer_form.PRODUCT_CARD_SELECT_BTN[0].wait_to_have_text("Удалить")
            self.product_offer_form.ADD_BTN.click()

            self.inquiries_page.locators.ADDED_PRODUCT.wait_to_have_count(1, timeout=20000)
            self.inquiries_page.locators.STEP_TITLE.wait_to_have_text("Наполнение и уточнение коммерческого заказа")
            self.inquiries_page.locators.INQUIRY_STATUS.wait_to_have_text("Обрабатывается")
            self.inquiries_page.locators.INQUIRY_STEP.wait_to_have_text("Управление составом заказа")
            self.inquiries_page.locators.TABS[0].check_attribute_by_value("aria-selected", "true")
            self.inquiries_page.locators.CHECK_CONFIGURATION_BTN.wait_to_be_enabled()

            self.inquiries_page.locators.ADDED_PRODUCT_ONE_TIME_PAYMENT[0].wait_to_be_visible()
            self.inquiries_page.locators.ADDED_PRODUCT_SUBSCRIPTION_FEE[0].wait_to_be_visible()

            self.inquiries_page.locators.ADDED_PRODUCT_EDIT_BTN[0].click(force=True)
            self.product_edit_form.RESOURCES_TAB.click()
            self.inquiries_page.auto_reserve_phone_number_resources()

            self.product_edit_form.INNER_CANCEL_BTN.click()

            self.inquiries_page.locators.CHECK_CONFIGURATION_BTN.click()
            self.inquiries_page.locators.LOAD_SPIN_FIRST.not_to_be_visible(timeout=60000)
            self.inquiries_page.locators.PRODUCT_CHECK_STATUS.wait_to_be_visible(timeout=10000)
            self.inquiries_page.locators.PRODUCT_CHECK_STATUS.wait_to_have_text(
                'Продукты заказа настроены корректно. Для продолжения продажи перейдите на следующий шаг, нажав на кнопку "Далее"'
            )

            self.inquiries_page.locators.NEXT_STEP_BTN.click()
            self.inquiries_page.locators.INQUIRY_STEP.wait_to_have_text(
                "Автоматическое управление Договором/ДС и ЛС", timeout=240000
            )
            self.inquiries_page.locators.LOAD_SPIN_STATUS_NAME_1.wait_to_have_text(
                'Происходит автоматическое выполнение этапа "Договор/ДС"', timeout=240000
            )
            self.inquiries_page.locators.LOAD_SPIN_HELP_TEXT_1.wait_to_have_text(
                "После этого будет автоматически выполнен переход на следующий шаг"
            )
            self.inquiries_page.locators.INQUIRY_STEP.wait_to_have_text("Управление продуктами", timeout=240000)
            self.inquiries_page.locators.LOAD_SPIN_STATUS_NAME_2.wait_to_have_text(
                re.compile(r"Выполняется технический заказ № \d{1,6} на управление продуктами клиента"), timeout=240000
            )
            self.inquiries_page.locators.LOAD_SPIN_HELP_TEXT_2.wait_to_have_text(
                "После завершения будет автоматически выполнен переход на следующий шаг"
            )
            self.inquiries_page.locators.LOAD_SPIN_FIRST.not_to_be_visible(timeout=240000)
            self.inquiries_page.locators.PRODUCT_INFO_STATUS.wait_to_have_text("Успешно выполнено", timeout=10000)

        with allure.step("Проверка вкладки 'Элементы заказа'"):
            self.inquiries_page.locators.TABS[1].click()
            self.inquiries_page.locators.TABS[1].check_attribute_by_value("aria-selected", "true")
            self.inquiries_page.locators.LOAD_SPIN_FIRST.not_to_be_visible(timeout=10000)
            self.inquiries_page.locators.PRODUCTS_CONTRACT_NUM.wait_to_be_visible()
            accounts = self.personal_account_api.get_personal_accounts("customer", new_client_id).json()["items"]
            account_id = accounts[0]["accountNumber"]
            self.inquiries_page.locators.PRODUCTS_NAME[0].wait_to_have_text(product_name)
            contact_num = self.inquiries_page.locators.PRODUCTS_CONTRACT_NUM[0].text
            self.inquiries_page.locators.PRODUCTS_PERSONAL_ACCOUNT_NUM[0].wait_to_have_text(str(account_id))
            self.inquiries_page.locators.PRODUCTS_SUBSCRIPTION_FEE[0].to_contain_text(f"{product_sum}.00")

        with allure.step('Перейти в карточку клиента Открыть вкладку "Продукты"'):
            self.inquiries_page.locators.CLIENT.click()

            self.client_profile.locators.PRODUCTS_TAB.click()
            self.client_profile.locators.PRODUCTS.wait_to_be_visible()
            self.client_profile.locators.PRODUCTS[0].to_contain_text("Действует с")
            self.client_profile.locators.PRODUCTS_CONTRACT_NUM[0].to_contain_text(contact_num)
            self.client_profile.locators.PRODUCTS_PERSONAL_ACCOUNT_NUM[0].to_contain_text(str(account_id))
            self.client_profile.locators.PRODUCTS_SUBSCRIPTION_FEE[0].to_contain_text(f"{product_sum}.00")
            self.client_profile.locators.PRODUCTS_STATUS_COLOR[0].element_have_css_color("background-color", "yellow")

    @allure.title("БП Активация продукта")
    @allure.tag("CAN_AUTH", "SUCCESS")
    @allure.description("БП Активация продукта")
    @allure.id(584472)
    @pytest.mark.regress
    def test_product_activation(self, base_url: str, create_user: int) -> None:
        clients = self.client_request_api.search_client(
            account_status_ids=[2], agreement_status_ids=[1], customer_status_ids=[2], customer_name="Авто"
        )
        client_data = self.personal_account_api.get_client_product_with_status(clients, "INACTIVE")
        account_id = self.personal_account_api.get_personal_accounts(
            entity_code="customer", entity_id=client_data.customer_id
        ).json()["items"][0]["accountId"]
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{client_data.customer_id}/overview")
        self.client_profile.locators.PRODUCTS_TAB.click()
        self.client_profile.locators.PRODUCTS.wait_to_be_visible()
        self.client_profile.locators.PRODUCTS_STATUS_COLOR[0].element_have_css_color("background-color", "yellow")
        self.personal_account_api.wait_check_current_main_balance(account_id, 0)

        with allure.step(f"Добавление платежа для ЛС {account_id}"):
            payment_data = PaymentInfo(
                document_number=generate_random_number(4),
                item_type="CUSTOMER_ACCOUNT",
                account_id=account_id,
                payment_method_type="CASH",
                currency_code="RUB",
                amount=client_data.product_amount + 100,
            )
            self.payment_api.wait_check_create_payment(payment_data)
            self.payment_api.create_payment(payment_data)
            self.payment_api.wait_last_payment_successful(account_id)
            self.personal_account_api.wait_check_current_main_balance(account_id, client_data.product_amount + 100)
        self.inquiries_page.locators.CLIENT.click()
        self.client_profile.locators.CURRENT_PERSONAL_ACCOUNT_LINK.click()
        delay(1, reason="Время для смены контекста и содержания меню")
        self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Платежи")

        self.payment_page.locators.CHECK_NUM_FIELDS.wait_to_be_visible()
        self.payment_page.locators.USER_BALANCE.wait_to_have_text("100.00", timeout=20000)

        self.inquiries_page.locators.CLIENT.click()
        self.client_profile.locators.PRODUCTS_TAB.click()
        self.client_profile.locators.PRODUCTS.wait_to_be_visible()
        self.client_profile.locators.PRODUCTS_STATUS_COLOR[0].element_have_css_color("background-color", "green")

    @allure.title("БП Отключение ПП")
    @allure.tag("CAN_AUTH", "SUCCESS")
    @allure.description(
        'Отключение продуктового предложения у абонента в продуктовом профиле клиента на вкладке "По абонентам" '
    )
    @allure.id(585790)
    @pytest.mark.regress
    @pytest.mark.smoke
    def test_turn_off_pp(self, base_url: str, create_user: int) -> None:
        new_client_id = create_user
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{new_client_id}/overview")
        client, product = self.client_request_api.product_sale(new_client_id)

        account_id = self.personal_account_api.get_personal_accounts(
            entity_code="customer", entity_id=new_client_id
        ).json()["items"][0]["accountId"]
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{new_client_id}/overview")

        with allure.step(f"Добавление платежа для ЛС {account_id}"):
            payment_data = PaymentInfo(
                document_number=generate_random_number(4),
                item_type="CUSTOMER_ACCOUNT",
                account_id=account_id,
                payment_method_type="CASH",
                currency_code="RUB",
                amount=400,
            )
            self.payment_api.wait_check_create_payment(payment_data)
            self.payment_api.create_payment(payment_data)
            self.payment_api.wait_last_payment_successful(account_id)
            self.personal_account_api.wait_check_current_main_balance(account_id, 400)
        self.client_profile.locators.CURRENT_PERSONAL_ACCOUNT_LINK.click()
        delay(1, reason="Время для смены контекста и содержания меню")
        self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Платежи")

        self.payment_page.locators.CHECK_NUM_FIELDS.wait_to_be_visible()
        self.payment_page.locators.USER_BALANCE.wait_to_have_text("100.00", timeout=20000)

        self.inquiries_page.locators.CLIENT.click()
        self.client_profile.locators.PRODUCTS_TAB.click()
        self.client_profile.locators.PRODUCTS.wait_to_be_visible()
        self.client_profile.locators.PRODUCTS_STATUS_COLOR[0].element_have_css_color("background-color", "green")

        self.client_profile.locators.PRODUCTS_DETAILS_OPEN_BTN.hover()
        self.client_profile.locators.TURN_OFF_BTN.click()
        self.client_profile.locators.MODAL_TITLE.wait_to_have_text(
            re.compile(r"Будет отключен выбранный продукт и все его зависимые продукты и опции \(при наличии\)")
        )
        self.client_profile.locators.FIRST_BTN.to_contain_text("Отмена")
        self.client_profile.locators.SECOND_BTN.to_contain_text("Отключить")
        self.client_profile.locators.SECOND_BTN.click()
        self.client_profile.locators.INFO_MESSAGE.wait_to_have_text(
            re.compile(
                r"Заявка на отключение продукта клиента №\d{1,6} создана. Обновите форму и учтите установленные фильтры"
            )
        )
        self.client_profile.locators.INFO_MESSAGE_LINK.click()

        self.inquiries_page.locators.INQUIRY_STATUS.wait_to_have_text("Обрабатывается")
        self.inquiries_page.locators.TABS[0].check_attribute_by_value("aria-selected", "true")

        with allure.step("Дождаться изменения шага на Завершение"):
            self.inquiries_page.locators.LOAD_SPIN_SECOND.not_to_be_visible(timeout=80000)
            self.inquiries_page.locators.SUCCESS_SETUP.wait_to_be_visible()

        with allure.step("Проверка вкладки 'Элементы заказа'"):
            self.inquiries_page.locators.TABS.wait_to_be_visible()
            self.inquiries_page.locators.TABS[1].click()
            self.inquiries_page.locators.TABS[1].check_attribute_by_value("aria-selected", "true")
            self.inquiries_page.locators.PRODUCTS_NAME[0].wait_to_have_text(product.product_name)
            self.inquiries_page.locators.PRODUCTS_STATUS.wait_to_have_text("Отключение")

        self.inquiries_page.locators.TABS[0].click()
        self.inquiries_page.locators.TABS[0].check_attribute_by_value("aria-selected", "true")
        self.inquiries_page.locators.PRODUCT_PROFILE_BTN.click()

        with allure.step("Проверка вкладки 'Продукты'"):
            self.client_profile.locators.PRODUCTS_LIST.wait_to_have_count(1)
            self.client_profile.locators.SUBSCRIBER[0].wait_to_have_text(product.phone_number)
            self.client_profile.locators.PRODUCTS_LIST_STATUS_COLOR.element_have_css_color(
                "background-color", "moon_white"
            )
            self.client_profile.locators.PRODUCT_NAME.wait_not_to_be_visible()
