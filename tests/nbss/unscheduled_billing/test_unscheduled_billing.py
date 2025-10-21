import allure
import pytest
from playwright.sync_api import APIRequestContext, Page

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from api.nbss.finances.billing_requests import BillingRequests
from api.nbss.finances.payments_requests import PaymentsRequests
from api.nbss.personal_account_requests import PersonalAccountRequests
from common.helpers.data_generator import calc_tax
from common.helpers.env_helper import UserData
from common.helpers.time_helpers import get_current_moscow_datetime, get_shifted_datetime
from models.user import IndividualClient
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.finances.billing_accounts_page import BillingAccountsPage


@allure.suite("E2E_86 Проведение внеочередного биллинга")
@pytest.mark.regress
@pytest.mark.nbss_portal
@pytest.mark.bia
class TestUnscheduledBilling:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_ui_stand_login: Page, api_request_context: APIRequestContext) -> None:
        self.client_request_api = ClientInquiriesRequests(api_request_context)
        self.personal_account_api = PersonalAccountRequests(api_request_context)
        self.payment_api = PaymentsRequests(api_request_context)
        self.billing_api = BillingRequests(api_request_context)
        self.client_profile = ClientProfilePage(nexign_ui_stand_login)
        self.billing_accounts_page = BillingAccountsPage(nexign_ui_stand_login)
        self.payment_period = 50

    @allure.title("Проведение внеочередного биллинга, начисления не оплачены")
    @allure.description(
        "Запуск внеочередного биллинга. Проверка данных на форме биллинговые счета \n"
        "Баланс отрицательный, начисления на личном счете не оплачены"
    )
    @allure.id(574935)
    def test_run_unscheduled_billing_with_unpaid_charge(
        self, base_url: str, create_user_with_postpaid_account: IndividualClient
    ) -> None:
        with allure.step("Выполнение предусловий"):
            client = create_user_with_postpaid_account
            client, product = self.client_request_api.product_sale(
                client.user_id,
                category="internet",
                agreement_id=client.agreements[0].id,
                account_id=client.agreements[0].accounts[0].id,
            )
            amount = product.one_time_payment + product.subscription_fee
            self.personal_account_api.wait_check_current_main_balance(client.agreements[0].accounts[0].id, -amount)
            self.client_profile.open(
                f"{base_url}customer-hierarchy-management/accounts/{client.agreements[0].accounts[0].id}/account"
            )

        self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Биллинговые счета")

        with allure.step("На форме биллинговые счета нажимаем на кнопку 'Запуск биллинга' (+)"):
            billing_date = get_current_moscow_datetime()
            payment_due = get_shifted_datetime(f"+{self.payment_period}d", billing_date)
            billing_task = self.billing_accounts_page.run_unscheduled_billing()

        with allure.step("Нажимаем на кнопку 'Список заданий биллинга'"):
            self.billing_accounts_page.locators.BILLING_TASKS_BTN.click()
            self.billing_accounts_page.locators.BILLING_TASK.wait_to_have_count(1)
            self.billing_accounts_page.check_billing_task(billing_type="Внеочередной биллинг", status="Выполняется")
            self.billing_api.wait_finish_billing(
                self.billing_api.get_billing_profile_id(client.agreements[0].accounts[0].id)
            )

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
            self.billing_accounts_page.check_bill(amount_due=amount, status_color="red")

        with allure.step("Нажимаем на запись о созданном нами счете"):
            self.billing_accounts_page.locators.ACCOUNT_NUMS_LIST.click(0)
            self.billing_accounts_page.check_billing_properties_value(
                payment_due=payment_due,
                end_period=billing_date,
                amount_due=amount,
                output_balance=amount,
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
                available_for_adjustment=product.subscription_fee,
            )
            self.billing_accounts_page.check_detail(
                detail_index=1,
                detail_name="Разовое списание за подключение доступа к сети и в интернет (Интернет домашний безлимитный)",
                charged=product.one_time_payment,
                subscriber=product.internet_number,
                product=product.product_name,
                available_for_adjustment=product.one_time_payment,
            )

        with allure.step("Переходим на вкладку 'Счета-фактуры'"):
            self.billing_accounts_page.locators.INVOICES_TAB.click()
            self.billing_accounts_page.check_invoice(
                invoice_type="Счет-фактура на начисления",
                date=billing_date,
                amount=amount,
                tax=calc_tax(product.one_time_payment) + calc_tax(product.subscription_fee),
                adjusted=0,
                balance=amount,
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

    @allure.title("Проведение внеочередного биллинга, начисления оплачены")
    @allure.description(
        "Запуск внеочередного биллинга. Проверка данных на форме биллинговые счета. \n"
        "Баланс нулевой, начисления на личном счете оплачены."
    )
    @allure.id(575595)
    def test_run_unscheduled_billing_with_charge(self, base_url: str, create_individual_user: IndividualClient) -> None:
        with allure.step("Выполнение предусловий"):
            client, product = self.client_request_api.product_sale(create_individual_user.user_id, category="internet")
            amount = product.one_time_payment + product.subscription_fee
            self.payment_api.create_default_payment(client.agreements[0].accounts[0].id, amount)
            self.personal_account_api.wait_check_current_main_balance(client.agreements[0].accounts[0].id, amount)
            self.personal_account_api.wait_check_current_main_balance(client.agreements[0].accounts[0].id, 0)
            self.client_profile.open(
                f"{base_url}customer-hierarchy-management/accounts/{client.agreements[0].accounts[0].id}/account"
            )

        self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Биллинговые счета")

        with allure.step("На форме биллинговые счета нажимаем на кнопку 'Запуск биллинга' (+)"):
            billing_date = get_current_moscow_datetime()
            payment_due = get_shifted_datetime(f"+{self.payment_period}d", billing_date)
            billing_task = self.billing_accounts_page.run_unscheduled_billing()

        with allure.step("Нажимаем на кнопку 'Список заданий биллинга'"):
            self.billing_accounts_page.locators.BILLING_TASKS_BTN.click()
            self.billing_accounts_page.locators.BILLING_TASK.wait_to_have_count(1)
            self.billing_accounts_page.check_billing_task(billing_type="Внеочередной биллинг", status="Выполняется")
            self.billing_api.wait_finish_billing(
                self.billing_api.get_billing_profile_id(client.agreements[0].accounts[0].id)
            )

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
                payment_due=payment_due,
                end_period=billing_date,
                charges_recorded=amount,
                payments_recorded=amount,
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
                tax=calc_tax(amount),
            )
            self.billing_accounts_page.check_invoice(
                invoice_index=1,
                invoice_type="Счет-фактура на начисления",
                date=billing_date,
                amount=amount,
                tax=calc_tax(product.one_time_payment) + calc_tax(product.subscription_fee),
                adjusted=0,
                balance=amount,
            )

        with allure.step("Переходим на вкладку 'Документы'"):
            self.billing_accounts_page.locators.DOCUMENTS_TAB.click()
            self.billing_accounts_page.locators.NO_DOCUMENT_BLOCK.wait_to_be_visible()

        with allure.step("Переходим на вкладку 'Связанные операции'"):
            self.billing_accounts_page.locators.LINKED_OPERATIONS_TAB.click()
            self.billing_accounts_page.check_linked_operation_tab(amount)

        with allure.step("Нажимаем на пункт 'Погашение'"):
            self.billing_accounts_page.locators.LINKED_OPERATIONS.select_by_value(f"Погашения: {amount:.2f}")
            self.billing_accounts_page.locators.TABLE_ROW_LINKED_OPERATION.wait_to_have_count(1)

        with allure.step("По остальным пунктам отсутствует информация"):
            self.billing_accounts_page.locators.LINKED_OPERATIONS.select_by_value("Списано: 0.00")
            self.billing_accounts_page.locators.NO_RECORDS_LINKED_OPERATION_FOUND.wait_to_be_visible()
            self.billing_accounts_page.locators.LINKED_OPERATIONS.select_by_value("Доначислено: 0.00")
            self.billing_accounts_page.locators.NO_RECORDS_LINKED_OPERATION_FOUND.wait_to_be_visible()

        with allure.step("Переходим на вкладку 'Внереализационные начисления'"):
            self.billing_accounts_page.locators.NON_OPERATING_INCOMES_TAB.click()
            self.billing_accounts_page.locators.NO_RECORDS_NON_OPERATING_INCOMES_FOUND.wait_to_be_visible()

    @allure.title("Проведение внеочередного биллинга, два начисления")
    @allure.description(
        "Создано два разных начисления, по двум продуктам\n"
        "Запуск внеочередного биллинга. Проверка данных на форме биллинговые счета\n"
        "Баланс нулевой, начисления на личном счете оплачены."
    )
    @allure.id(576218)
    def test_run_unscheduled_billing_with_two_charge(
        self, base_url: str, create_individual_user: IndividualClient
    ) -> None:
        with allure.step("Выполнение предусловий"):
            client, product_mobile = self.client_request_api.product_sale(create_individual_user.user_id)
            client, product_internet = self.client_request_api.product_sale(
                client.user_id,
                category="internet",
                agreement_id=client.agreements[0].id,
                account_id=client.agreements[0].accounts[0].id,
            )
            product_mobile.subscription_fee = 300
            amount = (
                product_mobile.one_time_payment
                + product_mobile.subscription_fee
                + product_internet.one_time_payment
                + product_internet.subscription_fee
            )
            payment_date = get_current_moscow_datetime()
            self.payment_api.create_default_payment(client.agreements[0].accounts[0].id, amount)
            self.personal_account_api.wait_check_current_main_balance(client.agreements[0].accounts[0].id, amount)
            self.personal_account_api.wait_check_current_main_balance(client.agreements[0].accounts[0].id, 0)
            self.client_profile.open(
                f"{base_url}customer-hierarchy-management/accounts/{client.agreements[0].accounts[0].id}/account"
            )

        self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Биллинговые счета")

        with allure.step("На форме биллинговые счета нажимаем на кнопку 'Запуск биллинга' (+)"):
            billing_date = get_current_moscow_datetime()
            payment_due = get_shifted_datetime(f"+{self.payment_period}d", billing_date)
            billing_task = self.billing_accounts_page.run_unscheduled_billing()

        with allure.step("Нажимаем на кнопку 'Список заданий биллинга'"):
            self.billing_accounts_page.locators.BILLING_TASKS_BTN.click()
            self.billing_accounts_page.locators.BILLING_TASK.wait_to_have_count(1)
            self.billing_accounts_page.check_billing_task(billing_type="Внеочередной биллинг", status="Выполняется")
            self.billing_api.wait_finish_billing(
                self.billing_api.get_billing_profile_id(client.agreements[0].accounts[0].id)
            )

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
                payment_due=payment_due,
                end_period=billing_date,
                charges_recorded=amount,
                payments_recorded=amount,
                generation_date=billing_date,
            )

        with allure.step("Переходим на вкладку 'Детали'"):
            self.billing_accounts_page.locators.DETAILS_TAB.click()
            self.billing_accounts_page.check_detail(
                detail_index=0,
                detail_name="Абон. плата за мобильный интернет с объемами с цветом номера - обычный",
                charged=product_mobile.subscription_fee,
                subscriber=product_mobile.phone_number,
                product=product_mobile.product_name,
                repaid=product_mobile.subscription_fee,
                available_for_adjustment=product_mobile.subscription_fee,
            )
            self.billing_accounts_page.check_detail(
                detail_index=1,
                detail_name="Абон. плата за предоставление доступа к сети оператора и в интернет (Интернет домашний безлимитный)",
                charged=product_internet.subscription_fee,
                subscriber=product_internet.internet_number,
                product=product_internet.product_name,
                repaid=product_internet.subscription_fee,
                available_for_adjustment=product_internet.subscription_fee,
            )
            self.billing_accounts_page.check_detail(
                detail_index=2,
                detail_name="Разовое списание за подключение доступа к сети и в интернет (Интернет домашний безлимитный)",
                charged=product_internet.one_time_payment,
                subscriber=product_internet.internet_number,
                product=product_internet.product_name,
                repaid=product_internet.one_time_payment,
                available_for_adjustment=product_internet.one_time_payment,
            )

        with allure.step("Переходим на вкладку 'Счета-фактуры'"):
            self.billing_accounts_page.locators.INVOICES_TAB.click()
            self.billing_accounts_page.check_invoice(
                invoice_index=0,
                invoice_type="Авансовый счет-фактура",
                date=payment_date,
                amount=amount,
                tax=calc_tax(amount),
            )
            self.billing_accounts_page.check_invoice(
                invoice_index=1,
                invoice_type="Счет-фактура на начисления",
                date=billing_date,
                amount=amount,
                tax=calc_tax(product_internet.one_time_payment)
                + calc_tax(product_internet.subscription_fee)
                + calc_tax(product_mobile.one_time_payment)
                + calc_tax(product_mobile.subscription_fee),
                adjusted=0,
                balance=amount,
            )

        with allure.step("Переходим на вкладку 'Документы'"):
            self.billing_accounts_page.locators.DOCUMENTS_TAB.click()
            self.billing_accounts_page.locators.NO_DOCUMENT_BLOCK.wait_to_be_visible()

        with allure.step("Переходим на вкладку 'Связанные операции'"):
            self.billing_accounts_page.locators.LINKED_OPERATIONS_TAB.click()
            self.billing_accounts_page.check_linked_operation_tab(amount)

        with allure.step("Нажимаем на пункт 'Погашение'"):
            self.billing_accounts_page.locators.LINKED_OPERATIONS.select_by_value(f"Погашения: {amount:.2f}")
            self.billing_accounts_page.locators.TABLE_ROW_LINKED_OPERATION.wait_to_have_count(1)

        with allure.step("По остальным пунктам отсутствует информация"):
            self.billing_accounts_page.locators.LINKED_OPERATIONS.select_by_value("Списано: 0.00")
            self.billing_accounts_page.locators.NO_RECORDS_LINKED_OPERATION_FOUND.wait_to_be_visible()
            self.billing_accounts_page.locators.LINKED_OPERATIONS.select_by_value("Доначислено: 0.00")
            self.billing_accounts_page.locators.NO_RECORDS_LINKED_OPERATION_FOUND.wait_to_be_visible()

        with allure.step("Переходим на вкладку 'Внереализационные начисления'"):
            self.billing_accounts_page.locators.NON_OPERATING_INCOMES_TAB.click()
            self.billing_accounts_page.locators.NO_RECORDS_NON_OPERATING_INCOMES_FOUND.wait_to_be_visible()

    @allure.title("Проведение внеочередного биллинга, отсутствуют начисления")
    @allure.description(
        "Запуск внеочередного биллинга. Проверка данных на форме биллинговые счета\n"
        "Баланс нулевой, начисления на личном счете не найдены за период биллинга."
    )
    @allure.id(576233)
    def test_run_unscheduled_billing_without_charge(
        self, base_url: str, create_user_with_agreement_and_account: IndividualClient
    ) -> None:
        with allure.step("Выполнение предусловий"):
            client = create_user_with_agreement_and_account
            self.client_profile.open(
                f"{base_url}customer-hierarchy-management/accounts/{client.agreements[0].accounts[0].id}/account"
            )

        self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Биллинговые счета")

        with allure.step("На форме биллинговые счета нажимаем на кнопку 'Запуск биллинга' (+)"):
            billing_date = get_current_moscow_datetime()
            payment_due = get_shifted_datetime(f"+{self.payment_period}d", billing_date)
            billing_task = self.billing_accounts_page.run_unscheduled_billing()

        with allure.step("Нажимаем на кнопку 'Список заданий биллинга'"):
            self.billing_accounts_page.locators.BILLING_TASKS_BTN.click()
            self.billing_accounts_page.locators.BILLING_TASK.wait_to_have_count(1)
            self.billing_accounts_page.check_billing_task(billing_type="Внеочередной биллинг", status="Выполняется")
            self.billing_api.wait_finish_billing(
                self.billing_api.get_billing_profile_id(client.agreements[0].accounts[0].id)
            )

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
                payment_due=payment_due,
                end_period=billing_date,
                generation_date=billing_date,
            )

        with allure.step("Переходим на вкладку 'Детали'"):
            self.billing_accounts_page.locators.DETAILS_TAB.click()
            self.billing_accounts_page.locators.NO_DETAIL_BLOCK.click()

        with allure.step("Переходим на вкладку 'Счета-фактуры'"):
            self.billing_accounts_page.locators.INVOICES_TAB.click()
            self.billing_accounts_page.locators.NO_INVOICE_BLOCK.click()

        with allure.step("Переходим на вкладку 'Документы'"):
            self.billing_accounts_page.locators.DOCUMENTS_TAB.click()
            self.billing_accounts_page.locators.NO_DOCUMENT_BLOCK.wait_to_be_visible()

        with allure.step("Переходим на вкладку 'Связанные операции'"):
            self.billing_accounts_page.locators.LINKED_OPERATIONS_TAB.click()
            self.billing_accounts_page.check_linked_operation_tab()

        with allure.step("Переходим на вкладку 'Внереализационные начисления'"):
            self.billing_accounts_page.locators.NON_OPERATING_INCOMES_TAB.click()
            self.billing_accounts_page.locators.NO_RECORDS_NON_OPERATING_INCOMES_FOUND.wait_to_be_visible()
