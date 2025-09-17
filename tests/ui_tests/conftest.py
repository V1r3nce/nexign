import pytest
from playwright.sync_api import APIRequestContext, Page, expect

from api.nbss.address_requests import AddressRequests
from api.nbss.attribute_requests import AttributeRequests
from api.nbss.client_requests.client_requests import ClientRequests
from api.nbss.personal_account_requests import PersonalAccountRequests
from common.helpers.env_helper import UserData
from common.helpers.time_helpers import delay
from db.requests.db_requests import CrabDBRequests
from models.user import IndividualClient, OrganizationClient
from pages.locators.home_page_elements import HomePage
from pages.locators.login_page import LoginForm


@pytest.fixture(scope="function")
def nexign_ui_stand_login(page: Page, base_url: str) -> Page:
    page.goto(base_url)
    login_page = LoginForm(page)
    home_page = HomePage(page)
    login_page.LOGIN.fill(UserData.login)
    page.locator(login_page.PASSWORD.path).click()
    page.keyboard.type(UserData.password)
    login_page.SUBMIT.element_have_css_color("background-color", "deep_blue")
    delay(0.5, "Кнопка без задержки иногда не срабатывает")
    login_page.SUBMIT.click()
    expect(page).to_have_title("Nexign UI", timeout=15000)
    home_page.USER_DROPDOWN_BTN.wait_to_be_visible(timeout=15000)
    yield page


@pytest.fixture(scope="function")
def nexign_ui_mock_login(page: Page, base_url: str) -> Page:
    page.goto(base_url)
    home_page = HomePage(page)
    expect(page).to_have_title("Nexign UI", timeout=15000)
    home_page.USER_DROPDOWN_BTN.wait_to_be_visible(timeout=15000)
    yield page


@pytest.fixture(scope="function")
def create_individual_user(
    api_request_auth_context: APIRequestContext,
    individual_user_data: IndividualClient,
    request: pytest.FixtureRequest,
) -> IndividualClient:
    client_request = ClientRequests(api_request_auth_context)
    return client_request.create_individual_client(individual_user_data)


@pytest.fixture(scope="function")
def create_organization(
    api_request_auth_context: APIRequestContext,
    organization_user_data: OrganizationClient,
    request: pytest.FixtureRequest,
) -> OrganizationClient:
    client_request = ClientRequests(api_request_auth_context)
    return client_request.create_organization(organization_user_data)


@pytest.fixture(scope="function")
def create_user_with_agreement_and_account(
    create_individual_user: IndividualClient, api_request_auth_context: APIRequestContext
) -> IndividualClient:
    """Фикстура создает пользователя, создает договор и личный счёт для него"""
    personal_account_api = PersonalAccountRequests(api_request_auth_context)
    return personal_account_api.create_agreement_and_account(create_individual_user)


@pytest.fixture(scope="function")
def create_organization_with_agreement_and_account(
    create_organization: OrganizationClient, api_request_auth_context: APIRequestContext
) -> OrganizationClient:
    """Фикстура создает юридическое лицо, создает договор и личный счёт для него"""
    personal_account_api = PersonalAccountRequests(api_request_auth_context)
    return personal_account_api.create_agreement_and_account(create_organization)


@pytest.fixture(scope="function")
def create_user_with_postpaid_account(
    create_individual_user: IndividualClient, api_request_auth_context: APIRequestContext
) -> IndividualClient:
    """Фикстура создает пользователя, создает договор и личный счёт для него"""
    client_api = ClientRequests(api_request_auth_context)
    return client_api.create_individual_client_with_postpaid_account(create_individual_user)


@pytest.fixture(scope="function")
def create_user_with_agreement_and_usd_account(
    create_individual_user: IndividualClient, api_request_auth_context: APIRequestContext
) -> IndividualClient:
    """Фикстура создает пользователя, создает договор и личный счёт для него в валюте USD"""
    client_api = ClientRequests(api_request_auth_context)
    return client_api.create_individual_client_with_agreement_and_usd_account(create_individual_user)


@pytest.fixture(scope="function")
def add_new_address_to_lam(api_request_auth_context: APIRequestContext) -> dict:
    """Возвращает созданный адрес в виде словаря {'addressId': int, 'addressString': str}"""
    address_api = AddressRequests(api_request_auth_context)
    return address_api.add_new_address_to_lam()


@pytest.fixture(scope="function")
def delete_additional_attributes(api_request_auth_context: APIRequestContext, base_url_api: str) -> list:
    """Фикстура удаляет на стенде все объекты класса Attribute из списка attributes. Объекты описывают дополнительные атрибуты
    Фикстура не учитывает ответы на запросы, так как туда могут поступать уже не существующие атрибуты.
    По сути нужна для того, чтобы в действующих атрибутах не было тестовых атрибутов, которые могут помешать другим тестам
    """
    api_attribute = AttributeRequests(api_request_auth_context)
    attributes: list = []
    yield attributes
    for attribute in attributes:
        if attribute.attr_type != "template":
            payload = {"entityTypeCode": attribute.attr_type, "isDeprecated": True}
        else:
            payload = {"isDeprecated": True}
        api_attribute.attribute_update_request(api_request_auth_context, base_url_api, attribute.name, payload)


@pytest.fixture(scope="function")
def create_crab_db_connection(api_request_auth_context) -> CrabDBRequests:
    """
    Фикстура возвращает инстанс класса CrabDBRequests, а также закрывает соединение после конца работы.
    При создании фикстур для других БД руководствоваться данной и делать по аналогии.
    """
    instance = CrabDBRequests(api_request_auth_context)
    instance.connect()
    yield instance
    instance.curr_conn.close()
