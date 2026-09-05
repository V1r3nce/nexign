"""Разбор дампа сети devtools («Copy all as cURL») в нормализованный список HTTP-запросов.

Заказчик снимает трафик в Chrome DevTools через «Copy all as cURL (cmd)», поэтому файл —
это набор команд ``curl`` в cmd-экранировании: кавычки записаны как ``^"``, каждый служебный
символ предваряется ``^``, перенос строки внутри команды делается завершающим ``^``,
а сами команды разделены символом ``&`` в конце строки.

Модуль снимает экранирование, разбирает команды shlex-токенайзером и отдаёт
:class:`scripts.dom_inspector.models.ApiDump` с тремя списками: полезные запросы, служебный
шум (антивирус, статика) и то, что разобрать не удалось.

Это задел на будущие бэкенд-тесты. Модуль полностью рабочий, но в основном сценарии проверки
локаторов (подкоманда ``html``) не участвует: он не импортирует ни ``element_index``,
ни ``locator_checker``, и сам не должен импортироваться из ветки ``html`` — только лениво,
внутри обработчика подкоманды ``api``.
"""

from __future__ import annotations

import json
import re
import shlex
from collections.abc import Iterable, Sequence
from pathlib import Path
from urllib.parse import SplitResult, parse_qsl, urlsplit

from scripts.dom_inspector.models import ApiDump, ApiRequest

# --------------------------------------------------------------------------------------
# Настраиваемые фильтры шума
# --------------------------------------------------------------------------------------

NOISE_HOST_PATTERNS: tuple[str, ...] = (
    "kaspersky-labs.com",
    "kaspersky.com",
    "kis.v2.scr.kaspersky-labs.com",
    "google-analytics.com",
    "googletagmanager.com",
    "doubleclick.net",
    "yandex.ru/metrika",
    "sentry.io",
    "localhost:0",
)
"""Подстроки хоста (или хоста с путём), по которым запрос считается служебным шумом."""

NOISE_PATH_SUFFIXES: tuple[str, ...] = (
    ".js",
    ".mjs",
    ".cjs",
    ".js.map",
    ".css",
    ".css.map",
    ".map",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".bmp",
    ".svg",
    ".ico",
    ".webp",
    ".avif",
    ".woff",
    ".woff2",
    ".ttf",
    ".otf",
    ".eot",
    ".mp4",
    ".webm",
    ".mp3",
    ".wav",
)
"""Расширения статики: скрипты, стили, шрифты, картинки и медиа."""

NOISE_SCHEMES: tuple[str, ...] = ("data", "blob", "chrome-extension", "about")
"""Схемы URL, которые никогда не являются запросом к бэкенду."""

INTERESTING_PATH_PREFIXES: tuple[str, ...] = ("/openapi/v1/", "/ps/v1/")
"""Префиксы путей проектного API — по ним запрос помечается как профильный."""

SIGNIFICANT_HEADERS: tuple[str, ...] = (
    "content-type",
    "accept",
    "accept-language",
    "authorization",
    "ps-timezone",
    "x-requested-with",
    "referer",
)
"""Заголовки, которые имеет смысл показывать в отчёте (остальные — транспортный шум)."""

DEFAULT_SEGMENT_RULES: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"^\d+$"), "{id}"),
    (
        re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"),
        "{uuid}",
    ),
    (re.compile(r"^[0-9a-fA-F]{16,}$"), "{hash}"),
    (re.compile(r"^\d+(?:[,;]\d+)+$"), "{ids}"),
)
"""Правила нормализации сегмента пути: ``/customers/15751/linkedPersons`` -> ``/customers/{id}/linkedPersons``."""

# --------------------------------------------------------------------------------------
# Служебные регулярки и таблицы опций curl
# --------------------------------------------------------------------------------------

CURL_START_RE: re.Pattern[str] = re.compile(r"^\s*curl(?:\.exe)?(?:\s|$)", re.IGNORECASE)
"""Строка, с которой начинается очередная команда curl."""

TRAILING_SEPARATOR_RE: re.Pattern[str] = re.compile(r"(?<!\^)[&;|]+\s*$")
"""Разделитель команд в конце последней строки (``--insecure &``)."""

_LONG_VALUE_OPTIONS: frozenset[str] = frozenset(
    {
        "--url",
        "--request",
        "--header",
        "--data",
        "--data-raw",
        "--data-ascii",
        "--data-binary",
        "--data-urlencode",
        "--json",
        "--form",
        "--form-string",
        "--cookie",
        "--cookie-jar",
        "--user-agent",
        "--referer",
        "--user",
        "--proxy",
        "--proxy-user",
        "--upload-file",
        "--output",
        "--write-out",
        "--range",
        "--max-time",
        "--connect-timeout",
        "--retry",
        "--max-redirs",
        "--cert",
        "--key",
        "--cacert",
        "--capath",
        "--ciphers",
        "--resolve",
        "--interface",
        "--limit-rate",
        "--dump-header",
        "--oauth2-bearer",
        "--aws-sigv4",
        "--config",
        "--time-cond",
        "--continue-at",
    }
)
"""Длинные опции curl, забирающие следующий токен как значение."""

_SHORT_VALUE_OPTIONS: dict[str, str] = {
    "X": "--request",
    "H": "--header",
    "d": "--data",
    "b": "--cookie",
    "c": "--cookie-jar",
    "A": "--user-agent",
    "e": "--referer",
    "u": "--user",
    "F": "--form",
    "o": "--output",
    "x": "--proxy",
    "T": "--upload-file",
    "E": "--cert",
    "w": "--write-out",
    "r": "--range",
    "m": "--max-time",
    "z": "--time-cond",
    "D": "--dump-header",
    "K": "--config",
    "U": "--proxy-user",
    "C": "--continue-at",
    "Y": "--limit-rate",
}
"""Короткие опции curl, забирающие значение, и их длинные синонимы."""

_DATA_OPTIONS: frozenset[str] = frozenset(
    {"--data", "--data-raw", "--data-ascii", "--data-binary", "--data-urlencode", "--json"}
)
"""Опции, переносящие тело запроса."""

_SHORT_FLAGS_WITH_METHOD: dict[str, str] = {"I": "HEAD", "G": "GET"}
"""Короткие флаги, задающие метод."""

_SCHEME_RE: re.Pattern[str] = re.compile(r"^([a-zA-Z][a-zA-Z0-9+.\-]*):")
"""Схема в начале URL."""

_SCHEMELESS_AUTHORITY_SCHEMES: frozenset[str] = frozenset({"data", "blob", "about", "mailto", "javascript", "tel"})
"""Схемы, которые пишутся без ``//`` и потому неотличимы от ``host:port`` без явного списка."""


def split_url(url: str) -> SplitResult:
    """Разбирает URL, корректно отличая схему без ``//`` от записи ``host:port``.

    ``data:image/png;base64,...`` — это схема ``data``, а ``localhost:8080/x`` — хост с портом,
    хотя обе строки выглядят одинаково («слово, двоеточие, хвост»). Первое разбирается как есть,
    второму достраивается ``http://``, иначе ``urlsplit`` вернёт схему ``localhost``.

    :param url: URL как он записан в команде curl.
    :return: Результат разбора urlsplit.
    """
    if "://" in url:
        return urlsplit(url)
    match = _SCHEME_RE.match(url)
    if match is not None and match.group(1).lower() in _SCHEMELESS_AUTHORITY_SCHEMES:
        return urlsplit(url)
    return urlsplit(f"http://{url}")


# --------------------------------------------------------------------------------------
# Снятие cmd-экранирования
# --------------------------------------------------------------------------------------


def unescape_cmd(text: str) -> str:
    """Снимает cmd-экранирование devtools и склеивает строки, разорванные символом ``^``.

    Разбор посимвольный, а не последовательностью ``str.replace``: только так корректно
    обрабатываются вложенные последовательности вида ``^\\^"`` (``\\"``) и ``^\\^\\^\\^"``
    (``\\\\\\"``), где наивная замена ``^"`` -> ``"`` первым шагом уже испортила бы текст.
    Правило cmd простое: ``^`` отменяет спецсмысл следующего символа, а ``^`` в конце строки
    съедает перевод строки.

    :param text: Текст команды в cmd-экранировании.
    :return: Команда без экранирования, склеенная в одну строку по местам переноса.
    """
    result: list[str] = []
    position = 0
    length = len(text)
    while position < length:
        char = text[position]
        if char != "^":
            result.append(char)
            position += 1
            continue
        position += 1
        if position >= length:
            break
        following = text[position]
        if following == "\r":
            position += 1
            if position < length and text[position] == "\n":
                position += 1
            continue
        if following == "\n":
            position += 1
            continue
        result.append(following)
        position += 1
    return "".join(result)


def _looks_cmd_escaped(command: str) -> bool:
    """Определяет, снят ли с команды cmd-стиль экранирования.

    :param command: Текст команды как он лежит в файле.
    :return: True, если команда записана в cmd-экранировании devtools.
    """
    return '^"' in command or "^&" in command or command.rstrip().endswith("^")


def _join_posix_continuations(command: str) -> str:
    """Склеивает строки bash-варианта дампа, где перенос сделан обратным слешем.

    :param command: Текст команды в posix-экранировании.
    :return: Команда, склеенная в одну строку.
    """
    return re.sub(r"\\\r?\n", " ", command)


def _normalize_command(command: str) -> str:
    """Приводит команду к однострочному виду без экранирования оболочки.

    :param command: Текст команды из файла.
    :return: Готовая к токенизации команда.
    """
    if _looks_cmd_escaped(command):
        return unescape_cmd(command)
    return _join_posix_continuations(command)


# --------------------------------------------------------------------------------------
# Нарезка дампа на команды
# --------------------------------------------------------------------------------------


def _has_continuation(line: str) -> bool:
    """Проверяет, продолжается ли команда на следующей строке.

    Учитывается и cmd-перенос (нечётное число ``^`` в конце), и bash-перенос
    (нечётное число ``\\`` в конце).

    :param line: Строка файла без завершающего перевода строки.
    :return: True, если следующая строка принадлежит той же команде.
    """
    stripped = line.rstrip()
    if not stripped:
        return False
    carets = len(stripped) - len(stripped.rstrip("^"))
    if carets % 2 == 1:
        return True
    slashes = len(stripped) - len(stripped.rstrip("\\"))
    return slashes % 2 == 1


def split_commands(text: str) -> list[tuple[int, str]]:
    """Режет дамп на команды curl.

    Разбор построчный, а не по разделителю ``&``: символ ``&`` встречается и внутри URL
    (там он экранирован как ``^&``), а в хвосте файла заказчик обычно доклеивает
    отформатированные тела ответов — такие строки командами не являются и просто
    пропускаются, ничего не ломая.

    :param text: Содержимое файла дампа целиком.
    :return: Список пар «номер первой строки команды (1-based), текст команды как в файле».
    """
    lines = [line.rstrip("\r") for line in text.split("\n")]
    total = len(lines)
    commands: list[tuple[int, str]] = []
    position = 0
    while position < total:
        if not CURL_START_RE.match(lines[position]):
            position += 1
            continue
        start_line = position + 1
        chunk = [lines[position]]
        last = position
        while True:
            current = lines[last]
            if not _has_continuation(current):
                is_blank_inside_value = last > position and not current.strip() and _has_continuation(lines[last - 1])
                if not is_blank_inside_value:
                    break
            if last + 1 >= total:
                break
            following = lines[last + 1]
            if CURL_START_RE.match(following):
                break
            chunk.append(following)
            last += 1
        commands.append((start_line, "\n".join(chunk)))
        position = last + 1
    return commands


# --------------------------------------------------------------------------------------
# Токенизация
# --------------------------------------------------------------------------------------


def tokenize_command(command: str) -> list[str]:
    """Разбивает однострочную команду на токены по правилам posix-оболочки.

    Внутри двойных кавычек ``\\"`` даёт кавычку, а ``\\\\`` — обратный слеш, поэтому JSON-тело
    восстанавливается без дополнительной обработки. Комментарии отключены: символ ``#``
    встречается в URL и не должен обрезать строку.

    :param command: Команда без экранирования оболочки, в одну строку.
    :return: Список токенов.
    :raises ValueError: Если кавычки в команде не закрыты.
    """
    lexer = shlex.shlex(command, posix=True)
    lexer.whitespace_split = True
    lexer.commenters = ""
    return list(lexer)


# --------------------------------------------------------------------------------------
# Фильтры шума и группировка
# --------------------------------------------------------------------------------------


def is_noise(
    url: str,
    host_patterns: Sequence[str] = NOISE_HOST_PATTERNS,
    path_suffixes: Sequence[str] = NOISE_PATH_SUFFIXES,
) -> tuple[bool, str | None]:
    """Решает, является ли запрос служебным шумом.

    Фильтр настраиваемый: списки хостов и расширений передаются аргументами, значения
    по умолчанию берутся из констант модуля.

    :param url: Полный URL запроса.
    :param host_patterns: Подстроки хостов, считающихся шумом (антивирус, аналитика).
    :param path_suffixes: Расширения статики (скрипты, стили, шрифты, картинки).
    :return: Пара «это шум, причина»; причина None, если запрос полезный.
    """
    parts = split_url(url)
    scheme = parts.scheme.lower()
    if scheme in NOISE_SCHEMES:
        return True, f"схема {scheme}"
    host = parts.netloc.lower()
    lowered_url = url.lower()
    for pattern in host_patterns:
        needle = pattern.lower()
        if needle in host or needle in lowered_url:
            return True, f"служебный домен {pattern}"
    path = parts.path.lower()
    for suffix in path_suffixes:
        if path.endswith(suffix):
            return True, f"статика {suffix}"
    return False, None


def is_interesting_path(path: str, prefixes: Sequence[str] = INTERESTING_PATH_PREFIXES) -> bool:
    """Проверяет, относится ли путь к профильному API проекта.

    :param path: Путь URL без query.
    :param prefixes: Префиксы путей проектного API.
    :return: True, если путь начинается с одного из префиксов.
    """
    return any(path.startswith(prefix) for prefix in prefixes)


def normalize_path(path: str, rules: Sequence[tuple[re.Pattern[str], str]] | None = None) -> str:
    """Заменяет переменные сегменты пути плейсхолдерами.

    ``/openapi/v1/customerManagement/customers/15751/linkedPersons`` превращается в
    ``/openapi/v1/customerManagement/customers/{id}/linkedPersons`` — так в отчёте виден
    API-контур сценария, а не список конкретных идентификаторов.

    :param path: Путь URL без query.
    :param rules: Правила «регулярка сегмента -> плейсхолдер»; None — правила по умолчанию.
    :return: Нормализованный путь.
    """
    active_rules = DEFAULT_SEGMENT_RULES if rules is None else rules
    segments = path.split("/")
    normalized: list[str] = []
    for segment in segments:
        replacement = segment
        for pattern, placeholder in active_rules:
            if pattern.fullmatch(segment):
                replacement = placeholder
                break
        normalized.append(replacement)
    return "/".join(normalized)


def group_by_path(
    requests: Iterable[ApiRequest],
    rules: Sequence[tuple[re.Pattern[str], str]] | None = None,
) -> dict[str, list[ApiRequest]]:
    """Группирует запросы по нормализованному пути.

    Порядок ключей — порядок первого появления пути в дампе, то есть порядок шагов сценария.

    :param requests: Запросы для группировки.
    :param rules: Правила нормализации сегментов; None — правила по умолчанию.
    :return: Словарь «нормализованный путь -> запросы в порядке появления».
    """
    grouped: dict[str, list[ApiRequest]] = {}
    for request in requests:
        key = normalize_path(request.path, rules)
        grouped.setdefault(key, []).append(request)
    return grouped


def significant_headers(request: ApiRequest, names: Sequence[str] = SIGNIFICANT_HEADERS) -> list[tuple[str, str]]:
    """Отбирает заголовки, осмысленные для описания API-вызова.

    :param request: Разобранный запрос.
    :param names: Имена интересующих заголовков в нижнем регистре.
    :return: Список пар «имя, значение» в исходном порядке.
    """
    wanted = {name.casefold() for name in names}
    return [(name, value) for name, value in request.headers if name.casefold() in wanted]


# --------------------------------------------------------------------------------------
# Разбор одной команды
# --------------------------------------------------------------------------------------


def _parse_header(value: str) -> tuple[str, str] | None:
    """Разбирает значение опции ``-H`` на имя и значение заголовка.

    :param value: Строка вида ``Content-Type: application/json``.
    :return: Пара «имя, значение» либо None, если строку разобрать нельзя.
    """
    if ":" not in value:
        if value.endswith(";"):
            return value[:-1].strip(), ""
        return None
    name, _, raw_value = value.partition(":")
    return name.strip(), raw_value.strip()


def _resolve_method(
    explicit: str | None,
    has_body: bool,
    head_flag: bool,
    get_flag: bool,
    upload_flag: bool,
) -> str:
    """Определяет HTTP-метод запроса по опциям curl.

    :param explicit: Значение ``-X`` / ``--request``, если оно было.
    :param has_body: Было ли передано тело.
    :param head_flag: Был ли флаг ``-I`` / ``--head``.
    :param get_flag: Был ли флаг ``-G`` / ``--get``.
    :param upload_flag: Был ли ``-T`` / ``--upload-file``.
    :return: Метод в верхнем регистре.
    """
    if explicit:
        return explicit.upper()
    if head_flag:
        return "HEAD"
    if get_flag:
        return "GET"
    if upload_flag:
        return "PUT"
    if has_body:
        return "POST"
    return "GET"


def _parse_command_detailed(command: str, index: int, source_line: int) -> tuple[ApiRequest | None, str | None]:
    """Разбирает команду curl и возвращает результат вместе с причиной отказа.

    :param command: Текст команды как он лежит в файле.
    :param index: Порядковый номер запроса, начиная с 1.
    :param source_line: Номер строки файла, с которой начинается команда.
    :return: Пара «запрос или None, причина отказа или None».
    """
    normalized = _normalize_command(command)
    stripped = TRAILING_SEPARATOR_RE.sub("", normalized).strip()
    if not stripped:
        return None, "пустая команда"
    try:
        tokens = tokenize_command(stripped)
    except ValueError as error:
        return None, f"не удалось разбить на токены: {error}"
    if not tokens:
        return None, "пустая команда"
    if tokens[0].lower() not in {"curl", "curl.exe"}:
        return None, f"команда начинается не с curl, а с {tokens[0]!r}"

    url: str | None = None
    explicit_method: str | None = None
    headers: list[tuple[str, str]] = []
    data_parts: list[str] = []
    form_parts: list[str] = []
    head_flag = False
    get_flag = False
    upload_flag = False
    extra_positionals: list[str] = []

    position = 1
    total = len(tokens)
    while position < total:
        token = tokens[position]
        name: str | None = None
        value: str | None = None
        if token.startswith("--"):
            option, separator, inline = token.partition("=")
            if option in _LONG_VALUE_OPTIONS:
                name = option
                if separator:
                    value = inline
                else:
                    position += 1
                    value = tokens[position] if position < total else ""
            else:
                name = option
        elif token.startswith("-") and len(token) > 1:
            letter = token[1]
            if letter in _SHORT_VALUE_OPTIONS:
                name = _SHORT_VALUE_OPTIONS[letter]
                if len(token) > 2:
                    value = token[2:]
                else:
                    position += 1
                    value = tokens[position] if position < total else ""
            else:
                for flag_letter in token[1:]:
                    if flag_letter in _SHORT_FLAGS_WITH_METHOD:
                        if _SHORT_FLAGS_WITH_METHOD[flag_letter] == "HEAD":
                            head_flag = True
                        else:
                            get_flag = True
                    elif flag_letter == "T":
                        upload_flag = True
                name = None
        else:
            if url is None:
                url = token
            else:
                extra_positionals.append(token)
            position += 1
            continue

        if name == "--url":
            url = value or url
        elif name == "--request":
            explicit_method = value or explicit_method
        elif name == "--header" and value is not None:
            parsed_header = _parse_header(value)
            if parsed_header is not None:
                headers.append(parsed_header)
        elif name == "--cookie" and value is not None:
            headers.append(("cookie", value))
        elif name == "--user-agent" and value is not None:
            headers.append(("user-agent", value))
        elif name == "--referer" and value is not None:
            headers.append(("referer", value))
        elif name in _DATA_OPTIONS and value is not None:
            data_parts.append(value)
        elif name in {"--form", "--form-string"} and value is not None:
            form_parts.append(value)
        elif name == "--upload-file":
            upload_flag = True
        elif name == "--head":
            head_flag = True
        elif name == "--get":
            get_flag = True
        position += 1

    if url is None:
        return None, "в команде не найден URL"

    body_raw: str | None = None
    if data_parts:
        body_raw = "&".join(data_parts)
    elif form_parts:
        body_raw = "\n".join(form_parts)

    body_json: object | None = None
    if body_raw is not None:
        try:
            body_json = json.loads(body_raw)
        except (ValueError, TypeError):
            body_json = None

    parsed_url = split_url(url)
    content_type: str | None = None
    for header_name, header_value in headers:
        if header_name.casefold() == "content-type":
            content_type = header_value
            break

    noise, noise_reason = is_noise(url)
    request = ApiRequest(
        index=index,
        method=_resolve_method(explicit_method, body_raw is not None, head_flag, get_flag, upload_flag),
        url=url,
        scheme=parsed_url.scheme,
        host=parsed_url.netloc,
        path=parsed_url.path,
        query=list(parse_qsl(parsed_url.query, keep_blank_values=True)),
        headers=headers,
        body_raw=body_raw,
        body_json=body_json,
        content_type=content_type,
        is_noise=noise,
        noise_reason=noise_reason,
        source_line=source_line,
        raw_command=stripped,
    )
    return request, None


def parse_curl_command(command: str, index: int, source_line: int) -> ApiRequest | None:
    """Разбирает одну команду curl в структуру запроса.

    Метод определяется так же, как это делает curl: явный ``-X`` побеждает всё, иначе
    ``--head`` даёт HEAD, ``--get`` — GET, ``--upload-file`` — PUT, наличие тела — POST,
    и только в остальных случаях GET. Тело склеивается из всех опций ``--data*`` и, если
    это валидный JSON, дополнительно кладётся разобранным в ``body_json``.

    :param command: Текст команды как он лежит в файле дампа.
    :param index: Порядковый номер запроса, начиная с 1.
    :param source_line: Номер строки файла, с которой начинается команда (1-based).
    :return: Разобранный запрос либо None, если команду разобрать не удалось.
    """
    request, _ = _parse_command_detailed(command, index, source_line)
    return request


# --------------------------------------------------------------------------------------
# Разбор файла целиком
# --------------------------------------------------------------------------------------


def read_dump_text(path: Path) -> tuple[str, str | None]:
    """Читает файл дампа, не падая на неожиданной кодировке.

    :param path: Путь к файлу дампа.
    :return: Пара «текст файла, предупреждение о кодировке или None».
    """
    raw = path.read_bytes()
    for encoding in ("utf-8-sig", "cp1251"):
        try:
            return raw.decode(encoding), None
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace"), (
        f"{path}: файл не читается ни как utf-8, ни как cp1251, часть символов заменена"
    )


def parse_curl_dump(
    path: Path,
    host_patterns: Sequence[str] = NOISE_HOST_PATTERNS,
    path_suffixes: Sequence[str] = NOISE_PATH_SUFFIXES,
) -> ApiDump:
    """Разбирает файл дампа сети целиком.

    Ни одна некорректная строка не прерывает разбор: всё, что не удалось разобрать,
    попадает в :attr:`ApiDump.failed` с указанием номера строки и причины, а разбор
    продолжается со следующей команды.

    :param path: Путь к файлу дампа devtools.
    :param host_patterns: Подстроки хостов, считающихся шумом.
    :param path_suffixes: Расширения статики, считающейся шумом.
    :return: Разобранный дамп: полезные запросы, шум и неразобранные команды.
    """
    text, encoding_warning = read_dump_text(path)
    dump = ApiDump(path=path)
    if encoding_warning is not None:
        dump.failed.append(encoding_warning)

    for index, (source_line, command) in enumerate(split_commands(text), start=1):
        try:
            request, reason = _parse_command_detailed(command, index, source_line)
        except Exception as error:  # разбор чужого дампа не должен падать никогда
            dump.failed.append(f"строка {source_line}: неожиданная ошибка разбора ({error})\n{command}")
            continue
        if request is None:
            dump.failed.append(f"строка {source_line}: {reason}\n{command}")
            continue
        noise, noise_reason = is_noise(request.url, host_patterns, path_suffixes)
        request.is_noise = noise
        request.noise_reason = noise_reason
        if noise:
            dump.noise.append(request)
        else:
            dump.requests.append(request)
    return dump


# --------------------------------------------------------------------------------------
# Текстовое представление
# --------------------------------------------------------------------------------------


def _body_marker(request: ApiRequest) -> str:
    """Возвращает пометку о наличии тела запроса.

    :param request: Разобранный запрос.
    :return: ``json``, ``body`` или пустая строка.
    """
    if request.body_raw is None:
        return ""
    return "json" if request.body_json is not None else "body"


def format_requests(dump: ApiDump, verbose: bool = False) -> str:
    """Готовит текстовое представление дампа для подкоманды ``api``.

    Основная часть — группировка по нормализованному пути: видно API-контур сценария,
    методы и признак наличия тела. В подробном режиме дополнительно печатаются query,
    значимые заголовки и тело каждого запроса.

    :param dump: Разобранный дамп.
    :param verbose: Печатать ли подробности по каждому запросу.
    :return: Готовый текст отчёта.
    """
    lines: list[str] = []
    lines.append(f"Дамп сети: {dump.path}")
    lines.append(
        f"Полезных запросов: {len(dump.requests)}; "
        f"отфильтровано шума: {len(dump.noise)}; "
        f"не разобрано: {len(dump.failed)}"
    )

    grouped = group_by_path(dump.requests)
    lines.append("")
    lines.append(f"API-контур сценария ({len(grouped)} уникальных путей):")
    for normalized, requests in grouped.items():
        methods = sorted({request.method for request in requests})
        markers = sorted({_body_marker(request) for request in requests} - {""})
        body_part = f" [{'/'.join(markers)}]" if markers else ""
        mark = "*" if is_interesting_path(normalized) else " "
        lines.append(f"  {mark} {','.join(methods):<12} x{len(requests):<3} {normalized}{body_part}")

    if verbose:
        lines.append("")
        lines.append("Запросы по порядку:")
        for request in dump.requests:
            lines.append("")
            lines.append(f"  #{request.index} (строка {request.source_line}) {request.method} {request.url}")
            if request.query:
                pairs = ", ".join(f"{name}={value}" for name, value in request.query)
                lines.append(f"    query: {pairs}")
            for name, value in significant_headers(request):
                lines.append(f"    {name}: {value}")
            if request.body_raw is not None:
                if request.body_json is not None:
                    rendered = json.dumps(request.body_json, ensure_ascii=False, indent=2)
                    indented = "\n".join(f"      {line}" for line in rendered.split("\n"))
                    lines.append("    тело (JSON):")
                    lines.append(indented)
                else:
                    lines.append(f"    тело: {request.body_raw}")

    if dump.failed:
        lines.append("")
        lines.append(f"Не разобрано ({len(dump.failed)}):")
        for entry in dump.failed:
            first_line = entry.split("\n", 1)[0]
            lines.append(f"  {first_line}")
    return "\n".join(lines)
