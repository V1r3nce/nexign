import pytest
from httpx import Client

from api.uniblp_requests.auth import UniblpAuthRequests
from common.enums.user import User
from common.helpers.checker import assert_that
from common.helpers.env_helper import BASE_URL_UNIBLP, UserData, get_user, get_var_from_env
from db.requests.db_requests import UniblpDBRequests
from models.context import test_context
from pages.base_page import BasePage
from pages.locators.uniblp_locators.login_elements_uniblp import LoginFormUniblpElements


@pytest.fixture()
def stand_login_uniblp(api_request_context) -> None:
    base_page = BasePage()
    api = UniblpAuthRequests()

    token = api.auth(*get_user(User.ADMIN))
    assert_that(lambda: token is not None, f"Не удалось получить токен для пользователя {get_user(User.ADMIN)[0]}")

    test_context.api_context_dict[User.ADMIN] = Client(
        headers={"Accept": "application/json", "Charset": "UTF-8", "authToken": token}
    )

    base_page.open(f"{BASE_URL_UNIBLP}/ps/uniblp/index.html", timeout=50000)
    login_page_uniblp = LoginFormUniblpElements()
    login_page_uniblp.LOGIN.wait_to_be_visible()
    login_page_uniblp.LOGIN.fill(UserData.login)
    login_page_uniblp.PASSWORD.fill(UserData.password)
    login_page_uniblp.SUBMIT.click()


@pytest.fixture(scope="function")
def create_admin_uniblp_db_connection() -> UniblpDBRequests:
    """
    Фикстура возвращает инстанс класса UniblpDBRequests,
    а также закрывает соединение после конца работы теста.
    """
    instance = UniblpDBRequests()
    admin_creds = (get_var_from_env("SSH_LOGIN"), get_var_from_env("SSH_PASSWORD"))
    instance.connect(credentials=admin_creds)
    yield instance
    instance.curr_conn.close()


@pytest.fixture(scope="function")
def app_parameter_post_pays(create_admin_uniblp_db_connection: UniblpDBRequests) -> None:
    """
    Фикстура для тестирования параметра BLP_TARGET_POST_PAYS_ENABLE.
    Устанавливает тестовое значение ДО и сбрасывает ПОСЛЕ теста.
    """
    uniblp_db = create_admin_uniblp_db_connection
    app_parameter = "BLP_TARGET_POST_PAYS_ENABLE"

    uniblp_db.change_app_parameters(param_name=app_parameter, param_value_number=1, param_value_string="999")

    yield

    uniblp_db.change_app_parameters(param_name=app_parameter, param_value_number=0, param_value_string="NULL")
