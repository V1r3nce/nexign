"""Точка входа утилиты ``dom_inspector``: проверка локаторов репозитория по снимкам DOM со стенда.

Заказчик снимает со стенда ``document.body.outerHTML``, кладёт файл в
``scripts/dom_inspector/dumps`` и запускает утилиту. Она отвечает на два вопроса:

* какие локаторы репозитория в этом DOM не находятся вообще — это сломанные локаторы;
* какие находятся больше одного раза — это риск strict mode в Playwright.

Плюс, где может, предлагает кандидатов на замену: элементы DOM, похожие на описание локатора.

Подкоманды:

* ``check``   — главная: разбор дампа, сбор локаторов, прогон, отчёт (алиас ``html``);
* ``inspect`` — инвентарь элементов снимка: id, data-testid, тексты кнопок, заголовки модалок;
  с ``--search`` ищет по тексту, подписям и любым атрибутам (class, type, href, role, data-*);
* ``api``     — разбор дампа сети devtools; в ``check`` не участвует, это задел под бэкенд-тесты.

Примеры::

    .venv/Scripts/python.exe -m scripts.dom_inspector.cli check scripts/dom_inspector/dumps/need_html
    .venv/Scripts/python.exe -m scripts.dom_inspector.cli check need_html --file client_profile.py
    .venv/Scripts/python.exe -m scripts.dom_inspector.cli inspect need_html --search Добавить
    .venv/Scripts/python.exe -m scripts.dom_inspector.cli inspect need_html --search ant-modal-content -v
    .venv/Scripts/python.exe -m scripts.dom_inspector.cli api scripts/dom_inspector/dumps/need_case
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

PROJECT_ROOT_PATH = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT_PATH) not in sys.path:
    sys.path.append(str(PROJECT_ROOT_PATH))

from scripts.dom_inspector.dump_parser import iter_snapshots, parse_dump_with_warnings  # noqa: E402
from scripts.dom_inspector.element_index import ParsedSnapshot, duplicate_test_ids, parse_snapshot  # noqa: E402
from scripts.dom_inspector.locator_checker import check_dump  # noqa: E402
from scripts.dom_inspector.models import (  # noqa: E402
    DEFAULT_OWNER_COVERAGE_THRESHOLD,
    DomElement,
    InspectionOptions,
    InspectionReport,
    LocatorCheckResult,
    MatchStatus,
    Severity,
    Snapshot,
)

#: Каталог, куда заказчик кладёт снятые со стенда дампы (в git не коммитятся, кроме README).
DEFAULT_DUMPS_DIR: Path = PROJECT_ROOT_PATH / "scripts" / "dom_inspector" / "dumps"

#: Каталог с локаторами страниц.
DEFAULT_LOCATORS_ROOT: Path = PROJECT_ROOT_PATH / "pages" / "locators"

#: Файл с классами-обёртками (Element, ElementsList, SelectWithId и прочими).
DEFAULT_UI_ELEMENTS_PATH: Path = PROJECT_ROOT_PATH / "pages" / "ui_elements.py"

#: Имена файлов в каталоге дампов, которые дампами не являются.
DUMPS_SERVICE_NAMES: frozenset[str] = frozenset({"README.md", ".gitkeep", ".gitignore"})

#: Порядок приоритета уровней важности: чем меньше число, тем важнее находка.
SEVERITY_ORDER: dict[Severity, int] = {
    Severity.HIGH: 0,
    Severity.MEDIUM: 1,
    Severity.LOW: 2,
    Severity.INFO: 3,
}

#: Разделы отчёта по порядку: ключ, заголовок, пояснение. Самое важное сверху.
SECTIONS: tuple[tuple[str, str, str], ...] = (
    (
        "compile_error",
        "СИНТАКСИЧЕСКАЯ ОШИБКА В СЕЛЕКТОРЕ",
        "селектор не компилируется движком — упадёт и в рантайме Playwright",
    ),
    (
        "not_found",
        "СЛОМАННЫЕ ЛОКАТОРЫ (не найдены в DOM)",
        "страница-владелец в дампе есть, а элемент не находится ни разу",
    ),
    (
        "text_mismatch",
        "ОПИСАНИЕ НЕ СОВПАЛО С ТЕКСТОМ ЭЛЕМЕНТА",
        "локатор находится, но подписан не тем, что реально лежит в DOM",
    ),
    (
        "multiple_visible",
        "НЕСКОЛЬКО ВИДИМЫХ СОВПАДЕНИЙ (strict mode)",
        "в снимке больше одного видимого элемента — клик упадёт по strict mode",
    ),
    (
        "unique_visible",
        "ДУБЛИ, ГДЕ ЛИШНИЕ СКРЫТЫ (strict mode)",
        "видимый элемент один, но совпадений несколько; Playwright считает все",
    ),
    (
        "not_checked",
        "НЕ ПРОВЕРЯЕТСЯ АВТОМАТИЧЕСКИ",
        "относительные и Playwright-специфичные селекторы: статически проверить нечем",
    ),
)

#: Разделы, попадающие в отчёт только без ключа --only-problems.
INFO_SECTIONS: frozenset[str] = frozenset({"not_checked"})

#: До какой длины текст интерактивного элемента считается его собственной подписью, а не текстом потомков.
MAX_OWN_TEXT_LENGTH: int = 80

#: Подпись элемента точно равна поисковому запросу.
QUALITY_EXACT: int = 4
#: Запрос попал в собственную подпись элемента (текст, id, data-testid, aria-label и прочие).
QUALITY_OWN: int = 3
#: Запрос попал в атрибут элемента: class, type, href, role, data-* и любой другой.
QUALITY_ATTR: int = 2
#: Запрос нашёлся только в тексте потомков контейнера — показывается по ключу ``--wide``.
QUALITY_DESCENDANT: int = 1

#: Как называется уровень совпадения в текстовом отчёте и в JSON.
QUALITY_MARKS: dict[int, str] = {
    QUALITY_EXACT: "точно",
    QUALITY_OWN: "подпись",
    QUALITY_ATTR: "атрибут",
    QUALITY_DESCENDANT: "текст потомков",
}

#: Атрибуты, которые печатаются в текстовом выводе даже без ``-v`` (плюс все data-*).
NOTABLE_ATTRS: frozenset[str] = frozenset({"type", "role", "href", "class", "name", "value", "for"})

#: До скольких символов обрезается значение атрибута в однострочном выводе.
MAX_ATTR_VALUE_LENGTH: int = 120

#: Теги полей ввода — отдельный раздел инвентаря.
FIELD_TAGS: frozenset[str] = frozenset({"input", "textarea", "select"})

#: Теги заголовков — отдельный раздел инвентаря.
HEADING_TAGS: frozenset[str] = frozenset({"h1", "h2", "h3", "h4", "h5"})

#: Сколько классов-владельцев показывать под файлом в секции «СТРАНИЦЫ, КОТОРЫХ НЕТ В ДАМПЕ».
MAX_CLASSES_IN_SECTION: int = 5


def _resolve_dump_path(raw: str | None, dumps_dir: Path = DEFAULT_DUMPS_DIR) -> Path:
    """Разворачивает путь к дампу: как есть, относительно корня или относительно каталога дампов.

    :param raw: Путь или имя файла из аргументов командной строки; None — искать единственный дамп.
    :param dumps_dir: Каталог с дампами.
    :return: Существующий путь к файлу дампа.
    :raises FileNotFoundError: Если файл не найден или в каталоге дампов не ровно один файл.
    """
    if raw is None:
        candidates = sorted(
            item for item in dumps_dir.glob("*") if item.is_file() and item.name not in DUMPS_SERVICE_NAMES
        )
        if len(candidates) == 1:
            return candidates[0]
        if not candidates:
            raise FileNotFoundError(
                f"Дамп не указан, и в каталоге {dumps_dir} его нет. Положите файл со снимком DOM туда "
                "или передайте путь аргументом."
            )
        names = ", ".join(item.name for item in candidates)
        raise FileNotFoundError(f"Дамп не указан, а в каталоге {dumps_dir} их несколько: {names}. Выберите один.")
    path = Path(raw).expanduser()
    variants = [path] if path.is_absolute() else [Path.cwd() / path, PROJECT_ROOT_PATH / path, dumps_dir / path]
    for variant in variants:
        if variant.is_file():
            return variant.resolve()
    raise FileNotFoundError(f"Файл дампа не найден: {raw}. Искали как есть, от корня проекта и в {dumps_dir}.")


def options_from_args(args: argparse.Namespace) -> InspectionOptions:
    """Собирает параметры проверки из разобранных аргументов командной строки.

    :param args: Аргументы подкоманды ``check``.
    :return: Параметры прогона.
    :raises FileNotFoundError: Если дамп, каталог локаторов или ui_elements.py не найдены.
    """
    dump_path = _resolve_dump_path(args.dump)
    locators_root = Path(args.locators).resolve() if args.locators else DEFAULT_LOCATORS_ROOT
    ui_elements_path = Path(args.ui_elements).resolve() if args.ui_elements else DEFAULT_UI_ELEMENTS_PATH
    if not locators_root.is_dir():
        raise FileNotFoundError(f"Каталог локаторов не найден: {locators_root}")
    if not ui_elements_path.is_file():
        raise FileNotFoundError(f"Файл с обёртками не найден: {ui_elements_path}")
    return InspectionOptions(
        dump_path=dump_path,
        locators_root=locators_root,
        ui_elements_path=ui_elements_path,
        project_root=PROJECT_ROOT_PATH,
        report_path=Path(args.report).resolve() if args.report else None,
        json_path=Path(args.json).resolve() if args.json else None,
        only_cases=frozenset(args.case or ()),
        only_snapshots=frozenset(args.snapshot or ()),
        owner_coverage_threshold=args.coverage,
        check_lists=args.check_lists,
        max_candidates=args.max_candidates,
        max_elements_per_snapshot=args.max_elements,
        fail_on_problems=not args.no_fail,
        verbose=args.verbose,
    )


def _matches_filters(check: LocatorCheckResult, args: argparse.Namespace) -> bool:
    """Проверяет, проходит ли находка фильтры по классам, файлам, модулям и атрибутам.

    :param check: Результат проверки локатора.
    :param args: Аргументы подкоманды ``check``.
    :return: True, если находку надо показывать.
    """
    locator = check.locator
    if args.locator_class and not any(
        locator.class_name == item or f"{locator.module}.{locator.class_name}" == item for item in args.locator_class
    ):
        return False
    if args.file and not any(
        locator.file == item or locator.file.endswith(item.replace("\\", "/")) for item in args.file
    ):
        return False
    if args.module and not any(locator.module == item or locator.module.startswith(f"{item}.") for item in args.module):
        return False
    if args.attr and locator.attr not in args.attr:
        return False
    return True


def section_of(check: LocatorCheckResult) -> str | None:
    """Определяет раздел отчёта для находки.

    Каждая находка попадает ровно в один раздел: сначала ошибка компиляции, затем сломанный
    локатор, затем расхождение описания с текстом, затем риски strict mode.

    :param check: Результат проверки локатора.
    :return: Ключ раздела либо None, если находку показывать не нужно.
    """
    if check.status is MatchStatus.COMPILE_ERROR:
        return "compile_error"
    if check.status is MatchStatus.NOT_FOUND:
        return "not_found"
    if check.text_mismatch:
        return "text_mismatch"
    if check.status is MatchStatus.MULTIPLE_VISIBLE:
        return "multiple_visible"
    if check.status is MatchStatus.UNIQUE_VISIBLE:
        return "unique_visible"
    if check.status is MatchStatus.NOT_CHECKED:
        return "not_checked"
    return None


def _group_key(check: LocatorCheckResult) -> tuple[str, str, str]:
    """Ключ склейки одинаковых находок: один селектор, объявленный в нескольких классах, — одна строка отчёта.

    :param check: Результат проверки локатора.
    :return: Кортеж (селектор, статус, описание).
    """
    return (check.locator.selector, str(check.status), check.locator.description)


def group_checks(checks: Sequence[LocatorCheckResult]) -> list[list[LocatorCheckResult]]:
    """Склеивает находки с одинаковым селектором, статусом и описанием.

    :param checks: Результаты проверки.
    :return: Список групп; внутри группы порядок объявления сохранён.
    """
    grouped: dict[tuple[str, str, str], list[LocatorCheckResult]] = {}
    for check in checks:
        grouped.setdefault(_group_key(check), []).append(check)
    return list(grouped.values())


def _group_severity(group: Sequence[LocatorCheckResult]) -> Severity:
    """Возвращает самый высокий уровень важности внутри группы.

    :param group: Склеенные находки.
    :return: Уровень важности.
    """
    return min((check.severity for check in group), key=lambda item: SEVERITY_ORDER[item])


def _sort_groups(groups: list[list[LocatorCheckResult]]) -> list[list[LocatorCheckResult]]:
    """Сортирует группы: сначала важность, затем число совпадений, затем адрес объявления.

    :param groups: Группы находок.
    :return: Отсортированный список групп.
    """
    return sorted(
        groups,
        key=lambda group: (
            SEVERITY_ORDER[_group_severity(group)],
            -group[0].max_matches_in_snapshot,
            group[0].locator.file,
            group[0].locator.line,
        ),
    )


def _format_case_line(report: InspectionReport) -> list[str]:
    """Готовит строки сводки по кейсам дампа.

    :param report: Отчёт проверки.
    :return: Строки вида ``case 29: снимков 8, статус note``.
    """
    lines: list[str] = []
    for block in report.dump.blocks:
        case_name = f"case {block.case_no}" if block.case_no is not None else "вне кейсов"
        jira = [note.jira_key for note in block.notes if note.jira_key]
        jira_part = f", jira {', '.join(jira)}" if jira else ""
        lines.append(
            f"    {case_name}: снимков {len(block.snapshots)}, пометок {len(block.notes)}, "
            f"статус {block.status}{jira_part}"
        )
    return lines


def _format_element(element: DomElement) -> str:
    """Однострочное описание найденного элемента DOM.

    :param element: Элемент из индекса снимка.
    :return: Строка вида ``<button> [data-testid=...] 'Создать' скрыт: css:clip-path-inset-100``.
    """
    selector = element.stable_selector or ""
    label = f" '{element.label}'" if element.label else ""
    if element.rendered:
        visibility = "виден"
    else:
        reason = f": {element.hidden_reason}" if element.hidden_reason else ""
        visibility = f"скрыт{reason}"
    return f"<{element.tag}> {selector}{label} — {visibility}".replace("  ", " ")


def _format_snapshot_line(check: LocatorCheckResult, limit: int = 3) -> list[str]:
    """Готовит строки со списком снимков, где селектор нашёлся.

    :param check: Результат проверки локатора.
    :param limit: Сколько снимков показывать подробно.
    :return: Строки отчёта; снимки идут от самого проблемного (больше всего совпадений),
        внутри снимка видимые элементы показываются первыми.
    """
    found = sorted(
        (result for result in check.results if result.match_count),
        key=lambda result: (-result.match_count, -result.rendered_count, result.snapshot_index),
    )
    lines: list[str] = []
    for result in found[:limit]:
        lines.append(f"      {result.address}: совпадений {result.match_count}, видимых {result.rendered_count}")
        for element in sorted(result.elements, key=lambda item: not item.rendered)[:limit]:
            lines.append(f"        {_format_element(element)}")
    if len(found) > limit:
        lines.append(f"      ... и ещё снимков с совпадениями: {len(found) - limit}")
    return lines


def _format_origins(group: Sequence[LocatorCheckResult], limit: int = 5) -> list[str]:
    """Готовит строки с местами объявления локатора.

    :param group: Склеенные находки одного селектора.
    :param limit: Сколько мест объявления показывать.
    :return: Строки отчёта.
    """
    origins = list(dict.fromkeys(check.locator.origin for check in group))
    lines = [f"      {origin}" for origin in origins[:limit]]
    if len(origins) > limit:
        lines.append(f"      ... и ещё мест объявления: {len(origins) - limit}")
    return lines


def _render_group(number: int, group: Sequence[LocatorCheckResult], options: InspectionOptions) -> list[str]:
    """Рендерит одну находку отчёта.

    :param number: Порядковый номер находки в разделе.
    :param group: Склеенные находки одного селектора.
    :param options: Параметры прогона (нужен verbose).
    :return: Строки отчёта.
    """
    head = group[0]
    locator = head.locator
    severity = _group_severity(group)
    wrapper = locator.wrapper or "строка"
    list_mark = ", списочная обёртка" if locator.is_list else ""
    lines = [
        f"  [{number}] {severity.upper():6} {locator.selector}",
        f"      описание: {locator.display_name} (обёртка {wrapper}{list_mark}, тип {locator.kind})",
    ]
    lines.extend(_format_origins(group))
    lines.append(f"      {head.message}")
    if head.compile_error:
        lines.append(f"      ошибка движка: {head.compile_error}")
    if head.text_mismatch:
        observed = ", ".join(f"'{text}'" for text in head.observed_texts[:5]) or "пусто"
        lines.append(f"      текст: ожидали '{head.expected_text}', в DOM {observed}")
    if head.status is MatchStatus.NOT_FOUND:
        coverage = head.owner_coverage or 0.0
        reason = (
            "якорный id/data-testid селектора найден в дампе"
            if head.owner_anchor_found
            else f"покрытие владельца (лучшее из файла и класса) {coverage:.0%} при пороге "
            f"{options.owner_coverage_threshold:.0%}"
        )
        lines.append(f"      страница в дампе есть: {reason}")
    lines.extend(_format_snapshot_line(head, limit=5 if options.verbose else 3))
    if head.candidates:
        lines.append("      кандидаты на замену:")
        for position, candidate in enumerate(head.candidates, start=1):
            lines.append(
                f"        {position}. {candidate.selector} (score {candidate.score:.2f}, "
                f"снимок #{candidate.snapshot_index}) — {candidate.reason}"
            )
            lines.append(f"           {_format_element(candidate.element)}")
    return lines


def pages_not_in_dump(checks: Sequence[LocatorCheckResult]) -> list[dict[str, Any]]:
    """Сводка по локаторам, которые фильтр покрытия признал относящимися к страницам вне дампа.

    Без неё статус ``page_not_in_dump`` виден только числом в шапке, и пользователь не может
    отличить «локатор проверен и цел» от «локатор молча пропущен».

    :param checks: Результаты проверки (уже с применёнными фильтрами отчёта).
    :return: Список записей по файлам-владельцам, в каждой — разбивка по классам.
    """
    by_file: dict[str, dict[str, Any]] = {}
    for check in checks:
        locator = check.locator
        entry = by_file.setdefault(
            locator.file,
            {"file": locator.file, "total": 0, "found": 0, "skipped": 0, "coverage": 0.0, "classes": {}},
        )
        klass = entry["classes"].setdefault(
            locator.class_name,
            {"class": locator.class_name, "total": 0, "found": 0, "skipped": 0, "coverage": 0.0},
        )
        for target in (entry, klass):
            target["total"] += 1
            if check.total_matches:
                target["found"] += 1
            if check.status is MatchStatus.PAGE_NOT_IN_DUMP:
                target["skipped"] += 1
                target["coverage"] = max(target["coverage"], check.owner_coverage or 0.0)
    entries: list[dict[str, Any]] = []
    for entry in by_file.values():
        if not entry["skipped"]:
            continue
        entry["classes"] = sorted(
            (item for item in entry["classes"].values() if item["skipped"]),
            key=lambda item: (-item["skipped"], item["class"]),
        )
        entries.append(entry)
    entries.sort(key=lambda item: (-item["skipped"], item["file"]))
    return entries


def _render_pages_not_in_dump(
    entries: Sequence[dict[str, Any]],
    options: InspectionOptions,
    args: argparse.Namespace,
) -> list[str]:
    """Рендерит справочную секцию «СТРАНИЦЫ, КОТОРЫХ НЕТ В ДАМПЕ».

    :param entries: Результат :func:`pages_not_in_dump`.
    :param options: Параметры прогона (нужен порог покрытия).
    :param args: Аргументы подкоманды ``check`` (нужен --limit).
    :return: Строки отчёта; пустой список, если пропущенных локаторов нет.
    """
    if not entries:
        return []
    skipped_total = sum(entry["skipped"] for entry in entries)
    absent = sum(1 for entry in entries if not entry["found"])
    lines = [
        "",
        "-" * 110,
        f"СТРАНИЦЫ, КОТОРЫХ НЕТ В ДАМПЕ: файлов {len(entries)} (полностью отсутствуют {absent}), "
        f"пропущено локаторов {skipped_total}",
        f"(покрытие владельца ниже порога {options.owner_coverage_threshold:.0%}: локатор НЕ проверялся "
        "и в проблемы не попал. Чтобы проверить их всё равно — ключ --coverage 0)",
        "-" * 110,
    ]
    limit = args.limit or len(entries)
    for entry in entries[:limit]:
        state = (
            "ни один локатор файла в дампе не нашёлся"
            if not entry["found"]
            else f"часть локаторов файла нашлась: {entry['found']} из {entry['total']}"
        )
        lines.append(
            f"  {entry['file']}: пропущено {entry['skipped']} из {entry['total']}, "
            f"лучшее покрытие у пропущенных {entry['coverage']:.0%} — {state}"
        )
        for klass in entry["classes"][:MAX_CLASSES_IN_SECTION]:
            lines.append(
                f"      {klass['class']}: пропущено {klass['skipped']} из {klass['total']}, "
                f"найдено {klass['found']}, лучшее покрытие у пропущенных {klass['coverage']:.0%}"
            )
        if len(entry["classes"]) > MAX_CLASSES_IN_SECTION:
            lines.append(f"      ... и ещё классов: {len(entry['classes']) - MAX_CLASSES_IN_SECTION}")
    if len(entries) > limit:
        lines.append(f"  ... показано {limit} из {len(entries)}; полный список — ключ --limit 0")
    return lines


def render_report(report: InspectionReport, args: argparse.Namespace) -> str:
    """Собирает текстовый отчёт для человека.

    Самое важное сверху: ошибки компиляции, сломанные локаторы, расхождения описания с текстом,
    затем риски strict mode. Каждая находка адресуется как «снимок #N, строки start-end, case M»
    плюс ``file:line класс.атрибут``.

    :param report: Результат проверки.
    :param args: Аргументы подкоманды ``check`` (фильтры и пороги вывода).
    :return: Готовый текст отчёта.
    """
    options = report.options
    lines: list[str] = []
    lines.append("=" * 110)
    lines.append(f"ПРОВЕРКА ЛОКАТОРОВ ПО ДАМПУ DOM: {options.dump_path}")
    lines.append("=" * 110)
    lines.append(
        f"  дамп: строк {report.dump.line_count}, снимков {len(report.dump.snapshots)}, кейсов {len(report.dump.blocks)}"
    )
    lines.extend(_format_case_line(report))
    lines.append(
        f"  локаторы: собрано {report.locators_total}, уникальных селекторов {report.selectors_total}, "
        f"проверено снимков {len(list(iter_snapshots(report.dump, options.only_cases, options.only_snapshots)))}"
    )
    counters = ", ".join(
        f"{status}={count}" for status, count in sorted(report.status_counters.items(), key=lambda item: str(item[0]))
    )
    lines.append(f"  статусы: {counters}")
    lines.append(f"  время: {report.duration_seconds:.1f} с")
    if report.warnings:
        lines.append("")
        lines.append(f"ПРЕДУПРЕЖДЕНИЯ ({len(report.warnings)}):")
        for warning in report.warnings[: args.limit or len(report.warnings)]:
            lines.append(f"  - {warning}")
        if args.limit and len(report.warnings) > args.limit:
            lines.append(f"  ... и ещё: {len(report.warnings) - args.limit}")

    selected = [check for check in report.checks if _matches_filters(check, args)]
    filtered_out = len(report.checks) - len(selected)
    if filtered_out:
        lines.append("")
        lines.append(f"ФИЛЬТР: показываются {len(selected)} локаторов из {len(report.checks)}")
    min_severity = SEVERITY_ORDER[Severity(args.min_severity)]
    shown_total = 0
    for key, title, hint in SECTIONS:
        if args.only_problems and key in INFO_SECTIONS:
            continue
        section_checks = [check for check in selected if section_of(check) == key]
        if not section_checks:
            continue
        groups = _sort_groups(group_checks(section_checks))
        groups = [group for group in groups if SEVERITY_ORDER[_group_severity(group)] <= min_severity]
        if not groups:
            continue
        limit = args.limit or len(groups)
        lines.append("")
        lines.append("-" * 110)
        lines.append(f"{title}: находок {len(groups)}, объявлений {len(section_checks)}")
        lines.append(f"({hint})")
        lines.append("-" * 110)
        for number, group in enumerate(groups[:limit], start=1):
            lines.extend(_render_group(number, group, options))
            shown_total += 1
        if len(groups) > limit:
            lines.append(f"  ... показано {limit} из {len(groups)}; полный список — ключ --limit 0")

    if not args.only_problems:
        lines.extend(_render_pages_not_in_dump(pages_not_in_dump(selected), options, args))

    relative = [
        (check.locator, secondary)
        for check in selected
        for secondary in check.locator.secondary_selectors
        if secondary.relative
    ]
    if relative and not args.only_problems:
        lines.append("")
        lines.append("-" * 110)
        lines.append(f"ВТОРИЧНЫЕ ОТНОСИТЕЛЬНЫЕ СЕЛЕКТОРЫ: {len(relative)} (не проверяются автоматически)")
        lines.append("-" * 110)
        for locator, secondary in relative[: args.limit or len(relative)]:
            lines.append(f"  {locator.origin}: {secondary.role} -> {secondary.selector}")
        if args.limit and len(relative) > args.limit:
            lines.append(f"  ... и ещё: {len(relative) - args.limit}")

    problems = [check for check in selected if check.is_problem]
    lines.append("")
    lines.append("=" * 110)
    lines.append(f"ИТОГО: проблемных объявлений {len(problems)}, показано находок {shown_total}")
    if problems:
        by_severity = {severity: 0 for severity in SEVERITY_ORDER}
        for check in problems:
            by_severity[check.severity] += 1
        lines.append("  " + ", ".join(f"{severity}={count}" for severity, count in by_severity.items()))
    lines.append("=" * 110)
    return "\n".join(lines)


def report_to_dict(report: InspectionReport, args: argparse.Namespace) -> dict[str, Any]:
    """Готовит машинный отчёт: то же самое, но без гигабайт HTML внутри.

    :param report: Результат проверки.
    :param args: Аргументы подкоманды ``check``.
    :return: Словарь, пригодный для :func:`json.dumps`.
    """
    selected = [check for check in report.checks if _matches_filters(check, args)]
    problems: list[dict[str, Any]] = []
    for check in selected:
        section = section_of(check)
        if section is None or (args.only_problems and not check.is_problem):
            continue
        problems.append(
            {
                "section": section,
                "status": str(check.status),
                "severity": str(check.severity),
                "selector": check.locator.selector,
                "kind": str(check.locator.kind),
                "description": check.locator.description,
                "wrapper": check.locator.wrapper,
                "is_list": check.locator.is_list,
                "origin": {
                    "file": check.locator.file,
                    "line": check.locator.line,
                    "class": check.locator.class_name,
                    "attr": check.locator.attr,
                },
                "total_matches": check.total_matches,
                "max_matches_in_snapshot": check.max_matches_in_snapshot,
                "snapshots_with_matches": check.snapshots_with_matches,
                "owner_coverage": check.owner_coverage,
                "owner_anchor_found": check.owner_anchor_found,
                "expected_text": check.expected_text,
                "observed_texts": check.observed_texts,
                "text_mismatch": check.text_mismatch,
                "compile_error": check.compile_error,
                "message": check.message,
                "snapshots": [
                    {
                        "index": result.snapshot_index,
                        "case_no": result.case_no,
                        "start_line": result.start_line,
                        "end_line": result.end_line,
                        "match_count": result.match_count,
                        "rendered_count": result.rendered_count,
                        "pw_visible_count": result.pw_visible_count,
                    }
                    for result in check.results
                    if result.match_count
                ],
                "candidates": [
                    {
                        "selector": candidate.selector,
                        "score": candidate.score,
                        "reason": candidate.reason,
                        "snapshot_index": candidate.snapshot_index,
                        "tag": candidate.element.tag,
                        "text": candidate.element.label,
                    }
                    for candidate in check.candidates
                ],
            }
        )
    return {
        "dump": {
            "path": str(report.dump.path),
            "line_count": report.dump.line_count,
            "snapshots": len(report.dump.snapshots),
            "cases": [
                {
                    "case_no": block.case_no,
                    "snapshots": len(block.snapshots),
                    "status": str(block.status),
                    "notes": [note.text for note in block.notes],
                }
                for block in report.dump.blocks
            ],
        },
        "locators_total": report.locators_total,
        "selectors_total": report.selectors_total,
        "duration_seconds": round(report.duration_seconds, 3),
        "status_counters": {str(status): count for status, count in report.status_counters.items()},
        "warnings": report.warnings,
        "pages_not_in_dump": pages_not_in_dump(selected),
        "pages_not_in_dump_total": sum(1 for check in selected if check.status is MatchStatus.PAGE_NOT_IN_DUMP),
        "problems_total": sum(1 for check in selected if check.is_problem),
        "problems": problems,
        "exit_code": report.exit_code,
    }


def write_report(report: InspectionReport, text: str, payload: dict[str, Any]) -> None:
    """Пишет текстовый отчёт и машинный JSON, если пути заданы.

    :param report: Результат проверки (нужны пути из options).
    :param text: Готовый текстовый отчёт.
    :param payload: Машинный отчёт.
    :return: Ничего.
    """
    options = report.options
    if options.report_path is not None:
        options.report_path.parent.mkdir(parents=True, exist_ok=True)
        options.report_path.write_text(text, encoding="utf-8")
        print(f"Текстовый отчёт записан: {options.report_path}")
    if options.json_path is not None:
        options.json_path.parent.mkdir(parents=True, exist_ok=True)
        options.json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"JSON-отчёт записан: {options.json_path}")


def run_check(args: argparse.Namespace) -> int:
    """Выполняет подкоманду ``check``.

    :param args: Аргументы подкоманды.
    :return: Код возврата процесса.
    """
    options = options_from_args(args)
    report = check_dump(options)
    payload = report_to_dict(report, args)
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        text = render_report(report, args)
    else:
        text = render_report(report, args)
        print(text)
    write_report(report, text, payload)
    return report.exit_code


def _selected_snapshots(dump_path: Path, args: argparse.Namespace) -> tuple[list[Snapshot], list[str]]:
    """Отбирает снимки дампа по фильтрам подкоманды ``inspect``.

    :param dump_path: Путь к дампу.
    :param args: Аргументы подкоманды.
    :return: Кортеж (снимки, предупреждения парсера).
    """
    document, warnings = parse_dump_with_warnings(dump_path)
    snapshots = list(iter_snapshots(document, frozenset(args.case or ()), frozenset(args.snapshot or ())))
    return snapshots, warnings


def _own_fields(element: DomElement, label: str) -> list[str]:
    """Собственные подписи элемента: то, что принадлежит именно ему, а не поддереву.

    Вёрстку (class, type, href, role, data-*) сюда класть нельзя — иначе поиск по слову
    «создать» начнёт цеплять каждый ``ant-btn-create``. Атрибуты ищет отдельная :func:`_attr_hits`,
    и её попадания идут в отчёт своим уровнем качества «атрибут».

    :param element: Элемент индекса.
    :param label: Подпись поля из ``<label>``, если есть.
    :return: Список непустых значений в нижнем регистре.
    """
    parts = [
        element.own_text,
        element.element_id or "",
        element.test_id or "",
        element.name or "",
        element.aria_label or "",
        element.title or "",
        element.placeholder or "",
        element.value or "",
        label,
    ]
    return [part.casefold() for part in parts if part]


def _shorten(value: str, limit: int = MAX_ATTR_VALUE_LENGTH) -> str:
    """Схлопывает пробелы и обрезает длинное значение атрибута до читаемой длины.

    :param value: Значение атрибута.
    :param limit: Предельная длина.
    :return: Значение, пригодное для однострочного вывода.
    """
    collapsed = " ".join(value.split())
    return collapsed if len(collapsed) <= limit else f"{collapsed[: limit - 1]}…"


def _attr_hits(element: DomElement, wanted: str) -> list[str]:
    """Атрибуты элемента, в имя или значение которых попала искомая подстрока.

    Именно эта функция закрывает поиск по class, type, href, role и любым data-*:
    в :func:`_own_fields` они не входят, а искать по ним надо.

    :param element: Элемент индекса.
    :param wanted: Искомая подстрока в нижнем регистре.
    :return: Список строк вида ``type='submit'`` в порядке объявления атрибутов.
    """
    hits: list[str] = []
    for name, value in element.attrs.items():
        if wanted in name.casefold() or wanted in value.casefold():
            hits.append(f"{name}='{_shorten(value)}'" if value else name)
    return hits


def _format_attrs(element: DomElement, verbose: bool) -> str:
    """Строка с атрибутами элемента для текстового вывода.

    :param element: Элемент индекса.
    :param verbose: True — печатать все атрибуты, False — только значимые из :data:`NOTABLE_ATTRS`.
    :return: Строка вида ``type='submit' class='ant-btn ant-btn-primary'``; пустая, если печатать нечего.
    """
    items = [
        (name, value)
        for name, value in element.attrs.items()
        if verbose or (name in NOTABLE_ATTRS or name.startswith("data-"))
    ]
    return " ".join(f"{name}='{_shorten(value)}'" if value else name for name, value in items)


def match_quality(element: DomElement, label: str, wanted: str) -> int:
    """Оценивает, насколько элемент отвечает поисковому запросу.

    :param element: Элемент индекса.
    :param label: Подпись поля из ``<label>``, если есть.
    :param wanted: Искомая подстрока в нижнем регистре.
    :return: :data:`QUALITY_EXACT` — подпись элемента точно равна запросу; :data:`QUALITY_OWN` —
        запрос внутри подписи самого элемента (текст кнопки часто лежит во вложенном ``<span>``,
        поэтому короткий текст поддерева тоже считается своим); :data:`QUALITY_ATTR` — запрос попал
        в атрибут (class, type, href, role, data-*); :data:`QUALITY_DESCENDANT` — запрос только
        в тексте потомков у контейнера; 0 — не совпало.
    """
    own = _own_fields(element, label)
    text = element.text.casefold()
    if text == wanted or any(part == wanted for part in own):
        return QUALITY_EXACT
    if any(wanted in part for part in own):
        return QUALITY_OWN
    if wanted in text and element.is_interactive and len(text) <= MAX_OWN_TEXT_LENGTH:
        return QUALITY_OWN
    if _attr_hits(element, wanted):
        return QUALITY_ATTR
    if wanted in text:
        return QUALITY_DESCENDANT
    return 0


def _inventory_groups(parsed: ParsedSnapshot) -> list[tuple[str, list[DomElement]]]:
    """Разбивает элементы снимка на разделы инвентаря.

    :param parsed: Разобранный снимок.
    :return: Список пар «заголовок раздела, элементы»; пустые разделы не возвращаются.
    """
    elements = parsed.index.elements
    groups = [
        ("интерактивных элементов с подписью", [item for item in elements if item.is_interactive and item.label]),
        ("поля ввода", [item for item in elements if item.tag in FIELD_TAGS]),
        (
            "заголовки и шапки модалок",
            [item for item in elements if item.tag in HEADING_TAGS or "modal-title" in item.attrs.get("class", "")],
        ),
    ]
    return [(title, items) for title, items in groups if items]


def _inventory_lines(parsed: ParsedSnapshot, args: argparse.Namespace) -> tuple[list[str], list[DomElement]]:
    """Готовит инвентарь одного снимка: кнопки, поля, заголовки, data-testid.

    :param parsed: Разобранный снимок.
    :param args: Аргументы подкоманды ``inspect``.
    :return: Пара «строки отчёта, показанные элементы» — второй список идёт один в один в ``--json``.
    """
    index = parsed.index
    limit = args.limit or len(index.elements)
    lines: list[str] = []
    shown: list[DomElement] = []
    for title, items in _inventory_groups(parsed):
        lines.append(f"  {title}: {len(items)}")
        for element in items[:limit]:
            label = parsed.labels.get(element.dom_path, "")
            label_part = f" подпись '{label}'" if label and element.tag in FIELD_TAGS else ""
            lines.append(f"    {_format_element(element)}{label_part}")
            attrs = _format_attrs(element, args.verbose)
            if args.verbose and attrs:
                lines.append(f"      атрибуты: {attrs}")
            if element not in shown:
                shown.append(element)
        if len(items) > limit:
            lines.append(f"    ... и ещё: {len(items) - limit}")
    lines.append(f"  значений data-testid: {len(index.by_test_id)}, значений id: {len(index.by_id)}")
    return lines, shown


def _search_hits(
    parsed: ParsedSnapshot, needle: str, args: argparse.Namespace
) -> tuple[list[tuple[int, DomElement]], int]:
    """Отбирает элементы снимка, отвечающие поисковому запросу.

    :param parsed: Разобранный снимок.
    :param needle: Искомая подстрока.
    :param args: Аргументы подкоманды ``inspect``.
    :return: Пара «список (качество, элемент) по убыванию качества, число отброшенных контейнеров».
    """
    wanted = needle.casefold()
    scored = [
        (match_quality(element, parsed.labels.get(element.dom_path, ""), wanted), position, element)
        for position, element in enumerate(parsed.index.elements)
    ]
    scored = [item for item in scored if item[0] > 0]
    containers = sum(1 for quality, _, _ in scored if quality == QUALITY_DESCENDANT)
    if not args.wide:
        scored = [item for item in scored if item[0] > QUALITY_DESCENDANT]
    scored.sort(key=lambda item: (-item[0], item[1]))
    return [(quality, element) for quality, _, element in scored], containers


def raw_html_hits(parsed: ParsedSnapshot, needle: str) -> int:
    """Сколько раз подстрока встречается в сыром HTML снимка.

    Индекс держит только опознаваемые элементы, поэтому «в индексе не нашлось» и «в дампе нет»
    — разные вещи. Сырой счётчик отличает истинный ноль от ложного.

    :param parsed: Разобранный снимок.
    :param needle: Искомая подстрока.
    :return: Число вхождений без учёта регистра.
    """
    return parsed.snapshot.html.casefold().count(needle.casefold())


def _search_lines(
    parsed: ParsedSnapshot,
    needle: str,
    args: argparse.Namespace,
    hits: Sequence[tuple[int, DomElement]],
    containers: int,
) -> list[str]:
    """Рендерит найденные элементы снимка.

    :param parsed: Разобранный снимок.
    :param needle: Искомая подстрока.
    :param args: Аргументы подкоманды ``inspect``.
    :param hits: Результат :func:`_search_hits`.
    :param containers: Число контейнеров, отброшенных без ``--wide``.
    :return: Строки отчёта; пустой список, если ничего не нашлось.
    """
    if not hits:
        return []
    wanted = needle.casefold()
    raw_total = raw_html_hits(parsed, needle)
    limit = args.limit or len(hits)
    lines = [f"  совпадений по '{needle}': {len(hits)}"]
    if raw_total > len(hits):
        lines.append(
            f"  (в сыром HTML снимка подстрока встречается {raw_total} раз; в индекс попадают только "
            "опознаваемые элементы — обычные div/span без id, текста и интерактивности в него не идут)"
        )
    if containers and not args.wide:
        lines.append(f"  (плюс {containers} контейнеров, где подстрока только в тексте потомков — ключ --wide)")
    for quality, element in hits[:limit]:
        lines.append(f"    [{QUALITY_MARKS[quality]}] {_format_element(element)}")
        matched = ", ".join(_attr_hits(element, wanted))
        if matched and (quality == QUALITY_ATTR or args.verbose):
            lines.append(f"      совпало в атрибутах: {matched}")
        if args.verbose:
            attrs = _format_attrs(element, verbose=True)
            if attrs:
                lines.append(f"      атрибуты: {attrs}")
            lines.append(f"      путь: {element.dom_path}")
    if len(hits) > limit:
        lines.append(f"    ... и ещё: {len(hits) - limit}")
    return lines


def _element_payload(element: DomElement, parsed: ParsedSnapshot, quality: int | None = None) -> dict[str, Any]:
    """Машинное описание элемента снимка со всеми его атрибутами.

    :param element: Элемент индекса.
    :param parsed: Разобранный снимок (нужен для подписи из ``<label>``).
    :param quality: Уровень совпадения, если элемент пришёл из поиска.
    :return: Словарь, пригодный для :func:`json.dumps`.
    """
    payload: dict[str, Any] = {
        "tag": element.tag,
        "selector": element.stable_selector,
        "text": element.label,
        "own_text": element.own_text,
        "id": element.element_id,
        "test_id": element.test_id,
        "role": element.role,
        "name": element.name,
        "aria_label": element.aria_label,
        "title": element.title,
        "placeholder": element.placeholder,
        "value": element.value,
        "field_label": parsed.labels.get(element.dom_path) or None,
        "is_interactive": element.is_interactive,
        "rendered": element.rendered,
        "pw_visible": element.pw_visible,
        "hidden_reason": element.hidden_reason,
        "attrs": dict(element.attrs),
        "dom_path": element.dom_path,
    }
    if quality is not None:
        payload["match"] = QUALITY_MARKS[quality]
    return payload


def _search_summary(dump_path: Path, needle: str, raw_by_snapshot: Mapping[str, int]) -> list[str]:
    """Готовит честный итог поиска, когда в индексе не нашлось ничего.

    :param dump_path: Путь к дампу (для подсказки про grep).
    :param needle: Искомая подстрока.
    :param raw_by_snapshot: Сколько раз подстрока встретилась в сыром HTML каждого снимка.
    :return: Строки итога.
    """
    raw_total = sum(raw_by_snapshot.values())
    lines = [
        f"  по подстроке '{needle}' среди проиндексированных элементов ничего не найдено",
        "  поиск покрывает: текст элемента и его потомков, id, data-testid, name, aria-label, title, "
        "placeholder, value, подпись из <label> и ВСЕ атрибуты (class, type, href, role, data-*),",
        "  но только у опознаваемых элементов — обычные div/span без id, без текста и без "
        "интерактивности в индекс снимка не попадают",
    ]
    if not raw_total:
        lines.append("  в сыром HTML снимков подстроки нет ни разу — это настоящий ноль, такой строки в дампе нет")
        return lines
    non_empty = [(address, count) for address, count in raw_by_snapshot.items() if count]
    listed = ", ".join(f"{address} — {count}" for address, count in non_empty[:5])
    if len(non_empty) > 5:
        listed = f"{listed} и ещё снимков: {len(non_empty) - 5}"
    lines.append(f"  НО в сыром HTML снимков подстрока встречается {raw_total} раз: {listed}")
    lines.append("  то есть это ложный ноль: элементы с ней есть, но в индекс не попали. Проверьте грепом:")
    lines.append(f'    grep -o -F "{needle}" "{dump_path}" | wc -l')
    return lines


def run_inspect(args: argparse.Namespace) -> int:
    """Выполняет подкоманду ``inspect``: показывает, что вообще есть на странице.

    :param args: Аргументы подкоманды.
    :return: Код возврата процесса.
    """
    dump_path = _resolve_dump_path(args.dump)
    snapshots, warnings = _selected_snapshots(dump_path, args)
    print(f"ИНВЕНТАРЬ ДАМПА: {dump_path}")
    for warning in warnings:
        print(f"  предупреждение: {warning}")
    if not snapshots:
        print("  снимков по заданным фильтрам не найдено")
        return 1
    payload: list[dict[str, Any]] = []
    raw_by_snapshot: dict[str, int] = {}
    total_found = 0
    for snapshot in snapshots:
        parsed = parse_snapshot(snapshot)
        shown: list[dict[str, Any]] = []
        if args.search:
            hits, containers = _search_hits(parsed, args.search, args)
            raw_by_snapshot[snapshot.address] = raw_html_hits(parsed, args.search)
            lines = _search_lines(parsed, args.search, args, hits, containers)
            if not lines:
                continue
            total_found += 1
            limit = args.limit or len(hits)
            shown = [_element_payload(element, parsed, quality) for quality, element in hits[:limit]]
        else:
            lines, elements = _inventory_lines(parsed, args)
            shown = [_element_payload(element, parsed) for element in elements]
        print("")
        print(f"{snapshot.address}: элементов в индексе {len(parsed.index.elements)} из {parsed.index.element_count}")
        for line in lines:
            print(line)
        if args.duplicates:
            duplicates = duplicate_test_ids(parsed.index)
            if duplicates:
                print(f"  повторяющиеся data-testid: {len(duplicates)}")
                for test_id, count in list(duplicates.items())[: args.limit or len(duplicates)]:
                    print(f"    {test_id} x{count}")
        if args.json:
            entry: dict[str, Any] = {
                "snapshot": snapshot.index,
                "case_no": snapshot.case_no,
                "start_line": snapshot.start_line,
                "end_line": snapshot.end_line,
                "indexed_elements": len(parsed.index.elements),
                "element_count": parsed.index.element_count,
                "search": args.search,
                "elements": shown,
            }
            if args.search:
                entry["raw_html_hits"] = raw_by_snapshot[snapshot.address]
            payload.append(entry)
    if args.search and not total_found:
        print("")
        for line in _search_summary(dump_path, args.search, raw_by_snapshot):
            print(line)
    if args.json:
        json_path = Path(args.json).resolve()
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"JSON записан: {json_path}")
    return 0


def run_api(args: argparse.Namespace) -> int:
    """Выполняет подкоманду ``api``: разбор дампа сети devtools.

    Импорт :mod:`scripts.dom_inspector.api_parser` ленивый — из ветки ``check`` он не грузится.

    :param args: Аргументы подкоманды.
    :return: Код возврата процесса.
    """
    from scripts.dom_inspector.api_parser import format_requests, parse_curl_dump

    dump_path = _resolve_dump_path(args.dump)
    dump = parse_curl_dump(dump_path)
    print(format_requests(dump, verbose=args.verbose))
    if args.json:
        json_path = Path(args.json).resolve()
        json_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "path": str(dump.path),
            "requests": [
                {
                    "index": request.index,
                    "method": request.method,
                    "url": request.url,
                    "host": request.host,
                    "path": request.path,
                    "query": request.query,
                    "headers": request.headers,
                    "content_type": request.content_type,
                    "body_json": request.body_json,
                    "body_raw": None if request.body_json is not None else request.body_raw,
                    "source_line": request.source_line,
                }
                for request in dump.requests
            ],
            "noise_total": len(dump.noise),
            "failed": dump.failed,
        }
        json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
        print(f"JSON записан: {json_path}")
    return 1 if dump.failed else 0


def _add_dump_argument(parser: argparse.ArgumentParser, help_text: str) -> None:
    """Добавляет общий позиционный аргумент с путём к дампу.

    :param parser: Парсер подкоманды.
    :param help_text: Текст подсказки.
    :return: Ничего.
    """
    parser.add_argument("dump", nargs="?", default=None, help=help_text)


def build_parser() -> argparse.ArgumentParser:
    """Создаёт парсер аргументов со всеми подкомандами.

    Парсер собирается внутри функции, а не на уровне модуля, чтобы модуль можно было
    импортировать в selfcheck без разбора ``sys.argv``.

    :return: Готовый парсер.
    """
    parser = argparse.ArgumentParser(
        prog="python -m scripts.dom_inspector.cli",
        description=(
            "Проверка локаторов репозитория по снимку DOM со стенда: что не находится вообще, "
            "что находится больше одного раза и чем это можно заменить."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True, metavar="КОМАНДА")

    check = subparsers.add_parser(
        "check",
        aliases=["html"],
        help="проверить локаторы репозитория по дампу DOM",
        description=(
            "Разбирает дамп DOM на снимки, статически собирает локаторы из pages/locators и гоняет "
            "их по каждому снимку. В отчёте: сломанные локаторы, расхождения описания с текстом "
            "элемента, дубли (риск strict mode) и кандидаты на замену."
        ),
    )
    _add_dump_argument(
        check,
        "путь к дампу DOM; можно указать только имя файла из scripts/dom_inspector/dumps. "
        "Если не указан и в каталоге дампов ровно один файл — берётся он",
    )
    check.add_argument("--locators", default=None, help="каталог с локаторами (по умолчанию pages/locators)")
    check.add_argument("--ui-elements", default=None, help="путь к pages/ui_elements.py с классами-обёртками")
    check.add_argument(
        "--class",
        dest="locator_class",
        action="append",
        default=[],
        metavar="ИМЯ",
        help="показывать только локаторы этого класса (можно повторять)",
    )
    check.add_argument(
        "--file",
        action="append",
        default=[],
        metavar="ПУТЬ",
        help="показывать только локаторы из этого файла, достаточно окончания пути (можно повторять)",
    )
    check.add_argument("--module", action="append", default=[], metavar="МОДУЛЬ", help="фильтр по точечному пути модуля")
    check.add_argument("--attr", action="append", default=[], metavar="ИМЯ", help="фильтр по имени атрибута локатора")
    check.add_argument("--case", action="append", type=int, default=[], metavar="N", help="проверять только этот кейс")
    check.add_argument(
        "--snapshot", action="append", type=int, default=[], metavar="N", help="проверять только этот снимок"
    )
    check.add_argument(
        "--min-severity",
        choices=[str(item) for item in SEVERITY_ORDER],
        default=str(Severity.INFO),
        help="порог вывода: показывать находки не ниже этого уровня важности",
    )
    check.add_argument(
        "--limit", type=int, default=20, metavar="N", help="сколько находок показывать в каждом разделе; 0 — все"
    )
    check.add_argument("--only-problems", action="store_true", help="только проблемные разделы, без справочных")
    check.add_argument("--format", choices=("text", "json"), default="text", help="формат вывода в stdout")
    check.add_argument("--report", default=None, metavar="ПУТЬ", help="записать текстовый отчёт в файл")
    check.add_argument("--json", default=None, metavar="ПУТЬ", help="записать машинный отчёт в JSON")
    check.add_argument(
        "--coverage",
        type=float,
        default=DEFAULT_OWNER_COVERAGE_THRESHOLD,
        metavar="ДОЛЯ",
        help="порог фильтра «страница локатора есть в дампе»: доля найденных селекторов владельца "
        "(лучшее из файла и класса); 0 — проверять все локаторы, ничего не отфильтровывая",
    )
    check.add_argument(
        "--check-lists", action="store_true", help="считать дубли у списочных обёрток полноценной проблемой"
    )
    check.add_argument(
        "--max-candidates", type=int, default=5, metavar="N", help="сколько кандидатов на замену предлагать"
    )
    check.add_argument(
        "--max-elements", type=int, default=10, metavar="N", help="сколько найденных элементов хранить на снимок"
    )
    check.add_argument("--no-fail", action="store_true", help="всегда выходить с кодом 0, даже если есть проблемы")
    check.add_argument("-v", "--verbose", action="store_true", help="подробный вывод")

    inspect = subparsers.add_parser(
        "inspect",
        help="показать инвентарь элементов снимка",
        description=(
            "Показывает, что вообще есть на странице: тексты кнопок и ссылок, поля ввода с подписями, "
            "заголовки модалок, значения id и data-testid. С ключом --search ищет по подстроке в тексте, "
            "подписях и любых атрибутах элемента. Индекс держит только опознаваемые элементы, поэтому "
            "при нулевом результате утилита отдельно считает вхождения подстроки в сыром HTML снимка."
        ),
    )
    _add_dump_argument(inspect, "путь к дампу DOM или имя файла из scripts/dom_inspector/dumps")
    inspect.add_argument(
        "--search",
        default=None,
        metavar="ТЕКСТ",
        help="искать по подстроке в тексте, id, data-testid, подписях и ЛЮБЫХ атрибутах "
        "(class, type, href, role, data-*); если в индексе не нашлось, печатается число "
        "вхождений в сыром HTML — истинный ноль отличается от ложного",
    )
    inspect.add_argument("--case", action="append", type=int, default=[], metavar="N", help="только этот кейс")
    inspect.add_argument("--snapshot", action="append", type=int, default=[], metavar="N", help="только этот снимок")
    inspect.add_argument("--limit", type=int, default=30, metavar="N", help="сколько элементов показывать; 0 — все")
    inspect.add_argument(
        "--wide",
        action="store_true",
        help="показывать и контейнеры, у которых искомая подстрока только в тексте потомков",
    )
    inspect.add_argument("--duplicates", action="store_true", help="показать повторяющиеся data-testid")
    inspect.add_argument("--json", default=None, metavar="ПУТЬ", help="записать инвентарь в JSON")
    inspect.add_argument("-v", "--verbose", action="store_true", help="показывать индексный путь элемента")

    api = subparsers.add_parser(
        "api",
        help="разбор дампа сети devtools (задел под будущие бэкенд-тесты)",
        description=(
            "Разбирает дамп сети devtools «copy all as cURL»: методы, пути, заголовки и тела запросов. "
            "ЭТО ЗАДЕЛ ПОД БУДУЩИЕ БЭКЕНД-ТЕСТЫ: подкоманда check её не вызывает и от неё не зависит, "
            "сейчас команда нужна только чтобы посмотреть, какие вызовы делает фронт."
        ),
    )
    _add_dump_argument(api, "путь к дампу сети или имя файла из scripts/dom_inspector/dumps")
    api.add_argument("--json", default=None, metavar="ПУТЬ", help="записать разобранные запросы в JSON")
    api.add_argument("-v", "--verbose", action="store_true", help="печатать заголовки и тела запросов")

    return parser


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Разбирает аргументы командной строки.

    :param argv: Аргументы; None — взять из ``sys.argv``.
    :return: Пространство имён с разобранными аргументами.
    """
    return build_parser().parse_args(argv)


def _configure_stdout(streams: Iterable[Any] = ()) -> None:
    """Переключает вывод на utf-8: иначе русский текст в консоли Windows превращается в крякозябры.

    :param streams: Потоки для переключения; по умолчанию stdout и stderr.
    :return: Ничего.
    """
    for stream in streams or (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> None:
    """Точка входа утилиты.

    :param argv: Аргументы командной строки; None — взять из ``sys.argv``.
    :return: Ничего.
    :raises SystemExit: Всегда: кодом 1, если найдены проблемы или файл дампа не найден.
    """
    _configure_stdout()
    args = parse_args(argv)
    handlers = {"check": run_check, "html": run_check, "inspect": run_inspect, "api": run_api}
    try:
        code = handlers[args.command](args)
    except FileNotFoundError as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        sys.exit(2)
    sys.exit(code)


if __name__ == "__main__":
    main()
