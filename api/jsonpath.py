from typing import Any

from jsonpath_ng import Child
from jsonpath_ng.exceptions import JsonPathLexerError, JsonPathParserError
from jsonpath_ng.ext import parse as json_parse
from loguru import logger

from common.helpers.conditions import Condition


class JsonPathParser:
    """Класс для получения значения из json."""

    def __init__(self, expression: str):
        self.expr: Child = self.get_expression(expression)
        self.result = None

    @staticmethod
    def get_expression(expression: str) -> Child:
        """Проверка синтаксиса выражения.
        :param expression: Выражение для поиска
        :return: выражение"""
        try:
            return json_parse(expression)
        except Exception as e:
            msg = f"Неправильный синтаксис выражения jsonpath: {expression}\n{e}\n"
            logger.error(msg)
            logger.error(e)
            raise JsonPathLexerError(msg)

    def parse(self, data: dict) -> Any | None:
        """Поиск значения по jsonpath выражению.
        :param data: Данные для поиска
        :return: значение"""
        found_data = self.expr.find(data)
        found_values = [datum.value for datum in found_data]

        if not found_values:
            msg = f"Значение jsonpath не найдено: {self.expr}"
            logger.error(msg)

            raise JsonPathParserError(msg)

        self.result = found_values
        return self.result if len(self.result) > 1 else self.result[0]

    def compare_values(self, op: str, value: str, values: dict) -> str | None:
        """Сравнение значений.

        :param op: Оператор
        :param value: значение
        :param values: выражение jsonpath
        :return: результат проверки
        """
        try:
            left_value = self.parse(values)
        except JsonPathParserError as e:
            return str(e)

        if not Condition(left_value, op, value).evaluate():
            logger.error(f"Условие не выполнено для ключа: {self.expr}")
            logger.error(f"{left_value} | {op} | {value}")

            return f"{left_value} | {op} | {value}"
        logger.info(f"Проверка:\n{left_value} | {op} | {value}")
        return None
