import allure
import pytest
from common.env_helper import BASE_URL_API, UserData, BASE_URL
from playwright.sync_api import Page, sync_playwright, APIRequestContext, expect
from pages.locators.login_page import LoginForm


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


@pytest.fixture(scope="function", autouse=True)
def stand_login(page: Page, base_url: str):
    page.goto(base_url)
    login_page = LoginForm(page)
    login_page.LOGIN.fill(UserData.login)
    page.locator(login_page.PASSWORD.path).click()
    page.keyboard.type(UserData.password)
    login_page.SUBMIT.click()
    expect(page).to_have_title('Nexign UI')
    yield page
    page.close()


@pytest.fixture(scope="function")
def api_request_auth_context(page: Page) -> APIRequestContext:
    request_context = page.request
    yield request_context
    request_context.dispose()


@pytest.fixture(scope="session")
def base_url_api():
    return BASE_URL_API


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


# @pytest.hookimpl(tryfirst=True, hookwrapper=True)
# def pytest_runtest_makereport(item, call):
#     """Прикрепляет скриншот после падения теста к allure отчету."""
#     outcome = yield
#     rep = outcome.get_result()
#     if rep.when == "call":
#         if rep.failed:
#             page = item.funcargs.get("page")
#             if page:
#                 allure.attach(page.screenshot(), name=f"screenshot-{item.nodeid}.png",
#                               attachment_type=allure.attachment_type.PNG)
