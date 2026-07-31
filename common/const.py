from enum import StrEnum


class Constants:
    AUTOMATION_USER_AGENT: str = "automation"
    DEFAULT_TIMEOUT: int = 10000
    DEFAULT_TIMEOUT_SECONDS: int = 10


class Title(StrEnum):
    default = "Nexign"
