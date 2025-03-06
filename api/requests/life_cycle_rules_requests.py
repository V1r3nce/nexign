from dataclasses import dataclass

import allure
from playwright.sync_api import APIResponse, Page

from common.helpers.env_helper import BASE_URL_API


@dataclass
class GraphInfo:
    """Класс для информации о графе"""
    graph : dict

    def __post_init__(self):
        self.graph_id = self.graph['graphId']
        self.name = self.graph['name']
        self.initial_status = self.graph['entityInitialStatus']['name']
        self.final_status = self.graph['entityFinalStatus']['name']

class LifeCycleRulesRequests:
    def __init__(self, page: Page):
        self.page = page
        self.page.context.set_extra_http_headers({"accept-language": "ru"})
        self.api_request_auth_context = self.page.request

    def get_graphs(self) -> APIResponse:
        """
        Метод получает список графов
        """
        payload = {}
        graphs = self.api_request_auth_context.post(
            url=f"{BASE_URL_API}/ps/v1/nlm/graphs/search", data=payload)
        assert graphs.status == 200, "Не получен список графов"
        return graphs

    @allure.step('Получить информацию о графе со статусом "Базовое правило"')
    def get_info_about_default_graph(self) -> GraphInfo:
        """
        Метод получает информацию о графе со статусом "Базовое правило".

        Returns:
        GraphInfo: объект с информацией о графе
        """
        graphs = self.get_graphs().json()['items']
        assert len(graphs) > 0, "Не получена информация о графах"

        default_graphs = list(filter(lambda graph: graph['isDefault'], graphs))
        assert len(default_graphs) == 1, "Базовое правило может быть только 1"
        return GraphInfo(default_graphs[0])

    @allure.step("Получить список статусов правил ЖЦ")
    def get_statuses(self) -> set[str]:
        """
        Метод получает список статусов

        Returns:
        set[str]: множество имен существующих статусов
        """
        statuses = self.api_request_auth_context.get(
            url=f"{BASE_URL_API}/openapi/v1/lifeCycleManagement/dictionaries/entityStatuses")
        assert statuses.status == 200, "Не получен список статусов"

        statuses_set = set()
        statuses_items = statuses.json()['items']
        assert len(statuses_items) > 0, "Не получена информация о статусах"
        for status_item in statuses_items:
            statuses_set.add(status_item['name'][0]['value'])
        return statuses_set

    def get_transitions(self, graph_id: int, payload: dict) -> APIResponse:
        """
        Метод получает список переходов графа

        Parameters:
        graph_id (int): id графа
        payload (dict): словарь фильтров поиска

        Returns:
        Response: объект ответа API со списком переходов графа
        """
        transitions = self.api_request_auth_context.post(
            url=f"{BASE_URL_API}/ps/v1/nlm/graphs/{graph_id}/transitions/search", data=payload)
        assert transitions.status == 200, "Не получен список статусов"
        return transitions

    @allure.step("Получить список событий")
    def get_events_names(self) -> list[str]:
        """
        Метод получает список событий

        Returns:
        list[str]: список существующих событий
        """
        events_names = []
        payload = {}
        events_data = self.api_request_auth_context.post(
            url=f"{BASE_URL_API}/ps/v1/nlm/dictionaries/events/search", data=payload)
        assert events_data.status == 200, "Не получен список событий"
        for event_item in events_data.json()['items']:
            events_names.append(event_item['name'])
        return events_names
