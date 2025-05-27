import allure
import pytest
from playwright.sync_api import Page

from common.helpers.time_helpers import delay
from pages.locators.dynamic_form_elements import AddOptionsForm, CreatePaymentForm, RequestCreate
from pages.locators.inquiries_page import InquiriesPage, ProductEditForm
from pages.locators.payments_elements import PaymentElements
from pages.locators.select_product_offers_form import SelectProductOffersForm
from pages.personal_account_page import PersonalAccountPage


@allure.epic("E2E_47 Подключение дополнительных ПП")
@allure.suite("E2E_47 Подключение дополнительных ПП")
@pytest.mark.usefixtures("nexign_ui_stand_login")
class TestAddOptionsProductProfile:
    @pytest.fixture(autouse=True)
    def setup(self, page: Page) -> None:
        self.personal_account_page = PersonalAccountPage(page)
        self.create_request = RequestCreate(page)
        self.inquiries_page = InquiriesPage(page)
        self.product_offer = SelectProductOffersForm(page)
        self.edit_product_form = ProductEditForm(page)
        self.payments_page = PaymentElements(page)
        self.create_payment_form = CreatePaymentForm(page)
        self.add_options_form = AddOptionsForm(page)

    @allure.title("Отмена добавления доп. опций в продуктовом профиле клиента")
    @allure.id(538607)
    @pytest.mark.regress
    def test_cancel_add_additional_options_customer_product_profile(self) -> None:
        self.personal_account_page.create_customer_with_type("organization")
        self.personal_account_page.dynamic_form.SAVE_BTN.click()
        self.personal_account_page.locators.INFO_MESSAGE.wait_to_be_visible()

        delay(1, "Время чтобы заявка подтянула данные созданного клиента")

        self.create_request.CREATE_APPLICATION.click()
        self.create_request.CHOOSE_AGREEMENT_BTN.select_by_value(value="Автоматически")
        self.create_request.SAVE_BTN.click()

        self.inquiries_page.LOAD_SPIN_FIRST.wait_to_be_visible(timeout=8000)
        self.inquiries_page.LOAD_SPIN_FIRST.wait_to_be_visible(timeout=8000)
        self.inquiries_page.LOAD_SPIN_SECOND.not_to_be_visible(timeout=80000)
        self.inquiries_page.LOAD_SPIN_SECOND.not_to_be_visible(timeout=80000)
        self.inquiries_page.LOCATOR_SALE.wait_to_be_visible()

        self.inquiries_page.ADD_SALE_BTN.click()
        self.product_offer.PRODUCT_TYPE.select_by_value("Монопродукт")
        self.product_offer.PRODUCT_CATEGORY.select_by_value("Мобильная связь")
        self.product_offer.SEARCH_BTN.click()
        self.product_offer.PRODUCT_CARD.wait_to_be_visible()
        delay(1, reason="не успевает прогрузиться выдача, нужно это ожидание")
        self.product_offer.PRODUCT_CARD_SELECT_BTN[0].click()
        self.product_offer.ADD_BTN.click()

        self.inquiries_page.ADDED_PRODUCT_INTERACTION_BTN.wait_elements_visible(element_index=1)
        self.inquiries_page.ADDED_PRODUCT_INTERACTION_BTN[1].click(force=True)

        self.edit_product_form.RESOURCES_TAB.click()

        self.edit_product_form.BOOK_RESOURCES.wait_to_be_enabled(timeout=8000)
        self.edit_product_form.BOOK_RESOURCES.click()
        self.inquiries_page.LOAD_SPIN_FIRST.not_to_be_visible(timeout=8000)
        self.edit_product_form.INNER_CANCEL_BTN.click()

        self.inquiries_page.CHECK_CONFIGURATION_BTN.click()
        self.inquiries_page.LOAD_SPIN_FIRST.not_to_be_visible(timeout=80000)
        self.inquiries_page.SUCCESS_SETUP.wait_to_be_visible()

        self.inquiries_page.NEXT_STEP_BTN.click()
        self.inquiries_page.LOAD_SPIN_FIRST.not_to_be_visible(timeout=80000)
        self.inquiries_page.AUTOMATIC_CREATE_CONTRACT_BTN.click()
        self.inquiries_page.LOAD_SPIN_FIRST.wait_to_be_visible()
        self.inquiries_page.LOAD_SPIN_FIRST.not_to_be_visible(timeout=1000000)

        self.inquiries_page.SUCCESS_SETUP.wait_to_be_visible()
        self.inquiries_page.PRODUCT_PROFILE_BTN.click()

        self.personal_account_page.locators.PERSONAL_ACCOUNTS_TAB.click()
        self.personal_account_page.locators.CURRENT_PERSONAL_ACCOUNT_LINK.wait_to_be_visible()
        self.personal_account_page.locators.CURRENT_PERSONAL_ACCOUNT_LINK.click()
        self.personal_account_page.locators.BURGER_MENU.select_by_value("Финансы > Платежи")

        self.payments_page.CREATE_PAYMENT_BTN.click()
        self.create_payment_form.SET_AMOUNT.fill("600")
        self.create_payment_form.PAYMENT_POINT.select_by_value("PNXL1/pointNx1")
        self.create_payment_form.INNER_ACCEPT_BTN.click()

        self.personal_account_page.locators.CURRENT_CLIENT_LINK.wait_to_be_visible()
        self.personal_account_page.locators.CURRENT_CLIENT_LINK.click()
        self.personal_account_page.locators.PRODUCTS_TAB.click()

        self.personal_account_page.locators.wait_to_be_enabled(type_offer="product")
        self.personal_account_page.locators.PRODUCTS_UPDATE_BTN.click()
        self.personal_account_page.locators.PRODUCTS_OPTIONS_OPEN_BTN[0].click()
        self.inquiries_page.LOAD_SPIN_SECOND.not_to_be_visible(timeout=8000)
        self.personal_account_page.locators.PRODUCTS_OPTIONS_ADD_BTN.wait_to_be_visible()
        self.personal_account_page.locators.PRODUCTS_OPTIONS_ADD_BTN.click()

        self.add_options_form.SEARCH_OPTIONS_FLD.fill("Блокировка")
        self.add_options_form.SEARCH_BTN.click()
        self.add_options_form.CHOSE_OPTION_BTN.wait_elements_visible(element_index=1)
        self.add_options_form.CHOSE_OPTION_BTN[1].click()
        self.add_options_form.SHOW_ONLY_CHOSEN_BTN.wait_to_be_visible(timeout=8000)
        self.add_options_form.SHOW_ONLY_CHOSEN_BTN.click()
        self.add_options_form.INNER_CANCEL_BTN.click()

        self.personal_account_page.locators.PRODUCTS_UPDATE_BTN.wait_to_be_visible()

    @allure.title("Добавление доп. опций для монопродукта в продуктовом профиле клиента")
    @allure.id(534773)
    @pytest.mark.regress
    def test_add_options_mono_product_customer_product_profile(self):
        self.personal_account_page.create_customer_with_type("organization")
        self.personal_account_page.dynamic_form.SAVE_BTN.click()
        self.personal_account_page.locators.INFO_MESSAGE.wait_to_be_visible()

        delay(1, "Время чтобы заявка подтянула данные созданного клиента")

        self.create_request.CREATE_APPLICATION.click()
        self.create_request.CHOOSE_AGREEMENT_BTN.select_by_value(value="Автоматически")
        self.create_request.SAVE_BTN.click()

        self.inquiries_page.LOAD_SPIN_FIRST.wait_to_be_visible(timeout=8000)
        self.inquiries_page.LOAD_SPIN_FIRST.wait_to_be_visible(timeout=8000)
        self.inquiries_page.LOAD_SPIN_SECOND.not_to_be_visible(timeout=80000)
        self.inquiries_page.LOAD_SPIN_SECOND.not_to_be_visible(timeout=80000)
        self.inquiries_page.LOCATOR_SALE.wait_to_be_visible()

        self.inquiries_page.ADD_SALE_BTN.click()
        self.product_offer.PRODUCT_TYPE.select_by_value("Монопродукт")
        self.product_offer.PRODUCT_CATEGORY.select_by_value("Мобильная связь")
        self.product_offer.SEARCH_BTN.click()
        self.product_offer.PRODUCT_CARD.wait_to_be_visible()
        delay(1, reason="не успевает прогрузиться выдача, нужно это ожидание")
        self.product_offer.PRODUCT_CARD_SELECT_BTN[0].click()
        self.product_offer.ADD_BTN.click()

        self.inquiries_page.auto_reserve_all_resources()

        self.inquiries_page.CHECK_CONFIGURATION_BTN.click()
        self.inquiries_page.LOAD_SPIN_FIRST.not_to_be_visible(timeout=80000)
        self.inquiries_page.SUCCESS_SETUP.wait_to_be_visible()

        self.inquiries_page.NEXT_STEP_BTN.click()
        self.inquiries_page.LOAD_SPIN_FIRST.not_to_be_visible(timeout=80000)
        self.inquiries_page.AUTOMATIC_CREATE_CONTRACT_BTN.click()
        self.inquiries_page.LOAD_SPIN_FIRST.wait_to_be_visible()
        self.inquiries_page.LOAD_SPIN_FIRST.not_to_be_visible(timeout=1000000)

        self.inquiries_page.SUCCESS_SETUP.wait_to_be_visible()
        self.inquiries_page.PRODUCT_PROFILE_BTN.click()

        self.personal_account_page.locators.PERSONAL_ACCOUNTS_TAB.click()
        self.personal_account_page.locators.CURRENT_PERSONAL_ACCOUNT_LINK.wait_to_be_visible()
        self.personal_account_page.locators.CURRENT_PERSONAL_ACCOUNT_LINK.click()
        self.personal_account_page.locators.BURGER_MENU.select_by_value("Финансы > Платежи")

        self.payments_page.CREATE_PAYMENT_BTN.click()
        self.create_payment_form.SET_AMOUNT.fill("700")
        self.create_payment_form.PAYMENT_POINT.select_by_value("PNXL1/pointNx1")
        self.create_payment_form.INNER_ACCEPT_BTN.click()

        self.personal_account_page.locators.CURRENT_CLIENT_LINK.wait_to_be_visible()
        self.personal_account_page.locators.CURRENT_CLIENT_LINK.click()
        self.personal_account_page.locators.PRODUCTS_TAB.click()

        self.personal_account_page.locators.wait_to_be_enabled(type_offer="product")
        self.personal_account_page.locators.PRODUCTS_UPDATE_BTN.click()
        self.personal_account_page.locators.PRODUCTS_OPTIONS_OPEN_BTN[0].click()
        self.inquiries_page.LOAD_SPIN_SECOND.not_to_be_visible(timeout=8000)
        self.personal_account_page.locators.PRODUCTS_OPTIONS_ADD_BTN.wait_to_be_visible()
        self.personal_account_page.locators.PRODUCTS_OPTIONS_ADD_BTN.click()

        self.add_options_form.SEARCH_OPTIONS_FLD.fill("+2 ГБ")
        self.add_options_form.SEARCH_BTN.click()
        self.add_options_form.CHOSE_OPTION_BTN.wait_elements_visible(element_index=0)
        self.add_options_form.CHOSE_OPTION_BTN[0].click()
        self.add_options_form.SHOW_ONLY_CHOSEN_BTN.wait_to_be_visible(timeout=8000)
        self.add_options_form.SHOW_ONLY_CHOSEN_BTN.click()
        self.add_options_form.INNER_ACCEPT_BTN.click()

        self.personal_account_page.locators.PRODUCTS_UPDATE_BTN.wait_to_be_visible()

        self.personal_account_page.locators.REQUESTS_TAB.click()
        self.inquiries_page.LOAD_SPIN_SECOND.not_to_be_visible(timeout=80000)
        self.personal_account_page.locators.REQUEST_NUMBER[1].wait_to_be_visible()
        self.personal_account_page.locators.REQUEST_NUMBER[1].click()
        self.inquiries_page.LOAD_SPIN_SECOND.not_to_be_visible(timeout=100000)

        self.inquiries_page.SUCCESS_SETUP.wait_to_be_visible()

        self.inquiries_page.TABS[1].click()
        self.inquiries_page.PRODUCTS[1].wait_to_be_visible(timeout=80000)

        self.inquiries_page.TABS[2].click()
        self.inquiries_page.DATA_SALE.wait_to_be_visible(timeout=80000)

        self.inquiries_page.TABS[3].click()
        self.inquiries_page.PROCESSING_STEP[0].wait_to_be_visible(timeout=80000)

        self.inquiries_page.TABS[4].click()
        self.inquiries_page.HISTORY_STEPS[0].wait_to_be_visible(timeout=80000)

        self.inquiries_page.TABS[5].click()
        self.inquiries_page.TECHNICAL_OFFERS[0].wait_to_be_visible(timeout=80000)

        self.inquiries_page.TABS[6].click()
        self.personal_account_page.locators.CURRENT_CLIENT_LINK.wait_to_be_visible()
        self.personal_account_page.locators.CURRENT_CLIENT_LINK.click()

        self.personal_account_page.locators.PRODUCTS_TAB.click()
        self.personal_account_page.locators.OPEN_OPTIONS_BTN[0].wait_to_be_visible(timeout=80000)

        self.personal_account_page.locators.OPEN_OPTIONS_BTN[0].click()
        self.personal_account_page.locators.CURRENT_OPTION_PRODUCT.wait_to_be_visible(timeout=80000)

        self.personal_account_page.locators.wait_to_be_enabled(type_offer="option")

    @allure.title("Добавление нескольких доп. опций для бандла в продуктовом профиле клиента")
    @allure.description(
        "Проверка возможности подключения опций для пакетного предложения через продуктовый профиль клиента"
    )
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=641863668",
        name="КР [UDS] Допродажа и управление услугами клиента. Подключение дополнительных продуктов.",
    )
    @allure.id(586001)
    @pytest.mark.regress
    def test_add_options_bandl_product_customer_product_profile(self):
        self.personal_account_page.create_customer_with_type("organization")
        self.personal_account_page.dynamic_form.SAVE_BTN.click()
        self.personal_account_page.locators.INFO_MESSAGE.wait_to_be_visible()

        delay(1, "Время чтобы заявка подтянула данные созданного клиента")
        self.create_request.CREATE_APPLICATION.click()
        self.create_request.CHOOSE_AGREEMENT_BTN.select_by_value(value="Автоматически")
        self.create_request.SAVE_BTN.click()

        self.inquiries_page.LOAD_SPIN_FIRST.wait_to_be_visible(timeout=8000)
        self.inquiries_page.LOAD_SPIN_FIRST.wait_to_be_visible(timeout=8000)
        self.inquiries_page.LOAD_SPIN_SECOND.not_to_be_visible(timeout=80000)
        self.inquiries_page.LOAD_SPIN_SECOND.not_to_be_visible(timeout=80000)
        self.inquiries_page.LOCATOR_SALE.wait_to_be_visible()

        self.inquiries_page.ADD_SALE_BTN.click()
        self.product_offer.PRODUCT_TYPE.select_by_value("Бандл")
        self.product_offer.PRODUCT_CATEGORY.select_by_value("Мобильная связь")
        self.product_offer.SEARCH_BTN.click()
        self.product_offer.PRODUCT_CARD.wait_to_be_visible()
        delay(1, reason="не успевает прогрузиться выдача, нужно это ожидание")
        self.product_offer.PRODUCT_CARD_SELECT_BTN[0].click()
        self.product_offer.ADD_BTN.click()

        self.inquiries_page.ADDED_PRODUCT_INTERACTION_BTN.wait_elements_visible(element_index=4)
        self.inquiries_page.ADDED_PRODUCT_INTERACTION_BTN[4].click(force=True)

        self.edit_product_form.RESOURCES_TAB.click()

        self.edit_product_form.BOOK_RESOURCES.wait_to_be_enabled(timeout=8000)
        self.edit_product_form.BOOK_RESOURCES.click()
        self.inquiries_page.LOAD_SPIN_FIRST.not_to_be_visible(timeout=8000)
        self.edit_product_form.INNER_CANCEL_BTN.click()

        self.inquiries_page.ADDED_PRODUCT_INTERACTION_BTN.wait_elements_visible(element_index=7)
        self.inquiries_page.ADDED_PRODUCT_INTERACTION_BTN[7].click(force=True)

        self.edit_product_form.RESOURCES_TAB.click()

        self.edit_product_form.BOOK_RESOURCES.wait_to_be_enabled(timeout=8000)
        self.edit_product_form.BOOK_RESOURCES.click()
        self.inquiries_page.LOAD_SPIN_FIRST.not_to_be_visible(timeout=8000)
        self.edit_product_form.INNER_CANCEL_BTN.click()

        self.inquiries_page.CHECK_CONFIGURATION_BTN.click()
        self.inquiries_page.LOAD_SPIN_FIRST.not_to_be_visible(timeout=80000)
        self.inquiries_page.SUCCESS_SETUP.wait_to_be_visible()

        self.inquiries_page.CHECK_TECHNICAL_FEASIBILITY_BTN.click()
        self.inquiries_page.LOAD_SPIN_FIRST.not_to_be_visible(timeout=80000)
        self.inquiries_page.SUCCESS_SETUP.wait_to_be_visible()

        self.inquiries_page.NEXT_STEP_BTN.click()
        self.inquiries_page.LOAD_SPIN_FIRST.not_to_be_visible(timeout=80000)
        self.inquiries_page.AUTOMATIC_CREATE_CONTRACT_BTN.click()
        self.inquiries_page.LOAD_SPIN_FIRST.wait_to_be_visible()
        self.inquiries_page.LOAD_SPIN_FIRST.not_to_be_visible(timeout=1000000)

        self.inquiries_page.SUCCESS_SETUP.wait_to_be_visible()
        self.inquiries_page.PRODUCT_PROFILE_BTN.click()

        self.personal_account_page.locators.PERSONAL_ACCOUNTS_TAB.click()
        self.personal_account_page.locators.CURRENT_PERSONAL_ACCOUNT_LINK.wait_to_be_visible()
        self.personal_account_page.locators.CURRENT_PERSONAL_ACCOUNT_LINK.click()
        self.personal_account_page.locators.BURGER_MENU.select_by_value("Финансы > Платежи")

        self.payments_page.CREATE_PAYMENT_BTN.click()
        self.create_payment_form.SET_AMOUNT.fill("5000")
        self.create_payment_form.PAYMENT_POINT.select_by_value("PNXL1/pointNx1")
        self.create_payment_form.INNER_ACCEPT_BTN.click()

        self.personal_account_page.locators.CURRENT_CLIENT_LINK.wait_to_be_visible()
        self.personal_account_page.locators.CURRENT_CLIENT_LINK.click()
        self.personal_account_page.locators.PRODUCTS_TAB.click()

        self.personal_account_page.locators.wait_to_be_enabled(type_offer="product")
        self.personal_account_page.locators.PRODUCTS_UPDATE_BTN.click()
        self.personal_account_page.locators.PRODUCTS_OPTIONS_OPEN_BTN[0].click()
        self.inquiries_page.LOAD_SPIN_SECOND.not_to_be_visible(timeout=8000)
        self.personal_account_page.locators.PRODUCTS_OPTIONS_ADD_BTN.wait_to_be_visible()
        self.personal_account_page.locators.PRODUCTS_OPTIONS_ADD_BTN.click()

        self.add_options_form.SEARCH_OPTIONS_FLD.fill("Блокировка")
        self.add_options_form.SEARCH_BTN.click()
        self.add_options_form.CHOSE_OPTION_BTN.wait_elements_visible(element_index=1)
        self.add_options_form.CHOSE_OPTION_BTN[1].click()
        self.add_options_form.CHOSE_OPTION_BTN.wait_elements_visible(element_index=3)
        self.add_options_form.CHOSE_OPTION_BTN[3].click()
        self.add_options_form.SHOW_ONLY_CHOSEN_BTN.wait_to_be_visible(timeout=8000)
        self.add_options_form.SHOW_ONLY_CHOSEN_BTN.click()
        self.add_options_form.INNER_ACCEPT_BTN.click()

        self.personal_account_page.locators.PRODUCTS_UPDATE_BTN.wait_to_be_visible()

        self.personal_account_page.locators.REQUESTS_TAB.click()
        self.inquiries_page.LOAD_SPIN_SECOND.not_to_be_visible(timeout=80000)
        self.personal_account_page.locators.REQUEST_NUMBER[1].wait_to_be_visible()
        self.personal_account_page.locators.REQUEST_NUMBER[1].click()
        self.inquiries_page.LOAD_SPIN_SECOND.not_to_be_visible(timeout=80000)

        self.inquiries_page.SUCCESS_SETUP.wait_to_be_visible()

        self.inquiries_page.TABS[1].wait_to_be_visible(timeout=80000)
        self.inquiries_page.TABS[1].click()
        self.inquiries_page.PRODUCTS[1].wait_to_be_visible(timeout=80000)

        self.inquiries_page.TABS[2].click()
        self.inquiries_page.DATA_SALE.wait_to_be_visible(timeout=80000)

        self.inquiries_page.TABS[3].click()
        self.inquiries_page.PROCESSING_STEP[0].wait_to_be_visible(timeout=80000)

        self.inquiries_page.TABS[4].click()
        self.inquiries_page.HISTORY_STEPS[0].wait_to_be_visible(timeout=80000)

        self.inquiries_page.TABS[5].click()
        self.inquiries_page.TECHNICAL_OFFERS[0].wait_to_be_visible(timeout=80000)

        self.inquiries_page.TABS[6].click()
        self.personal_account_page.locators.CURRENT_CLIENT_LINK.wait_to_be_visible()
        self.personal_account_page.locators.CURRENT_CLIENT_LINK.click()

        self.personal_account_page.locators.PRODUCTS_TAB.click()
        self.personal_account_page.locators.OPEN_OPTIONS_BTN[0].wait_to_be_visible(timeout=80000)

        delay(1, reason="не успевает прогрузиться список подключенных опций")
        self.personal_account_page.locators.OPEN_OPTIONS_BTN[0].click()
        self.personal_account_page.locators.CURRENT_OPTION_PRODUCT.wait_elements_visible(element_index=0)
        self.personal_account_page.locators.CURRENT_OPTION_PRODUCT.wait_elements_visible(element_index=1)

        self.personal_account_page.locators.wait_to_be_enabled(type_offer="option")
