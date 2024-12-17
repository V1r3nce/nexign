import pytest
from playwright.sync_api import APIRequestContext

from common.string_helper import generate_random_number, generate_russian_string


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
def create_user(api_request_auth_context: APIRequestContext):
    """Возвращает id созданного пользователя в виде str"""
    headers = {"Content-Type": "application/json"}
    random_name = "Авто" + generate_russian_string(7)
    payload = {"businessActivity": {},
               "party": {"biometricData": False, "birthDate": "1983-07-11", "gender": {"genderId": 1},
                         "identificationDocument": {"number": "777777", "series": "7777",
                                                    "type": {"identificationTypeId": 5}}, "isResident": True,
                         "nameInfo": {"firstName": "Андрей", "patronymic": "", "surname": random_name},
                         "nationality": {"nationalityId": 1}, "publicOfficial": False,
                         "speakingLanguage": {"languageId": 3}, "taxRegistrationCertificate": {}}, "type": "INDIVIDUAL"}
    request = api_request_auth_context.post(url="http://srv8-saiddeskbo:47225/openapi/v1/customerManagement/customers",
                                            headers=headers, data=payload)
    assert request.status == 200, "Не выполнен запрос на создание нового клиента ФЛ"
    payload_add_places = {"addressString": "Россия, Ленинградская обл., г. Санкт-петербург, ул. Уральская",
                          "entity": {"code": "customer", "id": request.json()['customerId']}, "externalAddressId": 13,
                          "type": {"placeTypeId": 1}}
    places = api_request_auth_context.post(url="http://srv8-saiddeskbo:47225/openapi/v1/customerManagement/places",
                                           headers=headers, data=payload_add_places)
    assert places.status == 200, "Не добавлен адрес регистрации для созданного клиента"
    response = request.json()['customerId']
    return response
