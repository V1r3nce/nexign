import json
from typing import Any, Callable

from loguru import logger


def is_json(data: Any) -> bool:
    if isinstance(data, bytes):
        return False
    try:
        json.loads(data)
    except (ValueError, TypeError):
        return False
    return True


def bytes_encoder(obj: Any) -> str:
    if isinstance(obj, bytes):
        try:
            return obj.decode("utf-8")
        except UnicodeDecodeError:
            return f"<bytes: {obj.hex()}>"
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def pretty_json(data: Any, default: Callable = bytes_encoder) -> str:
    try:
        if isinstance(data, bytes):
            data = data.decode("utf-8")
        if isinstance(data, str) and is_json(data):
            data = json.loads(data)
        return json.dumps(data, indent=4, ensure_ascii=False, default=default)
    except Exception as e:
        logger.info(
            f"Не удалось преобразовать данные в JSON. Тип данных: {type(data)}\nТекст ошибки: {e}\nДанные: {data}"
        )
        return data


def find_object_by_inner_value(objects: list[dict], key: str, value: str) -> dict:
    """Найти первый элемент json, где items[*][key] == value."""
    result = next((item for item in objects if item.get(key) == value), None)
    if result is None:
        raise ValueError(f"Не найден объект с {key}={value}")
    return result
