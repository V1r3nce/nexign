from typing import Any, Dict, Protocol

from playwright.sync_api import APIResponse


class GeneralResponse(Protocol):
    @property
    def status_code(self) -> int: ...

    def json(self) -> Dict[str, Any]: ...

    @property
    def text(self) -> str: ...

    @property
    def url(self) -> str: ...

    @property
    def headers(self) -> Dict[str, str]: ...


class PlaywrightAdapter:
    def __init__(self, response: APIResponse):
        self._resp = response

    @property
    def status_code(self) -> int:
        return self._resp.status

    def json(self) -> Dict[str, Any]:
        return self._resp.json()

    @property
    def text(self) -> str:
        return self._resp.text()

    @property
    def url(self) -> str:
        return self._resp.url

    @property
    def headers(self) -> Dict[str, str]:
        return self._resp.headers
