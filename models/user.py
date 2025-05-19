from dataclasses import dataclass

from common.helpers.data_generator import faker_ru, generate_random_number, get_shifted_datetime


@dataclass
class SearchUser:
    name: str = "Петр"
    surname: str = "Петров"
    inn: int = 444444444444


@dataclass
class EntrepreneurUser:
    last_name: str = f"автотесты-{faker_ru.last_name()}"
    first_name: str = f"автотесты-{faker_ru.first_name()}"
    document_serial: str = str(generate_random_number(4))
    document_num: str = str(generate_random_number(6))
    document_division_code: str = f"{generate_random_number(3)}-{generate_random_number(3)}"
    birth_date: str = faker_ru.date_of_birth().strftime("%d.%m.%Y")
    birth_place: str = faker_ru.city()
    inn: str = str(generate_random_number(12))
    snils: str = str(generate_random_number(11))
    contact_phone: str = faker_ru.phone_number()
    contact_email: str = faker_ru.email()
    okpo: str = str(generate_random_number(10))
    okato: str = str(generate_random_number(10))
    okved: str = str(generate_random_number(10))
    ogrn: str = str(generate_random_number(15))
    note: str = faker_ru.pystr(min_chars=10, max_chars=10)


@dataclass
class IndividualUser:
    last_name: str = f"автотесты-{faker_ru.last_name()}"
    first_name: str = f"автотесты-{faker_ru.first_name()}"
    document_serial: str = str(generate_random_number(4))
    document_num: str = str(generate_random_number(6))
    document_division_code: str = f"{generate_random_number(3)}-{generate_random_number(3)}"
    document_invalid_date: str = get_shifted_datetime("-1d").strftime("%d.%m.%Y")
    birth_date: str = faker_ru.date_of_birth(maximum_age=25).strftime("%d.%m.%Y")
    birth_place: str = faker_ru.city()
    inn: str = str(generate_random_number(12))
    snils: str = str(generate_random_number(11))
    contact_phone: str = faker_ru.phone_number()
    contact_email: str = faker_ru.email()


@dataclass
class OrgUser:
    inn: str = str(generate_random_number(10))
    registration_document: str = str(generate_random_number(10))
    registration_num: str = str(generate_random_number(6))
    okpo: str = str(generate_random_number(10))
    okato: str = str(generate_random_number(10))
    okved: str = str(generate_random_number(10))
    ogrn: str = str(generate_random_number(13))
    kpp: str = str(generate_random_number(9))
    note: str = faker_ru.pystr(min_chars=10, max_chars=10)
    customer_name: str = f"Autotest_{faker_ru.pystr(min_chars=10, max_chars=10)}"
    contact_phone: str = faker_ru.phone_number()
    contact_email: str = faker_ru.email()
