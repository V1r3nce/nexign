"""Настройки логгера и методы работы с ним"""

import json
import os
import sys
from json import JSONDecodeError
from typing import AnyStr
from urllib.parse import parse_qs

import allure
from _pytest.fixtures import SubRequest
from loguru import logger
from playwright.sync_api import APIResponse
from requests import PreparedRequest

from common.exceptions import InvalidLogLevel
from common.helpers.env_helper import LOGS_FOLDER
from common.helpers.json_utils import pretty_json


def create_logger(
    log_level: str,
    log_into_console: bool = False,
    log_file_name: str | None = None,
) -> None:
    """Создать логгер и установить уровень логирования

    Args:
        log_level: уровень логирования
        log_into_console: выводить логи только в консоль?
        log_file_name: файл для логов
    """
    log_level = log_level.upper()
    try:
        logger.remove()
        if not log_into_console:
            logger.add(
                sink=os.path.join(LOGS_FOLDER, log_file_name),
                format="\n{time:HH:mm:ss.SSS} | {level} | {name}:{function}:{line} | {message}",
                level=log_level,
                colorize=True,
            )
        else:
            logger.add(
                sink=sys.stdout,
                format=(
                    "\n<fg #ff7e00>{time:HH:mm:ss.SSS}</fg #ff7e00> | "
                    "<level>{level}</level> | "
                    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                    "<level>{message}</level>"
                ),
                level=log_level,
                colorize=True,
            )

    except ValueError:
        logger.error(f"Ошибка при установке уровня логгирования {log_level=}")
        raise InvalidLogLevel(
            f"Недопустимый уровень логирования '{log_level}'.\n"
            f"Уровень логирования должен быть одним из: ERROR, WARNING, INFO, DEBUG"
        )


def attach_body(body: AnyStr) -> None:
    """Прикрепить в allure тело запроса

    Args:
        body: Тело запроса
    """
    try:
        body_decoded = body if isinstance(body, str) else body.decode()
        allure.attach(
            body=json.dumps(obj=json.loads(body_decoded), indent=2, ensure_ascii=False),
            name="BODY",
            attachment_type=allure.attachment_type.JSON,
        )

    except JSONDecodeError:
        allure.attach(
            body=json.dumps(parse_qs(body if isinstance(body, str) else str(body)), indent=2, ensure_ascii=False),
            name="BODY",
            attachment_type=allure.attachment_type.JSON,
        )


def log_request(request: PreparedRequest, needs_allure: bool = True) -> None:
    """Залогировать запрос

    Args:
        request: запрос
        needs_allure:       Флаг логгирования в allure
            - True ->       Логгирует в allure
            - False ->      НЕ логгирует в allure
    """
    color = "blue"
    msg = (
        f"HTTP-Method: <{color}><n>{request.method}</n></{color}>\n"
        f"\t URL:     <{color}><n>{request.url}</n></{color}>\n"
        f"\t Headers: <{color}><n>{request.headers}</n></{color}>\n"
    )

    try:
        logger.opt(colors=True).debug(msg)

    except ValueError:
        logger.debug("Ошибка при логгировании последнего запроса:\n")
        logger.opt(colors=False).debug(msg.replace("<{color}><n>", "").replace("</n></{color}>", ""))

    if needs_allure:
        with allure.step(f"Запрос: [{request.method}] {request.url}"):
            allure.attach(
                body=json.dumps(dict(request.headers), indent=2),
                name="HEADERS",
                attachment_type=allure.attachment_type.JSON,
            )

            if request.body:
                attach_body(body=request.body)


def log_response(response: APIResponse, needs_allure: bool = True) -> None:
    """Залоггировать ответ

    Args:
        response: ответ
        needs_allure: Флаг логгирования в allure
    """
    color = {1: "light-blue", 2: "green", 3: "yellow", 4: "red", 5: "red"}.get(response.status // 100, "y")

    response_body = pretty_json(response.text())

    try:
        logger.opt(colors=True).debug(
            f"Code: <{color}><n>{response.status}</n></{color}>\n"
            f"\t Headers: <{color}><n>{response.headers}</n></{color}>\n"
            f"\t Body:    <{color}><n>{response_body}</n></{color}>"
        )

    except ValueError:
        logger.opt(colors=True).debug(
            f"Code: <{color}><n>{response.status}</n></{color}>\n"
            f"\t Headers: <{color}><n>{response.headers}</n></{color}>\n"
        )
        logger.debug(f"Body: {response_body}")

    if needs_allure:
        with allure.step(f"Ответ: [{response.status}] {response.url}"):
            allure.attach(
                body=json.dumps(dict(response.headers), indent=2, ensure_ascii=False),
                name="HEADERS",
                attachment_type=allure.attachment_type.JSON,
            )
            attach_body(body=response.body())


def log_fixture(request: SubRequest) -> None:
    """Вывести техническую информацию о фикстуре в дебаг

    Args:
        request: Объект класса SubRequest со служебной информацией о запуске
    """
    logger.debug(
        f"[{request.scope}] Фикстура: {request.fixturename}\n"
        f"\tПуть:      {request.path if hasattr(request, 'path') else 'None'}\n"
        f"\tКласс:     {request.cls if hasattr(request, 'cls') else 'None'}\n"
        f"\tТест:      {request.node.nodeid}\n"
        f"\tПараметры: {request.param if hasattr(request, 'param') else 'None'}\n"
    )
