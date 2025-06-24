import allure
from playwright.sync_api import APIRequestContext, APIResponse

from api.exceptions import ProjectNotFoundException, SpecificationNotFoundException
from api.requests.base_requests import BaseRequests
from common.helpers.checker import check_that
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

    @allure.step("API: Получить спецификацию по названию {name}")
    def get_ps_specification_by_name(self, name: str) -> dict | None:
        """
        Получить спецификацию по названию
        :param name: название спецификации
        :return: спецификация
        """
        specifications = self.get_ps_specifications().json()["content"]
        found_spec = None
        for spec in specifications:
            if name in spec["name"]:
                found_spec = spec
                break
        check_that(lambda: found_spec is not None, SpecificationNotFoundException, f"Спецификация {name} не найдена")
        return found_spec

    def get_project_id_by_params(self, params: dict) -> dict | None:
        """
        Получить проект по параметрам
        :param params: словарь параметров поиска проекта. Например: {"productOfferingsNumber": 1, "lifecycleStatus": "EDITING"}
        :return: проект
        """
        projects = self.get_projects().json()["content"]
        found_project = None
        for project in projects:
            if all(project.get(key) == value for key, value in params.items()):
                found_project = project
                break
        check_that(
            lambda: found_project is not None, ProjectNotFoundException, f"Проект с параметрами {params} не найден"
        )
        return found_project
