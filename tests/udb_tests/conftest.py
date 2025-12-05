import pytest
from playwright.sync_api import Page

from common.helpers.env_helper import BASE_URL_UDB, UserData
from pages.locators.udb_locators.login_elements_udb import LoginFormUdb
from pages.udb_pages.billing_tasks_page import BillingTasksPage


@pytest.fixture()
def stand_login_udb(page: Page):
    page.goto(f"{BASE_URL_UDB}/bia/tasks")
    login_page_udb = LoginFormUdb()
    uds_tasks_page = BillingTasksPage()
    login_page_udb.LOGIN.fill(UserData.login)
    page.locator(login_page_udb.PASSWORD.path).click()
    page.keyboard.type(UserData.password)
    login_page_udb.SUBMIT.click()
    uds_tasks_page.locators.TITLE.wait_to_have_text("Биллинг")
    yield page
