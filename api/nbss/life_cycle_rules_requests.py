from dataclasses import dataclass

import allure

from api.base_requests import BaseRequests
from common.helpers.env_helper import BASE_URL_API
from models.context import test_context


@dataclass
class GraphInfo:
    """Класс для информации о графе"""

    graph: dict

    def __post_init__(self) -> None:
        self.graph_id = self.graph["graphId"]
        self.name = self.graph["name"]
        self.initial_status = self.graph["entityInitialStatus"]["name"]
        self.final_status = self.graph["entityFinalStatus"]["name"]


class LifeCycleRulesRequests(BaseRequests):
    def __init__(self) -> None:
        test_context.page.context.set_extra_http_headers({"accept-language": "ru"})
        super().__init__()

    @allure.step("API: Получить список графов")
    def get_graphs(
        self,
        graph_id: int = None,
        graph_name: str = None,
        entity_type: str = None,
        initial_status_id: int = None,
        final_status_id: int = None,
        is_default: bool = None,
        is_actual: bool = True,
    ) -> list:
        """
        Метод получает список графов

        Parameters:
        graph_id (int): идентификатор графа
        graph_name (str): наименование правила
        entity_type (str): тип сущности
        initial_status_id (int): начальный статус
        final_status_id (int): конечный статус
        is_default (bool): признак, является ли граф базовым правилом
        is_actual (bool): признак, является ли граф действующим

        Returns:
        list: список словарей с данными о найденных графах
        """
        payload = {"isActual": is_actual}
        if graph_id:
            payload["graphId"] = graph_id
        if graph_name:
            payload["graphName"] = graph_name
        if entity_type:
            payload["entityTypeCode"] = entity_type
        if initial_status_id:
            payload["entityInitialStatusId"] = initial_status_id
        if final_status_id:
            payload["entityFinalStatusId"] = final_status_id
        if is_default is not None:
            payload["isDefault"] = is_default
        graphs = self.post(url=f"{BASE_URL_API}/ps/v1/nlm/graphs/search", data=payload)
        self.check_response_status(graphs, 200, "Не получен список графов")
        return graphs.json()["items"]

    @allure.step("API: Создать граф")
    def create_graph(
        self,
        graph_name: str,
        initial_status_id: int = 1,
        final_status_id: int = 4,
        entity_type: str = "product",
        is_default: bool = False,
    ) -> int:
        """
        Метод создаёт граф

        Parameters:
        graph_name (str): наименование правила
        initial_status_id (int): начальный статус
        final_status_id (int): конечный статус
        entity_type (str): тип сущности ("product" - Продукт клиента, "AGREEMENT" - Договор клиента)
        is_default (bool): признак, является ли граф базовым правилом

        Returns:
        int: идентификатор созданного графа
        """
        payload = {
            "graphName": graph_name,
            "entityTypeCode": entity_type,
            "isDefault": is_default,
            "entityInitialStatusId": initial_status_id,
            "entityFinalStatusId": final_status_id,
        }
        graph = self.post(url=f"{BASE_URL_API}/ps/v1/nlm/graphs", data=payload)
        self.check_response_status(graph, 201, "Не удалось создать граф")
        return graph.json()["graphId"]

    @allure.step("API: Получить список статусов правил ЖЦ")
    def get_statuses(self) -> set[str]:
        """
        Метод получает список статусов

        Returns:
        set[str]: множество имен существующих статусов
        """
        statuses = self.get(url=f"{BASE_URL_API}/openapi/v1/lifeCycleManagement/dictionaries/entityStatuses")
        self.check_response_status(statuses, 200, "Не получен список статусов")

        statuses_set = set()
        statuses_items = statuses.json()["items"]
        assert len(statuses_items) > 0, "Не получена информация о статусах"
        for status_item in statuses_items:
            statuses_set.add(status_item["name"][0]["value"])
        return statuses_set

    @allure.step("API: Получить список событий")
    def get_events_names(self) -> list[str]:
        """
        Метод получает список событий

        Returns:
        list[str]: список существующих событий
        """
        events_names = []
        payload: dict = {}
        events_data = self.post(url=f"{BASE_URL_API}/ps/v1/nlm/dictionaries/events/search", data=payload)
        self.check_response_status(events_data, 200, "Не получен список событий")
        for event_item in events_data.json()["items"]:
            events_names.append(event_item["name"])
        return events_names

    @allure.step("API: Аннулировать граф")
    def cancel_graph(self, graph_id: int) -> None:
        """
        Метод отправляет запрос на аннулирование графа

        Parameters:
        graph_id (int): идентификатор графа
        """
        graph = self.post(url=f"{BASE_URL_API}/ps/v1/nlm/graphs/{graph_id}/cancel")
        self.check_response_status(graph, 204, "Не удалось отправить запрос на аннулирование графа")
