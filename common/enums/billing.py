from enum import Enum

from common.enums.base_enums import FloatEnum


class DiscountTemplateAction(Enum):
    """Тип действия с шаблоном биллинговой скидки в истории изменений (dsc_bill_discount_templates_history)."""

    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class TaxPercent(FloatEnum):
    """Ставка налога на добавленную стоимость"""

    default_percent = 22.0
