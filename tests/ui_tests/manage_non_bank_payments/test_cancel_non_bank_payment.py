import re

import allure
import pytest
from playwright.sync_api import APIRequestContext, Page

from api.requests.payments_requests import PaymentInfo, PaymentsRequests
from api.requests.personal_account_requests import PersonalAccountRequests
from api.requests.registry_requests import RegistryRequests
from common.helpers.data_generator import (
    generate_random_number,
    get_current_datetime_string,
    get_current_datetime_string_for_api,
)
from common.helpers.time_helpers import delay
from pages.base_page import BasePage
from pages.client_profile_page import ClientProfilePage
from pages.locators.dynamic_form_elements import CancelPaymentForm
from pages.locators.inquiries_page import InquiriesPage
from pages.locators.payments_elements import PaymentDetailsElements
from pages.locators.registry_elements import RegistryElements
from pages.payments_page import PaymentsPage


@allure.suite("E2E_82 Управление небанковскими и наличными платежами")
class TestCancelNonBankPayments:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_ui_stand_login: Page, api_request_auth_context: APIRequestContext):
        self.base_page = BasePage(nexign_ui_stand_login)
        self.client_profile_page = ClientProfilePage(nexign_ui_stand_login)
        self.registry_elements = RegistryElements(nexign_ui_stand_login)
        self.personal_account_api = PersonalAccountRequests(api_request_auth_context)
        self.payment_api = PaymentsRequests(api_request_auth_context)
        self.registry_requests_api = RegistryRequests(api_request_auth_context)
        self.payment_page = PaymentsPage(nexign_ui_stand_login)
        self.payment_details_elements = PaymentDetailsElements(nexign_ui_stand_login)
        self.cancel_payment_form = CancelPaymentForm(nexign_ui_stand_login)
        self.inquiries_page = InquiriesPage(nexign_ui_stand_login)

    @allure.title('Аннулирование небанковского платежа на форме "Реестры"')
    @allure.id(603059)
    @pytest.mark.regress
    def test_cancel_non_bank_payment_registry_form(
        self, base_url: str, api_request_auth_context: APIRequestContext, create_user_with_agreement_and_account
    ):
        with allure.step("Выполнение предусловий"):
            client_info = create_user_with_agreement_and_account
            today = get_current_datetime_string_for_api(is_full_format=False)
            payment_amount = generate_random_number(3)
            today_user_friendly_view = get_current_datetime_string(is_full_format=False)

            with allure.step(f"Добавление платежа для ЛС {client_info.account_id}"):
                payment_data = PaymentInfo(
                    item_type="CUSTOMER_ACCOUNT",
                    account_id=client_info.account_id,
                    payment_method_type="CASH",
                    currency_code="RUB",
                    amount=payment_amount,
                )
                self.payment_api.wait_check_create_payment(payment_data)
                self.payment_api.create_payment(payment_data)
                self.registry_requests_api.wait_last_payment_amount_in_registry(
                    today, payment_data.document_number, payment_amount
                )
                self.payment_api.wait_last_payment_successful(client_info.account_id)
                self.personal_account_api.wait_check_current_main_balance(client_info.account_id, payment_amount)

        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{client_info.user_id}/overview")
        delay(1, reason="Время для смены контекста и содержания меню")
        self.client_profile_page.locators.BURGER_MENU.select_by_value("Реестры")

        self.registry_elements.CHECK_NUM_SEARCH.fill(str(payment_data.document_number))
        self.registry_elements.CHECK_NUM_FIELDS.wait_to_have_count(1)

        self.registry_elements.PAYMENT_DATES_FIELDS.wait_to_be_visible()
        self.registry_elements.PAYMENT_DATES_FIELDS.to_contain_text(0, today_user_friendly_view)
        self.registry_elements.STATUS_FIELDS.to_contain_text(0, "Действует")
        self.registry_elements.CHECK_NUM_FIELDS.to_contain_text(0, str(payment_data.document_number))
        self.registry_elements.CHECK_SUM_FIELDS.to_contain_text(0, str(payment_data.amount))
        self.registry_elements.PAYMENT_SUM_FIELDS.to_contain_text(0, str(payment_data.amount))
        self.registry_elements.CASHIER_FIELDS.to_contain_text(0, "PNXL1/pointNx1")

        self.registry_elements.CANCEL_PAYMENT_BTN.check_attribute_by_value("disabled", "")
        self.registry_elements.PAYMENT_DATES_FIELDS[0].click()
        self.registry_elements.CANCEL_PAYMENT_BTN.element_not_contain_disabled_attribute()
        self.registry_elements.CANCEL_PAYMENT_BTN.click()

        self.cancel_payment_form.TITLE.wait_to_have_text("Аннулирование платежа")
        self.cancel_payment_form.SUBTITLE.to_contain_text(f"На сумму {payment_amount} от {today_user_friendly_view}")
        self.cancel_payment_form.CANCEL_OPERATION_BTN.check_attribute_by_value("disabled", "")
        self.cancel_payment_form.CANCEL_REASON_INPUT_FROM_REGISTRY.wait_to_have_text("")

        self.cancel_payment_form.CANCEL_REASON_INPUT_FROM_REGISTRY.fill("Ошибочный платеж")
        self.cancel_payment_form.CANCEL_OPERATION_BTN.element_not_contain_disabled_attribute()
        self.cancel_payment_form.CANCEL_OPERATION_BTN.click()
        self.cancel_payment_form.TITLE.not_to_be_visible()

        self.registry_elements.CHECK_NUM_FIELDS.wait_to_be_visible()
        self.registry_elements.PAYMENT_DATES_FIELDS.to_contain_text(0, today_user_friendly_view)
        self.registry_elements.PAYMENT_SUM_FIELDS.to_contain_text(0, f"{payment_amount}")
        self.registry_elements.CHECK_NUM_FIELDS.to_contain_text(0, str(payment_data.document_number))
        self.registry_elements.STATUS_FIELDS.to_contain_text(0, "Аннулирован")

    @allure.title('Аннулирование небанковского платежа на форме "Платежи"')
    @allure.id(600513)
    @pytest.mark.regress
    def test_cancel_non_bank_payment_payments_form(
        self, base_url: str, api_request_auth_context: APIRequestContext, create_user_with_agreement_and_account
    ):
        with allure.step("Выполнение предусловий"):
            client_info = create_user_with_agreement_and_account
            today = get_current_datetime_string_for_api(is_full_format=False)
            payment_amount = generate_random_number(3)
            today_user_friendly_view = get_current_datetime_string(is_full_format=False)

            with allure.step(f"Добавление платежа для ЛС {client_info.account_id}"):
                payment_data = PaymentInfo(
                    item_type="CUSTOMER_ACCOUNT",
                    account_id=client_info.account_id,
                    payment_method_type="CASH",
                    currency_code="RUB",
                    amount=payment_amount,
                )
                self.payment_api.wait_check_create_payment(payment_data)
                self.payment_api.create_payment(payment_data)
                self.registry_requests_api.wait_last_payment_amount_in_registry(
                    today, payment_data.document_number, payment_amount
                )
                self.payment_api.wait_last_payment_successful(client_info.account_id)
                self.personal_account_api.wait_check_current_main_balance(client_info.account_id, payment_amount)

        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{client_info.user_id}/overview")

        self.client_profile_page.locators.CURRENT_PERSONAL_ACCOUNT_LINK.click()
        delay(1, reason="Время для смены контекста и содержания меню")
        self.client_profile_page.locators.BURGER_MENU.select_by_value("Платежи")

        self.payment_page.locators.CHECK_NUM_FIELDS.wait_to_be_visible()
        self.payment_page.locators.CHECK_NUM_FIELDS.to_contain_text(0, str(payment_data.document_number))
        self.payment_page.locators.PAYMENT_DATES_FIELDS.to_contain_text(0, today_user_friendly_view)
        self.payment_page.locators.REGISTRY_DATES_FIELDS.to_contain_text(0, today_user_friendly_view)
        self.payment_page.locators.SUM_FIELDS.to_contain_text(0, f"{payment_amount}")
        self.payment_page.locators.STATUS_FIELDS.to_contain_text(0, "Действует")

        self.payment_page.locators.CANCEL_PAYMENT_BTN.check_attribute_by_value("disabled", "")
        self.payment_page.locators.PAYMENT_DATES_FIELDS[0].click()
        delay(0.5, reason="Время на активацию кнопки")
        self.payment_page.locators.CANCEL_PAYMENT_BTN.element_not_contain_disabled_attribute()
        self.payment_page.locators.CANCEL_PAYMENT_BTN.click()

        self.cancel_payment_form.TITLE.wait_to_have_text("Аннулирование платежа")
        self.cancel_payment_form.SUBTITLE.to_contain_text(f"На сумму {payment_amount}.00 от {today_user_friendly_view}")
        self.cancel_payment_form.CANCEL_OPERATION_BTN.check_attribute_by_value("disabled", "")
        self.cancel_payment_form.CANCEL_REASON_INPUT.fill("Ошибочный платеж")
        self.cancel_payment_form.CANCEL_OPERATION_BTN.element_not_contain_disabled_attribute()
        self.cancel_payment_form.CANCEL_OPERATION_BTN.click()
        self.cancel_payment_form.TITLE.not_to_be_visible()

        self.payment_page.locators.CHECK_NUM_FIELDS.wait_to_be_visible()
        self.payment_page.locators.SUM_FIELDS.to_contain_text(0, f"{payment_amount}.00")
        self.payment_page.locators.STATUS_FIELDS.to_contain_text(0, "Аннулирован")
        self.payment_page.locators.USER_BALANCE.wait_to_have_text(f"{payment_amount}.00")

        self.payment_page.locators.CHECK_NUM_FIELDS[0].click()

        self.payment_details_elements.FORM_TITLE.wait_to_have_text("Платёж")
        self.payment_details_elements.FORM_STATUS.wait_to_have_text("Аннулирован")
        self.payment_details_elements.SUBTITLE.wait_to_have_text(
            re.compile(f"На сумму {payment_amount}.00 от {today_user_friendly_view}")
        )
        self.payment_details_elements.PAYMENT_DETAILS[0].to_contain_text(today_user_friendly_view)
        self.payment_details_elements.PAYMENT_DETAILS[1].to_contain_text(today_user_friendly_view)
        self.payment_details_elements.PAYMENT_DETAILS[2].to_contain_text(str(payment_data.document_number))
        self.payment_details_elements.PAYMENT_DETAILS[3].to_contain_text(f"{payment_amount}.00")
        self.payment_details_elements.PAYMENT_DETAILS[4].wait_to_have_text(re.compile(rf"{payment_amount}.00\sRUB"))
        self.payment_details_elements.PAYMENT_DETAILS[6].to_contain_text("PM:pm_gateway")
        self.payment_details_elements.PAYMENT_DETAILS[8].to_contain_text("PNXL1")
        self.payment_details_elements.PAYMENT_DETAILS[11].to_contain_text("Ошибочный платеж")

    @allure.title("Аннулирование небанковского платежа при недостатке средств")
    @allure.id(605159)
    @pytest.mark.regress
    def test_cancel_non_bank_payment_decreased_sum(
        self, base_url: str, api_request_auth_context: APIRequestContext, create_user: int
    ):
        with allure.step("Выполнение предусловий"):
            today = get_current_datetime_string_for_api(is_full_format=False)
            payment_amount = 650
            today_user_friendly_view = get_current_datetime_string(is_full_format=False)
            new_client_id = create_user

            self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{new_client_id}/overview")
            self.inquiries_page.sale_internet()

            account_id = self.personal_account_api.get_personal_accounts(
                entity_code="customer", entity_id=new_client_id
            ).json()["items"][0]["accountId"]
            self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{new_client_id}/overview")

            with allure.step(f"Добавление платежа для ЛС {account_id}"):
                payment_data = PaymentInfo(
                    item_type="CUSTOMER_ACCOUNT",
                    account_id=account_id,
                    payment_method_type="CASH",
                    currency_code="RUB",
                    amount=payment_amount,
                )
                self.payment_api.wait_check_create_payment(payment_data)
                self.payment_api.create_payment(payment_data)
                self.registry_requests_api.wait_last_payment_amount_in_registry(
                    today, payment_data.document_number, payment_amount
                )
                self.payment_api.wait_last_payment_successful(account_id)
                self.personal_account_api.wait_check_current_main_balance(account_id, payment_amount)

            self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{account_id}/overview")

        self.personal_account_api.wait_check_current_main_balance(account_id, 0)

        self.client_profile_page.locators.BURGER_MENU.select_by_value("Реестры")

        self.registry_elements.CHECK_NUM_SEARCH.fill(str(payment_data.document_number))
        self.registry_elements.CHECK_NUM_FIELDS.wait_to_have_count(1)

        self.registry_elements.PAYMENT_DATES_FIELDS.wait_to_be_visible()
        self.registry_elements.PAYMENT_DATES_FIELDS.to_contain_text(0, today_user_friendly_view)
        self.registry_elements.STATUS_FIELDS.to_contain_text(0, "Действует")
        self.registry_elements.CHECK_NUM_FIELDS.to_contain_text(0, str(payment_data.document_number))
        self.registry_elements.CHECK_SUM_FIELDS.to_contain_text(0, str(payment_data.amount))
        self.registry_elements.PAYMENT_SUM_FIELDS.to_contain_text(0, str(payment_data.amount))
        self.registry_elements.CASHIER_FIELDS.to_contain_text(0, "PNXL1/pointNx1")

        self.registry_elements.CANCEL_PAYMENT_BTN.check_attribute_by_value("disabled", "")
        self.registry_elements.PAYMENT_DATES_FIELDS[0].click()
        self.registry_elements.CANCEL_PAYMENT_BTN.element_not_contain_disabled_attribute()
        self.registry_elements.CANCEL_PAYMENT_BTN.click()

        self.cancel_payment_form.TITLE.wait_to_have_text("Аннулирование платежа")
        self.cancel_payment_form.SUBTITLE.to_contain_text(f"На сумму {payment_amount} от {today_user_friendly_view}")
        self.cancel_payment_form.CANCEL_REASON_INPUT_FROM_REGISTRY.wait_to_have_text("")

        self.cancel_payment_form.CANCEL_REASON_INPUT_FROM_REGISTRY.fill("Ошибочный платеж")
        self.cancel_payment_form.CANCEL_INFO_MESSAGE.wait_to_have_text(
            f"Недостаток средств 0 на счету {account_id} для отмены платежа с суммой {payment_amount}"
        )
        self.cancel_payment_form.CANCEL_OPERATION_BTN.not_to_be_enabled()
