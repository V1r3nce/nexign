"""Запись сетевых вызовов интерфейса по шагам теста.

Модуль отвечает на вопрос «какие запросы к бэкенду делает UI на каждом шаге кейса»: по нему
пишутся бэкенд-тесты, повторяющие тот же сценарий без браузера. Подписка идёт на события
страницы playwright, а привязка к шагам — на официальные хуки allure (см. :class:`StepTracker`).

В дамп попадают только вызовы проектного API: статика, метрика и прочий шум отсеиваются теми же
правилами, что и при разборе выгрузки из devtools (:mod:`scripts.dom_inspector.api_parser`).

Формат файла::

    allure.id 902222
    шаг 2 · Нажать кнопку "Добавить" на вкладке "Договоры"
    POST 201 /openapi/v1/customerManagement/agreements
        запрос: {"agreementNumber": "27801/2026/001681", ...}
        ответ: {"agreementId": 28051}
    GET 200 /openapi/v1/customerManagement/customers/28051 ×3

Тело ответа снимается не у всех: за ним нужен отдельный поход в браузер, поэтому берётся оно
только там, где несёт смысл для теста, — у изменяющих запросов и у любых ошибок.

Включается ключом ``--dump-api`` при запуске pytest, файл кладётся рядом с дампом DOM
в ``scripts/dom_inspector/dumps/<имя теста>.api.txt``.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from allure_commons import plugin_manager

from scripts.dom_inspector.api_parser import is_interesting_path, is_noise, split_url
from scripts.dom_inspector.step_tracker import StepTracker

#: Методы, меняющие состояние: у них тело ответа нужно всегда — там идентификаторы и коды ошибок.
MUTATING_METHODS: frozenset[str] = frozenset({"POST", "PUT", "PATCH", "DELETE"})

#: С какого кода ответ считается ошибочным и его тело тоже нужно.
ERROR_STATUS: int = 400

#: Сколько символов тела писать в дамп: запросы бывают на десятки килобайт, а тесту нужен
#: состав полей, а не каждый элемент справочника.
MAX_BODY_LENGTH: int = 2000


@dataclass(slots=True)
class ApiCall:
    """Один вызов бэкенда, снятый со страницы.

    :param method: HTTP-метод.
    :param path: Путь с query-строкой, без схемы и хоста.
    :param status: Код ответа.
    :param request_body: Тело запроса; пустая строка — тела не было.
    :param response_body: Тело ответа; пустая строка — не снималось или недоступно.
    :param count: Сколько раз подряд повторился такой же вызов.
    """

    method: str
    path: str
    status: int
    request_body: str = ""
    response_body: str = ""
    count: int = 1

    @property
    def key(self) -> tuple[str, str, int, str]:
        """Признак одинаковости вызовов для схлопывания повторов.

        :return: Метод, путь, код ответа и тело запроса.
        """
        return self.method, self.path, self.status, self.request_body

    def as_lines(self) -> list[str]:
        """Раскладывает вызов в строки дампа.

        :return: Строка вызова и, если есть, строки тел.
        """
        repeat = f" ×{self.count}" if self.count > 1 else ""
        lines = [f"{self.method} {self.status} {self.path}{repeat}"]
        if self.request_body:
            lines.append(f"    запрос: {self.request_body}")
        if self.response_body:
            lines.append(f"    ответ: {self.response_body}")
        return lines


class ApiRecorder(StepTracker):
    """Плагин allure: пишет вызовы бэкенда, сделанные интерфейсом на каждом шаге теста.

    :param dump_path: файл, в который дописываются вызовы
    :param case_no: идентификатор теста из allure.id
    :param test_name: имя тестового метода, попадает в шапку файла
    """

    def __init__(self, dump_path: Path, case_no: int | None, test_name: str) -> None:
        super().__init__()
        self.dump_path = dump_path
        self.case_no = case_no
        self.test_name = test_name
        self.written = 0
        self.skipped: list[str] = []
        self._pending: list[tuple[ApiCall, Any]] = []
        self._step_title = ""
        self._page: Any = None

    def attach(self, page: Any) -> None:
        """Подписывается на ответы страницы.

        :param page: Страница playwright.
        """
        self._page = page
        page.on("response", self._on_response)

    def detach(self) -> None:
        """Снимает подписку со страницы."""
        if self._page is None:
            return
        try:
            self._page.remove_listener("response", self._on_response)
        except Exception as error:  # страница могла закрыться раньше теста
            self.skipped.append(f"отписаться от событий не удалось ({type(error).__name__}: {error})")
        self._page = None

    def write_header(self) -> None:
        """Пишет шапку дампа, чтобы файл был опознан даже без единого вызова."""
        self.dump_path.parent.mkdir(parents=True, exist_ok=True)
        header = f"allure.id {self.case_no}" if self.case_no is not None else f"# {self.test_name}"
        with self.dump_path.open("a", encoding="utf-8") as dump:
            dump.write(header + "\n")

    def on_boundary(self, depth: int, title: str, exiting: bool) -> None:
        """Запоминает заголовок шага теста — под ним пишутся вызовы шага.

        :param depth: Глубина шага.
        :param title: Заголовок шага.
        :param exiting: True для выхода из шага.
        """
        if depth == 1 and not exiting:
            self._step_title = title

    def on_test_step_end(self, exc_type: Any, exc_val: Any) -> None:
        """Дописывает вызовы завершившегося шага теста.

        :param exc_type: Класс исключения, не используется.
        :param exc_val: Исключение, не используется.
        """
        self.flush()

    def flush(self) -> None:
        """Дописывает накопленные вызовы шага в файл, схлопывая подряд идущие повторы."""
        pending, self._pending = self._pending, []
        if not pending:
            return
        calls: list[ApiCall] = []
        for call, response in pending:
            _fill_response_body(call, response)
            if calls and calls[-1].key == call.key:
                calls[-1].count += 1
                continue
            calls.append(call)
        marker = f"шаг {self.step_no} · {self._step_title}" if self._step_title else f"шаг {self.step_no}"
        with self.dump_path.open("a", encoding="utf-8") as dump:
            dump.write(marker + "\n")
            for call in calls:
                dump.write("\n".join(call.as_lines()) + "\n")
        self.written += len(calls)

    def _on_response(self, response: Any) -> None:
        """Обработчик события страницы: берёт только дешёвые данные, тело ответа — потом.

        :param response: Ответ playwright.
        """
        try:
            request = response.request
            url = response.url
            if is_noise(url)[0]:
                return
            if not is_interesting_path(split_url(url).path):
                return
            call = ApiCall(
                method=request.method,
                path=_with_query(url),
                status=response.status,
                request_body=_cut(request.post_data or ""),
            )
        except Exception as error:  # событие не должно ронять тест
            self.skipped.append(f"вызов не записан ({type(error).__name__}: {error})")
            return
        self._pending.append((call, response))


def _fill_response_body(call: ApiCall, response: Any) -> None:
    """Забирает тело ответа там, где оно нужно тесту.

    За телом нужен отдельный поход в браузер, поэтому берём его только у изменяющих запросов
    и у ошибок: у остальных в дампе достаточно метода, пути и кода.

    :param call: Вызов, в который кладётся тело.
    :param response: Ответ playwright.
    """
    if call.method not in MUTATING_METHODS and call.status < ERROR_STATUS:
        return
    try:
        call.response_body = _cut(response.text())
    except Exception:  # тело могло не сохраниться после навигации — это не повод падать
        call.response_body = ""


def _with_query(url: str) -> str:
    """Возвращает путь запроса вместе с query-строкой.

    :param url: Полный URL.
    :return: Строка вида ``/openapi/v1/customers?limit=50``.
    """
    parts = split_url(url)
    return f"{parts.path}?{parts.query}" if parts.query else parts.path


def _cut(text: str) -> str:
    """Схлопывает тело в одну строку и обрезает до разумной длины.

    :param text: Тело запроса или ответа.
    :return: Однострочное тело не длиннее :data:`MAX_BODY_LENGTH`.
    """
    single_line = " ".join(text.split())
    if len(single_line) <= MAX_BODY_LENGTH:
        return single_line
    return single_line[:MAX_BODY_LENGTH] + f"… (обрезано, всего {len(single_line)})"


def start_recording(dump_path: Path, case_no: int | None, test_name: str, page: Any) -> ApiRecorder:
    """Начинает запись вызовов: чистит файл, пишет шапку и подписывается на события.

    :param dump_path: Файл дампа.
    :param case_no: Идентификатор теста из allure.id.
    :param test_name: Имя тестового метода.
    :param page: Страница playwright; None — подписываться не на что.
    :return: Объект записи.
    """
    if dump_path.exists():
        dump_path.unlink()
    recorder = ApiRecorder(dump_path, case_no, test_name)
    recorder.write_header()
    if page is not None:
        recorder.attach(page)
    plugin_manager.register(recorder)
    return recorder


def stop_recording(recorder: ApiRecorder) -> None:
    """Дописывает остаток, отписывается от событий и снимает плагин.

    :param recorder: Объект записи.
    """
    recorder.flush()
    recorder.detach()
    try:
        plugin_manager.unregister(recorder)
    except Exception:
        pass
