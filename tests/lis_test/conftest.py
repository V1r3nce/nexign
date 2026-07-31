from dataclasses import dataclass
from pathlib import Path

import pytest
from playwright.sync_api import Page

from api.lis_requests.phone_numbers import PhoneNumbersRequests
from api.lis_requests.sim_cards import SimCardsRequests
from common.helpers.env_helper import BASE_URL_LIS, UserData
from common.helpers.time_helpers import delay
from db.requests.db_requests import LisDBRequests
from pages.locators.lis_locators.home_elements_lis import HomeLisElements
from pages.locators.lis_locators.login_elements_lis import LoginFormLisElements
from pages.locators.lis_locators.sim_cards_shipment import SimCardShipmentLisElements


@pytest.fixture()
def stand_login_lis(api_request_context, page: Page) -> Page:
    page.goto(f"{BASE_URL_LIS}/ps/ng-urw/index.html")
    login_page_lis = LoginFormLisElements()
    home_page_lis = HomeLisElements()
    sim_shipment_lis = SimCardShipmentLisElements()
    login_page_lis.LOGIN.fill(UserData.login)
    page.locator(login_page_lis.PASSWORD.path).click()
    page.keyboard.type(UserData.password)
    login_page_lis.SUBMIT.click()
    home_page_lis.SIM_SHIPPING_BTN.wait_to_be_visible(timeout=20000)
    sim_shipment_lis.TITLE.wait_to_have_text("Отгрузка SIM-карт")
    yield page


@pytest.fixture
def remove_number_search_templates() -> list[dict]:
    """Фикстура для удаления шаблонов поиска номеров до и после теста"""
    phones_api = PhoneNumbersRequests()
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
def remove_sim_card_search_templates() -> None:
    """Фикстура для удаления шаблонов поиска SIM карт до и после теста"""
    sim_api = SimCardsRequests()
    sim_api.remove_all_search_templates()
    yield
    sim_api.remove_all_search_templates()


@pytest.fixture
def add_first_imsi_pool() -> None:
    """Добавление первого пула IMSI если новый стенд"""
    imsi_requests = SimCardsRequests()
    imsi_pools = imsi_requests.get_imsi_pools()
    if imsi_pools.status_code == 204:
        imsi_requests.add_imsi_pools(start_num="123456790000001", end_num="123456790000001")
    yield imsi_pools


@pytest.fixture
def change_first_uploaded_sim_project_to_common() -> None:
    """Изменить проект для загруженной первой SIM на Общий проект"""
    sim_requests = SimCardsRequests()
    sim_requests.change_first_uploaded_sim_project()


@dataclass
class CreatedImsis:
    imsi_1: str
    imsi_2: str
    new_sims_file_path: Path | str
    ship_sims_file_path: Path | str


@pytest.fixture(scope="function")
def create_lis_db_connection() -> LisDBRequests:
    """
    Фикстура возвращает инстанс класса LisDBRequests,
    а также закрывает соединение после конца работы теста.
    """
    instance = LisDBRequests()
    instance.connect()
    yield instance
    instance.curr_conn.close()
