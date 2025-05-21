import re

import allure
import pytest
from playwright.sync_api import Page

from common.helpers.data_generator import faker_ru
from common.helpers.env_helper import BASE_URL_CRAB
from common.helpers.time_helpers import delay
from pages.base_page import BasePage
from pages.crab_pages.crab_base_page import CrabBasePage
from pages.locators.client_profile import ClientProfile
from pages.locators.client_search import ClientSearch
from pages.locators.dynamic_form_elements import ClientChoice, CreateSalesAndServiceManagement, IndividualCustomerCreate
from pages.locators.home_page_elements import HomePage
from pages.locators.inquiries_page import InquiriesPage, ProductEditForm
from pages.locators.select_product_offers_form import SelectProductOffersForm


@allure.suite("Процесс продажи")
@allure.sub_suite("E2E_63 Продажа клиенту B2C")
class TestB2CSaleWithAutoContractProcess:
    @pytest.fixture(autouse=True)
    def setup(self, page: Page, nexign_ui_stand_login: Page) -> None:
        self.base_page = BasePage(nexign_ui_stand_login)
        self.home_page = HomePage(page)
        self.customer_create_form = IndividualCustomerCreate(page)
        self.client_search_page = ClientSearch(page)
        self.create_request_form = CreateSalesAndServiceManagement(page)
        self.client_choice = ClientChoice(page)
        self.client_profile = ClientProfile(page)
        self.inquiries_page = InquiriesPage(page)
        self.product_offer_form = SelectProductOffersForm(page)
        self.product_edit_form = ProductEditForm(page)

    @allure.title("Продажа B2C выбранному клиенту с автоматическим созданием договора и ЛС")
    @allure.tag("CAN_AUTH")
    @allure.description("При регистрации продажи, Клиент выбрал Автоматическое создание Договора/ЛС.")
    @allure.id(476400)
    @pytest.mark.regress
    def test_b2b_sale_with_auto_contract_process(self, base_url: str, create_user: int) -> None:
        contact_phone = faker_ru.phone_number()
        contact_email = faker_ru.email()
        new_client_id = create_user

        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{new_client_id}/overview")

        with allure.step("Пользователь нажал на кнопку создание продажи"):
            self.home_page.RIGHT_SIDE_BTN.wait_to_have_count(5, timeout=10000)
            self.home_page.RIGHT_SIDE_BTN.click(1)

        with allure.step('Заполнить контактные данные нажать на кнопку "сохранить"'):
            self.create_request_form.EMAIL.fill(contact_email)
            self.create_request_form.PHONE.fill(contact_phone)
            self.create_request_form.PRIORITY.select_by_value("Высокий")
            self.create_request_form.ADD_SALE_TYPE.select_by_value("Автоматически")

            self.create_request_form.SAVE_BTN.click()

        with allure.step("Создание продажи"):
            self.inquiries_page.INQUIRY_NAME.wait_to_have_text(re.compile(r"\d\. Продажа и управление услугами"))
            self.inquiries_page.INQUIRY_STATUS.wait_to_have_text("Обрабатывается")

            self.inquiries_page.LOAD_SPIN_FIRST.not_to_be_visible(timeout=60000)
            self.inquiries_page.PRODUCT_INFO_STATUS.wait_to_be_visible(timeout=10000)

            self.inquiries_page.ADD_SALE_BTN.click()
            self.product_offer_form.PRODUCT_TYPE.select_by_value("Монопродукт")
            self.product_offer_form.PRODUCT_CATEGORY.select_by_value("Интернет")
            self.product_offer_form.SEARCH_BTN.click()

            self.product_offer_form.PRODUCT_CARD_SELECT_BTN[0].click()
            self.product_offer_form.ADD_BTN.click()

            self.inquiries_page.ADDED_PRODUCT.wait_to_have_count(1, timeout=10000)

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
            self.inquiries_page.LOAD_SPIN_FIRST.not_to_be_visible(timeout=60000)
            self.inquiries_page.PRODUCT_CHECK_STATUS.wait_to_be_visible(timeout=10000)
            self.inquiries_page.PRODUCT_CHECK_STATUS.wait_to_have_text("Продукты заказа настроены корректно.")

            self.inquiries_page.CHECK_TECHNICAL_FEASIBILITY_BTN.click()
            self.inquiries_page.LOAD_SPIN_FIRST.not_to_be_visible(timeout=60000)
            self.inquiries_page.PRODUCT_CHECK_STATUS.wait_to_be_visible(timeout=10000)
            self.inquiries_page.PRODUCT_CHECK_STATUS.wait_to_have_text(
                'Для всех продуктов заказа есть техническая возможность подключения. Для продолжения оформления продажи перейдите на следующий шаг, нажав на кнопку "Далее".'
            )

            self.inquiries_page.REFRESH_BTN.click()
            self.inquiries_page.PRODUCT_CHECK_STATUS.wait_to_be_visible(timeout=10000)
            self.inquiries_page.PRODUCT_CHECK_STATUS.wait_to_have_text(
                'Для всех продуктов заказа есть техническая возможность подключения. Для продолжения оформления продажи перейдите на следующий шаг, нажав на кнопку "Далее".'
            )

            self.inquiries_page.NEXT_STEP_BTN.click()
            self.inquiries_page.LOAD_SPIN_FIRST.not_to_be_visible(timeout=240000)
            self.inquiries_page.PRODUCT_INFO_STATUS.wait_to_have_text("Успешно выполнено", timeout=10000)

        with allure.step("Ход заявки"):
            self.inquiries_page.TABS[5].click()
            self.inquiries_page.TABS[5].check_attribute_by_value("aria-selected", "true")
            self.inquiries_page.LOAD_SPIN_FIRST.not_to_be_visible(timeout=10000)
            self.inquiries_page.TECHNICAL_OFFERS.wait_to_be_visible()
            self.inquiries_page.TECHNICAL_OFFERS[0].to_contain_text("Выполнен")
            self.inquiries_page.TECHNICAL_OFFERS[1].to_contain_text("Выполнен")

            crab_oder_id_1 = self.inquiries_page.TECHNICAL_OFFERS_ID[0].text
            crab_oder_id_2 = self.inquiries_page.TECHNICAL_OFFERS_ID[1].text

            crab_tab = CrabBasePage(self.base_page.open_new_tab())
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
            self.base_page.bring_to_front(self.inquiries_page.page.title())
            crab_tab.close_page_by_index(-1)

            self.inquiries_page.TABS[4].click()

            self.inquiries_page.LOAD_SPIN_FIRST.not_to_be_visible(timeout=10000)
            self.inquiries_page.TABS[4].check_attribute_by_value("aria-selected", "true")
            self.inquiries_page.HISTORY_STEPS.wait_elements_visible(4, timeout=10000)
            self.inquiries_page.HISTORY_STEPS[4].to_contain_text("Завершение продажи")
            self.inquiries_page.HISTORY_STEPS[4].click()
            self.inquiries_page.STEP_PROCESSES[-1].to_contain_text("Закрытие")

            self.inquiries_page.TABS[1].click()
            self.inquiries_page.TABS[1].check_attribute_by_value("aria-selected", "true")

            self.inquiries_page.PRODUCTS_CONTRACT_NUM.wait_to_be_visible()
            contact_num = self.inquiries_page.PRODUCTS_CONTRACT_NUM[0].text
            personal_account_num = self.inquiries_page.PRODUCTS_PERSONAL_ACCOUNT_NUM[0].text
            subscription_fee = self.inquiries_page.PRODUCTS_SUBSCRIPTION_FEE[0].text

        with allure.step('Перейти в карточку клиента Открыть вкладку "Продукты"'):
            self.inquiries_page.CLIENT.click()

            self.client_profile.PRODUCTS_TAB.click()
            self.client_profile.PRODUCTS.wait_to_be_visible()
            self.client_profile.PRODUCTS[0].to_contain_text("Действует с")
            self.client_profile.PRODUCTS_CONTRACT_NUM[0].to_contain_text(contact_num)
            self.client_profile.PRODUCTS_PERSONAL_ACCOUNT_NUM[0].to_contain_text(personal_account_num)
            self.client_profile.PRODUCTS_SUBSCRIPTION_FEE[0].to_contain_text(subscription_fee)

            self.client_profile.PRODUCTS[0].click(force=True)
            self.product_edit_form.SUBSCRIPTION_FEE.to_contain_text(subscription_fee.replace(" RUB/Месяц", ""))

    @allure.title("Продажа B2C с неподтвержденным адресом")
    @allure.id(484486)
    @pytest.mark.parametrize("create_user", [pytest.param("Неизвестный адрес", id="wrong_address")], indirect=True)
    @pytest.mark.regress
    def test_sale_with_wrong_address(self, base_url: str, create_user: str) -> None:
        contact_phone = faker_ru.phone_number()
        contact_email = faker_ru.email()
        new_client_id = create_user

        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{new_client_id}/overview")

        with allure.step("Пользователь нажал на кнопку создание продажи"):
            self.home_page.RIGHT_SIDE_BTN.wait_to_have_count(5, timeout=10000)
            self.home_page.RIGHT_SIDE_BTN.click(1)

        with allure.step('Заполнить контактные данные нажать на кнопку "сохранить"'):
            self.create_request_form.EMAIL.fill(contact_email)
            self.create_request_form.PHONE.fill(contact_phone)
            self.create_request_form.PRIORITY.select_by_value("Высокий")
            self.create_request_form.ADD_SALE_TYPE.select_by_value("Автоматически")

            self.create_request_form.SAVE_BTN.click()

        with allure.step("Создание продажи"):
            self.inquiries_page.INQUIRY_NAME.wait_to_have_text(re.compile(r"\d\. Продажа и управление услугами"))
            self.inquiries_page.INQUIRY_STATUS.wait_to_have_text("Обрабатывается")

            self.inquiries_page.LOAD_SPIN_FIRST.not_to_be_visible(timeout=60000)
            self.inquiries_page.PRODUCT_INFO_STATUS.wait_to_be_visible(timeout=10000)

            self.inquiries_page.ADD_SALE_BTN.click()
            self.product_offer_form.EXPRESS_PTV.wait_to_be_visible()
            assert all(not item.is_checked() for item in self.product_offer_form.TECHNOLOGY.options_elements), (
                "Технологии выбраны"
            )

            self.product_offer_form.EXPRESS_PTV.click()
            delay(1, "Проставление технологий")
            assert any(item.is_checked() for item in self.product_offer_form.TECHNOLOGY.options_elements), (
                "Технологии не выбраны"
            )

            self.product_offer_form.PRODUCT_CARD.wait_to_have_count(0)
