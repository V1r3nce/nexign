from pathlib import Path
from typing import Callable

import allure
import pytest

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from api.nbss.personal_account_requests import PersonalAccountRequests
from common.helpers.data_generator import get_shifted_datetime_string
from common.helpers.env_helper import BASE_URL
from models.client import OrganizationClient
from models.context import test_context
from models.inquiry import prepare_inquiries
from models.product import B2BProducts, product_names_map
from pages.base_page import BasePage
from pages.locators.nbss.client.edit_product_activation_date_form import EditExecutionDateForm
from pages.locators.nbss.dynamic_form_elements import CreateSalesAndServiceManagement
from pages.locators.nbss.select_product_offers_form import SelectProductOffersFormElements
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.inquiries_page import InquiriesPage

OUT = Path("dom_capture")


@allure.epic("E2E_62_29 Сбор DOM (временный инструмент)")
@allure.suite("E2E_62_29 Сбор DOM")
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestCaptureDom:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login, create_organization: OrganizationClient) -> None:
        self.base_page = BasePage()
        self.client_profile = ClientProfilePage()
        self.inquiries_page = InquiriesPage()
        self.product_offer_form = SelectProductOffersFormElements()
        self.create_request_form = CreateSalesAndServiceManagement()
        self.edit_date_form = EditExecutionDateForm()
        self.client_inquiries_requests = ClientInquiriesRequests()
        self.personal_account_api = PersonalAccountRequests()
        self.future_date = get_shifted_datetime_string("+1d", template="%d.%m.%Y %H:%M")
        self.product_future = product_names_map[B2BProducts.mobile_on_date]
        OUT.mkdir(exist_ok=True)

    def _dump(self, name: str) -> None:
        (OUT / f"{name}.html").write_text(test_context.page.content(), encoding="utf-8")

    def _safe(self, name: str, action: Callable[[], None]) -> None:
        with allure.step(f"Дамп: {name}"):
            try:
                action()
            except Exception as exc:
                (OUT / f"{name}__ERROR.txt").write_text(repr(exc), encoding="utf-8")
            self._dump(name)

    def _overview(self) -> None:
        self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")

    @allure.title("Сбор DOM: сайдбар регистрации 'Создание продажи и управления услугами'")
    def test_capture_registration_sidebar(self) -> None:
        self._safe("reg_00_overview", self._overview)
        self._safe("reg_01_sidebar_open", lambda: self.inquiries_page.locators.CREATE_APPLICATION.click())
        self._safe("reg_02_sidebar_loaded", lambda: self.create_request_form.NEED_SPD.wait_to_be_visible(timeout=25000))
        self._safe("reg_03_future_checked", lambda: self.create_request_form.SCHEDULE_EXECUTION_CHECKBOX.click())

    @allure.title("Сбор DOM: шаг 'Управление составом заказа' — вкладки, сайдбар даты, форма выбора ПП, Экспресс ПТВ")
    def test_capture_order_step(self) -> None:
        user_id = test_context.client.user_id
        self._safe("ord_00_overview", self._overview)
        self._safe(
            "ord_01_after_sale",
            lambda: self.inquiries_page.sale_initialization(
                add_kp="auto", future_date=self.future_date, verify_open=False
            ),
        )
        self._safe("ord_02_created_inquiry", lambda: self.client_profile.open_created_inquiry(user_id))

        def add_product() -> None:
            test_context.client.inquiry.product.product_name = self.product_future
            self.inquiries_page.add_product_offer_to_commercial_order(test_context.client.inquiry.product)

        self._safe("ord_03_active_step", add_product)
        self._safe("ord_04_order_elements_tab", lambda: self.inquiries_page.open_tab("Элементы заказа"))
        self._safe("ord_05_sale_card_tab", lambda: self.inquiries_page.open_tab("Карточка продажи"))

        def open_sidebar() -> None:
            self.inquiries_page.open_tab("Активный шаг")
            self.inquiries_page.locators.EXECUTION_DATE_EDIT_BTN.click()

        self._safe("ord_06_edit_date_sidebar", open_sidebar)
        self._safe("ord_07_edit_date_calendar", lambda: self.edit_date_form.EXECUTION_DATE.click())
        self._safe("ord_08_reopen_inquiry", lambda: self.client_profile.open_created_inquiry(user_id))

        def open_product_form() -> None:
            self.inquiries_page.locators.ADD_SALE_BTN.click()
            self.product_offer_form.SEARCH_BTN.wait_to_be_enabled(timeout=15000)

        self._safe("ord_09_product_select_form", open_product_form)
        self._safe(
            "ord_10_product_form_future_date",
            lambda: self.inquiries_page.set_execution_date_on_product_form(self.future_date),
        )
        self._safe("ord_11_express_ptv", lambda: self.product_offer_form.EXPRESS_PTV.click())

    @allure.title("Сбор DOM: шаг 'Ожидание даты выполнения заказа' + сайдбар правки даты на нём")
    def test_capture_waiting_step(self) -> None:
        user_id = test_context.client.user_id
        self._safe("wait_00_overview", self._overview)
        self._safe(
            "wait_01_after_sale",
            lambda: self.inquiries_page.sale_initialization(
                add_kp="auto", future_date=self.future_date, verify_open=False
            ),
        )
        self._safe("wait_02_created_inquiry", lambda: self.client_profile.open_created_inquiry(user_id))

        def add_and_ready() -> None:
            test_context.client.inquiry.product.product_name = self.product_future
            self.inquiries_page.add_product_offer_to_commercial_order(test_context.client.inquiry.product)
            self.inquiries_page.auto_reserve_all_resources("mobile")
            self.inquiries_page.check_configuration()

        self._safe("wait_03_ready_to_next", add_and_ready)

        def to_waiting() -> None:
            self.inquiries_page.locators.NEXT_STEP_BTN.click()
            self.inquiries_page.locators.INQUIRY_STEP.to_contain_text("Ожидание даты выполнения заказа", timeout_sec=180)

        self._safe("wait_04_waiting_step", to_waiting)
        self._safe("wait_05_edit_date_sidebar", lambda: self.inquiries_page.locators.EXECUTION_DATE_EDIT_BTN.click())

    @allure.title("Сбор DOM: продуктовый профиль — смена ПП, добавить опцию, отключение, редактирование характеристик")
    def test_capture_product_profile(self) -> None:
        def sell_active() -> None:
            self.personal_account_api.create_agreement_and_account(test_context.client)
            self.client_inquiries_requests.product_sale(
                inquiry=prepare_inquiries(category=["mobile"], product_offering_id=[B2BProducts.mobile], as_list=False)
            )

        self._safe("pp_00_sell_active", sell_active)
        products_url = f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/products"

        def change_product() -> None:
            self.base_page.open(products_url)
            self.client_profile.locators.PRODUCT_NAME.wait_to_be_visible(timeout=15000)
            self.client_profile.locators.PRODUCTS_UPDATE_BTN.click()
            self.client_profile.locators.SUBSCRIBERS_DETAILS_OPEN_BTN[0].click()
            self.client_profile.locators.LOAD_SPINS.not_to_be_visible(timeout=8000)
            self.client_profile.locators.PRODUCTS_OPTIONS_CHANGE_MAIN_RODUCT_BTN.click()

        self._safe("pp_01_change_product_form", change_product)

        def add_option() -> None:
            self.base_page.open(products_url)
            self.client_profile.locators.PRODUCT_NAME.wait_to_be_visible(timeout=15000)
            self.client_profile.locators.PRODUCTS_UPDATE_BTN.click()
            self.client_profile.locators.PRODUCTS_OPTIONS_OPEN_BTN[0].click()
            self.client_profile.locators.PRODUCTS_OPTIONS_ADD_BTN.click()

        self._safe("pp_02_add_option_form", add_option)

        def disconnect() -> None:
            self.base_page.open(products_url)
            self.client_profile.locators.PRODUCT_NAME.wait_to_be_visible(timeout=15000)
            self.client_profile.locators.PRODUCTS_DETAILS_OPEN_BTN[0].click(force=True)
            self.client_profile.locators.TURN_OFF_BTN.click(force=True)

        self._safe("pp_03_disconnect_sidebar", disconnect)

        def edit_characteristics() -> None:
            self.base_page.open(products_url)
            self.client_profile.locators.PRODUCT_NAME.wait_to_be_visible(timeout=15000)
            self.client_profile.locators.PRODUCTS_DETAILS_OPEN_BTN[0].click(force=True)
            self.client_profile.locators.PRODUCT_EDIT_BTN.click()

        self._safe("pp_04_edit_characteristics_form", edit_characteristics)
