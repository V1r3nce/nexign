import base64

import allure
import pytest

from api.base_requests import BaseRequests
from common.helpers.env_helper import BASE_URL_UNIBLP, UserData


class UniblpAuthRequests(BaseRequests):
    @pytest.mark.sso
    @allure.step("API: Авторизация UNIBLP с логином {login}")
    def auth(self, login: str = None, password: str = None) -> None:
        user_login = login or UserData.login
        user_password = password or UserData.password

        credentials = f"{user_login}:{user_password}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {encoded_credentials}",
        }

        params = {"grant_type": "password", "username": user_login, "password": user_password}

        response = self.post(BASE_URL_UNIBLP + "/OAPI_LOGIN_SSO/ps/auth/api/token", params=params, headers=headers)
        self.check_response_status(response, 200, "API: Не удалось авторизоваться")
        return response.json().get("access_token", None)
