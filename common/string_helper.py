import random


def generate_random_number(num_digits: int):
    """Генерация рандомного числа из num_digits значений"""
    start = 10 ** (num_digits - 1)
    end = 10 ** num_digits - 1
    random_number = random.randint(start, end)
    return random_number


def generate_russian_string(length: int):
    """Генерация рандомной строки из length значений"""
    russian_letters = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
    return ''.join(random.choice(russian_letters) for _ in range(length))
