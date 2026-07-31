from datetime import datetime
from typing import Any, Callable, List

import allure
from httpx import Client, Request, TimeoutException
from playwright.sync_api import APIRequestContext
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from api.exceptions import LastResponseIsMissingException
from api.jsonpath import JsonPathParser
from common.helpers.checker import assert_that, check_that, wait_that
from common.helpers.json_utils import is_json
from common.logging import log_request, log_response
from models.playwright_bridge import GeneralResponse, PlaywrightAdapter


def log_request_decorator(method: str) -> Callable:
    def decorator(func: Callable) -> Callable:
        def wrapper(self, *args, **kwargs) -> Callable:  # type: ignore
            kwargs_copy = kwargs.copy()
            kwargs_copy.pop("auth", {})
            kwargs_copy.pop("timeout", None)
            request = Request(method, *args, headers=kwargs_copy.pop("headers", {}), **kwargs_copy)
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
    def api_context(self) -> APIRequestContext | Client:
        from models.context import test_context

        return test_context.api_context

    @staticmethod
    def check_response_status(
        response: GeneralResponse,
        expected_status_code: int | List[int] | Callable[[int], bool],
        error_message: str,
    ) -> None:
        """
        Проверяет HTTP-код ответа API: точное совпадение, вхождение в список или произвольное условие (callable).

        :param response: объект ответа API.
        :param expected_status_code: ожидаемый код (int), допустимые коды (list) или функция ``(code: int) -> bool``.
        :param error_message: текст ошибки при несовпадении с ожиданием.
        :return: None.
        """
        if callable(expected_status_code):
            expected_line = "Expected: условие на код статуса (callable)"
        else:
            expected_line = f"Expected status: {expected_status_code}"
        mes = (
            f"{error_message}\n{expected_line}\nActual status: {response.status_code}\nEndpoint: {response.url}\n"
            f"Message: {response.json().get('userMessage', response.text) if is_json(response) else response.text}"
        )
        if callable(expected_status_code):
            with allure.step("Проверка статуса ответа по условию (callable)"):
                assert_that(lambda: expected_status_code(response.status_code), message=mes)
        elif isinstance(expected_status_code, list):
            with allure.step(f"Проверка, что статус ответа входит в {expected_status_code}"):
                assert_that(lambda: response.status_code in expected_status_code, message=mes)
        else:
            with allure.step(f"Проверка, что статус ответа равен {expected_status_code}"):
                assert_that(lambda: response.status_code == expected_status_code, message=mes)

    def _request(self, method: str, url: str, **kwargs: Any) -> GeneralResponse:
        ctx = self.api_context

        if isinstance(ctx, APIRequestContext):
            if "json" in kwargs:
                kwargs["data"] = kwargs.pop("json")
            if "files" in kwargs:
                files = kwargs.pop("files")
                multipart = kwargs.pop("data", {})
                for name, (filename, fp, mime) in files.items():
                    fp.seek(0)
                    multipart[name] = {"name": filename, "mimeType": mime, "buffer": fp.read()}
                kwargs["multipart"] = multipart
            if "timeout" in kwargs:
                timeout = kwargs.pop("timeout")
                kwargs["timeout"] = timeout * 1000 if isinstance(timeout, (int, float)) else int(timeout) * 1000
            try:
                response = PlaywrightAdapter(getattr(ctx, method)(url, **kwargs))
            except PlaywrightTimeoutError as e:
                raise AssertionError(e)

        elif isinstance(ctx, Client):
            try:
                response = getattr(ctx, method)(url, **kwargs)
            except TimeoutException as e:
                raise AssertionError(e)
        else:
            raise ValueError("Передан некорректный контекст")

        self._last_response = response
        return response

    @log_request_decorator("POST")
    def post(self, url: str, **kwargs: Any) -> GeneralResponse:
        return self._request("post", url, **kwargs)

    @log_request_decorator("GET")
    def get(self, url: str, **kwargs: Any) -> GeneralResponse:
        return self._request("get", url, **kwargs)

    @log_request_decorator("PUT")
    def put(self, url: str, **kwargs: Any) -> GeneralResponse:
        return self._request("put", url, **kwargs)

    @log_request_decorator("DELETE")
    def delete(self, url: str, **kwargs: Any) -> GeneralResponse:
        return self._request("delete", url, **kwargs)

    @log_request_decorator("PATCH")
    def patch(self, url: str, **kwargs: Any) -> GeneralResponse:
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
        response: GeneralResponse = None,
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

    def get_response_content_by_jsonpath(self, json_path: str, response: GeneralResponse = None) -> str:
        """Получение значения из ответа по jsonpath.
        https://pypi.org/project/jsonpath-ng/
        :param json_path: jsonpath выражение (путь к полю). Например: "$.user.name"
        :param response: ответ запроса. Если не указан берется последний ответ
        :return: значение по выражению
        """
        resp = response or self._last_response
        parsed_data = JsonPathParser(json_path).parse(resp.json())

        assert_that(lambda: parsed_data, f"Значение по выражению '{json_path}' не найдено")
        return parsed_data  # type: ignore
