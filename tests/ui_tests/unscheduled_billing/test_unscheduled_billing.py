import allure
import pytest
from playwright.sync_api import APIRequestContext, Page

from api.requests.billing_requests import BillingRequests
from api.requests.payments_requests import PaymentsRequests
from api.requests.personal_account_requests import PersonalAccountRequests
from common.helpers.data_generator import round_up
from common.helpers.env_helper import UserData
from common.helpers.string_helper import check_price
from common.helpers.time_helpers import get_current_moscow_datetime
from pages.billing_accounts_page import BillingAccountsPage
from pages.client_profile_page import ClientProfilePage
from pages.locators.inquiries_page import InquiriesPage
from tests.ui_tests.conftest import ClientInfo


@allure.suite("E2E_86 Проведение внеочередного биллинга")
class TestUnscheduledBilling:
    @pytest.fixture(autouse=True)
    def setup(
        self,
        nexign_ui_stand_login: Page,
        api_request_auth_context: APIRequestContext,
        create_user: int,
    ) -> None:
        self.personal_account_api = PersonalAccountRequests(api_request_auth_context)
        self.payment_api = PaymentsRequests(api_request_auth_context)
        self.billing_api = BillingRequests(api_request_auth_context)

        self.client_profile = ClientProfilePage(nexign_ui_stand_login)
        self.inquiries_page = InquiriesPage(nexign_ui_stand_login)
        self.billing_accounts_page = BillingAccountsPage(nexign_ui_stand_login)
        self.client = ClientInfo(user_id=create_user)

    @allure.title("Проведение внеочередного биллинга, начисления оплачены")
    @allure.tag("can_aurh", "success")
    @allure.description(
        "Запуск внеочередного биллинга. Проверка данных на форме биллинговые счета. "
        "Баланс нулевой, начисления на личном счете оплачены."
    )
    @allure.id(575595)
    @pytest.mark.regress
    def test_run_unscheduled_billing_with_charge(self, base_url: str) -> None:
        with allure.step("Выполнение предусловий"):
            self.client_profile.open(f"{base_url}customer-hierarchy-management/customers/{self.client.user_id}/overview")
            product = self.inquiries_page.sale_internet()
            amount = product.one_time_payment + product.subscription_fee
            self.client.account_id = self.personal_account_api.get_personal_accounts(
                "customer", self.client.user_id
            ).json()["items"][0]["accountId"]
            self.payment_api.create_default_payment(self.client.account_id, amount)
            self.personal_account_api.wait_check_current_main_balance(self.client.account_id, amount)
            self.personal_account_api.wait_check_current_main_balance(self.client.account_id, 0)
            self.client_profile.open(
                f"{base_url}customer-hierarchy-management/accounts/{self.client.account_id}/account"
            )

        with allure.step("Переходим на форму 'Биллинговые счета'"):
            self.client_profile.locators.BURGER_MENU.select_by_value("Биллинговые счета")
            self.billing_accounts_page.base_elements.PAGE_TITLE.wait_to_have_text("Биллинговые счета")

        with allure.step("На форме биллинговые счета нажимаем на кнопку 'Запуск биллинга' (+)"):
            billing_date = get_current_moscow_datetime()
            billing_task = self.billing_accounts_page.run_unscheduled_billing()

        with allure.step("Нажимаем на кнопку 'Список заданий биллинга'"):
            self.billing_accounts_page.locators.BILLING_TASKS_BTN.click()
            self.billing_accounts_page.locators.BILLING_TASK.wait_to_have_count(1)
            self.billing_accounts_page.check_billing_task(billing_type="Внеочередной биллинг", status="Выполняется")
            self.billing_api.wait_finish_billing(self.billing_api.get_billing_profile_id(self.client.account_id))

        self.billing_accounts_page.locators.UPDATE_BILLING_TASKS_BTN.click()
        self.billing_accounts_page.check_billing_task(
            task=billing_task,
            task_type="Биллинг",
            run_date=billing_date,
            status="Завершено",
            user=UserData.login,
            billing_type="Внеочередной биллинг",
            bill_date=billing_date,
        )

        with allure.step(
            "Закрываем форму 'Задания биллинга' На форме 'Биллинговые счета' нажимаем на кнопку 'Обновить'"
        ):
            self.billing_accounts_page.locators.TASKS_CLOSE_BTN.click()
            self.billing_accounts_page.locators.REFRESH_BTN.click()
            self.billing_accounts_page.check_bill()

        with allure.step("Нажимаем на запись о созданном нами счете"):
            self.billing_accounts_page.locators.ACCOUNT_NUMS_LIST.click(0)
            self.billing_accounts_page.check_billing_properties_value(
                payment_due=billing_date,
                end_period=billing_date,
                charged=amount,
                charges_recorded=amount,
                generation_date=billing_date,
            )

        with allure.step("Переходим на вкладку 'Детали'"):
            self.billing_accounts_page.locators.DETAILS_TAB.click()
            self.billing_accounts_page.check_detail(
                detail_index=0,
                detail_name="Абон. плата за предоставление доступа к сети оператора и в интернет (Интернет домашний безлимитный)",
                charged=product.subscription_fee,
                subscriber=product.internet_number,
                product=product.product_name,
                repaid=product.subscription_fee,
                available_for_adjustment=product.subscription_fee,
            )
            self.billing_accounts_page.check_detail(
                detail_index=1,
                detail_name="Разовое списание за подключение доступа к сети и в интернет (Интернет домашний безлимитный)",
                charged=product.one_time_payment,
                subscriber=product.internet_number,
                product=product.product_name,
                repaid=product.one_time_payment,
                available_for_adjustment=product.one_time_payment,
            )

        with allure.step("Переходим на вкладку 'Счета-фактуры'"):
            self.billing_accounts_page.locators.INVOICES_TAB.click()
            self.billing_accounts_page.check_invoice(
                invoice_index=0,
                invoice_type="Авансовый счет-фактура",
                date=billing_date,
                amount=amount,
                tax=round(amount / 6, 2),
            )
            self.billing_accounts_page.check_invoice(
                invoice_index=1,
                invoice_type="Счет-фактура на начисления",
                date=billing_date,
                amount=amount,
                tax=round_up(amount / 6, 2),
                adjusted=0,
                balance=amount,
            )

        with allure.step("Переходим на вкладку 'Документы'"):
            self.billing_accounts_page.locators.DOCUMENTS_TAB.click()
            self.billing_accounts_page.locators.NO_DOCUMENT_BLOCK.wait_to_be_visible()

        with allure.step("Переходим на вкладку 'Связанные операции'"):
            self.billing_accounts_page.locators.LINKED_OPERATIONS_TAB.click()
            self.billing_accounts_page.locators.LINKED_OPERATIONS_NAME.wait_for_text_in_all(
                ["Погашение", "Списано", "Доначислено"]
            )
            self.billing_accounts_page.locators.LINKED_OPERATIONS_VALUE_LOADER.wait_not_to_be_visible()
            check_price(self.billing_accounts_page.locators.LINKED_OPERATIONS_VALUE[0], amount)
            check_price(self.billing_accounts_page.locators.LINKED_OPERATIONS_VALUE[1], 0)
            check_price(self.billing_accounts_page.locators.LINKED_OPERATIONS_VALUE[2], 0)

        with allure.step("Нажимаем на пункт 'Погашение'"):
            self.billing_accounts_page.locators.LINKED_OPERATIONS_NAME[0].click()
            self.billing_accounts_page.locators.TABLE_ROW_LINKED_OPERATION.wait_to_have_count(1)

        with allure.step("По остальным пунктам отсутствует информация"):
            self.billing_accounts_page.locators.LINKED_OPERATIONS_NAME[1].click()
            self.billing_accounts_page.locators.NO_RECORDS_LINKED_OPERATION_FOUND.wait_to_be_visible()
            self.billing_accounts_page.locators.LINKED_OPERATIONS_NAME[2].click()
            self.billing_accounts_page.locators.NO_RECORDS_LINKED_OPERATION_FOUND.wait_to_be_visible()

        with allure.step("Переходим на вкладку 'Внереализационные начисления'"):
            self.billing_accounts_page.locators.NON_OPERATING_INCOMES_TAB.click()
            self.billing_accounts_page.locators.NO_RECORDS_NON_OPERATING_INCOMES_FOUND.wait_to_be_visible()
