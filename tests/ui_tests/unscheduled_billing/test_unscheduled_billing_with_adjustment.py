import allure
import pytest
from playwright.sync_api import APIRequestContext, Page

from api.requests.adjustment_requests import AdjustmentRequests
from api.requests.billing_requests import BillingRequests
from api.requests.client_requests import ClientRequests
from api.requests.payments_requests import PaymentsRequests
from api.requests.personal_account_requests import PersonalAccountRequests
from common.helpers.data_generator import calc_tax, get_datetime_from_full_time_string
from common.helpers.env_helper import UserData
from common.helpers.time_helpers import get_current_moscow_datetime, get_shifted_datetime
from models.user import IndividualClient
from pages.billing_accounts_page import BillingAccountsPage
from pages.client_profile_page import ClientProfilePage
from pages.inquiries_page import InquiriesPage


@allure.suite("E2E_86 Проведение внеочередного биллинга")
@pytest.mark.regress
class TestUnscheduledBillingWithAdjustment:
    @pytest.fixture(autouse=True)
    def setup(
        self,
        nexign_ui_stand_login: Page,
        api_request_auth_context: APIRequestContext,
        create_user_with_postpaid_account: IndividualClient,
    ) -> None:
        self.client_request_api = ClientRequests(api_request_auth_context)
        self.personal_account_api = PersonalAccountRequests(api_request_auth_context)
        self.payment_api = PaymentsRequests(api_request_auth_context)
        self.billing_api = BillingRequests(api_request_auth_context)
        self.adjustment_api = AdjustmentRequests(api_request_auth_context)
        self.client_profile = ClientProfilePage(nexign_ui_stand_login)
        self.inquiries_page = InquiriesPage(nexign_ui_stand_login)
        self.billing_accounts_page = BillingAccountsPage(nexign_ui_stand_login)
        self.client = create_user_with_postpaid_account
        self.payment_period = 50

        with allure.step("Выполнение предусловий"):
            with allure.step(f"Продажа интернета для постоплатного ЛС {self.client.account_id}"):
                self.client, self.product = self.client_request_api.product_sale(
                    self.client.user_id,
                    category="internet",
                    agreement_id=self.client.agreement_id,
                    account_id=self.client.account_id,
                )
                self.total = self.product.one_time_payment + self.product.subscription_fee
                self.personal_account_api.wait_check_current_main_balance(self.client.account_id, -self.total)

            with allure.step(f"Добавление платежа на сумму {self.product.one_time_payment + 50}"):
                self.amount = self.product.one_time_payment + 50
                self.adjustment_sum = self.total - self.amount
                self.payment_api.create_default_payment(self.client.account_id, self.amount)
                self.personal_account_api.wait_check_current_main_balance(self.client.account_id, -self.adjustment_sum)
                self.personal_account_api.wait_accruals(self.client.user_id)
                self.payment_data = self.payment_api.get_payments(self.client.account_id).json()["items"][0]
                self.payment_date = get_datetime_from_full_time_string(self.payment_data["paymentDate"], True)

            with allure.step("Проведение внеочередного биллинга"):
                self.billing_profile_id = self.billing_api.get_billing_profile_id(self.client.account_id)
                self.billing_api.run_unscheduled_billing(self.billing_profile_id)
                self.billing_api.wait_billing(self.billing_profile_id)
                self.billing_api.wait_finish_billing(self.billing_profile_id, 3, 100)
                self.bill_data = self.billing_api.get_list_of_bills([self.billing_profile_id])[0]
                self.first_billing_date = get_datetime_from_full_time_string(
                    self.bill_data["billingRun"]["period"]["endDateTime"], True
                )
                self.first_payment_due = get_shifted_datetime(f"+{self.payment_period}d", self.first_billing_date)

    @allure.title("Проведение внеочередного биллинга для начислений с корректировкой начисления")
    @allure.description(
        "Запуск внеочередного биллинга. Проверка данных на форме биллинговые счета \n"
        "Баланс положительный и покрывает начисления поступившие на лицевой счет"
    )
    @allure.id(574963)
    def test_run_unscheduled_billing_with_charge_adjustment(self, base_url: str) -> None:
        bill_id = self.bill_data["billId"]

        with allure.step("Добавим корректировку начисления"):
            self.adjustment_api.create_adjustment(
                adjustment_type_id=2,
                adjustment_reason_id=2,
                bill_id=bill_id,
                bill_detail_value_id=self.billing_api.get_bill_detail_value_id(bill_id),
                billing_profile_id=self.billing_profile_id,
                amount=self.adjustment_sum,
            )
            self.adjustment_api.wait_adjustment_status(self.client.account_id)
            self.adjustment_data = self.adjustment_api.get_adjustment_list(self.client.account_id)["items"][0]

        with allure.step("Выбрав лицевой счет клиента, переходим на форму 'Биллинговые счета'"):
            self.client_profile.open(
                f"{base_url}customer-hierarchy-management/accounts/{self.client.account_id}/account"
            )
            self.client_profile.locators.CLIENT_FIO.wait_to_be_visible()
            self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Биллинговые счета")

        with allure.step("На форме биллинговые счета нажимаем на кнопку 'Запуск биллинга' (+)"):
            second_billing_date = get_current_moscow_datetime()
            second_payment_due = get_shifted_datetime(f"+{self.payment_period}d", second_billing_date)
            second_billing_task = self.billing_accounts_page.run_unscheduled_billing()

        with allure.step("Нажимаем на кнопку 'Список заданий биллинга'"):
            self.billing_accounts_page.locators.BILLING_TASKS_BTN.click()
            self.billing_accounts_page.locators.BILLING_TASK.wait_to_have_count(2)
            self.billing_accounts_page.check_billing_task(
                task_index=1, billing_type="Внеочередной биллинг", status="Выполняется"
            )
            self.billing_api.wait_finish_billing(self.billing_profile_id)

        self.billing_accounts_page.locators.UPDATE_BILLING_TASKS_BTN.click()
        self.billing_accounts_page.check_billing_task(
            task_index=1,
            task=second_billing_task,
            task_type="Биллинг",
            run_date=second_billing_date,
            status="Завершено",
            user=UserData.login,
            billing_type="Внеочередной биллинг",
            bill_date=second_billing_date,
        )

        with allure.step("Закрываем форму 'Задания биллинга', нажимаем на кнопку 'Обновить'"):
            self.billing_accounts_page.locators.TASKS_CLOSE_BTN.click()
            self.billing_accounts_page.locators.REFRESH_BTN.click()
            self.billing_accounts_page.check_bill(bill_index=0)
            self.billing_accounts_page.check_bill(bill_index=1)

        with allure.step("Проверяем данные о первом счете"):
            with allure.step("Нажимаем на запись о счете"):
                self.billing_accounts_page.locators.ACCOUNT_NUMS_LIST.click(0)
                self.billing_accounts_page.check_billing_properties_value(
                    payment_due=self.first_payment_due,
                    amount_due=self.adjustment_sum,
                    end_period=self.first_billing_date,
                    output_balance=self.adjustment_sum,
                    paid=self.adjustment_sum,
                    adjusted_accruals=-self.adjustment_sum,
                    charges_recorded=self.total,
                    payments_recorded=self.amount,
                    generation_date=self.first_billing_date,
                )

            with allure.step("Переходим на вкладку 'Детали'"):
                self.billing_accounts_page.locators.DETAILS_TAB.click()
                self.billing_accounts_page.locators.DETAIL.wait_to_have_count(2)
                self.billing_accounts_page.check_detail(
                    detail_name="Абон. плата за предоставление доступа к сети оператора и в интернет (Интернет домашний безлимитный)",
                    charged=self.product.subscription_fee,
                    subscriber=self.product.internet_number,
                    adjusted=self.adjustment_sum,
                    product=self.product.product_name,
                    repaid=self.product.subscription_fee - self.adjustment_sum,
                    available_for_adjustment=self.product.subscription_fee - self.adjustment_sum,
                )
                self.billing_accounts_page.check_detail(
                    detail_index=1,
                    detail_name="Разовое списание за подключение доступа к сети и в интернет (Интернет домашний безлимитный)",
                    charged=self.product.one_time_payment,
                    subscriber=self.product.internet_number,
                    product=self.product.product_name,
                    repaid=self.product.one_time_payment,
                    available_for_adjustment=self.product.one_time_payment,
                )

            with allure.step("Переходим на вкладку 'Счета-фактуры'"):
                self.billing_accounts_page.locators.INVOICES_TAB.click()
                self.billing_accounts_page.locators.INVOICE.wait_to_have_count(2)
                self.billing_accounts_page.check_invoice(
                    invoice_type="Авансовый счет-фактура",
                    date=self.payment_date,
                    amount=self.amount,
                    tax=calc_tax(self.amount),
                )
                self.billing_accounts_page.check_invoice(
                    invoice_index=1,
                    invoice_type="Счет-фактура на начисления",
                    date=self.first_billing_date,
                    amount=self.total,
                    tax=calc_tax(self.product.subscription_fee + self.product.one_time_payment),
                    adjusted=self.adjustment_sum,
                    balance=self.amount,
                )
                tax_invoice_number = self.billing_accounts_page.locators.INVOICE_NUMBER[1].text

            with allure.step("Переходим на вкладку 'Документы'"):
                self.billing_accounts_page.locators.DOCUMENTS_TAB.click()
                self.billing_accounts_page.locators.NO_DOCUMENT_BLOCK.wait_to_be_visible()

            with allure.step("Переходим на вкладку 'Связанные операции'"):
                self.billing_accounts_page.locators.LINKED_OPERATIONS_TAB.click()
                self.billing_accounts_page.check_linked_operation_tab(self.total, self.adjustment_sum)
                self.billing_accounts_page.locators.LINKED_OPERATIONS_NAME.click(0)
                self.billing_accounts_page.locators.TABLE_ROW_LINKED_OPERATION.wait_to_have_count(2)
                self.billing_accounts_page.check_repayments(
                    repayments_object=f"Платеж N {self.payment_data['documentNumber']}",
                    date=self.payment_date,
                    amount=self.amount,
                )
                self.billing_accounts_page.check_repayments(
                    repayments_index=1,
                    repayments_object=f"Корректировка N {self.adjustment_data['adjustmentId']}",
                    date=get_datetime_from_full_time_string(self.adjustment_data["adjustmentDate"], True),
                    amount=self.adjustment_sum,
                )
                self.billing_accounts_page.locators.LINKED_OPERATIONS_NAME.click(1)
                self.billing_accounts_page.locators.TABLE_ROW_LINKED_OPERATION.wait_to_have_count(1)
                self.billing_accounts_page.check_debited(
                    date=get_datetime_from_full_time_string(self.adjustment_data["adjustmentDate"], True),
                    amount=self.adjustment_sum,
                    tax=self.adjustment_data["sumInfo"]["tax"],
                    detail="Абон. плата за предоставление доступа к сети оператора и в интернет (Интернет домашний безлимитный)",
                    reason="Отрицательная корректировка детали счета",
                )

            with allure.step("Переходим на вкладку 'Внереализационные начисления'"):
                self.billing_accounts_page.locators.NON_OPERATING_INCOMES_TAB.click()
                self.billing_accounts_page.locators.NO_RECORDS_NON_OPERATING_INCOMES_FOUND.wait_to_be_visible()

        with allure.step("Проверяем данные о втором счете"):
            with allure.step("Нажимаем на запись о счете"):
                self.billing_accounts_page.locators.ACCOUNT_NUMS_LIST.click(1)
                self.billing_accounts_page.locators.PROPERTIES_TAB.click()
                self.billing_accounts_page.check_billing_properties_value(
                    payment_due=second_payment_due,
                    start_period=self.first_billing_date,
                    end_period=second_billing_date,
                    input_balance=self.adjustment_sum,
                    charge_adjustments_recorded=-self.adjustment_sum,
                    generation_date=second_billing_date,
                )

            with allure.step("Переходим на вкладку 'Детали'"):
                self.billing_accounts_page.locators.DETAILS_TAB.click()
                self.billing_accounts_page.locators.DETAIL.wait_to_have_count(1)
                self.billing_accounts_page.check_detail(
                    detail_name="Абон. плата за предоставление доступа к сети оператора и в интернет (Интернет домашний безлимитный)",
                    charged=-self.adjustment_sum,
                )

            with allure.step("Переходим на вкладку 'Счета-фактуры'"):
                self.billing_accounts_page.locators.INVOICES_TAB.click()
                self.billing_accounts_page.locators.INVOICE.wait_to_have_count(2)
                self.billing_accounts_page.check_invoice(
                    invoice_type="Авансовый счет-фактура",
                    date=second_billing_date,
                    amount=self.adjustment_sum,
                    tax=calc_tax(self.adjustment_sum),
                )
                self.billing_accounts_page.check_invoice(
                    invoice_index=1,
                    invoice_type="Исправленный счет-фактура на начисления",
                    number=tax_invoice_number,
                    date=self.first_billing_date,
                    amount=self.product.subscription_fee - self.adjustment_sum,
                    tax=calc_tax(self.product.subscription_fee - self.adjustment_sum),
                    adjustment_tax_invoice=tax_invoice_number,
                    adjustment_number=1,
                    adjustment_date=second_billing_date,
                    adjusted=0,
                    balance=0,
                )

            with allure.step("Переходим на вкладку 'Документы'"):
                self.billing_accounts_page.locators.DOCUMENTS_TAB.click()
                self.billing_accounts_page.locators.NO_DOCUMENT_BLOCK.wait_to_be_visible()

            with allure.step("Переходим на вкладку 'Связанные операции'"):
                self.billing_accounts_page.locators.LINKED_OPERATIONS_TAB.click()
                self.billing_accounts_page.check_linked_operation_tab()

            with allure.step("Переходим на вкладку 'Внереализационные начисления'"):
                self.billing_accounts_page.locators.NON_OPERATING_INCOMES_TAB.click()
                self.billing_accounts_page.locators.NO_RECORDS_NON_OPERATING_INCOMES_FOUND.wait_to_be_visible()

    @allure.title("Проведение внеочередного биллинга для начислений с корректировкой платежа")
    @allure.description(
        "Запуск внеочередного биллинга. Проверка данных на форме биллинговые счета \n"
        "Баланс положительный и покрывает начисления поступившие на лицевой счет"
    )
    @allure.id(575331)
    def test_run_unscheduled_billing_with_payment_adjustment(self, base_url: str) -> None:
        billing_payment_id = int(self.payment_api.get_payments(self.client.account_id).json()["items"][0]["paymentId"])

        with allure.step("Добавим корректировку платежа"):
            self.adjustment_api.create_adjustment(
                adjustment_type_id=10,
                adjustment_reason_id=13,
                billing_payment_id=billing_payment_id,
                billing_profile_id=self.billing_profile_id,
                amount=self.adjustment_sum,
            )
            self.adjustment_api.wait_adjustment_status(self.client.account_id)

        with allure.step("Выбрав лицевой счет клиента, переходим на форму 'Биллинговые счета'"):
            self.client_profile.open(
                f"{base_url}customer-hierarchy-management/accounts/{self.client.account_id}/account"
            )
            self.client_profile.locators.CLIENT_FIO.wait_to_be_visible()
            self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Биллинговые счета")

        with allure.step("На форме биллинговые счета нажимаем на кнопку 'Запуск биллинга' (+)"):
            second_billing_date = get_current_moscow_datetime()
            second_payment_due = get_shifted_datetime(f"+{self.payment_period}d", second_billing_date)
            second_billing_task = self.billing_accounts_page.run_unscheduled_billing()

        with allure.step("Нажимаем на кнопку 'Список заданий биллинга'"):
            self.billing_accounts_page.locators.BILLING_TASKS_BTN.click()
            self.billing_accounts_page.locators.BILLING_TASK.wait_to_have_count(2)
            self.billing_accounts_page.check_billing_task(
                task_index=1, billing_type="Внеочередной биллинг", status="Выполняется"
            )
            self.billing_api.wait_finish_billing(self.billing_profile_id)

        self.billing_accounts_page.locators.UPDATE_BILLING_TASKS_BTN.click()
        self.billing_accounts_page.check_billing_task(
            task_index=1,
            task=second_billing_task,
            task_type="Биллинг",
            run_date=second_billing_date,
            status="Завершено",
            user=UserData.login,
            billing_type="Внеочередной биллинг",
            bill_date=second_billing_date,
        )

        with allure.step(
            "Закрываем форму 'Задания биллинга' На форме 'Биллинговые счета' нажимаем на кнопку 'Обновить'"
        ):
            self.billing_accounts_page.locators.TASKS_CLOSE_BTN.click()
            self.billing_accounts_page.locators.REFRESH_BTN.click()
            self.billing_accounts_page.check_bill(bill_index=0)
            self.billing_accounts_page.check_bill(bill_index=1)

        with allure.step("Проверяем данные о первом счете"):
            with allure.step("Нажимаем на запись о счете"):
                self.billing_accounts_page.locators.ACCOUNT_NUMS_LIST.click(0)
                self.billing_accounts_page.check_billing_properties_value(
                    payment_due=self.first_payment_due,
                    amount_due=self.adjustment_sum,
                    end_period=self.first_billing_date,
                    output_balance=self.adjustment_sum,
                    paid=self.adjustment_sum,
                    adjusted_payments=-self.adjustment_sum,
                    charges_recorded=self.total,
                    payments_recorded=self.amount,
                    generation_date=self.first_billing_date,
                )

            with allure.step("Переходим на вкладку 'Детали'"):
                self.billing_accounts_page.locators.DETAILS_TAB.click()
                self.billing_accounts_page.locators.DETAIL.wait_to_have_count(2)
                self.billing_accounts_page.check_detail(
                    detail_name="Абон. плата за предоставление доступа к сети оператора и в интернет (Интернет домашний безлимитный)",
                    charged=self.product.subscription_fee,
                    subscriber=self.product.internet_number,
                    product=self.product.product_name,
                    repaid=self.product.subscription_fee,
                    available_for_adjustment=self.product.subscription_fee,
                )
                self.billing_accounts_page.check_detail(
                    detail_index=1,
                    detail_name="Разовое списание за подключение доступа к сети и в интернет (Интернет домашний безлимитный)",
                    charged=self.product.one_time_payment,
                    subscriber=self.product.internet_number,
                    product=self.product.product_name,
                    repaid=self.product.one_time_payment,
                    available_for_adjustment=self.product.one_time_payment,
                )

            with allure.step("Переходим на вкладку 'Счета-фактуры'"):
                self.billing_accounts_page.locators.INVOICES_TAB.click()
                self.billing_accounts_page.locators.INVOICE.wait_to_have_count(2)
                self.billing_accounts_page.check_invoice(
                    invoice_type="Авансовый счет-фактура",
                    date=self.payment_date,
                    amount=self.amount,
                    tax=calc_tax(self.amount),
                )
                self.billing_accounts_page.check_invoice(
                    invoice_index=1,
                    invoice_type="Счет-фактура на начисления",
                    date=self.first_billing_date,
                    amount=self.total,
                    tax=calc_tax(self.product.subscription_fee + self.product.one_time_payment),
                    adjusted=0,
                    balance=self.total,
                )

            with allure.step("Переходим на вкладку 'Документы'"):
                self.billing_accounts_page.locators.DOCUMENTS_TAB.click()
                self.billing_accounts_page.locators.NO_DOCUMENT_BLOCK.wait_to_be_visible()

            with allure.step("Переходим на вкладку 'Связанные операции'"):
                self.billing_accounts_page.locators.LINKED_OPERATIONS_TAB.click()
                self.billing_accounts_page.check_linked_operation_tab(
                    self.total,
                )
                self.billing_accounts_page.locators.LINKED_OPERATIONS_NAME.click(0)
                self.billing_accounts_page.locators.TABLE_ROW_LINKED_OPERATION.wait_to_have_count(2)
                self.billing_accounts_page.check_repayments(
                    repayments_object=f"Платеж N {self.payment_data['documentNumber']}",
                    date=self.payment_date,
                    amount=self.amount,
                )
                self.billing_accounts_page.check_repayments(
                    repayments_index=1,
                    repayments_object=f"Корректировка N {self.adjustment_data['adjustmentId']}",
                    date=get_datetime_from_full_time_string(self.adjustment_data["adjustmentDate"], True),
                    amount=self.adjustment_sum,
                )

            with allure.step("Переходим на вкладку 'Внереализационные начисления'"):
                self.billing_accounts_page.locators.NON_OPERATING_INCOMES_TAB.click()
                self.billing_accounts_page.locators.NO_RECORDS_NON_OPERATING_INCOMES_FOUND.wait_to_be_visible()

        with allure.step("Проверяем данные о втором счете"):
            with allure.step("Нажимаем на запись о счете"):
                self.billing_accounts_page.locators.ACCOUNT_NUMS_LIST.click(1)
                self.billing_accounts_page.locators.PROPERTIES_TAB.click()
                self.billing_accounts_page.check_billing_properties_value(
                    payment_due=second_payment_due,
                    start_period=self.first_billing_date,
                    end_period=second_billing_date,
                    input_balance=self.adjustment_sum,
                    charge_adjustments_recorded=-self.adjustment_sum,
                    generation_date=second_billing_date,
                )

            with allure.step("Переходим на вкладку 'Детали'"):
                self.billing_accounts_page.locators.DETAILS_TAB.click()
                self.billing_accounts_page.locators.NO_DETAIL_BLOCK.click()

            with allure.step("Переходим на вкладку 'Счета-фактуры'"):
                self.billing_accounts_page.locators.INVOICES_TAB.click()
                self.billing_accounts_page.locators.INVOICE.wait_to_have_count(2)
                self.billing_accounts_page.check_invoice(
                    invoice_type="Авансовый счет-фактура",
                    date=second_billing_date,
                    amount=self.adjustment_sum,
                    tax=calc_tax(self.adjustment_sum),
                )

            with allure.step("Переходим на вкладку 'Документы'"):
                self.billing_accounts_page.locators.DOCUMENTS_TAB.click()
                self.billing_accounts_page.locators.NO_DOCUMENT_BLOCK.wait_to_be_visible()

            with allure.step("Переходим на вкладку 'Связанные операции'"):
                self.billing_accounts_page.locators.LINKED_OPERATIONS_TAB.click()
                self.billing_accounts_page.check_linked_operation_tab()

            with allure.step("Переходим на вкладку 'Внереализационные начисления'"):
                self.billing_accounts_page.locators.NON_OPERATING_INCOMES_TAB.click()
                self.billing_accounts_page.locators.NO_RECORDS_NON_OPERATING_INCOMES_FOUND.wait_to_be_visible()
