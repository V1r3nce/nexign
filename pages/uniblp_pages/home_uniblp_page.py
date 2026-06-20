from httpx import Client

from api.uniblp_requests.auth import UniblpAuthRequests
from common.enums.user import User
from common.helpers.checker import assert_that
from common.helpers.env_helper import BASE_URL_UNIBLP, UserData, get_user
from models.context import test_context
from pages.base_page import BasePage
from pages.locators.uniblp_locators.home_elements_uniblp import HomeUniblpElements
from pages.locators.uniblp_locators.login_elements_uniblp import LoginFormUniblpElements


class HomeUniblpPage(BasePage):
    def __init__(self) -> None:
        super().__init__()

        self.locators = HomeUniblpElements()

    def open_and_login_uniblp(self) -> None:
        base_page = BasePage()
        api = UniblpAuthRequests()

        token = api.auth(*get_user(User.ADMIN))
        assert_that(lambda: token is not None, f"Не удалось получить токен для пользователя {get_user(User.ADMIN)[0]}")

        test_context.api_context = Client(headers={"Accept": "application/json", "Charset": "UTF-8", "authToken": token})

        base_page.open(f"{BASE_URL_UNIBLP}/ps/uniblp/index.html", timeout=50000)
        login_page_uniblp = LoginFormUniblpElements()
        login_page_uniblp.LOGIN.wait_to_be_visible()
        login_page_uniblp.LOGIN.fill(UserData.login)
        login_page_uniblp.PASSWORD.fill(UserData.password)
        login_page_uniblp.SUBMIT.click()
