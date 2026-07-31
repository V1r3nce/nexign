import base64
import re
from datetime import datetime, timedelta
from typing import Any
from unicodedata import normalize

import allure

from common.helpers.checker import assert_that
from common.helpers.time_helpers import get_datetime_from_string
from pages.ui_elements import Element


def remove_parantheses(s: str) -> str:
    """
    Удаляет текст в круглых скобках вместе с самими скобками и удаляет лишние пробелы в начале, конце и между словами

    :param s - исходная строка
    :return - строка без текста в скобках и нормальными пробелами
    """
    result = re.sub(r"\s*\(.*?\)\s*", " ", s).strip()
    return re.sub(r"\s+", " ", result)


def get_price_and_currency(s: str) -> tuple[float, str | Any | None]:
    """
    Получает из строки со стоимостью сумму и валюту (300.00 RUB/Месяц, 0.00 RUB и т.д.)

    :param s - исходная строка

    :return price - сумма абонентской платы/разового платежа
    :return currency - валюта абонентской платы/разового платежа
    """
    res = re.split(r"[\n/]+", s)[0].replace("\xa0", "").replace("\u2009", "").replace(" ", "")
    try:
        return float(res), None
    except ValueError:
        if s.strip() == "—":
            return 0, None
        price = float(res[:-4])
        currency = res[-3:]
        return price, currency


def extract_volumes(volumes: str) -> tuple[int, int]:
    pattern = r"([\d\s]+)\s*из\s*([\d\s]+)"
    match = re.search(pattern, volumes, flags=re.IGNORECASE)
    volume, max_volume = match.groups()
    return int(remove_all_whitespaces(volume)), int(remove_all_whitespaces(max_volume))


def extract_volume_in_inquiry(volume: str) -> int:
    return int(remove_all_whitespaces(volume.split(" ")[0]))


def convert_amount_to_balance_string(amount: float) -> str:
    """
    Функция для получения строкового представления баланса из числа с плавающей точкой.
    Например, 1235 -> 1 234.00, 344.0 -> 344.00, 1235123.0 -> 1 235 123.00
    :param amount: число с плавающей точкой
    :return: строковое представление
    """
    formatted_amount = f"{abs(amount):,.2f}"

    formatted_amount = formatted_amount.replace(",", " ")

    if amount < 0:
        formatted_amount = "-" + formatted_amount

    return formatted_amount


@allure.step("Преобразовать число {value} в строку с разделителем '{separator}' между разрядами")
def add_separators(value: int, separator: str = " ") -> str:
    """
    Пример:
    value: 5463758647, separator: "-" => return: 5-463-758-647
    value: 1234 => return: 1 234
    """
    return f"{value:,}".replace(",", separator)


@allure.step("Проверить, что сумма в '{element_with_price}' равна {expected_price}")
def check_price(element_with_price: Element, expected_price: float, check_format: bool = True) -> None:
    value = get_price_and_currency(element_with_price.text)[0]
    tolerance = abs(value * 0.00001)
    assert_that(
        lambda: expected_price - value <= tolerance,
        f"Значение '{element_with_price.locator_name}' равно {value}, ожидалось {expected_price}",
    )
    if check_format:
        element_with_price.wait_to_have_text(re.compile(r"\d+\.\d{2}"))


@allure.step("Проверить, что дата в '{element_with_date}' больше {expected_datetime} не больше чем на {diff} с")
def check_that_date_later(element_with_date: Element, expected_datetime: datetime, diff: int) -> None:
    current_datetime = get_datetime_from_string(element_with_date.text)
    assert_that(
        lambda: current_datetime - expected_datetime <= timedelta(seconds=diff),
        f"Значение '{element_with_date.locator_name}' отличается более чем на {diff} секунд",
    )


def convert_string_to_base64(income_data: str) -> str:
    """Переводит строку в формат base64"""
    encoded_auth = income_data.encode("utf-8")
    base64_outcome = base64.b64encode(encoded_auth).decode("utf-8")
    return base64_outcome


def balance_parse(locator_text: str) -> float:
    return float(normalize("NFKD", locator_text.split(" RUB")[0]).replace(" ", ""))


def sim_price_parse(locator_text: str) -> float:
    return float(locator_text.split("Стоимость: ")[1].split(" RUB")[0])


def clean_text_from_ansi(text: str) -> str:
    """
    Метод для очистки строки от ANSI символов
    :param text: неочищенный текст
    :return: очищенный текст
    """
    return re.sub(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", text)


def remove_line_breaks_and_spaces(text: str) -> str:
    return text.replace("\n", "").replace(" ", "")


def remove_all_whitespaces(text: str) -> str:
    return "".join(ch for ch in text if not ch.isspace())
