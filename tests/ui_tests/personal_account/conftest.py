from dataclasses import dataclass

import allure
import pytest
from playwright.sync_api import APIRequestContext

from api.exceptions import ClientNotFoundException
from api.requests.address_requests import AddressRequests
from api.requests.client_requests import ClientRequests
from common.helpers.checker import wait_that
from common.helpers.data_generator import (
    generate_random_number,
    generate_russian_string,
    get_shifted_datetime,
)
from common.helpers.time_helpers import delay
from models.address_info import BasicSystemAddress


@dataclass
class Client:
    customer_id: int = (0,)
    account_id: int = (0,)
    account_number: int = (0,)
    customer_name: str = ""
    customer_patronymic: str = ""
    customer_surname: str = ""
    passport_series: int = 0
    passport_number: int = 0
    agreement_id: int = 0
    agreement_number: int = 0


@allure.step("API: Создание нового клиента")
@pytest.fixture(scope="function")
def create_user_b2c(
    api_request_auth_context: APIRequestContext, base_url_api: str, request: pytest.FixtureRequest
) -> Client:
    """
    Метод создает нового Клиента B2C с фамилией Авто...

    Parameters:
    api_request_auth_context (APIRequestContext): объект контекста Playwright.
    base_url_api (str): URL стенда.

    Returns:
    int: id нового Клиента.
    """
    address = getattr(request, "param", BasicSystemAddress.address)
    api_addresses = AddressRequests(api_request_auth_context)

    headers = {"Content-Type": "application/json"}

    customer_name = "Андрей"
    customer_surname = "Авто" + generate_russian_string(7)
    customer_patronymic = "Автоотчество"
    passport_series = generate_random_number(4)
    passport_number = generate_random_number(6)
    last_year = get_shifted_datetime("-500d").strftime("%Y-%m-%d")
    next_year = get_shifted_datetime("+500d").strftime("%Y-%m-%d")

    payload = {
        "businessActivity": {},
        "party": {
            "biometricData": False,
            "birthDate": "1983-07-11",
            "birthPlace": "Москва",
            "gender": {"genderId": 1},
            "identificationDocument": {
                "dateOfIssue": f"{last_year}",
                "providedByOrganization": "ГУ МВД РОССИИ",
                "divisionCode": "123-456",
                "number": f"{passport_number}",
                "series": f"{passport_series}",
                "type": {"identificationTypeId": 5},
                "validFor": f"{next_year}",
            },
            "isResident": True,
            "nameInfo": {"firstName": customer_name, "patronymic": customer_patronymic, "surname": customer_surname},
            "nationality": {"nationalityId": 1},
            "publicOfficial": False,
            "speakingLanguage": {"languageId": 3},
            "taxRegistrationCertificate": {"taxIdentificationNumber": "123456789123"},
        },
        "type": "INDIVIDUAL",
    }
    client_api = ClientRequests(api_request_auth_context)
    request = client_api.post(
        url=f"{base_url_api}/openapi/v1/customerManagement/customers", headers=headers, data=payload
    )
    assert request.status == 200, "Не выполнен запрос на создание нового клиента ФЛ"
    api_addresses.add_base_address_to_client(address, request.json()["customerId"])
    customer_id = request.json()["customerId"]

    wait_that(
        lambda: client_api.get_client_data(customer_id).status == 200,
        timeout=5,
        sleep_seconds=0.5,
        exception=ClientNotFoundException,
        message="Пользователь не был создан в установленное время",
    )
    delay(1, reason="UI не успевает за API")
    return Client(
        customer_id=customer_id,
        customer_name=customer_name,
        customer_patronymic=customer_patronymic,
        customer_surname=customer_surname,
        passport_series=passport_series,
        passport_number=passport_number,
    )
