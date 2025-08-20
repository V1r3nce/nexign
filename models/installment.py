from dataclasses import dataclass


@dataclass
class InstallmentTypeStatusMap:
    map = {
        "default": "Действующая",
        "cancel": "Аннулирована",
        "init_payment": "Ожидание первоначального платежа",
        "draft": "Черновик",
        "partially_paid": "Частично оплачена",
        "paid": "Оплачена",
    }
