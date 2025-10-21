import os
import urllib.parse
from importlib.metadata import version
from pathlib import Path

import allure
import pytest
from playwright.sync_api import APIRequestContext, Browser, BrowserContext, Page, Playwright

from common.const import Constants
from common.custom_allure_step import step_decorator
from common.helpers.download_helper import CheckFile
from common.helpers.env_helper import (
    BASE_URL,
    BASE_URL_API,
    HAR_DIR,
    LOGS_FOLDER,
    get_var_from_env,
)
from common.helpers.time_helpers import get_now_time
from common.logging import create_logger
from models.context import test_context

test_run_mode = get_var_from_env("TEST_RUN_MODE")
remote_driver = get_var_from_env("REMOTE_DRIVER") if test_run_mode == "remote" else None

if remote_driver == "SELENOID" and test_run_mode == "remote":
    os.environ["SELENIUM_REMOTE_URL"] = "http://srv8-triptindus:4444/wd/hub"
    os.environ["SELENIUM_REMOTE_CAPABILITIES"] = f'''
        {{"selenoid:options":
            {{
                "name":"{get_now_time()}",
                "enableVNC": true,
                "enableVideo": false,
                "sessionTimeout": "5m"
            }}
        }}
        '''


@pytest.fixture(scope="session")
def moon_url_with_params(request: pytest.FixtureRequest) -> str | None:
    if remote_driver == "MOON":
        remote_driver_host = get_var_from_env(f"{remote_driver}_HOST")

        moon_url = f"ws://{remote_driver_host}/playwright/chrome/playwright-{version('playwright')}"

        params = {
            "headless": f"{request.config.getoption('--headless')}",
            "name": get_now_time(),
        }
        url_params = urllib.parse.urlencode(params, doseq=True)
        ws_url = f"{moon_url}?{url_params}"
        return ws_url
    return None


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--headless", action="store_true", default=False, help="headless mode")


@pytest.fixture(scope="session")
def get_browser(request: pytest.FixtureRequest, playwright: Playwright, moon_url_with_params: str | None) -> Browser:
    """Фикстура отвечающая за запуск браузера, в зависимости от режима запуска (локальный или удаленный)
    и удаленного драйвера (если выбран удаленный режим)"""

    if test_run_mode == "remote" and remote_driver == "MOON":
        browser = playwright.chromium.connect(moon_url_with_params)
    else:
        browser = playwright.chromium.launch(
            channel="chrome", headless=request.config.getoption("--headless"), args=["--start-maximized"]
        )
    yield browser
    browser.close()


@pytest.fixture(scope="function")
def context(request: pytest.FixtureRequest, get_browser: Browser, test_name: str) -> BrowserContext:
    browser = get_browser
    context = browser.new_context(
        no_viewport=False if remote_driver == "MOON" and test_run_mode == "remote" else True,
        record_har_path=HAR_DIR / f"{test_name}.har",
        record_har_url_filter="**/openapi/**",
        record_har_mode="minimal",
    )
    context.set_default_timeout(Constants.DEFAULT_TIMEOUT)
    yield context

    context.close()


@pytest.fixture(scope="function")
def page(context: BrowserContext) -> Page:
    page = context.new_page()
    if remote_driver == "MOON":
        page.set_viewport_size({"width": 1920, "height": 1080})
    yield page
    page.close()


@pytest.fixture(scope="function")
def api_request_context(page: Page) -> APIRequestContext:
    request_context = page.request
    yield request_context
    request_context.dispose()


@pytest.fixture(scope="session")
def base_url_api() -> str:
    return BASE_URL_API


@pytest.fixture(scope="session")
def base_url() -> str:
    return BASE_URL


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo) -> None:
    """Прикрепляет скриншот после падения теста к allure отчету."""
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call":
        if rep.failed:
            try:
                page_context = item.funcargs.get("page").context
                page = page_context.pages[-1]
                if page:
                    allure.attach(
                        page.screenshot(),
                        name=f"screenshot-{item.nodeid}.png",
                        attachment_type=allure.attachment_type.PNG,
                    )
            except Exception as e:
                print(f"Failed to attach screenshot: {e}")
    elif rep.when == "teardown":
        log_file = Path(os.path.join(LOGS_FOLDER, item.name.replace("/", "_") + ".log"))
        har_file = Path(os.path.join(HAR_DIR, item.name.replace("/", "_") + ".har"))
        if log_file.exists():
            allure.attach.file(log_file, name=log_file.name, attachment_type=allure.attachment_type.TEXT)
        if har_file.exists():
            allure.attach.file(har_file, name=har_file.name, attachment_type=allure.attachment_type.JSON)


@pytest.fixture
def remove_file_from_download_folder() -> list:
    """Фикстура для удаления файла после теста из папки root/download"""
    file_names: list = []
    yield file_names
    for item in file_names:
        file_check = CheckFile(item)
        file_check.remove_file_from_download()


@pytest.fixture
def test_name(request: pytest.FixtureRequest) -> str:
    if request.node.name:
        name = request.node.name.replace("/", "_")
        test_context.test_name = name
        return name
    else:
        return ""


@pytest.fixture(autouse=True)
def create_log_file(request: pytest.FixtureRequest, test_name: str) -> None:
    create_logger(log_level=get_var_from_env("LOG_LEVEL", "INFO"), log_file_name=test_name + ".log")

    allure.step = step_decorator(allure.step)


@pytest.fixture(autouse=True, scope="session")
def clear_log_folder() -> None:
    for log in Path(LOGS_FOLDER).glob("*.log"):
        try:
            log.unlink()
        except FileNotFoundError:
            pass


@pytest.fixture(autouse=True, scope="session")
def clear_har_folder() -> None:
    for har in Path(HAR_DIR).glob("*.har"):
        try:
            har.unlink()
        except FileNotFoundError:
            pass
