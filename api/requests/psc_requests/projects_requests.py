import allure
from playwright.sync_api import APIRequestContext, APIResponse

from api.requests.base_requests import BaseRequests
from common.helpers.env_helper import BASE_URL_PSC


class ProjectRequests(BaseRequests):
    def __init__(self, api_request_auth_context: APIRequestContext):
        super().__init__(api_request_auth_context)

    @allure.step("API: Получить список проектов")
    def get_projects(self) -> APIResponse:
        """
        Получить список проектов
        """
        payload = {"page": 0, "size": 30, "sortBy": "id", "sortDirection": "desc"}
        projects = self.post(url=f"{BASE_URL_PSC}/ProductCatalog/api/v2/secured/projects/search", data=payload)
        self.check_response_status(projects, 200, "Не получен список проектов")
        return projects

    @allure.step("API: Получить список спецификаций")
    def get_ps_specifications(self) -> APIResponse:
        """
        Получить список спецификаций
        """
        payload = {"page": 0, "size": 30, "sortBy": "id", "sortDirection": "desc"}
        specifications = self.post(
            url=f"{BASE_URL_PSC}/ProductCatalog/api/v2/secured/specifications/productSpecifications/search", data=payload
        )
        self.check_response_status(specifications, 200, "Не получен список спецификаций")
        return specifications
