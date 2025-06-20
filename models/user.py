import datetime
import inspect
from dataclasses import asdict, dataclass, field
from functools import cached_property

from common.helpers.data_generator import (
    faker_ru,
    generate_random_number,
    get_current_datetime_string_for_api,
)
from common.helpers.time_helpers import get_shifted_datetime
from models.address_info import BasicSystemAddress


@dataclass
class BaseClient:
    def to_dict(self) -> dict:
        """Преобразует объект в словарь, включая все свойства (@cached_property)"""
        result = asdict(self)

        properties = {}
        for cls in inspect.getmro(type(self)):
            for name, prop in vars(cls).items():
                if isinstance(prop, property):
                    properties[name] = prop

        for name, prop in properties.items():
            result[name] = getattr(self, name)

        return result

    test_id: str = field(default_factory=lambda: "")
    user_id: int = field(default_factory=lambda: None)
    agreement_id: int = field(default_factory=lambda: None)
    agreement_number: int = field(default_factory=lambda: None)
    account_id: int = field(default_factory=lambda: None)
    account_number: int = field(default_factory=lambda: None)

    date_for_api: str = field(default_factory=lambda: get_current_datetime_string_for_api(is_full_format=False))

    inn: str = field(default_factory=lambda: str(generate_random_number(12)))
    contact_phone: str = field(default_factory=lambda: faker_ru.phone_number())
    contact_email: str = field(default_factory=lambda: faker_ru.email())
    registration_address: str = field(default_factory=lambda: BasicSystemAddress.address)
    tax_scheme: str = field(default_factory=lambda: "НДС")
    tax_scheme_id: int = field(default_factory=lambda: 1)
    nationality: str = field(default_factory=lambda: "Россия")
    nationality_id: int = field(default_factory=lambda: 1)
    speaking_language: str = field(default_factory=lambda: "Русский")
    speaking_language_id: int = field(default_factory=lambda: 3)
    bank_account: str = field(default_factory=lambda: str(generate_random_number(20)))
    bank_name: str = field(default_factory=lambda: 'АО "Россельхозбанк", 044525111')
    operator_bank_details: str = field(default_factory=lambda: "СЕВЕРО-ЗАПАДНЫЙ БАНК ПАО СБЕРБАНК, 40702840109998965649")

    @cached_property
    def issue_date(self) -> str:
        return get_shifted_datetime("-500d").strftime("%d.%m.%Y")

    @cached_property
    def issue_date_for_api(self) -> str:
        return datetime.datetime.strptime(self.issue_date, "%d.%m.%Y").strftime("%Y-%m-%d")

    is_resident: str = field(default_factory=lambda: "Да")
    is_resident_bool: bool = field(default_factory=lambda: True)


@dataclass
class PersonClient(BaseClient):
    """Общий класс для физического лица и ИП"""

    start_date = datetime.date(1990, 1, 1)
    end_date = datetime.date(2020, 12, 31)

    patronymic: str = field(default_factory=lambda: faker_ru.middle_name())
    gender: str = field(default_factory=lambda: "Мужской")
    gender_id: int = field(default_factory=lambda: 1)
    document_type: str = field(default_factory=lambda: "Паспорт гражданина РФ")
    document_type_id: int = field(default_factory=lambda: 5)
    document_serial: str = field(default_factory=lambda: str(generate_random_number(4)))
    document_num: str = field(default_factory=lambda: str(generate_random_number(6)))
    document_division_code: str = field(
        default_factory=lambda: f"{generate_random_number(3)}-{generate_random_number(3)}"
    )
    document_provide_by: str = field(default_factory=lambda: "ГУ МВД РОССИИ")

    @cached_property
    def document_date(self) -> str:
        return faker_ru.date_between(self.start_date, self.end_date).strftime("%d.%m.%Y")

    @cached_property
    def document_valid_date(self) -> str:
        return faker_ru.date_between(datetime.datetime.today(), get_shifted_datetime("+500d")).strftime("%d.%m.%Y")

    @cached_property
    def document_date_for_api(self) -> str:
        return datetime.datetime.strptime(self.document_date, "%d.%m.%Y").strftime("%Y-%m-%d")

    @cached_property
    def document_valid_date_for_api(self) -> str:
        return datetime.datetime.strptime(self.document_valid_date, "%d.%m.%Y").strftime("%Y-%m-%d")

    @cached_property
    def birth_date(self) -> str:
        return faker_ru.date_of_birth().strftime("%d.%m.%Y")

    @cached_property
    def birth_date_for_api(self) -> str:
        return datetime.datetime.strptime(self.birth_date, "%d.%m.%Y").strftime("%Y-%m-%d")

    birth_place: str = field(default_factory=lambda: faker_ru.city())
    snils: str = field(default_factory=lambda: str(generate_random_number(11)))
    is_public: str = field(default_factory=lambda: "Нет")
    is_public_bool: bool = field(default_factory=lambda: False)


@dataclass
class EntrepreneurClient(PersonClient):
    type: str = field(default_factory=lambda: "Индивидуальный предприниматель")
    sur_name: str = field(default_factory=lambda: f"ИП-автотесты-{faker_ru.last_name()}")
    first_name: str = field(default_factory=lambda: f"ИП-автотесты-{faker_ru.first_name()}")
    okpo: str = field(default_factory=lambda: str(generate_random_number(10)))
    okato: str = field(default_factory=lambda: str(generate_random_number(10)))
    okved: str = field(default_factory=lambda: str(generate_random_number(10)))
    ogrn: str = field(default_factory=lambda: str(generate_random_number(15)))
    note: str = field(default_factory=lambda: faker_ru.pystr(min_chars=10, max_chars=10))
    proprietary_form: str = field(default_factory=lambda: "ИП, Индивидуальный предприниматель")
    registration_document: str = field(default_factory=lambda: str(generate_random_number(10)))

    @cached_property
    def registration_date(self) -> str:
        return faker_ru.date_between(self.start_date, self.end_date).strftime("%d.%m.%Y")

    reputation: str = field(default_factory=lambda: "Автотестовая репутация")
    business_activity: str = field(default_factory=lambda: "Агент")


@dataclass
class IndividualClient(PersonClient):
    type: str = field(default_factory=lambda: "Физическое лицо")
    sur_name: str = field(default_factory=lambda: f"ФЛ-автотесты-{faker_ru.last_name()}")
    first_name: str = field(default_factory=lambda: f"ФЛ-автотесты-{faker_ru.first_name()}")

    @cached_property
    def document_invalid_date(self) -> str:
        return get_shifted_datetime("-1d").strftime("%d.%m.%Y")


@dataclass
class OrganizationClient(BaseClient):
    type: str = field(default_factory=lambda: "Юридическое лицо")
    name_related_person: str = field(default_factory=lambda: "ЮЛ Тестовое наименование")
    inn: str = field(default_factory=lambda: str(generate_random_number(10)))
    proprietary_form: str = field(default_factory=lambda: "АО, Акционерное Общество")

    @cached_property
    def registration_date(self) -> str:
        return faker_ru.date_between(PersonClient.start_date, PersonClient.end_date).strftime("%d.%m.%Y")

    registration_document: str = field(default_factory=lambda: str(generate_random_number(10)))
    registration_num: str = field(default_factory=lambda: str(generate_random_number(6)))
    okpo: str = field(default_factory=lambda: str(generate_random_number(10)))
    okato: str = field(default_factory=lambda: str(generate_random_number(10)))
    okved: str = field(default_factory=lambda: str(generate_random_number(10)))
    ogrn: str = field(default_factory=lambda: str(generate_random_number(13)))
    kpp: str = field(default_factory=lambda: str(generate_random_number(9)))
    note: str = field(default_factory=lambda: faker_ru.pystr(min_chars=10, max_chars=10))
    customer_name: str = field(default_factory=lambda: f"ЮЛ-Автотесты-{faker_ru.pystr(min_chars=10, max_chars=10)}")

    speaking_language: str = field(default_factory=lambda: "Русский")
    business_activity: str = field(default_factory=lambda: "Агент")
    reputation: str = field(default_factory=lambda: "Автотестовая репутация")
    is_vip_bool: bool = field(default_factory=lambda: False)
