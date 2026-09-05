"""Автоматическая запись DOM по шагам теста во время прогона.

Подписывается на официальные хуки allure (``allure_commons.plugin_manager``) и после выхода
из каждого шага верхнего уровня — то есть из ``with allure.step(...)``, написанного прямо
в тесте, — сохраняет текущий DOM страницы в файл-дамп.

Шаги внутри пейдж-объектов (декораторы ``@allure.step`` на методах) вложены в шаг теста,
поэтому в дамп не попадают: снимок делается ровно один раз на шаг теста.

Формат файла совпадает с тем, что читает :mod:`scripts.dom_inspector.dump_parser`::

    case 15
    шаг 2
    <html ...>...</html>
    шаг 3
    <html ...>...</html>

Включается ключом ``--dump-dom`` при запуске pytest, файлы кладутся в
``scripts/dom_inspector/dumps/<имя теста>.txt``.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from allure_commons import hookimpl, plugin_manager

CASE_NO_RE = re.compile(r"^\s*(\d+)\s*[.)]")
BLANK_URL_PREFIXES = ("about:", "chrome-error:")


class DomRecorder:
    """Плагин allure: пишет DOM страницы после каждого шага теста верхнего уровня.

    :param dump_path: файл, в который дописываются снимки
    :param case_no: номер кейса из заголовка теста, если удалось его разобрать
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
        self._header_written = False

    @hookimpl
    def start_step(self, uuid: str, title: str, params: dict[str, Any]) -> None:
        """Хук allure: вход в шаг. Считаем вложенность, чтобы отличать шаги теста от шагов пейджей."""
        self.depth += 1

    @hookimpl
    def stop_step(self, uuid: str, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Хук allure: выход из шага. Снимок делаем только для шага верхнего уровня."""
        self.depth -= 1
        if self.depth != 0:
            return
        self.step_no += 1
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
        """Дописывает снимок в файл: сначала шапка кейса, затем строка шага и DOM одной строкой."""
        self.dump_path.parent.mkdir(parents=True, exist_ok=True)
        with self.dump_path.open("a", encoding="utf-8") as dump:
            if not self._header_written:
                dump.write(f"case {self.case_no}\n" if self.case_no is not None else f"# {self.test_name}\n")
                self._header_written = True
            dump.write(f"шаг {self.step_no}\n")
            dump.write(" ".join(html.split()) + "\n")
        self.written += 1


def case_no_from_title(title: str | None) -> int | None:
    """Достаёт номер кейса из заголовка вида '15. Перевод клиента ...'."""
    if not title:
        return None
    found = CASE_NO_RE.match(title)
    return int(found.group(1)) if found else None


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
