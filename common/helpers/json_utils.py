from typing import Any

import json
from loguru import logger


def is_json(data: Any):
    if isinstance(data, bytes):
        return False
    try:
        json.loads(data)
    except (ValueError, TypeError):
        return False
    return True


def pretty_json(data: Any, default=None):
    try:
        if isinstance(data, bytes):
            data = data.decode("utf-8")
        if isinstance(data, str) and is_json(data):
            data = json.loads(data)
        return json.dumps(data, indent=4, ensure_ascii=False, default=default)
    except Exception as e:
        logger.info(
            f"Не удалось преобразовать данные в JSON. Тип данных: {type(data)}\n"
            f"Текст ошибки: {e}\n"
            f"Данные: {data}"
        )
        return data
