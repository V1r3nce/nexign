from enum import StrEnum


class InquiryStep(StrEnum):
    SearchBlockingEntities = "Поиск блокирующих сущностей"
    AutoAgreementAndAccountManagement = "Автоматическое управление Договором/ДС и ЛС"
    DocumentGenerationTechnicalStep = "Формирование документов (тех.шаг)"
    ManageProducts = "Управление продуктами"
    ControlCommercialOrderCheck = "Контрольная Проверка КЗ"
    SaleCompletion = "Завершение продажи"
    SaleCompletedSuccessfully = "Успешно выполнено"


class InquiryAddAgreementAdd(StrEnum):
    auto = "CREATE_AUTO"
    manual = "CREATE_MANUAL"


class InquiryAddAccount(StrEnum):
    auto = "AUTO"
    manual = "MANUAL"


class InquiryNeedSPD(StrEnum):
    not_create = "NOT_CREATE"
    auto = "CREATE_AUTO"


class InquiryApiSteps(StrEnum):
    agreement_step = "AGR_CHK_FEAS"
    account_step = "CREATE_USE_ACCOUNT"
    document_approval = "CREATE_DOCS_TECH"
    control_check_commercial_order = "CONTROL_CHECK_CO"
    clarifying_needs = "CLARIFYING_NEEDS_VERIFYING"
    technical_solution_verifying = "TECHNICAL_SOLUTION"
    sale_close = "SALE_CLOSE"
