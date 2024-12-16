from pathlib import Path

import pytest
from pages.locators.welcome import WelcomePage
from playwright.sync_api import Page, expect, sync_playwright, APIRequestContext


@pytest.fixture(scope="function", autouse=True)
def stand_login(page: Page, base_url: str):
    page.set_viewport_size({'width': 1920, 'height': 1080})
    page.goto(base_url)
    page.locator(f"id={WelcomePage.input_login}").click()
    page.keyboard.type('Admin')
    page.locator(f"id={WelcomePage.input_password}").click()
    page.keyboard.type('1111')
    page.locator('button:text("Войти")').click()
    expect(page).to_have_title('Nexign UI')
    yield page


def pytest_addoption(parser):
    parser.addoption(
        "--headless", action="store_true", default=False, help="headless mode"
    )


@pytest.fixture(scope="session")
def context(request):
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(channel='chrome', headless=request.config.getoption("--headless"))
    yield browser


@pytest.fixture(scope="function")
def api_request_context(page: Page) -> APIRequestContext:
    request_context = page.request
    yield request_context
    request_context.dispose()


@pytest.fixture(scope="function")
def api_request_auth_context(page: Page):
    request_context = page.request
    payload = 'grant_type=password&username=Admin&password=1111'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'Authorization': 'Basic YXBpX2dhdGV3YXk6MTExMQ=='
    }
    auth_response = request_context.post("http://srv8-saiddeskbo:47225/connect/token", headers=headers,
                                         data=payload)
    auth_json = auth_response.json()
    token = auth_json.get("access_token")
    if not token:
        raise AssertionError("Не получен токен авторизации")
    page.set_extra_http_headers(headers={"Authorization": f"Bearer {token}"})
    request_context = page.request
    yield request_context
    request_context.dispose()
