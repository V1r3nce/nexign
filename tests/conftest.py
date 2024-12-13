import pytest
from pages.locators.welcome import WelcomePage
from playwright.sync_api import Page, expect, sync_playwright


@pytest.fixture(scope="function", autouse=True)
def stand_login(page: Page, base_url: str):
    page.goto(base_url)
    page.locator(f"id={WelcomePage.input_login}").click()
    page.keyboard.type('Admin')
    page.locator(f"id={WelcomePage.input_password}").click()
    page.keyboard.type('1111')
    page.locator('button:text("Войти")').click()
    expect(page).to_have_title('Nexign UI')


def pytest_addoption(parser):
    parser.addoption(
        "--headless", action="store_true", default=False, help="headless mode"
    )


@pytest.fixture(scope="session")
def context(request):
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=request.config.getoption("--headless"))
    yield browser
#
# import pytest
# from playwright.sync_api import sync_playwright, Page, APIRequestContext
#
#
# @pytest.fixture(scope="function")
# def browser_context():
#     with sync_playwright() as p:
#         browser = p.chromium.launch(channel='chrome', headless=False)
#         context_options = {
#             "user_agent": "Chrome/131.0.6778.85",
#             "viewport": {"width": 1920, "height": 1080},
#             "locale": "en-US",
#             "timezone_id": "Europe/Moscow",
#             "permissions": ["geolocation"]
#         }
#
#         context = browser.new_context(**context_options)
#         yield context
#         context.close()
#         browser.close()

#
# @pytest.fixture(scope="function")
# def browser(browser_context) -> Page:
#     page = browser_context.new_page()
#     yield page
#     page.close()
#
#
# @pytest.fixture(scope="function")
# def api_request_context(browser_context) -> APIRequestContext:
#     request_context = browser_context.request
#     yield request_context
#     request_context.dispose()
