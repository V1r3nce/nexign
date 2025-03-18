"""Переопределение контекстного менеджера allure.step, чтобы шаг попадал в логи."""
from loguru import logger


class CustomAllure:
    def __init__(self, title):
        self.title = title

    def __enter__(self):
        logger.info(f"Allure step: {self.title}")

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


def step_decorator(func):
    def wrapper(title, *args, **kwargs):
        with CustomAllure(title):
            return func(title, *args, **kwargs)

    return wrapper