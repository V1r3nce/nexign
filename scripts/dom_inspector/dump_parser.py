"""Разбор файла-дампа DOM (формат need_html) на снимки, блоки кейсов и пометки автора.

Модуль намеренно не зависит ни от CLI, ни от BeautifulSoup/lxml — только stdlib. Он отвечает
ровно за одно: превратить построчный текстовый дамп в :class:`DumpDocument`.

Формат дампа. Заказчик снимает со стенда ``document.body.outerHTML`` и складывает снимки в один
файл, перемежая их человеческими пометками на русском языке::

    case: 29
    <body>...</body>
    <body>...</body>
    case 30: (Только создание договора вручную)
    <body>...</body>
    Все есть

Ключевая особенность: снимок почти всегда МНОГОСТРОЧНЫЙ. Внутренние переводы строк порождают
многострочное значение атрибута ``style`` у скрытой ``<textarea>`` и текст a11y-подсказок dnd-kit,
поэтому наивное правило «строка не начинается с угловой скобки — значит комментарий» даёт на
реальном дампе 437 ложных комментариев вместо 28 настоящих. Единственно верное правило:
снимок начинается со строки, подходящей под :data:`SNAPSHOT_START_RE`, и заканчивается первой
последующей строкой, чей ``rstrip()`` оканчивается на один из :data:`SNAPSHOT_END_SUFFIXES`;
сканирование продолжается со строки ПОСЛЕ конца снимка, а не после его начала.

Снимки и пометки привязываются к ближайшему маркеру кейса ВЫШЕ них. Снимки, встреченные до
первого маркера (обрезанный дамп), попадают в блок с ``case_no=None`` — падать в этом случае
нельзя. Формат следующих выгрузок может измениться, поэтому парсер никогда не бросает исключение
из-за содержимого файла: он возвращает то, что смог разобрать, и список предупреждений
(см. :func:`parse_dump_with_warnings`).
"""

from __future__ import annotations

import re
from collections.abc import Iterator, Sequence
from pathlib import Path

from scripts.dom_inspector.models import CaseBlock, DumpDocument, Note, NoteStatus, Snapshot

# Начало снимка. Сейчас заказчик копирует только тело страницы (в файле 26 строк "<body>" и
# 10 строк '<body class=""'), но если однажды он скопирует documentElement.outerHTML, начало
# снимка станет "<!DOCTYPE html>" или "<html ...>" — поддерживаем все три варианта сразу.
# Граница слова обязательна: подстрока "<head" в дампе встречается 29 раз, и все 29 — это
# "<header class=...>", а не служебный тег.
SNAPSHOT_START_RE: re.Pattern[str] = re.compile(r"^\s*<(?:!doctype|html|body)\b", re.IGNORECASE)

# Чем оканчивается последняя строка снимка. Проверяется по rstrip(): в файле подстрока "</body>"
# встречается ровно 36 раз и каждый раз в самом конце строки.
SNAPSHOT_END_SUFFIXES: tuple[str, ...] = ("</body>", "</html>")

# Маркер тест-кейса. Покрывает все написания, встреченные в реальном дампе:
# "case: 29", "case 30: (Только создание договора вручную)", "case31:", "case 24:".
# Якорь ^ обязателен и применяется ТОЛЬКО к строкам вне снимков, иначе русская фраза
# "в кейсе номер 4" или текстовый узел внутри разметки породят несуществующий кейс.
CASE_MARKER_RE: re.Pattern[str] = re.compile(r"^\s*case\s*[:\-]?\s*(\d+)\s*[:\-.)]?\s*(.*)$", re.IGNORECASE)

# Ссылка на баг в пометке: "тут баг, так что скипни по причине https://jira.nexign.com/browse/RMBSS-18239".
JIRA_LINK_RE: re.Pattern[str] = re.compile(r"https?://jira\.nexign\.com/browse/([A-Za-z]+-\d+)")

# Маркеры статуса пометки. Сравнение через casefold: в дампе встречаются "Все есть", "все есть"
# и даже "вСЕ ЕСТЬ".
DONE_MARKERS: tuple[str, ...] = ("все есть", "всё есть")
OUTDATED_MARKERS: tuple[str, ...] = ("outdated",)

# Оговорки, отменяющие статус "готово". В дампе есть пометка "тут у тебя все есть кроме" —
# формально она содержит маркер готовности, но по смыслу означает обратное, и кейс 35, к которому
# она относится, действительно не доделан (у него 4 снимка и отдельная инструкция ниже).
DONE_QUALIFIERS: tuple[str, ...] = ("кроме",)

# Символ, которым декодер заменяет битые байты при errors="replace".
REPLACEMENT_CHAR: str = "�"


def read_dump_lines(path: Path) -> list[str]:
    """Читает файл дампа и режет его на значимые строки.

    Файл открывается как ``utf-8-sig`` (BOM снимается, если он есть) с ``errors="replace"``,
    чтобы битые байты не роняли разбор трёхмегабайтного дампа. Используется штатная трансляция
    переводов строк, поэтому будущие выгрузки с CRLF разберутся так же, как текущая с LF.
    Строки режутся по переводу строки, а не через ``splitlines()``: последний дополнительно режет
    по вертикальной табуляции, переводу страницы и юникодным разделителям, которые вполне могут
    встретиться внутри значения атрибута и испортить снимок.

    :param path: Путь к файлу дампа.
    :return: Список значимых строк без завершающего пустого элемента.
    :raises FileNotFoundError: Если файла по указанному пути нет.
    """
    if not path.is_file():
        raise FileNotFoundError(f"Файл дампа не найден: {path}")
    with path.open("r", encoding="utf-8-sig", errors="replace") as stream:
        text = stream.read()
    lines = text.split("\n")
    del text
    if lines and lines[-1] == "":
        lines.pop()
    return lines


def parse_case_marker(line: str) -> tuple[int, str] | None:
    """Распознаёт строку-маркер тест-кейса.

    Применять только к строкам, не попавшим ни в один снимок.

    :param line: Строка файла целиком.
    :return: Кортеж (номер кейса, хвост маркера после номера) либо None, если строка не маркер.
    """
    match = CASE_MARKER_RE.match(line)
    if match is None:
        return None
    try:
        case_no = int(match.group(1))
    except ValueError:
        # Абсурдно длинная последовательность цифр (ограничение int_max_str_digits) — не маркер.
        return None
    return case_no, match.group(2).strip()


def classify_note(text: str) -> tuple[NoteStatus, str | None]:
    """Классифицирует человеческую пометку автора дампа.

    Приоритет статусов: ссылка на баг (кейс пропускается) важнее пометки об устаревании,
    а она важнее пометки о готовности — тот же порядок, что и в :attr:`CaseBlock.status`.
    Пометка о готовности с оговоркой из :data:`DONE_QUALIFIERS` ("все есть кроме") статуса
    готовности НЕ даёт: это свободный комментарий, кейс не доделан.

    :param text: Текст пометки.
    :return: Кортеж (статус пометки, ключ задачи Jira или None).
    """
    jira_match = JIRA_LINK_RE.search(text)
    jira_key = jira_match.group(1).upper() if jira_match is not None else None
    lowered = text.casefold()
    if jira_key is not None:
        return NoteStatus.SKIP, jira_key
    if any(marker.casefold() in lowered for marker in OUTDATED_MARKERS):
        return NoteStatus.OUTDATED, None
    has_done_marker = any(marker.casefold() in lowered for marker in DONE_MARKERS)
    has_qualifier = any(qualifier.casefold() in lowered for qualifier in DONE_QUALIFIERS)
    if has_done_marker and not has_qualifier:
        return NoteStatus.DONE, None
    return NoteStatus.NOTE, None


def _is_snapshot_end(line: str) -> bool:
    """Проверяет, что строка закрывает снимок.

    :param line: Строка файла целиком.
    :return: True, если после отбрасывания хвостовых пробелов строка оканчивается закрывающим тегом.
    """
    return line.rstrip().endswith(SNAPSHOT_END_SUFFIXES)


def _is_boundary(line: str) -> bool:
    """Проверяет, что строка заведомо начинает новый блок дампа.

    Используется только как аварийная граница для незакрытого снимка. Маркер считается границей
    лишь тогда, когда в строке нет разметки: иначе текстовый узел вида ``case 5:`` внутри снимка
    разорвал бы вполне корректный документ.

    :param line: Строка файла целиком.
    :return: True, если строка начинает новый снимок или является маркером кейса.
    """
    if SNAPSHOT_START_RE.match(line) is not None:
        return True
    return "<" not in line and parse_case_marker(line) is not None


def _find_snapshot_end(lines: Sequence[str], start: int) -> tuple[int, bool]:
    """Ищет индекс последней строки снимка, начинающегося со строки ``start``.

    Поиск начинается с самой строки-начала: в реальном дампе есть однострочный снимок
    (строка 331, 76 821 символ), и цикл, стартующий с ``start + 1``, проглотил бы его вместе
    со следующим. Если закрывающего тега нет вовсе (дамп оборвался), снимок закрывается перед
    ближайшей строкой, начинающей новый блок, либо на последней строке файла.

    :param lines: Все строки файла.
    :param start: Индекс строки-начала снимка (0-based).
    :return: Кортеж (индекс последней строки снимка, признак усечения).
    """
    for current in range(start, len(lines)):
        if _is_snapshot_end(lines[current]):
            return current, False
        if current > start and _is_boundary(lines[current]):
            return current - 1, True
    return len(lines) - 1, True


def parse_lines(lines: Sequence[str], path: Path) -> tuple[DumpDocument, list[str]]:
    """Разбирает уже прочитанные строки дампа.

    Вынесено отдельно от :func:`parse_dump`, чтобы разбор можно было проверить на синтетической
    фикстуре без обращения к файловой системе.

    :param lines: Значимые строки файла в исходном порядке.
    :param path: Путь к исходному файлу — попадает в :attr:`DumpDocument.path`.
    :return: Кортеж (разобранный документ, список предупреждений).
    """
    warnings: list[str] = []
    document = DumpDocument(path=path, line_count=len(lines))
    orphan_block = CaseBlock(case_no=None)
    blocks: list[CaseBlock] = [orphan_block]
    current = orphan_block
    seen_cases: dict[int, int] = {}
    snapshot_index = 0
    broken_bytes_reported = False
    index = 0

    while index < len(lines):
        line = lines[index]
        if not broken_bytes_reported and REPLACEMENT_CHAR in line:
            warnings.append(f"строка {index + 1}: файл содержит битые байты, они заменены символом подстановки")
            broken_bytes_reported = True

        if SNAPSHOT_START_RE.match(line) is not None:
            end, truncated = _find_snapshot_end(lines, index)
            snapshot_index += 1
            snapshot = Snapshot(
                index=snapshot_index,
                case_no=current.case_no,
                start_line=index + 1,
                end_line=end + 1,
                html="\n".join(lines[index : end + 1]),
                truncated=truncated,
            )
            current.snapshots.append(snapshot)
            document.snapshots.append(snapshot)
            if truncated:
                warnings.append(
                    f"снимок #{snapshot.index} (строки {snapshot.start_line}-{snapshot.end_line}) "
                    "не имеет закрывающего тега и закрыт по аварийному правилу"
                )
            index = end + 1
            continue

        if not line.strip():
            index += 1
            continue

        marker = parse_case_marker(line)
        if marker is not None:
            case_no, inline_note = marker
            if case_no in seen_cases:
                warnings.append(
                    f"строка {index + 1}: номер кейса {case_no} уже встречался в строке {seen_cases[case_no]}"
                )
            seen_cases[case_no] = index + 1
            current = CaseBlock(case_no=case_no, marker_line=index + 1, marker_raw=line, inline_note=inline_note)
            blocks.append(current)
            # Хвост маркера сохраняется в inline_note, но если он несёт статус
            # ("case 22: outdated", ссылка на баг), его надо продублировать в notes,
            # иначе CaseBlock.status этого статуса не увидит.
            inline_status, inline_jira = classify_note(inline_note)
            if inline_note and inline_status is not NoteStatus.NOTE:
                current.notes.append(Note(line=index + 1, text=inline_note, status=inline_status, jira_key=inline_jira))
            index += 1
            continue

        status, jira_key = classify_note(line)
        current.notes.append(
            Note(
                line=index + 1,
                text=line,
                status=status,
                jira_key=jira_key,
                after_snapshot_index=current.snapshots[-1].index if current.snapshots else None,
            )
        )
        if line.lstrip().startswith("<") or _is_snapshot_end(line):
            warnings.append(f"строка {index + 1}: похоже на разметку вне снимка — возможно, формат дампа изменился")
        index += 1

    if orphan_block.snapshots or orphan_block.notes:
        warnings.append(
            f"до первого маркера кейса найдено снимков: {len(orphan_block.snapshots)}, "
            f"пометок: {len(orphan_block.notes)} — они отнесены к кейсу с номером None"
        )
    else:
        blocks.remove(orphan_block)

    document.blocks = blocks
    if not lines:
        warnings.append("файл дампа пуст")
    elif not document.snapshots:
        warnings.append("в дампе не найдено ни одного снимка DOM (ожидалась строка, начинающаяся с <body)")
    if lines and not seen_cases:
        warnings.append("в дампе не найдено ни одного маркера кейса (ожидалась строка вида 'case 29:')")
    return document, warnings


def parse_dump_with_warnings(path: Path) -> tuple[DumpDocument, list[str]]:
    """Разбирает файл дампа и возвращает вместе с результатом список предупреждений.

    Предупреждения — это всё, что выглядит как изменение формата или порча данных: усечённые
    снимки, снимки до первого маркера, повторяющиеся номера кейсов, разметка вне снимка,
    битые байты. Разбор при этом не прерывается.

    :param path: Путь к файлу дампа.
    :return: Кортеж (разобранный документ, список предупреждений).
    :raises FileNotFoundError: Если файла по указанному пути нет.
    """
    return parse_lines(read_dump_lines(path), path)


def parse_dump(path: Path) -> DumpDocument:
    """Разбирает файл дампа DOM на снимки, блоки кейсов и пометки автора.

    Один линейный проход по строкам файла: строка, подходящая под :data:`SNAPSHOT_START_RE`,
    открывает снимок, первая последующая строка с закрывающим тегом его закрывает, всё остальное
    непустое считается человеческой пометкой. И снимки, и пометки привязываются к ближайшему
    маркеру кейса выше.

    Если нужны предупреждения о подозрительных местах файла, используйте
    :func:`parse_dump_with_warnings`.

    :param path: Путь к файлу дампа.
    :return: Разобранный документ.
    :raises FileNotFoundError: Если файла по указанному пути нет.
    """
    return parse_dump_with_warnings(path)[0]


def iter_snapshots(
    document: DumpDocument,
    only_cases: frozenset[int] = frozenset(),
    only_snapshots: frozenset[int] = frozenset(),
) -> Iterator[Snapshot]:
    """Перебирает снимки документа с фильтрацией по номерам кейсов и снимков.

    Фильтры сужают выборку совместно: при обоих заданных множествах снимок должен подойти
    под каждое из них. Пустое множество означает «без ограничения». Снимки вне кейсов
    (``case_no is None``) непустым фильтром по кейсам всегда отбрасываются.

    :param document: Разобранный документ.
    :param only_cases: Номера кейсов, которые нужно оставить; пустое множество — все.
    :param only_snapshots: Сквозные номера снимков, которые нужно оставить; пустое множество — все.
    :return: Итератор по снимкам в порядке их появления в файле.
    """
    for snapshot in document.snapshots:
        if only_cases and snapshot.case_no not in only_cases:
            continue
        if only_snapshots and snapshot.index not in only_snapshots:
            continue
        yield snapshot
