import pytest

from api.lis_requests.ip_addresses import IpAddressRequests


@pytest.fixture(scope="function")
def add_new_ip_addresses_to_lis(request: pytest.FixtureRequest) -> str | list:
    ip_address_request = IpAddressRequests()
    ip_count = getattr(request, "param", 1)
    return ip_address_request.generate_ip_addresses(ip_count)
