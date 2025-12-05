import pytest
from playwright.sync_api import Page

from api.exceptions import CancelGraphException
from api.nbss.life_cycle_rules_requests import GraphInfo, LifeCycleRulesRequests
from common.helpers.checker import wait_that
from common.helpers.data_generator import generate_random_number


@pytest.fixture
def add_and_cancel_graph(page: Page) -> GraphInfo:
    """Фикстура для создания и аннулирования правила ЖЦ"""
    life_cycle_rules_requests = LifeCycleRulesRequests()
    name = "Граф Тест_" + str(generate_random_number(4))
    graph_id = life_cycle_rules_requests.create_graph(name)
    graph = GraphInfo(life_cycle_rules_requests.get_graphs(graph_id=graph_id)[0])
    yield graph
    if life_cycle_rules_requests.get_graphs(graph_id=graph_id):
        life_cycle_rules_requests.cancel_graph(graph_id)
        wait_that(
            lambda: len(life_cycle_rules_requests.get_graphs(graph_id=graph_id)) == 0,
            timeout=20,
            sleep_seconds=0.5,
            exception=CancelGraphException,
            message="Граф не аннулировался за 20 секунд",
        )
