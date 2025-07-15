import pytest
from playwright.sync_api import APIRequestContext

from api.requests.lis_requests.generate_ip_addresses import IpAddressRequests


@pytest.fixture(scope="function")
def add_new_ip_addresses_to_lis(
    request: pytest.FixtureRequest, api_request_auth_context: APIRequestContext
) -> str | list:
    ip_address_request = IpAddressRequests(api_request_auth_context)
    ip_count = getattr(request, "param", 1)
    return ip_address_request.generate_ip_addresses(ip_count)
