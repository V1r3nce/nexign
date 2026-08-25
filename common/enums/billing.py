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


class BillingDetail(CustomEnum):
    fee_for_providing_access_to_network = ("Абон. плата за предоставление доступа к сети оператора и в интернет", 100015)
    fee_for_vlan = ("Абон. плата за VLAN", 100055)
    fee_flex_mobile_mini = ("Абон. плата за Гибкий бизнес мини с цветом номера - обычный", 100088)
    fee_mobile = ("Абон. плата за мобильную связь с цветом номера - обычный", 100007)
