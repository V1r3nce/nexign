import allure
from playwright.sync_api import APIRequestContext

from api.requests.base_requests import BaseRequests
from common.helpers.env_helper import BASE_URL_API


class BillingRequests(BaseRequests):
    def __init__(self, api_request_auth_context: APIRequestContext):
        super().__init__(api_request_auth_context)

    @allure.step("API: Получение id биллингового профиля")
    def get_billing_profile_id(self, hierarchy_node_id: int, hierarchy_node_type: str = "ACCOUNT") -> int:
        payload = {"hierarchyNodeId": hierarchy_node_id, "hierarchyNodeType": hierarchy_node_type}
        response = self.post(url=f"{BASE_URL_API}/bss-box/v1/finance/billingProfiles/searchByHierarchyNode",
                             data=payload)
        self.check_response_status(response, 200, "Не удалось получить id биллингового профиля")
        return response.json()["billingProfileId"]

    @allure.step("API: Запуск внеочередного биллинга")
    def run_unscheduled_billing(self, billing_profile_id: int) -> str:
        payload = {"billingProfileId": billing_profile_id}
        response = self.post(url=f"{BASE_URL_API}/bss-box/v2/billing/billingTasks/unscheduled/run", data=payload)
        self.check_response_status(response, 202,
                                   "При запуске внеочередного биллинга возникла ошибка")
        return response.json()["billingTaskId"]

    @allure.step("API: Получение списка запусков биллинга для BillingProfile={billing_profile_id}")
    def get_billing_profile_runs(self, billing_profile_id: int, get_last: bool = None,
                                 start_period_datetime_range_start: str = None,
                                 start_period_datetime_range_end: str = None,
                                 end_period_datetime_range_start: str = None,
                                 end_period_datetime_range_end: str = None,
                                 billing_task_status_ids: list[int] = None, billing_category_ids: list[int] = None,
                                 billing_task_ids: list[str] = None, billing_profile_billing_run_ids: list[str] = None,
                                 billing_task_type_ids: list[int] = None, created_by_users: list[str] = None,
                                 creation_date_range_start: str = None,
                                 creation_date_range_end: str = None) -> list[dict]:
        payload = {}
        if start_period_datetime_range_start and start_period_datetime_range_end:
            payload["billingRunPeriodRange"] = {}
            payload["billingRunPeriodRange"]["startPeriodDateTimeRange"] = {
                "startDateTime": start_period_datetime_range_start,
                "endDateTime": start_period_datetime_range_end
            }
        if end_period_datetime_range_start and end_period_datetime_range_end:
            if "billingRunPeriodRange" not in payload:
                payload["billingRunPeriodRange"] = {}
            payload["billingRunPeriodRange"]["endPeriodDateTimeRange"] = {
                "startDateTime": end_period_datetime_range_start,
                "endDateTime": end_period_datetime_range_end
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
                "endDateTime": creation_date_range_end
            }

        billing_profile_runs = self.post(
            url=f"{BASE_URL_API}/bss-box/v1/finance/billingProfiles/{billing_profile_id}/billingProfileBillingRuns/search",
            data=payload)
        self.check_response_status(billing_profile_runs, 200,
                                   "При получении списка запусков биллинга возникла ошибка")
        return billing_profile_runs.json()["items"]
