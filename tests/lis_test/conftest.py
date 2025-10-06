from dataclasses import dataclass
from pathlib import Path
from typing import Any, Generator

import pytest
from playwright.sync_api import APIRequestContext, APIResponse, Page

from api.lis_requests import SimCardsRequests
from api.lis_requests.phone_numbers import PhoneNumbersRequests
from common.helpers.env_helper import BASE_URL_LIS, UserData
from common.helpers.time_helpers import delay
from pages.locators.lis_locators.home_elements_lis import HomeElementsLis
from pages.locators.lis_locators.login_elements_lis import LoginFormLis
from pages.locators.lis_locators.sim_cards_shipment import SimCardShipmentElementsLis


@pytest.fixture(scope="function")
def stand_login_lis(page: Page) -> Page:
    page.goto(f"{BASE_URL_LIS}/ps/ng-urw/index.html")
    login_page_lis = LoginFormLis(page)
    home_page_lis = HomeElementsLis(page)
    sim_shipment_lis = SimCardShipmentElementsLis(page)
    login_page_lis.LOGIN.fill(UserData.login)
    page.locator(login_page_lis.PASSWORD.path).click()
    page.keyboard.type(UserData.password)
    login_page_lis.SUBMIT.click()
    home_page_lis.SIM_SHIPPING_BTN.wait_to_be_visible(timeout=20000)
    sim_shipment_lis.TITLE.wait_to_have_text("Отгрузка SIM-карт")
    yield page


@pytest.fixture
def remove_number_search_templates(api_request_context: APIRequestContext) -> list[dict]:
    """Фикстура для удаления шаблонов поиска номеров до и после теста"""
    phones_api = PhoneNumbersRequests(api_request_context)
    templates = phones_api.get_phone_numbers_templates()
    template_items = templates.json()["items"]
    if len(template_items) > 0:
        for item in template_items:
            phones_api.delete_phone_numbers_template(item["phoneNumberFiltersTemplateId"])
            delay(0.5, reason="Для корректной отработки запросов")
    yield template_items
    templates_after = phones_api.get_phone_numbers_templates()
    template_items_after = templates_after.json()["items"]
    if len(template_items_after) > 0:
        for item in template_items_after:
            phones_api.delete_phone_numbers_template(item["phoneNumberFiltersTemplateId"])
            delay(0.5, reason="Для корректной отработки запросов")


@pytest.fixture
def remove_sim_card_search_templates(api_request_context: APIRequestContext) -> None:
    """Фикстура для удаления шаблонов поиска SIM карт до и после теста"""
    sim_api = SimCardsRequests(api_request_context)
    sim_api.remove_all_search_templates()
    yield
    sim_api.remove_all_search_templates()


@pytest.fixture
def add_first_imsi_pool(api_request_context: APIRequestContext) -> None:
    """Добавление первого пула IMSI если новый стенд"""
    imsi_requests = SimCardsRequests(api_request_context)
    imsi_pools = imsi_requests.get_imsi_pools()
    if imsi_pools.status_text == "No Content":
        imsi_requests.add_imsi_pools(start_num="123456790000001", end_num="123456790000001")
    yield imsi_pools


@pytest.fixture
def change_first_uploaded_sim_project_to_common(api_request_context: APIRequestContext) -> None:
    """Изменить проект для загруженной первой SIM на Общий проект"""
    sim_requests = SimCardsRequests(api_request_context)
    sim_requests.change_first_uploaded_sim_project()


@pytest.fixture
def add_first_msisdn_8800(api_request_context: APIRequestContext) -> Generator[APIResponse, Any, None]:
    """Добавление первого пула MSISDN 8800 если новый стенд"""
    msisdn_requests = PhoneNumbersRequests(api_request_context, 0)
    imsi_pools = msisdn_requests.get_phone_numbers()
    if not imsi_pools.json()["items"]:
        msisdn_requests.add_phone_numbers(
            start_number="8000000002",
            count_number="1",
            type_def=False,
            phone_number_type_id=5,
            operator_id=100002,
            equipment_id=1,
            phone_number_type_link_id=3,
        )
    yield imsi_pools


@dataclass
class CreatedImsis:
    imsi_1: str
    imsi_2: str
    new_sims_file_path: Path | str
    ship_sims_file_path: Path | str
