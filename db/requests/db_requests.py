import allure
from playwright.sync_api import APIRequestContext

from db.requests.db_base import DBBase


class CrabDBRequests(DBBase):
    """
    Класс для работы с БД CRAB.
    Используется в связке с фикстурой create_crab_db_connection.
    Пример использования: в setup тестового класса "self.db = create_crab_db_connection" и потом уже у возвращенного инстанса вызывать методы данного класса
    """

    def __init__(self, api_request_auth_context: APIRequestContext) -> None:
        super().__init__("crab", api_request_auth_context)

    @allure.step("DB: Получение дочерних заказов из БД CRAB")
    def get_child_orders(self, parent_order_id: int) -> list:
        res = self.process_select(f"select * from orders o where o.root_external_id = 'order-{parent_order_id}';")
        return res

    @allure.step("DB: Получение дочернего udsServiceConnect заказа из БД CRAB")
    def get_service_connect_order_id(self, parent_order_id: int) -> int | None:
        for order in self.process_select(
            f"select o.external_id from orders o where o.root_external_id = 'order-{parent_order_id}' and o.workflow_name='udsServiceConnect';"
        ):
            return order
        return None
