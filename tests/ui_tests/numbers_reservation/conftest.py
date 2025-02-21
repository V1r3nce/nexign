from dataclasses import dataclass

import pytest
from playwright.sync_api import APIRequestContext, Page

from api.requests.personal_account_requests import PersonalAccountRequests, PersonalAccountData
from common.const import Constants
from common.helpers.data_generator import get_current_datetime_string_for_api
from common.helpers.env_helper import BASE_URL_LIS
from pages.locators.lis_locators.home_elements_lis import HomeElementsLis
from tests.conftest import remote_driver
from tests.ui_tests.manage_address_info.conftest import create_user


@dataclass
class ClientInfo:
    user_id: int = 0
    agreement_id: int = 0
    agreement_number: int = 0
    account_id: int = 0
    account_number: int = 0

@pytest.fixture(scope="function")
def create_account(create_user: int, api_request_auth_context: APIRequestContext) -> ClientInfo:
    client = ClientInfo(create_user)
    personal_account_api = PersonalAccountRequests(api_request_auth_context)
    date = get_current_datetime_string_for_api(is_full_format=False)
    client.agreement_id, client.agreement_number = personal_account_api.create_agreement(client.user_id, date)
    account_data = PersonalAccountData(
        agreement_id=client.agreement_id,
        is_cash_payment_enabled=False
    )
    client.account_id, client.account_number = personal_account_api.create_personal_account(account_data)
    return client

@pytest.fixture(scope="function")
def lis_stand_login_new_page(page: Page):
    lis_page = page.context.new_page()
    if remote_driver == "MOON": lis_page.set_viewport_size({"width": 1920, "height": 1080})
    lis_page.set_default_timeout(Constants.DEFAULT_TIMEOUT)

    lis_page.goto(f"{BASE_URL_LIS}/ps/ng-urw/index.html")
    home_page_lis = HomeElementsLis(lis_page)
    home_page_lis.SIM_SHIPPING_BTN.wait_to_be_visible(timeout=20000)
    yield lis_page
    lis_page.close()
