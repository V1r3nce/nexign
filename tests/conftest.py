from typing import Dict

import pytest
from common.selector.welcome import WelcomePage
from _pytest.fixtures import SubRequest
from playwright.sync_api import Page, Playwright
from common.const import Constants
import time


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
    """This fixture allows setting browser context arguments for Playwright.

    Args:
        browser_context_args (dict): Base browser context arguments.
        request (SubRequest): Pytest request object to get the 'browser_context_args' fixture value.
        base_url (str): The base URL for the application under test.
    Returns:
        dict: Updated browser context arguments.
    See Also:
        https://playwright.dev/python/docs/api/class-browser#browser-new-contex

    Returns:
        dict: Updated browser context arguments.
    """
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
    """Fixture to set browser launch arguments.

    This fixture updates the browser launch arguments to start the browser maximized
    and sets the test ID attribute for selectors.

    Args:
        browser_type_launch_args (Dict): Original browser type launch arguments.
        playwright (Playwright): The Playwright instance.

    Returns:
        Dict: Updated browser type launch arguments with maximized window setting.

    Note:
        This fixture has a session scope, meaning it will be executed once per test session.

    See Also:
        https://playwright.dev/python/docs/api/class-browsertype#browser-type-launch
    """
    playwright.selectors.set_test_id_attribute("data-test")
    return {**browser_type_launch_args, "args": ["--start-maximized"]}

# @pytest.hookimpl(tryfirst=True, hookwrapper=True)
# def pytest_runtest_makereport(item: Item):
#     """Hook implementation to generate test report for each test phase.
#
#     Args:
#         item: Pytest item object.
#
#     Yields:
#         Outcome of the test execution.
#     """
#     outcome = yield
#     rep = outcome.get_result()
#     setattr(item, f"rep_{rep.when}", rep)
