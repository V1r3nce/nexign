from enum import StrEnum


class InquiryStep(StrEnum):
    SearchBlockingEntities = "Поиск блокирующих сущностей"
    AutoAgreementAndAccountManagement = "Автоматическое управление Договором/ДС и ЛС"
    DocumentGenerationTechnicalStep = "Формирование документов (тех.шаг)"
    ManageProducts = "Управление продуктами"
    ControlCommercialOrderCheck = "Контрольная Проверка КЗ"
    SaleCompletion = "Завершение продажи"
    SaleCompletedSuccessfully = "Успешно выполнено"
