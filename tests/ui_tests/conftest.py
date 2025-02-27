from playwright.sync_api import Page, expect

from common.helpers.env_helper import UserData
from pages.locators.login_page import LoginForm
import allure
import pytest
from playwright.sync_api import APIRequestContext
from waiting import wait

from api.requests.client_requests import ClientRequests
from common.helpers.data_generator import generate_russian_string
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
    address = getattr(request,'param', BasicSystemAddress.address)

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
    request = api_request_auth_context.post(url=f"{base_url_api}/openapi/v1/customerManagement/customers",
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
    places = api_request_auth_context.post(url=f"{base_url_api}/openapi/v1/customerManagement/places",
                                           headers=headers, data=payload_add_places)
    assert places.status == 200, "Не добавлен адрес регистрации для созданного клиента"
    customer_id = request.json()['customerId']
    client_api = ClientRequests(api_request_auth_context)
    wait(
        lambda: client_api.get_client_data(customer_id).status == 200,
        timeout_seconds=5, sleep_seconds=0.5,
        waiting_for="Пользователь не был создан в установленное время")
    delay(1, reason="UI не успевает за API")
    return customer_id
