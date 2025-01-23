import pytest
from playwright.sync_api import Page

from common.helpers.env_helper import UserData, BASE_URL_LIS
from pages.locators.lis_locators.home_elements_lis import HomeElementsLis
from pages.locators.lis_locators.login_elements_lis import LoginFormLis


@pytest.fixture(scope="function")
def stand_login_lis(page: Page):
    page.goto(f"{BASE_URL_LIS}/ps/ng-urw/index.html")
    login_page_lis = LoginFormLis(page)
    home_page_lis = HomeElementsLis(page)
    login_page_lis.LOGIN.fill(UserData.login)
    page.locator(login_page_lis.PASSWORD.path).click()
    page.keyboard.type(UserData.password)
    login_page_lis.SUBMIT.click()
    home_page_lis.SIM_SHIPPING_BTN.wait_to_be_visible()
    yield page
