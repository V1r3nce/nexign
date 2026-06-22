from datetime import timedelta

import allure
import pytest

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from api.nbss.finances.billing_discount import BillingDiscountsRequests
from common.helpers.data_generator import (
    generate_english_string,
    generate_russian_string,
)
from common.helpers.env_helper import BASE_URL
from common.helpers.time_helpers import get_current_moscow_datetime
from pages.locators.nbss.finances.discount_and_charges import (
    AddBillingDiscountFormStep4,
    AddBillingDiscountOrChargeFormStep3,
    AddProductOfferForm,
    FilterForm,
)

# from db.requests.db_requests import UDBRequests
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.finances.discount_and_charges import DiscountAndChargesPage


@allure.link(
    url="confluence.nexign.com/pages/viewpage.action?pageId=659783906", name="8.6. Управление биллинговыми скидками"
)
@allure.epic("E2E_67 Управление биллинговыми скидками")
@allure.suite("E2E_67 Управление биллинговыми скидками")
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestEditBillingDiscount:
    @pytest.fixture(autouse=True)
    def setup(
        self,
        nexign_stand_login,
        create_organization,
        # create_udb_connection: UDBRequests
    ) -> None:
        self.client_profile = ClientProfilePage()
        self.client_request_api = ClientInquiriesRequests()
        self.discount_page = DiscountAndChargesPage()
        self.discount_requests_api = BillingDiscountsRequests()
        self.add_discount_form_step_2 = AddProductOfferForm()
        self.filter_form = FilterForm()
        self.start_dt = get_current_moscow_datetime()
        self.start_date = self.start_dt.strftime("%d.%m.%Y")
        self.end_date = (self.start_dt + timedelta(days=30)).strftime("%d.%m.%Y")
        self.discount_amount = "50"
        self.priority = "1"
        self.add_discount_form_step_4 = AddBillingDiscountFormStep4()
        self.add_discount_form_step_3 = AddBillingDiscountOrChargeFormStep3()
        # self.udb: UDBRequests = create_udb_connection

    @allure.title("19. Сохранение истории создания шаблона биллинговых скидок")
    @allure.id(936943)
    def test_delete_billing_discount(self) -> None:
        discount_scheme_name_ru = f"Тестовая_биллинговая_скидка_{generate_russian_string(6)}"
        discount_scheme_name_en = f"Test_billing_discount_{generate_english_string(6)}"

        # discount_request = self.udb.discount_template_compare()
        self.client_profile.open(f"{BASE_URL}welcome")
        self.client_profile.locators.BURGER_MENU.select_by_value("Биллинг > Скидки/доначисления")
        self.discount_page.locators.SELECTED_TAB_TITLE.wait_to_have_text("Скидки/доначисления")

        self.discount_page.locators.ADD_BTN[0].wait_to_be_enabled(timeout=15000)
        self.discount_page.locators.ADD_BTN[0].click()
        self.discount_page.fill_discount_data(
            discount_scheme_name_ru=discount_scheme_name_ru,
            discount_scheme_name_en=discount_scheme_name_en,
            start_date=self.start_date,
            end_date=self.end_date,
        )
        self.discount_page.locators.ADD_BTN[2].wait_to_be_enabled(timeout=15000)
        self.discount_page.locators.ADD_BTN[2].click()
        self.discount_page.fill_discount_action()

        with allure.step("Применение фильтра по типу скидки"):
            self.discount_page.locators.FILTER_BTN.wait_to_be_enabled(timeout=15000)
            self.discount_page.locators.FILTER_BTN.click()
            self.filter_form.TYPE.select_by_value("Скидки")
            self.filter_form.SET_BTN.click()

        with allure.step("Проверяем, что скидка отображается"):
            self.discount_page.locators.DISCOUNTS.wait_to_have_count(1, timeout=10000)
            self.discount_page.check_properties(start_date=self.start_date, end_date=self.end_date)

        with allure.step("Удаление скидку"):
            self.discount_page.locators.DISCOUNT_DELETE_BTN.click()
            self.discount_page.locators.MODAL_SECOND_BTN.click()

        with allure.step("Проверяем, что скидка отсутствует"):
            self.discount_page.locators.DISCOUNTS.wait_to_have_count(0)
