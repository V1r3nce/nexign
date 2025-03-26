import allure
import pytest
from playwright.sync_api import Page
from pages.locators.dynamic_form_elements import IndividualCustomerCreate, CreateOrganization, PromisedPaymentForm, \
    RequestCreate
from pages.locators.inquiries_page import InquiriesPage, ProductEditForm, ChangeResourcesForm
from pages.locators.promised_payment import PromisedPaymentPage
from pages.locators.select_product_offers_form import SelectProductOffersForm
from pages.personal_account_page import PersonalAccountPage


@allure.epic("E2E_80 Управление обещанными платежами")
@allure.suite("E2E_80 Управление обещанными платежами")
@pytest.mark.usefixtures("nexign_ui_stand_login")
class TestConnectPromisedPayment:

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.personal_account_page = PersonalAccountPage(page)
        self.customer_create_form = IndividualCustomerCreate(page)
        self.organization_create_form = CreateOrganization(page)
        self.promised_payment = PromisedPaymentPage(page)
        self.promised_payment_form = PromisedPaymentForm(page)
        self.create_request = RequestCreate(page)
        self.inquiries_page = InquiriesPage(page)
        self.product_offer = SelectProductOffersForm(page)
        self.edit_product_form = ProductEditForm(page)
        self.change_product_form = ChangeResourcesForm(page)

    @allure.title("02. Успешное подключение ОП без комиссии ЮЛ")
    @allure.id(579874)
    def test_connect_promised_payment_b2b(self):
        self.personal_account_page.create_customer_with_type('organization')
        self.personal_account_page.dynamic_form.SAVE_BTN.click()
        self.personal_account_page.notifications.SUCCESS_CREATE_CLIENT.wait_to_be_visible()

        self.personal_account_page.notifications.SUCCESS_NOTIFICATIONS_CLOSE_BTN.click()
        self.personal_account_page.locators.CREATE_AGREEMENT_BTN.click()
        self.personal_account_page.dynamic_elements.CONTRACT_NUM.wait_to_be_visible()

        self.personal_account_page.fill_data_create_agreement(type_client='organization')
        self.personal_account_page.dynamic_form.CREATE_BTN.click()
        self.personal_account_page.notifications.SUCCESS_CREATE_CLIENT.wait_to_be_visible()

        self.personal_account_page.notifications.SUCCESS_NOTIFICATIONS_CLOSE_BTN.click()
        self.personal_account_page.locators.PERSONAL_ACCOUNTS_TAB.click()
        self.personal_account_page.locators.ADD_PERSONAL_ACCOUNT_BTN.click()
        self.personal_account_page.dynamic_form.CREATE_BTN.click()
        self.personal_account_page.notifications.SUCCESS_CREATE_CLIENT.wait_to_be_visible()
        self.personal_account_page.notifications.SUCCESS_NOTIFICATIONS_CLOSE_BTN.click()

        self.personal_account_page.locators.BURGER_MENU_BTN.click()
        self.personal_account_page.locators.BURGER_MENU_EL_BTN[3].click()

        self.promised_payment.CONNECT_BTN.wait_to_be_visible()
        self.promised_payment.CONNECT_BTN.click()
        self.promised_payment_form.CUSTOM_PARAM_BTN.click()
        self.promised_payment_form.fill_data_for_promised_payment()
        self.promised_payment_form.INNER_ACCEPT_BTN.click()
        self.personal_account_page.notifications.SUCCESS_CREATE_CLIENT.wait_to_be_visible()
        self.personal_account_page.notifications.SUCCESS_NOTIFICATIONS_CLOSE_BTN.click()

        self.promised_payment.PRODUCT_PROMISED_PAYMENT_FLD.wait_to_be_visible()

    @allure.title("01. Успешное подключение ОП без комиссии ФЛ")
    @allure.id(579843)
    def test_connect_promised_payment_b2c(self):
        self.personal_account_page.create_customer_with_type('individual')
        self.personal_account_page.dynamic_form.SAVE_BTN.click()
        self.personal_account_page.notifications.SUCCESS_CREATE_CLIENT.wait_to_be_visible()

        self.personal_account_page.notifications.SUCCESS_NOTIFICATIONS_CLOSE_BTN.click()
        self.personal_account_page.locators.CREATE_AGREEMENT_BTN.click()
        self.personal_account_page.dynamic_elements.CONTRACT_NUM.wait_to_be_visible()

        self.personal_account_page.fill_data_create_agreement(type_client='individual')
        self.personal_account_page.dynamic_form.CREATE_BTN.click()
        self.personal_account_page.notifications.SUCCESS_CREATE_CLIENT.wait_to_be_visible()

        self.personal_account_page.notifications.SUCCESS_NOTIFICATIONS_CLOSE_BTN.click()
        self.personal_account_page.locators.PERSONAL_ACCOUNTS_TAB.click()
        self.personal_account_page.locators.ADD_PERSONAL_ACCOUNT_BTN.click()
        self.personal_account_page.dynamic_form.CREATE_BTN.click()
        self.personal_account_page.notifications.SUCCESS_CREATE_CLIENT.wait_to_be_visible()
        self.personal_account_page.notifications.SUCCESS_NOTIFICATIONS_CLOSE_BTN.click()

        self.personal_account_page.locators.BURGER_MENU_BTN.click()
        self.personal_account_page.locators.BURGER_MENU_EL_BTN[3].click()

        self.promised_payment.CONNECT_BTN.wait_to_be_visible()
        self.promised_payment.CONNECT_BTN.click()
        self.promised_payment_form.CUSTOM_PARAM_BTN.click()
        self.promised_payment_form.fill_data_for_promised_payment()
        self.promised_payment_form.INNER_ACCEPT_BTN.click()
        self.personal_account_page.notifications.SUCCESS_CREATE_CLIENT.wait_to_be_visible()
        self.personal_account_page.notifications.SUCCESS_NOTIFICATIONS_CLOSE_BTN.click()

        self.promised_payment.PRODUCT_PROMISED_PAYMENT_FLD.wait_to_be_visible()

    @allure.title("04. Подключение ОП из списка продуктовых предложений")
    @allure.id(583495)
    def test_connect_promised_payment_from_list_product_offer(self):
        self.personal_account_page.create_customer_with_type('organization')
        self.personal_account_page.dynamic_form.SAVE_BTN.click()
        self.personal_account_page.notifications.SUCCESS_CREATE_CLIENT.wait_to_be_visible()

        self.personal_account_page.notifications.SUCCESS_NOTIFICATIONS_CLOSE_BTN.click()
        self.personal_account_page.locators.CREATE_AGREEMENT_BTN.click()
        self.personal_account_page.dynamic_elements.CONTRACT_NUM.wait_to_be_visible()

        self.personal_account_page.fill_data_create_agreement(type_client='organisation')
        self.personal_account_page.dynamic_form.CREATE_BTN.click()
        self.personal_account_page.notifications.SUCCESS_CREATE_CLIENT.wait_to_be_visible()

        self.personal_account_page.notifications.SUCCESS_NOTIFICATIONS_CLOSE_BTN.click()
        self.personal_account_page.locators.PERSONAL_ACCOUNTS_TAB.click()
        self.personal_account_page.locators.ADD_PERSONAL_ACCOUNT_BTN.click()
        self.personal_account_page.dynamic_form.CREATE_BTN.click()
        self.personal_account_page.notifications.SUCCESS_CREATE_CLIENT.wait_to_be_visible()
        self.personal_account_page.notifications.SUCCESS_NOTIFICATIONS_CLOSE_BTN.click()

        self.personal_account_page.locators.BURGER_MENU_BTN.click()
        self.personal_account_page.locators.BURGER_MENU_EL_BTN[3].click()

        self.promised_payment.CONNECT_BTN.wait_to_be_visible()
        self.promised_payment.CONNECT_BTN.click()

        self.promised_payment_form.PRODUCT_OFFER_FLD.select_by_value(value='ОП на 100 на 1 день с комиссией 0')
        self.promised_payment_form.INNER_ACCEPT_BTN.click()
        self.personal_account_page.notifications.SUCCESS_CREATE_CLIENT.wait_to_be_visible()
        self.personal_account_page.notifications.SUCCESS_NOTIFICATIONS_CLOSE_BTN.click()

        self.promised_payment.PRODUCT_PROMISED_PAYMENT_FLD.wait_to_be_visible()

    @allure.title("07. Подключение ОП с произвольными параметрами")
    @allure.id(583882)
    def test_connect_promised_payment_with_arbitrary_parameters(self):
        self.personal_account_page.create_customer_with_type("individual")
        self.personal_account_page.dynamic_form.SAVE_BTN.click()
        self.personal_account_page.notifications.SUCCESS_NOTIFICATIONS_CLOSE_BTN.click()

        self.create_request.CREATE_APPLICATION.click()
        self.create_request.CHOOSE_AGREEMENT_BTN.select_by_value(value='Автоматически')
        self.create_request.SAVE_BTN.click()
        self.inquiries_page.LOAD_SPIN_AFTER_SALE.wait_to_be_visible(timeout=60000)
        self.inquiries_page.LOAD_SPIN_AFTER_SALE.not_to_be_visible(timeout=60000)
        self.inquiries_page.PRODUCT_INFO_STATUS.wait_to_be_visible()

        self.inquiries_page.ADD_SALE_BTN.click()

        self.product_offer.PRODUCT_TYPE.select_by_value("Монопродукт")
        self.product_offer.PRODUCT_CATEGORY.select_by_value("Мобильная связь")
        self.product_offer.SEARCH_BTN.click()
        self.product_offer.PRODUCT_CARD.wait_to_be_visible()
        self.product_offer.PRODUCT_CARD.wait_elements_visible(0)
        self.product_offer.PRODUCT_CARD_SELECT_BTN[1].click()
        self.product_offer.ADD_BTN.click()

        self.inquiries_page.ADDED_PRODUCT_EDIT_BTN.wait_elements_visible(element_index=0)
        self.inquiries_page.ADDED_PRODUCT_EDIT_BTN[0].click(force=True)

        self.edit_product_form.RESOURCES_TAB.click()
        self.edit_product_form.BOOK_RESOURCES.wait_to_be_enabled(timeout=8000)

        self.edit_product_form.CHANGE_RESOURCES_BTN.click()
        self.change_product_form.FORM.wait_to_be_visible(timeout=8000)
        self.change_product_form.NUMBERS.wait_elements_visible(element_index=1)
        number = self.change_product_form.NUMBERS[1].text
        self.change_product_form.NUMBERS[1].click()
        self.change_product_form.INNER_ACCEPT_BTN.click()

        self.edit_product_form.BOOK_RESOURCES.wait_to_be_enabled(timeout=8000)
        self.edit_product_form.BOOK_RESOURCES.click()
        self.inquiries_page.LOAD_SPIN_FIRST.not_to_be_visible(timeout=8000)
        self.edit_product_form.CANCEL_BUTTON.click()
        self.personal_account_page.locators.CURRENT_CLIENT_LINK.click()

        self.personal_account_page.locators.CREATE_AGREEMENT_BTN.click()
        self.personal_account_page.dynamic_elements.CONTRACT_NUM.wait_to_be_visible()

        self.personal_account_page.fill_data_create_agreement(type_client='individual')
        self.personal_account_page.dynamic_form.CREATE_BTN.click()
        self.personal_account_page.notifications.SUCCESS_CREATE_CLIENT.wait_to_be_visible()

        self.personal_account_page.notifications.SUCCESS_NOTIFICATIONS_CLOSE_BTN.click()
        self.personal_account_page.locators.PERSONAL_ACCOUNTS_TAB.click()
        self.personal_account_page.locators.ADD_PERSONAL_ACCOUNT_BTN.click()
        self.personal_account_page.dynamic_form.CREATE_BTN.click()
        self.personal_account_page.notifications.SUCCESS_CREATE_CLIENT.wait_to_be_visible()
        self.personal_account_page.notifications.SUCCESS_NOTIFICATIONS_CLOSE_BTN.click()

        self.personal_account_page.locators.BURGER_MENU_BTN.click()
        self.personal_account_page.locators.BURGER_MENU_EL_BTN[3].click()

        self.promised_payment.CONNECT_BTN.wait_to_be_visible(timeout=60000)
        self.promised_payment.CONNECT_BTN.click()

        self.promised_payment_form.CUSTOM_PARAM_BTN.click()
        self.promised_payment_form.fill_data_for_promised_payment(commission_type=True, abonent=number)
        self.promised_payment_form.INNER_ACCEPT_BTN.click()
        self.personal_account_page.notifications.SUCCESS_CREATE_CLIENT.wait_to_be_visible()
        self.personal_account_page.notifications.SUCCESS_NOTIFICATIONS_CLOSE_BTN.click()

        self.promised_payment.PRODUCT_PROMISED_PAYMENT_FLD.wait_to_be_visible()
