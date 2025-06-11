import operator as python_operator
from typing import Any, Callable

from common.helpers.checker import check_that


def equals(a: Any, b: Any) -> bool:
    """Функция проверяет, что a равен b."""
    if a == b:
        return True
    else:
        return str(a) == str(b)


def has(a: Any, b: Any) -> bool:
    """Функция проверяет, что a содержит b."""
    if isinstance(a, list):
        if len(a) == 1:
            if not isinstance(b, list):
                return str(b) in str(a[0])
        if isinstance(a[0], str) and isinstance(b, int):
            return str(b) in a
    return str(b) in str(a)


def include(a: Any, b: Any) -> bool:
    """Функция проверяет, что b содержит a."""
    if isinstance(a, list):
        if len(a) == 1:
            if not isinstance(b, list):
                return str(a[0]) in b
            return a[0] in b
    return str(a) in str(b)


class Condition:
    operators = {
        "==": equals,
        "!=": lambda a, b: a != b,
        ">=": lambda a, b: a >= b,
        ">": lambda a, b: a > b,
        "<=": lambda a, b: a <= b,
        "<": lambda a, b: a < b,
        "equals": equals,
        "has": has,
        "in": include,
        "gt": lambda a, b: a > b,
        "lt": lambda a, b: a < b,
    }

    def __init__(self, left_value: str, operator: str, right_value: str):
        self.left_value = left_value
        self.right_value = right_value
        self.logical_operator, self.comparison_operator = self.parse_operator(operator)

    def parse_operator(self, operator: str) -> tuple:
        """
        Преобразование оператора в логический оператор и оператор сравнения. Проверка на отрицание.
        :param operator: оператор сравнения (==, !=, >, >=, <, <=, has, in, not in, not has, equals, gt, lt)
        :return: логический оператор и оператор сравнения
        """
        logical_operator = python_operator.truth
        comparison_operator = None

        check_that(
            lambda: isinstance(operator, str),
            ValueError,
            f"Передан некорректный оператор: {operator}\n Доступные операторы: {self.operators.keys()}",
        )

        for condition_op in operator.split():
            if condition_op == "not":
                logical_operator = python_operator.not_
            else:
                comparison_operator = condition_op

        check_that(
            lambda: comparison_operator in self.operators,
            ValueError,
            f"Передан некорректный оператор сравнения: {comparison_operator}\n Доступные операторы: {self.operators.keys()}",
        )

        return logical_operator, comparison_operator

    def evaluate(self) -> bool:
        """Проверка условия.
        :return: Результат проверки условия"""
        operator_func: Callable = self.operators.get(self.comparison_operator)
        compare_values = lambda left_value, right_value: self.logical_operator(operator_func(left_value, right_value))

        return compare_values(self.left_value, self.right_value)
