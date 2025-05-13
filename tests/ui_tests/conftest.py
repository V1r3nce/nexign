import allure
import pytest
from playwright.sync_api import APIRequestContext, Page, expect

from api.exceptions import ClientNotFoundException, UpdateStatusException
from api.requests.address_requests import AddressRequests
from api.requests.client_requests import ClientInfo, ClientRequests
from api.requests.payments_requests import PaymentInfo, PaymentsRequests
from api.requests.personal_account_requests import PersonalAccountData, PersonalAccountRequests
from common.helpers.checker import wait_that
from common.helpers.data_generator import (
    generate_random_number,
    generate_russian_string,
    get_current_datetime_string_for_api,
)
from common.helpers.env_helper import UserData
from common.helpers.time_helpers import delay
from models.address_info import BasicSystemAddress
from pages.locators.login_page import LoginForm


@pytest.fixture(scope="function")
def nexign_ui_stand_login(page: Page, base_url: str) -> Page:
    page.goto(base_url)
    login_page = LoginForm(page)
    login_page.LOGIN.fill(UserData.login)
    page.locator(login_page.PASSWORD.path).click()
    page.keyboard.type(UserData.password)
    login_page.SUBMIT.click()
    expect(page).to_have_title("Nexign UI", timeout=15000)
    yield page


@allure.step("API: Создание нового клиента")
@pytest.fixture(scope="function")
def create_user(api_request_auth_context: APIRequestContext, base_url_api: str, request: pytest.FixtureRequest) -> int:
    """
    Метод создает нового Клиента с фамилией Авто...

    Parameters:
    api_request_auth_context (APIRequestContext): объект контекста Playwright.
    base_url_api (str): URL стенда.

    Returns:
    int: id нового Клиента.
    """
    address = getattr(request, "param", BasicSystemAddress.address)
    api_addresses = AddressRequests(api_request_auth_context)

    headers = {"Content-Type": "application/json"}
    random_name = "Авто" + generate_russian_string(7)
    payload = {
        "businessActivity": {},
        "party": {
            "biometricData": False,
            "birthDate": "1983-07-11",
            "gender": {"genderId": 1},
            "identificationDocument": {"number": "777777", "series": "7777", "type": {"identificationTypeId": 5}},
            "isResident": True,
            "nameInfo": {"firstName": "Андрей", "patronymic": "", "surname": random_name},
            "nationality": {"nationalityId": 1},
            "publicOfficial": False,
            "speakingLanguage": {"languageId": 3},
            "taxRegistrationCertificate": {"taxIdentificationNumber": "123123123123"},
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
    return customer_id


@allure.step("API: Создание нового клиента ЮЛ")
@pytest.fixture(scope="function")
def create_organization(
    api_request_auth_context: APIRequestContext, base_url_api: str, request: pytest.FixtureRequest
) -> int:
    """
    Метод создает нового Клиента типа Юридическое лицо с названием АвтоЮЛ_...

    Parameters:
    api_request_auth_context (APIRequestContext): объект контекста Playwright.
    base_url_api (str): URL стенда.

    Returns:
    int: id нового Клиента.
    """
    address = getattr(request, "param", BasicSystemAddress.address)
    api_addresses = AddressRequests(api_request_auth_context)

    headers = {"Content-Type": "application/json"}
    random_name = "АвтоЮЛ_" + generate_russian_string(7)
    payload = {
        "additionalAttributes": [{"code": "isVIP", "value": False, "valueType": "BOOLEAN"}],
        "businessActivity": {},
        "businessInfo": {},
        "party": {
            "isResident": True,
            "nameInfo": {"corporateName": random_name},
            "nationality": {"nationalityId": 1},
            "proprietaryForm": {},
            "speakingLanguage": {"languageId": 3},
            "taxRegistrationCertificate": {"taxIdentificationNumber": "5272572572"},
        },
        "type": "ORGANIZATION",
    }
    client_api = ClientRequests(api_request_auth_context)
    request = client_api.post(
        url=f"{base_url_api}/openapi/v1/customerManagement/customers", headers=headers, data=payload
    )
    assert request.status == 200, "Не выполнен запрос на создание нового клиента ЮЛ"
    api_addresses.add_base_address_to_client(address, request.json()["customerId"])
    customer_id = request.json()["customerId"]

    add_payload = {
        "entityId": customer_id,
        "entityTypeCode": "customer_organization",
        "values": [{"attributeCode": "taxScheme", "value": "1", "valueType": "VARCHAR"}],
    }
    add_values = client_api.post(
        url=f"{base_url_api}/openapi/v1/attribute-service/entityTypes/entities/values/add",
        headers=headers,
        data=add_payload,
    )
    assert add_values.status == 200, (
        "Не выполнен запрос на добавление значений дополнительных атрибутов для нового клиента ЮЛ"
    )

    wait_that(
        lambda: client_api.get_client_data(customer_id).status == 200,
        timeout=5,
        sleep_seconds=0.5,
        exception=ClientNotFoundException,
        message="Пользователь не был создан в установленное время",
    )
    delay(1, reason="UI не успевает за API")
    return customer_id


@pytest.fixture(scope="function")
def create_user_with_agreement_and_account(create_user: int, api_request_auth_context: APIRequestContext) -> ClientInfo:
    """Фикстура создает пользователя, создает договор и личный счёт для него"""
    client = ClientInfo(create_user)
    personal_account_api = PersonalAccountRequests(api_request_auth_context)
    date = get_current_datetime_string_for_api(is_full_format=False)
    client.agreement_id, client.agreement_number = personal_account_api.create_agreement(client.user_id, date)
    account_data = PersonalAccountData(agreement_id=client.agreement_id, is_cash_payment_enabled=False)
    client.account_id, client.account_number = personal_account_api.create_personal_account(account_data)
    wait_that(
        lambda: personal_account_api.get_personal_accounts("customer", client.user_id).json()["items"][0]["accountId"]
        == client.account_id,
        exception=UpdateStatusException,
        timeout=10,
        sleep_seconds=0.5,
        message="Аккаунт не создался в указанное время",
    )
    return client


@pytest.fixture(scope="function")
def create_user_with_agreement_and_usd_account(
    create_user: int, api_request_auth_context: APIRequestContext
) -> ClientInfo:
    """Фикстура создает пользователя, создает договор и личный счёт для него в валюте USD"""
    client = ClientInfo(create_user)
    personal_account_api = PersonalAccountRequests(api_request_auth_context)
    date = get_current_datetime_string_for_api(is_full_format=False)
    client.agreement_id, client.agreement_number = personal_account_api.create_agreement(client.user_id, date)
    account_data = PersonalAccountData(agreement_id=client.agreement_id, is_cash_payment_enabled=False, currency_id=2)
    client.account_id, client.account_number = personal_account_api.create_personal_account(account_data)
    wait_that(
        lambda: personal_account_api.get_personal_accounts("customer", client.user_id).json()["items"][0]["currency"][
            "name"
        ]
        == "USD",
        exception=UpdateStatusException,
        timeout=10,
        sleep_seconds=0.5,
        message="Аккаунт не создался в указанное время",
    )
    return client


@pytest.fixture(scope="function")
def create_agreement_and_account_for_user(api_request_auth_context: APIRequestContext):
    """Фикстура создает для переданного пользователя договор и личный счёт"""

    def pass_user_id(user_id: int) -> ClientInfo:
        client = ClientInfo(user_id)
        personal_account_api = PersonalAccountRequests(api_request_auth_context)
        date = get_current_datetime_string_for_api(is_full_format=False)
        client.agreement_id, client.agreement_number = personal_account_api.create_agreement(client.user_id, date)
        account_data = PersonalAccountData(agreement_id=client.agreement_id, is_cash_payment_enabled=False)
        client.account_id, client.account_number = personal_account_api.create_personal_account(account_data)
        wait_that(
            lambda: client.account_id
            in [
                i["accountId"]
                for i in personal_account_api.get_personal_accounts("customer", client.user_id).json()["items"]
            ],
            exception=UpdateStatusException,
            timeout=10,
            sleep_seconds=0.5,
            message="Аккаунт не создался в указанное время",
        )
        return client

    return pass_user_id


@pytest.fixture(scope="function")
def create_account_with_payment(
    create_user_with_agreement_and_account: ClientInfo, api_request_auth_context: APIRequestContext
) -> tuple[ClientInfo, PaymentInfo]:
    payment_api = PaymentsRequests(api_request_auth_context)
    personal_account_api = PersonalAccountRequests(api_request_auth_context)
    client = create_user_with_agreement_and_account
    amount = generate_random_number(3)
    payment_data = PaymentInfo(
        item_type="CUSTOMER_ACCOUNT",
        account_id=client.account_id,
        payment_method_type="CASH",
        currency_code="RUB",
        amount=amount,
    )
    payment_api.wait_check_create_payment(payment_data)
    payment_api.create_payment(payment_data)
    payment_api.wait_last_payment_successful(client.account_id)
    personal_account_api.wait_check_current_main_balance(client.account_id, amount)
    return client, payment_data


@pytest.fixture(scope="function")
def add_new_address_to_lam(api_request_auth_context: APIRequestContext, base_url_api: str) -> dict:
    """Возвращает созданный адрес в виде словаря {'addressId': int, 'addressString': str}"""
    request_context = api_request_auth_context
    headers = {"Content-Type": "application/json"}
    api_addresses = AddressRequests(api_request_auth_context)
    russia_address_id = api_addresses.get_russia_parent_id()
    random_number = generate_random_number(3)
    payload = {
        "classifierCode": "addresses",
        "elements": {
            "region": {"attributes": {"name": {"ru": "Самарская область"}, "regionType": {"enumerationCode": "obl."}}},
            "city": {"attributes": {"name": {"ru": "Самара"}, "cityType": {"enumerationCode": "g."}}},
            "street": {"attributes": {"name": {"ru": "Полевая"}, "streetType": {"enumerationCode": "ul."}}},
            "house": {"attributes": {"houseType": {"enumerationCode": "d."}, "number": {"ru": random_number}}},
        },
        "parentAddressId": russia_address_id,
    }
    try:
        request = request_context.post(
            url=f"{base_url_api}/openapi/v1/locationManagement/addresses", headers=headers, data=payload
        )
        api_addresses.check_response_status(request, 200, "Не выполнен запрос на создание нового адреса в LAM")
    except AssertionError:
        payload["elements"]["house"]["attributes"]["number"]["ru"] = random_number + 1
        request = request_context.post(
            url=f"{base_url_api}/openapi/v1/locationManagement/addresses", headers=headers, data=payload
        )
        api_addresses.check_response_status(request, 200, "Не выполнен запрос на создание нового адреса в LAM")
    response = request.json()
    return response
