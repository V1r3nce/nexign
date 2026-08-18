from enum import Enum

from common.enums.base_enums import CustomEnum, FloatEnum


class DiscountTemplateAction(Enum):
    """Тип действия с шаблоном биллинговой скидки в истории изменений (dsc_bill_discount_templates_history)."""

    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class TaxPercent(FloatEnum):
    """Ставка налога на добавленную стоимость"""

    default_percent = 22.0


class BillingStatus(CustomEnum):
    successful = ("Полностью реализован", 4)


class AdjustmentType(CustomEnum):
    payment_negative = ("Отрицательная корректировка платежа", 3)
    payment_positive = ("Положительная корректировка платежа", 13)


class AdjustmentReason(CustomEnum):
    pass
