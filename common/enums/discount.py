from enum import StrEnum


class DiscountErrors(StrEnum):
    IncorrectDiscountPercentValue = "Значение должно быть от 0 до 100 включительно"
