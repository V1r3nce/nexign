from dataclasses import dataclass

from playwright.sync_api import Page, expect

from api.exceptions import ClientNotFoundException, UpdateStatusException
from api.requests.personal_account_requests import PersonalAccountRequests, PersonalAccountData
from common.helpers.checker import wait_that
from common.helpers.env_helper import UserData
from pages.locators.login_page import LoginForm
import allure
import pytest
from playwright.sync_api import APIRequestContext

from api.requests.client_requests import ClientRequests
from common.helpers.data_generator import generate_russian_string, get_current_datetime_string_for_api
from common.helpers.time_helpers import delay
from models.address_info import BasicSystemAddress


@pytest.fixture(scope="function")
def nexign_ui_stand_login(page: Page, base_url: str):
    page.goto(base_url)
    login_page = LoginForm(page)
    login_page.LOGIN.fill(UserData.login)
    page.locator(login_page.PASSWORD.path).click()
    page.keyboard.type(UserData.password)
    login_page.SUBMIT.click()
    expect(page).to_have_title('Nexign UI', timeout=15000)
    yield page


@allure.step("API: Создание нового клиента")
@pytest.fixture(scope="function")
def create_user(api_request_auth_context: APIRequestContext, base_url_api: str, request):
    """
    Метод создает нового Клиента с фамилией Авто...

    Parameters:
    api_request_auth_context (APIRequestContext): объект контекста Playwright.
    base_url_api (str): URL стенда.

    Returns:
    int: id нового Клиента.
    """
    address = getattr(request, 'param', BasicSystemAddress.address)

    headers = {"Content-Type": "application/json"}
    random_name = "Авто" + generate_russian_string(7)
    payload = {
        "businessActivity": {},
        "party": {
            "biometricData": False,
            "birthDate": "1983-07-11",
            "gender": {"genderId": 1},
            "identificationDocument": {
                "number": "777777", "series": "7777",
                "type": {"identificationTypeId": 5}
            },
            "isResident": True,
            "nameInfo": {
                "firstName": "Андрей",
                "patronymic": "",
                "surname": random_name
            },
            "nationality": {"nationalityId": 1},
            "publicOfficial": False,
            "speakingLanguage": {"languageId": 3},
            "taxRegistrationCertificate": {
                "taxIdentificationNumber": "123123123123"
            }
        },
        "type": "INDIVIDUAL"
    }
    client_api = ClientRequests(api_request_auth_context)
    request = client_api.post(url=f"{base_url_api}/openapi/v1/customerManagement/customers",
                                            headers=headers, data=payload)
    assert request.status == 200, "Не выполнен запрос на создание нового клиента ФЛ"
    payload_add_places = {
        "addressString": address,
        "entity": {
            "code": "customer",
            "id": request.json()['customerId']
        },
        "externalAddressId": 13,
        "type": {"placeTypeId": 1}
    }
    places = client_api.post(url=f"{base_url_api}/openapi/v1/customerManagement/places",
                                           headers=headers, data=payload_add_places)
    assert places.status == 200, "Не добавлен адрес регистрации для созданного клиента"
    customer_id = request.json()['customerId']

    wait_that(
        lambda: client_api.get_client_data(customer_id).status == 200,
        timeout=5, sleep_seconds=0.5, exception=ClientNotFoundException,
        message="Пользователь не был создан в установленное время")
    delay(1, reason="UI не успевает за API")
    return customer_id


@dataclass
class ClientInfo:
    user_id: int = 0
    agreement_id: int = 0
    agreement_number: int = 0
    account_id: int = 0
    account_number: int = 0


@pytest.fixture(scope="function")
def create_user_with_agreement_and_account(create_user: int, api_request_auth_context: APIRequestContext) -> ClientInfo:
    """Фикстура создает пользователя, создает договор и личный счёт для него"""
    client = ClientInfo(create_user)
    personal_account_api = PersonalAccountRequests(api_request_auth_context)
    date = get_current_datetime_string_for_api(is_full_format=False)
    client.agreement_id, client.agreement_number = personal_account_api.create_agreement(client.user_id, date)
    account_data = PersonalAccountData(
        agreement_id=client.agreement_id,
        is_cash_payment_enabled=False
    )
    client.account_id, client.account_number = personal_account_api.create_personal_account(account_data)
    wait_that(lambda:
              personal_account_api.get_personal_accounts("customer", client.user_id).json()["items"][0][
                  "accountId"] == client.account_id,
              exception=UpdateStatusException, timeout=10, sleep_seconds=0.5,
              message="Аккаунт не создался в указанное время")
    return client


@pytest.fixture(scope="function")
def create_user_with_agreement_and_usd_account(create_user: int,
                                               api_request_auth_context: APIRequestContext) -> ClientInfo:
    """Фикстура создает пользователя, создает договор и личный счёт для него в валюте USD"""
    client = ClientInfo(create_user)
    personal_account_api = PersonalAccountRequests(api_request_auth_context)
    date = get_current_datetime_string_for_api(is_full_format=False)
    client.agreement_id, client.agreement_number = personal_account_api.create_agreement(client.user_id, date)
    account_data = PersonalAccountData(
        agreement_id=client.agreement_id,
        is_cash_payment_enabled=False,
        currency_id=2
    )
    client.account_id, client.account_number = personal_account_api.create_personal_account(account_data)
    wait_that(lambda:
              personal_account_api.get_personal_accounts("customer", client.user_id).json()["items"][0][
                  "currency"]["name"] == "USD",
              exception=UpdateStatusException, timeout=10, sleep_seconds=0.5,
              message="Аккаунт не создался в указанное время")
    return client
