import pytest
from playwright.sync_api import Page, expect

from common.helpers.env_helper import UserData
from pages.locators.login_page import LoginForm



@pytest.fixture(scope="function")
def nexign_ui_stand_login(page: Page, base_url: str):
    page.goto(base_url)
    login_page = LoginForm(page)
    login_page.LOGIN.fill(UserData.login)
    page.locator(login_page.PASSWORD.path).click()
    page.keyboard.type(UserData.password)
    login_page.SUBMIT.click()
    expect(page).to_have_title('Nexign UI', timeout=15000)
    yield page