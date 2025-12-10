import re

import allure
import pytest

from common.helpers.checker import assert_that
from common.helpers.env_helper import BASE_URL_CRAB
from common.helpers.time_helpers import delay
from models.context import test_context
from models.user import IndividualClient
from pages.base_page import BasePage
from pages.crab_pages.crab_base_page import CrabBasePage
from pages.locators.nbss.client.client_profile import ClientProfileElements
from pages.locators.nbss.client.client_search import ClientSearchElements
from pages.locators.nbss.dynamic_form_elements import (
    ClientChoice,
    CreateSalesAndServiceManagement,
    IndividualCustomerCreate,
    ProductInfoForm,
)
from pages.locators.nbss.home_page_elements import HomePageElements
from pages.locators.nbss.inquiries_elements import ProductEditForm
from pages.locators.nbss.select_product_offers_form import SelectProductOffersFormElements
from pages.nbss.inquiries_page import InquiriesPage


@allure.suite("Процесс продажи")
@allure.sub_suite("E2E_63 Продажа клиенту B2C")
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestB2CSaleWithAutoContractProcess:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login) -> None:
        self.base_page = BasePage()
        self.home_page = HomePageElements()
        self.customer_create_form = IndividualCustomerCreate()
        self.client_search_page = ClientSearchElements()
        self.create_request_form = CreateSalesAndServiceManagement()
        self.client_choice = ClientChoice()
        self.client_profile = ClientProfileElements()
        self.inquiries_page = InquiriesPage()
        self.product_offer_form = SelectProductOffersFormElements()
        self.product_edit_form = ProductEditForm()
        self.product_info_form = ProductInfoForm()

    @allure.title("Продажа B2C выбранному клиенту с автоматическим созданием договора и ЛС")
    @allure.description("При регистрации продажи, Клиент выбрал Автоматическое создание Договора/ЛС.")
    @allure.id(476400)
    def test_b2b_sale_with_auto_contract_process(self, base_url: str, create_individual_user: IndividualClient) -> None:
        client = create_individual_user
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")

        with allure.step("Создание продажи"):
            self.inquiries_page.sale_initialization(client, need_contact_data=True, priority="Высокий", add_kp="no")

            self.inquiries_page.locators.ADD_SALE_BTN.click()
            self.product_offer_form.PRODUCT_TYPE.select_by_value("Монопродукт")
            self.product_offer_form.PRODUCT_CATEGORY.select_by_value("Интернет")
            self.product_offer_form.SEARCH_BTN.click()

            self.inquiries_page.choose_product_offer_with_name("Скоростной Уют")
            self.product_offer_form.ADD_BTN.click()

            self.inquiries_page.locators.ADDED_PRODUCT.wait_to_have_count(1, timeout=10000)

            self.inquiries_page.locators.ADDED_PRODUCT_ONE_TIME_PAYMENT[0].wait_to_be_visible()
            self.inquiries_page.locators.ADDED_PRODUCT_SUBSCRIPTION_FEE[0].wait_to_be_visible()
            self.inquiries_page.locators.INQUIRY_STATUS.wait_to_have_text("Обрабатывается")

            self.inquiries_page.locators.ADDED_PRODUCT_VISIBLE_BTN[0].click(force=True)
            self.product_edit_form.SPECIFICATION_TAB.to_have_class(re.compile(r".+active"))
            self.product_edit_form.SPECIFICATION.wait_to_be_visible()

            self.product_edit_form.SERVICES_TAB.click()
            self.product_edit_form.SERVICES_TAB.to_have_class(re.compile(r".+active"))
            self.product_edit_form.SERVICES.wait_to_be_visible()

            self.product_edit_form.INNER_CANCEL_BTN.click()

            self.inquiries_page.check_configuration()
            self.inquiries_page.check_technical_feasibility()

            self.inquiries_page.locators.REFRESH_BTN.click()
            self.inquiries_page.locators.PRODUCT_CHECK_STATUS.wait_to_be_visible(timeout=10000)
            self.inquiries_page.locators.PRODUCT_CHECK_STATUS.wait_to_have_text(
                'Для всех продуктов заказа есть техническая возможность подключения. Для продолжения оформления продажи перейдите на следующий шаг, нажав на кнопку "Далее".'
            )

            self.inquiries_page.locators.NEXT_STEP_BTN.click()
            self.inquiries_page.wait_connect_package_offers_and_close_inquiry()

        with allure.step("Ход заявки"):
            self.inquiries_page.locators.TABS.click(5)
            self.inquiries_page.locators.TABS[5].wait_to_have_text("Технические заказы")
            self.inquiries_page.locators.TABS[5].check_attribute_by_value("aria-selected", "true")
            self.inquiries_page.locators.LOAD_SPIN_FIRST.not_to_be_visible(timeout=10000)
            self.inquiries_page.locators.TECHNICAL_OFFERS.wait_to_be_visible()
            self.inquiries_page.locators.TECHNICAL_OFFERS[0].to_contain_text("Выполнен")
            self.inquiries_page.locators.TECHNICAL_OFFERS[1].to_contain_text("Выполнен")

            crab_oder_id_1 = self.inquiries_page.locators.TECHNICAL_OFFERS_ID[0].text
            crab_oder_id_2 = self.inquiries_page.locators.TECHNICAL_OFFERS_ID[1].text

            self.base_page.open_new_tab()
            crab_tab = CrabBasePage()
            crab_tab.open(f"{BASE_URL_CRAB}/#/orders")

            crab_tab.locators.ORDERS.wait_to_be_visible()

            crab_tab.locators.ORDER_ID_SEARCH.fill(f"order-{crab_oder_id_1}")
            crab_tab.press_keyboard_button("Enter")
            crab_tab.locators.ORDERS.wait_to_have_count(1)
            crab_tab.locators.ORDERS_ID[0].wait_to_have_text(f"order-{crab_oder_id_1}")

            crab_tab.locators.ORDER_ID_SEARCH.fill(f"order-{crab_oder_id_2}")
            crab_tab.press_keyboard_button("Enter")
            crab_tab.locators.ORDERS.wait_to_have_count(1)
            crab_tab.locators.ORDERS_ID[0].wait_to_have_text(f"order-{crab_oder_id_2}")

        with allure.step('Перейти на вкладку "История обработки"'):
            self.base_page.bring_to_front(self.inquiries_page.title)
            crab_tab.close_page_by_index(-1)

            self.inquiries_page.locators.TABS.click(4)
            self.inquiries_page.locators.TABS[4].wait_to_have_text("История обработки")

            self.inquiries_page.locators.LOAD_SPIN_FIRST.not_to_be_visible(timeout=10000)
            self.inquiries_page.locators.TABS[4].check_attribute_by_value("aria-selected", "true")
            self.inquiries_page.locators.HISTORY_STEPS.wait_to_be_visible(timeout=10000)
            self.inquiries_page.locators.HISTORY_STEPS[-1].to_contain_text("Завершение продажи")
            self.inquiries_page.locators.HISTORY_STEPS[-1].click()
            self.inquiries_page.locators.STEP_PROCESSES[-1].to_contain_text("Закрытие")

            self.inquiries_page.locators.TABS.click(1)
            self.inquiries_page.locators.TABS[1].wait_to_have_text("Элементы заказа")
            self.inquiries_page.locators.TABS[1].check_attribute_by_value("aria-selected", "true")

            self.inquiries_page.locators.PRODUCTS_CONTRACT_NUM.wait_to_be_visible()
            contact_num = self.inquiries_page.locators.PRODUCTS_CONTRACT_NUM[0].text
            personal_account_num = self.inquiries_page.locators.PRODUCTS_PERSONAL_ACCOUNT_NUM[0].text
            subscription_fee = self.inquiries_page.locators.PRODUCTS_SUBSCRIPTION_FEE[0].text

        with allure.step('Перейти в карточку клиента Открыть вкладку "Продукты"'):
            self.inquiries_page.locators.CLIENT.click()

            self.client_profile.PRODUCTS_TAB.click()
            self.client_profile.PRODUCTS.wait_to_be_visible()
            self.client_profile.PRODUCTS[0].to_contain_text("Действует с")
            self.client_profile.PRODUCTS_CONTRACT_NUM[0].to_contain_text(contact_num)
            self.client_profile.PRODUCTS_PERSONAL_ACCOUNT_NUM[0].to_contain_text(personal_account_num)
            self.client_profile.PRODUCTS_SUBSCRIPTION_FEE[0].to_contain_text(subscription_fee)

            self.client_profile.PRODUCT_NAME[0].click(force=True)
            self.product_info_form.SUBSCRIPTION_FEE.to_contain_text(subscription_fee.replace(" RUB", ""))

    @allure.title("Продажа B2C с неподтвержденным адресом")
    @allure.id(484486)
    @pytest.mark.parametrize(
        "create_individual_user", [pytest.param("Неизвестный адрес", id="wrong_address")], indirect=True
    )
    def test_sale_with_wrong_address(self, base_url: str, create_individual_user: IndividualClient) -> None:
        client = create_individual_user
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")

        with allure.step("Создание продажи"):
            self.inquiries_page.sale_initialization(client, need_contact_data=True, priority="Высокий", add_kp="no")

            self.inquiries_page.locators.ADD_SALE_BTN.click()
            self.product_offer_form.EXPRESS_PTV.wait_to_be_visible()
            assert_that(
                lambda: all(not item.is_checked() for item in self.product_offer_form.TECHNOLOGY.options_elements),
                "Технологии выбраны",
            )

            self.product_offer_form.EXPRESS_PTV.click()
            delay(1, "Проставление технологий")
            assert_that(
                lambda: any(item.is_checked() for item in self.product_offer_form.TECHNOLOGY.options_elements),
                "Технологии не выбраны",
            )

            self.product_offer_form.PRODUCT_CARD.wait_to_have_count(0)
