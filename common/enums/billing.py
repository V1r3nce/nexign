from enum import Enum, StrEnum

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
    negative_bill = ("Отрицательная корректировка счета", 1)
    negative_bill_detail_included = ("Отрицательная корректировка детализации счета", 2)
    negative_payment = ("Отрицательная корректировка платежа", 3)
    positive_payment = ("Положительная корректировка платежа", 10)
    positive_target_detail = ("Положительная корректировка детали счета в текущем периоде", 13)
    negative_target_detail = ("Отрицательная корректировка детали счета в текущем периоде", 14)
    positive_bill_detail_included = ("Положительная корректировка значения детализации чека", 15)
    negative_invoice = ("Отрицательная корректировка счет-фактуры", 18)
    negative_invoice_string = ("Отрицательная корректировка строки счет-фактуры", 19)
    positive_invoice_string = ("Положительная корректировка строки счет-фактуры", 20)


class AdjustmentReason(CustomEnum):
    a = ("Отрицательная корректировка счета", 1)
    ("Отрицательная корректировка детали счета", 2)
    ("Корректировка платежа", 3)
    ("Положительная корректировка детали счета в текущем периоде", 18)


class BillingDetail(StrEnum):
    pass
