from enum import StrEnum


class InfoServiceTopic(StrEnum):
    """Темы группы «Информационно-справочное обслуживание»."""

    Group = "(1) 01 Информационно-справочное обслуживание"
    AddInfoToRegisteredClaim = "(101) Добавить информацию в ранее зарегистрированную претензию"
    CloseRegisteredClaimByClient = "(102) Закрытие зарегистрированной претензии по инициативе клиента"


class SettlementServiceTopic(StrEnum):
    """Темы группы «Расчетно-справочное обслуживание»."""

    Group = "(2) 02 Расчетно-справочное обслуживание"
    RefundOfFunds = "(202) Возврат денежных средств"
    ProvisionOfSettlementDocuments = "(201) Предоставление Расчетно-платежных документов (РПД)"
    DebtRestructuring = "(203) Реструктуризация долга"


class ClaimTopic(StrEnum):
    """Темы группы «Претензия»."""

    Group = "(3) 03 Претензия"
    DisagreeWithCalculations = "(301) Не согласен с расчетами"
    PartnerReward = "(302) Претензия по вознаграждения партнёра"


class TechnicalSupportTopic(StrEnum):
    """Темы группы «Техническая поддержка»."""

    Group = "(4) 04 Техническая поддержка"
    NoConnectionOrDataTransfer = r"(401) Не устанавливается соединение\Не идет передача данных"
    NoNetworkRegistration = "(402) Нет регистрации в сети"
    PartnerAccountAccessProblems = "(403) Проблемы с доступом в ЛК партнёра"


class ActionTopic(StrEnum):
    """Темы группы «Действия»."""

    Group = "(5) 05 Действия"
    AgreementRenewal = "(RENEWAL_AGREEMENT) Переоформление договора"
    Sale = "(SALE_TOPIC_GRP) Продажа"
    AgreementTermination = "(AGREEMENT_TERMINATION) Расторжение договора"


class TestTopic(StrEnum):
    """Темы группы «[TEST] Группа тем для тестирования»."""

    Group = "(TEST_TOPIC_GROUP) [TEST] Группа тем для тестирования"
    Date = "(TEST_DATE) TEST_DATE"
    Rmbss18918 = "(TEST_RMBSS_18918) TEST_RMBSS_18918 [TEST_RMBSS]"
    UrlAttributeSupport = "(TEST_RMBSS_15409) TEST_Поддержка в CPM доп.атрибута типа URL"
    UrlAttributeSupportKeep = "(TEST_ATTR_URL) TEST_Поддержка в CPM доп.атрибута типа URL. НЕ УДАЛЯТЬ!"
    AttributesKeep = "(TEST_ATTR) TEST_Тестирование атрибутов. НЕ УДАЛЯТЬ!"
    SubscriberChangeKeep = "(TEST_CHANGE_SUBSCRIPTION) TEST_проверка смены абонента. НЕ УДАЛЯТЬ!"
    GroovyScriptSleep = "(TEST_SCRIPT_SLEEP) [TEST] Groovy-script sleep() testing"
    FilesCreation = "(TEST_FILES) [TEST] Создание файлов"
    GroovyLog = "(TEST_GROOVY_LOG) [TEST] Тестирование логов"
    Timer = "(123) ТЕСТ_ТАЙМЕР"
    AdditionalAttributes = "(TEST_ATTRIBUTES) Тест доп. атрибутов"
    TopicRule = "(TEST_TOPIC_RULE) Тест_правила с атрибутами типа Oapi-справочник"


class UmnpTopic(StrEnum):
    """Темы группы «[UMNP] Перенос номеров в сетях подвижной связи»."""

    Group = "(UMNP_TOPICS) [UMNP] Перенос номеров в сетях подвижной связи"
    DonorGroup = "(UMNP_DONOR) [UMNP] Донор"
    DonorNumberCapacityReturn = "(UMNP_DONOR_RETURN) [UMNP] Возврат номерной ёмкости (донор)"
    DonorB2CTransfer = "(UMNP_DONOR_B2C) [UMNP] Перенос номеров B2C (донор)"
    RecipientGroup = "(UMNP_RECIPIENT) [UMNP] Реципиент"
    RecipientNumberCapacityReturn = "(UMNP_RECIPIENT_RETURN) [UMNP] Возврат номерной ёмкости (реципиент)"
    RecipientB2CTransfer = "(UMNP_RECIPIENT_B2C) [UMNP] Перенос до 50 номеров B2C (реципиент)"
