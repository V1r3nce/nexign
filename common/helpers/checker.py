from collections.abc import Callable
from typing import Any, Type, Union

import allure
from playwright.sync_api import APIResponse
from waiting import TimeoutExpired, wait

from common.const import Constants

MessageType = Union[str, Callable[[], str]]
ExceptionType = type[Exception]


def core_wait(
    condition: Callable,
    exception_message: MessageType,
    exception: ExceptionType = AssertionError,
    timeout: int = Constants.DEFAULT_TIMEOUT_SECONDS,
    sleep_seconds: float = 0.5,
    **kwargs: Any,
) -> None:
    try:
        wait(condition, timeout_seconds=timeout, sleep_seconds=sleep_seconds, **kwargs)
    except TimeoutExpired:
        exception_message = exception_message() if callable(exception_message) else exception_message
        raise exception(exception_message)


def _check(
    condition: Callable,
    exception: ExceptionType,
    message: MessageType,
    ignore: ExceptionType | tuple[ExceptionType] | tuple = (),
    timeout: int | bool = 0,
    **kwargs: Any,
) -> None:
    if timeout is True:
        timeout = Constants.DEFAULT_TIMEOUT_SECONDS

    ignore = ignore if isinstance(ignore, tuple) else (ignore,)

    return core_wait(
        condition=condition,
        exception_message=message,
        exception=exception,
        timeout=timeout,
        expected_exceptions=ignore,
        **kwargs,
    )


def check_that(condition: Callable, exception: ExceptionType | None = None, message: MessageType | None = None) -> None:
    """Проверка со своим исключением.

    Ошибки обработанные этой функцией,
    будут покрашены в желтый цвет allure отчета, означающий баг в тесте, а не продукте.
    params:
        condition: lambda функция с выражением
        exception: исключение
        message: сообщение об ошибке
    return: переданное исключение, если выражение ложь
    """
    return _check(condition=condition, exception=exception, message=message)


def assert_that(condition: Callable, message: MessageType, timeout: int = 0, **kwargs: Any) -> None:
    """Альтернативный ассерт. Ошибки обработанные этой функцией, будут покрашены в красный цвет означающий баг в ПО.
    params:
        condition: lambda функция с выражением
        message: сообщение об ошибке
        timeout: время ожидания
    return: AssertionError если выражение - ложь
    """
    return _check(condition=condition, exception=AssertionError, message=message, timeout=timeout, **kwargs)


@allure.step("Ожидание выполнения условия")
def wait_that(
    condition: Callable, exception: ExceptionType, message: MessageType, timeout: bool | int = True, **kwargs: Any
) -> None:
    """Ожидание с собственным исключением.

    Ошибки обработанные этой функцией,
    будут покрашены в желтый цвет allure отчета, означающий баг в тесте, а не продукте.
    params:
        condition: lambda функция с выражением
        exception: исключение
        message: сообщение об ошибке
        timeout: время ожидания
    return: переданное исключение, если выражение ложь
    """
    return _check(condition=condition, exception=exception, message=message, timeout=timeout, **kwargs)


def check_response_conflicts(response: APIResponse, exception: Type[Exception] = AssertionError) -> None:
    check_that(
        lambda: len(response.json().get("conflicts")) == 0,
        exception,
        "\n".join([conflict.get("message") for conflict in response.json().get("conflicts")]),
    )
