import re

import allure
import pytest

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from api.nbss.client_requests.client_requests import ClientRequests
from api.nbss.finances.payments_requests import PaymentsRequests
from api.nbss.inquiry_requests import AppealRequests
from api.nbss.personal_account_requests import PersonalAccountRequests
from common.helpers.data_generator import generate_random_number
from models.address_info import AddressInfo
from models.client import IndividualClient
from models.context import test_context
from pages.base_page import BasePage
from pages.locators.nbss.dynamic_form_elements import CreateSalesAndServiceManagement, IndividualCustomerCreate
from pages.locators.nbss.home_page_elements import HomePageElements
from pages.locators.nbss.inquiries_elements import ProductEditForm
from pages.locators.nbss.select_product_offers_form import SelectProductOffersFormElements
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.finances.payments_page import PaymentsPage
from pages.nbss.inquiries_page import InquiriesPage


@allure.epic("Общие бизнес-процессы")
@allure.suite("Общие бизнес-процессы")
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestCommonBusinessProcessesB2C:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login, individual_user_data: IndividualClient) -> None:
        self.base_page = BasePage()
        self.home_page = HomePageElements()
        self.customer_create_form = IndividualCustomerCreate()
        self.client_profile = ClientProfilePage()
        self.inquiries_page = InquiriesPage()
        self.create_request_form = CreateSalesAndServiceManagement()
        self.product_offer_form = SelectProductOffersFormElements()
        self.product_edit_form = ProductEditForm()
        self.payment_page = PaymentsPage()
        self.personal_account_api = PersonalAccountRequests()
        self.client_api = ClientRequests()
        self.client_request_api = ClientInquiriesRequests()
        self.inquiries_api = AppealRequests()
        self.payment_api = PaymentsRequests()
        self.user = individual_user_data

    @allure.title("БП Создание клиента B2C")
    @allure.description("Создание клиента B2C - физ. лица с добавлением адреса в справочник")
    @allure.id(584470)
    @pytest.mark.sanity
    def test_individual_customer_create(self, base_url: str, add_new_address_to_lam: dict) -> None:
        new_address = add_new_address_to_lam["addressString"]

        with allure.step('Пользователь нажимает на "Создать клиента ФЛ"'):
            self.home_page.CREATE_CUSTOMER_BTN.click()
            self.customer_create_form.LAST_NAME.wait_to_be_visible()
        self.user.registration_address = new_address
        with allure.step("В открывшейся форме пользователь вводит данные клиента"):
            self.customer_create_form.fill_data_for_individual_client(self.user)
        with allure.step("Сохранить клиента"):
            allure.description("Форма заполнения данных закрывается, открывается форму клиентской карточки")
            self.customer_create_form.SAVE_BTN.click()
            self.customer_create_form.LAST_NAME.not_to_be_visible(timeout=15000)

            self.client_profile.locators.CLIENT_TAB.click()
            self.client_profile.locators.CLIENT_FIO.to_contain_text(
                f"{self.user.sur_name} {self.user.first_name} {self.user.patronymic}"
            )
            self.client_profile.locators.GENDER.to_have_value(self.user.gender)
            self.client_profile.locators.DOCUMENT_TYPE.to_contain_text(self.user.document_type)
            self.client_profile.locators.DOCUMENT_SERIAL_AND_NUM.to_contain_text(self.user.document_serial)
            self.client_profile.locators.DOCUMENT_SERIAL_AND_NUM.to_contain_text(self.user.document_num)
            self.client_profile.locators.DOCUMENT_PROVIDE_BY.to_contain_text(self.user.document_provide_by)
            self.client_profile.locators.DOCUMENT_DIVISION_CODE.to_contain_text(self.user.document_division_code)
            self.client_profile.locators.DOCUMENT_DATE.to_contain_text(self.user.document_date)
            self.client_profile.locators.DOCUMENT_VALID_DATE.to_contain_text(self.user.document_valid_date)
            self.client_profile.locators.BIRTH_DATE.to_contain_text(self.user.birth_date)
            self.client_profile.locators.BIRTH_PLACE.to_contain_text(self.user.birth_place)
            self.client_profile.locators.INN.to_contain_text(self.user.inn)
            self.client_profile.locators.SNILS.to_contain_text(self.user.snils)

            self.client_profile.locators.ADDRESSES_TAB.click()
            self.client_profile.locators.TABLE_ADDRESSES.to_contain_text(0, new_address)

    @allure.title("БП Добавление адреса в справочник")
    @allure.description("Добавление адреса в справочник в процессе создания клиента")
    @allure.id(584473)
    @pytest.mark.sanity
    def test_individual_customer_add_address(self, base_url: str) -> None:
        building_number = generate_random_number(3)
        flat_number = generate_random_number(2)
        new_address = f"{AddressInfo().country}, {AddressInfo().region}, {AddressInfo().city}, {AddressInfo().street}, д. {building_number}, кв. {flat_number}"

        with allure.step('Пользователь нажимает на "Создать клиента ФЛ"'):
            self.home_page.CREATE_CUSTOMER_BTN.click()
            self.customer_create_form.LAST_NAME.wait_to_be_visible()
        with allure.step("В открывшейся форме пользователь вводит данные клиента"):
            self.customer_create_form.fill_data_for_individual_client(self.user)
        self.customer_create_form.REGISTRATION_ADDRESS_CROSS.click()
        self.customer_create_form.REGISTRATION_ADDRESS.open_dropdown()
        self.client_profile.add_address_form.ADD_ADDRESS_TO_CATALOG.to_contain_text("Добавить адрес в справочник")
        self.client_profile.add_address_form.ADD_ADDRESS_TO_CATALOG.click()

        self.client_profile.fill_client_new_address(
            country=AddressInfo().country,
            region=AddressInfo().region,
            city=AddressInfo().city,
            street=AddressInfo().street,
            building_number=building_number,
            flat_number=flat_number,
        )

        self.client_profile.create_address_form.ADD_ADDRESS_OBJECT_BTN.not_to_be_visible()
        self.client_profile.create_address_form.CREATE_BTN.click()
        self.client_profile.create_address_form.TITLE.not_to_be_visible()

        with allure.step("Сохранить клиента"):
            allure.description("Форма заполнения данных закрывается, открывается форму клиентской карточки")
            self.customer_create_form.SAVE_BTN.click()
            self.customer_create_form.LAST_NAME.not_to_be_visible(timeout=15000)

            self.client_profile.locators.CLIENT_TAB.click()
            self.client_profile.locators.CLIENT_FIO.to_contain_text(
                f"{self.user.sur_name} {self.user.first_name} {self.user.patronymic}"
            )
            self.client_profile.locators.GENDER.to_have_value(self.user.gender)
            self.client_profile.locators.DOCUMENT_TYPE.to_contain_text(self.user.document_type)
            self.client_profile.locators.DOCUMENT_SERIAL_AND_NUM.to_contain_text(self.user.document_serial)
            self.client_profile.locators.DOCUMENT_SERIAL_AND_NUM.to_contain_text(self.user.document_num)
            self.client_profile.locators.DOCUMENT_PROVIDE_BY.to_contain_text(self.user.document_provide_by)
            self.client_profile.locators.DOCUMENT_DIVISION_CODE.to_contain_text(self.user.document_division_code)
            self.client_profile.locators.DOCUMENT_DATE.to_contain_text(self.user.document_date)
            self.client_profile.locators.DOCUMENT_VALID_DATE.to_contain_text(self.user.document_valid_date)
            self.client_profile.locators.BIRTH_DATE.to_contain_text(self.user.birth_date)
            self.client_profile.locators.BIRTH_PLACE.to_contain_text(self.user.birth_place)
            self.client_profile.locators.INN.to_contain_text(self.user.inn)
            self.client_profile.locators.SNILS.to_contain_text(self.user.snils)

            self.client_profile.locators.ADDRESSES_TAB.click()
            self.client_profile.locators.TABLE_ADDRESSES.to_contain_text(0, new_address)

    @allure.title("БП Продажа продукта клиенту B2C")
    @allure.description("Продажа продуктового предложения клиенту B2C")
    @allure.id(584471)
    def test_b2c_sale(self, base_url: str, create_individual_user: IndividualClient) -> None:
        new_client_id = create_individual_user.user_id

        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{new_client_id}/overview")

        with allure.step("Создание продажи"):
            self.inquiries_page.sale_initialization(self.user, need_contact_data=True, priority="Высокий")

            self.inquiries_page.locators.ADD_SALE_BTN.click()
            self.product_offer_form.PRODUCT_TYPE.select_by_value("Монопродукт")
            self.product_offer_form.PRODUCT_CATEGORY.select_by_value("Мобильная связь")
            self.product_offer_form.SEARCH_BTN.click()

            product = self.inquiries_page.choose_product_offer_with_name("На связи")
            self.product_offer_form.ADD_BTN.click()

            self.inquiries_page.locators.ADDED_PRODUCT.wait_to_have_count(1, timeout=20000)
            self.inquiries_page.locators.STEP_TITLE.wait_to_have_text("Наполнение и уточнение коммерческого заказа")
            self.inquiries_page.locators.INQUIRY_STATUS.wait_to_have_text("Обрабатывается")
            self.inquiries_page.locators.INQUIRY_STEP.wait_to_have_text("Управление составом заказа")
            self.inquiries_page.locators.TABS[0].check_attribute_by_value("aria-selected", "true")
            self.inquiries_page.locators.CHECK_CONFIGURATION_BTN.wait_to_be_enabled()

            self.inquiries_page.locators.ADDED_PRODUCT_ONE_TIME_PAYMENT[0].wait_to_be_visible()
            self.inquiries_page.locators.ADDED_PRODUCT_SUBSCRIPTION_FEE[0].wait_to_be_visible()

            self.inquiries_page.locators.ADDED_PRODUCT_NOT_FILLED_CHARS_BTN[0].click(force=True)
            self.product_edit_form.RESOURCES_TAB.click()
            self.inquiries_page.auto_reserve_phone_number_resources()

            self.product_edit_form.INNER_ACCEPT_BTN.click()

            self.inquiries_page.check_configuration()
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
            self.inquiries_page.locators.SUCCESS_COMPLITED.wait_to_be_visible(timeout=40000)
            self.inquiries_page.locators.PRODUCT_INFO_STATUS.wait_to_have_text(re.compile("Успешно выполнено"))

        with allure.step("Проверка вкладки 'Элементы заказа'"):
            self.inquiries_page.locators.TABS[1].click()
            self.inquiries_page.locators.TABS[1].check_attribute_by_value("aria-selected", "true")
            self.inquiries_page.locators.LOAD_SPIN_FIRST.not_to_be_visible(timeout=10000)
            self.inquiries_page.locators.PRODUCTS_CONTRACT_NUM.wait_to_be_visible()
            accounts = self.personal_account_api.get_personal_accounts("customer", new_client_id).json()["items"]
            account_number = accounts[0]["accountNumber"]
            self.inquiries_page.locators.PRODUCTS_NAME[0].wait_to_have_text(product.product_name)
            contact_num = self.inquiries_page.locators.PRODUCTS_CONTRACT_NUM[0].text
            self.inquiries_page.locators.PRODUCTS_PERSONAL_ACCOUNT_NUM[0].wait_to_have_text(str(account_number))
            self.inquiries_page.locators.PRODUCTS_SUBSCRIPTION_FEE[0].to_contain_text(f"{product.subscription_fee:.2f}")

        with allure.step('Перейти в карточку клиента Открыть вкладку "Продукты"'):
            self.inquiries_page.locators.CLIENT.click()

            self.client_profile.locators.PRODUCTS_TAB.click()
            self.client_profile.locators.PRODUCTS.wait_to_be_visible()
            self.client_profile.locators.PRODUCTS[0].to_contain_text("Действует с")
            self.client_profile.locators.PRODUCTS_CONTRACT_NUM[0].to_contain_text(contact_num)
            self.client_profile.locators.PRODUCTS_PERSONAL_ACCOUNT_NUM[0].to_contain_text(str(account_number))
            self.client_profile.locators.PRODUCTS_SUBSCRIPTION_FEE[0].to_contain_text(f"{product.subscription_fee:.2f}")
            self.client_profile.locators.PRODUCTS_STATUS_COLOR[0].element_have_css_color("background-color", "yellow")

    @allure.title("БП Активация продукта")
    @allure.description("БП Активация продукта")
    @allure.id(584472)
    @pytest.mark.sanity
    def test_product_activation(self, base_url: str, create_individual_user: IndividualClient) -> None:
        client = create_individual_user
        inquiry = self.client_request_api.product_sale()
        balance = 100

        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")
        self.client_profile.locators.PRODUCTS_TAB.click(timeout=10000)
        self.client_profile.locators.PRODUCTS.wait_to_be_visible()
        self.client_profile.locators.PRODUCTS_STATUS_COLOR[0].element_have_css_color("background-color", "yellow")
        self.personal_account_api.wait_check_current_main_balance(client.agreements[0].accounts[0].id, 0)

        with allure.step(f"Добавление платежа для ЛС {test_context.client.agreements[0].accounts[0].id}"):
            amount = balance
            if inquiry.product.one_time_payment:
                amount += inquiry.product.one_time_payment
            if inquiry.product.subscription_fee:
                amount += inquiry.product.subscription_fee
            self.payment_api.create_default_payment(
                client.agreements[0].accounts[0].id,
                amount,
            )
            self.personal_account_api.wait_check_current_main_balance(
                client.agreements[0].accounts[0].id,
                amount,
            )
        self.inquiries_page.locators.CLIENT.click()
        self.client_profile.locators.CURRENT_PERSONAL_ACCOUNT_LINK.click()
        self.base_page.base_elements.CONTEXT_ELEMENT.wait_for_text_in_all(["Лицевой счет"], timeout=10000)
        self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Платежи")

        self.payment_page.payment_elements.CHECK_NUM_FIELDS.wait_to_be_visible()
        self.personal_account_api.wait_check_current_main_balance(client.agreements[0].accounts[0].id, balance)
        self.payment_page.payment_elements.USER_BALANCE.wait_to_have_text(f"{balance:.2f}", timeout=7000)

        self.inquiries_page.locators.CLIENT.click()
        self.client_profile.locators.PRODUCTS_TAB.click()
        self.client_profile.locators.PRODUCTS.wait_to_be_visible()
        self.client_profile.locators.PRODUCTS_STATUS_COLOR[0].element_have_css_color("background-color", "green")

    @allure.title("БП Отключение ПП")
    @allure.description(
        'Отключение продуктового предложения у абонента в продуктовом профиле клиента на вкладке "По абонентам" '
    )
    @allure.id(585790)
    @pytest.mark.smoke
    def test_turn_off_pp(self, base_url: str, create_individual_user: IndividualClient) -> None:
        client = create_individual_user
        inquiry = self.client_request_api.product_sale()
        balance = 100

        with allure.step(f"Добавление платежа для ЛС {test_context.client.agreements[0].accounts[0].id}"):
            self.payment_api.create_default_payment(
                client.agreements[0].accounts[0].id,
                inquiry.product.one_time_payment + inquiry.product.subscription_fee + balance,
            )
            self.personal_account_api.wait_check_current_main_balance(client.agreements[0].accounts[0].id, balance)

        self.base_page.open(
            f"{base_url}customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
        )
        self.base_page.base_elements.CONTEXT_ELEMENT.wait_for_text_in_all(["Лицевой счет"], timeout=10000)
        self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Платежи")

        self.payment_page.payment_elements.CHECK_NUM_FIELDS.wait_to_be_visible()
        self.payment_page.payment_elements.USER_BALANCE.wait_to_have_text(f"{balance:.2f}", timeout=10000)

        self.inquiries_page.locators.CLIENT.click()
        self.client_profile.locators.PRODUCTS_TAB.click()
        self.client_profile.locators.PRODUCTS.wait_to_be_visible()
        self.client_profile.locators.PRODUCTS_STATUS_COLOR[0].element_have_css_color("background-color", "green")

        self.client_profile.locators.PRODUCT_LIMIT.wait_to_be_visible()
        self.client_profile.locators.PRODUCTS_DETAILS_OPEN_BTN.wait_to_be_visible()
        self.client_profile.locators.PRODUCTS_DETAILS_OPEN_BTN.click(force=True)
        self.client_profile.locators.TURN_OFF_BTN.wait_to_be_visible()
        self.client_profile.locators.TURN_OFF_BTN.click(force=True)
        self.create_request_form.TITLE.wait_to_have_text("Создание продажи и управление услугами", timeout=10000)
        self.create_request_form.SAVE_BTN.click()
        inquiry_id = self.client_request_api._get_nth_inquiry(client.user_id, 2)
        self.base_page.open(f"{base_url}inquiries/{inquiry_id}")
        self.inquiries_page.locators.INQUIRY_STATUS.wait_to_have_text("Обрабатывается", timeout=15000)
        self.inquiries_page.locators.TABS[0].check_attribute_by_value("aria-selected", "true")
        self.inquiries_api.wait_appeal_status(inquiry_id, timeout=200000)
        self.base_page.refresh_page(wait="load")
        with allure.step("Дождаться изменения шага на Завершение продажи"):
            self.inquiries_page.locators.INQUIRY_STEP.wait_to_have_text("Завершение продажи", timeout=15000)
            self.inquiries_page.locators.SUCCESS_COMPLITED.wait_to_be_visible(timeout=10000)

        with allure.step("Проверка вкладки 'Элементы заказа'"):
            self.inquiries_page.locators.TABS.wait_to_be_visible()
            self.inquiries_page.locators.TABS[1].click()
            self.inquiries_page.locators.TABS[1].check_attribute_by_value("aria-selected", "true")
            self.inquiries_page.locators.PRODUCTS_NAME[0].wait_to_have_text(inquiry.product.product_name)
            self.inquiries_page.locators.PRODUCTS_STATUS.wait_to_have_text("Отключение")

        self.inquiries_page.locators.TABS[0].click()
        self.inquiries_page.locators.TABS[0].check_attribute_by_value("aria-selected", "true")
        self.inquiries_page.locators.PRODUCT_PROFILE_BTN.click()

        with allure.step("Проверка вкладки 'Продукты'"):
            self.client_profile.locators.PRODUCTS_LIST.wait_to_have_count(1)
            self.client_profile.locators.SUBSCRIBER[0].wait_to_have_text(inquiry.product.phone_number)
            self.client_profile.locators.PRODUCTS_LIST_STATUS_COLOR[0].element_have_css_color(
                "background-color", "moon_white"
            )
            self.client_profile.locators.PRODUCT_NAME.wait_not_to_be_visible()
