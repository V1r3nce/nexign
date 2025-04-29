import pytest
from playwright.sync_api import Page

from common.helpers.env_helper import BASE_URL_PSC, UserData
from pages.locators.psc_locators.home_element_psc import HomeElementsPsc
from pages.locators.psc_locators.login_page_psc import LoginFormPsc


@pytest.fixture(scope="function")
def stand_login_pcs(page: Page) -> Page:
    page.goto(f"{BASE_URL_PSC}/ProductCatalog/ui/catalog/product-offering")
    login_page = LoginFormPsc(page)
    home_page = HomeElementsPsc(page)
    login_page.LOGIN.fill(UserData.login)
    login_page.PASSWORD.click()
    login_page.PASSWORD.type(UserData.password)
    login_page.SUBMIT.click()
    home_page.APP_LOGO.wait_to_be_visible()
    yield home_page.page
