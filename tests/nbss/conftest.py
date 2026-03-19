import os

import allure
import pytest

from api.nbss.address_requests import AddressRequests
from api.nbss.attribute_requests import AttributeRequests
from api.nbss.auth import NBSSAuthRequests
from api.nbss.client_requests.client_requests import ClientRequests
from api.nbss.personal_account_requests import PersonalAccountRequests
from api.nbss.points_of_sale_requests import PointsOfSaleRequests
from api.psc_requests.projects_requests import ProjectRequests
from common.enums.user import User
from common.helpers.env_helper import get_user
from db.requests.db_requests import OMSDBRequests
from models.client import EntrepreneurClient, IndividualClient, OrganizationClient
from models.context import test_context
from pages.base_page import BasePage
from pages.locators.nbss.home_page_elements import HomePageElements
from pages.nbss.login_page import LoginPage
from ssh.requests.ssh_requests import SSHNWMRequests


@pytest.fixture()
def nexign_stand_login(api_request_context, base_url_api: str, base_url: str, user: User) -> None:
    """Фикстура для авторизации с указанным пользователем. По умолчанию фикстура будет использовать пользователя Admin.
    Если нам нужно войти под другим пользователем, нужно указать над тестом маркер нужного пользователя.
    Если указан пользователь отличный от Admin, то создастся отдельный контекст для админа (это требуется для выполнения продажи, создания пользователей и т.д.)

    Роли хранятся в Enum common.enums.user.User
    Доступные роли:
    - Admin (по умолчанию)
    - ADMIN_TEST, SELLER_JR_TEST, SELLER_TEST, SELLER_SR_TEST
    - CUSTOMER_CARE_TEST, SP_MANAGER_TEST, SECURITY_TEST, FINANCE_TEST

    Пример (рекомендовано использовать Enum. Поддерживается передача одного пользователя.):
        @pytest.mark.user(User.SECURITY_TEST)
        @pytest.mark.user(User.FINANCE_TEST)

    Для переключения API контекста необходимо использовать метод switch_api_context_to_user
    Пример:
        test_context.switch_api_context_to_user(User.ADMIN)
    """
    with allure.step("Авторизация в Nexign NBSS UI"):
        base_page = BasePage()
        home_page = HomePageElements()
        api = NBSSAuthRequests()

        if user != User.ADMIN:
            ui = LoginPage()
            ui.login(*get_user(user))

            test_context.switch_api_context_to_user(User.ADMIN)
            api.auth(*get_user(User.ADMIN))
            test_context.switch_api_context_to_user(user)
        else:
            api.auth(*get_user(user))

        base_page.open(base_url, timeout=15000)
        base_page.expect_title("Nexign UI", timeout=5000)
        home_page.USER_DROPDOWN_BTN.wait_to_be_visible(timeout=15000)


@pytest.fixture(scope="function")
def nexign_ui_mock_login(base_url: str) -> None:
    base_page = BasePage()
    base_page.open(base_url)
    home_page = HomePageElements()
    base_page.expect_title("Nexign UI", timeout=15000)
    home_page.USER_DROPDOWN_BTN.wait_to_be_visible(timeout=15000)


@pytest.fixture(scope="function")
def create_individual_user(individual_user_data: IndividualClient, request: pytest.FixtureRequest) -> IndividualClient:
    client_request = ClientRequests()
    return client_request.create_individual_client(individual_user_data)


@pytest.fixture(scope="function")
def create_organization(
    organization_user_data: OrganizationClient, request: pytest.FixtureRequest
) -> OrganizationClient:
    client_request = ClientRequests()
    return client_request.create_organization(organization_user_data)


@pytest.fixture(scope="function")
def create_individual_user_with_agreement(
    individual_user_data: IndividualClient, request: pytest.FixtureRequest
) -> IndividualClient:
    client_request = ClientRequests()
    return client_request.create_individual_client_with_agreement(individual_user_data)


@pytest.fixture(scope="function")
def create_user_with_agreement_and_account(create_individual_user: IndividualClient) -> IndividualClient:
    """Фикстура создает пользователя, создает договор и личный счёт для него"""
    personal_account_api = PersonalAccountRequests()
    return personal_account_api.create_agreement_and_account(create_individual_user)


@pytest.fixture(scope="function")
def create_organization_with_agreement_and_account(create_organization: OrganizationClient) -> OrganizationClient:
    """Фикстура создает юридическое лицо, создает договор и личный счёт для него"""
    personal_account_api = PersonalAccountRequests()
    return personal_account_api.create_agreement_and_account(create_organization)


@pytest.fixture(scope="function")
def create_organization_with_agreement_guarantee_and_account(
    create_organization: OrganizationClient,
) -> OrganizationClient:
    """Фикстура создает юридическое лицо, создаёт договор со статусом по гарантии и личный счёт для него"""
    client_requests = ClientRequests()
    return client_requests.personal_account_api.create_agreement_and_account(create_organization, status_id=3)


@pytest.fixture(scope="function")
def create_entrepreneur(
    entrepreneur_user_data: EntrepreneurClient, request: pytest.FixtureRequest
) -> EntrepreneurClient:
    """Фикстура создает индивидуального предпринимателя"""
    client_request = ClientRequests()
    return client_request.create_entrepreneur_client(entrepreneur_user_data)


@pytest.fixture(scope="function")
def create_entrepreneur_with_agreement_and_account(create_entrepreneur: EntrepreneurClient) -> EntrepreneurClient:
    """Фикстура создает индивидуального предпринимателя, создает договор и личный счёт для него"""
    personal_account_api = PersonalAccountRequests()
    return personal_account_api.create_agreement_and_account(create_entrepreneur)


@pytest.fixture(scope="function")
def create_user_with_postpaid_account(individual_user_data: IndividualClient) -> IndividualClient:
    """Фикстура создает пользователя, создает договор и личный счёт для него"""
    client_api = ClientRequests()
    return client_api.create_individual_client_with_postpaid_account(individual_user_data)


@pytest.fixture(scope="function")
def create_organization_with_postpaid_account(organization_user_data: OrganizationClient) -> OrganizationClient:
    """Фикстура создает ЮЛ, создает договор и постоплатный ЛС для него"""
    client_api = ClientRequests()
    return client_api.create_organization_client_with_postpaid_account(organization_user_data)


@pytest.fixture(scope="function")
def create_user_with_agreement_and_usd_account(individual_user_data: IndividualClient) -> IndividualClient:
    """Фикстура создает пользователя, создает договор и личный счёт для него в валюте USD"""
    client_api = ClientRequests()
    return client_api.create_individual_client_with_agreement_and_usd_account(individual_user_data)


@pytest.fixture(scope="function")
def add_new_address_to_lam() -> dict:
    """Возвращает созданный адрес в виде словаря {'addressId': int, 'addressString': str}"""
    address_api = AddressRequests()
    return address_api.add_new_address_to_lam()


@pytest.fixture(scope="function")
def delete_additional_attributes(base_url_api: str) -> list:
    """Фикстура удаляет на стенде все объекты класса Attribute из списка attributes. Объекты описывают дополнительные атрибуты
    Фикстура не учитывает ответы на запросы, так как туда могут поступать уже не существующие атрибуты.
    По сути нужна для того, чтобы в действующих атрибутах не было тестовых атрибутов, которые могут помешать другим тестам
    """
    api_attribute = AttributeRequests()
    attributes: list = []
    yield attributes
    for attribute in attributes:
        if attribute.attr_type != "template":
            payload = {"entityTypeCode": attribute.attr_type, "isDeprecated": True}
        else:
            payload = {"isDeprecated": True}
        api_attribute.attribute_update_request(base_url_api, attribute.name, payload)


@pytest.fixture(scope="function")
def cleanup_download_files() -> list[str]:
    files: list[str] = []
    yield files

    for path in files:
        if not path:
            continue

        try:
            if os.path.exists(path):
                os.remove(path)

        except FileNotFoundError:
            pass

        except PermissionError as exc:
            allure.attach(
                body=str(exc),
                name="Ошибка прав доступа при удалении файла",
                attachment_type=allure.attachment_type.TEXT,
            )

        except OSError as exc:
            allure.attach(
                body=str(exc),
                name="Системная ошибка при удалении файла",
                attachment_type=allure.attachment_type.TEXT,
            )


@pytest.fixture(scope="function")
def create_oms_db_connection() -> OMSDBRequests:
    """
    Фикстура возвращает инстанс класса CrabDBRequests, а также закрывает соединение после конца работы.
    При создании фикстур для других БД руководствоваться данной и делать по аналогии.
    """
    instance = OMSDBRequests()
    instance.connect()
    yield instance
    instance.curr_conn.close()


@pytest.fixture(scope="function")
def create_nwm_ssh_connection() -> SSHNWMRequests:
    """
    Фикстура возвращает инстанс класса SSHNWMRequests, а также закрывает соединение после конца работы.
    При создании фикстур для других хостов руководствоваться данной и делать по аналогии.
    """
    instance = SSHNWMRequests()
    instance.connect()
    yield instance
    instance.curr_conn.close()


@pytest.fixture(scope="function")
def clean_project_product_offerings() -> list:
    """
    Фикстура посылает запрос по проекту для того, чтобы он не отображался на витрине. Конкретно выставляется дата до которой действительно
    продуктовое предложение - сейчас плюс 3 минуты.
    """
    project_api = ProjectRequests()
    projects: list = []
    yield projects
    for project in projects:
        project_api.change_date_and_send_to_apc(project)


@pytest.fixture(scope="function")
def cleanup_user_points_of_sale() -> list[int]:
    """
    Фикстура отвязывает новые точки продажи от пользователя после выполнения теста.
    Работает с пользователем, получает его userId.
    Собирает список точек продажи до начала теста и после теста, удаляет только те, которые появились новые.
    Фикстура не учитывает ответы на запросы, так как точки продажи могут быть уже отвязаны.
    """
    points_of_sale_api = PointsOfSaleRequests()

    user_id = points_of_sale_api.get_user_id_by_login()

    initial_partner_point_ids = points_of_sale_api.get_user_points_of_sale(user_id)

    yield initial_partner_point_ids

    try:
        final_partner_point_ids = points_of_sale_api.get_user_points_of_sale(user_id)

        new_partner_point_ids = [
            point_id for point_id in final_partner_point_ids if point_id not in initial_partner_point_ids
        ]

        for partner_point_id in new_partner_point_ids:
            try:
                points_of_sale_api.unbind_point_of_sale_from_user(user_id, partner_point_id)
            except Exception as exc:
                allure.attach(
                    body=str(exc),
                    name=f"Ошибка при отвязывании точки продажи {partner_point_id}",
                    attachment_type=allure.attachment_type.TEXT,
                )
    except Exception as exc:
        allure.attach(
            body=str(exc),
            name="Ошибка при получении списка точек продажи для очистки",
            attachment_type=allure.attachment_type.TEXT,
        )
