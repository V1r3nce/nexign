import allure
import pytest
from common.env_helper import BASE_URL_API, UserData, BASE_URL
from playwright.sync_api import Page, sync_playwright, APIRequestContext


def pytest_addoption(parser):
    parser.addoption(
        "--headless", action="store_true", default=False, help="headless mode"
    )


@pytest.fixture(scope="session")
def context(request):
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(channel='chrome', headless=request.config.getoption("--headless"))
    yield browser
    browser.close()


@pytest.fixture(scope="function")
def api_request_context(page: Page) -> APIRequestContext:
    request_context = page.request
    yield request_context
    request_context.dispose()


@pytest.fixture(scope="session")
def base_url_api():
    return BASE_URL_API

@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


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
    """Прикрепляет скриншот после падения теста к allure отчету."""
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call":
        if rep.failed:
            page = item.funcargs.get("page")
            if page:
                allure.attach(page.screenshot(), name=f"screenshot-{item.nodeid}.png", attachment_type=allure.attachment_type.PNG)
