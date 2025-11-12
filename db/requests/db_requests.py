from datetime import datetime, timedelta

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


class LisDBRequests(DBBase):
    """
    Класс для работы с БД LIS.
    Используется в связке с фикстурой create_lis_db_connection.
    """

    def __init__(self, api_request_auth_context: APIRequestContext) -> None:
        super().__init__("lis", api_request_auth_context)

    @allure.step("DB: Поиск безопасного номера (Свободен + Открыт для использования) → MSISDN")
    def get_safe_number_candidate(self) -> str | None:
        """
        Ищет один номер со статусом 'Свободен' и состоянием 'Открыт для использования'.

        :return: MSISDN подходящего номера строкой, либо None если такой номер не найден.
        """
        sql = """
            SELECT msisdn
            FROM lis.lis_numbers
            WHERE lsts_lsts_id = 1
              AND nstt_nstt_id = 2
            LIMIT 1;
        """

        rows = self.process_select(sql, is_empty=True)
        if not rows:
            return None
        return str(rows[0][0])

    @allure.step("DB: Перевод номера {msisdn} в карантин (nstt=4, isolation_end_date)")
    def put_number_into_quarantine(self, msisdn: str, iso_end: datetime | None = None) -> None:
        """
        Переводит указанный номер в состояние 'Освобожден' (карантин) и устанавливает дату окончания карантина.

        :param msisdn: Номер (MSISDN), который нужно перевести в карантин.
        :param iso_end: Дата окончания карантина (дата без времени). Если не задано — ставится завтрашний день 00:00.
        :return: None
        """
        if iso_end is None:
            iso_end = datetime.now().date() + timedelta(days=1)

        iso_end_str = f"{iso_end} 00:00:00"

        sql = f"""
            UPDATE lis.lis_numbers
               SET nstt_nstt_id = 4,
                   isolation_end_date = '{iso_end_str}'
             WHERE msisdn = '{msisdn}';
        """

        self.process_changes(sql)

    @allure.step("DB: Создание карантинного номера → вернуть MSISDN")
    def make_quarantine_number(self, iso_end: datetime | None = None) -> str:
        """
        Находит свободный номер (Свободен + Открыт для использования), переводит его в карантин и возвращает MSISDN.

        :param iso_end: Дата окончания карантина (дата без времени). Если не задано — ставится завтрашний день 00:00.
        :return: MSISDN переведённого в карантин номера.
        :raises AssertionError: Если не найден ни один подходящий номер.
        """
        msisdn = self.get_safe_number_candidate()
        if msisdn is None:
            raise AssertionError("Нет номера со статусом 'Свободен' и состоянием 'Открыт для использования'.")

        self.put_number_into_quarantine(msisdn, iso_end)
        return msisdn
