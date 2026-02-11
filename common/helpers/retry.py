import time
from contextlib import contextmanager


@contextmanager
def retry(tries: int = 3, delay: int = 1, exceptions: Exception = (Exception,)) -> None:
    """
    Менеджер контекста для повтора блока кода, ожидающий возможность появления исключений exceptions.
    При их появлении делается следующая попытка. Неуказанные исключения будут обработаны в обычном порядке.
    Если все три попытки завершатся неуспешно, то все три падения будут записаны и выведены в сообщении AssertionError
    :param tries: количество попыток
    :param delay: задержка между попытками
    :param exceptions: ожидаемые исключения
    """
    attempt = 1
    raised_messages = []
    while True:
        try:
            yield
            break
        except exceptions as e:
            raised_messages.append(e)
            if attempt >= tries:
                result_message = "Все попытки выполнения исчерпаны\n"
                for i in range(tries):
                    result_message += f"\nОшибка {i + 1} попытки: {raised_messages[i]}"
                raise AssertionError(result_message)

            time.sleep(delay)
            attempt += 1
