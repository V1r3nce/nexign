import random
from datetime import datetime, timedelta

from faker import Faker


def get_shifted_datetime(shift: str, date_time: datetime = None) -> datetime:
    shift_operator = shift[:1]
    shift_value = int(shift[1:-1])
    shift_key = shift[-1]
    shifts = ['+', '-']

    assert shift_operator in shifts

    shift_keys = {
        "m": "minutes",
        "h": "hours",
        "d": "days",
    }
    assert shift_key in shift_keys

    shift_key = shift_keys[shift_key]
    current_datetime = date_time or datetime.now()
    if shift_operator == '+':
        return current_datetime + timedelta(**{shift_key: shift_value})
    else:
        return current_datetime - timedelta(**{shift_key: shift_value})

def generate_random_number(num_digits: int):
    start = 10 ** (num_digits - 1)
    end = 10 ** num_digits - 1
    random_number = random.randint(start, end)
    return random_number


def generate_russian_string(length: int):
    russian_letters = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
    return ''.join(random.choice(russian_letters) for _ in range(length))


class FakerRu(Faker):
    def __init__(self):
        super().__init__("ru_RU")

    def phone_number(self):
        return f"+79{generate_random_number(9)}"


faker_ru = FakerRu()
print(datetime.today(), get_shifted_datetime("+100m"))
