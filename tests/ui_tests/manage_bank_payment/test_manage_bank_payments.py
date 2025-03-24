import re
import pytest
import allure
from playwright.sync_api import Page, APIRequestContext
from datetime import timedelta, timezone

from api.exceptions import CreatePaymentException
from api.requests.client_requests import ClientRequests
from api.requests.payments_requests import PaymentsUniblpRequests, PaymentUniblpInfo, PaymentsRequests
from api.requests.personal_account_requests import PersonalAccountRequests
from api.requests.registry_requests import RegistryRequests
from common.helpers.checker import wait_that
from common.helpers.data_generator import get_current_datetime_string_for_api, generate_random_number, \
    get_current_datetime_string, get_shifted_datetime
from common.helpers.time_helpers import delay
from pages.base_page import BasePage
from pages.client_profile_page import ClientProfilePage
from pages.locators.payments_elements import PaymentElements, PaymentDetailsElements
from pages.locators.registry_elements import RegistryElements, RegistryDetailsElements


@allure.epic("E2E_81 Управление банковскими платежами")
@allure.suite("E2E_81 Управление банковскими платежами")
class TestManageBankPayments:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_ui_stand_login: Page, api_request_auth_context: APIRequestContext):
        self.base_page = BasePage(nexign_ui_stand_login)
        self.client_profile_page = ClientProfilePage(nexign_ui_stand_login)
        self.registry_elements = RegistryElements(nexign_ui_stand_login)
        self.registry_details_elements = RegistryDetailsElements(nexign_ui_stand_login)
        self.payment_details_elements = PaymentDetailsElements(nexign_ui_stand_login)
        self.payment_elements = PaymentElements(nexign_ui_stand_login)
        self.client_request_api = ClientRequests(api_request_auth_context)
        self.personal_account_api = PersonalAccountRequests(api_request_auth_context)
        self.payment_api = PaymentsRequests(api_request_auth_context)
        self.payment_api_uniblp = PaymentsUniblpRequests(api_request_auth_context)
        self.registry_requests_api = RegistryRequests(api_request_auth_context)

    @allure.title("Отображение платежа в реестре платежей")
    @allure.id(580953)
    @allure.description("Отображение платежа в реестре платежей")
    @allure.link(url="https://confluence.nexign.com/pages/viewpage.action?pageId=462935916",
                 name="LLD Прием и аннулирование платежа")
    @allure.link(url="https://confluence.nexign.com/pages/viewpage.action?pageId=471415127",
                 name="ФС Прием платежей")
    @allure.tag("can_auth", "success")
    def test_payment_preview_in_registry_list(self, base_url: str, api_request_auth_context: APIRequestContext):
        clients = self.client_request_api.search_client(account_status_ids=[2], agreement_status_ids=[1],
                                                        customer_status_ids=[2], customer_name="Авто")
        client_data = self.personal_account_api.get_client_with_currency_type(clients, "RUB")
        payment_amount = generate_random_number(3)
        today = get_current_datetime_string_for_api(is_full_format=False)
        today_user_friendly_view = get_current_datetime_string(is_full_format=False)
        doc_number = generate_random_number(4)
        payment_data = PaymentUniblpInfo(
            item_type="CUSTOMER_ACCOUNT",
            amount=payment_amount,
            currency_code="RUB",
            account_id=client_data.account_id,
            document_number=doc_number,
            payment_date=get_shifted_datetime("+240m").replace(tzinfo=timezone(timedelta(hours=3))).isoformat(),
            payment_method_type="BANK_ACCOUNT_TRANSFER",
        )
        self.payment_api_uniblp.create_payment(payment_data)
        delay(2, reason="Время на проведение платежа")
        wait_that(
            lambda: self.registry_requests_api.get_registry_list(today, today, "-paymentDate").json()["items"][0][
                        "status"]["code"] == "SUCCEEDED",
            timeout=25, sleep_seconds=0.5, exception=CreatePaymentException,
            message="Платеж не появился в указанное время")

        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{client_data.customer_id}/overview")
        self.client_profile_page.locators.BURGER_MENU_BTN.click()
        self.client_profile_page.locators.BURGER_MENU_EL_BTN[3].click()

        self.registry_elements.PAYMENT_DATES_FIELDS.wait_to_be_visible()
        self.registry_elements.PAYMENT_DATES_FIELDS.to_contain_text(0, today_user_friendly_view)
        self.registry_elements.STATUS_FIELDS.to_contain_text(0, "Действует")
        self.registry_elements.CHECK_NUM_FIELDS.to_contain_text(0, str(doc_number))
        self.registry_elements.CHECK_SUM_FIELDS.to_contain_text(0, str(payment_data.amount))
        self.registry_elements.PAYMENT_SUM_FIELDS.to_contain_text(0, str(payment_data.amount))
        self.registry_elements.CASHIER_FIELDS.to_contain_text(0, "uniblp/uniblp")
        self.registry_elements.CHECK_NUM_FIELDS[0].click()

        form_title = f"Платёж от {today_user_friendly_view}"
        self.registry_details_elements.FORM_TITLE.wait_to_have_text(re.compile(form_title))
        self.registry_details_elements.PAYMENT_DETAILS.wait_to_have_count(5)
        self.registry_details_elements.PAYMENT_DETAILS[0].to_contain_text(today_user_friendly_view)
        self.registry_details_elements.PAYMENT_DETAILS[1].to_contain_text(str(payment_amount))
        self.registry_details_elements.PAYMENT_DETAILS[2].to_contain_text(str(doc_number))
        self.registry_details_elements.PAYMENT_DETAILS[3].to_contain_text("Банковский перевод")
        self.registry_details_elements.PAYMENT_DETAILS[4].to_contain_text("uniblp/uniblp")
        self.registry_details_elements.FORM_TABS[1].click()

        self.registry_details_elements.FORM_TABS[1].to_have_class("ant-tabs-tab ant-tabs-tab-active")
        self.registry_details_elements.GOAL_TABLE_FIRST_COLUMN[0].wait_to_have_text(
            f"Лицевой счет {client_data.account_id}")
        self.registry_details_elements.GOAL_TABLE_FIRST_COLUMN[1].wait_to_have_text("Исходная сумма:")
        self.registry_details_elements.GOAL_TABLE_FIRST_COLUMN[2].wait_to_have_text(f"{payment_amount}.00 RUB.")

    @allure.title("Отображение платежа в платежах клиента")
    @allure.id(580954)
    @allure.description("Отображение платежа в платежах клиента")
    @allure.link(url="https://confluence.nexign.com/pages/viewpage.action?pageId=462935916",
                 name="LLD Прием и аннулирование платежа")
    @allure.link(url="https://confluence.nexign.com/pages/viewpage.action?pageId=471415127",
                 name="ФС Прием платежей")
    @allure.tag("can_auth", "success")
    def test_payment_preview_in_payment_list(self, base_url: str, api_request_auth_context: APIRequestContext):
        clients = self.client_request_api.search_client(account_status_ids=[2], agreement_status_ids=[1],
                                                        customer_status_ids=[2], customer_name="Авто")
        client_data = self.personal_account_api.get_client_with_currency_type(clients, "RUB")
        payment_amount = generate_random_number(3)
        today_user_friendly_view = get_current_datetime_string(is_full_format=False)
        doc_number = generate_random_number(4)
        payment_data = PaymentUniblpInfo(
            item_type="CUSTOMER_ACCOUNT",
            amount=payment_amount,
            currency_code="RUB",
            account_id=client_data.account_id,
            document_number=doc_number,
            payment_date=get_shifted_datetime("+241m").replace(tzinfo=timezone(timedelta(hours=3))).isoformat(),
            payment_method_type="BANK_ACCOUNT_TRANSFER",
        )
        self.payment_api_uniblp.create_payment(payment_data)
        delay(2, reason="Время на проведение платежа")
        wait_that(
            lambda: self.payment_api.get_payments(client_data.account_id, "-paymentDate").json()["items"][0][
                        "status"]["code"] == "SUCCEEDED",
            timeout=25, sleep_seconds=0.5, exception=CreatePaymentException,
            message="Платеж не появился в указанное время")

        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{client_data.customer_id}/overview")
        self.client_profile_page.locators.CURRENT_PERSONAL_ACCOUNT_LINK.click()
        delay(1, reason="Время для смены контекста и содержания меню")
        self.client_profile_page.locators.BURGER_MENU_BTN.click()
        self.client_profile_page.locators.BURGER_MENU_EL_BTN[1].click()

        self.payment_elements.ACCOUNT_NUM.wait_to_have_text(client_data.account_number)
        self.payment_elements.USER_NAME.wait_to_have_text(client_data.customer_name)
        (self.payment_elements.USER_BALANCE.
         wait_to_have_text(re.compile(r"^(\d{1,3}\.\d{2})|(\d{1,3}\s\d{1,3}\.\d{2})$")))

        self.payment_elements.CHECK_NUM_FIELDS.wait_to_be_visible()
        self.payment_elements.CHECK_NUM_FIELDS.to_contain_text(0, str(doc_number))
        self.payment_elements.PAYMENT_DATES_FIELDS.to_contain_text(0, today_user_friendly_view)
        self.payment_elements.REGISTRY_DATES_FIELDS.to_contain_text(0, today_user_friendly_view)
        self.payment_elements.SUM_FIELDS.to_contain_text(0, f"{payment_data.amount}.00")
        self.payment_elements.STATUS_FIELDS.to_contain_text(0, "Действует")

        self.payment_elements.CHECK_NUM_FIELDS[0].click()

        self.payment_details_elements.FORM_TITLE.wait_to_have_text("Платёж")
        self.payment_details_elements.FORM_STATUS.wait_to_have_text("Действует")
        (self.payment_details_elements.SUBTITLE.
         wait_to_have_text(re.compile(f"На сумму {payment_data.amount}.00 от {today_user_friendly_view}")))
        self.payment_details_elements.PAYMENT_DETAILS[0].to_contain_text(today_user_friendly_view)
        self.payment_details_elements.PAYMENT_DETAILS[1].to_contain_text(today_user_friendly_view)
        self.payment_details_elements.PAYMENT_DETAILS[2].to_contain_text(str(doc_number))
        self.payment_details_elements.PAYMENT_DETAILS[3].to_contain_text(f"{payment_data.amount}.00")
        self.payment_details_elements.PAYMENT_DETAILS[4].wait_to_have_text(re.compile(f"{payment_data.amount}.00\sRUB"))
        self.payment_details_elements.PAYMENT_DETAILS[6].to_contain_text("PM:pm_gateway")
        self.payment_details_elements.PAYMENT_DETAILS[8].to_contain_text("uniblp")
        self.payment_details_elements.FORM_TABS[1].click()

        self.payment_details_elements.FORM_TABS[1].to_have_class("ant-tabs-tab ant-tabs-tab-active")
        self.payment_details_elements.PAYMENT_TYPE_BTN[0].wait_to_have_text("Погашения: 0.00")
        self.payment_details_elements.PAYMENT_TYPE_BTN[1].wait_to_have_text("Корректировки: 0.00")
        self.payment_details_elements.PAYMENT_TYPE_BTN[0].element_have_css_color("color", "deep_blue")
        self.payment_details_elements.PAYMENT_DATE_FIELDS.wait_not_to_be_visible()
        self.payment_details_elements.PAYMENT_TYPE_BTN[1].click()
        self.payment_details_elements.PAYMENT_TYPE_BTN[1].element_have_css_color("color", "deep_blue")
        self.payment_details_elements.PAYMENT_DATE_FIELDS.wait_not_to_be_visible()
