import re

import allure
import pytest
from playwright.sync_api import APIRequestContext, Page

from api.requests.personal_account_requests import PersonalAccountRequests
from common.helpers.data_generator import generate_random_number
from common.helpers.time_helpers import delay
from models.user import OrganizationClient
from pages.client_profile_page import ClientProfilePage
from pages.inquiries_page import InquiriesPage
from pages.locators.dynamic_form_elements import CreateSalesAndServiceManagement
from pages.locators.home_page_elements import HomePage
from pages.locators.inquiries_elements import ProductEditForm
from pages.locators.select_product_offers_form import SelectProductOffersForm
from pages.personal_account_page import PersonalAccountPage


@allure.epic("Общие бизнес-процессы")
@allure.suite("Общие бизнес-процессы")
class TestCommonBusinessProcessesB2B:
    @pytest.fixture(autouse=True)
    def setup(
        self,
        nexign_ui_stand_login: Page,
        api_request_auth_context: APIRequestContext,
        organization_user_data: OrganizationClient,
    ) -> None:
        self.home_page = HomePage(nexign_ui_stand_login)
        self.personal_account_page = PersonalAccountPage(nexign_ui_stand_login, organization_user_data)
        self.client_profile = ClientProfilePage(nexign_ui_stand_login)
        self.inquiries_page = InquiriesPage(nexign_ui_stand_login)
        self.create_request_form = CreateSalesAndServiceManagement(nexign_ui_stand_login)
        self.product_offer_form = SelectProductOffersForm(nexign_ui_stand_login)
        self.product_edit_form = ProductEditForm(nexign_ui_stand_login)
        self.personal_account_api = PersonalAccountRequests(api_request_auth_context)
        self.user_data = organization_user_data

    @allure.title("БП Создание клиента B2B(ЮЛ)")
    @allure.tag("CAN_AUTH", "SUCCESS")
    @allure.description("Создание клиента B2B(ЮЛ) с полным вводом адреса")
    @allure.id(585281)
    @pytest.mark.regress
    def test_create_client_b2b(self) -> None:
        building_number = generate_random_number(3)
        flat_number = generate_random_number(2)
        new_address = f"Россия, Самарская обл., г. Самара, ул. Осипенко, д. {building_number}, кв. {flat_number}"

        self.home_page.CREATE_ORG_BTN.click()
        delay(1, reason="Без ожидания форма заполняется не корректно")
        self.personal_account_page.organization_create_form.CUSTOMER_NAME.fill(self.user_data.customer_name)
        (self.personal_account_page.organization_create_form.TAX_SCHEME.select_by_value("НДС"))
        self.personal_account_page.organization_create_form.REGISTRATION_ADDRESS.open_dropdown()
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
        self.personal_account_page.organization_create_form.REGISTRATION_ADDRESS.to_contain_text(new_address)
        self.personal_account_page.dynamic_form.SAVE_BTN.click()
        self.personal_account_page.dynamic_form.SAVE_BTN.not_to_be_visible()

        self.client_profile.locators.CLIENT_FIO.to_contain_text(self.user_data.customer_name)
        self.client_profile.locators.CLIENT_TAB.click()
        self.client_profile.locators.ADDRESSES_TAB.click()
        self.client_profile.locators.TABLE_ADDRESSES.to_contain_text(0, new_address)

    @allure.title("БП Продажа продукта клиенту B2B")
    @allure.tag("CAN_AUTH", "SUCCESS")
    @allure.description("Продажа продукта клиенту B2B")
    @allure.id(585282)
    @pytest.mark.regress
    @pytest.mark.smoke
    def test_selling_product_b2b_client(self, add_two_msisdn_free_and_open_for_use) -> None:
        self.personal_account_page.create_customer_with_type("organization")
        self.personal_account_page.dynamic_form.SAVE_BTN.click()
        self.client_profile.locators.CLIENT_FIO.wait_to_be_visible()
        new_client_id = self.personal_account_page.get_customer_id_from_url()

        with allure.step("Пользователь нажал на кнопку создание продажи"):
            self.home_page.RIGHT_SIDE_BTN.wait_to_have_count(4, timeout=10000)
            self.home_page.RIGHT_SIDE_BTN.click(1)

        with allure.step('Заполнить контактные данные нажать на кнопку "сохранить"'):
            self.create_request_form.EMAIL.fill(self.user_data.contact_email)
            self.create_request_form.PHONE.fill(self.user_data.contact_phone)
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
                self.product_offer_form.PRODUCT_CARD_SELECT_BTN.wait_to_have_count(3)
                product_name = self.product_offer_form.PRODUCT_CARD_NAME[0].text
                single_payment = self.product_offer_form.PRODUCT_SINGLE_PAYMENTS[0].text.split(".")[0]
                product_sum = self.product_offer_form.PRODUCT_CARD_SUMS[0].text.split(".")[0]
                self.product_offer_form.PRODUCT_CARD_SELECT_BTN[0].click()
                self.product_offer_form.PRODUCT_CARD_SELECT_BTN[0].wait_to_have_text("Удалить")
            self.product_offer_form.ADD_BTN.click()
            self.product_offer_form.ADD_BTN.not_to_be_visible()

            self.inquiries_page.locators.ADDED_PRODUCT.wait_to_have_count(1, timeout=10000)
            self.inquiries_page.locators.STEP_TITLE.wait_to_have_text("Наполнение и уточнение коммерческого заказа")
            self.inquiries_page.locators.INQUIRY_STATUS.wait_to_have_text("Обрабатывается")
            self.inquiries_page.locators.INQUIRY_STEP.wait_to_have_text("Управление составом заказа")
            self.inquiries_page.locators.TABS[0].check_attribute_by_value("aria-selected", "true")
            self.inquiries_page.locators.CHECK_CONFIGURATION_BTN.wait_to_be_enabled()

            self.inquiries_page.locators.ADDED_PRODUCT_ONE_TIME_PAYMENT[0].wait_to_be_visible()
            self.inquiries_page.locators.ADDED_PRODUCT_SUBSCRIPTION_FEE[0].wait_to_be_visible()

            self.inquiries_page.locators.ADDED_PRODUCT_EDIT_BTN[0].click(force=True)
            self.product_edit_form.RESOURCES_TAB.click()
            phone_number = self.inquiries_page.auto_reserve_phone_number_resources()[1]

            self.product_edit_form.INNER_CANCEL_BTN.click()
            self.product_edit_form.RESOURCES_TAB.not_to_be_visible()

            self.inquiries_page.locators.CHECK_CONFIGURATION_BTN.click()
            self.inquiries_page.locators.LOAD_SPIN_FIRST.not_to_be_visible(timeout=60000)
            self.inquiries_page.locators.PRODUCT_CHECK_STATUS.wait_to_be_visible(timeout=10000)
            self.inquiries_page.locators.PRODUCT_CHECK_STATUS.wait_to_have_text(
                'Продукты заказа настроены корректно. Для продолжения продажи перейдите на следующий шаг, нажав на кнопку "Далее"'
            )

            self.inquiries_page.locators.NEXT_STEP_BTN.click()
            delay(1, reason="Зависает продажа без таймаута")
            self.inquiries_page.locators.AUTO_AGREEMENT_BTN.click()
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
            self.inquiries_page.locators.SUBSCRIBERS[0].wait_to_have_text(phone_number)
            self.inquiries_page.locators.PRODUCTS_NAME[0].wait_to_have_text(product_name)
            contact_num = self.inquiries_page.locators.PRODUCTS_CONTRACT_NUM[0].text
            self.inquiries_page.locators.PRODUCTS_PERSONAL_ACCOUNT_NUM[0].wait_to_have_text(str(account_id))
            self.inquiries_page.locators.ADDED_PRODUCT_ONE_TIME_PAYMENT[0].to_contain_text(f"{single_payment}.00")
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
