import re


def remove_parantheses(s: str) -> str:
    """
    Удаляет текст в круглых скобках вместе с самими скобками и удаляет лишние пробелы в начале, конце и между словами

    :param s - исходная строка
    :return - строка без текста в скобках и нормальными пробелами
    """
    result = re.sub(r'\s*\(.*?\)\s*', ' ', s).strip()
    return re.sub(r'\s+', ' ', result)


def get_price_and_currency(s: str) -> (float, str | None):
    """
    Получает из строки со стоимостью сумму и валюту (300.00 RUB/Месяц, 0.00 RUB и т.д.)

    :param s - исходная строка

    :return price - сумма абонентской платы/разового платежа
    :return currency - валюта абонентской платы/разового платежа
    """
    res = re.split(r'[\n/ ]+', s)
    price = float(res[0])
    currency = res[1] if len(res) > 1 else None
    return price, currency
