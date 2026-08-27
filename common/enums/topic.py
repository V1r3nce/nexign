from typing import Tuple

from common.enums.base_enums import CustomEnum


class BaseTopic(CustomEnum):
    def get_theme_code_and_name(self) -> Tuple[str, str]:
        theme_code = self.value.split(" ")[0].strip("()")
        theme_name = self.value.replace(self.value.split()[0], "").strip()
        return theme_code, theme_name


class InfoServiceTopic(BaseTopic):
    """Темы группы «Информационно-справочное обслуживание»."""

    Group = ("(1) 01 Информационно-справочное обслуживание", -1)
    AddInfoToRegisteredClaim = ("(101) Добавить информацию в ранее зарегистрированную претензию", 17)
    CloseRegisteredClaimByClient = ("(102) Закрытие зарегистрированной претензии по инициативе клиента", 36)


class SettlementServiceTopic(BaseTopic):
    """Темы группы «Расчетно-справочное обслуживание»."""

    Group = ("(2) 02 Расчетно-справочное обслуживание", -1)
    RefundOfFunds = ("(202) Возврат денежных средств", 25)
    ProvisionOfSettlementDocuments = ("(201) Предоставление Расчетно-платежных документов (РПД)", 2)
    DebtRestructuring = ("(203) Реструктуризация долга", 31)


class ClaimTopic(BaseTopic):
    """Темы группы «Претензия»."""

    Group = ("(3) 03 Претензия", -1)
    DisagreeWithCalculations = ("(301) Не согласен с расчетами", 12)
    PartnerReward = ("(302) Претензия по вознаграждения партнёра", 14)


class TechnicalSupportTopic(BaseTopic):
    """Темы группы «Техническая поддержка»."""

    Group = ("(4) 04 Техническая поддержка", -1)
    NoConnectionOrDataTransfer = (r"(401) Не устанавливается соединение\Не идет передача данных", 27)
    NoNetworkRegistration = ("(402) Нет регистрации в сети", 13)
    PartnerAccountAccessProblems = ("(403) Проблемы с доступом в ЛК партнёра", 15)


class ActionTopic(BaseTopic):
    """Темы группы «Действия»."""

    Group = ("(5) 05 Действия", -1)
    AgreementRenewal = ("(RENEWAL_AGREEMENT) Переоформление договора", -1)
    TransferProducts = ("(TRANSFER_PRODUCTS) Перенос продуктов на другие ЛС", 22)
    SaleTopicGrp = ("(SALE_TOPIC_GRP) Продажа", -1)
    SaleTopic = ("(SALE_TOPIC) Продажа и управление услугами", 26)
    AgreementTermination = ("(AGREEMENT_TERMINATION) Расторжение договора", 34)


class TestTopic(BaseTopic):
    """Темы группы «[TEST] Группа тем для тестирования»."""

    Group = ("(TEST_TOPIC_GROUP) [TEST] Группа тем для тестирования", -1)
    Date = ("(TEST_DATE) TEST_DATE", 4)
    UrlAttributeSupport = ("(TEST_RMBSS_15409) TEST_Поддержка в CPM доп.атрибута типа URL", 28)
    UrlAttributeSupportKeep = ("(TEST_ATTR_URL) TEST_Поддержка в CPM доп.атрибута типа URL. НЕ УДАЛЯТЬ!", 24)
    AttributesKeep = ("(TEST_ATTR) TEST_Тестирование атрибутов. НЕ УДАЛЯТЬ!", 29)
    SubscriberChangeKeep = ("(TEST_CHANGE_SUBSCRIPTION) TEST_проверка смены абонента. НЕ УДАЛЯТЬ!", 11)
    GroovyScriptSleep = ("(TEST_SCRIPT_SLEEP) [TEST] Groovy-script sleep() testing", 20)
    FilesCreation = ("(TEST_FILES) [TEST] Создание файлов", 30)
    GroovyLog = ("(TEST_GROOVY_LOG) [TEST] Тестирование логов", 7)
    Timer = ("(123) ТЕСТ_ТАЙМЕР", 8)
    AdditionalAttributes = ("(TEST_ATTRIBUTES) Тест доп. атрибутов", 3)
    TopicRule = ("(TEST_TOPIC_RULE) Тест_правила с атрибутами типа Oapi-справочник", 21)


class UmnpTopic(BaseTopic):
    """Темы группы «[UMNP] Перенос номеров в сетях подвижной связи»."""

    Group = ("(UMNP_TOPICS) [UMNP] Перенос номеров в сетях подвижной связи", -1)
    DonorGroup = ("(UMNP_DONOR) [UMNP] Донор", -1)
    DonorNumberCapacityReturn = ("(UMNP_DONOR_RETURN) [UMNP] Возврат номерной ёмкости (донор)", 35)
    DonorB2CTransfer = ("(UMNP_DONOR_B2C) [UMNP] Перенос номеров B2C (донор)", 16)
    RecipientGroup = ("(UMNP_RECIPIENT) [UMNP] Реципиент", -1)
    RecipientNumberCapacityReturn = ("(UMNP_RECIPIENT_RETURN) [UMNP] Возврат номерной ёмкости (реципиент)", 1)
    RecipientB2CTransfer = ("(UMNP_RECIPIENT_B2C) [UMNP] Перенос до 50 номеров B2C (реципиент)", 9)
