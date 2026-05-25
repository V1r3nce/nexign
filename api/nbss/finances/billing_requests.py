from typing import Literal

import allure
import pytest

from api.base_requests import BaseRequests
from api.exceptions import BillingStatusException, GetBillingException, GetLinkedInquiryException
from common.helpers.checker import wait_that
from common.helpers.env_helper import BASE_URL_API
from models.context import test_context


class BillingRequests(BaseRequests):
    @pytest.mark.udb
    @allure.step("API: Получение id биллингового профиля")
    def get_billing_profile_id(self, hierarchy_node_id: int, hierarchy_node_type: str = "ACCOUNT") -> int:
        payload = {"hierarchyNodeId": hierarchy_node_id, "hierarchyNodeType": hierarchy_node_type}
        response = self.post(
            url=f"{BASE_URL_API}/bss-box/v1/finance/billingProfiles/searchByHierarchyNode", json=payload
        )
        self.check_response_status(response, 200, "Не удалось получить id биллингового профиля")
        return response.json()["billingProfileId"]

    @pytest.mark.udb
    @allure.step("API: Запуск внеочередного биллинга")
    def run_unscheduled_billing(self, billing_profile_id: int) -> str:
        payload = {"billingProfileId": billing_profile_id}
        response = self.post(url=f"{BASE_URL_API}/bss-box/v2/billing/billingTasks/unscheduled/run", json=payload)
        self.check_response_status(response, 202, "При запуске внеочередного биллинга возникла ошибка")
        return response.json()["billingTaskId"]

    @pytest.mark.udb
    @allure.step("API: Получение списка запусков биллинга для BillingProfile={billing_profile_id}")
    def get_billing_profile_runs(
        self,
        billing_profile_id: int,
        get_last: bool = None,
        sort_by: str = None,
        start_period_datetime_range_start: str = None,
        start_period_datetime_range_end: str = None,
        end_period_datetime_range_start: str = None,
        end_period_datetime_range_end: str = None,
        billing_task_status_ids: list[int] = None,
        billing_category_ids: list[int] = None,
        billing_task_ids: list[str] = None,
        billing_profile_billing_run_ids: list[str] = None,
        billing_task_type_ids: list[int] = None,
        created_by_users: list[str] = None,
        creation_date_range_start: str = None,
        creation_date_range_end: str = None,
    ) -> list[dict]:
        params = {"sort": sort_by}
        payload: dict = {}
        if start_period_datetime_range_start and start_period_datetime_range_end:
            payload["billingRunPeriodRange"] = {}
            payload["billingRunPeriodRange"]["startPeriodDateTimeRange"] = {
                "startDateTime": start_period_datetime_range_start,
                "endDateTime": start_period_datetime_range_end,
            }
        if end_period_datetime_range_start and end_period_datetime_range_end:
            if "billingRunPeriodRange" not in payload:
                payload["billingRunPeriodRange"] = {}
            payload["billingRunPeriodRange"]["endPeriodDateTimeRange"] = {
                "startDateTime": end_period_datetime_range_start,
                "endDateTime": end_period_datetime_range_end,
            }
        if billing_task_status_ids:
            payload["billingTaskStatusIds"] = billing_task_status_ids
        if billing_category_ids:
            payload["billingCategoryIds"] = billing_category_ids
        if billing_task_ids:
            payload["billingTaskIds"] = billing_task_ids
        if billing_profile_billing_run_ids:
            payload["billingProfileBillingRunIds"] = billing_profile_billing_run_ids
        if billing_task_type_ids:
            payload["billingTaskTypeIds"] = billing_task_type_ids
        if get_last is not None:
            payload["getLast"] = get_last
        if created_by_users:
            payload["createdbyUsers"] = created_by_users
        if creation_date_range_start and creation_date_range_end:
            payload["creationDateRange"] = {
                "startDateTime": creation_date_range_start,
                "endDateTime": creation_date_range_end,
            }

        billing_profile_runs = self.post(
            url=f"{BASE_URL_API}/bss-box/v1/finance/billingProfiles/{billing_profile_id}/billingProfileBillingRuns/search",
            params=params,
            json=payload,
        )
        self.check_response_status(billing_profile_runs, 200, "При получении списка запусков биллинга возникла ошибка")
        return billing_profile_runs.json()["items"]

    @pytest.mark.udb
    @allure.step("Ожидание появление запуска биллинга для {billing_profile_id}")
    def wait_billing(
        self,
        billing_profile_id: int,
        billing_task_count: int = 1,
        end_period_start: str = "2000-01-01T00:00:00.000",
        end_period_end: str = "3000-01-01T00:00:00.000",
    ) -> None:
        wait_that(
            lambda: len(
                self.get_billing_profile_runs(
                    billing_profile_id,
                    end_period_datetime_range_start=end_period_start,
                    end_period_datetime_range_end=end_period_end,
                )
            )
            == billing_task_count,
            exception=GetBillingException,
            timeout=20,
            sleep_seconds=1.5,
            message="Биллинговый счет не появился в указанное время",
        )

    @pytest.mark.udb
    @allure.step("Ожидание статуса последнего запуска биллинга")
    def wait_finish_billing(
        self,
        billing_profile_id: int,
        billing_status_id: int = 3,
        wait_time: int = 60,
        end_period_start: str = "2000-01-01T00:00:00.000",
        end_period_end: str = "3000-01-01T00:00:00.000",
    ) -> None:
        initial_number_of_runs = len(
            self.get_billing_profile_runs(
                billing_profile_id,
                sort_by="-billingTask(creationDate)",
                end_period_datetime_range_start=end_period_start,
                end_period_datetime_range_end=end_period_end,
                billing_task_status_ids=[3],
            )
        )
        wait_that(
            lambda: len(
                self.get_billing_profile_runs(
                    billing_profile_id,
                    end_period_datetime_range_start=end_period_start,
                    end_period_datetime_range_end=end_period_end,
                )
            )
            > initial_number_of_runs,
            timeout=wait_time,
            sleep_seconds=1.5,
            exception=BillingStatusException,
            message=f"Биллинг не появился за {wait_time} секунд",
        )
        wait_that(
            lambda: self.get_billing_profile_runs(
                billing_profile_id,
                sort_by="-billingTask(creationDate)",
                end_period_datetime_range_start=end_period_start,
                end_period_datetime_range_end=end_period_end,
            )[0]["billingTask"]["status"]["billingTaskStatusId"]
            == billing_status_id,
            timeout=wait_time,
            sleep_seconds=1.5,
            exception=BillingStatusException,
            message=f"Биллинг не завершился за {wait_time} секунд",
        )

    @pytest.mark.udb
    @allure.step("API: Получение списка биллинговых счетов")
    def get_list_of_bills(self, billing_profile_ids: list[int]) -> list[dict]:
        payload = {"billingProfileIds": billing_profile_ids, "isNotPreliminary": True}
        bills = self.post(url=f"{BASE_URL_API}/bss-box/v2/finance/bills/search", json=payload)
        self.check_response_status(bills, 200, "При получении списка биллинговых счетов возникла ошибка")
        return bills.json()["items"]

    @allure.step("API: Получение списка id биллинговых счетов")
    def get_list_of_billing_ids(self, billing_profile_ids: list[int]) -> list[str]:
        items = self.get_list_of_bills(billing_profile_ids)
        return [item.get("billId") for item in items]

    @pytest.mark.udb
    @allure.step("Ожидание появления связанных заявок у биллингового счета")
    def wait_link_bill_and_inquiry(self, billing_profile_id: int) -> None:
        wait_that(
            lambda: len(self.get_list_of_bills([billing_profile_id])[0]["disputeInfo"]["inquiryIds"]) > 0,
            timeout=40,
            sleep_seconds=0.5,
            exception=GetLinkedInquiryException,
            message="У биллингового счета не появились связанные заявки за указанное время",
        )

    @pytest.mark.udb
    @allure.step("API: Получение список значений деталей биллингового счета")
    def get_bill_details(self, bill_id: str) -> list[dict]:
        params = {"limit": 10, "sort": "billDetail(name)", "offset": 0}
        payload = {"isDisplay": True, "isInformational": False}
        details = self.post(
            url=f"{BASE_URL_API}/bss-box/v2/finance/bills/{bill_id}/billDetailValues/search", params=params, json=payload
        )
        self.check_response_status(details, 200, "При получении списка деталей биллингового счета возникла ошибка")
        return details.json()["items"]

    @pytest.mark.udb
    @allure.step("API: Ожидание появления значения в указанном поле биллингового счета")
    def wait_bill_info_value(self, bill_id: str, field_name: str, value: str | int) -> None:
        self.check_response_content(
            f"$..{field_name}",
            "has",
            value,
            request=lambda: self.get(f"{BASE_URL_API}/bss-box/v2/finance/bills/{bill_id}"),
            timeout=10,
        )

    @pytest.mark.udb
    @allure.step("Получение идентификатора значения биллинговой детали")
    def get_bill_detail_value_id(
        self,
        bill_id: str,
        detail_name: str = "Абон. плата за предоставление доступа к сети оператора и в интернет",
    ) -> int | None:
        """
            Метод получает идентификатор биллинговой детали по её названию

        :param bill_id: идентификатор биллингового счета
        :param detail_name: название биллинговой детали для поиска (по умолчанию: абонентская плата)
        :return: идентификатор значения найденной детали или None, если не найден
        :raises AssertionError: если деталь с указанным названием не найдена
        """
        bill_details_data = self.get_bill_details(bill_id)
        for detail in bill_details_data:
            if detail["billDetail"]["name"] == detail_name:
                return int(detail["billDetailValueId"])
        raise AssertionError(f"Отсутствует деталь с name = {detail_name}")

    @pytest.mark.udb
    @allure.step("Получение названия биллинговой детали")
    def get_bill_detail_name(self, bill_id: str, bill_detail_value_id: int) -> str:
        """
        Метод получает название биллинговой детали по идентификатору

        :param bill_id: идентификатор счета
        :param bill_detail_value_id: идентификатор детали в счете
        :return: название найденной детали
        :raises AssertionError: если деталь с указанным bill_detail_value_id не найдена
        """
        bill_details_data = self.get_bill_details(bill_id)
        for item in bill_details_data:
            if item.get("billDetailValueId") == bill_detail_value_id:
                if "billDetail" in item and "name" in item["billDetail"]:
                    return str(item["billDetail"]["name"])

        raise AssertionError(f"Отсутствует деталь с bill_detail_value_id = {bill_detail_value_id} в счёте {bill_id}")

    @pytest.mark.udb
    @allure.step("Ожидание появления связанных заявок у детали биллингового счета")
    def wait_link_bill_detail_and_inquiry(self, bill_id: str) -> None:
        wait_that(
            lambda: len(self.get_bill_details(bill_id)[0]["disputeInfo"]["inquiryIds"]) > 0,
            timeout=40,
            sleep_seconds=0.5,
            exception=GetLinkedInquiryException,
            message="У детали  биллингового счета не появились связанные заявки за указанное время",
        )

    @pytest.mark.udb
    @allure.step("API: Получение списка значений счетов-фактур биллингового счета")
    def get_bill_tax_invoices(self, billing_run_id: str) -> list[dict]:
        headers = {"accept-language": "ru"}
        payload = {
            "taxInvoiceDateRange": {
                "endDateTime": "3000-01-01T00:00:00.000Z",
                "startDateTime": "2000-01-01T00:00:00.000Z",
            },
            "billingProfileBillingRunId": billing_run_id,
        }
        tax_invoices = self.post(
            url=f"{BASE_URL_API}/bss-box/v1/finance/taxInvoices/search", json=payload, headers=headers
        )
        self.check_response_status(
            tax_invoices, 200, "При получении списка счетов-фактур биллингового счета возникла ошибка"
        )
        return tax_invoices.json()["items"]

    def get_tax_invoice_id(self, billing_run_id: str, tax_invoice_type: str) -> str | None:
        for tax_invoice in self.get_bill_tax_invoices(billing_run_id):
            if tax_invoice["details"]["taxInvoiceType"]["name"] == tax_invoice_type:
                return tax_invoice["taxInvoiceId"]
        return None

    @allure.step("Получение номера счета-фактуры")
    def get_tax_invoice_number(self, billing_run_id: str, tax_invoice_type: str) -> str | None:
        """
        Метод получает номер счета-фактуры по ожидаемому типу

        :param billing_run_id: идентификатор биллинг-рана
        :param tax_invoice_type: тип счета-фактуры для поиска
        :return: номер найденного счета-фактуры или None, если не найден
        :raises AssertionError: если счет-фактура с указанным типом не найден
        """
        invoice_data = self.get_bill_tax_invoices(billing_run_id)
        for tax_invoice in invoice_data:
            if tax_invoice["details"]["taxInvoiceType"]["name"] == tax_invoice_type:
                tax_invoice_number = tax_invoice["details"]["ownInfo"]["taxInvoiceNumber"]
                return tax_invoice_number
        raise AssertionError(f"Отсутствует счет-фактура с типом = {tax_invoice_type}")

    @pytest.mark.udb
    @allure.step("API: Расчет налогов по биллинговому профилю для объекта биллинга")
    def calculate_taxes(
        self,
        billing_profile_id: int,
        object_type: Literal["PAYMENT", "BILL_DETAIL_VALUE", "ADJUSTMENT"],
        amount: float,
        action_date: str = None,
        bill_detail_id: int = None,
        adjustment_type_id: int = None,
        billing_payment_id: int = None,
        bill_id: str = None,
        bill_detail_value_id: int = None,
        tax_invoice_id: int = None,
    ) -> dict:
        payload = {
            "amount": amount,
            "objectType": object_type,
            "taxCalculationMethod": "EXTRACT_FROM_BASE",
        }
        if action_date:
            payload["actionDate"] = action_date
        match payload["objectType"]:
            case "BILL_DETAIL_VALUE":
                payload["billDetailId"] = bill_detail_id
            case "ADJUSTMENT":
                payload["adjustmentTypeId"] = adjustment_type_id
                if billing_payment_id:
                    payload["billingPaymentId"] = billing_payment_id
                if bill_id:
                    payload["billId"] = bill_id
                if bill_detail_value_id:
                    payload["billDetailValueId"] = bill_detail_value_id
                if tax_invoice_id:
                    payload["taxInvoiceId"] = tax_invoice_id
                if bill_detail_id:
                    payload["billDetailId"] = bill_detail_id

        tax = self.post(
            url=f"{BASE_URL_API}/bss-box/v2/finance/billingProfiles/{billing_profile_id}/calculateTaxes", json=payload
        )
        self.check_response_status(tax, 200, "При расчете налога по биллинговому профилю возникла ошибка")
        return tax.json()

    @pytest.mark.udb
    @allure.step(
        "API: Запуск внеочередного биллинга для billing_profile_id={billing_profile_id} и ожидание его завершения"
    )
    def execute_unscheduled_billing_and_wait_completion(self, billing_profile_id: int | None = None) -> None:
        """
        Выполняет полный сценарий внеочередного биллинга:

        1. Запускает внеочередной биллинговый процесс.
        2. Ожидает появления биллингового запуска для профиля.
        3. Ожидает завершения последнего биллингового задания
           с успешным статусом.

        :param billing_profile_id: ID биллингового профиля

        :raises GetBillingException: если биллинговый запуск не появился
        :raises BillingStatusException: если биллинг не завершился за допустимое время
        """
        if billing_profile_id is None:
            billing_profile_id = self.get_billing_profile_id(test_context.client.agreements[0].accounts[0].id)
        self.run_unscheduled_billing(billing_profile_id=billing_profile_id)
        self.wait_billing(billing_profile_id=billing_profile_id)
        self.wait_finish_billing(billing_profile_id=billing_profile_id)

    @allure.step("API: Ожидание появления документа с именем {document_name} биллинга ЛС")
    def wait_document_with_name(self, billing_id: str, document_name: str, account_id: str | None = None) -> None:
        wait_that(
            lambda: any(
                [
                    document_name in item.get("fileName")
                    for item in self.get_documents(billing_id=billing_id, account_id=account_id).get("items")
                ]
            ),
            timeout=15,
            sleep_seconds=3,
            exception=AssertionError,
            message=f"Документ с названием {document_name} не появился в списке за 15 секунд",
        )

    @allure.step("API: Получение документов биллинга ЛС")
    def get_documents(self, billing_id: str, account_id: str | None = None) -> dict:
        payload = {
            "recipients": [
                {
                    "recipientId": test_context.client.agreements[0].accounts[0].id
                    if account_id is None
                    else account_id,
                    "recipientType": "account",
                    "tags": [{"name": "billId", "value": billing_id}],
                }
            ],
            "resultMode": 0,
        }
        response = self.post(f"{BASE_URL_API}/openapi/v1/reports/digital/files/search", json=payload)
        self.check_response_status(response, 200, "Не получен список документов")
        return response.json()

    @allure.step("API: Ожидание появления документа в  списке и успешного выполнения")
    def wait_document_done(self, document_name: str = "nbss_invoice_bill.pdf") -> None:
        document_timeout = 15
        bill_id = self.get_list_of_billing_ids(
            [self.get_billing_profile_id(test_context.client.agreements[0].accounts[0].id)]
        )[0]
        self.wait_document_with_name(bill_id, document_name)
        wait_that(
            lambda: any(
                [
                    document_name in item.get("fileName") and item.get("documentStatus").get("code") == "COMPLETED"
                    for item in self.get_documents(billing_id=bill_id).get("items")
                ]
            ),
            timeout=document_timeout,
            sleep_seconds=3,
            exception=AssertionError,
            message=f"Документ с названием {document_name} не выполнился успешно за {document_timeout} секунд",
        )
