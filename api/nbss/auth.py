import allure
from playwright.sync_api import APIRequestContext

from api.base_requests import BaseRequests
from common.helpers.env_helper import BASE_URL, BASE_URL_API, UserData


class NBSSAuthRequests(BaseRequests):
    def __init__(self, api_request_auth_context: APIRequestContext):
        super().__init__(api_request_auth_context)

    @allure.step("API: Авторизация NBSS")
    def auth(self) -> None:
        self.get(BASE_URL)
        self.post(BASE_URL_API + "/connect/login", data={"login": UserData.login, "password": UserData.password})
