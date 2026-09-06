"""Общий учёт шагов allure для записывающих плагинов.

И запись DOM, и запись сетевых вызовов привязывают снятое к шагу теста, а значит обеим нужно
одно и то же: подписка на официальные хуки allure, счётчик шагов верхнего уровня, текущая
глубина вложенности и стек заголовков. Держать это в двух местах — гарантированно развести их
поведение, поэтому бухгалтерия шагов живёт здесь, а наследники решают только, что делать
на границах шага.

Нумеруются шаги ВЕРХНЕГО уровня, то есть ``with allure.step(...)``, написанные прямо в тесте.
Шаги пейдж-объектов вложены в них и своего номера не получают — они приходят в
:meth:`StepTracker.on_boundary` с фактической глубиной.
"""

from __future__ import annotations

from typing import Any

from allure_commons import hookimpl


class StepTracker:
    """Считает шаги allure и зовёт наследника на границах шага.

    :ivar depth: Текущая глубина вложенности шагов: 1 — шаг теста, больше — шаги пейджей.
    :ivar step_no: Номер текущего шага теста, начиная с 1.
    """

    def __init__(self) -> None:
        self.depth = 0
        self.step_no = 0
        self._titles: list[str] = []

    @hookimpl
    def start_step(self, uuid: str, title: str, params: dict[str, Any]) -> None:
        """Хук allure: вход в шаг.

        :param uuid: Идентификатор шага в allure, не используется.
        :param title: Заголовок шага.
        :param params: Параметры шага, не используются.
        """
        self.depth += 1
        self._titles.append(title)
        if self.depth == 1:
            self.on_test_step_start()
        self.on_boundary(self.depth, title, exiting=False)

    @hookimpl
    def stop_step(self, uuid: str, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Хук allure: выход из шага.

        :param uuid: Идентификатор шага в allure, не используется.
        :param exc_type: Класс исключения, если шаг упал.
        :param exc_val: Исключение, если шаг упал.
        :param exc_tb: Трассировка, не используется.
        """
        depth = self.depth
        self.depth -= 1
        title = self._titles.pop() if self._titles else ""
        self.on_boundary(depth, title, exiting=True)
        if depth == 1:
            self.on_test_step_end(exc_type, exc_val)

    def on_test_step_start(self) -> None:
        """Вызывается на входе в шаг теста, до :meth:`on_boundary`. Наследник может переопределить."""
        self.step_no += 1

    def on_boundary(self, depth: int, title: str, exiting: bool) -> None:
        """Вызывается на каждой границе каждого шага.

        :param depth: Глубина шага: 1 — шаг теста, 2 и больше — вложенные шаги пейджей.
        :param title: Заголовок шага.
        :param exiting: True для выхода из шага, False для входа.
        """

    def on_test_step_end(self, exc_type: Any, exc_val: Any) -> None:
        """Вызывается на выходе из шага теста, после :meth:`on_boundary`.

        :param exc_type: Класс исключения, если шаг упал.
        :param exc_val: Исключение, если шаг упал.
        """
