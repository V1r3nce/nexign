from typing import Dict

import pytest
from pages.locators.welcome import WelcomePage
from _pytest.fixtures import SubRequest
from playwright.sync_api import Page, Playwright
from common.const import Constants


@pytest.fixture(scope="function", autouse=True)
def stand_login(page: Page, request: SubRequest, base_url: str):
    page.goto(base_url)
    page.locator(WelcomePage.input_login).fill('Admin')
    page.locator(WelcomePage.input_password).fill('1111')
    page.click(WelcomePage.login_submit)


@pytest.fixture(scope="function")
def browser_context_args(
        browser_context_args: Dict, base_url: str, request: SubRequest
):
    context_args = {
        **browser_context_args,
        "no_viewport": True,
        "user_agent": Constants.AUTOMATION_USER_AGENT,
    }

    if hasattr(request, "param"):
        context_args["storage_state"] = {
            "cookies": [
                {
                    "name": "session-username",
                    "value": request.param,
                    "url": base_url,
                }
            ]
        }
    return context_args


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args: Dict, playwright: Playwright):

    playwright.selectors.set_test_id_attribute("data-test")
    return {**browser_type_launch_args, "args": ["--start-maximized"]}
