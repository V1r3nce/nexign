import re

import allure
import pytest
from playwright.sync_api import APIRequestContext, Page

from api.exceptions import UpdateStatusException
from api.requests.client_requests import ClientRequests
from api.requests.payments_requests import PaymentsRequests, PaymentsUniblpRequests, PaymentUniblpInfo
from api.requests.personal_account_requests import PersonalAccountData, PersonalAccountRequests
from api.requests.registry_requests import RegistryRequests
from common.helpers.checker import wait_that
from common.helpers.data_generator import (
    generate_random_number,
    get_current_datetime_string,
    get_current_datetime_string_for_api,
)
from common.helpers.time_helpers import delay
from models.user import IndividualClient
from pages.base_page import BasePage
from pages.client_profile_page import ClientProfilePage
from pages.locators.payments_elements import PaymentDetailsElements
from pages.locators.registry_elements import RegistryDetailsElements, RegistryElements
from pages.payments_page import PaymentsPage


@allure.epic("E2E_81 Управление банковскими платежами")
@allure.suite("E2E_81 Управление банковскими платежами")
class TestManageBankPayments:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_ui_stand_login: Page, api_request_auth_context: APIRequestContext) -> None:
        self.base_page = BasePage(nexign_ui_stand_login)
        self.client_profile_page = ClientProfilePage(nexign_ui_stand_login)
        self.registry_elements = RegistryElements(nexign_ui_stand_login)
        self.registry_details_elements = RegistryDetailsElements(nexign_ui_stand_login)
        self.payment_details_elements = PaymentDetailsElements(nexign_ui_stand_login)
        self.payment_page = PaymentsPage(nexign_ui_stand_login)
        self.client_profile_page = ClientProfilePage(nexign_ui_stand_login)
        self.client_request_api = ClientRequests(api_request_auth_context)
        self.personal_account_api = PersonalAccountRequests(api_request_auth_context)
        self.payment_api = PaymentsRequests(api_request_auth_context)
        self.payment_api_uniblp = PaymentsUniblpRequests(api_request_auth_context)
        self.registry_requests_api = RegistryRequests(api_request_auth_context)

    @allure.title("Отображение платежа в реестре платежей")
    @allure.id(580953)
    @allure.description("Отображение платежа в реестре платежей")
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=462935916",
        name="LLD Прием и аннулирование платежа",
    )
    @allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=471415127", name="ФС Прием платежей")
    @allure.tag("can_auth", "success")
    @pytest.mark.regress
    def test_payment_preview_in_registry_list(
        self,
        base_url: str,
        api_request_auth_context: APIRequestContext,
        create_user_with_agreement_and_account: IndividualClient,
    ) -> None:
        client_info = create_user_with_agreement_and_account
        payment_amount = generate_random_number(3)
        today = get_current_datetime_string_for_api(is_full_format=False)
        today_user_friendly_view = get_current_datetime_string(is_full_format=False)
        doc_number = generate_random_number(4)
        payment_data = PaymentUniblpInfo(
            item_type="CUSTOMER_ACCOUNT",
            amount=payment_amount,
            currency_code="RUB",
            account_id=client_info.agreements[0].accounts[0].id,
            document_number=doc_number,
            payment_method_type="BANK_ACCOUNT_TRANSFER",
        )
        self.payment_api_uniblp.wait_check_create_payment(payment_data)
        self.payment_api_uniblp.create_payment(payment_data)

        self.registry_requests_api.wait_last_payment_amount_in_registry(today, doc_number, payment_amount)
        self.registry_requests_api.wait_payment_for_doc_successful(today, doc_number)

        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{client_info.user_id}/overview")
        delay(1, reason="Время для смены контекста и содержания меню")
        self.client_profile_page.locators.BURGER_MENU.select_by_value("Платежные системы > Реестр платежей")

        self.registry_elements.PAYMENT_SYSTEM_TABS[1].click()
        self.registry_elements.PAYMENT_SYSTEM_TABS[1].check_attribute_by_value("aria-selected", "true")
        self.registry_elements.CHECK_NUM_SEARCH.fill(str(doc_number))
        self.registry_elements.PAYMENT_DATES_FIELDS.wait_to_have_count(1)
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

        self.registry_details_elements.FORM_TABS[1].check_attribute_by_value("aria-selected", "true")
        self.registry_details_elements.GOAL_TABLE_FIRST_COLUMN[0].wait_to_have_text(
            f"Лицевой счет {client_info.agreements[0].accounts[0].id}"
        )
        self.registry_details_elements.GOAL_TABLE_FIRST_COLUMN[1].wait_to_have_text("Исходная сумма:")
        self.registry_details_elements.GOAL_TABLE_FIRST_COLUMN[2].wait_to_have_text(f"{payment_amount}.00 RUB.")

    @allure.title("Отображение платежа в платежах клиента")
    @allure.id(580954)
    @allure.description("Отображение платежа в платежах клиента")
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=462935916",
        name="LLD Прием и аннулирование платежа",
    )
    @allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=471415127", name="ФС Прием платежей")
    @allure.tag("can_auth", "success")
    @pytest.mark.regress
    def test_payment_preview_in_payment_list(
        self,
        base_url: str,
        api_request_auth_context: APIRequestContext,
        create_user_with_agreement_and_account: IndividualClient,
    ) -> None:
        client_info = create_user_with_agreement_and_account
        payment_amount = generate_random_number(3)
        today_user_friendly_view = get_current_datetime_string(is_full_format=False)
        doc_number = generate_random_number(4)
        client_name = self.client_request_api.get_client_data(client_info.user_id).json()["party"]["nameInfo"]["name"]
        payment_data = PaymentUniblpInfo(
            item_type="CUSTOMER_ACCOUNT",
            amount=payment_amount,
            currency_code="RUB",
            account_id=client_info.agreements[0].accounts[0].id,
            document_number=doc_number,
            payment_method_type="BANK_ACCOUNT_TRANSFER",
        )
        self.payment_api_uniblp.wait_check_create_payment(payment_data)
        self.payment_api_uniblp.create_payment(payment_data)

        self.payment_api.wait_last_payment_successful(client_info.agreements[0].accounts[0].id)
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{client_info.user_id}/overview")
        self.client_profile_page.locators.CURRENT_PERSONAL_ACCOUNT_LINK.click()
        delay(1, reason="Время для смены контекста и содержания меню")
        self.client_profile_page.locators.BURGER_MENU.select_by_value("Финансы > Платежи")

        self.payment_page.locators.ACCOUNT_NUM.wait_to_have_text(client_info.agreements[0].accounts[0].number)
        self.payment_page.locators.USER_NAME.wait_to_have_text(client_name)
        (
            self.payment_page.locators.USER_BALANCE.wait_to_have_text(
                re.compile(r"^(\d{1,3}\.\d{2})|(\d{1,3}\s\d{1,3}\.\d{2})$")
            )
        )

        self.payment_page.locators.CHECK_NUM_FIELDS.wait_to_be_visible()
        self.payment_page.locators.CHECK_NUM_FIELDS.to_contain_text(0, str(doc_number))
        self.payment_page.locators.PAYMENT_DATES_FIELDS.to_contain_text(0, today_user_friendly_view)
        self.payment_page.locators.REGISTRY_DATES_FIELDS.to_contain_text(0, today_user_friendly_view)
        self.payment_page.locators.SUM_FIELDS.to_contain_text(0, f"{payment_data.amount}.00")
        self.payment_page.locators.STATUS_FIELDS.to_contain_text(0, "Действует")

        self.payment_page.locators.CHECK_NUM_FIELDS[0].click()

        self.payment_details_elements.FORM_TITLE.wait_to_have_text("Платёж")
        self.payment_details_elements.FORM_STATUS.wait_to_have_text("Действует")
        (
            self.payment_details_elements.SUBTITLE.wait_to_have_text(
                re.compile(f"На сумму {payment_data.amount}.00 от {today_user_friendly_view}")
            )
        )
        self.payment_details_elements.PAYMENT_DETAILS[0].to_contain_text(today_user_friendly_view)
        self.payment_details_elements.PAYMENT_DETAILS[1].to_contain_text(today_user_friendly_view)
        self.payment_details_elements.PAYMENT_DETAILS[2].to_contain_text(str(doc_number))
        self.payment_details_elements.PAYMENT_DETAILS[3].to_contain_text(f"{payment_data.amount}.00")
        self.payment_details_elements.PAYMENT_DETAILS[4].wait_to_have_text(re.compile(rf"{payment_data.amount}.00\sRUB"))
        self.payment_details_elements.PAYMENT_DETAILS[6].to_contain_text("PM:pm_gateway")
        self.payment_details_elements.PAYMENT_DETAILS[8].to_contain_text("uniblp")
        self.payment_details_elements.FORM_TABS[1].click()

        self.payment_details_elements.FORM_TABS[1].check_attribute_by_value("aria-selected", "true")
        self.payment_details_elements.PAYMENT_TYPE_BTN[0].wait_to_have_text("Погашения: 0.00")
        self.payment_details_elements.PAYMENT_TYPE_BTN[1].wait_to_have_text("Корректировки: 0.00")
        self.payment_details_elements.PAYMENT_TYPE_BTN[0].element_have_css_color("color", "deep_blue")
        self.payment_details_elements.PAYMENT_DATE_FIELDS.wait_not_to_be_visible()
        self.payment_details_elements.PAYMENT_TYPE_BTN[1].click()
        self.payment_details_elements.PAYMENT_TYPE_BTN[1].to_have_class(re.compile("checked"))
        self.payment_details_elements.PAYMENT_DATE_FIELDS.wait_not_to_be_visible()

    @allure.title("Прием банковского платежа в валюте")
    @allure.id(580982)
    @allure.description("Прием банковского платежа в валюте")
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=462935916",
        name="LLD Прием и аннулирование платежа",
    )
    @allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=471415127", name="ФС Прием платежей")
    @allure.tag("can_auth", "success")
    @pytest.mark.regress
    def test_payment_preview_in_usd_currency(
        self,
        base_url: str,
        api_request_auth_context: APIRequestContext,
        create_user_with_agreement_and_usd_account: IndividualClient,
    ) -> None:
        client_info = create_user_with_agreement_and_usd_account
        payment_amount = generate_random_number(2)
        today_user_friendly_view = get_current_datetime_string(is_full_format=False)
        doc_number = generate_random_number(4)
        payment_data = PaymentUniblpInfo(
            item_type="CUSTOMER_ACCOUNT",
            amount=payment_amount,
            currency_code="USD",
            account_id=client_info.agreements[0].accounts[0].id,
            document_number=doc_number,
            payment_method_type="BANK_ACCOUNT_TRANSFER",
        )
        self.payment_api_uniblp.wait_check_create_payment(payment_data)
        self.payment_api_uniblp.create_payment(payment_data)

        self.payment_api.wait_last_payment_amount(client_info.agreements[0].accounts[0].id, payment_amount)
        self.payment_api.wait_last_payment_successful(client_info.agreements[0].accounts[0].id)
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{client_info.user_id}/overview")
        self.client_profile_page.locators.CURRENT_PERSONAL_ACCOUNT_LINK.click()
        delay(1, reason="Время для смены контекста и содержания меню")
        self.client_profile_page.locators.BURGER_MENU.select_by_value("Финансы > Платежи")

        self.payment_page.locators.ACCOUNT_NUM.wait_to_have_text(client_info.agreements[0].accounts[0].number)
        (
            self.payment_page.locators.USER_BALANCE.wait_to_have_text(
                re.compile(r"^(\d{1,3}\.\d{2})|(\d{1,3}\s\d{1,3}\.\d{2})$")
            )
        )
        self.payment_page.locators.USER_CURRENCY.to_contain_text("USD")

        self.payment_page.locators.CHECK_NUM_FIELDS.wait_to_be_visible()
        self.payment_page.locators.CHECK_NUM_FIELDS.to_contain_text(0, str(doc_number))
        self.payment_page.locators.PAYMENT_DATES_FIELDS.to_contain_text(0, today_user_friendly_view)
        self.payment_page.locators.REGISTRY_DATES_FIELDS.to_contain_text(0, today_user_friendly_view)
        self.payment_page.locators.SUM_FIELDS.to_contain_text(0, f"{payment_data.amount}.00")
        self.payment_page.locators.STATUS_FIELDS.to_contain_text(0, "Действует")

        self.payment_page.locators.CHECK_NUM_FIELDS[0].click()

        self.payment_details_elements.FORM_TITLE.wait_to_have_text("Платёж")
        self.payment_details_elements.FORM_STATUS.wait_to_have_text("Действует")
        (
            self.payment_details_elements.SUBTITLE.wait_to_have_text(
                re.compile(f"На сумму {payment_data.amount}.00 от {today_user_friendly_view}")
            )
        )
        self.payment_details_elements.PAYMENT_DETAILS[0].to_contain_text(today_user_friendly_view)
        self.payment_details_elements.PAYMENT_DETAILS[1].to_contain_text(today_user_friendly_view)
        self.payment_details_elements.PAYMENT_DETAILS[2].to_contain_text(str(doc_number))
        self.payment_details_elements.PAYMENT_DETAILS[3].to_contain_text(f"{payment_data.amount}.00")
        self.payment_details_elements.PAYMENT_DETAILS[4].wait_to_have_text(re.compile(rf"{payment_data.amount}.00\sUSD"))
        self.payment_details_elements.PAYMENT_DETAILS[6].to_contain_text("PM:pm_gateway")
        self.payment_details_elements.PAYMENT_DETAILS[8].to_contain_text("uniblp")

        self.client_profile_page.press_keyboard_button("Escape")
        self.client_profile_page.locators.BURGER_MENU.select_by_value("Платежные системы > Реестр платежей")

        self.registry_elements.PAYMENT_SYSTEM_TABS[1].click()
        self.registry_elements.PAYMENT_SYSTEM_TABS[1].check_attribute_by_value("aria-selected", "true")
        self.registry_elements.CHECK_NUM_SEARCH.fill(str(doc_number))
        self.registry_elements.PAYMENT_DATES_FIELDS.wait_to_be_visible()
        self.registry_elements.PAYMENT_DATES_FIELDS.to_contain_text(0, today_user_friendly_view)
        self.registry_elements.STATUS_FIELDS.to_contain_text(0, "Действует")
        self.registry_elements.CHECK_NUM_FIELDS.to_contain_text(0, str(doc_number))
        self.registry_elements.CHECK_SUM_FIELDS[0].wait_to_have_text(re.compile(rf"{payment_data.amount}.00\sUSD"))
        self.registry_elements.PAYMENT_SUM_FIELDS[0].wait_to_have_text(re.compile(rf"{payment_data.amount}.00\sUSD"))
        self.registry_elements.CASHIER_FIELDS.to_contain_text(0, "uniblp/uniblp")
        self.registry_elements.CHECK_NUM_FIELDS[0].click()

        form_title = f"Платёж от {today_user_friendly_view}"
        self.registry_details_elements.FORM_TITLE.wait_to_have_text(re.compile(form_title))
        self.registry_details_elements.PAYMENT_DETAILS.wait_to_have_count(5)
        self.registry_details_elements.PAYMENT_DETAILS[0].to_contain_text(today_user_friendly_view)
        (
            self.registry_details_elements.PAYMENT_DETAILS[1].wait_to_have_text(
                re.compile(rf"{payment_data.amount}.00\sUSD")
            )
        )
        self.registry_details_elements.PAYMENT_DETAILS[2].to_contain_text(str(doc_number))
        self.registry_details_elements.PAYMENT_DETAILS[3].to_contain_text("Банковский перевод")
        self.registry_details_elements.PAYMENT_DETAILS[4].to_contain_text("uniblp/uniblp")

    @allure.title("Перенос баланса")
    @allure.id(580986)
    @allure.description("Перенос баланса")
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=462935916",
        name="LLD Прием и аннулирование платежа",
    )
    @allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=471415127", name="ФС Прием платежей")
    @allure.tag("can_auth", "success")
    @pytest.mark.regress
    def test_payments_relocate_balance(
        self,
        base_url: str,
        api_request_auth_context: APIRequestContext,
        create_user_with_agreement_and_account: IndividualClient,
    ) -> None:
        client_info = create_user_with_agreement_and_account
        payment_amount = 250
        relocate_amount = 100
        doc_number = generate_random_number(4)
        today_user_friendly_view = get_current_datetime_string(is_full_format=False)
        account_data = PersonalAccountData(
            agreement_id=client_info.agreements[0].id,
            is_cash_payment_enabled=False,
        )
        self.personal_account_api.create_personal_account(account_data)
        wait_that(
            lambda: len(self.personal_account_api.get_personal_accounts("customer", client_info.user_id).json()["items"])
            == 2,
            exception=UpdateStatusException,
            timeout=10,
            sleep_seconds=0.5,
            message="2ой аккаунт не создался в указанное время",
        )
        accounts = self.personal_account_api.get_personal_accounts("customer", client_info.user_id).json()["items"]
        first_account_id, _ = accounts[0]["accountId"], accounts[1]["accountId"]
        first_account_num, second_account_num = accounts[0]["accountNumber"], accounts[1]["accountNumber"]

        payment_data = PaymentUniblpInfo(
            item_type="CUSTOMER_ACCOUNT",
            amount=payment_amount,
            currency_code="RUB",
            account_id=first_account_id,
            document_number=doc_number,
            payment_method_type="BANK_ACCOUNT_TRANSFER",
        )
        self.payment_api_uniblp.wait_check_create_payment(payment_data)
        self.payment_api_uniblp.create_payment(payment_data)

        self.payment_api.wait_last_payment_amount(client_info.agreements[0].accounts[0].id, payment_amount)
        self.payment_api.wait_last_payment_successful(client_info.agreements[0].accounts[0].id)
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{client_info.user_id}/overview")
        self.client_profile_page.locators.WIDGET_PERSONAL_ACCOUNT_IDS[0].click()
        self.client_profile_page.locators.RELATED_PERSONS_TAB.wait_to_be_visible()
        delay(1, reason="Время для смены контекста и содержания меню")
        self.client_profile_page.locators.BURGER_MENU.select_by_value("Финансы > Платежи")

        self.payment_page.locators.PAYMENT_DATES_FIELDS.wait_to_be_visible()
        self.payment_page.locators.BALANCE_TRANSFER_BTN.click()

        client_name = self.client_request_api.get_client_data(client_info.user_id).json()["party"]["nameInfo"]["name"]
        self.payment_page.check_from_account_fields(
            first_account_num, client_name, "Основной счёт", "", "", rf"{payment_amount}.00\sRUB", "", "—"
        )

        self.payment_page.locators.USER_NAME.wait_to_be_visible()
        self.payment_page.locators.PERSONAL_ACCOUNT_SELECTOR.click()
        self.payment_page.locators.PERSONAL_ACCOUNT_SEARCH_BTN.check_attribute_by_value("disabled", "")
        self.payment_page.locators.PERSONAL_ACCOUNT_CHOOSE_BTN.check_attribute_by_value("disabled", "")
        self.payment_page.locators.PERSONAL_ACCOUNT_TO_SEARCH.fill(second_account_num)
        self.payment_page.locators.PERSONAL_ACCOUNT_SEARCH_BTN.element_not_contain_disabled_attribute()
        self.payment_page.locators.PERSONAL_ACCOUNT_SEARCH_BTN.click()
        self.payment_page.locators.PERSONAL_ACCOUNT_DATA[0].wait_to_be_visible()
        self.payment_page.locators.PERSONAL_ACCOUNT_DATA[1].to_contain_text(second_account_num)
        self.payment_page.locators.PERSONAL_ACCOUNT_CHOOSE_BTN.element_not_contain_disabled_attribute()
        self.payment_page.locators.PERSONAL_ACCOUNT_CHOOSE_BTN.click()
        self.payment_page.locators.PERSONAL_ACCOUNT_CHOOSE_BTN.not_to_be_visible()
        self.payment_page.check_to_account_fields(
            second_account_num, client_name, "Основной счёт", "", "", r"0.00\sRUB", r"0.00\sRUB", r"0.00\sRUB"
        )

        self.payment_page.locators.DONOR_ADJUSTMENT_REASON.select_by_value("Перенос средств по заявлению клиента")
        self.payment_page.locators.RECIPIENT_ADJUSTMENT_REASON.select_by_value("Перенос средств по заявлению клиента.")
        self.payment_page.locators.CHOSEN_DONOR_ADJUSTMENT_REASON.wait_to_have_text(
            "Перенос средств по заявлению клиента"
        )
        self.payment_page.locators.CHOSEN_RECIPIENT_ADJUSTMENT_REASON.wait_to_have_text(
            "Перенос средств по заявлению клиента."
        )
        self.payment_page.locators.TRANSFER_ACCEPT.check_attribute_by_value("disabled", "")
        self.payment_page.locators.BALANCE_TO_TRANSFER.fill(str(relocate_amount))
        self.payment_page.locators.FROM_ACCOUNT_COMMENT.click()
        self.payment_page.locators.TRANSFER_ACCEPT.element_not_contain_disabled_attribute()
        self.payment_page.check_from_account_fields(
            first_account_num,
            client_name,
            "Основной счёт",
            "Перенос средств по заявлению клиента",
            "",
            rf"{payment_amount}.00\sRUB",
            f"{relocate_amount}",
            rf"{payment_amount - relocate_amount}.00\sRUB",
        )
        self.payment_page.check_to_account_fields(
            second_account_num,
            client_name,
            "Основной счёт",
            "Перенос средств по заявлению клиента.",
            "",
            r"0.00\sRUB",
            rf"{relocate_amount}.00\sRUB",
            rf"{relocate_amount}.00\sRUB",
        )
        self.payment_page.locators.TRANSFER_ACCEPT.click()

        self.payment_page.locators.INFO_MESSAGE.wait_to_have_text("Перенос баланса выполнен")
        self.payment_page.locators.INFO_MESSAGE.not_to_be_visible()
        delay(2, reason="Сумма баланса обновляется не сразу")
        self.payment_page.locators.USER_BALANCE.wait_to_have_text(f"{payment_amount - relocate_amount}.00")
        delay(2, reason="Нужно время не успевает прогрузиться корректировка")
        self.payment_page.locators.CHECK_NUM_FIELDS[0].click()

        self.payment_details_elements.FORM_TABS[0].check_attribute_by_value("aria-selected", "true")
        self.payment_details_elements.FORM_TABS[1].click()
        self.payment_details_elements.PAYMENT_TYPE_BTN.to_contain_text(0, f"Погашения: {relocate_amount}.00")
        self.payment_details_elements.PAYMENT_TYPE_BTN[1].wait_to_have_text("Корректировки: 0.00")
        self.payment_details_elements.PAYMENT_DATE_FIELDS[0].to_contain_text(today_user_friendly_view)
        self.payment_details_elements.PAYMENT_SUM_FIELDS[0].to_contain_text(f"{relocate_amount}.00")
        self.payment_details_elements.PAYMENT_OBJECTS_FIELDS[0].to_contain_text(
            f"Отрицательная корректировка лицевого счета от {today_user_friendly_view} на сумму {relocate_amount}"
        )
        self.payment_page.press_keyboard_button("Escape")
        self.client_profile_page.locators.CURRENT_CLIENT_LINK.click()
        self.client_profile_page.locators.WIDGET_PERSONAL_ACCOUNT_SUM.wait_to_be_visible()
        (
            self.client_profile_page.locators.WIDGET_PERSONAL_ACCOUNT_SUM[0].wait_to_have_text(
                f"{payment_amount - relocate_amount}.00 RUB"
            )
        )
        self.client_profile_page.locators.WIDGET_PERSONAL_ACCOUNT_SUM[1].wait_to_have_text(f"{relocate_amount}.00 RUB")
