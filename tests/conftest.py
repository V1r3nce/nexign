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