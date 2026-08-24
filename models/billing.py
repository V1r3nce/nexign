from typing import Any

from common.helpers.checker import assert_that
from models.base_models import CamelModel


class AdjustmentAmount(CamelModel):
    """Денежная сумма с разбивкой на сумму с налогом, без налога и сам налог."""

    amount_with_tax: float
    amount_without_tax: float
    tax: float


class AdjustmentsSumInfo(CamelModel):
    corrected: AdjustmentAmount
    available_for_correction: AdjustmentAmount


class ResultSumInfo(CamelModel):
    charged_total_amount_with_tax: float
    charged_total_amount_without_tax: float
    charged_total_tax: float
    charges_amount_with_tax: float
    charges_amount_without_tax: float
    charges_tax: float
    in_balance_with_tax: float
    payments_amount_with_tax: float
    payment_adjustments_amount_with_tax: float
    out_balance_with_tax: float
    charge_adjustments_amount_with_tax: float


class DisputeInfo(CamelModel):
    inquiry_ids: list[Any]
    is_disputed: bool


class BillType(CamelModel):
    name: str
    bill_type_id: int


class BillingProfile(CamelModel):
    billing_profile_id: int
    customer_id: int
    currency_code: str


class ResultDebitInfo(CamelModel):
    due_date: str
    debit_with_tax: float


class BillingTaskStatus(CamelModel):
    billing_task_status_id: int
    name: str


class BillingCategory(CamelModel):
    billing_category_id: int
    name: str


class Period(CamelModel):
    start_date_time: str
    end_date_time: str | None

    def get_end_date_time(self) -> str:
        end_date = self.end_date_time
        assert_that(lambda: end_date is not None, "Поле end_date_time у биллинга пустое")
        return end_date[:19]


class BillingTask(CamelModel):
    status: BillingTaskStatus
    run_date: str
    work_period: Period
    is_fixed: bool
    billing_category: BillingCategory
    customer_order_id: str | None = None
    billing_task_id: str


class BillingRun(CamelModel):
    billing_profile_billing_run_id: str
    bills_count: int
    billing_task: BillingTask
    period: Period


class ResultCreditInfo(CamelModel):
    advance_amount_with_tax: float


class BillStatus(CamelModel):
    name: str
    bill_status_id: int


class StatusInfo(CamelModel):
    creation_user: str
    status: BillStatus
    cancellation_date: str | None = None
    cancellation_user: str | None = None
    creation_date: str


class DebitStatus(CamelModel):
    debit_status_name: str
    debit_status_id: int


class CurrentDebitInfo(CamelModel):
    is_overdue: bool
    days_overdue: int
    paid_date: str | None
    debit_with_tax: float
    debit_status: DebitStatus
    is_installment: bool
    paid_amount_with_tax: float


class PreviousBill(CamelModel):
    """Ссылка на предыдущий счет — сокращённая версия объекта счета."""

    bill_id: str
    bill_type: BillType
    bill_number: str
    billing_run: BillingRun


class Bill(CamelModel):
    """Биллинговый счет."""

    discounts: list[Any] | None = None
    accounting_balances: list[Any] = []
    result_sum_info: ResultSumInfo
    issue_date: str
    commercial_order_id: str | None = None
    adjustment_reason_group_sum_info: list[Any] = []
    allow_unpaid_shipment: bool | None = None
    dispute_info: DisputeInfo
    adjustments_sum_info: AdjustmentsSumInfo
    bill_type: BillType
    billing_profile: BillingProfile
    result_debit_info: ResultDebitInfo
    billing_run: BillingRun
    billing_profile_status: str
    previous_bill: PreviousBill | None = None
    installment_order_product_id: int | None = None
    fpm_product_id: int | None = None
    result_credit_info: ResultCreditInfo
    is_preliminary_with_shipment: bool | None = None
    is_preliminary_with_installment: bool | None = None
    status_info: StatusInfo
    bill_number: str
    bill_id: str
    current_debit_info: CurrentDebitInfo
