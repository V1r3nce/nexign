from enum import StrEnum


class Constants:
    DEFAULT_TIMEOUT: int = 10000
    DEFAULT_TIMEOUT_SECONDS: int = 10
    LIS_RETRY_DELAY = 15
    LIS_RETRY_EXCEPTIONS = (AssertionError,)


class Title(StrEnum):
    default = "Nexign"
