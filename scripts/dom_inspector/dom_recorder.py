"""Автоматическая запись DOM по шагам теста во время прогона.

Подписывается на официальные хуки allure (``allure_commons.plugin_manager``) и после выхода
из каждого шага верхнего уровня — то есть из ``with allure.step(...)``, написанного прямо
в тесте, — сохраняет текущий DOM страницы в файл-дамп.

Снимок пишется на входе и на выходе каждого шага — и вложенные шаги пейдж-объектов тоже
снимаются, все под номером шага теста, в который они вложены. Двух снимков на шаг теста мало:
один ``with allure.step`` тянет десяток действий, и кнопка «Далее», нажатая в середине, ни
на входе, ни на выходе уже не видна — локатор выглядит сломанным, хотя тест прошёл. Глубина
ограничена :data:`MAX_STEP_DEPTH`: шаги обёрток элементов (``fill``, ``click``) лежат глубже
и снимков не дают, иначе дамп распухнет на пустом месте. Одинаковые подряд снимки не пишутся.

Из снимка вырезается содержимое ``<style>`` и ``<script>``: девять десятых веса страницы —
это CSS, а разбору нужна разметка. Вырезает парсер, а не регулярка: разметка при этом
не страдает, что проверено сравнением выборок по снимкам.

Если шаг упал, после его снимков дописывается строка с ошибкой — по одному DOM не всегда
видно, на каком именно вызове playwright сдался.

Формат файла::

    allure.id 902222
    шаг 1
    <html ...>...</html>
    шаг 1
    <html ...>...</html>
    шаг 2
    <html ...>...</html>
    ошибка шага 2: TimeoutError: Locator.click: Timeout 15000ms exceeded

Включается ключом ``--dump-dom`` при запуске pytest, файлы кладутся в
``scripts/dom_inspector/dumps/<имя теста>.txt``. Запись живёт только на фазу вызова теста,
поэтому шаги setup-фикстур (авторизация, создание клиента по API) в дамп не попадают.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from allure_commons import hookimpl, plugin_manager
from bs4 import BeautifulSoup

BLANK_URL_PREFIXES = ("about:", "chrome-error:")

#: Сколько символов сообщения об ошибке писать в дамп: playwright печатает простыню на полсотни
#: строк, а разбору нужны тип ошибки и первая строка — по ним и видно, что именно не сработало.
MAX_ERROR_LENGTH = 400

#: До какой вложенности шагов снимать DOM. 1 — шаг теста, 2 — метод пейджа, вызванный из теста,
#: 3 — метод пейджа, вызванный из метода пейджа. Глубже лежат шаги обёрток элементов: снимок
#: на каждый fill и click дал бы сотни почти одинаковых страниц.
MAX_STEP_DEPTH = 3


def _without_styles(html: str) -> str:
    """Вырезает из снимка содержимое ``<style>`` и ``<script>``.

    На CSS приходится около девяти десятых веса страницы, а разбору он не нужен: локаторы
    ищутся по разметке. Режется парсером, а не регуляркой: подстрока ``ant-modal-content``
    встречается и в правиле CSS, и в атрибуте класса, и текстовая замена сносит оба.

    :param html: Снимок страницы целиком.
    :return: Снимок без содержимого стилей и скриптов; при сбое разбора — исходный снимок.
    """
    try:
        soup = BeautifulSoup(html, "lxml")
        for tag in soup(["style", "script"]):
            tag.decompose()
        return str(soup)
    except Exception:  # разбор не должен стоить снимка
        return html


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
        if self.depth <= MAX_STEP_DEPTH:
            self._capture()

    @hookimpl
    def stop_step(self, uuid: str, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Хук allure: выход из шага. Снимаем результат шага — по нему сверяется бизнес-состояние."""
        depth = self.depth
        self.depth -= 1
        if depth <= MAX_STEP_DEPTH:
            self._capture()
        if depth == 1 and exc_type is not None:
            self._write_error(exc_type, exc_val)

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
        self._write(_without_styles(html))

    def _write_error(self, exc_type: Any, exc_val: Any) -> None:
        """Дописывает в дамп причину падения шага.

        Снимок показывает, ЧТО осталось на странице, но не показывает, на каком вызове тест
        сдался: локатор мог не найтись, клик — не пройти по strict mode, ожидание — истечь.

        :param exc_type: Класс исключения.
        :param exc_val: Само исключение.
        """
        name = getattr(exc_type, "__name__", str(exc_type))
        message = " ".join(str(exc_val).split())[:MAX_ERROR_LENGTH]
        with self.dump_path.open("a", encoding="utf-8") as dump:
            dump.write(f"ошибка шага {self.step_no}: {name}: {message}\n")

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
