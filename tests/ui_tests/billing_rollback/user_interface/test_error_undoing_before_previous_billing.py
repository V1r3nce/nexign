import re

import allure
import pytest
from playwright.sync_api import APIRequestContext, Page

from api.requests.billing_requests import BillingRequests
from api.requests.payments_requests import PaymentInfo, PaymentsRequests
from api.requests.personal_account_requests import PersonalAccountRequests
from pages.billing_accounts_page import BillingAccountsPage
from pages.client_profile_page import ClientProfilePage
from pages.locators.dynamic_form_elements import CreateInquiryNotification
from pages.locators.inquiries_page import InquiriesPage
from tests.conftest import CreatedImsis


@pytest.mark.usefixtures("nexign_ui_stand_login")
class TestErrorUndoingBeforePreviousBilling:
    @pytest.fixture(autouse=True)
    def setup(self, page: Page, nexign_ui_stand_login: Page, api_request_auth_context: APIRequestContext):
        self.client_profile = ClientProfilePage(nexign_ui_stand_login)
        self.inquiries_page = InquiriesPage(nexign_ui_stand_login)
        self.personal_account_api = PersonalAccountRequests(api_request_auth_context)
        self.payment_api = PaymentsRequests(api_request_auth_context)
        self.billing_api = BillingRequests(api_request_auth_context)
        self.notification = CreateInquiryNotification(nexign_ui_stand_login)

        self.billing_accounts_page = BillingAccountsPage(page)

    @allure.suite("E2E_85 Откат биллинга")
    @allure.title("Ошибка при откате биллинга до завершения предыдущего процесса биллинга")
    @allure.id(577553)
    @allure.description(
        "Появление диалогового окна с сообщением об ошибке при попытке отката биллинга, до завершения предыдущего процесса биллинга."
    )
    @allure.link(url="jira.nexign.com/browse/TUDS-2569", name="TUDS-2569")
    @allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=555189386", name="Откат биллинга по клиенту")
    @pytest.mark.regress
    def test_error_undoing_before_previous_billing(
        self, page: Page, base_url: str, create_user: int, add_two_imsi_free_shipped: CreatedImsis
    ):
        with allure.step("Проведение продажи и начисление платежа клиенту"):
            user_id = create_user
            self.client_profile.open(f"{base_url}customer-hierarchy-management/customers/{user_id}/overview")
            product = self.inquiries_page.sale_phone_number()
            account_id = self.personal_account_api.get_personal_accounts("customer", user_id).json()["items"][0][
                "accountId"
            ]
            subscription_id = self.personal_account_api.get_client_subscriptions(user_id).json()["items"][0][
                "subscriptionId"
            ]
            replace_number_price = 100.00
            payment_data = PaymentInfo(
                item_type="CUSTOMER_ACCOUNT",
                amount=product.one_time_payment + product.subscription_fee + replace_number_price,
                currency_code="RUB",
                account_id=account_id,
                payment_method_type="CASH",
            )
            self.payment_api.create_payment(payment_data)

        with allure.step(f"Проведение биллинга для ЛС: {account_id}"):
            self.personal_account_api.wait_accruals(subscription_id)
            billing_profile_id = self.billing_api.get_billing_profile_id(account_id)
            self.billing_api.run_unscheduled_billing(billing_profile_id)
            self.billing_api.wait_billing(billing_profile_id)
            self.billing_api.wait_finish_billing(billing_profile_id, 3)

        with allure.step("Открыть биллинговый счёт, который был сформирован раньше"):
            self.client_profile.open(f"{base_url}customer-hierarchy-management/customers/{user_id}/products")
            self.client_profile.locators.SUBSCRIBER.wait_to_be_visible()
            account_num = self.client_profile.locators.PRODUCTS_PERSONAL_ACCOUNT_NUM.text

            self.client_profile.open(f"{base_url}customer-hierarchy-management/accounts/{account_id}/account")
            self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Биллинговые счета")

            self.billing_accounts_page.locators.BILLING_LAUNCH_BTN.wait_to_be_visible()
            self.billing_accounts_page.locators.REFRESH_BTN.click()
            self.billing_accounts_page.locators.ACCOUNT_NUMS_LIST.wait_elements_visible(0)
            self.billing_accounts_page.locators.ACCOUNT_NUMS_LIST[0].click()

            self.billing_accounts_page.check_billing_properties()

        with allure.step('Нажать на кнопку "Запуск биллинга" и нажать на кнопку "Запустить"'):
            self.billing_accounts_page.locators.BILLING_LAUNCH_BTN.wait_to_be_visible()
            self.billing_accounts_page.locators.BILLING_LAUNCH_BTN.click()

            self.billing_accounts_page.locators.SECOND_BTN.wait_to_be_visible()
            self.billing_accounts_page.locators.SECOND_BTN.click()
            self.billing_accounts_page.locators.MODAL.wait_not_to_be_visible()

            self.notification.CROSS_BTN.wait_to_be_visible()
            billing_popup_text = re.compile(
                rf"Запущен внеочередной биллинг по лицевому счету: {account_num} "
                r"Задание: \d{4}-\d{12}-\d{2}"
            )
            self.notification.INQUIRY_NOTIFICATION.wait_to_have_text(billing_popup_text)

        with allure.step('Нажать кнопку "Откатить биллинг" и нажать кнопку "Выполнить"'):
            self.billing_accounts_page.locators.BILLING_BTNS[0].click()

            self.billing_accounts_page.locators.MODAL[1].wait_to_be_visible()
            rollback_modal_text = re.compile(
                r"Будет выполнен откат внеочередного биллинга от \d{2}\.\d{2}\.\d{4} \d{2}\:\d{2}\:\d{2}."
                r"Количество счетов: 1"
            )
            self.billing_accounts_page.locators.MODAL_BODY_TEXT[1].wait_to_have_text(rollback_modal_text)
            self.billing_accounts_page.locators.EXECUTE_BTN[1].click()

            self.billing_accounts_page.locators.MODAL.wait_elements_visible(2)

        with allure.step('Закрыть диалоговое окно с сообщением об ошибке и нажать кнопку "Список заданий биллинга"'):
            self.billing_accounts_page.locators.EXECUTE_BTN[2].click()
            self.billing_accounts_page.locators.MODAL[2].not_to_be_visible()

            self.billing_accounts_page.locators.REFRESH_BTN.click()
            self.billing_accounts_page.locators.BILLING_TASKS_BTN.wait_to_be_visible()
            self.billing_accounts_page.locators.BILLING_TASKS_BTN.click()
            self.billing_accounts_page.locators.TASK_TYPE_LIST.wait_elements_visible(1)
            self.billing_accounts_page.locators.TASK_TYPE_LIST[0].to_contain_text("Биллинг")
            self.billing_accounts_page.locators.TASK_TYPE_LIST[1].to_contain_text("Биллинг")
            self.billing_accounts_page.locators.TASK_STATUS_LIST[0].to_contain_text("Завершено")
            self.billing_accounts_page.locators.TASK_STATUS_LIST[1].to_contain_text("Выполняется")
            self.billing_api.wait_finish_billing(billing_profile_id, 3)

        with allure.step('Закрыть список заданий биллинга и нажать кнопку "Обновить"'):
            self.billing_accounts_page.locators.TASKS_CLOSE_BTN.click()

            self.billing_accounts_page.locators.REFRESH_BTN.wait_to_be_visible()
            self.billing_accounts_page.locators.REFRESH_BTN.click()

            self.billing_accounts_page.locators.ACCOUNT_NUMS_LIST.wait_elements_visible(1)
