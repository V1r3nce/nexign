import pytest
from pages.locators.welcome import WelcomePage
from playwright.sync_api import Page, expect, sync_playwright, APIRequestContext


@pytest.fixture(scope="function")
def browser_context():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=False)
        context_options = {
            "user_agent": "Chrome/131.0.6778.85",
            "viewport": {"width": 1920, "height": 1080},
            "locale": "en-US",
            "timezone_id": "Europe/Moscow",
            "permissions": ["geolocation"]
        }

        context = browser.new_context(**context_options)
        yield context
        context.close()
        browser.close()


@pytest.fixture(scope="function")
def browser(browser_context) -> Page:
    page = browser_context.new_page()
    yield page
    page.close()


@pytest.fixture(scope="function")
def stand_login(browser: Page, base_url: str):
    browser.goto(base_url)
    browser.locator(f"id={WelcomePage.input_login}").click()
    browser.keyboard.type('Admin')
    browser.locator(f"id={WelcomePage.input_password}").click()
    browser.keyboard.type('1111')
    browser.locator('button:text("Войти")').click()
    expect(browser).to_have_title('Nexign UI')
    return browser


@pytest.fixture(scope="function")
def api_request_context(browser_context) -> APIRequestContext:
    request_context = browser_context.request
    yield request_context
    request_context.dispose()


@pytest.fixture(scope="function")
def api_request_auth_context(browser_context):
    request_context = browser_context.request
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
    browser_context.set_extra_http_headers(headers={"Authorization": f"Bearer {token}"})
    request_context = browser_context.request
    yield request_context
    request_context.dispose()
