from typing import Tuple

import allure
import pytest

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from api.nbss.client_requests.client_requests import MainProduct
from api.nbss.finances.adjustment_requests import AdjustmentRequests
from api.nbss.finances.billing_requests import BillingRequests
from api.nbss.finances.payments_requests import PaymentsRequests
from api.nbss.installment_requests import InstallmentRequests
from api.nbss.personal_account_requests import PersonalAccountRequests
from common.helpers.data_generator import get_current_datetime_string, get_shifted_datetime_string
from common.helpers.time_helpers import delay
from models.context import test_context
from models.inquiry import prepare_inquiries
from models.installment import InstallmentTypeStatusMap
from models.user import BaseClient, EntrepreneurClient, IndividualClient, OrganizationClient
from pages.base_page import BasePage
from pages.locators.base_elements import BaseElements
from pages.locators.nbss.finances.debt_restructuring import DebtRestructuringElements
from pages.nbss.finances.billing_accounts_page import BillingAccountsPage
from pages.nbss.finances.debt_restructuring import DebtRestructuringPage


class DebtRestructuringBase:
    """
    Класс сделан как переходник к логике page,api,test. При написании получались сущности, которые не получилось вынести ни в один из предыдущих.
    Например, использование дефолтных параметров при создании рассрочки. Также использование типов рассрочек для централизованной обработки кейсов.
    Реализован метод client_prepare который по сути precondition и является комбинацией действий из api запросов.
    """

    @pytest.fixture(autouse=True)
    def setup(
        self,
        nexign_stand_login,
        create_individual_user,
        base_url,
    ) -> None:
        self.base_page = BasePage()
        self.client_api = ClientInquiriesRequests()
        self.payment_api = PaymentsRequests()
        self.adjustment_api = AdjustmentRequests()
        self.billing_api = BillingRequests()
        self.personal_account_api = PersonalAccountRequests()
        self.installment_api = InstallmentRequests()
        self.billing_accounts_page = BillingAccountsPage()
        self.base_elements = BaseElements()
        self.debt_restructuring = DebtRestructuringElements()
        self.debt_restructuring_page = DebtRestructuringPage()
        self.user = create_individual_user
        # Дефолтные параметры для тестов
        self.debt = 150
        self.payment = 1000
        self.paid = 0
        self.init_payment = 50
        self.installment_type = "default"
        self.installment_type_status_map = InstallmentTypeStatusMap().map

    @allure.step(
        "Создание клиента, продажа продукта. Проведение платежа, активация продукта. Создание отрицательной корректировки"
    )
    def client_prepare(
        self, category="mobile"
    ) -> Tuple[EntrepreneurClient | IndividualClient | OrganizationClient | None, MainProduct | None]:
        inquiry = self.client_api.product_sale(self.user, prepare_inquiries(category))
        self.payment_api.create_default_payment(test_context.client.get_agreement().accounts[0].id, self.payment)
        payment_data = self.payment_api.get_payments(test_context.client.agreements[0].accounts[0].id).json()["items"][0]

        payment_id = int(payment_data["paymentId"])
        billing_payment_id = int(payment_data["paymentItem"]["paymentItemId"])
        client_balance = self.payment - inquiry.product.total_amount
        self.paid = inquiry.product.total_amount - self.debt
        self.personal_account_api.wait_check_current_main_balance(
            test_context.client.agreements[0].accounts[0].id, client_balance
        )

        self.payment_api.wait_check_add_adjustment_for_payment(payment_id)
        self.adjustment_api.create_adjustment(
            adjustment_type_id=3,
            adjustment_reason_id=3,
            billing_payment_id=billing_payment_id,
            billing_profile_id=self.billing_api.get_billing_profile_id(test_context.client.agreements[0].accounts[0].id),
            amount=self.payment - self.debt,
        )
        self.adjustment_api.wait_adjustment_status(test_context.client.agreements[0].accounts[0].id)
        return test_context.client, inquiry.product

    def set_installment_type(self, installment_type: str) -> None:
        self.installment_type = installment_type
        self.debt_restructuring_page.installment_type = installment_type
        self.installment_api.installment_type = installment_type
        self.debt_restructuring_page.installment_api.installment_type = installment_type

    def billing_conduction(self, client: BaseClient):
        self.billing_accounts_page.billing_conduction(client)

    @allure.step("Создание рассрочки")
    def installment_create(self, withdraw: list[int], payment_number: int = 4, expected_date_number: int = 4):
        with allure.step("Нажатие кнопки добавить и ожидание сайдбара"):
            self.debt_restructuring.ADD_BTN.click()
            self.debt_restructuring.BILL_CHECKBOXES.wait_to_be_visible()
        with allure.step("Заполнение параметров рассрочки"):
            self.debt_restructuring_page.fill_withdraw_table(withdraw)
            delay(1)
            self.debt_restructuring.NEXT_SIDEBAR_BTN.click()
            if self.installment_type == "init_payment":
                self.debt_restructuring.SUM_OF_PAYMENT.fill("0")
                self.debt_restructuring.INIT_PAYMENT_CHECKBOX.wait_to_be_enabled()
                self.debt_restructuring.INIT_PAYMENT_CHECKBOX.click()
                self.debt_restructuring.INIT_PAYMENT_DATE.fill(get_current_datetime_string(is_full_format=False))
                self.debt_restructuring.INIT_PAYMENT.fill(str(self.init_payment))
                self.debt_restructuring.FIRST_PAYMENT_DATE.fill(get_shifted_datetime_string("+1d", is_full_format=False))
            else:
                self.debt_restructuring.FIRST_PAYMENT_DATE.fill(get_current_datetime_string(is_full_format=False))
            self.debt_restructuring.PAYMENT_NUMBER.fill(str(payment_number))
            self.debt_restructuring.CALCULATE_BTN.click()
            self.debt_restructuring.PAYMENTS.wait_to_have_count(expected_date_number)
            if self.installment_type == "delete":
                self.debt_restructuring.PAYMENTS[0].click()
                self.debt_restructuring.PAYMENT_DELETE_BTN.click()
            if self.installment_type not in ["draft", "error"]:
                self.debt_restructuring.REGISTER_BTN.click()
            if self.installment_type == "draft":
                self.debt_restructuring.DRAFT_SAVE_BTN.click()
