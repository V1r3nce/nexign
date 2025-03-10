import pytest
from playwright.sync_api import Page

from common.const import Constants
from common.helpers.env_helper import BASE_URL_LIS
from pages.locators.lis_locators.home_elements_lis import HomeElementsLis
from tests.conftest import remote_driver


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
