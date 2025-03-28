import pytest
from playwright.sync_api import APIRequestContext

from api.requests.lis_requests.generate_ip_addresses import generate_ip_addresses


@pytest.fixture(scope="function")
def add_new_ip_addresses_to_lis(
    request: pytest.FixtureRequest, api_request_auth_context: APIRequestContext, base_url_api: str
) -> str | list:
    ip_count = getattr(request, "param", 1)
    return generate_ip_addresses(api_request_auth_context, base_url_api, ip_count)
