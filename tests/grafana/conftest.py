import pytest
from playwright.sync_api import Page

from common.helpers.env_helper import BASE_URL_GRAFANA, UserData
from pages.locators.grafana.home_elements_grafana import HomeGrafanaElements
from pages.locators.grafana.login_elements_grafana import LoginFormGrafanaElements


@pytest.fixture()
def stand_login_grafana(api_request_context, page: Page) -> Page:
    page.goto(BASE_URL_GRAFANA)
    login_page = LoginFormGrafanaElements()
    home_page = HomeGrafanaElements()
    login_page.LOGIN.fill(UserData.login)
    login_page.PASSWORD.click()
    login_page.PASSWORD.type("admin")
    login_page.LOGIN_BTN.click()
    login_page.SKIP_BTN.wait_to_be_visible(timeout=15000)
    login_page.SKIP_BTN.click()
    home_page.APP_LOGO.wait_to_be_visible(timeout=15000)
    yield page
