from enum import StrEnum
from functools import lru_cache


class Services(StrEnum):
    gsm_access = "Доступ к сети GSM"
    incoming_communication = "Входящая связь"
    outgoing_communication = "Исходящая связь"
    call_forwarding = "Переадресация вызова"
    sms = "SMS"
    mms = "MMS"
    mobile_internet = "Мобильный интернет"
    caller_id = "Определитель номера (АОН)"
    conference_call = "Конференц-связь"
    call_hold = "Удержание вызова"

    @classmethod
    @lru_cache(maxsize=1)
    def mobile_services(cls) -> list:
        return [cls.gsm_access, cls.incoming_communication, cls.outgoing_communication, cls.sms, cls.mobile_internet]
