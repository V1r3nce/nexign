import random


def generate_random_number(num_digits: int):
    start = 10 ** (num_digits - 1)
    end = 10 ** num_digits - 1
    random_number = random.randint(start, end)
    return random_number
