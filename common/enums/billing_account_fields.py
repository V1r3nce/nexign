from enum import StrEnum


class BillingAccountFields(StrEnum):
    billing_category = "Категория биллинга"
    payment_due_date = "Срок оплаты"
    period = "Период"
    payment_amount = "Итого к оплате"
    related_inquiries = "Связанные заявки"
    is_restructuring = "Реструктуризация"
    in_balance = "Входящий баланс"
    out_balance = "Исходящий баланс"
    paid_amount = "Оплачено"
    accounted_additional_charges = "Учтено доначислений"
    charges_adjusted = "Откорректировано начислений"
    payments_adjusted = "Откорректировано платежей"
    accounted_billing_discounts = "Учтено биллинговых скидок"
    accounted_charges = "Учтено начислений"
    accounted_payments = "Учтено платежей"
    accounted_product_discounts = "Учтено продуктовых скидок"
    accounted_payment_adjustments = "Учтено корректировок платежей"
    accounted_charge_adjustments = "Учтено корректировок начислений"
    account_type = "Тип счета"
    generation_date = "Дата генерации"
