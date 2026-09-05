"""Самопроверка пакета ``scripts.dom_inspector``: приёмочный сценарий заказчика плюс регрессии.

Запуск из корня репозитория::

    .venv/Scripts/python.exe -m scripts.dom_inspector.selfcheck.check_pipeline

Проверяется три вещи:

* приёмочный сценарий на синтетической мини-фикстуре: локатор ``chm-ChmAgreementsList-tlb-1-create``
  подписан «Кнопка 'Добавить' договор», в DOM это кнопка «Создать», встречается дважды,
  один экземпляр скрыт через ``clip-path: inset(100%)``. Ожидаем ``UNIQUE_VISIBLE``,
  ``text_mismatch=True`` и первым кандидатом настоящую кнопку «Добавить».
  Фикстура нужна потому, что в живом репозитории этот локатор уже поправлен руками;
* разбор дампа: маркеры кейсов, границы снимков, классификация пометок;
* подкоманда ``inspect``: поиск по атрибутам (class, type, href, data-*), отличие истинного нуля
  от ложного и совпадение машинного вывода ``--json`` с человеческим;
* фильтр покрытия: класс-владелец вместо файла, якорный ``#id`` и раздел про страницы вне дампа;
* регрессия по репозиторию: число собранных локаторов и единственный битый селектор.

Скрипт ничего не пишет в репозиторий: временные файлы создаются в каталоге ОС и удаляются.
"""

from __future__ import annotations

import contextlib
import io
import json
import shutil
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT_PATH = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT_PATH) not in sys.path:
    sys.path.append(str(PROJECT_ROOT_PATH))

from scripts.dom_inspector.cli import (  # noqa: E402
    build_parser,
    render_report,
    report_to_dict,
    run_inspect,
    section_of,
)
from scripts.dom_inspector.dump_parser import parse_dump_with_warnings  # noqa: E402
from scripts.dom_inspector.locator_checker import check_dump, collapse_ws_outside_quotes  # noqa: E402
from scripts.dom_inspector.locator_collector import (  # noqa: E402
    EXPECTED_LOCATOR_COUNT,
    SYNTHESIZED_WRAPPERS,
    classify_selector,
    collect_locators,
)
from scripts.dom_inspector.models import InspectionOptions, MatchStatus, NoteStatus, SelectorKind  # noqa: E402

#: Эталонный локатор из практики: подписан «Добавить», а в DOM это «Создать» в двух экземплярах.
REFERENCE_SELECTOR = "[data-testid=chm-ChmAgreementsList-tlb-1-create]"

#: Локатор, который человек нашёл руками как правильную замену.
REFERENCE_REPLACEMENT = "[data-testid=chm-ChmAgreementCreation-btn-agreements-buttons-addButtonTitle]"

#: Мини-снимок DOM: настоящая кнопка «Добавить», видимая «Создать» и её скрытый дубль.
FIXTURE_HTML = (
    '<body><div id="app" class="platform-root">'
    '<button data-testid="chm-ChmAgreementCreation-btn-agreements-buttons-addButtonTitle" '
    'type="button" class="ant-btn ant-btn-primary"><span>Добавить</span></button>'
    '<button data-testid="chm-ChmAgreementsList-tlb-1-create" type="button" class="ant-btn">'
    "<span>Создать</span></button>"
    '<div style="clip-path: inset(100%); position: fixed; opacity: 0; z-index: -200">'
    '<button data-testid="chm-ChmAgreementsList-tlb-1-create" type="button" class="ant-btn">'
    "<span>Создать</span></button></div>"
    '<div class="ant-modal-content"><div class="ant-modal-title">Найден дубликат</div></div>'
    "</div></body>"
)

#: Синтетический дамп: маркер кейса, снимок, пометка автора и кейс со ссылкой на баг.
FIXTURE_DUMP = "\n".join(
    [
        "case 29:",
        FIXTURE_HTML,
        "Все есть",
        "case31:",
        "тут баг, так что скипни по причине https://jira.nexign.com/browse/RMBSS-18239",
        "",
    ]
)

#: Фикстура локаторов: тот самый неверно подписанный локатор плюс заведомо отсутствующий.
FIXTURE_LOCATORS = '''"""Фикстура локаторов для самопроверки dom_inspector."""

from pages.ui_elements import Element, ElementsList


class AgreementsFixtureElements:
    """Локаторы мини-фикстуры."""

    def __init__(self) -> None:
        """Объявляет локаторы фикстуры."""
        self.ADD_AGREEMENT_BTN = Element("[data-testid=chm-ChmAgreementsList-tlb-1-create]", "Кнопка 'Добавить' договор")
        self.MODAL_TITLE = Element("[class*=modal-title]", "Заголовок модального окна")
        self.MISSING_BTN = Element("[data-testid=totally-absent-button]", "Кнопка 'Которой нет'")
        self.ROWS = ElementsList("button", "Кнопки страницы")
'''

#: Мини-снимок для проверки фильтра покрытия: страница с якорным id и тремя опознаваемыми кнопками.
COVERAGE_HTML = (
    '<body><div id="anchor-page" class="page">'
    '<button data-testid="cov-one" type="button"><span>Один</span></button>'
    '<button data-testid="cov-two" type="button"><span>Два</span></button>'
    '<button data-testid="cov-three" type="button"><span>Три</span></button>'
    "</div></body>"
)

#: Дамп для проверки фильтра покрытия.
COVERAGE_DUMP = "\n".join(["case 1:", COVERAGE_HTML, ""])

#: Класс-владелец, чья страница в дампе есть: три локатора находятся, четвёртый сломан.
COVERAGE_PRESENT_LOCATORS = '''"""Фикстура: страница, которая в дампе есть."""

from pages.ui_elements import Element


class CoveredPageElements:
    """Локаторы присутствующей страницы."""

    def __init__(self) -> None:
        """Объявляет локаторы присутствующей страницы."""
        self.ONE = Element("[data-testid=cov-one]", "Кнопка 'Один'")
        self.TWO = Element("[data-testid=cov-two]", "Кнопка 'Два'")
        self.THREE = Element("[data-testid=cov-three]", "Кнопка 'Три'")
        self.BROKEN = Element("#anchor-page span[class*='spin-dot']", "Лоадер страницы")
'''

#: Класс-владелец, чьей страницы в дампе нет вовсе: покрытие нулевое.
COVERAGE_ABSENT_LOCATORS = '''"""Фикстура: страница, которой в дампе нет."""

from pages.ui_elements import Element


class AbsentPageElements:
    """Локаторы отсутствующей страницы."""

    def __init__(self) -> None:
        """Объявляет локаторы отсутствующей страницы."""
        self.A = Element("[data-testid=absent-a]", "Кнопка A")
        self.B = Element("[data-testid=absent-b]", "Кнопка B")
        self.C = Element("[data-testid=absent-c]", "Кнопка C")
'''

#: Класс с низким покрытием: 1 из 6 локаторов найден, но у одного из сломанных есть якорь страницы.
COVERAGE_ANCHOR_LOCATORS = '''"""Фикстура: низкое покрытие плюс якорный id в селекторе."""

from pages.ui_elements import Element


class AnchorProbeElements:
    """Локаторы с низким покрытием класса."""

    def __init__(self) -> None:
        """Объявляет локаторы с низким покрытием класса."""
        self.FOUND = Element("[data-testid=cov-one]", "Кнопка 'Один'")
        self.NO_ANCHOR_1 = Element("[data-testid=nope-1]", "Нет якоря 1")
        self.NO_ANCHOR_2 = Element("[data-testid=nope-2]", "Нет якоря 2")
        self.NO_ANCHOR_3 = Element("[data-testid=nope-3]", "Нет якоря 3")
        self.NO_ANCHOR_4 = Element("[data-testid=nope-4]", "Нет якоря 4")
        self.ANCHORED = Element("#anchor-page .spin-dot", "Лоадер по якорю страницы")
'''


def _fail(failures: list[str], condition: bool, message: str) -> None:
    """Регистрирует проваленную проверку.

    :param failures: Накопитель сообщений об ошибках.
    :param condition: Проверяемое условие.
    :param message: Что именно ожидалось.
    :return: Ничего.
    """
    if condition:
        print(f"  ok   {message}")
    else:
        print(f"  FAIL {message}")
        failures.append(message)


def check_reference_case(failures: list[str], workdir: Path) -> None:
    """Приёмочный сценарий заказчика на синтетической мини-фикстуре.

    :param failures: Накопитель сообщений об ошибках.
    :param workdir: Временный каталог для фикстур.
    :return: Ничего.
    """
    print("Приёмочный сценарий (мини-фикстура):")
    dump_path = workdir / "fixture_dump"
    dump_path.write_text(FIXTURE_DUMP, encoding="utf-8")
    locators_root = workdir / "fixture_locators"
    locators_root.mkdir()
    (locators_root / "__init__.py").write_text("", encoding="utf-8")
    (locators_root / "agreements_fixture.py").write_text(FIXTURE_LOCATORS, encoding="utf-8")
    options = InspectionOptions(
        dump_path=dump_path,
        locators_root=locators_root,
        ui_elements_path=PROJECT_ROOT_PATH / "pages" / "ui_elements.py",
        project_root=workdir,
        fail_on_problems=True,
    )
    report = check_dump(options)
    by_attr = {check.locator.attr: check for check in report.checks}
    _fail(failures, len(report.checks) == 4, f"собрано 4 локатора фикстуры (получено {len(report.checks)})")
    reference = by_attr.get("ADD_AGREEMENT_BTN")
    if reference is None:
        failures.append("локатор ADD_AGREEMENT_BTN не собран")
        print("  FAIL локатор ADD_AGREEMENT_BTN не собран")
        return
    _fail(failures, reference.locator.selector == REFERENCE_SELECTOR, "селектор эталонного локатора разобран как есть")
    _fail(
        failures,
        reference.status is MatchStatus.UNIQUE_VISIBLE,
        f"статус эталонного локатора unique_visible (получен {reference.status})",
    )
    _fail(
        failures,
        reference.max_matches_in_snapshot == 2,
        f"совпадений в снимке 2 (получено {reference.max_matches_in_snapshot})",
    )
    _fail(failures, reference.text_mismatch, "расхождение описания и текста поймано")
    _fail(failures, reference.expected_text == "Добавить", f"из описания взято 'Добавить' ({reference.expected_text})")
    _fail(failures, reference.observed_texts == ["Создать"], f"в DOM найдено 'Создать' ({reference.observed_texts})")
    candidates = [candidate.selector for candidate in reference.candidates]
    _fail(
        failures,
        bool(candidates) and candidates[0] == REFERENCE_REPLACEMENT,
        f"первый кандидат — настоящая кнопка «Добавить» ({candidates[:1]})",
    )
    hidden = [element for result in reference.results for element in result.elements if not element.rendered]
    _fail(
        failures,
        any(element.hidden_reason == "css:clip-path-inset-100" for element in hidden),
        "дубль опознан как скрытый через clip-path: inset(100%)",
    )
    _fail(
        failures,
        all(element.pw_visible for result in reference.results for element in result.elements),
        "скрытый дубль всё равно считается для strict mode (pw_visible=True)",
    )
    missing = by_attr["MISSING_BTN"]
    _fail(failures, missing.status is MatchStatus.NOT_FOUND, f"отсутствующий локатор — not_found ({missing.status})")
    _fail(failures, section_of(reference) == "text_mismatch", "эталон попадает в раздел про расхождение текста")
    _fail(failures, section_of(missing) == "not_found", "отсутствующий локатор попадает в раздел сломанных")
    _fail(failures, report.exit_code == 1, "код возврата 1 при найденных проблемах")
    args = build_parser().parse_args(["check", str(dump_path)])
    text = render_report(report, args)
    _fail(failures, "СЛОМАННЫЕ ЛОКАТОРЫ" in text, "в текстовом отчёте есть раздел сломанных локаторов")
    _fail(failures, REFERENCE_REPLACEMENT in text, "в текстовом отчёте напечатан кандидат на замену")
    payload = report_to_dict(report, args)
    _fail(failures, payload["problems_total"] >= 2, "машинный отчёт содержит найденные проблемы")


def check_dump_parsing(failures: list[str], workdir: Path) -> None:
    """Регрессия разбора дампа на синтетическом файле.

    :param failures: Накопитель сообщений об ошибках.
    :param workdir: Временный каталог для фикстур.
    :return: Ничего.
    """
    print("Разбор дампа:")
    dump_path = workdir / "fixture_dump"
    document, warnings = parse_dump_with_warnings(dump_path)
    _fail(failures, len(document.snapshots) == 1, f"снимков 1 (получено {len(document.snapshots)})")
    _fail(failures, len(document.blocks) == 2, f"кейсов 2 (получено {len(document.blocks)})")
    _fail(failures, document.blocks[0].case_no == 29, "первый маркер разобран как case 29")
    _fail(failures, document.blocks[1].case_no == 31, "слитный маркер case31 разобран")
    _fail(failures, document.blocks[0].status is NoteStatus.DONE, "пометка «Все есть» даёт статус done")
    _fail(failures, document.blocks[1].status is NoteStatus.SKIP, "ссылка на Jira даёт статус skip")
    _fail(
        failures,
        document.blocks[1].notes[0].jira_key == "RMBSS-18239",
        "ключ задачи Jira извлечён из ссылки",
    )
    _fail(failures, not warnings, f"предупреждений нет (получено {warnings})")
    _fail(failures, not document.snapshots[0].truncated, "снимок не помечен усечённым")


def check_inspect_search(failures: list[str], workdir: Path) -> None:
    """Регрессия подкоманды ``inspect``: поиск по атрибутам, честный ноль и фильтрация JSON.

    Закрывает три претензии приёмки: поиск не видел class/type/href/data-*; вывод не показывал
    атрибуты вообще; ``--json`` игнорировал ``--search`` и ``--limit``.

    :param failures: Накопитель сообщений об ошибках.
    :param workdir: Временный каталог для фикстур.
    :return: Ничего.
    """
    print("Подкоманда inspect:")
    dump_path = workdir / "fixture_dump"
    parser = build_parser()

    def run(*extra: str) -> str:
        """Прогоняет ``inspect`` и возвращает захваченный stdout.

        :param extra: Дополнительные ключи командной строки.
        :return: Текст вывода.
        """
        args = parser.parse_args(["inspect", str(dump_path), *extra])
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            run_inspect(args)
        return buffer.getvalue()

    by_class = run("--search", "ant-modal-content")
    _fail(failures, "[атрибут]" in by_class, "поиск находит элемент по значению class")
    _fail(failures, "class='ant-modal-content'" in by_class, "в выводе показано, в каком атрибуте совпало")
    by_type = run("--search", "ant-btn")
    _fail(failures, "совпадений по 'ant-btn': 3" in by_type, f"по class найдены все три кнопки:\n{by_type}")
    verbose = run("--search", "addButtonTitle", "-v")
    _fail(failures, "type='button'" in verbose, "с ключом -v печатаются атрибуты элемента")
    true_zero = run("--search", "совершенно-отсутствующая-строка")
    _fail(failures, "настоящий ноль" in true_zero, "истинный ноль назван истинным")
    false_zero = run("--search", "z-index")
    _fail(failures, "ложный ноль" in false_zero, f"ложный ноль отличён от истинного:\n{false_zero}")
    _fail(failures, "grep -o -F" in false_zero, "при ложном нуле выдана подсказка про grep")

    json_path = workdir / "inspect.json"
    args = parser.parse_args(["inspect", str(dump_path), "--search", "ant-btn", "--json", str(json_path)])
    with contextlib.redirect_stdout(io.StringIO()):
        run_inspect(args)
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    elements = [element for entry in payload for element in entry["elements"]]
    _fail(failures, len(elements) == 3, f"--json отдаёт ровно отфильтрованные элементы (получено {len(elements)})")
    _fail(failures, all("attrs" in element for element in elements), "в JSON у элемента есть словарь attrs")
    _fail(
        failures,
        any(element["attrs"].get("type") == "button" for element in elements),
        "атрибут type виден в машинном выводе",
    )
    limited = workdir / "inspect_limited.json"
    args = parser.parse_args(["inspect", str(dump_path), "--search", "ant-btn", "--limit", "1", "--json", str(limited)])
    with contextlib.redirect_stdout(io.StringIO()):
        run_inspect(args)
    limited_payload = json.loads(limited.read_text(encoding="utf-8"))
    limited_elements = [element for entry in limited_payload for element in entry["elements"]]
    _fail(failures, len(limited_elements) == 1, f"--json учитывает --limit (получено {len(limited_elements)})")


def check_coverage_filter(failures: list[str], workdir: Path) -> None:
    """Регрессия фильтра покрытия: класс-владелец, якорный id и раздел про пропущенные страницы.

    :param failures: Накопитель сообщений об ошибках.
    :param workdir: Временный каталог для фикстур.
    :return: Ничего.
    """
    print("Фильтр покрытия:")
    dump_path = workdir / "coverage_dump"
    dump_path.write_text(COVERAGE_DUMP, encoding="utf-8")
    locators_root = workdir / "coverage_locators"
    locators_root.mkdir()
    (locators_root / "__init__.py").write_text("", encoding="utf-8")
    (locators_root / "covered_page.py").write_text(COVERAGE_PRESENT_LOCATORS, encoding="utf-8")
    (locators_root / "absent_page.py").write_text(COVERAGE_ABSENT_LOCATORS, encoding="utf-8")
    (locators_root / "anchor_page.py").write_text(COVERAGE_ANCHOR_LOCATORS, encoding="utf-8")
    options = InspectionOptions(
        dump_path=dump_path,
        locators_root=locators_root,
        ui_elements_path=PROJECT_ROOT_PATH / "pages" / "ui_elements.py",
        project_root=workdir,
    )
    report = check_dump(options)
    by_origin = {f"{check.locator.class_name}.{check.locator.attr}": check for check in report.checks}
    broken = by_origin["CoveredPageElements.BROKEN"]
    _fail(
        failures,
        broken.status is MatchStatus.NOT_FOUND,
        f"сломанный локатор присутствующей страницы — not_found (получен {broken.status})",
    )
    anchored = by_origin["AnchorProbeElements.ANCHORED"]
    _fail(
        failures,
        anchored.status is MatchStatus.NOT_FOUND,
        f"якорный id перевешивает низкое покрытие класса (получен {anchored.status})",
    )
    _fail(failures, anchored.owner_anchor_found, "якорь селектора отмечен в результате проверки")
    no_anchor = by_origin["AnchorProbeElements.NO_ANCHOR_1"]
    _fail(
        failures,
        no_anchor.status is MatchStatus.PAGE_NOT_IN_DUMP,
        f"локатор без якоря при низком покрытии остаётся отфильтрованным (получен {no_anchor.status})",
    )
    absent = by_origin["AbsentPageElements.A"]
    _fail(
        failures,
        absent.status is MatchStatus.PAGE_NOT_IN_DUMP,
        f"страница, которой нет в дампе, отфильтрована (получен {absent.status})",
    )
    _fail(
        failures,
        any("--coverage 0" in warning for warning in report.warnings),
        "в предупреждениях сказано про --coverage 0",
    )
    args = build_parser().parse_args(["check", str(dump_path), "--limit", "0"])
    text = render_report(report, args)
    _fail(failures, "СТРАНИЦЫ, КОТОРЫХ НЕТ В ДАМПЕ" in text, "в отчёте есть раздел про страницы вне дампа")
    _fail(failures, "absent_page.py" in text, "отфильтрованный файл назван по имени")
    _fail(failures, "AbsentPageElements" in text, "отфильтрованный класс назван по имени")
    payload = report_to_dict(report, args)
    _fail(failures, "pages_not_in_dump" in payload, "в JSON есть ключ pages_not_in_dump")
    absent_entry = next(
        (entry for entry in payload["pages_not_in_dump"] if entry["file"].endswith("absent_page.py")), None
    )
    _fail(
        failures,
        absent_entry is not None and absent_entry["skipped"] == 3 and absent_entry["found"] == 0,
        f"в JSON у отсутствующей страницы пропущено 3, найдено 0 (получено {absent_entry})",
    )
    _fail(
        failures,
        payload["pages_not_in_dump_total"] == 7,
        f"всего отфильтровано 7 локаторов (получено {payload['pages_not_in_dump_total']})",
    )


def check_repository(failures: list[str]) -> None:
    """Регрессия по реальному репозиторию: сбор локаторов и классификация селекторов.

    :param failures: Накопитель сообщений об ошибках.
    :return: Ничего.
    """
    print("Репозиторий:")
    records, _ = collect_locators(
        PROJECT_ROOT_PATH / "pages" / "locators",
        PROJECT_ROOT_PATH / "pages" / "ui_elements.py",
        PROJECT_ROOT_PATH,
    )
    _fail(
        failures,
        len(records) == EXPECTED_LOCATOR_COUNT,
        f"собрано {EXPECTED_LOCATOR_COUNT} локаторов (получено {len(records)})",
    )
    _fail(failures, all(record.selector for record in records), "пустых селекторов нет")
    synthesized = [record for record in records if record.wrapper in SYNTHESIZED_WRAPPERS]
    _fail(failures, len(synthesized) == 40, f"локаторов с синтезом id 40 (получено {len(synthesized)})")
    _fail(
        failures,
        all(record.selector.startswith(("[id$=", "[class*=dropdown-trigger]")) for record in synthesized),
        "у SelectWithId/DropdownWithId селектор собран по шаблону, а не взят сырым id",
    )
    _fail(
        failures,
        classify_selector("div.foo") is SelectorKind.CSS,
        "CSS не принимается за XPath (lxml компилирует 'div.foo' как валидный XPath)",
    )
    _fail(failures, classify_selector("//button[1]") is SelectorKind.XPATH, "XPath распознан по префиксу")
    _fail(failures, collapse_ws_outside_quotes("div  > p") == "div > p", "пробелы схлопнуты (иначе падает soupsieve)")
    _fail(
        failures,
        collapse_ws_outside_quotes("[title='а  б']") == "[title='а  б']",
        "пробелы внутри кавычек сохранены",
    )


def main() -> None:
    """Точка входа самопроверки.

    :return: Ничего.
    :raises SystemExit: Кодом 1, если хотя бы одна проверка провалилась.
    """
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8")
    failures: list[str] = []
    workdir = Path(tempfile.mkdtemp(prefix="dom_inspector_selfcheck_"))
    try:
        check_reference_case(failures, workdir)
        check_dump_parsing(failures, workdir)
        check_inspect_search(failures, workdir)
        check_coverage_filter(failures, workdir)
        check_repository(failures)
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
    print("")
    if failures:
        print(f"ПРОВАЛЕНО ПРОВЕРОК: {len(failures)}")
        for failure in failures:
            print(f"  - {failure}")
        sys.exit(1)
    print("Все проверки пройдены.")


if __name__ == "__main__":
    main()
