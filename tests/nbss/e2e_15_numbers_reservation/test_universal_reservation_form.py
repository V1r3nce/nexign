import allure
import pytest

from api.lis_requests.equipment import EquipmentRequests
from api.lis_requests.phone_numbers import PhoneNumbersRequests
from api.lis_requests.sim_cards import SimCardsRequests
from common.exceptions import NexignBaseException
from common.helpers.checker import check_that
from common.helpers.env_helper import BASE_URL
from common.helpers.string_helper import convert_amount_to_balance_string
from models.client import OrganizationClient
from models.context import test_context
from models.inquiry import prepare_inquiries
from models.product import B2BProducts, DefaultStandardId, product_names_map
from models.services import Services
from pages.base_page import BasePage
from pages.locators.nbss.inquiries_elements import ProductEditForm, ReserveResourcesForm
from pages.locators.nbss.select_product_offers_form import SelectProductOffersFormElements
from pages.nbss.inquiries_page import InquiriesPage


@allure.epic("E2E_15 Бронирование номеров")
@allure.suite("E2E_15 Бронирование номеров")
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestUniversalReservationForm:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login) -> None:
        self.sim_requests = SimCardsRequests()
        self.equipment_requests = EquipmentRequests()
        self.number_requests = PhoneNumbersRequests()

        self.base_page = BasePage()
        self.inquiries_page = InquiriesPage()
        self.product_offer_form = SelectProductOffersFormElements()
        self.product_edit_form = ProductEditForm()
        self.reserve_form = ReserveResourcesForm()

        self.product = product_names_map.get(B2BProducts.mobile)
        self.subscription_period = "мес"
        self.subscription_period_count = "1"

    @allure.title("01. Бронирование мобильного номера при продаже B2B (Просмотр выбранных номеров)")
    @allure.id(654955)
    @pytest.mark.parametrize("create_switch", [DefaultStandardId.mobile], indirect=True)
    def test_mobile_phone_reservation_view_selected_numbers(
        self, create_organization: OrganizationClient, create_switch, create_number_and_start_exploitation
    ) -> None:
        switch_name = create_switch.name
        created_number = create_number_and_start_exploitation
        number_last_digit = str(created_number)[-1]
        self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")
        self.inquiries_page.sale_initialization(
            test_context.client, create_add_agreement="manual", need_contact_data=True, priority="Высокий", add_kp="no"
        )

        self.inquiries_page.locators.ADD_SALE_BTN.click()
        self.product_offer_form.REGION.wait_to_be_visible()
        region = self.product_offer_form.REGION.text

        self.inquiries_page.find_product_in_form(self.product, "Мобильная связь")
        self.inquiries_page.check_inquiry_state_after_product_addition(product_count=1, region=region)

        self.inquiries_page.locators.TABS[1].click()
        self.inquiries_page.locators.PRODUCTS_NAME[0].wait_to_have_text(self.product)
        self.inquiries_page.locators.PRODUCTS_CONTRACT_NUM[0].wait_to_have_text("Не выбран")
        self.inquiries_page.locators.PRODUCTS_PERSONAL_ACCOUNT_NUM[0].wait_to_have_text("Не распределен")
        self.inquiries_page.open_product_info_from_order_elements_tab()
        self.inquiries_page.check_characteristics_tab()
        self.product_edit_form.INNER_CANCEL_BTN.click()

        self.inquiries_page.locators.TABS[0].click()
        self.inquiries_page.locators.ADDED_PRODUCT_EDIT_BTN[0].wait_to_be_visible()
        self.inquiries_page.locators.ADDED_PRODUCT_EDIT_BTN[0].click(force=True)
        self.product_edit_form.RESOURCES_TAB.wait_to_be_visible(timeout=10000)
        self.product_edit_form.RESOURCES_TAB.click()
        self.inquiries_page.open_mobile_phone_reserve_form(self.product)

        self.reserve_form.SWITCH.wait_to_have_text("")
        self.reserve_form.SWITCH.select_by_value(switch_name)
        self.reserve_form.FREE_FOR.to_contain_text("3")
        self.reserve_form.STANDARD_INPUT.wait_to_have_text("GSM")
        self.reserve_form.REGION.wait_to_have_text(region)

        self.inquiries_page.search_number_by_mask(f"%{number_last_digit}")
        check_that(
            lambda: all(number.endswith(number_last_digit) for number in self.reserve_form.NUMBER.text_list),
            exception=NexignBaseException,
            message="Мобильные номера, оканчивающиеся на 7 не найдены",
        )

        self.reserve_form.NUMBER_CHECKBOX.click(0)
        phone_number = self.reserve_form.NUMBER[0].text
        self.reserve_form.ONLY_CHOOSE_TEXT.wait_to_have_text("Только выбранные: 1")
        self.reserve_form.INFO_MESSAGE.wait_to_have_text("Осталось выбрать 0 из 1")

        self.reserve_form.ONLY_CHOOSE_RADIOBUTTON.click()
        self.inquiries_page.check_number_reserve_fields_not_displayed()

        self.reserve_form.BOOK_BTN.click()
        self.reserve_form.TITLE.not_to_be_visible(timeout=10000)
        self.product_edit_form.PHONE_NUMBER.wait_to_have_text(phone_number)

    @allure.title("02. Бронирование мобильного номера при продаже B2B (Смена класса номера)")
    @allure.id(654971)
    @pytest.mark.parametrize("create_switch", [DefaultStandardId.mobile], indirect=True)
    def test_mobile_phone_reservation_change_number_class(
        self, create_organization: OrganizationClient, create_switch, create_number_and_start_exploitation
    ) -> None:
        switch_name = create_switch.name
        created_number = create_number_and_start_exploitation
        number_last_digit = str(created_number)[-1]
        self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")
        self.inquiries_page.sale_initialization(
            test_context.client, create_add_agreement="manual", need_contact_data=True, priority="Высокий", add_kp="no"
        )

        self.inquiries_page.locators.ADD_SALE_BTN.click()
        self.inquiries_page.find_product_in_form(self.product, "Мобильная связь")
        self.inquiries_page.check_inquiry_state_after_product_addition(product_count=1)

        self.inquiries_page.locators.ADDED_PRODUCT_EDIT_BTN[0].wait_to_be_visible()
        self.inquiries_page.locators.ADDED_PRODUCT_EDIT_BTN[0].click(force=True)
        self.product_edit_form.RESOURCES_TAB.click()
        self.inquiries_page.open_mobile_phone_reserve_form(self.product)

        self.reserve_form.SWITCH.wait_to_have_text("")
        self.reserve_form.SWITCH.select_by_value(switch_name)
        self.inquiries_page.search_number_by_mask(f"%{number_last_digit}")
        check_that(
            lambda: all(number.endswith(number_last_digit) for number in self.reserve_form.NUMBER.text_list),
            exception=NexignBaseException,
            message="Мобильные номера, оканчивающиеся на 7 не найдены",
        )
        self.reserve_form.NUMBER_CHECKBOX.click(0)
        self.reserve_form.INFO_MESSAGE.wait_to_have_text("Осталось выбрать 0 из 1")

        self.reserve_form.NUMBER_CLASS.not_to_be_enabled()
        self.reserve_form.NUMBER_CLASS_TOOLTIP.hover()
        self.reserve_form.NUMBER_CLASS_TOOLTIP_TEXT.wait_to_have_text(
            'Изменить фильтр можно, если ресурсы не выбраны. Для очистки списка выбранных ресурсов нажмите кнопку очистки у переключателя "Только выбранные"'
        )
        self.reserve_form.CLEAR_SELECTED_BTN.click()
        self.reserve_form.CLEAR_SELECTED_CONFIRM_BTN.click()

        self.reserve_form.INFO_MESSAGE.wait_to_have_text("Осталось выбрать 1 из 1")
        self.reserve_form.NUMBER_CLASS.select_by_value("Платиновый")
        self.reserve_form.SEARCH_BUTTON.click()
        self.reserve_form.NUMBER_CLASS_NAME.wait_to_have_count(0)

    @allure.title("04. Бронирование стационарного номера при продаже B2B (базовый сценарий) (PSTN)")
    @allure.id(654972)
    def test_stationary_phone_reservation(self, create_organization: OrganizationClient) -> None:
        self.product = "Телефонная связь"

        self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")
        self.inquiries_page.sale_initialization(
            test_context.client, create_add_agreement="manual", need_contact_data=True, priority="Высокий", add_kp="no"
        )

        self.inquiries_page.locators.ADD_SALE_BTN.click()
        self.inquiries_page.find_product_in_form(self.product, "Стационарная телефония")
        self.inquiries_page.check_inquiry_state_after_product_addition(product_count=1)

        self.inquiries_page.locators.ADDED_PRODUCT_EDIT_BTN[0].wait_to_be_visible()
        self.inquiries_page.locators.ADDED_PRODUCT_EDIT_BTN[0].click(force=True)
        self.product_edit_form.RESOURCES_TAB.click()
        self.product_edit_form.RESERVE_RESOURCES_BTN.click()

        self.inquiries_page.search_number_by_mask("%%")
        self.reserve_form.NUMBER_CHECKBOX.click(0)
        phone_number = self.reserve_form.NUMBER[0].text
        self.reserve_form.BOOK_BTN.click()

        self.product_edit_form.CHANGE_NUMBER_BTN.wait_to_be_visible()
        self.product_edit_form.DELETE_RESOURSE_BTN.wait_to_be_visible()
        self.product_edit_form.PHONE_NUMBER.wait_to_have_text(phone_number, timeout=10000)

    @allure.title("05. Базовый сценарий бронирования физической SIM-карты (B2B)")
    @allure.id(654973)
    def test_sim_card_reservation(self, create_organization: OrganizationClient) -> None:
        services = Services().set

        self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")
        self.inquiries_page.sale_initialization(
            test_context.client, create_add_agreement="manual", need_contact_data=True, priority="Высокий", add_kp="no"
        )

        test_context.client.inquiry_list = prepare_inquiries(category="mobile", product_offering_id=500017)
        product = self.inquiries_page.add_product_offer_to_commercial_order(test_context.client.inquiry.product)

        one_time_price = convert_amount_to_balance_string(product.one_time_payment)
        subscription_fee = convert_amount_to_balance_string(product.subscription_fee)

        self.inquiries_page.check_inquiry_state_after_product_addition(product_count=1)

        self.inquiries_page.locators.TABS[1].click()
        self.inquiries_page.locators.PRODUCTS_NAME[0].wait_to_have_text(self.product)
        self.inquiries_page.locators.PRODUCTS_CONTRACT_NUM[0].wait_to_have_text("Не выбран")
        self.inquiries_page.locators.PRODUCTS_PERSONAL_ACCOUNT_NUM[0].wait_to_have_text("Не распределен")
        self.inquiries_page.locators.ADDED_PRODUCT_VISIBLE_BTN[0].wait_to_be_visible(timeout=15000)
        self.inquiries_page.locators.ADDED_PRODUCT_VISIBLE_BTN[0].hover()
        self.inquiries_page.locators.ADDED_PRODUCT_VISIBLE_BTN[0].click(force=True)

        self.inquiries_page.check_characteristics_tab()
        self.inquiries_page.check_prices_tab(
            one_time_price=one_time_price,
            one_time_discount="0",
            one_time_final_price=one_time_price,
            periodic_price=subscription_fee,
            periodic_discount="0",
            periodic_final_price=subscription_fee,
            subscription_period=self.subscription_period,
            subscription_period_count=self.subscription_period_count,
        )
        self.product_edit_form.SERVICES_TAB.click()
        self.product_edit_form.MODAL_SECOND_BTN.wait_to_be_visible()
        self.product_edit_form.MODAL_SECOND_BTN.click()
        self.inquiries_page.check_services_tab(services)
        self.product_edit_form.INNER_CANCEL_BTN.click()

        self.inquiries_page.locators.TABS[0].click()
        self.inquiries_page.locators.ADDED_PRODUCT_EDIT_BTN[0].click(force=True)
        self.product_edit_form.RESOURCES_TAB.click()
        self.product_edit_form.RESERVE_RESOURCES_SELECT.select_by_value("SIM-карта")
        self.inquiries_page.search_number_by_mask("%%")
        self.reserve_form.NUMBER.wait_to_have_count_or_greater(1)
        self.reserve_form.SIM_CHECKBOX.click(0)
        ICCID = self.reserve_form.SIM_ICC[0].text
        self.reserve_form.BOOK_BTN.click()

        self.product_edit_form.CHANGE_NUMBER_BTN.wait_to_be_visible()
        self.product_edit_form.DELETE_RESOURSE_BTN.wait_to_be_visible()
        self.product_edit_form.ICCID.wait_to_have_text(ICCID, timeout=10000)

    @allure.title("06. Бронирование мобильного номера (B2B)(SIM забронирована)")
    @allure.id(663724)
    def test_phone_number_reservation_after_sim_card(self, create_organization: OrganizationClient) -> None:
        self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")
        self.inquiries_page.sale_initialization(
            test_context.client, create_add_agreement="manual", need_contact_data=True, priority="Высокий", add_kp="no"
        )

        self.inquiries_page.locators.ADD_SALE_BTN.click()
        self.inquiries_page.find_product_in_form(self.product, "Мобильная связь")
        self.inquiries_page.check_inquiry_state_after_product_addition(product_count=1)

        self.inquiries_page.locators.ADDED_PRODUCT_EDIT_BTN[0].click(force=True)
        self.product_edit_form.RESOURCES_TAB.click()
        self.product_edit_form.RESERVE_RESOURCES_SELECT.select_by_value("SIM-карта")
        self.reserve_form.SWITCH.wait_to_be_visible()
        self.reserve_form.SWITCH.select_by_index(0)
        self.reserve_form.SEARCH_BUTTON.click()
        self.reserve_form.SIM_CHECKBOX.click(0)
        ICCID = self.reserve_form.SIM_ICC[0].text
        switch = self.reserve_form.SIM_SWITCH[0].text
        self.reserve_form.SWITCH.wait_to_have_text(switch)
        self.reserve_form.BOOK_BTN.click()

        self.product_edit_form.CHANGE_NUMBER_BTN.wait_to_be_visible()
        self.product_edit_form.DELETE_RESOURSE_BTN.wait_to_be_visible()
        self.product_edit_form.ICCID.wait_to_have_text(ICCID, timeout=10000)

        self.product_edit_form.RESERVE_RESOURCES_SELECT.select_by_value("Телефонный номер (мобильный)")
        self.inquiries_page.check_switch_selected_and_disabled(switch_name=switch)

    @allure.title("07. Бронирования физической SIM-карты (B2B)(MSISDN забронирован)")
    @allure.id(663680)
    def test_sim_card_reservation_after_phone_number(self, create_organization: OrganizationClient) -> None:
        self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")
        self.inquiries_page.sale_initialization(
            test_context.client, create_add_agreement="manual", need_contact_data=True, priority="Высокий", add_kp="no"
        )

        self.inquiries_page.locators.ADD_SALE_BTN.click()
        self.inquiries_page.find_product_in_form(self.product, "Мобильная связь")
        self.inquiries_page.check_inquiry_state_after_product_addition(product_count=1)

        self.inquiries_page.locators.ADDED_PRODUCT_EDIT_BTN[0].click(force=True)
        self.product_edit_form.RESOURCES_TAB.click()
        self.product_edit_form.RESERVE_RESOURCES_SELECT.select_by_value("Телефонный номер (мобильный)")
        self.reserve_form.SWITCH.wait_to_be_visible()
        self.reserve_form.SWITCH.select_by_index(0)
        self.reserve_form.SEARCH_BUTTON.click()
        self.reserve_form.NUMBER_CHECKBOX.click(0)
        phone_number = self.reserve_form.NUMBER[0].text
        switch = self.reserve_form.NUMBER_SWITCH[0].text
        self.reserve_form.SWITCH.wait_to_have_text(switch)
        self.reserve_form.BOOK_BTN.click()

        self.product_edit_form.LOAD_SPINS.wait_not_to_be_visible()
        self.product_edit_form.CHANGE_NUMBER_BTN.wait_to_be_visible()
        self.product_edit_form.DELETE_RESOURSE_BTN.wait_to_be_visible()
        self.product_edit_form.PHONE_NUMBER.wait_to_have_text(phone_number, timeout=10000)

        self.product_edit_form.RESERVE_RESOURCES_SELECT.select_by_value("SIM-карта")

    @allure.title("08. Отмена бронирования")
    @allure.id(656661)
    def test_cancel_reservation(self, create_organization: OrganizationClient) -> None:
        self.product = "Гибкий бизнес"

        self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")
        self.inquiries_page.sale_initialization(
            test_context.client, create_add_agreement="manual", need_contact_data=True, priority="Высокий", add_kp="no"
        )

        self.inquiries_page.locators.ADD_SALE_BTN.click()
        self.inquiries_page.find_product_in_form(self.product, "Мобильная связь")
        self.inquiries_page.check_inquiry_state_after_product_addition(product_count=1)

        self.inquiries_page.locators.ADDED_PRODUCT_EDIT_BTN[0].click(force=True)
        self.product_edit_form.RESOURCES_TAB.click()
        iccid, number = self.inquiries_page.auto_reserve_phone_number_resources()

        self.product_edit_form.CHANGE_ICCID_BTN.wait_to_be_visible()
        self.product_edit_form.CHANGE_NUMBER_BTN.wait_to_be_visible()
        self.product_edit_form.DELETE_RESOURSE_BTN.wait_to_have_count(2)

        self.product_edit_form.ICCID.wait_to_have_text(iccid)
        self.product_edit_form.DELETE_RESOURSE_BTN.click(0)
        self.product_edit_form.ICCID.wait_to_have_text("—", timeout=10000)

        self.product_edit_form.PHONE_NUMBER.wait_to_have_text(number)
        self.product_edit_form.DELETE_RESOURSE_BTN.click(0)
        self.product_edit_form.PHONE_NUMBER.wait_to_have_text("—", timeout=10000)
