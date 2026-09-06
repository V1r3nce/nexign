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

Из снимка вырезается содержимое ``<style>``, ``<script>`` и внутренности ``<svg>``: вместе это
пять шестых веса страницы, а разбору нужна разметка. Сами теги ``<svg>`` остаются — по ним
есть локаторы. Вырезает парсер, а не регулярка: разметка при этом не страдает, что проверено
сравнением выборок по снимкам.

Перед снимком пишется строка ``шаг N · <заголовок шага>``: номер — это шаг теста, заголовок —
тот шаг (в том числе вложенный), на границе которого снят DOM; у снимка с выхода из шага
к заголовку добавляется ``(выход)``. Без заголовка по дампу не понять, какое именно действие
дало снимок.

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

from allure_commons import plugin_manager
from bs4 import BeautifulSoup

from scripts.dom_inspector.step_tracker import StepTracker

BLANK_URL_PREFIXES = ("about:", "chrome-error:")

#: Сколько символов сообщения об ошибке писать в дамп: playwright печатает простыню на полсотни
#: строк, а разбору нужны тип ошибки и первая строка — по ним и видно, что именно не сработало.
MAX_ERROR_LENGTH = 400

#: До какой вложенности шагов снимать DOM. 1 — шаг теста, 2 — метод пейджа, вызванный из теста,
#: 3 — метод пейджа, вызванный из метода пейджа. Глубже лежат шаги обёрток элементов: снимок
#: на каждый fill и click дал бы сотни почти одинаковых страниц.
MAX_STEP_DEPTH = 4

#: Сколько символов заголовка шага писать рядом со снимком.
MAX_TITLE_LENGTH = 120


def _slim_snapshot(html: str) -> str:
    """Выкидывает из снимка то, что весит, но разбору не нужно.

    Полностью убираются ``<style>`` и ``<script>``, у ``<svg>`` вычищается содержимое, а сам тег
    остаётся — на него есть локаторы. Режется парсером, а не регуляркой: подстрока
    ``ant-modal-content`` встречается и в правиле CSS, и в атрибуте класса, и текстовая замена
    сносит оба. Парсер ``lxml`` быстрее, но он не всегда установлен, поэтому есть запасной
    стандартный ``html.parser``: молча отдавать нечищеный снимок в разы дороже.

    :param html: Снимок страницы целиком.
    :return: Облегчённый снимок; если разобрать не удалось ни одним парсером — исходный.
    """
    for parser in ("lxml", "html.parser"):
        try:
            soup = BeautifulSoup(html, parser)
        except Exception:  # парсер не установлен — пробуем следующий
            continue
        for tag in soup(["style", "script"]):
            tag.decompose()
        for tag in soup("svg"):
            tag.clear()
        return str(soup)
    return html


class DomRecorder(StepTracker):
    """Плагин allure: пишет DOM страницы на входе и выходе каждого шага теста.

    Снимка только на выходе не хватает: локаторы шага работают внутри него, а к концу шага
    страница уже другая. Кнопка «Далее» сменилась на «Создать», форма редактирования закрылась
    после сохранения — и целый локатор выглядит сломанным.

    :param dump_path: файл, в который дописываются снимки
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
        self.skipped_same = 0
        self._step_digests: set[str] = set()

    def on_test_step_start(self) -> None:
        """Новый шаг теста: снимки предыдущего больше не мешают отсеивать повторы."""
        super().on_test_step_start()
        self._step_digests.clear()

    def on_boundary(self, depth: int, title: str, exiting: bool) -> None:
        """Снимает DOM на границе шага, если она не глубже :data:`MAX_STEP_DEPTH`.

        :param depth: Глубина шага.
        :param title: Заголовок шага.
        :param exiting: True для выхода из шага.
        """
        if depth > MAX_STEP_DEPTH:
            return
        if exiting:
            self._capture(f"{title} (выход)" if title else "")
        else:
            self._capture(title)

    def on_test_step_end(self, exc_type: Any, exc_val: Any) -> None:
        """Дописывает причину падения шага теста.

        :param exc_type: Класс исключения.
        :param exc_val: Исключение.
        """
        if exc_type is not None:
            self._write_error(exc_type, exc_val)

    def _capture(self, title: str) -> None:
        """Снимает DOM текущей страницы и дописывает его в файл.

        :param title: Заголовок шага, на границе которого снят DOM.
        """
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
        self._write(_slim_snapshot(html), title)

    def write_header(self) -> None:
        """Пишет шапку дампа: по ней разбор понимает, к какому тесту относится файл.

        Шапка пишется сразу, а не с первым снимком: тест мог упасть до того, как появилась
        хоть одна страница, и такой файл с одной строкой об ошибке всё равно должен быть
        опознан — иначе разбор относит его к чужому кейсу.
        """
        self.dump_path.parent.mkdir(parents=True, exist_ok=True)
        header = f"allure.id {self.case_no}" if self.case_no is not None else f"# {self.test_name}"
        with self.dump_path.open("a", encoding="utf-8") as dump:
            dump.write(header + "\n")

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

    def _write(self, html: str, title: str) -> None:
        """Дописывает снимок в файл: сначала шапка кейса, затем строка шага и DOM одной строкой.

        Повтор внутри шага не пишется: у шага теста граница входа и выхода есть у каждого
        вложенного шага, и добрая половина этих снимков — одна и та же страница. Разбору
        второй экземпляр ничего не добавляет, а дамп от него распухает вдвое. Сравнение идёт
        со всеми снимками шага, а не только с предыдущим: страница часто возвращается
        к прежнему виду (форма открылась и закрылась), и такой возврат тоже повтор.

        :param html: Облегчённый снимок страницы.
        :param title: Заголовок шага, на границе которого снят DOM.
        """
        single_line = " ".join(html.split())
        digest = hashlib.md5(single_line.encode("utf-8")).hexdigest()
        if digest in self._step_digests:
            self.skipped_same += 1
            return
        self._step_digests.add(digest)
        self.dump_path.parent.mkdir(parents=True, exist_ok=True)
        with self.dump_path.open("a", encoding="utf-8") as dump:
            marker = f"шаг {self.step_no}"
            if title:
                marker += " · " + " ".join(title.split())[:MAX_TITLE_LENGTH]
            dump.write(marker + "\n")
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
    recorder.write_header()
    plugin_manager.register(recorder)
    return recorder


def stop_recording(recorder: DomRecorder) -> None:
    """Снимает подписку на хуки allure."""
    try:
        plugin_manager.unregister(recorder)
    except Exception:
        pass
