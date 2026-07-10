from dataclasses import dataclass, field
from typing import Any, Literal

import allure
import pytest

from api.base_requests import BaseRequests
from api.exceptions import (
    ClientNotFoundException,
    LinkedPersonException,
    LinkedPersonFunctionException,
    LinkedPersonPullAddressException,
    UpdateStatusException,
)
from api.lis_requests.apn import APNRequests
from api.lis_requests.ip_addresses import IpAddressRequests
from api.nbss.address_requests import AddressRequests
from api.nbss.finances.payments_requests import PaymentInfo, PaymentsRequests
from api.nbss.personal_account_requests import PersonalAccountData, PersonalAccountRequests
from common.enums.linked_person import Specialization
from common.enums.user import User
from common.helpers.checker import assert_that, check_response_conflicts, wait_that
from common.helpers.env_helper import BASE_URL_API
from common.helpers.time_helpers import delay, get_now_time
from models.address_info import BasicSystemAddress
from models.client import EntrepreneurClient, IndividualClient, OrganizationClient
from models.context import test_context
from models.playwright_bridge import GeneralResponse
from models.product import MainProduct


@dataclass
class InfoAboutBundle:
    bundle_name: str = ""
    products: list[MainProduct] = field(default_factory=list)
    one_time_payment: float = 0.0
    subscription_fee: float = 0.0

    def add_product(self, product: MainProduct) -> None:
        self.products.append(product)
        self.one_time_payment += product.one_time_payment
        self.subscription_fee += product.subscription_fee


@dataclass
class ClientDataFromResponseGetClientData:
    """Класс данных по клиенту для парсинга ответа API запроса get_client_data
    organization: ЮЛ
    individual: ФЛ"""

    client_data: dict
    client_type: str = "organization"

    def __post_init__(self) -> None:
        self.customer_id = self.client_data["customerId"]
        self.full_name = self.client_data["party"]["nameInfo"]["name"]
        self.nationality = self.client_data["party"]["nationality"]["name"]
        self.tax_number = self.client_data["party"]["taxRegistrationCertificate"]["taxIdentificationNumber"]
        self.isResident = "Да" if self.client_data["party"]["isResident"] else "Нет"
        if self.client_type == "individual":
            self.birth_date = self.client_data["party"]["birthDate"]
            self.gender = self.client_data["party"]["gender"]["name"]
            self.document_series = self.client_data["party"]["identificationDocument"]["series"]
            self.document_num = self.client_data["party"]["identificationDocument"]["number"]
            self.document_type = self.client_data["party"]["identificationDocument"]["type"]["name"]


class ClientRequests(BaseRequests):
    def __init__(self) -> None:
        super().__init__()
        self.personal_account_api = PersonalAccountRequests()
        self.payment_api = PaymentsRequests()
        self.apn_api = APNRequests()
        self.ip_api = IpAddressRequests()

        test_context.switch_api_context_to_user(User.ADMIN)

    def _build_organization_put_payload(
        self,
        client_data: OrganizationClient,
        corporate_name: str,
        include_full_attributes: bool = False,
    ) -> dict[str, Any]:
        """
        Формирует тело PUT для обновления клиента ЮЛ (customerManagement/customers).

        :param client_data: данные клиента ЮЛ.
        :param corporate_name: наименование организации (corporateName / name).
        :param include_full_attributes: если True — добавляет расширенные реквизиты (ОКАТО, ОКВЭД, КПП, ОКПО, ОПФ, язык).
        :return: словарь тела запроса для PUT.
        """
        party: dict[str, Any] = {
            "ARCPS": client_data.okato if include_full_attributes else None,
            "economicActivities": client_data.okved if include_full_attributes else None,
            "isResident": client_data.is_resident_bool,
            "nameInfo": {
                "corporateName": corporate_name,
                "name": corporate_name,
                "type": "PARTY_ORGANIZATION_NAME",
            },
            "nationality": {"nationalityId": client_data.nationality_id},
            "taxRegistrationCertificate": {
                "foreignRegistrationNumber": None,
                "PSRN": client_data.ogrn,
                "PSRNInfo": None,
                "registrationDate": None,
                "registrationReasonCode": client_data.kpp if include_full_attributes else None,
                "RNNBO": client_data.okpo if include_full_attributes else None,
                "taxIdentificationNumber": client_data.inn,
            },
            "type": "PARTY_ORGANIZATION",
        }
        if include_full_attributes:
            party["proprietaryForm"] = {"proprietaryFormId": client_data.proprietary_form_id}
            party["speakingLanguage"] = {"languageId": client_data.speaking_language_id}

        return {
            "additionalAttributes": [
                {"code": "isVIP", "value": client_data.is_vip_bool, "valueType": "BOOLEAN"},
            ],
            "businessActivity": {},
            "businessInfo": {"reputation": None},
            "note": None,
            "party": party,
            "region": {},
            "salesRepresentative": {},
        }

    @pytest.mark.praim
    @allure.step("API: Создание нового клиента ФЛ")
    def create_individual_client(self, client_data: IndividualClient) -> IndividualClient:
        """
        Метод создает клиента типа Физическое лицо

        :param client_data: инстанс класса IndividualClient
        :return: инстанс класса IndividualClient с заполненным user_id
        """
        api_addresses = AddressRequests()
        payload = {
            "businessActivity": {},
            "party": {
                "INILA": client_data.snils,
                "biometricData": False,
                "birthDate": client_data.birth_date_for_api,
                "birthPlace": client_data.birth_place,
                "gender": {"genderId": client_data.gender_id},
                "identificationDocument": {
                    "dateOfIssue": client_data.issue_date_for_api,
                    "providedByOrganization": client_data.document_provide_by,
                    "divisionCode": client_data.document_division_code,
                    "number": client_data.document_num,
                    "series": client_data.document_serial,
                    "type": {"identificationTypeId": client_data.document_type_id},
                    "validFor": client_data.document_valid_date_for_api,
                },
                "isResident": client_data.is_resident_bool,
                "nameInfo": {
                    "firstName": client_data.first_name,
                    "patronymic": client_data.patronymic,
                    "surname": client_data.sur_name,
                },
                "nationality": {"nationalityId": client_data.nationality_id},
                "publicOfficial": client_data.is_public_bool,
                "speakingLanguage": {"languageId": client_data.speaking_language_id},
                "taxRegistrationCertificate": {"taxIdentificationNumber": client_data.inn},
            },
            "type": "INDIVIDUAL",
        }
        request = self.post(url=f"{BASE_URL_API}/openapi/v1/customerManagement/customers", json=payload)
        self.check_response_status(request, 200, "Не выполнен запрос на создание нового клиента ФЛ")

        client_data.user_id = request.json()["customerId"]
        self.set_additional_attribute(
            "customer_individual",
            client_data.user_id,
            [
                {
                    "attributeCode": "taxSchemeId",
                    "value": client_data.tax_scheme_id,
                    "valueType": client_data.tax_scheme_type,
                }
            ],
        )
        api_addresses.add_base_address_to_client(client_data.registration_address, client_data.user_id)

        wait_that(
            lambda: self.get_client_data(client_data.user_id).status_code == 200,
            timeout=5,
            sleep_seconds=0.5,
            exception=ClientNotFoundException,
            message="Пользователь не был создан в установленное время",
        )
        delay(1, reason="UI не успевает за API")
        test_context.client_list.append(client_data)
        test_context.client = client_data
        return client_data

    @pytest.mark.praim
    def _create_organization(
        self,
        client_data: OrganizationClient,
        is_potential_customer: bool = False,
        is_successful: bool = True,
    ) -> GeneralResponse:
        """
        Отправляет POST на создание клиента ЮЛ (OAPI customerManagement/customers).

        :param client_data: данные клиента ЮЛ для сборки тела запроса.
        :param is_potential_customer: если True — формирует минимальное тело «Потенциальный» (customerStatusId=1).
        :param is_successful: при True ожидается код 200; при False — любой код ответа, отличный от 200.
        :return: объект ответа API.
        """
        if is_potential_customer:
            payload = {
                "additionalAttributes": [
                    {"code": "isVIP", "value": client_data.is_vip_bool, "valueType": "BOOLEAN"},
                ],
                "businessActivity": {},
                "businessInfo": {},
                "party": {
                    "isResident": client_data.is_resident_bool,
                    "nameInfo": {"corporateName": client_data.customer_name},
                    "nationality": {"nationalityId": client_data.nationality_id},
                    "proprietaryForm": {"proprietaryFormId": client_data.proprietary_form_id},
                    "speakingLanguage": {"languageId": client_data.speaking_language_id},
                    "taxRegistrationCertificate": {"PSRN": client_data.ogrn},
                },
                "partyRoleType": "customer",
                "region": {},
                "salesRepresentative": {},
                "status": {"customerStatusId": 1},
                "type": "ORGANIZATION",
            }
        else:
            payload = {
                "additionalAttributes": [{"code": "isVIP", "value": client_data.is_vip_bool, "valueType": "BOOLEAN"}],
                "businessActivity": {},
                "businessInfo": {},
                "party": {
                    "isResident": client_data.is_resident_bool,
                    "nameInfo": {"corporateName": client_data.customer_name},
                    "nationality": {"nationalityId": client_data.nationality_id},
                    "proprietaryForm": {"proprietaryFormId": client_data.proprietary_form_id},
                    "speakingLanguage": {"languageId": client_data.speaking_language_id},
                    "ARCPS": client_data.okato,
                    "economicActivities": client_data.okved,
                    "taxRegistrationCertificate": {
                        "taxIdentificationNumber": client_data.inn,
                        "registrationReasonCode": client_data.kpp,
                        "PSRN": client_data.ogrn,
                        "RNNBO": client_data.okpo,
                    },
                },
                "type": "ORGANIZATION",
            }
        response = self.post(url=f"{BASE_URL_API}/openapi/v1/customerManagement/customers", json=payload)
        if is_successful:
            self.check_response_status(
                response,
                200,
                "Не выполнен запрос на создание нового клиента ЮЛ",
            )
        else:
            self.check_response_status(
                response,
                lambda code: code != 200,
                "Ожидался статус код не 200 при создании клиента ЮЛ",
            )
        return response

    @pytest.mark.praim
    @allure.step("API: Создание нового клиента ЮЛ")
    def create_organization(
        self,
        client_data: OrganizationClient,
        is_potential_customer: bool = False,
    ) -> OrganizationClient:
        """
        Создаёт клиента типа юридическое лицо.

        :param client_data: экземпляр OrganizationClient с данными для создания.
        :param is_potential_customer: сценарий «Потенциальный»: без адреса и без записи в test_context; тело с customerStatusId и минимальным набором полей.
        :return: тот же объект client_data; поле user_id заполняется из ответа.
        """
        if is_potential_customer:
            response = self._create_organization(client_data, is_potential_customer=True, is_successful=True)
            check_response_conflicts(response)
            client_data.user_id = response.json()["customerId"]
            wait_that(
                lambda: self.get_client_data(client_data.user_id).status_code == 200,
                timeout=5,
                sleep_seconds=0.5,
                exception=ClientNotFoundException,
                message="Пользователь не был создан в установленное время",
            )
            return client_data

        api_addresses = AddressRequests()
        response = self._create_organization(client_data, is_potential_customer=False, is_successful=True)

        client_data.user_id = response.json()["customerId"]
        self.set_additional_attribute(
            "customer_organization",
            client_data.user_id,
            [
                {
                    "attributeCode": "AuthorizationCode",
                    "value": client_data.auth_code,
                    "valueType": client_data.auth_code_type,
                },
                {
                    "attributeCode": "taxSchemeId",
                    "value": client_data.tax_scheme_id,
                    "valueType": client_data.tax_scheme_type,
                },
            ],
        )
        api_addresses.add_base_address_to_client(client_data.registration_address, client_data.user_id)

        wait_that(
            lambda: self.get_client_data(client_data.user_id).status_code == 200,
            timeout=5,
            sleep_seconds=0.5,
            exception=ClientNotFoundException,
            message="Пользователь не был создан в установленное время",
        )
        delay(1, reason="UI не успевает за API")
        test_context.client_list.append(client_data)
        test_context.client = client_data
        return client_data

    @pytest.mark.praim
    @allure.step("API: Создание нового клиента ИП")
    def create_entrepreneur_client(self, client_data: EntrepreneurClient) -> EntrepreneurClient:
        """
        Метод создает клиента типа Индивидуальный предприниматель

        :param client_data: инстанс класса EntrepreneurClient
        :return: инстанс класса EntrepreneurClient с заполненным user_id
        """
        api_addresses = AddressRequests()
        payload = {
            "businessActivity": {},
            "businessInfo": {},
            "party": {
                "isResident": client_data.is_resident_bool,
                "nameInfo": {
                    "firstName": client_data.first_name,
                    "surname": client_data.sur_name,
                    "patronymic": client_data.patronymic,
                },
                "nationality": {"nationalityId": client_data.nationality_id},
                "proprietaryForm": {"proprietaryFormId": client_data.proprietary_form_id},
                "speakingLanguage": {"languageId": client_data.speaking_language_id},
                "publicOfficial": client_data.is_public_bool,
                "gender": {"genderId": client_data.gender_id},
                "birthDate": client_data.birth_date_for_api,
                "birthPlace": client_data.birth_place,
                "taxRegistrationCertificate": {
                    "taxIdentificationNumber": client_data.inn,
                    "PSRN": client_data.ogrn,
                },
                "identificationDocument": {
                    "dateOfIssue": client_data.issue_date_for_api,
                    "providedByOrganization": client_data.document_provide_by,
                    "divisionCode": client_data.document_division_code,
                    "number": client_data.document_num,
                    "series": client_data.document_serial,
                    "type": {"identificationTypeId": client_data.document_type_id},
                    "validFor": client_data.document_valid_date_for_api,
                },
            },
            "type": "ENTREPRENEUR",
        }
        response = self.post(url=f"{BASE_URL_API}/openapi/v1/customerManagement/customers", json=payload)
        self.check_response_status(response, 200, "Не выполнен запрос на создание нового клиента ИП")

        client_data.user_id = response.json()["customerId"]
        self.set_additional_attribute(
            "customer_entrepreneur",
            client_data.user_id,
            [
                {
                    "attributeCode": "taxSchemeId",
                    "value": client_data.tax_scheme_id,
                    "valueType": client_data.tax_scheme_type,
                }
            ],
        )
        api_addresses.add_base_address_to_client(client_data.registration_address, client_data.user_id)

        wait_that(
            lambda: self.get_client_data(client_data.user_id).status_code == 200,
            timeout=5,
            sleep_seconds=0.5,
            exception=ClientNotFoundException,
            message="Пользователь не был создан в установленное время",
        )
        delay(1, reason="UI не успевает за API")
        test_context.client_list.append(client_data)
        test_context.client = client_data
        return client_data

    def create_individual_client_with_agreement_and_account(self, client_data: IndividualClient) -> IndividualClient:
        """Метод создает клиента типа Физическое лицо, создает договор и лицевой счёт для него"""
        created_individual_client = self.create_individual_client(client_data)
        return self.personal_account_api.create_agreement_and_account(created_individual_client)

    def create_individual_client_with_agreement(self, client_data: IndividualClient) -> IndividualClient:
        """Метод создает клиента типа Физическое лицо и создает договор для него"""
        client = self.create_individual_client(client_data)
        self.personal_account_api.create_agreement(client)
        return client

    def create_organization_with_linked_person(self, client_data: OrganizationClient) -> OrganizationClient:
        created_organization = self.create_organization(client_data)
        self.create_linked_person(client_id=created_organization.user_id, phone=True)
        return created_organization

    def create_organization_with_agreement_and_account(self, client_data: OrganizationClient) -> OrganizationClient:
        """Метод создает клиента типа Юридическое лицо, создает договор и лицевой счёт для него"""
        created_organization = self.create_organization(client_data)
        return self.personal_account_api.create_agreement_and_account(created_organization)

    def create_individual_client_with_postpaid_account(self, client_data: IndividualClient) -> IndividualClient:
        """Метод создает клиента типа Физическое лицо, создает договор и постоплатный лицевой счёт для него"""
        client = self.create_individual_client(client_data)
        agreement_id, agreement_number = self.personal_account_api.create_agreement(client)
        self.personal_account_api.create_personal_account(
            PersonalAccountData(
                agreement_id=agreement_id,
                rating_type=2,
                threshold_break=2000,
                threshold_control=True,
            ),
            client.user_id,
        )
        return client

    def create_individual_client_with_agreement_and_usd_account(self, client_data: IndividualClient) -> IndividualClient:
        """Метод создает клиента типа Физическое лицо, создает договор и личный счёт для него в валюте USD"""
        client = self.create_individual_client(client_data)
        agreement_id, agreement_number = self.personal_account_api.create_agreement(client)
        account_data = PersonalAccountData(agreement_id=agreement_id, is_cash_payment_enabled=False, currency_id=2)
        self.personal_account_api.create_personal_account(account_data, client.user_id)
        wait_that(
            lambda: self.personal_account_api.get_personal_accounts("customer", client.user_id).json()["items"][0][
                "currency"
            ]["name"]
            == "USD",
            exception=UpdateStatusException,
            timeout=10,
            sleep_seconds=0.5,
            message="Аккаунт не создался в указанное время",
        )
        return client

    @allure.step("API: Создание клиента ЮЛ, договора со статусом по гарантии и ЛС")
    def create_organization_with_agreement_guarantee_and_account(
        self, client_data: OrganizationClient
    ) -> OrganizationClient:
        """
        Метод создает клиента типа Юридическое лицо, затем создает договор со статусом по гарантии и лицевой счёт
        Не дублирует логику создания клиента — переиспользует create_individual_client и create_agreement_and_account
        """
        created_org = self.create_organization(client_data)
        return self.personal_account_api.create_agreement_and_account(created_org, status_id=3)

    def create_organization_client_with_postpaid_account(self, client_data: OrganizationClient) -> OrganizationClient:
        """Метод создает клиента типа Юридическое лицо, создает договор и постоплатный лицевой счёт для него"""
        client = self.create_organization(client_data)
        agreement_id, agreement_number = self.personal_account_api.create_agreement(client)
        self.personal_account_api.create_personal_account(
            PersonalAccountData(
                agreement_id=agreement_id,
                rating_type=2,
                threshold_break=10000000,
                threshold_control=True,
            ),
            client.user_id,
        )
        return client

    @allure.step("API: Получить данные по клиенту '{customer_id}'")
    def get_client_data(self, customer_id: int, check_status: bool = False) -> GeneralResponse:
        """
        Возвращает данные клиента по идентификатору (GET customerManagement/customers).

        :param customer_id: идентификатор клиента.
        :param check_status: если True — дополнительно проверяется код ответа 200.
        :return: объект ответа API с данными клиента.
        """
        client = self.get(url=f"{BASE_URL_API}/openapi/v1/customerManagement/customers/{customer_id}")
        if check_status:
            self.check_response_status(client, 200, "Не удалось получить данные клиента")
        return client

    @allure.step("API: Отображаемое имя статуса жизненного цикла клиента '{customer_id}'")
    def get_customer_lifecycle_status_display_name(self, customer_id: int) -> str:
        """
        Возвращает отображаемое имя статуса жизненного цикла клиента.

        :param customer_id: идентификатор клиента.
        :return: строка с отображаемым именем статуса (например «Потенциальный»).
        """
        data = self.get_client_data(customer_id).json()
        for path in (
            ("customerLifecycleStatus", "name"),
            ("lifecycleStatus", "name"),
            ("customerStatus", "name"),
            ("status", "name"),
        ):
            cur: Any = data
            for key in path:
                if not isinstance(cur, dict) or key not in cur:
                    cur = None
                    break
                cur = cur[key]
            if isinstance(cur, str) and cur.strip():
                return cur
        raise KeyError("Не найдено поле статуса клиента (name) в ответе GET customers/{id}")

    @allure.step("API: Статус клиента '{customer_id}' = '{expected_status}'")
    def check_customer_lifecycle_status(self, customer_id: int, expected_status: str) -> None:
        """
        Проверяет, что у клиента отображаемый статус жизненного цикла совпадает с ожидаемым.

        :param customer_id: идентификатор клиента.
        :param expected_status: ожидаемое отображаемое имя статуса.
        :return: None.
        """
        actual = self.get_customer_lifecycle_status_display_name(customer_id)
        assert_that(
            lambda: actual == expected_status, lambda: f"Ожидался статус «{expected_status}», получено: {actual!r}"
        )

    @allure.step("API: Дождаться статуса клиента '{customer_id}' = '{expected_status}'")
    def wait_customer_lifecycle_status(
        self,
        customer_id: int,
        expected_status: str,
        timeout: int = 30,
    ) -> None:
        """
        Ожидает, пока отображаемый статус жизненного цикла клиента станет равен ожидаемому.

        :param customer_id: идентификатор клиента.
        :param expected_status: ожидаемое отображаемое имя статуса (например «Действующий»).
        :param timeout: таймаут ожидания в секундах.
        :return: None.
        """
        wait_that(
            lambda: self.get_customer_lifecycle_status_display_name(customer_id) == expected_status,
            timeout=timeout,
            sleep_seconds=0.5,
            exception=AssertionError,
            message=lambda: (
                "Не дождались статуса за "
                f"{timeout} сек. Ожидали «{expected_status}», получили «{self.get_customer_lifecycle_status_display_name(customer_id)}»."
            ),
        )

    @allure.step("API: У клиента '{customer_id}' нет лицевых счетов")
    def check_customer_has_no_personal_accounts(self, customer_id: int) -> None:
        """
        Проверяет, что у клиента нет лицевых счетов (список items пуст).

        :param customer_id: идентификатор клиента.
        :return: None.
        """
        accounts_resp = self.personal_account_api.get_personal_accounts("customer", customer_id)
        items = accounts_resp.json().get("items", [])
        assert_that(lambda: len(items) == 0, lambda: f"У клиента без договора не должно быть лицевых счетов: {items}")

    @allure.step("API: Обновить клиента ЮЛ (PUT customerManagement/customers)")
    def put_organization_customer(
        self,
        client_data: OrganizationClient,
        corporate_name: str,
        apply_date: str | None = None,
        is_successful: bool = True,
    ) -> GeneralResponse:
        """
        Обновляет данные клиента ЮЛ через PUT customerManagement/customers (тело OAPI / CHM).

        :param client_data: данные клиента ЮЛ; должен быть задан user_id.
        :param corporate_name: новое наименование организации (corporateName).
        :param apply_date: дата применения изменений (applyDate); если None — дата по Москве для CHM.
        :param is_successful: при True ожидается код 200, проверка conflicts и обновление customer_name; при False — код ответа, отличный от 200.
        :return: объект ответа API.
        """
        assert client_data.user_id is not None, "Не задан user_id клиента"
        if apply_date is None:
            apply_date = get_now_time("%Y-%m-%dT%H:%M:%S")
        params = {"applyDate": apply_date, "getObject": "true"}
        payload = self._build_organization_put_payload(client_data, corporate_name)
        response = self.put(
            url=f"{BASE_URL_API}/openapi/v1/customerManagement/customers/{client_data.user_id}",
            params=params,
            json=payload,
        )
        if is_successful:
            self.check_response_status(response, 200, "Не выполнен PUT по обновлению клиента ЮЛ")
            check_response_conflicts(response)
            client_data.customer_name = corporate_name
        else:
            self.check_response_status(
                response,
                lambda code: code != 200,
                "Ожидался статус код не 200 при обновлении клиента ЮЛ",
            )
        return response

    @allure.step("API: Дозаполнить ЮЛ после «Потенциального» (ИНН, КПП, ОГРН, код авторизации, схема, адрес)")
    def fill_organization_attributes_for_agreement_after_potential(
        self,
        client_data: OrganizationClient,
        corporate_name: str | None = None,
    ) -> None:
        """
        Дозаполняет реквизиты ЮЛ после статуса «Потенциальный»: PUT с полным набором полей, атрибуты customer_organization и базовый адрес.

        :param client_data: данные клиента ЮЛ; должен быть задан user_id.
        :param corporate_name: наименование; если None — берётся из client_data.customer_name.
        :return: None.
        """
        assert client_data.user_id is not None, "Не задан user_id клиента"
        name = corporate_name if corporate_name is not None else client_data.customer_name
        apply_date = get_now_time("%Y-%m-%dT%H:%M:%S")
        params = {"applyDate": apply_date, "getObject": "true"}
        payload = self._build_organization_put_payload(
            client_data,
            name,
            include_full_attributes=True,
        )
        response = self.put(
            url=f"{BASE_URL_API}/openapi/v1/customerManagement/customers/{client_data.user_id}",
            params=params,
            json=payload,
        )
        self.check_response_status(response, 200, "Не выполнен PUT по дозаполнению клиента ЮЛ")
        check_response_conflicts(response)
        self.set_additional_attribute(
            "customer_organization",
            client_data.user_id,
            [
                {
                    "attributeCode": "AuthorizationCode",
                    "value": client_data.auth_code,
                    "valueType": client_data.auth_code_type,
                },
                {
                    "attributeCode": "taxSchemeId",
                    "value": client_data.tax_scheme_id,
                    "valueType": client_data.tax_scheme_type,
                },
            ],
        )
        api_addresses = AddressRequests()
        api_addresses.add_base_address_to_client(client_data.registration_address, client_data.user_id)
        client_data.customer_name = name

    @allure.step("API: Наименование ЮЛ (corporateName) по '{customer_id}'")
    def get_organization_corporate_name(self, customer_id: int) -> str:
        """
        Возвращает наименование юридического лица (corporateName) из данных клиента.

        :param customer_id: идентификатор клиента.
        :return: строка с наименованием организации.
        """
        data = self.get_client_data(customer_id).json()
        return data["party"]["nameInfo"]["corporateName"]

    @allure.step("API: ИНН ЮЛ (taxIdentificationNumber) по '{customer_id}'")
    def get_organization_tax_identification_number(self, customer_id: int) -> str | None:
        """
        Возвращает ИНН юридического лица из свидетельства о налоговой регистрации.

        :param customer_id: идентификатор клиента.
        :return: строка с ИНН или None, если поле отсутствует.
        """
        cert = self.get_client_data(customer_id).json().get("party", {}).get("taxRegistrationCertificate") or {}
        tid = cert.get("taxIdentificationNumber")
        return str(tid) if tid is not None else None

    @allure.step("API: PUT customerManagement/customers (произвольное тело)")
    def put_customer(
        self,
        customer_id: int,
        payload: dict[str, Any],
        apply_date: str | None = None,
        is_successful: bool = True,
    ) -> GeneralResponse:
        """
        Выполняет PUT customerManagement/customers с произвольным телом (негативные и позитивные сценарии).

        :param customer_id: идентификатор клиента.
        :param payload: тело запроса PUT.
        :param apply_date: дата применения; если None — дата по Москве для CHM.
        :param is_successful: при True ожидается код 200 и проверка conflicts; при False — код ответа, отличный от 200.
        :return: объект ответа API.
        """
        if apply_date is None:
            apply_date = get_now_time("%Y-%m-%dT%H:%M:%S")
        params = {"applyDate": apply_date, "getObject": "true"}
        response = self.put(
            url=f"{BASE_URL_API}/openapi/v1/customerManagement/customers/{customer_id}",
            params=params,
            json=payload,
        )
        if is_successful:
            self.check_response_status(response, 200, "Не выполнен PUT по клиенту")
            check_response_conflicts(response)
        else:
            self.check_response_status(
                response,
                lambda code: code != 200,
                "Ожидался статус код не 200 при PUT по клиенту",
            )
        return response

    @staticmethod
    def build_put_organization_null_required_attributes_payload(
        organization_user_data: OrganizationClient,
    ) -> dict[str, Any]:
        return {
            "additionalAttributes": [
                {"code": "isVIP", "value": organization_user_data.is_vip_bool, "valueType": "BOOLEAN"},
            ],
            "businessActivity": {},
            "businessInfo": {"reputation": None},
            "note": None,
            "party": {
                "ARCPS": None,
                "economicActivities": None,
                "isResident": organization_user_data.is_resident_bool,
                "nameInfo": {
                    "corporateName": None,
                    "name": None,
                    "type": "PARTY_ORGANIZATION_NAME",
                },
                "nationality": {"nationalityId": organization_user_data.nationality_id},
                "taxRegistrationCertificate": {
                    "foreignRegistrationNumber": None,
                    "PSRN": organization_user_data.ogrn,
                    "PSRNInfo": None,
                    "registrationDate": None,
                    "registrationReasonCode": None,
                    "RNNBO": None,
                    "taxIdentificationNumber": organization_user_data.inn,
                },
                "type": "PARTY_ORGANIZATION",
            },
            "region": {},
            "salesRepresentative": {},
        }

    @pytest.mark.praim
    @allure.step("API: Обновить данные по клиенту '{customer_id}'")
    def put_client_data(
        self, customer_id: int, apply_date: str, client_type: str, expected_code: int, **kwargs: Any
    ) -> GeneralResponse:
        """
        Обновить данные по клиенту.
            if client_type == "organization" - reputation_message, customer_name, inn, kpp (str)
            elif client_type == "individual" - patronymic, series, number, inn, snils (str)
            elif client_type == "entrepreneur" - surname, first_name, patronymic, series, number, inn, snils (str)
            else - without attributes

        Args:
            customer_id (int): id Клиента.
            apply_date (str): дата обновления данных по клиенту
            client_type (str): тип клиента
            expected_code (int): ожидаемый статус код ответа API


        Returns:
            Response: объект ответа API с данными клиента.
        """
        params = {"applyDate": apply_date, "getObject": "true"}
        if client_type == "organization":
            payload = {
                "note": None,
                "businessInfo": {"reputation": kwargs.get("reputation_message")},
                "businessActivity": {"businessActivityId": 3},
                "externalReference": {"externalCustomerId": "212345"},
                "party": {
                    "nameInfo": {"corporateName": kwargs.get("customer_name")},
                    "proprietaryForm": {"proprietaryFormId": 4},
                    "isResident": True,
                    "nationality": {"nationalityId": 1},
                    "taxRegistrationCertificate": {
                        "taxIdentificationNumber": kwargs.get("inn"),
                        "registrationReasonCode": kwargs.get("kpp"),
                        "PSRN": "1172375467400",
                        "registrationDate": "2022-11-02",
                        "PSRNInfo": "00D67D7D5751F",
                        "foreignRegistrationNumber": None,
                        "RNNBO": "09513533",
                    },
                    "speakingLanguage": {"languageId": 3},
                    "note": None,
                    "ARCPS": "46439000156",
                    "economicActivities": "4622",
                },
            }
        elif client_type == "individual":
            payload = {
                "note": None,
                "businessInfo": None,
                "businessActivity": {"businessActivityId": 3},
                "externalReference": {"externalCustomerId": "212345"},
                "party": {
                    "nameInfo": {"patronymic": kwargs.get("patronymic")},
                    "birthPlace": "Самара",
                    "birthDate": "1994-01-01",
                    "isResident": True,
                    "nationality": {"nationalityId": 1},
                    "identificationDocument": {
                        "type": {"identificationTypeId": 5},
                        "series": kwargs.get("series"),
                        "number": kwargs.get("number"),
                        "dateOfIssue": "2022-03-09",
                        "providedByOrganization": "МВД",
                        "divisionCode": "770094",
                        "validFor": None,
                    },
                    "taxRegistrationCertificate": {"taxIdentificationNumber": kwargs.get("inn")},
                    "INILA": kwargs.get("snils"),
                    "biometricData": False,
                    "publicOfficial": False,
                    "speakingLanguage": {"languageId": 3},
                    "note": None,
                },
                "additionalAttributes": [  # type: ignore
                    {"code": "stringAttribute", "valueType": "STRING", "value": "test string value 2"},
                    {"code": "numberAttribute", "valueType": "NUMBER", "value": 1000001},
                    {"code": "booleanAttribute", "valueType": "BOOLEAN", "value": True},
                    {"code": "dateAttribute", "valueType": "STRING", "value": None},
                    {"code": "dateTimeAttribute", "valueType": "STRING", "value": None},
                    {"code": "int32Attribute", "valueType": "NUMBER", "value": None},
                    {"code": "int64Attribute", "valueType": "NUMBER", "value": None},
                    {"code": "stringArray", "valueType": "STRING", "value": "test string value 3"},
                    {"code": "stringArray", "valueType": "STRING", "value": "test string value 4"},
                    {"code": "stringArray", "valueType": "STRING", "value": "test string value 5"},
                    {"code": "numberArray", "valueType": "NUMBER", "value": 100000},
                    {"code": "booleanArray", "valueType": "BOOLEAN", "value": False},
                ],
            }
        elif client_type == "entrepreneur":
            payload = {
                "note": None,
                "businessInfo": None,
                "businessActivity": {"businessActivityId": 3},
                "externalReference": {"externalCustomerId": "212345"},
                "party": {
                    "nameInfo": {
                        "surname": kwargs.get("surname"),
                        "firstName": kwargs.get("first_name"),
                        "patronymic": kwargs.get("patronymic"),
                    },
                    "proprietaryForm": {"proprietaryFormId": 34},
                    "birthPlace": "Самара",
                    "birthDate": "1994-01-01",
                    "gender": {"genderId": 1},
                    "isResident": True,
                    "nationality": {"nationalityId": 1},
                    "identificationDocument": {
                        "type": {"identificationTypeId": 5},
                        "series": kwargs.get("series"),
                        "number": kwargs.get("number"),
                        "dateOfIssue": "2022-03-09",
                        "providedByOrganization": "МВД",
                        "divisionCode": "770094",
                        "validFor": None,
                    },
                    "taxRegistrationCertificate": {
                        "taxIdentificationNumber": kwargs.get("inn"),
                        "PSRN": "312506377281216",
                        "registrationDate": "2016-02-15",
                        "PSRNInfo": "F377B812AABD83F",
                        "RNNBO": "0742491350",
                    },
                    "INILA": kwargs.get("snils"),
                    "publicOfficial": False,
                    "speakingLanguage": {"languageId": 3},
                    "note": None,
                    "ARCPS": "46439000156",
                    "economicActivities": "4622",
                },
            }
        else:
            payload = {}
        client = self.put(
            url=f"{BASE_URL_API}/openapi/v1/customerManagement/customers/{customer_id}", params=params, json=payload
        )
        self.check_response_status(client, expected_code, "Не обновились данные по клиенту")
        return client

    @allure.step("API: Обновить данные по подразделению клиента '{subdivision_id}'")
    def put_client_subdivision_data(
        self, subdivision_id: int, apply_date: str, expected_code: int, payload_data: bool, **kwargs: Any
    ) -> GeneralResponse:
        """
        Обновить данные по подразделению клиента
        Args:
            subdivision_id (int): id подразделения.
            apply_date (str): дата обновления данных по клиенту
            expected_code (int): ожидаемый код ответа
            payload_data (bool): нужно ли отправлять данные в теле запроса
            **kwargs - new_name, kpp (str) новые данные для подразделения
        Returns:
            Response: объект ответа API с данными клиента.
        """
        params = {"applyDate": apply_date, "getObject": "true"}
        if payload_data:
            payload = {
                "businessActivity": {"businessActivityId": 3},
                "note": None,
                "externalReference": {"externalSubdivisionId": "2"},
                "party": {
                    "nameInfo": {"corporateName": kwargs.get("new_name")},
                    "nationality": {"nationalityId": 1},
                    "note": None,
                    "taxRegistrationCertificate": {"registrationReasonCode": kwargs.get("kpp")},
                },
            }
        else:
            payload = {}
        subdivision = self.put(
            url=f"{BASE_URL_API}/openapi/v1/customerManagement/subdivisions/{subdivision_id}",
            params=params,
            json=payload,
        )
        self.check_response_status(subdivision, expected_code, "Не обновились данные по подразделению")
        return subdivision

    @allure.step("API: Получить данные по связанному лицу '{linked_person_id}'")
    def get_linked_person_data(self, linked_person_id: int) -> GeneralResponse:
        """
        Получить данные по связанному лицу.

        Args:
            linked_person_id (int): id связанного лица.

        Returns:
            Response: объект ответа API с данными связанного лица.
        """
        linked_person = self.get(url=f"{BASE_URL_API}/openapi/v1/customerManagement/linkedPersons/{linked_person_id}")
        return linked_person

    @allure.step("API: Получить данные по специализации связанного лица '{linked_function_id}'")
    def get_linked_person_specialisation(self, linked_function_id: int) -> GeneralResponse:
        """
        Получить данные по специализации связанного лица.

        Args:
            linked_function_id (int): id функции связанного лица.

        Returns:
            Response: объект ответа API с данными связанного лица.
        """
        linked_person = self.get(
            url=f"{BASE_URL_API}/openapi/v1/customerManagement/linkedPersons/linkedPersonFunctions/{linked_function_id}"
        )
        return linked_person

    @pytest.mark.praim
    @allure.step("API: Обновить телефон связанного лица '{linked_person_id}' на '{phone}'")
    def update_linked_person_phone(self, linked_person_id: int, phone: str) -> None:
        payload = {"phoneContacts": [{"additional": None, "base": phone, "isMain": True, "type": {"phoneTypeId": 2}}]}
        response = self.post(
            url=f"{BASE_URL_API}/openapi/v1/customerManagement/linkedPersons/{linked_person_id}/phoneContacts/update",
            json=payload,
        )
        self.check_response_status(response, 200, "Не обновился телефон связанного лица")

    @pytest.mark.praim
    @allure.step("API: Создать связанное лицо для клиента '{client_id}'")
    def create_linked_person(
        self,
        client_id: int,
        name: str = None,
        linked_person: IndividualClient | None = None,
        specialization: Specialization = Specialization.RequestsProcessing,
        phone: bool | str = False,
    ) -> int:
        """
        Метод создает обезличенное связанное лицо, если не передан linked_person.
        Или создает связанное лицо, если передан.

        Args:
            client_id: id Клиента.
            name: название связанного лица.
            linked_person: экземпляр класса IndividualClient.
            specialization: специализация связанного лица.

        Returns:
            int: id связанного лица.
        """
        if linked_person:
            payload = {
                "party": {
                    "birthDate": linked_person.birth_date_for_api,
                    "birthPlace": linked_person.birth_place,
                    "gender": {"genderId": linked_person.gender_id},
                    "identificationDocument": {
                        "number": linked_person.document_num,
                        "series": linked_person.document_serial,
                        "type": {"identificationTypeId": linked_person.document_type_id},
                    },
                    "INILA": linked_person.snils,
                    "isResident": linked_person.is_resident_bool,
                    "nameInfo": {
                        "name": f"{linked_person.first_name} {linked_person.sur_name} {linked_person.patronymic}",
                        "firstName": linked_person.first_name,
                        "patronymic": linked_person.patronymic,
                        "surname": linked_person.sur_name,
                    },
                    "nationality": {"nationalityId": linked_person.nationality_id},
                    "publicOfficial": linked_person.is_public_bool,
                    "speakingLanguage": {"languageId": linked_person.speaking_language_id},
                    "taxRegistrationCertificate": {"taxIdentificationNumber": linked_person.inn},
                    "type": "INDIVIDUAL",
                }
            }
        else:
            payload = {
                "party": {
                    "nameInfo": {"impersonalName": name or test_context.client.linked_person_name},
                    "note": None,
                    "speakingLanguage": {"languageId": 3},
                    "type": "IMPERSONAL",
                }
            }
        response = self.post(
            url=f"{BASE_URL_API}/openapi/v1/customerManagement/customers/{client_id}/linkedPersons", json=payload
        )
        self.check_response_status(response, 200, "Не привязалось связанное лицо")
        delay(0.5, "Нужно время на сохранение данных")
        linked_person_id = response.json()["linkedPersonId"]
        payload_add_functions = {
            "entity": {"code": "customer", "id": client_id},
            "linkedPersonFunctionType": "CONTACT_PERSON",
            "specializationTypes": [{"specializationTypeId": specialization.value}],
        }
        response_add_func = self.post(
            url=f"{BASE_URL_API}/openapi/v1/customerManagement/linkedPersons/{linked_person_id}/linkedPersonFunctions",
            json=payload_add_functions,
        )
        self.check_response_status(response, 200, "Не привязалась функция связанного лица")

        if phone:
            phone = phone if isinstance(phone, str) else test_context.client.linked_person_phone
            self.update_linked_person_phone(linked_person_id, phone)

        linked_function_id = response_add_func.json().get("linkedPersonFunctionId")
        assert_that(lambda: linked_function_id is not None, "Не получен linkedPersonFunctionId")
        wait_that(
            lambda: self.get_linked_person_data(linked_person_id).status_code == 200,
            timeout=5,
            sleep_seconds=0.5,
            exception=LinkedPersonException,
            message="Связанное лицо не было создано в установленное время",
        )
        wait_that(
            lambda: self.get_linked_person_specialisation(linked_function_id).status_code == 200,
            timeout=5,
            sleep_seconds=0.5,
            exception=LinkedPersonFunctionException,
            message="Функция связанного лица не была создана в установленное время",
        )
        api_addresses = AddressRequests()
        wait_that(
            lambda: api_addresses.get_client_addresses(linked_person_id).status_code == 200,
            timeout=5,
            sleep_seconds=0.5,
            exception=LinkedPersonPullAddressException,
            message="Не сформирован пул адресов связанного лица",
        )
        delay(1, reason="Даже при наличии нового связного лица через API, на UI возникает ошибка если рано перейти")
        if test_context.client is not None and test_context.client.inquiry is not None:
            test_context.client.inquiry.linked_person_id = linked_person_id
        return linked_person_id

    @allure.step(
        "API: Создать 'Обезличенное' связанное лицо для клиента '{client_id}' с названием '{name}' и базовым "
        "адресом регистрации"
    )
    def create_linked_person_with_registration_address(
        self, client_id: int, name: str, map_url: list[None | str] = None
    ) -> int:
        """
        Метод создает обезличенное связанное лицо с адресом регистрации

        Args:
            client_id (int): id Клиента.
            name (str): название связанного лица.

        Returns:
            int: id связанного лица.
        """
        linked_person_id = self.create_linked_person(client_id=client_id, name=name)
        api_addresses = AddressRequests()
        api_addresses.add_registry_address_linked_person(linked_person_id=linked_person_id, map_url=map_url)
        return linked_person_id

    @pytest.mark.cpm
    @allure.step("API: Создание комментария для {entity_type} с идентификатором {entity_id}")
    def create_comment(self, entity_type: Literal["INQUIRY", "CUSTOMER"], entity_id: int, comment: str) -> int:
        """
        Метод создает комментарий для Клиента/Заявки

        :param entity_type: тип сущности, для которой добавляется комментарий ("INQUIRY" - Заявка, "CUSTOMER" - Клиент)
        :param entity_id: идентификатор сущности (заявки/клиента)
        :param comment: текст комментария
        :return: идентификатор комментария
        """
        payload = {"entity": {"entityId": entity_id, "entityTypeCode": entity_type}, "text": comment}
        response = self.post(url=f"{BASE_URL_API}/openapi/v1/crm/notes", json=payload)
        self.check_response_status(
            response, 201, f"Не удалось создать комментарий для {entity_type} с идентификатором {entity_id}"
        )
        return response.json()["noteId"]

    @pytest.mark.praim
    @allure.step("API: Создать подразделение для ЮЛ")
    def make_subdivision(self, client_id: int, unit_name: str) -> int:
        """
        Метод для создания подразделения для ЮЛ
        """
        payload = {
            "party": {
                "nameInfo": {"corporateName": unit_name},
                "nationality": {"nationalityId": 1},
                "note": None,
                "taxRegistrationCertificate": {},
            }
        }
        subdivision = self.post(
            url=f"{BASE_URL_API}/openapi/v1/customerManagement/customers/{client_id}/subdivisions", json=payload
        )
        self.check_response_status(subdivision, 200, "Не создано подразделение ЮЛ")
        payload_add_places = {
            "addressString": BasicSystemAddress.address,
            "entity": {"code": "subdivision", "id": subdivision.json()["subdivisionId"]},
            "externalAddressId": BasicSystemAddress.external_address_id,
            "type": {"placeTypeId": 1},
        }
        places = self.post(url=f"{BASE_URL_API}/openapi/v1/customerManagement/places", json=payload_add_places)
        self.check_response_status(places, 200, "Не добавлен адрес регистрации для подразделения")
        return subdivision.json()["subdivisionId"]

    @allure.step("API: Установка значений дополнительных атрибутов для экземпляра сущности")
    def set_additional_attribute(self, entity_type_code: str, entity_id: int, values: Any) -> dict:
        payload = {"entityId": entity_id, "entityTypeCode": entity_type_code, "values": values}
        response = self.post(
            url=f"{BASE_URL_API}/openapi/v1/attribute-service/entityTypes/{entity_type_code}/entities/{entity_id}/values/set",
            json=payload,
        )
        self.check_response_status(response, 200, "Не добавлен адрес регистрации для подразделения")
        return response.json()

    @allure.step("API: Установка значений дополнительных атрибутов для экземпляра сущности")
    def create_client_with_payment(
        self, client: IndividualClient | OrganizationClient, balance: float
    ) -> IndividualClient | OrganizationClient:
        if client.type == "Физическое лицо":
            client = self.create_individual_client_with_agreement_and_account(client)
        if client.type == "Юридическое лицо":
            client = self.create_organization_with_agreement_and_account(client)
        self.payment_api.create_default_payment(client.agreements[0].accounts[0].id, balance)
        self.personal_account_api.wait_check_current_main_balance(client.agreements[0].accounts[0].id, balance)
        return client

    @allure.step("Создание договора и ЛС. Пополнение ЛС на сумму {balance}")
    def create_agreement_and_account_with_payment(
        self, client: IndividualClient | OrganizationClient | EntrepreneurClient, balance: float
    ) -> PaymentInfo:
        client = self.personal_account_api.create_agreement_and_account(client)
        payment = PaymentInfo()
        payment.document_number = int(
            self.payment_api.create_default_payment(client.agreements[-1].accounts[0].id, balance)
        )
        self.personal_account_api.wait_check_current_main_balance(client.agreements[-1].accounts[0].id, balance)
        return payment

    @pytest.mark.nbss_cfg
    @allure.step("API: Создание APN, добавление IP адресов")
    def add_apn_and_add_customer_lock(self, count: int = 5) -> None:
        """
        Метод для создания APN, добавления туда IP адресов и их введения в эксплуатацию. Закрепление клиента за этим APN
        """
        apn = self.apn_api.add_apn()
        self.ip_api.generate_ip_addresses_and_activate(apn=apn, count=count)
        payload = {"accessPointId": apn.id, "customerId": test_context.client.user_id}
        response = self.post(f"{BASE_URL_API}/openapi/v1/tailored_nbss/customers/accessPoints/add", json=payload)
        self.check_response_status(response, 204, "Не получилось закрепить APN за клиентом")
        test_context.client.apn = apn

    @allure.step("API: Поиск договоров клиента")
    def search_client_agreements(self, customer_id: int, limit: int = 10, offset: int = 0) -> GeneralResponse:
        url = f"{BASE_URL_API}/openapi/v1/customerManagement/agreements/search"
        params = {"returnCount": True, "limit": limit, "sort": "agreementNumber", "offset": offset}
        body = {"entity": {"code": "customer", "id": customer_id}}
        response = self.post(url, params=params, json=body)
        self.check_response_status(response, 200, f"Не выполнен запрос на поиск договоров для клиента {customer_id}")
        return response.json().get("items", [])
