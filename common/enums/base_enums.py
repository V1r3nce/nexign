from enum import StrEnum
from typing import Any, Iterator


class CustomEnum(StrEnum):
    def __new__(cls, name: str, obj_id: int) -> str:
        obj = str.__new__(cls, name)
        obj._value_ = name
        obj.id = obj_id
        return obj


class ListableEnum:
    @classmethod
    def as_list(cls) -> list[str]:
        return [member.value for member in cls]


class SmartConstant:
    """
    Контейнер для констант.
    Работает как массив строк для 'in' и 'for',
    но ведет себя как одиночная строка при выводе и вызове строковых методов.
    """

    def __init__(self, values: str | bytes | list[str] | list[bytes]) -> None:
        if isinstance(values, (str, bytes)) or not hasattr(values, "__iter__"):
            self._all_values = (str(values),)
        else:
            self._all_values = tuple(str(v) for v in values)

    @property
    def _first(self) -> str:
        return self._all_values[0] if self._all_values else ""

    def __contains__(self, item: str) -> bool:
        return item in self._all_values

    def __iter__(self) -> Iterator[str]:
        return iter(self._all_values)

    def __len__(self) -> int:
        return len(self._all_values)

    def __getitem__(self, index: int) -> str:
        return self._all_values[index]

    def __repr__(self) -> str:
        return repr(self._first)

    def __str__(self) -> str:
        return self._first

    def __eq__(self, other: str) -> bool:
        return self._first == other or self._all_values == other

    def __getattr__(self, name: str) -> str:
        return getattr(self._first, name)


class RegistryMeta(type):
    """Метакласс для автоматического создания SmartConstant из полей класса"""

    def __init__(cls, name: str, bases: tuple[type, ...], dct: dict[str, Any]) -> None:
        super().__init__(name, bases, dct)
        for key, value in dct.items():
            if not key.startswith("__") and not callable(value):
                setattr(cls, key, SmartConstant(value))


class ImmutableRegistry(metaclass=RegistryMeta):
    """Базовый класс для текстовых констант"""

    pass
