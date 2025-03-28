"""Переопределение контекстного менеджера allure.step, чтобы шаг попадал в логи."""

from typing import Any, Callable

from loguru import logger


class CustomAllure:
    def __init__(self, title: str):
        self.title = title

    def __enter__(self) -> None:
        logger.info(f"Allure step: {self.title}")

    def __exit__(self, exc_type, exc_val, exc_tb):  # type: ignore
        pass


def step_decorator(func: Callable) -> Callable:
    def wrapper(title: str, *args: Any, **kwargs: Any) -> Any:
        with CustomAllure(title):
            return func(title, *args, **kwargs)

    return wrapper
