import pytest
from playwright.sync_api import Page, APIRequestContext

from common.string_helper import generate_random_number


@pytest.fixture(scope="function")
def get_start_page(browser) -> Page:
    page = browser.goto("http://srv8-saiddeskbo:47132/nus/openid/index.html?form=login&")
    yield page


@pytest.fixture(scope="function")
def add_new_address_to_lam(api_request_auth_context: tuple[APIRequestContext, dict[str, str]]):
    """Возвращает созданный адрес в виде словаря {'addressId': int, 'addressString': str}"""
    request_context, headers = api_request_auth_context
    headers["Content-Type"] = "application/json"
    random_number = generate_random_number(3)
    payload = {"classifierCode": "addresses", "elements": {
        "region": {"attributes": {"name": {"ru": "Самарская область"}, "regionType": {"enumerationCode": "obl."}}},
        "city": {"attributes": {"name": {"ru": "Самара"}, "cityType": {"enumerationCode": "g."}}},
        "street": {"attributes": {"name": {"ru": "Полевая"}, "streetType": {"enumerationCode": "ul."}}},
        "house": {"attributes": {"houseType": {"enumerationCode": "d."}, "number": {"ru": random_number}}}},
               "parentAddressId": 1}
    request = request_context.post(url="http://srv8-saiddeskbo:47225/openapi/v1/locationManagement/addresses",
                                   headers=headers, data=payload)
    response = request.json()
    return response
