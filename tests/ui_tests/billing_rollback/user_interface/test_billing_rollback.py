import re

import allure
import pytest
from playwright.sync_api import APIRequestContext, Page

from api.requests.billing_requests import BillingRequests
from api.requests.client_requests.client_inquiries_requests import ClientInquiriesRequests
from api.requests.payments_requests import PaymentsRequests
from api.requests.personal_account_requests import PersonalAccountRequests
from models.user import IndividualClient
from pages.billing_accounts_page import BillingAccountsPage
from pages.client_profile_page import ClientProfilePage
from tests.conftest import CreatedImsis


@allure.suite("E2E_85 Откат биллинга")
@allure.link(url="jira.nexign.com/browse/TUDS-2569", name="TUDS-2569")
@allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=555189386", name="Откат биллинга по клиенту")
@pytest.mark.regress
class TestBillingRollback:
    @pytest.fixture(autouse=True)
    def setup(
        self,
        nexign_ui_stand_login: Page,
        api_request_auth_context: APIRequestContext,
        create_individual_user: IndividualClient,
        add_two_imsi_free_shipped: CreatedImsis,
    ):
        self.client_profile = ClientProfilePage(nexign_ui_stand_login)
        self.billing_accounts_page = BillingAccountsPage(nexign_ui_stand_login)
        self.client_api = ClientInquiriesRequests(api_request_auth_context)
        self.personal_account_api = PersonalAccountRequests(api_request_auth_context)
        self.payment_api = PaymentsRequests(api_request_auth_context)
        self.billing_api = BillingRequests(api_request_auth_context)

        self.client = create_individual_user
        self.client, self.product = self.client_api.product_sale(self.client.user_id, category="internet")
        balance = 100.00
        self.payment_api.create_default_payment(
            self.client.agreements[0].accounts[0].id,
            self.product.one_time_payment + self.product.subscription_fee + balance,
        )
        self.personal_account_api.wait_accruals(self.client.user_id)

        self.billing_profile_id = self.billing_api.get_billing_profile_id(self.client.agreements[0].accounts[0].id)
        self.billing_api.run_unscheduled_billing(self.billing_profile_id)
        self.billing_api.wait_billing(self.billing_profile_id)
        self.billing_api.wait_finish_billing(self.billing_profile_id, 3)

    @allure.title("Отмена отката внеочередного биллинга")
    @allure.id(577548)
    @allure.description("Отмена отката биллинга в окне подтверждения отката биллинга из пользовательского интерфейса")
    def test_undoing_extraordinary_billing(self, base_url: str):
        with allure.step('Перейти на форму "Биллинговые счета" и открыть последний биллинговый счёт'):
            self.client_profile.open(
                f"{base_url}customer-hierarchy-management/accounts/{self.client.agreements[0].accounts[0].id}/account"
            )
            self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Биллинговые счета")
            self.billing_accounts_page.locators.BILLING_LAUNCH_BTN.wait_to_be_visible()
            self.billing_accounts_page.locators.ACCOUNT_NUMS_LIST.click(0)
            self.billing_accounts_page.check_billing_properties()

        with allure.step('Нажать кнопку "Откатить биллинг" и нажать кнопку "Отмена"'):
            self.billing_accounts_page.locators.BILLING_BTNS.click(0)
            self.billing_accounts_page.locators.MODAL.wait_to_be_visible()
            self.billing_accounts_page.locators.MODAL_BODY_TEXT[0].wait_to_have_text(
                re.compile(
                    r"Будет выполнен откат внеочередного биллинга от \d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2}."
                    r"Количество счетов: 1"
                )
            )
            self.billing_accounts_page.locators.MODAL_FIRST_BTN.click()
            self.billing_accounts_page.locators.MODAL.wait_not_to_be_visible()

        with allure.step(
            'Нажать кнопку "Список заданий биллинга", проверить, закрыть список заданий биллинга, проверить что биллинговый счет не удалился'
        ):
            self.billing_accounts_page.locators.BILLING_TASKS_BTN.click()
            self.billing_accounts_page.check_billing_task(task_type="Биллинг", status="Завершено")
            self.billing_accounts_page.locators.TASKS_CLOSE_BTN.click()
            self.billing_accounts_page.locators.REFRESH_BTN.click()
            self.billing_accounts_page.locators.ACCOUNT_NUMS_LIST.wait_to_have_count(1)

    @allure.title("Повторный внеочередной биллинг после отката")
    @allure.id(579148)
    @allure.description("Успешное проведение внеочередного биллинга, после отката внеочередного биллинга")
    def test_rebilling_after_rollback(self, base_url: str):
        with allure.step('Перейти на форму "Биллинговые счета" и открыть последний биллинговый счёт'):
            self.client_profile.open(
                f"{base_url}customer-hierarchy-management/accounts/{self.client.agreements[0].accounts[0].id}/account"
            )
            self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Биллинговые счета")
            self.billing_accounts_page.locators.REFRESH_BTN.click()
            self.billing_accounts_page.locators.ACCOUNT_NUMS_LIST.click(0)

            self.billing_accounts_page.check_billing_properties()

        with allure.step('Нажать кнопку "Откатить биллинг" и нажать кнопку "Выполнить"'):
            self.billing_accounts_page.locators.BILLING_BTNS.click(0)
            self.billing_accounts_page.locators.MODAL.wait_to_be_visible()
            self.billing_accounts_page.locators.MODAL_BODY_TEXT[0].wait_to_have_text(
                re.compile(
                    r"Будет выполнен откат внеочередного биллинга от \d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2}."
                    r"Количество счетов: 1"
                )
            )
            self.billing_accounts_page.locators.MODAL_SECOND_BTN.click()
            self.billing_accounts_page.locators.MODAL.wait_not_to_be_visible()
            rollback_popup_text = re.compile(
                rf"Запущен откат внеочередного биллинга от \d{{2}}\.\d{{2}}\.\d{{4}} \d{{2}}:\d{{2}}:\d{{2}} по лицевому счету: {self.client.agreements[0].accounts[0].number} Задание: \d{{4}}-\d{{12}}-\d{{2}}"
            )
            self.billing_accounts_page.locators.INFO_MESSAGE[0].wait_to_have_text("Формируется заявка на откат")
            self.billing_accounts_page.locators.INFO_MESSAGE.wait_elements_visible(1)
            self.billing_accounts_page.locators.INFO_MESSAGE[-1].wait_to_have_text(rollback_popup_text)
            self.billing_api.wait_billing(self.billing_profile_id, 2)
            self.billing_api.wait_finish_billing(self.billing_profile_id, 3)

        with allure.step(
            'Нажать кнопку "Список заданий биллинга", проверить, закрыть список заданий биллинга, нажать "Обновить"'
        ):
            self.billing_accounts_page.locators.BILLING_TASKS_BTN.click()

            self.billing_accounts_page.locators.TASK_TYPE_LIST.wait_to_have_count(2)
            self.billing_accounts_page.check_billing_task(task_type="Биллинг", status="Завершено или откачено")
            self.billing_accounts_page.check_billing_task(task_index=1, task_type="Откат биллинга", status="Завершено")
            self.billing_accounts_page.locators.TASKS_CLOSE_BTN.click()
            self.billing_accounts_page.locators.REFRESH_BTN.click()
            self.billing_accounts_page.locators.ACCOUNT_NUMS_LIST.wait_to_have_count(0)

        with allure.step('Нажать на кнопку "Запуск биллинга" и нажать на кнопку "Запустить"'):
            self.billing_accounts_page.locators.BILLING_LAUNCH_BTN.wait_to_be_visible()
            self.billing_accounts_page.run_unscheduled_billing(self.client.agreements[0].accounts[0].number)
            self.billing_api.wait_billing(self.billing_profile_id, 3)
            self.billing_api.wait_finish_billing(self.billing_profile_id, 3)

        with allure.step(
            'Нажать кнопку "Список заданий биллинга", проверить, закрыть список заданий биллинга, нажать "Обновить"'
        ):
            self.billing_accounts_page.locators.BILLING_TASKS_BTN.click()
            self.billing_accounts_page.locators.TASK_TYPE_LIST.wait_to_have_count(3)
            self.billing_accounts_page.check_billing_task(task_type="Биллинг", status="Завершено или откачено")
            self.billing_accounts_page.check_billing_task(task_index=1, task_type="Откат биллинга", status="Завершено")
            self.billing_accounts_page.check_billing_task(task_index=2, task_type="Биллинг", status="Завершено")
            self.billing_accounts_page.locators.TASKS_CLOSE_BTN.click()
            self.billing_accounts_page.locators.REFRESH_BTN.click()

        with allure.step("Открыть биллинговый счёт"):
            self.billing_accounts_page.locators.ACCOUNT_NUMS_LIST.click(0)
            self.billing_accounts_page.check_billing_properties()

    @allure.title("Ошибка при откате не последнего биллинга")
    @allure.id(577552)
    @allure.description(
        "Появление диалогового окна с сообщением об ошибке при попытке отката биллинга, "
        "не являющегося последним проведенным на данном лицевом счете."
    )
    def test_error_undoing_not_last_billing(self, base_url: str):
        with allure.step("Проведение второго биллинга"):
            self.billing_api.run_unscheduled_billing(self.billing_profile_id)
            self.billing_api.wait_finish_billing(self.billing_profile_id, 3)

        with allure.step("Открыть биллинговый счёт, который был сформирован раньше"):
            self.client_profile.open(
                f"{base_url}customer-hierarchy-management/accounts/{self.client.agreements[0].accounts[0].id}/account"
            )
            self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Биллинговые счета")
            self.billing_accounts_page.locators.BILLING_LAUNCH_BTN.wait_to_be_visible()
            self.billing_accounts_page.locators.REFRESH_BTN.click()
            self.billing_accounts_page.locators.ACCOUNT_NUMS_LIST.click(0)

            self.billing_accounts_page.check_billing_properties()

        with allure.step('Нажать кнопку "Откатить биллинг" и нажать кнопку "Выполнить"'):
            self.billing_accounts_page.locators.BILLING_BTNS.click(0)
            self.billing_accounts_page.locators.MODAL.wait_to_be_visible()
            self.billing_accounts_page.locators.MODAL_BODY_TEXT[0].wait_to_have_text(
                re.compile(
                    r"Будет выполнен откат внеочередного биллинга от \d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2}."
                    r"Количество счетов: 1"
                )
            )
            self.billing_accounts_page.locators.MODAL_SECOND_BTN.click()
            self.billing_accounts_page.locators.MODAL.wait_elements_visible(1)

        with allure.step('Закрыть диалоговое окно с сообщением об ошибке и нажать кнопку "Список заданий биллинга"'):
            self.billing_accounts_page.locators.FOOTER_CLOSE_BTN.wait_elements_visible(2)
            self.billing_accounts_page.locators.FOOTER_CLOSE_BTN[-1].click()
            self.billing_accounts_page.locators.MODAL[1].not_to_be_visible()

            self.billing_accounts_page.locators.BILLING_TASKS_BTN.wait_to_be_visible()
            self.billing_accounts_page.locators.BILLING_TASKS_BTN.click()
            self.billing_accounts_page.locators.TASK_TYPE_LIST.wait_to_have_count(2)
            self.billing_accounts_page.check_billing_task(task_type="Биллинг", status="Завершено")
            self.billing_accounts_page.check_billing_task(task_index=1, task_type="Биллинг", status="Завершено")

        with allure.step('Закрыть список заданий биллинга и нажать кнопку "Обновить"'):
            self.billing_accounts_page.locators.TASKS_CLOSE_BTN.click()
            self.billing_accounts_page.locators.REFRESH_BTN.click()
            self.billing_accounts_page.locators.ACCOUNT_NUMS_LIST.wait_to_have_count(2)

    @allure.title("Ошибка при откате биллинга до завершения предыдущего процесса биллинга")
    @allure.id(577553)
    @allure.description(
        "Появление диалогового окна с сообщением об ошибке при попытке отката биллинга, "
        "до завершения предыдущего процесса биллинга."
    )
    def test_error_undoing_before_previous_billing(self, base_url: str):
        with allure.step("Открыть биллинговый счёт, который был сформирован раньше"):
            self.client_profile.open(
                f"{base_url}customer-hierarchy-management/accounts/{self.client.agreements[0].accounts[0].id}/account"
            )
            self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Биллинговые счета")
            self.billing_accounts_page.locators.BILLING_LAUNCH_BTN.wait_to_be_visible()
            self.billing_accounts_page.locators.REFRESH_BTN.click()
            self.billing_accounts_page.locators.ACCOUNT_NUMS_LIST.click(0)

            self.billing_accounts_page.check_billing_properties()

        with allure.step('Нажать на кнопку "Запуск биллинга" и нажать на кнопку "Запустить"'):
            self.billing_accounts_page.locators.BILLING_LAUNCH_BTN.wait_to_be_visible()
            self.billing_accounts_page.run_unscheduled_billing(self.client.agreements[0].accounts[0].number)

        with allure.step('Нажать кнопку "Откатить биллинг" и нажать кнопку "Выполнить"'):
            self.billing_accounts_page.locators.BILLING_BTNS.click(0)
            self.billing_accounts_page.locators.MODAL[1].wait_to_be_visible()
            rollback_modal_text = re.compile(
                r"Будет выполнен откат внеочередного биллинга от \d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2}."
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
            self.billing_accounts_page.locators.TASK_TYPE_LIST.wait_to_have_count(2)
            self.billing_accounts_page.check_billing_task(task_type="Биллинг", status="Завершено")
            self.billing_accounts_page.check_billing_task(task_index=1, task_type="Биллинг", status="Выполняется")
            self.billing_api.wait_finish_billing(self.billing_profile_id, 3)

        with allure.step('Закрыть список заданий биллинга и нажать кнопку "Обновить"'):
            self.billing_accounts_page.locators.TASKS_CLOSE_BTN.click()
            self.billing_accounts_page.locators.REFRESH_BTN.wait_to_be_visible()
            self.billing_accounts_page.locators.REFRESH_BTN.click()
            self.billing_accounts_page.locators.ACCOUNT_NUMS_LIST.wait_to_have_count(2)
