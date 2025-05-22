import pytest
from playwright.sync_api import Page

from common.helpers.env_helper import BASE_URL_RFD, UserData
from pages.locators.rfd_locators.home_element_rfd import HomeElementsRfd
from pages.locators.rfd_locators.login_page_rfd import LoginFormRfd


@pytest.fixture(scope="function")
def stand_login_rfd(page: Page) -> Page:
    page.goto(f"{BASE_URL_RFD}/ps/refdata/")
    login_page = LoginFormRfd(page)
    home_page = HomeElementsRfd(page)
    login_page.LOGIN.fill(UserData.login)
    login_page.PASSWORD.click()
    login_page.PASSWORD.type(UserData.password)
    login_page.SUBMIT.click()
    home_page.REFDATA_LOGO.wait_to_be_visible(timeout=6000)
    yield home_page.page
