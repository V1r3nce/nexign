"""Автоматическая запись DOM по шагам теста во время прогона.

Подписывается на официальные хуки allure (``allure_commons.plugin_manager``) и после выхода
из каждого шага верхнего уровня — то есть из ``with allure.step(...)``, написанного прямо
в тесте, — сохраняет текущий DOM страницы в файл-дамп.

Шаги внутри пейдж-объектов (декораторы ``@allure.step`` на методах) вложены в шаг теста
и своих снимков не дают.

На шаг пишутся два снимка — на входе и на выходе, оба под одним номером шага. Одного мало:
локаторы шага работают внутри него, и к концу шага страница уже другая — кнопка «Далее»
сменилась на «Создать», форма редактирования закрылась после сохранения. Второй снимок
не пишется, если он не отличается от первого.

Формат файла::

    allure.id 902222
    шаг 1
    <html ...>...</html>
    шаг 1
    <html ...>...</html>
    шаг 2
    <html ...>...</html>

Включается ключом ``--dump-dom`` при запуске pytest, файлы кладутся в
``scripts/dom_inspector/dumps/<имя теста>.txt``. Запись живёт только на фазу вызова теста,
поэтому шаги setup-фикстур (авторизация, создание клиента по API) в дамп не попадают.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from allure_commons import hookimpl, plugin_manager

BLANK_URL_PREFIXES = ("about:", "chrome-error:")


class DomRecorder:
    """Плагин allure: пишет DOM страницы на входе и выходе каждого шага теста.

    :param dump_path: файл, в который дописываются снимки
    :param case_no: идентификатор теста из allure.id
    :param test_name: имя тестового метода, попадает в шапку файла
    """

    def __init__(self, dump_path: Path, case_no: int | None, test_name: str) -> None:
        self.dump_path = dump_path
        self.case_no = case_no
        self.test_name = test_name
        self.depth = 0
        self.step_no = 0
        self.written = 0
        self.skipped: list[str] = []
        self.skipped_same = 0
        self._last_digest: str | None = None
        self._step_has_snapshot = False
        self._header_written = False

    @hookimpl
    def start_step(self, uuid: str, title: str, params: dict[str, Any]) -> None:
        """Хук allure: вход в шаг. Снимаем DOM на входе в шаг теста — до его действий.

        Снимка только на выходе не хватает: локаторы шага работают внутри него, а к концу
        шага страница уже другая. Кнопка «Далее» сменилась на «Создать», форма редактирования
        закрылась после сохранения — и целый локатор выглядит сломанным.
        """
        self.depth += 1
        if self.depth == 1:
            self.step_no += 1
            self._step_has_snapshot = False
            self._capture()

    @hookimpl
    def stop_step(self, uuid: str, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Хук allure: выход из шага. Снимаем результат шага — по нему сверяется бизнес-состояние."""
        self.depth -= 1
        if self.depth != 0:
            return
        self._capture()

    def _capture(self) -> None:
        """Снимает DOM текущей страницы и дописывает его в файл."""
        page = self._current_page()
        if page is None:
            self.skipped.append(f"шаг {self.step_no}: страница браузера ещё не создана")
            return
        try:
            url = page.url
            if url.startswith(BLANK_URL_PREFIXES):
                self.skipped.append(f"шаг {self.step_no}: страница пуста ({url})")
                return
            html = page.content()
        except Exception as error:  # страница могла закрыться или уйти в навигацию
            self.skipped.append(f"шаг {self.step_no}: снять DOM не удалось ({type(error).__name__}: {error})")
            return
        self._write(html)

    @staticmethod
    def _current_page() -> Any:
        """Возвращает текущую страницу playwright из контекста теста или None."""
        try:
            from models.context import test_context
        except Exception:
            return None
        page = getattr(test_context, "page", None)
        return page or None

    def _write(self, html: str) -> None:
        """Дописывает снимок в файл: сначала шапка кейса, затем строка шага и DOM одной строкой.

        Второй снимок шага не пишется, если он не отличается от первого: шаг мог ничего
        не поменять на странице, и копия того же мегабайта разбору ничего не добавит.
        Первый снимок шага пишется всегда — иначе шаг остался бы без снимка и его локаторы
        никто бы не проверил.
        """
        single_line = " ".join(html.split())
        digest = hashlib.md5(single_line.encode("utf-8")).hexdigest()
        if self._step_has_snapshot and digest == self._last_digest:
            self.skipped_same += 1
            return
        self._last_digest = digest
        self._step_has_snapshot = True
        self.dump_path.parent.mkdir(parents=True, exist_ok=True)
        with self.dump_path.open("a", encoding="utf-8") as dump:
            if not self._header_written:
                header = f"allure.id {self.case_no}" if self.case_no is not None else f"# {self.test_name}"
                dump.write(header + "\n")
                self._header_written = True
            dump.write(f"шаг {self.step_no}\n")
            dump.write(single_line + "\n")
        self.written += 1


def allure_id_of(item: object) -> int | None:
    """Достаёт allure.id теста из его маркеров.

    Номер кейса из заголовка (``15. Перевод клиента ...``) недоступен: allure.title
    в маркеры pytest не попадает, а allure.id попадает как ``allure_label`` с
    ``label_type="as_id"``. По нему разбор и находит тест.

    :param item: Тест pytest.
    :return: Идентификатор из allure.id или None.
    """
    for marker in getattr(item, "own_markers", ()):
        if getattr(marker, "kwargs", {}).get("label_type") == "as_id" and marker.args:
            try:
                return int(marker.args[0])
            except (TypeError, ValueError):
                return None
    return None


def start_recording(dump_path: Path, case_no: int | None, test_name: str) -> DomRecorder:
    """Регистрирует запись DOM: начинает файл с нуля и подписывается на хуки allure."""
    if dump_path.exists():
        dump_path.unlink()
    recorder = DomRecorder(dump_path, case_no, test_name)
    plugin_manager.register(recorder)
    return recorder


def stop_recording(recorder: DomRecorder) -> None:
    """Снимает подписку на хуки allure."""
    try:
        plugin_manager.unregister(recorder)
    except Exception:
        pass
