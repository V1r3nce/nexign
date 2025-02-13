import pytest
from playwright.sync_api import Page

from api.requests.lis_requests.phone_numbers import PhoneNumbersRequests
from common.helpers.env_helper import UserData, BASE_URL_LIS
from common.helpers.time_helpers import delay
from pages.locators.lis_locators.home_elements_lis import HomeElementsLis
from pages.locators.lis_locators.login_elements_lis import LoginFormLis


@pytest.fixture(scope="function")
def stand_login_lis(page: Page):
    page.goto(f"{BASE_URL_LIS}/ps/ng-urw/index.html")
    login_page_lis = LoginFormLis(page)
    home_page_lis = HomeElementsLis(page)
    login_page_lis.LOGIN.fill(UserData.login)
    page.locator(login_page_lis.PASSWORD.path).click()
    page.keyboard.type(UserData.password)
    login_page_lis.SUBMIT.click()
    home_page_lis.SIM_SHIPPING_BTN.wait_to_be_visible(timeout=20000)
    yield page


@pytest.fixture
def remove_number_search_templates(api_request_auth_context):
    """Фикстура для удаления шаблонов поиска номеров до и после теста"""
    phones_api = PhoneNumbersRequests(api_request_auth_context)
    templates = phones_api.get_phone_numbers_templates()
    template_items = templates.json()["items"]
    if len(template_items) > 0:
        for item in template_items:
            phones_api.delete_phone_numbers_template(item["phoneNumberFiltersTemplateId"])
            delay(.5, reason="Для корректной отработки запросов")
    yield template_items
    templates_after = phones_api.get_phone_numbers_templates()
    template_items_after = templates_after.json()["items"]
    if len(template_items_after) > 0:
        for item in template_items_after:
            phones_api.delete_phone_numbers_template(item["phoneNumberFiltersTemplateId"])
            delay(.5, reason="Для корректной отработки запросов")
