import pytest
from playwright.sync_api import APIRequestContext

from api.requests.address_requests import AddressRequests
from common.helpers.data_generator import generate_random_number


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
        assert request.status == 200, "Не выполнен запрос на создание нового адреса в LAM"
    except AssertionError:
        payload["elements"]["house"]["attributes"]["number"]["ru"] = random_number + 1
        request = request_context.post(
            url=f"{base_url_api}/openapi/v1/locationManagement/addresses", headers=headers, data=payload
        )
        assert request.status == 200, "Не выполнен запрос на создание нового адреса в LAM"
    response = request.json()
    return response
