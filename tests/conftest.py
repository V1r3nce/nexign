import os
import urllib.parse

import allure
import pytest

from common.const import Constants
from common.helpers.download_helper import CheckFile
from common.helpers.env_helper import BASE_URL_API, UserData, BASE_URL, get_var_from_env
from playwright.sync_api import Page, APIRequestContext, expect, Playwright, BrowserContext
from importlib.metadata import version

from common.helpers.time_helpers import get_now_time
from pages.locators.login_page import LoginForm

remote_driver = get_var_from_env("REMOTE_DRIVER")
test_run_mode = get_var_from_env("TEST_RUN_MODE")

if remote_driver == "SELENOID" and test_run_mode == "remote":
    os.environ["SELENIUM_REMOTE_URL"] = "http://srv8-triptindus:4444/wd/hub"
    os.environ['SELENIUM_REMOTE_CAPABILITIES'] = \
        f'''
        {{"selenoid:options":
            {{
                "name":"{get_now_time()}", 
                "enableVNC": true, 
                "enableVideo": false, 
                "sessionTimeout": "5m"
            }}
        }}
        '''

@pytest.fixture()
def moon_url_with_params(request):
    if remote_driver == "MOON":
        remote_driver_host = get_var_from_env(f"{remote_driver}_HOST")

        moon_url = f"ws://{remote_driver_host}/playwright/chrome/playwright-{version('playwright')}"

        params = {
            'headless': f"{request.config.getoption('--headless')}",
            'name': f"{request.node.name} | {get_now_time()}"
        }
        url_params = urllib.parse.urlencode(params, doseq=True)
        ws_url = f"{moon_url}?{url_params}"
        return ws_url


def pytest_addoption(parser):
    parser.addoption(
        "--headless", action="store_true", default=False, help="headless mode"
    )

@pytest.fixture()
def get_browser(request, playwright: Playwright, moon_url_with_params):
    """Фикстура отвечающая за запуск браузера, в зависимости от режима запуска (локальный или удаленный)
    и удаленного драйвера (если выбран удаленный режим)"""

    if test_run_mode == "local":
        browser = playwright.chromium.launch(channel='chrome', headless=request.config.getoption("--headless"),
                                             args=["--start-maximized"])
    else:
        if remote_driver == "MOON":
            browser = playwright.chromium.connect(moon_url_with_params)
        else:
            browser = playwright.chromium.launch(channel='chrome', headless=request.config.getoption("--headless"),
                                                 args=["--start-maximized"])

    return browser

@pytest.fixture(scope="function")
def context(request, get_browser) -> BrowserContext:
    browser = get_browser
    context = browser.new_context(no_viewport=False if remote_driver == "MOON" else True)
    yield context
    context.close()
    browser.close()


@pytest.fixture(scope="function")
def page(context: BrowserContext) -> Page:
    page = context.new_page()
    if remote_driver == "MOON": page.set_viewport_size({"width": 1920, "height": 1080})
    page.set_default_timeout(Constants.DEFAULT_TIMEOUT)
    yield page
    page.close()


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


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Прикрепляет скриншот после падения теста к allure отчету."""
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call":
        if rep.failed:
            page = item.funcargs.get("page")
            if page:
                allure.attach(page.screenshot(), name=f"screenshot-{item.nodeid}.png",
                              attachment_type=allure.attachment_type.PNG)


@pytest.fixture
def remove_file_from_download_folder():
    """Фикстура для удаления файла после теста из папки root/download"""
    file_names = []
    yield file_names
    for item in file_names:
        file_check = CheckFile(item)
        file_check.remove_file_from_download()
