import math
import random
from datetime import datetime, timedelta, timezone

from faker import Faker

from common.helpers.time_helpers import get_shifted_datetime


def get_current_datetime_string(is_full_format: bool = True) -> str:
    now = datetime.now()
    return now.strftime("%d.%m.%Y %H:%M:%S") if is_full_format else now.strftime("%d.%m.%Y")


def get_current_datetime_string_for_api(is_full_format: bool = True) -> str:
    now = datetime.now()
    return now.strftime("%Y-%m-%dT%H:%M:%S") if is_full_format else now.strftime("%Y-%m-%d")


def get_shifted_datetime_string(shift: str, is_full_format: bool = True, shift_from: datetime | None = None) -> str:
    shifted_date = get_shifted_datetime(shift, shift_from)
    return shifted_date.strftime("%d.%m.%Y %H:%M:%S") if is_full_format else shifted_date.strftime("%d.%m.%Y")


def get_exact_day_of_current_month(day: str | int | None = None, is_full_format: bool = True) -> str:
    """
    Функция возвращает дату дня текущего месяца в формате строки.

    :param day:
        - "first" для первого дня месяца
        - "last" для последнего дня месяца
        - целое число для конкретного дня месяца
        - пустое значение для текущей даты
    :param is_full_format:
        - True для полного формата (ДД.ММ.ГГГГ ЧЧ:ММ:СС)
        - False для формата ДД.ММ.ГГГГ

    : return - строка с датой в заданном формате
    """
    now = datetime.now()

    day_actions = {
        "first": datetime(now.year, now.month, 1),
        "last": (datetime(now.year, now.month + 1, 1) if now.month < 12 else datetime(now.year + 1, 1, 1))
        - timedelta(days=1),
    }

    if not day:
        date = now
    elif day in day_actions:
        date = day_actions[day]
    else:
        try:
            date = datetime(now.year, now.month, day)
        except ValueError:
            raise ValueError(f"Невалидный день '{day}' для текущей даты {now.month}/{now.year}")

    return date.strftime("%d.%m.%Y %H:%M:%S") if is_full_format else date.strftime("%d.%m.%Y")


def get_datetime_from_full_time_string(date_string: str, replace_timezone: bool = False) -> datetime:
    """
    Получить объект datetime из строки вида %Y-%m-%dT%H:%M:%S или %Y-%m-%dT%H:%M:%S.000
    :param date_string: строка вида %Y-%m-%dT%H:%M:%S или %Y-%m-%dT%H:%M:%S.000
    :param replace_timezone: если задан True, то при преобразовании объекта нужно заменить timezone
    :return: объект datetime
    """
    if replace_timezone:
        date_object = datetime.strptime(date_string[:19], "%Y-%m-%dT%H:%M:%S").replace(
            tzinfo=timezone(timedelta(hours=3))
        )
    else:
        date_object = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S")
    return date_object


def generate_random_number(num_digits: int) -> int:
    start = 10 ** (num_digits - 1)
    end = 10**num_digits - 1
    random_number = random.randint(start, end)
    return random_number


def generate_russian_string(length: int) -> str:
    russian_letters = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
    return "".join(random.choice(russian_letters) for _ in range(length))


def generate_english_string(length: int) -> str:
    letters = "abcdefghijklmnopqrstuvwxyz"
    return "".join(random.choice(letters) for _ in range(length))


def generate_random_ip(parts_num: int) -> str:
    """
    Функция генирирует ip, частично или полностью
    :param parts_num - количество сгенирированных частей ip
    :return - Полный или неполный ip

    Пример:
    parts_num: 3 => return: 100.100.100
    """
    return ".".join(str(random.randint(0, 255)) for _ in range(parts_num))


def calc_tax(amount: float, tax_percent: float = 20) -> float:
    """
    Функция рассчитывает сумму налога
    :param amount - сумма с учетом налога
    :param tax_percent - процент налога, налоговая ставка
    :return - сумма налога, округленная до 2 сотых

    Пример:
    amount: 550, tax_percent: 20 => return: 91.67
    """
    return round(amount * tax_percent / (100 + tax_percent), 2)


def round_up(number: float, digits: int) -> float:
    """
    Функция округляет число в большую сторону
    :param number - число, которое нужно округлить
    :param digits - точность, с которой нужно округлить (количество знаков после запятой)
    :return - округленное число

    Пример:
    number: 133.33333333, digits: 2 => return: 133.34
    """
    mult = 10**digits
    return math.ceil(number * mult) / mult


class FakerRu(Faker):
    def __init__(self) -> None:
        super().__init__("ru_RU")

    def phone_number(self) -> str:
        return f"+79{generate_random_number(9)}"


faker_ru = FakerRu()
