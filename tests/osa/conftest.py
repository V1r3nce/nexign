import pytest
from playwright.sync_api import Page

from common.helpers.env_helper import BASE_URL_OSA
from pages.locators.osa_locators.home_page_osa import HomeOsaElements


@pytest.fixture()
def stand_login_osa(api_request_context, page: Page) -> Page:
    page.goto(BASE_URL_OSA)
    home_page = HomeOsaElements()
    home_page.HEADER_LOGO.wait_to_be_visible(timeout=15000)
    yield page
