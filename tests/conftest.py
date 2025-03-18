import os
import urllib.parse
from pathlib import Path

import allure
import pytest

from common.const import Constants
from common.custom_allure_step import step_decorator
from common.helpers.download_helper import CheckFile
from common.helpers.env_helper import BASE_URL_API, BASE_URL, get_var_from_env, LOGS_FOLDER
from playwright.sync_api import Page, APIRequestContext, Playwright, BrowserContext
from importlib.metadata import version

from common.helpers.time_helpers import get_now_time
from common.logging import create_logger

test_run_mode = get_var_from_env("TEST_RUN_MODE")
remote_driver = get_var_from_env("REMOTE_DRIVER") if test_run_mode == "remote" else None

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

    if test_run_mode == "remote" and remote_driver == "MOON":
        browser = playwright.chromium.connect(moon_url_with_params)
    else:
        browser = playwright.chromium.launch(channel='chrome', headless=request.config.getoption("--headless"),
                                             args=["--start-maximized"])
    return browser

@pytest.fixture(scope="function")
def context(request, get_browser) -> BrowserContext:
    browser = get_browser
    context = browser.new_context(no_viewport=False if remote_driver == "MOON" and test_run_mode == "remote" else True)
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
            page_context = item.funcargs.get("page").context
            page = page_context.pages[-1]
            if page:
                try:
                    allure.attach(page.screenshot(), name=f"screenshot-{item.nodeid}.png",
                                  attachment_type=allure.attachment_type.PNG)
                except:
                    print(f"Не удалось сделать скриншот")
    elif rep.when == "teardown":
        log_file = Path(os.path.join(LOGS_FOLDER, item.name.replace("/", "_") + ".log"))
        if log_file.exists():
            allure.attach.file(log_file, name=log_file.name, attachment_type=allure.attachment_type.TEXT)

@pytest.fixture
def remove_file_from_download_folder():
    """Фикстура для удаления файла после теста из папки root/download"""
    file_names = []
    yield file_names
    for item in file_names:
        file_check = CheckFile(item)
        file_check.remove_file_from_download()

@pytest.fixture(autouse=True)
def create_log_file(request):
    test_name = request.node.name.replace("/", "_")
    create_logger(log_level=get_var_from_env("LOG_LEVEL", "INFO"), log_file_name=test_name + ".log")

    allure.step = step_decorator(allure.step)

@pytest.fixture(autouse=True, scope="session")
def clear_log_folder():
    for log in Path(LOGS_FOLDER).glob("*.log"):
        try:
            log.unlink()
        except FileNotFoundError:
            pass