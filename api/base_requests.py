from datetime import datetime
from typing import Any, Callable, List

import allure
from playwright.sync_api import APIRequestContext, APIResponse
from requests import Request

from api.exceptions import LastResponseIsMissingException
from api.jsonpath import JsonPathParser
from common.helpers.checker import assert_that, check_that, wait_that
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
    def __init__(self) -> None:
        self._last_response = None

    @property
    def api_context(self) -> APIRequestContext:
        from models.context import test_context

        return test_context.api_context

    @staticmethod
    def check_response_status(response: APIResponse, expected_status_code: int | List[int], error_message: str) -> None:
        mes = (
            f"{error_message}\nExpected status: {expected_status_code}\nActual status: {response.status}\nEndpoint: {response.url}\n"
            f"Message: {response.json().get('userMessage', response.text()) if is_json(response) else response.text()}"
        )

        if isinstance(expected_status_code, list):
            with allure.step(f"Проверка, что статус ответа входит в {expected_status_code}"):
                assert_that(lambda: response.status in expected_status_code, message=mes)
        else:
            with allure.step(f"Проверка, что статус ответа равен {expected_status_code}"):
                assert_that(lambda: response.status == expected_status_code, message=mes)

    def _request(self, method: str, url: str, **kwargs: Any) -> APIResponse:
        response = getattr(self.api_context, method)(url, **kwargs)
        self._last_response = response
        return response

    @log_request_decorator("POST")
    def post(self, url: str, **kwargs: Any) -> APIResponse:
        return self._request("post", url, **kwargs)

    @log_request_decorator("GET")
    def get(self, url: str, **kwargs: Any) -> APIResponse:
        return self._request("get", url, **kwargs)

    @log_request_decorator("PUT")
    def put(self, url: str, **kwargs: Any) -> APIResponse:
        return self._request("put", url, **kwargs)

    @log_request_decorator("DELETE")
    def delete(self, url: str, **kwargs: Any) -> APIResponse:
        return self._request("delete", url, **kwargs)

    @log_request_decorator("PATCH")
    def patch(self, url: str, **kwargs: Any) -> APIResponse:
        return self._request("patch", url, **kwargs)

    @staticmethod
    def get_last_created_item_response(response_list: list) -> dict:
        """
        Возвращает последний по дате создания item из списка response_list ответа
        :param response_list: список items из ответа
        :return: item, он же словарь(часть ответа на запрос)
        """
        date_template = "%Y-%m-%d %H:%M:%S"
        max_date = datetime.strptime("1000-01-01 10:00:00", date_template)
        last_item = dict()
        for item in response_list:
            curr = datetime.strptime(item["createDate"].replace("T", " "), date_template)
            if max_date < curr:
                max_date = curr
                last_item = item
        return last_item

    def check_response_content(
        self,
        json_path: str,
        operator: str,
        condition: str,
        response: APIResponse = None,
        request: Callable = None,
        timeout: int = 0,
    ) -> None:
        """Проверка полей ответа через jsonpath.
        https://pypi.org/project/jsonpath-ng/
        :param json_path: jsonpath выражение (путь к полю). Например: "$.user.name"
        :param operator: оператор сравнения (==, !=, >, >=, <, <=, has, in, not in, not has, equals, gt, lt)
        :param condition: условие для сравнения (строка, с которой сравниваем)
        :param response: ответ запроса. Если не указан берется последний ответ
        :param request: запрос как callable для возможности ожидания выполнения условия
        :param timeout: время ожидания выполнения условия
        """
        resp = response or self._last_response or request
        check_that(lambda: resp is not None, LastResponseIsMissingException, "Не найден последний ответ API")
        with allure.step(f"API: Проверка:\n{json_path} {operator} {condition}"):

            def request_json() -> dict:
                return request().json() if request is not None else resp.json()

            error = JsonPathParser(json_path).compare_values(operator, condition, request_json())
            if error:
                wait_that(
                    lambda: not JsonPathParser(json_path).compare_values(operator, condition, request_json()),
                    AssertionError,
                    f"Условия не выполнены для {json_path}:\n{error}",
                    timeout=timeout,
                )

    def get_response_content_by_jsonpath(self, json_path: str, response: APIResponse = None) -> Any | None:
        """Получение значения из ответа по jsonpath.
        https://pypi.org/project/jsonpath-ng/
        :param json_path: jsonpath выражение (путь к полю). Например: "$.user.name"
        :param response: ответ запроса. Если не указан берется последний ответ
        :return: значение по выражению
        """
        resp = response or self._last_response
        parsed_data = JsonPathParser(json_path).parse(resp.json())

        assert_that(lambda: parsed_data, f"Значение по выражунию '{json_path}' не найдено")
        return parsed_data
