from __future__ import annotations

from typing import Any
from urllib.parse import quote

import allure

from api.base_requests import BaseRequests
from common.helpers.checker import assert_that
from common.helpers.env_helper import BASE_URL_ZOOKEEPER
from models.playwright_bridge import GeneralResponse


class ZookeeperRequests(BaseRequests):
    DEFAULT_PATH_PARTS: list[str] = ["ps", "config", "apps", "common", "partyUnique"]

    def _path_parts(self, path_parts: list[str] | None) -> list[str]:
        """
        Возвращает сегменты пути к znode или значение по умолчанию.

        :param path_parts: список сегментов пути; если None — используется DEFAULT_PATH_PARTS.
        :return: список сегментов пути.
        """
        return path_parts if path_parts is not None else self.DEFAULT_PATH_PARTS

    @staticmethod
    def _znode_value_for_put(current: Any, new_value: str) -> Any:
        """
        Приводит новое значение znode к типу текущего значения из GET (int/str), чтобы PUT соответствовал контракту API.

        :param current: текущее значение znodeValue из ответа GET.
        :param new_value: новое значение в виде строки.
        :return: значение для поля znodeValue в теле PUT.
        """
        if isinstance(current, int) and new_value.isdigit():
            return int(new_value)
        return new_value

    def _zk_url(self, path_parts: list[str]) -> str:
        """
        Собирает URL запроса к API Zookeeper для указанного пути.

        :param path_parts: сегменты пути внутри префикса zk/.
        :return: полный URL для GET/PUT znode.
        """
        encoded = quote("zk/" + "/".join(path_parts), safe="")
        return f"{BASE_URL_ZOOKEEPER}/api/zk/{encoded}"

    @allure.step("API Zookeeper: GET znode")
    def get_znode(self, path_parts: list[str] | None = None) -> dict[str, Any]:
        """
        Выполняет GET znode по пути (по умолчанию partyUnique).

        :param path_parts: сегменты пути к znode; если None — путь по умолчанию.
        :return: тело ответа API в виде словаря.
        """
        parts = self._path_parts(path_parts)
        response = self.get(self._zk_url(parts))
        self.check_response_status(response, 200, "Не удалось выполнить GET Zookeeper znode")
        return response.json()

    @allure.step("API Zookeeper: PUT znode")
    def put_znode(self, payload: dict[str, Any], path_parts: list[str] | None = None) -> GeneralResponse:
        """
        Выполняет PUT znode с переданным телом.

        :param payload: тело запроса (как правило, объект из GET с обновлённым znodeValue).
        :param path_parts: сегменты пути к znode; если None — путь по умолчанию.
        :return: объект ответа API.
        """
        parts = self._path_parts(path_parts)
        response = self.put(self._zk_url(parts), json=payload)
        self.check_response_status(response, [200, 204], "Не удалось выполнить PUT Zookeeper znode")
        return response

    @allure.step("API Zookeeper: GET → PUT → GET, выставить znodeValue")
    def set_znode_value(self, new_znode_value: str, path_parts: list[str] | None = None) -> None:
        """
        Читает znode, выставляет znodeValue и проверяет, что значение применилось (GET → PUT → GET).

        :param new_znode_value: новое значение znodeValue (строка; при необходимости приводится к типу текущего значения).
        :param path_parts: сегменты пути к znode; если None — путь по умолчанию.
        :return: None.
        """
        parts = self._path_parts(path_parts)
        before = self.get_znode(parts)
        coerced = self._znode_value_for_put(before["znodeValue"], new_znode_value)
        self.put_znode({**before, "znodeValue": coerced}, parts)
        after = self.get_znode(parts)
        actual = after["znodeValue"]
        with allure.step("Проверка, что znodeValue выставлено"):
            assert_that(
                lambda: str(actual) == str(new_znode_value),
                message=f"Ожидали znodeValue={new_znode_value!r}, получили {actual!r}",
            )
