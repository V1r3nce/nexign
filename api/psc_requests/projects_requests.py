import allure
from playwright.sync_api import APIResponse

from api.base_requests import BaseRequests
from api.exceptions import ProjectNotFoundException, PSCProjectPublicationFailed, SpecificationNotFoundException
from common.helpers.checker import check_that, wait_that
from common.helpers.env_helper import BASE_URL_PSC


class ProjectRequests(BaseRequests):
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

    @allure.step("API: Получение проекта по параметрам")
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

    @allure.step("API: Получение проекта по идентификатору")
    def get_project_by_id(self, project_id: int) -> dict:
        response = self.get(f"{BASE_URL_PSC}/ProductCatalog/api/v2/secured/projects/{project_id}")
        self.check_response_status(response, 200, "Не удалось получить проект по идентификатору")
        return response.json()

    @allure.step("API: Получение статуса проекта по идентификатору")
    def get_project_lifecycle_status_by_id(self, project_id: int) -> str:
        project = self.get_project_by_id(project_id)
        return project["lifecycleStatus"]

    @allure.step("API: Отправка заявки на публикацию проекта")
    def publish_project_by_id(self, project_id: int, params: dict) -> None:
        response = self.post(
            f"{BASE_URL_PSC}/ProductCatalog/api/v2/secured/projects/{project_id}/publications", params=params
        )
        self.check_response_status(response, [200, 202], "Не удалось создать заявку на публикацию")

    @allure.step("API: Создание заявки на проектную публикацию")
    def publish_test_project_by_id(self, project_id: int) -> None:
        params = {"skippedPublication": True, "projectPublication": True, "target": "TEST"}
        self.publish_project_by_id(project_id, params)

    @allure.step("API: Создание заявки на публикацию в прод")
    def publish_prod_project_by_id(self, project_id: int) -> None:
        params = {"target": "PROD"}
        self.publish_project_by_id(project_id, params)

    @allure.step("API: Возврат проекта в разработку")
    def back_project_to_dev(self, project_id: int) -> None:
        params = {"target": "DEV"}
        self.publish_project_by_id(project_id, params)

    @allure.step("API: Проверка существования проекта с {project_id}")
    def check_project_existing(self, project_id: int) -> None:
        check_timeout = 20
        wait_that(
            lambda: self.get_project_lifecycle_status_by_id(project_id) == "EDITING",
            timeout=check_timeout,
            sleep_seconds=5,
            exception=PSCProjectPublicationFailed,
            message=f"Проектная публикация не завершилась за {check_timeout}",
        )

    @allure.step("API: Публикация проекта и ожидание завершения")
    def publish_project_and_wait_success(self, project_id: int) -> None:
        self.check_project_existing(project_id)
        publish_timeout = 90
        self.publish_test_project_by_id(project_id)
        wait_that(
            lambda: self.get_project_lifecycle_status_by_id(project_id) == "TEST_SUCCESS",
            timeout=publish_timeout,
            sleep_seconds=5,
            exception=PSCProjectPublicationFailed,
            message=f"Проектная публикация не завершилась за {publish_timeout}",
        )
        self.publish_prod_project_by_id(project_id)
        wait_that(
            lambda: self.get_project_lifecycle_status_by_id(project_id) == "PROM_SUCCESS",
            timeout=publish_timeout,
            sleep_seconds=5,
            exception=PSCProjectPublicationFailed,
            message=f"Проект не был опубликован за {publish_timeout}",
        )

    @allure.step("API: Возврат проекта в разработку и ожидание завершения")
    def back_project_and_wait_success(self, project_id: int) -> None:
        publish_timeout = 30
        self.back_project_to_dev(project_id)
        wait_that(
            lambda: self.get_project_lifecycle_status_by_id(project_id) == "EDITING",
            timeout=publish_timeout,
            sleep_seconds=5,
            exception=PSCProjectPublicationFailed,
            message=f"Возврат в разработку не был совершен за {publish_timeout}",
        )
