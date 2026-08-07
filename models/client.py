import datetime
import inspect
import json
from dataclasses import asdict, dataclass, field
from functools import cached_property

import allure

from common.enums.ats import PersonalAccountPaymentMethod, TaxScheme
from common.helpers.data_generator import (
    faker,
    generate_random_number,
    get_current_datetime_string_for_api,
)
from common.helpers.time_helpers import get_shifted_datetime
from models.address_info import BasicSystemAddress
from models.inquiry import InquiryInfo, prepare_inquiries
from models.lis_resources import APNInfo


@dataclass
class Account:
    id: int = field(default_factory=lambda: None)
    number: int = field(default_factory=lambda: None)
    type_id: int = field(default_factory=lambda: None)
    rating_type: int = field(default_factory=lambda: None)
    currency_id: int = field(default_factory=lambda: None)
    threshold_break: int = field(default_factory=lambda: None)
    threshold_control: bool = field(default_factory=lambda: False)
    is_cash_payment_enabled: bool = field(default_factory=lambda: True)


@dataclass
class Agreement:
    id: int = field(default_factory=lambda: None)
    number: str = field(default_factory=lambda: None)
    accounts: list[Account] = field(default_factory=list)

    def __getattribute__(self, name: str) -> object:
        """По умолчанию account - первый элемент списка accounts."""
        if name == "account":
            accounts = super().__getattribute__("accounts")
            if accounts:
                return accounts[0]
        return super().__getattribute__(name)

    def add_account(
        self,
        account_id: int,
        number: int,
        type_id: int = 1,
        rating_type: int = PersonalAccountPaymentMethod.prepaid.id,
        currency_id: int = 1,
        threshold_break: int = 0,
        threshold_control: bool = False,
        is_cash_payment_enabled: bool = True,
    ) -> None:
        """Метод добавляет информацию о лицевом счете для договора"""
        if account_id not in [account.id for account in self.accounts]:
            account = Account(
                id=account_id,
                number=number,
                type_id=type_id,
                rating_type=rating_type,
                currency_id=currency_id,
                threshold_break=threshold_break,
                threshold_control=threshold_control,
                is_cash_payment_enabled=is_cash_payment_enabled,
            )
            self.accounts.append(account)


@dataclass
class BaseClient:
    """
    Базовый класс для клиента.
    :param inquiry: это текущая заявка (поинтер), с которой работает тест. По умолчанию это первый элемент inquiry_list.
    :param inquiry_list: - список заявок. Для работы с одной из заявок, переключается поинтер inquiry на нужный из списка.
    """

    inquiry: InquiryInfo | None = field(default_factory=lambda: None)
    inquiry_list: list[InquiryInfo] = field(
        default_factory=lambda: prepare_inquiries(["mobile"]),  # type: ignore
        metadata={"description": "По умолчанию создается заявка с продуктом категории 'mobile'"},
    )

    def __getattribute__(self, name: str) -> object:
        """По умолчанию inquiry(agreement) - первый элемент списка inquiry_list(agreements)."""
        if name == "inquiry":
            inquiry = super().__getattribute__("inquiry")
            inquiry_list = super().__getattribute__("inquiry_list")
            if inquiry is None and inquiry_list:
                return inquiry_list[0]
        if name == "agreement":
            agreements = super().__getattribute__("agreements")
            if agreements:
                return agreements[0]
        return super().__getattribute__(name)

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

    def add_agreement(
        self,
        agreement_id: int,
        number: str,
    ) -> None:
        """Метод добавляет информацию о договоре для клиента"""
        if agreement_id not in [agreement.id for agreement in self.inquiry_list]:
            agreement = Agreement(id=agreement_id, number=number)
            self.agreements.append(agreement)

    def get_agreement(self, agreement_id: int | None = None, agreement_number: int | None = None) -> Agreement | None:
        """
        Метод возвращает объект договора, полученный по id или номеру договора
        Если id и номер договора не заданы, возвращает первый созданный договор на клиенте
        """
        if agreement_id:
            for agreement in self.agreements:
                if agreement.id == agreement_id:
                    return agreement
        elif agreement_number:
            for agreement in self.agreements:
                if agreement.number == agreement_number:
                    return agreement  # type: ignore
        else:
            return self.agreements[0]
        return None

    user_id: int = field(default_factory=lambda: None)
    agreements: list[Agreement] = field(default_factory=list)

    date_for_api: str = field(default_factory=lambda: get_current_datetime_string_for_api(is_full_format=False))

    inn: str = field(default_factory=lambda: str(generate_random_number(12)))
    contact_phone: str = field(default_factory=lambda: faker.phone_number_russian())
    contact_phone_code: str = field(default_factory=lambda: "+7")
    contact_phone_type: str = field(default_factory=lambda: "Сотовый")
    contact_email: str = field(default_factory=lambda: faker.email())
    registration_address: str = field(default_factory=lambda: BasicSystemAddress.address)
    external_address_id: int = field(default_factory=lambda: BasicSystemAddress.external_address_id)
    tax_scheme: str = field(default_factory=lambda: TaxScheme.default_scheme)
    tax_scheme_id: int = field(default_factory=lambda: 1)
    tax_scheme_type: str = field(default_factory=lambda: "DICTIONARY")
    nationality: str = field(default_factory=lambda: "Россия")
    nationality_id: int = field(default_factory=lambda: 1)
    speaking_language: str = field(default_factory=lambda: "Русский")
    speaking_language_id: int = field(default_factory=lambda: 3)
    bank_account: str = field(default_factory=lambda: str(generate_random_number(20)))
    bank_id: int = field(default_factory=lambda: 1)
    bank_name: str = field(
        default_factory=lambda: "Северо-Западный Банк ОАО «Сбербанк России» г. Санкт-Петербург, 044525225"
    )
    operator_bank_details: str = field(
        default_factory=lambda: 'Публичное акционерное общество "Сбербанк России", 40702810600020000500'
    )
    operator_name: str = field(default_factory=lambda: "Иванов Иван Иванович")
    apn: APNInfo | None = field(default_factory=lambda: None)
    linked_person_name: str = field(default_factory=lambda: f"{faker.last_name()} {faker.first_name()}")
    linked_person_phone: str = field(default_factory=lambda: f"+7{faker.phone_number_russian()}")
    contact_person: str = field(default_factory=lambda: f"{faker.last_name()} {faker.first_name()}")

    @property
    def operator_first_name(self) -> str:
        parts = (self.operator_name or "").split()
        if not parts:
            return ""
        if len(parts) == 1:
            return parts[0]
        if len(parts) == 2:
            return parts[1]
        return parts[-2]

    @property
    def operator_surname(self) -> str:
        parts = (self.operator_name or "").split()
        if not parts:
            return ""
        if len(parts) == 1:
            return parts[0]
        return parts[-1]

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

    patronymic: str = field(default_factory=lambda: faker.middle_name())
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
        return faker.date_between(self.start_date, self.end_date).strftime("%d.%m.%Y")

    @cached_property
    def document_valid_date(self) -> str:
        issue_dt = datetime.datetime.strptime(self.document_date, "%d.%m.%Y").date()
        start = max(issue_dt + datetime.timedelta(days=1), get_shifted_datetime("+1d").date())
        end = max(issue_dt + datetime.timedelta(days=500), get_shifted_datetime("+500d").date())
        return faker.date_between(start, end).strftime("%d.%m.%Y")

    @cached_property
    def document_date_for_api(self) -> str:
        return datetime.datetime.strptime(self.document_date, "%d.%m.%Y").strftime("%Y-%m-%d")

    @cached_property
    def document_valid_date_for_api(self) -> str:
        return datetime.datetime.strptime(self.document_valid_date, "%d.%m.%Y").strftime("%Y-%m-%d")

    @cached_property
    def birth_date(self) -> str:
        return faker.date_of_birth().strftime("%d.%m.%Y")

    @cached_property
    def birth_date_for_api(self) -> str:
        return datetime.datetime.strptime(self.birth_date, "%d.%m.%Y").strftime("%Y-%m-%d")

    birth_place: str = field(default_factory=lambda: faker.city())
    snils: str = field(default_factory=lambda: str(generate_random_number(11)))
    is_public: str = field(default_factory=lambda: "Нет")
    is_public_bool: bool = field(default_factory=lambda: False)


@dataclass
class EntrepreneurClient(PersonClient):
    category: str = field(default_factory=lambda: "b2b")
    type: str = field(default_factory=lambda: "Индивидуальный предприниматель")
    sur_name: str = field(default_factory=lambda: f"ИП-автотесты-{faker.last_name()}")
    first_name: str = field(default_factory=lambda: f"ИП-автотесты-{faker.first_name()}")
    okpo: str = field(default_factory=lambda: str(generate_random_number(10)))
    okato: str = field(default_factory=lambda: str(generate_random_number(10)))
    okved: str = field(default_factory=lambda: str(generate_random_number(10)))
    ogrn: str = field(default_factory=lambda: str(generate_random_number(15)))
    note: str = field(default_factory=lambda: faker.pystr(min_chars=10, max_chars=10))
    proprietary_form: str = field(default_factory=lambda: "ИП, Индивидуальный предприниматель")
    proprietary_form_id: int = field(default_factory=lambda: 34)
    registration_document: str = field(default_factory=lambda: str(generate_random_number(10)))

    @cached_property
    def registration_date(self) -> str:
        return faker.date_between(self.start_date, self.end_date).strftime("%d.%m.%Y")

    reputation: str = field(default_factory=lambda: "Автотестовая репутация")
    business_activity: str = field(default_factory=lambda: "Агент")


@dataclass
class IndividualClient(PersonClient):
    category: str = field(default_factory=lambda: "b2c")
    type: str = field(default_factory=lambda: "Физическое лицо")
    sur_name: str = field(default_factory=lambda: f"ФЛ-автотесты-{faker.last_name()}")
    first_name: str = field(default_factory=lambda: f"ФЛ-автотесты-{faker.first_name()}")

    @cached_property
    def document_invalid_date(self) -> str:
        return get_shifted_datetime("-1d").strftime("%d.%m.%Y")


@dataclass
class OrganizationClient(BaseClient):
    category: str = field(default_factory=lambda: "b2b")
    type: str = field(default_factory=lambda: "Юридическое лицо")
    name_related_person: str = field(default_factory=lambda: "ЮЛ Тестовое наименование")
    inn: str = field(default_factory=lambda: str(generate_random_number(10)))
    proprietary_form: str = field(default_factory=lambda: "АО, Акционерное Общество")
    proprietary_form_id: int = field(default_factory=lambda: 1)

    @cached_property
    def registration_date(self) -> str:
        return faker.date_between(PersonClient.start_date, PersonClient.end_date).strftime("%d.%m.%Y")

    registration_document: str = field(default_factory=lambda: str(generate_random_number(10)))
    registration_num: str = field(default_factory=lambda: str(generate_random_number(6)))
    okpo: str = field(default_factory=lambda: str(generate_random_number(8)))
    okato: str = field(default_factory=lambda: str(generate_random_number(10)))
    okved: str = field(default_factory=lambda: str(generate_random_number(10)))
    ogrn: str = field(default_factory=lambda: faker.ogrn())
    kpp: str = field(default_factory=lambda: str(generate_random_number(9)))
    note: str = field(default_factory=lambda: faker.pystr(min_chars=10, max_chars=10))
    customer_name: str = field(default_factory=lambda: f"ЮЛ-Автотесты-{faker.pystr(min_chars=10, max_chars=10)}")

    speaking_language: str = field(default_factory=lambda: "Русский")
    business_activity: str = field(default_factory=lambda: "Агент")
    reputation: str = field(default_factory=lambda: "Автотестовая репутация")
    is_vip_bool: bool = field(default_factory=lambda: False)
    auth_code: int = field(default_factory=lambda: generate_random_number(4))
    auth_code_type: str = field(default_factory=lambda: "VARCHAR")


@dataclass
class PaymentInfo:
    """
    Класс данных платежа

    item_type (str): тип цели платежа (CUSTOMER_ACCOUNT, PARTNER_ACCOUNT, AGREEMENT, PHONE_NUMBER, ICCID)
    amount (float): сумма платежа
    currency_code (str): код валюты (USD, EUR, и т.д.)
    account_id (int): id цели платежа
    document_number (int): номер документа, должен быть уникальным в системе
    point_id (int): идентификатор кассы (1 - voucher, 2 - uniblp, 3 - PNXL1, 4 - PNXL2, 5 - PNXUSD1, 6 - PNXUSD2)
    payment_date (str): дата когда произведён платеж
    payment_method_type (str): тип метода оплаты (CASH, BANK_CARD, PAYPAL, BANK_ACCOUNT_TRANSFER)
    phone_number (str): номер телефона абонента или номер договора абонента для услуги интернет
    """

    item_type: str = "CUSTOMER_ACCOUNT"
    amount: float = 0
    currency_code: str = "RUB"
    account_id: int = 0
    document_number: int | None = field(default_factory=lambda: generate_random_number(8))
    point_id: int = 3
    payment_method_type: str = "CASH"
    phone_number: str = ""
    payment_date: str = ""


def generate_individual_client() -> IndividualClient:
    with allure.step("Генерация нового пользователя типа ФЛ"):
        client = IndividualClient()
        allure.attach(
            str(json.dumps(client.to_dict(), indent=2, ensure_ascii=False)),
            name="individual_client_info",
            attachment_type=allure.attachment_type.JSON,
        )
        return client


def generate_organization_client() -> OrganizationClient:
    with allure.step("Генерация нового пользователя типа ЮЛ"):
        client = OrganizationClient()
        allure.attach(
            str(json.dumps(client.to_dict(), indent=2, ensure_ascii=False)),
            name="organization_client_info",
            attachment_type=allure.attachment_type.JSON,
        )
        return client


def generate_entrepreneur_client() -> EntrepreneurClient:
    with allure.step("Генерация нового пользователя типа ИП"):
        client = EntrepreneurClient()
        allure.attach(
            str(json.dumps(client.to_dict(), indent=2, ensure_ascii=False)),
            name="entrepreneur_client_info",
            attachment_type=allure.attachment_type.JSON,
        )
        return client
