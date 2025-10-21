import re

import allure
import pytest
from playwright.sync_api import APIRequestContext, Page

from api.nbss.client_requests.client_requests import ClientRequests
from api.nbss.personal_account_requests import PersonalAccountRequests
from common.helpers.data_generator import generate_random_number
from common.helpers.env_helper import BASE_URL
from common.helpers.time_helpers import delay
from models.context import test_context
from models.user import OrganizationClient
from pages.base_page import BasePage
from pages.locators.nbss.dynamic_form_elements import CreateSalesAndServiceManagement
from pages.locators.nbss.home_page_elements import HomePage
from pages.locators.nbss.inquiries_elements import ProductEditForm
from pages.locators.nbss.select_product_offers_form import SelectProductOffersForm
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.inquiries_page import InquiriesPage
from pages.nbss.personal_account_page import PersonalAccountPage


@allure.epic("Общие бизнес-процессы")
@allure.suite("Общие бизнес-процессы")
@pytest.mark.regress
class TestCommonBusinessProcessesB2B:
    @pytest.fixture(autouse=True)
    def setup(
        self,
        nexign_ui_stand_login: Page,
        api_request_context: APIRequestContext,
        organization_user_data: OrganizationClient,
    ) -> None:
        self.base_page = BasePage(nexign_ui_stand_login)
        self.home_page = HomePage(nexign_ui_stand_login)
        self.personal_account_page = PersonalAccountPage(nexign_ui_stand_login, organization_user_data)
        self.client_profile = ClientProfilePage(nexign_ui_stand_login)
        self.inquiries_page = InquiriesPage(nexign_ui_stand_login)
        self.create_request_form = CreateSalesAndServiceManagement(nexign_ui_stand_login)
        self.product_offer_form = SelectProductOffersForm(nexign_ui_stand_login)
        self.product_edit_form = ProductEditForm(nexign_ui_stand_login)
        self.personal_account_api = PersonalAccountRequests(api_request_context)
        self.client_api = ClientRequests(api_request_context)
        self.user_data = organization_user_data

    @allure.title("БП Создание клиента B2B(ЮЛ)")
    @allure.description("Создание клиента B2B(ЮЛ) с полным вводом адреса")
    @allure.id(585281)
    def test_create_client_b2b(self) -> None:
        building_number = generate_random_number(3)
        flat_number = generate_random_number(2)
        new_address = f"Россия, Самарская обл., г. Самара, ул. Осипенко, д. {building_number}, кв. {flat_number}"

        self.home_page.CREATE_ORG_BTN.click()
        self.personal_account_page.organization_create_form.INN.fill(self.user_data.inn)
        self.personal_account_page.organization_create_form.KPP.fill(self.user_data.kpp)
        self.personal_account_page.organization_create_form.NEXT_BTN.click()

        self.personal_account_page.organization_create_form.PROPRIETARY_FORM.select_by_value(
            self.user_data.proprietary_form
        )
        self.personal_account_page.organization_create_form.CLIENT_NAME.fill(self.user_data.customer_name)
        self.personal_account_page.organization_create_form.OGRN.fill(self.user_data.ogrn)
        self.personal_account_page.organization_create_form.TAX_SCHEME.select_by_value(self.user_data.tax_scheme)
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
        self.personal_account_page.organization_create_form.SAVE_BTN.click()
        self.personal_account_page.organization_create_form.SAVE_BTN.not_to_be_visible(timeout=10000)

        self.client_profile.locators.CLIENT_FIO.wait_to_be_visible(timeout=10000)
        self.client_profile.locators.CLIENT_FIO.to_contain_text(self.user_data.customer_name)
        self.client_profile.locators.CLIENT_TAB.click()
        self.client_profile.locators.ADDRESSES_TAB.click()
        self.client_profile.locators.TABLE_ADDRESSES.to_contain_text(0, new_address)

    @allure.title("БП Продажа продукта клиенту B2B")
    @allure.description("Продажа продукта клиенту B2B")
    @allure.id(585282)
    @pytest.mark.smoke
    def test_selling_product_b2b_client(self) -> None:
        self.client = self.client_api.create_organization(self.user_data)
        self.base_page.open(BASE_URL + f"customer-hierarchy-management/customers/{test_context.client.user_id}/overview")
        self.client_profile.locators.CONTEXT_ELEMENT.wait_for_text_in_all(["Клиент"], timeout=10000)
        self.client_profile.locators.CLIENT_FIO.wait_to_be_visible()

        with allure.step("Создание продажи"):
            self.inquiries_page.sale_initialization(self.user_data, need_contact_data=True, priority="Высокий")

            self.inquiries_page.locators.ADD_SALE_BTN.click()
            self.product_offer_form.PRODUCT_TYPE.select_by_value("Монопродукт")
            self.product_offer_form.PRODUCT_CATEGORY.select_by_value("Мобильная связь")
            self.product_offer_form.SEARCH_BTN.click()

            product = self.inquiries_page.choose_product_offer_with_name("Бизнес на связи")
            self.product_offer_form.ADD_BTN.click()
            self.product_offer_form.ADD_BTN.not_to_be_visible(timeout=10000)

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
            product.phone_number = self.inquiries_page.auto_reserve_phone_number_resources()[1]

            self.product_edit_form.INNER_ACCEPT_BTN.click()
            self.product_edit_form.RESOURCES_TAB.not_to_be_visible()

            self.inquiries_page.check_configuration()

            self.inquiries_page.locators.NEXT_STEP_BTN.click()
            delay(1, reason="Зависает продажа без таймаута")
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
            accounts = self.personal_account_api.get_personal_accounts("customer", test_context.client.user_id).json()[
                "items"
            ]
            account_number = accounts[0]["accountNumber"]
            self.inquiries_page.locators.MONOPRODUCT_SUBSCRIBERS[0].wait_to_have_text(product.phone_number)
            self.inquiries_page.locators.PRODUCTS_NAME[0].wait_to_have_text(product.product_name)
            contact_num = self.inquiries_page.locators.PRODUCTS_CONTRACT_NUM[0].text
            self.inquiries_page.locators.PRODUCTS_PERSONAL_ACCOUNT_NUM[0].wait_to_have_text(str(account_number))
            self.inquiries_page.locators.ADDED_PRODUCT_ONE_TIME_PAYMENT[0].to_contain_text(
                f"{product.one_time_payment:.2f}"
            )
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
