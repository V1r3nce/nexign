from enum import Enum


class DiscountTemplateAction(Enum):
    """Тип действия с шаблоном биллинговой скидки в истории изменений (dsc_bill_discount_templates_history)."""

    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
