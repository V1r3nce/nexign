import time
from functools import wraps
from typing import Any, Callable


def retry(
    tries: int = 3, delay: int = 1, exceptions: tuple = (Exception,)
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            attempt = 1
            raised_messages = []

            while True:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    raised_messages.append(e)
                    if attempt >= tries:
                        result_message = "Все попытки выполнения исчерпаны\n"
                        for i in range(tries):
                            result_message += f"\nОшибка {i + 1} попытки: {raised_messages[i]}"
                        raise AssertionError(result_message)

                    time.sleep(delay)
                    attempt += 1

        return wrapper

    return decorator


def execute_with_retry(func: Callable[[], Any], tries: int = 3, delay: int = 1, exceptions: tuple = (Exception,)) -> Any:
    attempt = 1
    raised_messages = []
    while True:
        try:
            return func()  # Выполняем переданный кусок кода
        except exceptions as e:
            raised_messages.append(e)
            if attempt >= tries:
                result_message = "Все попытки выполнения исчерпаны\n"
                for i in range(tries):
                    result_message += f"\nОшибка {i + 1} попытки: {raised_messages[i]}"
                raise AssertionError(result_message)

            time.sleep(delay)
            attempt += 1
