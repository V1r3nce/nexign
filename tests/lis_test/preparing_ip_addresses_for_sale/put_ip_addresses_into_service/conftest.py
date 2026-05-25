import pytest

from api.lis_requests.ip_addresses import IpAddressRequests
from models.stand_context import stand_context


@pytest.fixture(scope="function")
def add_new_ip_addresses_to_lis(request: pytest.FixtureRequest) -> str | list:
    ip_address_request = IpAddressRequests()
    ip_count = getattr(request, "param", 1)
    return ip_address_request.generate_closed_ip_address(apn=stand_context.stand_equipment.default_apn, count=ip_count)[
        0
    ]
