from typing import Any, Type

import allure
import psycopg2
from bs4 import BeautifulSoup

from api.base_requests import BaseRequests
from common.helpers.checker import check_that
from common.helpers.env_helper import BASE_URL_STANDHELPER
from db.exceptions import DBConnectionNotEstablished, DBCreditsNotFound, DBInvalidSQLQuery, StandhelperIsNotParsable
from models.db import DBCredits


class DBBase(BaseRequests):
    """
    Базовый класс для работы с БД. Не надо создавать его инстанс!
    Требуется для наследования. Смотри CrabDBRequests как пример использования.
    """

    def __init__(self, db_name: str) -> None:
        super().__init__()
        self.credits = self.get_db_credits(db_name)
        self.curr_conn = None

    def __new__(cls: Type["DBBase"], *args: Any, **kwargs: Any) -> "DBBase":
        if cls is DBBase:
            raise TypeError("Cannot instantiate DBBase directly")
        return super().__new__(cls)

    @allure.step("API: Парсинг данных с standhelper")
    def parse_standhelper(self, page_html: str) -> list:
        result = []
        soup = BeautifulSoup(page_html, "html.parser")
        table = soup.find("tbody")
        check_that(lambda: table is not None, StandhelperIsNotParsable, "Не удалось получить таблицу из standhelper")
        rows = table.find_all("tr")
        for row_index, row in enumerate(rows):
            cells = row.find_all(["td", "th"])
            result.append([cell.get_text(strip=True) for cell in cells])
        return result

    @allure.step("API: Получение данных о БД")
    def get_db_credits(self, db_name: str) -> DBCredits:
        parsed_credits = DBCredits()
        response = self.get(BASE_URL_STANDHELPER)
        self.check_response_status(response, 200, "Не удалось получить данные standhelper")
        urls = self.parse_standhelper(response.text())
        for url in urls:
            if f"DB {db_name.upper()}" in url[0]:
                parsed_credits.uri = url[1].replace("jdbc:", "")
                parsed_credits.user = url[2]
                parsed_credits.password = url[3]
                return parsed_credits
        raise DBCreditsNotFound("Не удалось найти указанную БД в реквизитах")

    @allure.step("DB: Установление соединения с БД")
    def connect(self) -> None:
        connect_str = self.credits.uri.replace("//", f"//{self.credits.user}:{self.credits.password}@")
        try:
            self.curr_conn = psycopg2.connect(connect_str)
        except psycopg2.Error:
            raise DBConnectionNotEstablished(
                f"Не удалось установить соединение с БД. Строка, с которой не удалось подключиться: {connect_str}"
            )

    @allure.step("DB: Выполнение select запроса к БД")
    def process_select(self, sql: str, is_empty: bool = False) -> list:
        """
        Выполняет SELECT-запрос и возвращает все строки результата.

        :param sql: SQL запрос SELECT.
        :param is_empty: Если False — при 0 строк выбрасывает AssertionError.
                         Если True — возвращает [] как валидный результат.
        :return: Список кортежей (строк результата). Может быть пустым, если is_empty=True.
        :raises DBInvalidSQLQuery: В случае ошибки исполнения SQL.
        """
        cur = self.curr_conn.cursor()
        try:
            cur.execute(sql)
            rows = cur.fetchall()
            allure.attach(body=sql, name="SQL", attachment_type=allure.attachment_type.TEXT)
        except psycopg2.Error:
            cur.close()
            raise DBInvalidSQLQuery("Некорректный SQL запрос")
        finally:
            cur.close()

        if not rows and not is_empty:
            raise AssertionError(f"SELECT вернул 0 строк, но ответ ожидался непустым. SQL запрос:\n{sql}")

        return rows

    @allure.step("DB: Выполнение запроса с изменением данных в БД")
    def process_changes(self, sql: str) -> None:
        """
        :param sql: SQL запрос типа INSERT, UPDATE, DELETE
        """
        cur = self.curr_conn.cursor()
        try:
            cur.execute(sql)
            self.curr_conn.commit()
            allure.attach(body=sql, name="SQL", attachment_type=allure.attachment_type.TEXT)
        except psycopg2.Error:
            self.curr_conn.rollback()
            cur.close()
            raise DBInvalidSQLQuery("Некорректный SQL запрос")
        cur.close()
