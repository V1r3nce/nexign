import allure

from api.base_requests import BaseRequests
from common.helpers.checker import wait_that
from common.helpers.env_helper import BASE_URL_LIS


class DirectoryRequests(BaseRequests):
    def __init__(self) -> None:
        super().__init__()
        self.macro_region_id = 999

    @allure.step("API: Поиск агентов для ресурсов")
    def _search_agents_for_resources(
        self,
        limit: int = 50,
        offset: int = 0,
    ) -> list:
        """
        Выполняет POST-запрос поиска агентов для ресурсов (agentsForResources/search).

        :param limit: limit (по умолчанию 50)
        :param offset: offset (по умолчанию 0)
        :return: Список агентов (items) из ответа API
        """
        url = f"{BASE_URL_LIS}/OAPI/v1/lis/logicalResources/cache/agentsForResources/search"
        params = {"limit": limit, "offset": offset}
        payload = {"macroRegionIds": [0, self.macro_region_id]}

        response = self.post(url=url, params=params, data=payload)
        self.check_response_status(response, 200, "Не удалось получить список агентов для ресурсов")

        data = response.json()
        return data.get("items", [])

    @allure.step("API: Поиск агентов для ресурсов и проверка наличия имени в ответе")
    def check_agent_for_resource_exists_by_name(
        self,
        name: str,
        limit: int = 50,
        offset: int = 0,
        timeout: int = 15,
    ) -> None:
        """
        POST-запрос поиска агентов для ресурсов (agentsForResources/search).
        Ждёт появления в ответе элемента с переданным именем; при истечении timeout падает с ошибкой.
        macroRegionIds не передаётся в метод — используется [0, macro_region_id].
        :param name: Имя для поиска и проверки в ответе
        :param limit: limit (по умолчанию 50)
        :param offset: offset (по умолчанию 0)
        :param timeout: Время ожидания появления имени в ответе, сек (по умолчанию 30)
        """

        def condition() -> bool:
            items = self._search_agents_for_resources(limit=limit, offset=offset)
            return any(item.get("name") == name for item in items if isinstance(item, dict))

        wait_that(
            condition,
            AssertionError,
            f"Имя '{name}' не появилось в ответе agentsForResources/search в течение {timeout} сек",
            timeout=timeout,
        )

    @allure.step("API: Проверить наличие агента по имени и что его статус «Закрыта»")
    def check_agent_status_by_name(
        self,
        name: str,
        status: str,
        limit: int = 50,
        offset: int = 0,
        timeout: int = 15,
    ) -> None:
        """
        Ждёт появления агента с переданным именем в agentsForResources/search,
        затем проверяет, что у него статус «Закрыта» (status.name).
        :param name: Имя агента (торговой точки)
        :param status: Статус торговой точки
        :param limit: limit (по умолчанию 50)
        :param offset: offset (по умолчанию 0)
        :param timeout: Время ожидания появления имени, сек (по умолчанию 15)
        """
        self.check_agent_for_resource_exists_by_name(name=name, limit=limit, offset=offset, timeout=timeout)

        def status_matches() -> bool:
            items = self._search_agents_for_resources(limit=limit, offset=offset)
            item = next(
                (i for i in items if isinstance(i, dict) and i.get("name") == name),
                None,
            )
            return (item or {}).get("status", {}).get("name") == status

        wait_that(
            status_matches,
            AssertionError,
            f"У агента '{name}' статус не стал '{status}' в течение {timeout} с",
            timeout=timeout,
        )
