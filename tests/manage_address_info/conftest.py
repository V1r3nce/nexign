import pytest
from playwright.sync_api import APIRequestContext
from waiting import wait

from api.requests.client_requests import ClientRequests
from common.string_helper import generate_random_number, generate_russian_string
from common.time_helpers import delay
from models.address_info import BasicSystemAddress


@pytest.fixture(scope="function")
def add_new_address_to_lam(api_request_auth_context: APIRequestContext, base_url_api: str):
    """Возвращает созданный адрес в виде словаря {'addressId': int, 'addressString': str}"""
    request_context = api_request_auth_context
    headers = {"Content-Type": "application/json"}
    random_number = generate_random_number(3)
    payload = {"classifierCode": "addresses", "elements": {
        "region": {"attributes": {"name": {"ru": "Самарская область"}, "regionType": {"enumerationCode": "obl."}}},
        "city": {"attributes": {"name": {"ru": "Самара"}, "cityType": {"enumerationCode": "g."}}},
        "street": {"attributes": {"name": {"ru": "Полевая"}, "streetType": {"enumerationCode": "ul."}}},
        "house": {"attributes": {"houseType": {"enumerationCode": "d."}, "number": {"ru": random_number}}}},
               "parentAddressId": 1}
    try:
        request = request_context.post(url=f"{base_url_api}/openapi/v1/locationManagement/addresses",
                                       headers=headers, data=payload)
        assert request.status == 200, "Не выполнен запрос на создание нового адреса в LAM"
    except AssertionError:
        payload['elements']['house']['attributes']['number']['ru'] = random_number + 1
        request = request_context.post(url=f"{base_url_api}/openapi/v1/locationManagement/addresses",
                                       headers=headers, data=payload)
        assert request.status == 200, "Не выполнен запрос на создание нового адреса в LAM"
    response = request.json()
    return response


@pytest.fixture(scope="function")
def create_user(api_request_auth_context: APIRequestContext, base_url_api: str):
    """
    Метод создает нового Клиента с фамилией Авто...

    Parameters:
    api_request_auth_context (APIRequestContext): объект контекста Playwright.
    base_url_api (str): URL стенда.

    Returns:
    int: id нового Клиента.
    """
    headers = {"Content-Type": "application/json"}
    random_name = "Авто" + generate_russian_string(7)
    payload = {"businessActivity": {},
               "party": {"biometricData": False, "birthDate": "1983-07-11", "gender": {"genderId": 1},
                         "identificationDocument": {"number": "777777", "series": "7777",
                                                    "type": {"identificationTypeId": 5}}, "isResident": True,
                         "nameInfo": {"firstName": "Андрей", "patronymic": "", "surname": random_name},
                         "nationality": {"nationalityId": 1}, "publicOfficial": False,
                         "speakingLanguage": {"languageId": 3}, "taxRegistrationCertificate": {}}, "type": "INDIVIDUAL"}
    request = api_request_auth_context.post(url=f"{base_url_api}/openapi/v1/customerManagement/customers",
                                            headers=headers, data=payload)
    assert request.status == 200, "Не выполнен запрос на создание нового клиента ФЛ"
    payload_add_places = {"addressString": BasicSystemAddress.address,
                          "entity": {"code": "customer", "id": request.json()['customerId']}, "externalAddressId": 13,
                          "type": {"placeTypeId": 1}}
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
