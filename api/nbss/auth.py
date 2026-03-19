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


class SSOAuthRequests(BaseRequests):
    @pytest.mark.sso
    @allure.step("API: Авторизация SSO с логином {login}")
    def auth(self, login: str = None, password: str = None) -> str | None:
        user_login = login or UserData.login
        user_password = password or UserData.password
        headers = {"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"}
        payload = f"grant_type=password&username={user_login}&password={user_password}"
        response = self.post(
            BASE_URL_API + "/ps/auth/api/token", auth=(user_login, user_password), headers=headers, data=payload
        )
        self.check_response_status(response, 200, "API: Не удалось авторизоваться")
        return response.json().get("access_token", None)
