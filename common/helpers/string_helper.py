import base64
import re
from typing import Any
from unicodedata import normalize


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


def convert_string_to_base64(income_data: str) -> str:
    """Переводит строку в формат base64"""
    encoded_auth = income_data.encode("utf-8")
    base64_outcome = base64.b64encode(encoded_auth).decode("utf-8")
    return base64_outcome


def balance_parse(locator_text: str) -> float:
    return float(normalize("NFKD", locator_text.split(" RUB")[0]).replace(" ", ""))


def sim_price_parse(locator_text: str) -> float:
    return float(locator_text.split("Стоимость: ")[1].split(" RUB")[0])
