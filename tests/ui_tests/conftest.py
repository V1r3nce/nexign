import allure
import pytest
from playwright.sync_api import APIRequestContext, Page, expect

from api.exceptions import ClientNotFoundException, UpdateStatusException
from api.requests.address_requests import AddressRequests
from api.requests.attribute_requests import AttributeRequests
from api.requests.client_requests import ClientRequests
from api.requests.personal_account_requests import PersonalAccountData, PersonalAccountRequests
from common.helpers.checker import wait_that
from common.helpers.data_generator import (
    generate_random_number,
)
from common.helpers.env_helper import UserData
from common.helpers.time_helpers import delay
from models.user import IndividualClient, OrganizationClient
from pages.locators.home_page_elements import HomePage
from pages.locators.login_page import LoginForm


@pytest.fixture(scope="function")
def nexign_ui_stand_login(page: Page, base_url: str) -> Page:
    page.goto(base_url)
    login_page = LoginForm(page)
    home_page = HomePage(page)
    login_page.LOGIN.fill(UserData.login)
    page.locator(login_page.PASSWORD.path).click()
    page.keyboard.type(UserData.password)
    delay(0.5, reason="Не всегда успевает форма")
    login_page.SUBMIT.click()
    expect(page).to_have_title("Nexign UI", timeout=15000)
    home_page.USER_DROPDOWN_BTN.wait_to_be_visible(timeout=15000)
    yield page


@allure.step("API: Создание нового клиента ФЛ")
@pytest.fixture(scope="function")
def create_individual_user(
    api_request_auth_context: APIRequestContext,
    base_url_api: str,
    individual_user_data: IndividualClient,
    request: pytest.FixtureRequest,
) -> IndividualClient:
    """
    Метод создает нового Клиента

    Parameters:
    api_request_auth_context (APIRequestContext): объект контекста Playwright.
    base_url_api (str): URL стенда.

    Returns:
    IndividualClient: нового Клиента типа ФЛ.
    """
    user_data = individual_user_data
    address = getattr(request, "param", user_data.registration_address)
    api_addresses = AddressRequests(api_request_auth_context)

    headers = {"Content-Type": "application/json"}
    payload = {
        "businessActivity": {},
        "party": {
            "biometricData": False,
            "birthDate": user_data.birth_date_for_api,
            "birthPlace": user_data.birth_place,
            "gender": {"genderId": user_data.gender_id},
            "identificationDocument": {
                "dateOfIssue": user_data.issue_date_for_api,
                "providedByOrganization": user_data.document_provide_by,
                "divisionCode": user_data.document_division_code,
                "number": user_data.document_num,
                "series": user_data.document_serial,
                "type": {"identificationTypeId": user_data.document_type_id},
                "validFor": user_data.document_valid_date_for_api,
            },
            "isResident": user_data.is_resident_bool,
            "nameInfo": {
                "firstName": user_data.first_name,
                "patronymic": user_data.patronymic,
                "surname": user_data.sur_name,
            },
            "nationality": {"nationalityId": user_data.nationality_id},
            "publicOfficial": user_data.is_public_bool,
            "speakingLanguage": {"languageId": user_data.speaking_language_id},
            "taxRegistrationCertificate": {"taxIdentificationNumber": user_data.inn},
        },
        "type": "INDIVIDUAL",
    }
    client_api = ClientRequests(api_request_auth_context)
    request = client_api.post(
        url=f"{base_url_api}/openapi/v1/customerManagement/customers", headers=headers, data=payload
    )
    client_api.check_response_status(request, 200, "Не выполнен запрос на создание нового клиента ФЛ")
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
    user_data.user_id = customer_id
    return user_data


@allure.step("API: Создание нового клиента ЮЛ")
@pytest.fixture(scope="function")
def create_organization(
    api_request_auth_context: APIRequestContext,
    base_url_api: str,
    organization_user_data: OrganizationClient,
    request: pytest.FixtureRequest,
) -> OrganizationClient:
    """
    Метод создает нового Клиента типа Юридическое лицо с названием АвтоЮЛ_...

    Parameters:
    api_request_auth_context (APIRequestContext): объект контекста Playwright.
    base_url_api (str): URL стенда.

    Returns:
    OrganizationClient: нового Клиента типа ЮЛ.
    """
    api_addresses = AddressRequests(api_request_auth_context)
    user_data = organization_user_data
    address = getattr(request, "param", user_data.registration_address)

    headers = {"Content-Type": "application/json"}
    payload = {
        "additionalAttributes": [{"code": "isVIP", "value": user_data.is_vip_bool, "valueType": "BOOLEAN"}],
        "businessActivity": {},
        "businessInfo": {},
        "party": {
            "isResident": user_data.is_resident_bool,
            "nameInfo": {"corporateName": user_data.customer_name},
            "nationality": {"nationalityId": user_data.nationality_id},
            "proprietaryForm": {},
            "speakingLanguage": {"languageId": user_data.speaking_language_id},
            "taxRegistrationCertificate": {
                "taxIdentificationNumber": user_data.inn,
                "PSRN": user_data.ogrn,
            },
        },
        "type": "ORGANIZATION",
    }
    client_api = ClientRequests(api_request_auth_context)
    response = client_api.post(
        url=f"{base_url_api}/openapi/v1/customerManagement/customers", headers=headers, data=payload
    )
    client_api.check_response_status(response, 200, "Не выполнен запрос на создание нового клиента ЮЛ")
    api_addresses.add_base_address_to_client(address, response.json()["customerId"])
    customer_id = response.json()["customerId"]

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
    client_api.check_response_status(
        add_values, 200, "Не выполнен запрос на добавление значений дополнительных атрибутов для нового клиента ЮЛ"
    )

    wait_that(
        lambda: client_api.get_client_data(customer_id).status == 200,
        timeout=5,
        sleep_seconds=0.5,
        exception=ClientNotFoundException,
        message="Пользователь не был создан в установленное время",
    )
    delay(1, reason="UI не успевает за API")
    user_data.user_id = customer_id
    return user_data


@pytest.fixture(scope="function")
def create_user_with_agreement_and_account(
    create_individual_user: IndividualClient, api_request_auth_context: APIRequestContext
) -> IndividualClient:
    """Фикстура создает пользователя, создает договор и личный счёт для него"""
    client = create_individual_user
    personal_account_api = PersonalAccountRequests(api_request_auth_context)
    client.agreement_id, client.agreement_number = personal_account_api.create_agreement(
        client.user_id, client.date_for_api
    )
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
def create_user_with_postpaid_account(
    create_individual_user: IndividualClient, api_request_auth_context: APIRequestContext
) -> IndividualClient:
    """Фикстура создает пользователя, создает договор и личный счёт для него"""
    client = create_individual_user
    personal_account_api = PersonalAccountRequests(api_request_auth_context)
    client.agreement_id, client.agreement_number = personal_account_api.create_agreement(
        client.user_id, client.date_for_api
    )
    client.account_id, client.account_number = personal_account_api.create_personal_account(
        PersonalAccountData(
            agreement_id=client.agreement_id,
            raiting_type=2,
            threshold_break=2000,
            threshold_control=True,
        )
    )
    wait_that(
        lambda: personal_account_api.get_personal_accounts("customer", client.user_id).json()["items"][0]["accountId"]
        == client.account_id,
        exception=UpdateStatusException,
        timeout=10,
        sleep_seconds=0.5,
        message="Аккаунт не создался за 10 секунд",
    )
    return client


@pytest.fixture(scope="function")
def create_user_with_agreement_and_usd_account(
    create_individual_user: IndividualClient, api_request_auth_context: APIRequestContext
) -> IndividualClient:
    """Фикстура создает пользователя, создает договор и личный счёт для него в валюте USD"""
    client = create_individual_user
    personal_account_api = PersonalAccountRequests(api_request_auth_context)
    client.agreement_id, client.agreement_number = personal_account_api.create_agreement(
        client.user_id, client.date_for_api
    )
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
def create_agreement_and_account_for_user(
    api_request_auth_context: APIRequestContext, individual_user_data: IndividualClient
):
    """Фикстура создает для переданного пользователя договор и личный счёт"""

    def pass_user_id(user_id: int) -> IndividualClient:
        client = individual_user_data
        client.user_id = user_id
        personal_account_api = PersonalAccountRequests(api_request_auth_context)
        client.agreement_id, client.agreement_number = personal_account_api.create_agreement(
            client.user_id, client.date_for_api
        )
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


@pytest.fixture(scope="function")
def delete_additional_attributes(api_request_auth_context: APIRequestContext, base_url_api: str) -> list:
    """Фикстура удаляет на стенде все объекты класса Attribute из списка attributes. Объекты описывают дополнительные атрибуты
    Фикстура не учитывает ответы на запросы, так как туда могут поступать уже не существующие атрибуты.
    По сути нужна для того, чтобы в действующих атрибутах не было тестовых атрибутов, которые могут помешать другим тестам
    """
    api_attribute = AttributeRequests(api_request_auth_context)
    attributes: list = []
    yield attributes
    for attribute in attributes:
        if attribute.attr_type != "template":
            payload = {"entityTypeCode": attribute.attr_type, "isDeprecated": True}
        else:
            payload = {"isDeprecated": True}
        api_attribute.attribute_update_request(api_request_auth_context, base_url_api, attribute.name, payload)
