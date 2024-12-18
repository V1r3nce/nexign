import allure
import pytest
from common.env_helper import BASE_URL_API, UserData
from playwright.sync_api import Page, expect, sync_playwright, APIRequestContext
from pages.locators.login_page import LoginForm


@pytest.fixture(scope="function", autouse=True)
def stand_login(page: Page, base_url: str):
    page.goto(base_url)
    # page.set_viewport_size({'width': 1920, 'height': 1080})
    page.locator(LoginForm.LOGIN).click()
    page.keyboard.type(UserData.login)
    page.locator(LoginForm.PASSWORD).click()
    page.keyboard.type(UserData.password)
    page.locator(LoginForm.SUBMIT).click()
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


@pytest.fixture()
def base_url_api():
    return BASE_URL_API


@pytest.fixture(scope="function")
def api_request_auth_context(page: Page, base_url_api: str):
    request_context = page.request
    payload = f'grant_type=password&username={UserData.login}&password={UserData.password}'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'Authorization': 'Basic YXBpX2dhdGV3YXk6MTExMQ=='
    }
    auth_response = request_context.post(f"{base_url_api}/connect/token", headers=headers,
                                         data=payload)
    auth_json = auth_response.json()
    token = auth_json.get("access_token")
    if not token:
        raise AssertionError("Не получен токен авторизации")
    page.set_extra_http_headers(headers={"Authorization": f"Bearer {token}"})
    request_context = page.request
    yield request_context
    request_context.dispose()

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call":
        if rep.failed:
            page = item.funcargs.get("page")
            if page:
                allure.attach(page.screenshot(), name=f"screenshot-{item.nodeid}.png", attachment_type=allure.attachment_type.PNG)
