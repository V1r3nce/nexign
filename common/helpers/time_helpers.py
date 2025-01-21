import time
from datetime import timedelta, datetime


import allure


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


@allure.step("Ожидание {timeout} сек., причина '{reason}'")
def delay(timeout: [int, float], reason: [str, None] = None):
    time.sleep(timeout)


def get_now_time():
    date = datetime.now()
    return date.strftime("%H:%M:%S")

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
