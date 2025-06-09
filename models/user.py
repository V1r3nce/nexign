import datetime
from dataclasses import dataclass, field

from common.helpers.data_generator import (
    faker_ru,
    generate_random_number,
    get_current_datetime_string_for_api,
    get_shifted_datetime,
)
from models.address_info import BasicSystemAddress


@dataclass
class BaseClient:
    test_id: str = ""
    user_id: int = None
    agreement_id: int = None
    agreement_number: int = None
    account_id: int = None
    account_number: int = None

    date_for_api: str = get_current_datetime_string_for_api(is_full_format=False)

    inn: str = str(generate_random_number(12))
    contact_phone: str = faker_ru.phone_number()
    contact_email: str = faker_ru.email()
    registration_address: str = BasicSystemAddress.address
    tax_scheme: str = "НДС"
    nationality: str = "Россия"
    nationality_id: int = 1
    speaking_language: str = "Русский"
    speaking_language_id: int = 3
    bank_account: str = str(generate_random_number(20))
    bank_name: str = 'АО "Россельхозбанк", 044525111'
    operator_bank_details: str = "СЕВЕРО-ЗАПАДНЫЙ БАНК ПАО СБЕРБАНК, 40702840109998965649"

    issue_date: str = get_shifted_datetime("-500d").strftime("%d.%m.%Y")
    issue_date_for_api: str = datetime.datetime.strptime(issue_date, "%d.%m.%Y").strftime("%Y-%m-%d")

    is_resident: str = "Да"
    is_resident_bool: bool = True


@dataclass
class PersonClient(BaseClient):
    """Общий класс для физического лица и ИП"""

    start_date = datetime.date(1990, 1, 1)
    end_date = datetime.date(2020, 12, 31)
    patronymic: str = field(default_factory=lambda: faker_ru.middle_name())
    gender: str = "Мужской"
    gender_id: int = 1
    document_type: str = "Паспорт гражданина РФ"
    document_type_id: int = 5
    document_serial: str = str(generate_random_number(4))
    document_num: str = str(generate_random_number(6))
    document_division_code: str = f"{generate_random_number(3)}-{generate_random_number(3)}"
    document_provide_by: str = "ГУ МВД РОССИИ"

    document_date: str = faker_ru.date_between(start_date, end_date).strftime("%d.%m.%Y")
    document_valid_date: str = faker_ru.date_between(datetime.datetime.today(), get_shifted_datetime("+500d")).strftime(
        "%d.%m.%Y"
    )
    document_date_for_api: str = datetime.datetime.strptime(document_date, "%d.%m.%Y").strftime("%Y-%m-%d")
    document_valid_date_for_api: str = datetime.datetime.strptime(document_valid_date, "%d.%m.%Y").strftime("%Y-%m-%d")
    birth_date: str = faker_ru.date_of_birth(maximum_age=25).strftime("%d.%m.%Y")
    birth_date_for_api: str = datetime.datetime.strptime(birth_date, "%d.%m.%Y").strftime("%Y-%m-%d")
    # TODO(Sidorov A.) вернуть рандомную дату ДР после исправления бага https://jira.nexign.com/browse/TUDS-3486

    birth_place: str = faker_ru.city()
    snils: str = str(generate_random_number(11))
    is_public: str = "Нет"
    is_public_bool: bool = False


@dataclass
class EntrepreneurClient(PersonClient):
    sur_name: str = field(default_factory=lambda: f"ИП-автотесты-{faker_ru.last_name()}")
    first_name: str = field(default_factory=lambda: f"ИП-автотесты-{faker_ru.first_name()}")
    okpo: str = str(generate_random_number(10))
    okato: str = str(generate_random_number(10))
    okved: str = str(generate_random_number(10))
    ogrn: str = str(generate_random_number(15))
    note: str = faker_ru.pystr(min_chars=10, max_chars=10)
    proprietary_form: str = "ИП, Индивидуальный предприниматель"
    registration_document: str = str(generate_random_number(10))
    registration_date: str = faker_ru.date_between(PersonClient.start_date, PersonClient.end_date).strftime("%d.%m.%Y")

    reputation: str = "Автотестовая репутация"
    business_activity: str = "Агент"


@dataclass
class IndividualClient(PersonClient):
    sur_name: str = field(default_factory=lambda: f"ФЛ-автотесты-{faker_ru.last_name()}")
    first_name: str = field(default_factory=lambda: f"ФЛ-автотесты-{faker_ru.first_name()}")
    document_invalid_date: str = get_shifted_datetime("-1d").strftime("%d.%m.%Y")


@dataclass
class OrganizationClient(BaseClient):
    name_related_person: str = "ЮЛ Тестовое наименование"
    inn: str = str(generate_random_number(10))
    proprietary_form: str = "АО, Акционерное Общество"
    registration_date: str = faker_ru.date_between(PersonClient.start_date, PersonClient.end_date).strftime("%d.%m.%Y")
    registration_document: str = str(generate_random_number(10))
    registration_num: str = str(generate_random_number(6))
    okpo: str = str(generate_random_number(10))
    okato: str = str(generate_random_number(10))
    okved: str = str(generate_random_number(10))
    ogrn: str = str(generate_random_number(13))
    kpp: str = str(generate_random_number(9))
    note: str = faker_ru.pystr(min_chars=10, max_chars=10)
    customer_name: str = f"ЮЛ-Автотесты-{faker_ru.pystr(min_chars=10, max_chars=10)}"

    speaking_language: str = "Русский"
    business_activity: str = "Агент"
    reputation: str = "Автотестовая репутация"
    is_vip_bool: bool = False
