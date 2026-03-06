import allure
import pytest

from api.base_requests import BaseRequests
from common.helpers.env_helper import BASE_URL, BASE_URL_API, UserData


class NBSSAuthRequests(BaseRequests):
    @pytest.mark.sso
    @allure.step("API: Авторизация NBSS с логином {login}")
    def auth(self, login: str = None, password: str = None) -> None:
        user_login = login or UserData.login
        user_password = password or UserData.password
        self.get(BASE_URL)
        self.post(BASE_URL_API + "/connect/login", data={"login": user_login, "password": user_password})
        response = self.get(BASE_URL)
        self.check_response_status(response, 200, "API: Не удалось авторизоваться")
