import allure
from playwright.sync_api import APIRequestContext

from api.exceptions import AdjustmentStatusException, CreateAdjustmentException
from api.requests.base_requests import BaseRequests
from api.requests.billing_requests import BillingRequests
from common.helpers.checker import wait_that
from common.helpers.env_helper import BASE_URL_API
from common.helpers.time_helpers import get_iso_now_time_moscow


class AdjustmentRequests(BaseRequests):
    def __init__(self, api_request_auth_context: APIRequestContext):
        super().__init__(api_request_auth_context)
        self.billing_api = BillingRequests(api_request_auth_context)

    @allure.step("API: Получение списка корректировок")
    def get_adjustment_list(self, account_id: int) -> dict:
        billing_profile_id = self.billing_api.get_billing_profile_id(account_id)
        params = {"limit": 30, "sort": "-adjustmentDate", "offset": 0}
        payload = {"billingProfileId": billing_profile_id}
        adjustments = self.post(url=f"{BASE_URL_API}/bss-box/v1/finance/adjustments/search", params=params, data=payload)
        self.check_response_status(adjustments, 200, "Не удалось получить список корректировок")
        return adjustments.json()

    @allure.step("Ожидание статуса последней корректировки")
    def wait_adjustment_status(self, account_id: int, adjustment_status_id: int = 2) -> None:
        wait_that(
            lambda: self.get_adjustment_list(account_id)["items"][0]["statusInfo"]["status"]["adjustmentStatusId"]
            == adjustment_status_id,
            timeout=20,
            sleep_seconds=0.5,
            exception=AdjustmentStatusException,
            message="Корректировка не перешла в указанный статус за указанное время",
        )

    @allure.step("Ожидание статуса всех корректировок клиента")
    def wait_all_adjustments_status(self, account_id: int, adjustment_count: int, adjustment_status_id: int = 2) -> None:
        expected_adjustment_statuses = [adjustment_status_id] * adjustment_count

        wait_that(
            lambda: [
                item["statusInfo"]["status"]["adjustmentStatusId"]
                for item in list(self.get_adjustment_list(account_id)["items"])
            ]
            == expected_adjustment_statuses,
            timeout=20,
            sleep_seconds=0.5,
            exception=AdjustmentStatusException,
            message="Не все корректировки перешли в указанный статус за указанное время",
        )

    @allure.step("API: Проверка возможности создать новую корректировку")
    def check_create_adjustment(self, payload: dict) -> list:
        adjustment = self.post(url=f"{BASE_URL_API}/bss-box/v2/finance/adjustments/add/check", data=payload)
        self.check_response_status(adjustment, 200, "При проверке возможности создать корректировку возникла ошибка")
        return adjustment.json()["conflicts"]

    @allure.step("API: Создание корректировки")
    def create_adjustment(
        self,
        adjustment_type_id: int,
        adjustment_reason_id: int,
        amount: int,
        adjustment_date: str = get_iso_now_time_moscow(),
        billing_profile_id: int = None,
        billing_payment_id: int = None,
        bill_id: str = None,
        bill_detail_value_id: int = None,
        tax_invoice_id: str = None,
    ) -> int:
        payload = {
            "adjustmentDate": adjustment_date,
            "adjustmentReason": {"adjustmentReasonId": adjustment_reason_id},
            "adjustmentTarget": {"adjustmentType": {"adjustmentTypeId": adjustment_type_id}},
            "billingProfile": {"billingProfileId": billing_profile_id},
            "sumInfo": {
                "amountWithTax": amount,
                "taxCalculationMethod": "EXTRACT_FROM_BASE",
            },
        }

        if billing_payment_id:
            payload["adjustmentTarget"]["billingPayment"] = {"billingPaymentId": billing_payment_id}
        if bill_id:
            payload["adjustmentTarget"]["bill"] = {"billId": bill_id}
        if bill_detail_value_id:
            payload["adjustmentTarget"]["billDetailValue"] = {"billDetailValueId": bill_detail_value_id}
        if tax_invoice_id:
            payload["adjustmentTarget"]["taxInvoice"] = {"taxInvoiceId": tax_invoice_id}

        wait_that(
            lambda: len(self.check_create_adjustment(payload)) == 0,
            timeout=20,
            sleep_seconds=0.5,
            exception=CreateAdjustmentException,
            message="При создании корректировки возникнет ошибка",
        )

        calculate_taxes = self.billing_api.calculate_taxes(
            object_type="ADJUSTMENT",
            amount=amount,
            adjustment_type_id=adjustment_type_id,
            billing_profile_id=billing_profile_id,
            billing_payment_id=billing_payment_id,
            bill_id=bill_id,
            bill_detail_value_id=bill_detail_value_id,
            tax_invoice_id=tax_invoice_id,
        )
        payload["sumInfo"]["amountWithoutTax"] = calculate_taxes["amountWithoutTax"]
        payload["sumInfo"]["tax"] = calculate_taxes["taxAmount"]
        payload["sumInfo"]["taxIsManuallyCorrected"] = False

        adjustment = self.post(url=f"{BASE_URL_API}/bss-box/v2/finance/adjustments", data=payload)
        self.check_response_status(adjustment, 200, "При создании корректировки возникла ошибка")
        return adjustment.json()["adjustmentId"]
