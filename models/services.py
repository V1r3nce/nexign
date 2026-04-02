from dataclasses import dataclass


@dataclass
class Services:
    gsm_access: str = "Доступ к сети GSM"
    incoming_communication: str = "Входящая связь"
    outgoing_communication: str = "Исходящая связь"
    call_forwarding: str = "Переадресация вызова"
    sms: str = "SMS"
    mms: str = "MMS"
    mobile_internet: str = "Мобильный интернет"
    caller_id: str = "Определитель номера (АОН)"
    conference_call: str = "Конференц-связь"
    call_hold: str = "Удержание вызова"

    @property
    def set(self) -> set:
        service_names = {service_name for service_field, service_name in self.__dict__.items()}
        return service_names
