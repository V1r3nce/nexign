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
    res = re.split(r"[\n/]+", s)[0].replace("\xa0", "")
    try:
        return float(res), None
    except ValueError:
        price = float(res[:-4])
        currency = res[-3:]
        return price, currency


@allure.step("Преобразовать число {value} в строку с разделителем '{separator}' между разрядами")
def add_separators(value: int, separator: str = " ") -> str:
    """
    Пример:
    value: 5463758647, separator: "-" => return: 5-463-758-647
    value: 1234 => return: 1 234
    """
    return f"{value:,}".replace(",", separator)


@allure.step("Проверить, что сумма в '{element_with_price}' равна {expected_price}")
def check_price(element_with_price: Element, expected_price: float) -> None:
    value = get_price_and_currency(element_with_price.text)[0]
    assert_that(
        lambda: expected_price == value,
        f"Значение '{element_with_price.locator_name}' равно {value}, ожидалось {expected_price}",
    )
    element_with_price.wait_to_have_text(re.compile(r"\d+\.\d{2}"))


@allure.step("Проверить, что дата в '{element_with_date}' больше {expected_datetime} не больше чем на {diff} с")
def check_that_date_later(element_with_date: Element, expected_datetime: datetime, diff: int) -> None:
    current_datetime = get_datetime_from_string(element_with_date.text)
    assert_that(
        lambda: current_datetime - expected_datetime < timedelta(seconds=diff),
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
