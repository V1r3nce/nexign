from typing import Any, Callable, List

import allure
from playwright.sync_api import APIRequestContext, APIResponse
from requests import Request

from common.helpers.checker import assert_that
from common.helpers.json_utils import is_json, pretty_json
from common.logging import log_request, log_response


def log_request_decorator(method: str) -> Callable:
    def decorator(func: Callable) -> Callable:
        def wrapper(self, *args, **kwargs) -> Callable:  # type: ignore
            kwargs_copy = kwargs.copy()
            copy_data = pretty_json(kwargs_copy.pop("data", kwargs_copy.pop("json", {})))
            if "multipart" in kwargs:
                request = Request(method, *args, data=pretty_json(kwargs_copy.pop("multipart")), **kwargs_copy).prepare()
            else:
                request = Request(
                    method, *args, headers=kwargs_copy.pop("headers", {}), data=copy_data, **kwargs_copy
                ).prepare()
            log_request(request)
            response = func(self, *args, **kwargs)
            log_response(response)
            return response

        return wrapper

    return decorator


class BaseRequests:
    def __init__(self, api_request_auth_context: APIRequestContext):
        self.api_request_auth_context = api_request_auth_context

    @staticmethod
    def check_response_status(response: APIResponse, expected_status_code: int | List[int], error_message: str) -> None:
        mes = (
            f"{error_message}\nExpected status: {expected_status_code}\nActual status: {response.status}\n"
            f"Message: {response.json().get('userMessage', response.text()) if is_json(response) else response.text()}"
        )

        if isinstance(expected_status_code, list):
            with allure.step(f"Проверка, что статус ответа входит в {expected_status_code}"):
                assert_that(lambda: response.status in expected_status_code, message=mes)
        else:
            with allure.step(f"Проверка, что статус ответа равен {expected_status_code}"):
                assert_that(lambda: response.status == expected_status_code, message=mes)

    @log_request_decorator("POST")
    def post(self, url: str, **kwargs: Any) -> APIResponse:
        return self.api_request_auth_context.post(url, **kwargs)

    @log_request_decorator("GET")
    def get(self, url: str, **kwargs: Any) -> APIResponse:
        return self.api_request_auth_context.get(url, **kwargs)

    @log_request_decorator("PUT")
    def put(self, url: str, **kwargs: Any) -> APIResponse:
        return self.api_request_auth_context.put(url, **kwargs)

    @log_request_decorator("DELETE")
    def delete(self, url: str, **kwargs: Any) -> APIResponse:
        return self.api_request_auth_context.delete(url, **kwargs)

    @log_request_decorator("PATCH")
    def patch(self, url: str, **kwargs: Any) -> APIResponse:
        return self.api_request_auth_context.patch(url, **kwargs)
