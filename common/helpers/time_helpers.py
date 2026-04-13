import re
import time
from datetime import date, datetime, timedelta, timezone

import allure

from common.helpers.checker import assert_that

TIME_FOR_UPDATE_LIST = "Время на обновление списка"
TIME_FOR_UPDATE_STATUS = "Время на обновление статуса"
TIME_FOR_DOWNLOAD_FILE = "Время на загрузку файла"
TIME_FOR_UPDATE_COLOR = "Время на обновление цвета"
TIME_FOR_TURN_ON_SWITCH = "Время для включения свича"
TIME_FOR_PAGE_LOAD = "Время для загрузки страницы"
TIME_FOR_UPDATE_CHECKBOX_STATUS = "Время для смены состояния чекбокса"
TIME_FOR_LIST_LOAD = "Время для загрузки списка"
TIME_FOR_UPDATE_DATE = "Время для обновления даты"
TIME_TO_CLEAR_THE_FIELD = "Время для очищения поля"


def delay(timeout: int | float, reason: str | None = None) -> None:
    with allure.step(f"Ожидание {timeout} сек., причина '{reason}'"):
        time.sleep(timeout)


def get_now_time(fmt: str = "%H:%M:%S") -> str:
    return datetime.now().strftime(fmt)


def get_iso_now_time_moscow() -> str:
    """Возвращает время в формате 2025-03-26T12:34:56+03:00"""
    return datetime.now().replace(tzinfo=timezone(timedelta(hours=3))).isoformat()


def get_current_moscow_datetime() -> datetime:
    return datetime.now(timezone(timedelta(hours=3)))


def get_datetime_from_string(date_string: str, is_full_format: bool = True) -> datetime:
    """Получить объект datetime из строки вида %d.%m.%Y %H:%M:%S или %d.%m.%Y с часовым поясом +03:00"""
    if is_full_format:
        pattern = r"^\d{2}.\d{2}.\d{4} \d{2}:\d{2}:\d{2}$"
        assert_that(lambda: re.match(pattern, date_string), "Формат даты/сама дата отличается от ожидаемого")
        date = datetime.strptime(date_string, "%d.%m.%Y %H:%M:%S")
    else:
        pattern = r"^\d{2}.\d{2}.\d{4}"
        assert_that(lambda: re.match(pattern, date_string), "Формат даты/сама дата отличается от ожидаемого")
        date = datetime.strptime(date_string, "%d.%m.%Y")
    return date.replace(tzinfo=timezone(timedelta(hours=3)))


def get_shifted_datetime(shift: str, date_time: datetime = None) -> datetime:
    """
    Возвращает дату/время, сдвинутую на указанное значение
    :param shift: строка вида "+1m", "-1h", "+1d", "-1y"
    :param date_time: дата/время, относительно которого будет происходить сдвиг
    :return: дата/время, сдвинутая на указанное значение
    """
    shift_operator = shift[:1]
    shift_value = int(shift[1:-1])
    shift_key = shift[-1]
    shifts = ["+", "-"]

    assert shift_operator in shifts, f"Неверный символ операции: {shift_operator}. Доступные варианты: {shifts}"

    shift_keys = {
        "m": "minutes",
        "h": "hours",
        "d": "days",
        "y": "years",
    }
    assert shift_key in shift_keys, f"Неверный символ ключа: {shift_key}. Доступные варианты: {shift_keys}"
    shift_key = shift_keys[shift_key]

    current_time = date_time or datetime.now()
    if shift_operator == "+":
        return current_time + timedelta(**{shift_key: shift_value})
    else:
        return current_time - timedelta(**{shift_key: shift_value})


def timestamp_to_datetime_string(timestamp: int) -> str:
    return datetime.fromtimestamp(timestamp / 1000, timezone(timedelta(hours=3))).strftime("%d.%m.%Y %H:%M:%S")


def get_current_day_psc() -> str:
    curr_date = str(date.today())
    curr_date += "T00:00:00.000"
    return curr_date


def convert_shifted_psc(shifted_datetime: datetime) -> str:
    """
    Метод для преобразования даты и времени в формат нужный PSC
    :param shifted_datetime: дата и время
    :return: преобразованная строка
    """
    datetime_str = str(shifted_datetime)
    datetime_str = datetime_str.replace(" ", "T")
    return datetime_str[: len(datetime_str) - 6] + "000"
