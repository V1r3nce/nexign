import allure
import pytest
from playwright.sync_api import APIRequestContext, Page, expect

from api.nbss.address_requests import AddressRequests
from api.nbss.attribute_requests import AttributeRequests
from api.nbss.auth import NBSSAuthRequests
from api.nbss.client_requests.client_requests import ClientRequests
from api.nbss.personal_account_requests import PersonalAccountRequests
from common.enums.user_roles import UserRole
from common.helpers.env_helper import get_user_by_role
from db.requests.db_requests import CrabDBRequests
from models.user import EntrepreneurClient, IndividualClient, OrganizationClient
from pages.base_page import BasePage
from pages.locators.nbss.home_page_elements import HomePage
from ssh.requests.ssh_requests import SSHNWMRequests


@pytest.fixture(scope="function")
def nexign_ui_stand_login(page: Page, api_request_context, base_url_api: str, base_url: str, role: UserRole) -> Page:
    """Фикстура для авторизации с указанной ролью. По умолчанию фикстура будет использовать роль Admin.
    Если нам нужно войти под другой ролью, нужно указать над тестом маркер нужной нам роли.

    Роли хранятся в Enum common.enums.user_roles.UserRole
    Доступные роли:
    - Admin (по умолчанию)
    - ADMIN_TEST, SELLER_JR_TEST, SELLER_TEST, SELLER_SR_TEST
    - CUSTOMER_CARE_TEST, SP_MANAGER_TEST, SECURITY_TEST, FINANCE_TEST

    Примеры (рекомендовано использовать Enum):
    @pytest.mark.role(UserRole.SECURITY_TEST)
    @pytest.mark.role(UserRole.FINANCE_TEST)
    """
    role_string = str(role)
    login, password = get_user_by_role(role_string)

    with allure.step(f"Авторизация в Nexign NBSS UI ролью {role}"):
        base_page = BasePage(page)
        home_page = HomePage(page)
        api = NBSSAuthRequests(api_request_context)

        api.auth(login=login, password=password)
        base_page.open(base_url, timeout=15000)
        base_page.expect_title("Nexign UI", timeout=15000)
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
    api_request_context: APIRequestContext,
    individual_user_data: IndividualClient,
    request: pytest.FixtureRequest,
) -> IndividualClient:
    client_request = ClientRequests(api_request_context)
    return client_request.create_individual_client(individual_user_data)


@pytest.fixture(scope="function")
def create_organization(
    api_request_context: APIRequestContext,
    organization_user_data: OrganizationClient,
    request: pytest.FixtureRequest,
) -> OrganizationClient:
    client_request = ClientRequests(api_request_context)
    return client_request.create_organization(organization_user_data)


@pytest.fixture(scope="function")
def create_user_with_agreement_and_account(
    create_individual_user: IndividualClient, api_request_context: APIRequestContext
) -> IndividualClient:
    """Фикстура создает пользователя, создает договор и личный счёт для него"""
    personal_account_api = PersonalAccountRequests(api_request_context)
    return personal_account_api.create_agreement_and_account(create_individual_user)


@pytest.fixture(scope="function")
def create_organization_with_agreement_and_account(
    create_organization: OrganizationClient, api_request_context: APIRequestContext
) -> OrganizationClient:
    """Фикстура создает юридическое лицо, создает договор и личный счёт для него"""
    personal_account_api = PersonalAccountRequests(api_request_context)
    return personal_account_api.create_agreement_and_account(create_organization)


@pytest.fixture(scope="function")
def create_entrepreneur_with_agreement_and_account(
    api_request_context: APIRequestContext,
    entrepreneur_user_data: EntrepreneurClient,
    request: pytest.FixtureRequest,
) -> EntrepreneurClient:
    """Фикстура создает индивидуального предпринимателя, создает договор и личный счёт для него"""
    client_request = ClientRequests(api_request_context)
    created_entrepreneur = client_request.create_entrepreneur_client(entrepreneur_user_data)
    personal_account_api = PersonalAccountRequests(api_request_context)
    return personal_account_api.create_agreement_and_account(created_entrepreneur)


@pytest.fixture(scope="function")
def create_user_with_postpaid_account(
    individual_user_data: IndividualClient, api_request_context: APIRequestContext
) -> IndividualClient:
    """Фикстура создает пользователя, создает договор и личный счёт для него"""
    client_api = ClientRequests(api_request_context)
    return client_api.create_individual_client_with_postpaid_account(individual_user_data)


@pytest.fixture(scope="function")
def create_user_with_agreement_and_usd_account(
    individual_user_data: IndividualClient, api_request_context: APIRequestContext
) -> IndividualClient:
    """Фикстура создает пользователя, создает договор и личный счёт для него в валюте USD"""
    client_api = ClientRequests(api_request_context)
    return client_api.create_individual_client_with_agreement_and_usd_account(individual_user_data)


@pytest.fixture(scope="function")
def add_new_address_to_lam(api_request_context: APIRequestContext) -> dict:
    """Возвращает созданный адрес в виде словаря {'addressId': int, 'addressString': str}"""
    address_api = AddressRequests(api_request_context)
    return address_api.add_new_address_to_lam()


@pytest.fixture(scope="function")
def delete_additional_attributes(api_request_context: APIRequestContext, base_url_api: str) -> list:
    """Фикстура удаляет на стенде все объекты класса Attribute из списка attributes. Объекты описывают дополнительные атрибуты
    Фикстура не учитывает ответы на запросы, так как туда могут поступать уже не существующие атрибуты.
    По сути нужна для того, чтобы в действующих атрибутах не было тестовых атрибутов, которые могут помешать другим тестам
    """
    api_attribute = AttributeRequests(api_request_context)
    attributes: list = []
    yield attributes
    for attribute in attributes:
        if attribute.attr_type != "template":
            payload = {"entityTypeCode": attribute.attr_type, "isDeprecated": True}
        else:
            payload = {"isDeprecated": True}
        api_attribute.attribute_update_request(api_request_context, base_url_api, attribute.name, payload)


@pytest.fixture(scope="function")
def create_crab_db_connection(api_request_context) -> CrabDBRequests:
    """
    Фикстура возвращает инстанс класса CrabDBRequests, а также закрывает соединение после конца работы.
    При создании фикстур для других БД руководствоваться данной и делать по аналогии.
    """
    instance = CrabDBRequests(api_request_context)
    instance.connect()
    yield instance
    instance.curr_conn.close()


@pytest.fixture(scope="function")
def create_nwm_ssh_connection(api_request_context) -> SSHNWMRequests:
    """
    Фикстура возвращает инстанс класса SSHNWMRequests, а также закрывает соединение после конца работы.
    При создании фикстур для других хостов руководствоваться данной и делать по аналогии.
    """
    instance = SSHNWMRequests(api_request_context)
    instance.connect()
    yield instance
    instance.curr_conn.close()
