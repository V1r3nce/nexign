from enum import StrEnum

from common.enums.base_enums import CustomEnum


class InquiryStep(StrEnum):
    SearchBlockingEntities = "Поиск блокирующих сущностей"
    AutoAgreementAndAccountManagement = "Автоматическое управление Договором/ДС и ЛС"
    DocumentGenerationTechnicalStep = "Формирование документов (тех.шаг)"
    ManageProducts = "Управление продуктами"
    ControlCommercialOrderCheck = "Контрольная Проверка КЗ"
    SaleCompletion = "Завершение продажи"
    SaleCompletedSuccessfully = "Успешно выполнено"
    FormingAndApprovalCommercialOffer = "Формирование и согласование документа КП"
    CheckingPossibilityConcludingAgreement = "Проверка возможности заключения договора"
    ManageOrderStructure = "Управление составом заказа"


class InquiryTab(StrEnum):
    ActiveStep = "Активный шаг"
    OrderItems = "Элементы заказа"
    SaleCard = "Карточка продажи"
    Overview = "Обзор"
    ContactData = "Контактные данные"
    TechnicalOrders = "Технические заказы"
    CurrentState = "Текущее состояние"
    ProcessingHistory = "История обработки"
    Documents = "Документы"


class InquiryDocumentFormationMode(StrEnum):
    CreateAuto = "Сформировать, факт согласования автоматически"
    CreateManual = "Сформировать, факт согласования вручную"
    NotCreate = "Не формировать"


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


class InquiryEventResultCodes(StrEnum):
    success = "EXEC_COMPLETED"
    error = "EXEC_ERROR"
    requirements_failed = "REQUIREMENTS_FAILED"
    executing = "EXECUTING"
    waiting = "WAITING"


class InquiryEventStates(CustomEnum):
    done = ("Обработка завершена", 4)


class TechnicalOrderStageCodes(StrEnum):
    technical_solution = "TECHNICAL_SOLUTION"
    service_organization = "SERVICE_ORGANIZATION"
    completed = "COMPLETED"
