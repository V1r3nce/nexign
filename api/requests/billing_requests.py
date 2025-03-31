import allure
from playwright.sync_api import APIRequestContext

from api.exceptions import BillingStatusException, GetBillingException, GetLinkedInquiryException
from api.requests.base_requests import BaseRequests
from common.helpers.checker import wait_that
from common.helpers.env_helper import BASE_URL_API


class BillingRequests(BaseRequests):
    def __init__(self, api_request_auth_context: APIRequestContext):
        super().__init__(api_request_auth_context)

    @allure.step("API: Получение id биллингового профиля")
    def get_billing_profile_id(self, hierarchy_node_id: int, hierarchy_node_type: str = "ACCOUNT") -> int:
        payload = {"hierarchyNodeId": hierarchy_node_id, "hierarchyNodeType": hierarchy_node_type}
        response = self.post(
            url=f"{BASE_URL_API}/bss-box/v1/finance/billingProfiles/searchByHierarchyNode", data=payload
        )
        self.check_response_status(response, 200, "Не удалось получить id биллингового профиля")
        return response.json()["billingProfileId"]

    @allure.step("API: Запуск внеочередного биллинга")
    def run_unscheduled_billing(self, billing_profile_id: int) -> str:
        payload = {"billingProfileId": billing_profile_id}
        response = self.post(url=f"{BASE_URL_API}/bss-box/v2/billing/billingTasks/unscheduled/run", data=payload)
        self.check_response_status(response, 202, "При запуске внеочередного биллинга возникла ошибка")
        return response.json()["billingTaskId"]

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
            data=payload,
        )
        self.check_response_status(billing_profile_runs, 200, "При получении списка запусков биллинга возникла ошибка")
        return billing_profile_runs.json()["items"]

    @allure.step("Ожидание появление запуска биллинга для {billing_profile_id}")
    def wait_billing(
        self,
        billing_profile_id: int,
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
            > 0,
            exception=GetBillingException,
            timeout=10,
            sleep_seconds=0.5,
            message="Биллинговый счет не появился в указанное время",
        )

    @allure.step("Ожидание статуса последнего запуска биллинга")
    def wait_finish_billing(
        self,
        billing_profile_id: int,
        billing_status_id: int = 3,
        end_period_start: str = "2000-01-01T00:00:00.000",
        end_period_end: str = "3000-01-01T00:00:00.000",
    ) -> None:
        wait_that(
            lambda: self.get_billing_profile_runs(
                billing_profile_id,
                sort_by="-billingTask(creationDate)",
                end_period_datetime_range_start=end_period_start,
                end_period_datetime_range_end=end_period_end,
            )[0]["billingTask"]["status"]["billingTaskStatusId"]
            == billing_status_id,
            timeout=60,
            sleep_seconds=0.5,
            exception=BillingStatusException,
            message="Биллинг не завершился в указанное время",
        )

    @allure.step("API: Получение списка биллинговых счетов")
    def get_list_of_bills(self, billing_profile_ids: list[int]) -> list[dict]:
        payload = {"billingProfileIds": billing_profile_ids, "isNotPreliminary": True}
        bills = self.post(url=f"{BASE_URL_API}/bss-box/v2/finance/bills/search", data=payload)
        self.check_response_status(bills, 200, "При получении списка биллинговых счетов возникла ошибка")
        return bills.json()["items"]

    @allure.step("Ожидание появления связанных заявок у биллингового счета")
    def wait_link_bill_and_inquiry(self, billing_profile_id: int) -> None:
        wait_that(
            lambda: len(self.get_list_of_bills([billing_profile_id])[0]["disputeInfo"]["inquiryIds"]) > 0,
            timeout=40,
            sleep_seconds=0.5,
            exception=GetLinkedInquiryException,
            message="У биллингового счета не появились связанные заявки за указанное время",
        )

    @allure.step("API: Получение список значений деталей биллингового счета")
    def get_bill_details(self, bill_id: int) -> list[dict]:
        params = {"sort": "billDetail(name)"}
        payload = {"isDisplay": True, "isInformational": False}
        details = self.post(
            url=f"{BASE_URL_API}/bss-box/v2/finance/bills/{bill_id}/billDetailValues/search", params=params, data=payload
        )
        self.check_response_status(details, 200, "При получении списка деталей биллингового счета возникла ошибка")
        return details.json()["items"]

    @allure.step("Ожидание появления связанных заявок у детали биллингового счета")
    def wait_link_bill_detail_and_inquiry(self, bill_id: int) -> None:
        wait_that(
            lambda: len(self.get_bill_details(bill_id)[0]["disputeInfo"]["inquiryIds"]) > 0,
            timeout=40,
            sleep_seconds=0.5,
            exception=GetLinkedInquiryException,
            message="У детали  биллингового счета не появились связанные заявки за указанное время",
        )
