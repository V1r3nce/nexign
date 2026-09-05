"""Прогон локаторов репозитория по снимкам DOM и классификация результатов.

Модуль отвечает на два вопроса заказчика: какие локаторы в снимке не находятся вообще
(сломаны) и какие находятся более одного раза (риск strict mode в Playwright). Дополнительно
сверяет человекочитаемое описание локатора с фактическим текстом найденного элемента
и подбирает кандидатов на замену.

CSS исполняется через soupsieve, XPath — через lxml. Если lxml не установлен, XPath-локаторы
получают статус :attr:`MatchStatus.NOT_CHECKED`, а в отчёт добавляется явное предупреждение,
а не ложное «сломан». Селектор, который не скомпилировался, тоже отделён от «не найден»:
для него заведён отдельный статус :attr:`MatchStatus.COMPILE_ERROR`.

Рендер отчёта в текст живёт в cli.py — здесь формируются только машинные структуры из models.
"""

from __future__ import annotations

import re
import time
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field, replace
from typing import Any

import soupsieve

from scripts.dom_inspector.dump_parser import iter_snapshots, parse_dump
from scripts.dom_inspector.element_index import (
    ParsedSnapshot,
    describe_bs4_element,
    describe_lxml_element,
    dom_path_of,
    normalize_text,
    parse_snapshot,
    text_key,
)
from scripts.dom_inspector.locator_collector import classify_selector, collect_locators, group_by_selector
from scripts.dom_inspector.models import (
    DomElement,
    DumpDocument,
    InspectionOptions,
    InspectionReport,
    LocatorCheckResult,
    LocatorRecord,
    MatchStatus,
    ReplacementCandidate,
    SelectorKind,
    Severity,
    SnapshotIndex,
    SnapshotMatchResult,
)

try:
    from lxml import etree as lxml_etree

    LXML_AVAILABLE = True
except ImportError:  # pragma: no cover - окружение без lxml
    lxml_etree = None
    LXML_AVAILABLE = False

#: Типы селекторов, которые вообще можно исполнить по документу.
EXECUTABLE_KINDS: frozenset[SelectorKind] = frozenset({SelectorKind.CSS, SelectorKind.XPATH})

#: Теги, которые предпочтительнее видеть в кандидате на замену (настоящий управляющий элемент).
LEAF_TAGS: frozenset[str] = frozenset({"button", "a", "input", "select", "textarea", "label", "option", "summary"})

#: Теги-обёртки: технически подходят, но как кандидат хуже настоящей кнопки.
WRAPPER_TAGS: frozenset[str] = frozenset({"div", "span", "li", "td", "th", "p", "section"})

#: Родовые слова в начале описания локатора, которые не являются подписью элемента.
DESCRIPTION_PREFIXES: frozenset[str] = frozenset(
    {
        "блок",
        "вкладка",
        "выпадающий",
        "заголовок",
        "значение",
        "иконка",
        "информация",
        "кнопка",
        "колонка",
        "меню",
        "модальное",
        "надпись",
        "окно",
        "переключатель",
        "плашка",
        "поле",
        "радиокнопка",
        "селект",
        "список",
        "ссылка",
        "столбец",
        "строка",
        "таблица",
        "текст",
        "тумблер",
        "уведомление",
        "чек-бокс",
        "чекбокс",
        "элемент",
    }
)

#: Текст в кавычках любого начертания: 'Добавить', "Добавить", «Добавить», “Добавить”, ‘Добавить’.
QUOTED_TEXT_RE: re.Pattern[str] = re.compile(
    r"'([^']{1,80})'|\"([^\"]{1,80})\"|«([^»]{1,80})»|“([^”]{1,80})”|‘([^’]{1,80})’"
)

#: Литералы значений атрибутов и идентификаторов для дешёвого предфильтра.
PREFILTER_TOKEN_RE: re.Pattern[str] = re.compile(
    r"""\[\s*[\w:|.-]+\s*[~^|*$]?=\s*(?:"([^"]+)"|'([^']+)'|([^\]\s]+))|\#([A-Za-z_][\w-]*)"""
)

#: Содержимое :not(...) из предфильтра выбрасывается, иначе получаем ложные нули.
NOT_PSEUDO_RE: re.Pattern[str] = re.compile(r":not\([^()]*\)")

#: Минимальная длина литерала, при которой предфильтр ему доверяет.
PREFILTER_MIN_TOKEN_LENGTH = 5

#: Минимальная длина подписи, при которой ей доверяют как частичному совпадению.
MIN_CONTAINMENT_LENGTH = 4

#: Якорный id в CSS (``#customer-individual-view``) и в атрибутной форме (``[id='...']``, ``@id="..."``).
ANCHOR_ID_RE: re.Pattern[str] = re.compile(
    r"""\#([A-Za-z_][\w:.-]*)|\[\s*id\s*=\s*(?:"([^"]+)"|'([^']+)'|([^\]\s]+))\s*\]|@id\s*=\s*(?:"([^"]+)"|'([^']+)')"""
)

#: Якорный data-testid в CSS (``[data-testid=chm-...]``) и в XPath (``@data-testid='...'``).
ANCHOR_TEST_ID_RE: re.Pattern[str] = re.compile(
    r"""\[\s*data-testid\s*=\s*(?:"([^"]+)"|'([^']+)'|([^\]\s]+))\s*\]|@data-testid\s*=\s*(?:"([^"]+)"|'([^']+)')"""
)

#: Сколько адресов снимков перечислять в строке-пояснении: полный список даёт нечитаемую простыню.
MAX_ADDRESSES_IN_MESSAGE = 2

#: Подпись элемента не имеет ничего общего с описанием локатора.
MATCH_NONE = ""
#: Собственный текст элемента точно равен подписи из описания.
MATCH_TEXT = "text"
#: Подпись совпала по aria-label / title / placeholder / value.
MATCH_ATTR = "attr"
#: Подписи пересекаются частично (одна входит в другую).
MATCH_PARTIAL = "partial"

_RUNNER_CACHE: dict[tuple[str, SelectorKind], SelectorRunner] = {}
_PATH_MAPS: dict[int, tuple[SnapshotIndex, dict[str, DomElement]]] = {}
_LABEL_MAPS: dict[int, tuple[SnapshotIndex, dict[str, list[DomElement]]]] = {}


def reset_caches() -> None:
    """Сбрасывает кэши скомпилированных селекторов и индексов снимков.

    Вызывается в начале :func:`check_dump`, чтобы повторный прогон в том же процессе
    (например по другому дампу) не подхватил элементы предыдущего.

    :return: None.
    """
    _RUNNER_CACHE.clear()
    _PATH_MAPS.clear()
    _LABEL_MAPS.clear()


def collapse_ws_outside_quotes(selector: str) -> str:
    """Схлопывает последовательности пробельных символов вне кавычек и обрезает края.

    Обязательная предобработка перед ``soupsieve.compile``: soupsieve 2.8.4 падает на
    ``div  > p`` («The combinator ... must have a selector before it»), хотя браузер
    и Playwright такое принимают. Пробелы внутри значений атрибутов не трогаются.

    :param selector: Исходный CSS-селектор.
    :return: Селектор с одиночными пробелами вне кавычек.
    """
    chunks: list[str] = []
    quote: str | None = None
    index = 0
    length = len(selector)
    while index < length:
        char = selector[index]
        if quote is not None:
            chunks.append(char)
            if char == "\\" and index + 1 < length:
                chunks.append(selector[index + 1])
                index += 1
            elif char == quote:
                quote = None
        elif char in "\"'":
            quote = char
            chunks.append(char)
        elif char.isspace():
            end = index
            while end < length and selector[end].isspace():
                end += 1
            chunks.append(" ")
            index = end - 1
        else:
            chunks.append(char)
        index += 1
    return "".join(chunks).strip()


def has_top_level_comma(selector: str) -> bool:
    """Есть ли в селекторе запятая верхнего уровня (то есть это список «или»).

    :param selector: CSS-селектор.
    :return: True, если запятая найдена вне скобок и кавычек.
    """
    depth = 0
    quote: str | None = None
    index = 0
    length = len(selector)
    while index < length:
        char = selector[index]
        if quote is not None:
            if char == "\\":
                index += 2
                continue
            if char == quote:
                quote = None
        elif char in "\"'":
            quote = char
        elif char in "([":
            depth += 1
        elif char in ")]":
            depth = max(0, depth - 1)
        elif char == "," and depth == 0:
            return True
        index += 1
    return False


def extract_prefilter_tokens(selector: str) -> tuple[str, ...]:
    """Достаёт из селектора литералы, которые обязаны встречаться в тексте снимка.

    Селекторы со списком верхнего уровня фильтровать нельзя (запятая — это «или»),
    содержимое ``:not(...)`` тоже выбрасывается, иначе появляются ложные нули.

    :param selector: CSS-селектор.
    :return: Кортеж литералов длиной не меньше :data:`PREFILTER_MIN_TOKEN_LENGTH`.
    """
    if has_top_level_comma(selector):
        return ()
    body = selector
    while True:
        stripped = NOT_PSEUDO_RE.sub("", body)
        if stripped == body:
            break
        body = stripped
    tokens: list[str] = []
    for match in PREFILTER_TOKEN_RE.finditer(body):
        value = match.group(1) or match.group(2) or match.group(3) or match.group(4)
        if not value or value.startswith("-"):
            continue
        if len(value) >= PREFILTER_MIN_TOKEN_LENGTH:
            tokens.append(value)
    return tuple(dict.fromkeys(tokens))


def token_prefilter(selector: str, html: str) -> bool:
    """Дешёвая проверка «имеет ли смысл вообще запускать движок на этом снимке».

    Даёт ускорение примерно в 4.5 раза при побитово том же результате: если хоть один
    литерал из селектора не встречается подстрокой в тексте снимка, совпадений заведомо ноль.

    :param selector: CSS-селектор.
    :param html: Текст снимка DOM.
    :return: True, если селектор нужно исполнять; False, если совпадений точно нет.
    """
    tokens = extract_prefilter_tokens(selector)
    return all(token in html for token in tokens)


def extract_expected_text(description: str) -> str | None:
    """Достаёт подпись элемента из человекочитаемого описания локатора.

    ``Кнопка 'Добавить' договор`` -> ``Добавить``. Поддержаны кавычки ``' " « » “ ” ‘ ’``.

    :param description: Описание локатора (аргумент locator_name).
    :return: Текст в кавычках либо None, если кавычек нет.
    """
    match = QUOTED_TEXT_RE.search(description or "")
    if match is None:
        return None
    for group in match.groups():
        if group and group.strip():
            return normalize_text(group)
    return None


def search_phrases(record: LocatorRecord) -> list[str]:
    """Строит список фраз, по которым ищутся кандидаты на замену.

    Приоритет: текст в кавычках, затем описание без родового слова («Кнопка Обновить» ->
    «Обновить»), затем описание целиком.

    :param record: Локатор репозитория.
    :return: Список непустых фраз без повторов, в порядке убывания приоритета.
    """
    phrases: list[str] = []
    quoted = extract_expected_text(record.description)
    if quoted:
        phrases.append(quoted)
    description = normalize_text(record.description or "")
    if description:
        words = description.split(" ")
        trimmed = list(words)
        while trimmed and trimmed[0].casefold().strip(".,:;") in DESCRIPTION_PREFIXES:
            trimmed = trimmed[1:]
        if trimmed and len(trimmed) != len(words):
            phrases.append(" ".join(trimmed))
        phrases.append(description)
    return [phrase for phrase in dict.fromkeys(phrases) if phrase]


class SelectorRunner:
    """Скомпилированный селектор: компиляция один раз, исполнение на каждом снимке.

    :ivar selector: Исходная строка селектора.
    :ivar kind: Тип селектора, определяющий движок.
    :ivar prepared: Строка, реально переданная движку (для CSS — со схлопнутыми пробелами).
    :ivar error: Текст ошибки компиляции; при не-None :meth:`run` всегда возвращает пустой список.
    :ivar unavailable: True, если движок недоступен (нет lxml) либо тип селектора не исполняется.
    :ivar last_error: Текст последней runtime-ошибки движка, если она была.
    """

    __slots__ = ("selector", "kind", "prepared", "error", "unavailable", "last_error", "_tokens", "_css", "_xpath")

    def __init__(self, selector: str, kind: SelectorKind) -> None:
        """Компилирует селектор нужным движком.

        :param selector: Строка селектора.
        :param kind: Тип селектора.
        """
        self.selector = selector
        self.kind = kind
        self.prepared = selector.strip()
        self.error: str | None = None
        self.unavailable = False
        self.last_error: str | None = None
        self._tokens: tuple[str, ...] = ()
        self._css: Any = None
        self._xpath: Any = None
        if kind is SelectorKind.CSS:
            self.prepared = collapse_ws_outside_quotes(selector)
            self._tokens = extract_prefilter_tokens(self.prepared)
            try:
                self._css = soupsieve.compile(self.prepared)
            except Exception as exc:  # noqa: BLE001 - текст ошибки нужен в отчёте
                self.error = _format_exception(exc)
        elif kind is SelectorKind.XPATH:
            if not LXML_AVAILABLE:
                self.unavailable = True
            else:
                try:
                    self._xpath = lxml_etree.XPath(self.prepared)
                except Exception as exc:  # noqa: BLE001 - текст ошибки нужен в отчёте
                    self.error = _format_exception(exc)
        else:
            self.unavailable = True

    @property
    def executable(self) -> bool:
        """Можно ли реально исполнить селектор по документу.

        :return: True, если селектор скомпилирован и движок доступен.
        """
        return self.error is None and not self.unavailable

    def run(self, parsed: ParsedSnapshot) -> list[DomElement]:
        """Исполняет селектор на одном снимке.

        :param parsed: Разобранный снимок (оба дерева плюс индекс элементов).
        :return: Найденные элементы; пустой список при ошибке компиляции, недоступном
            движке, отсечении предфильтром или runtime-ошибке движка.
        """
        self.last_error = None
        if not self.executable:
            return []
        if self._css is not None:
            if self._tokens and not all(token in parsed.snapshot.html for token in self._tokens):
                return []
            try:
                nodes = self._css.select(parsed.soup)
            except Exception as exc:  # noqa: BLE001 - runtime-ошибку показываем, но не роняем прогон
                self.last_error = _format_exception(exc)
                return []
            return [resolve_element(parsed, node, from_lxml=False) for node in nodes]
        try:
            raw = self._xpath(parsed.tree)
        except Exception as exc:  # noqa: BLE001 - runtime-ошибку показываем, но не роняем прогон
            self.last_error = _format_exception(exc)
            return []
        if not isinstance(raw, list):
            return []
        return [
            resolve_element(parsed, node, from_lxml=True)
            for node in raw
            if hasattr(node, "tag") and isinstance(getattr(node, "tag", None), str)
        ]


def get_runner(selector: str, kind: SelectorKind) -> SelectorRunner:
    """Кэширующая фабрика скомпилированных селекторов.

    :param selector: Строка селектора.
    :param kind: Тип селектора.
    :return: Экземпляр :class:`SelectorRunner`, один и тот же для одинаковой пары аргументов.
    """
    key = (selector, kind)
    runner = _RUNNER_CACHE.get(key)
    if runner is None:
        runner = SelectorRunner(selector, kind)
        _RUNNER_CACHE[key] = runner
    return runner


def _format_exception(exc: BaseException) -> str:
    """Приводит исключение движка к однострочному виду для отчёта.

    :param exc: Пойманное исключение.
    :return: Строка вида ``SelectorSyntaxError: Invalid predicate``.
    """
    message = str(exc).replace("\r", " ").split("\n")[0].strip()
    return f"{type(exc).__name__}: {message}" if message else type(exc).__name__


def _path_map(parsed: ParsedSnapshot) -> dict[str, DomElement]:
    """Возвращает карту «индексный путь -> описанный элемент» для снимка.

    Карта строится один раз на снимок: она позволяет не описывать один и тот же узел
    повторно для каждого из 2682 локаторов.

    :param parsed: Разобранный снимок.
    :return: Словарь dom_path -> DomElement.
    """
    key = parsed.index.snapshot_index
    cached = _PATH_MAPS.get(key)
    if cached is not None and cached[0] is parsed.index:
        return cached[1]
    mapping = {element.dom_path: element for element in parsed.index.elements}
    _PATH_MAPS[key] = (parsed.index, mapping)
    return mapping


def _label_map(index: SnapshotIndex) -> dict[str, list[DomElement]]:
    """Строит индекс «нормализованная подпись -> элементы» поверх :class:`SnapshotIndex`.

    К штатному ``by_text`` добавляются aria-label, title, placeholder и value, потому что
    у иконочных кнопок собственного текста нет, а подпись из описания локатора есть.

    :param index: Индекс снимка.
    :return: Словарь ключ текста -> список элементов.
    """
    key = index.snapshot_index
    cached = _LABEL_MAPS.get(key)
    if cached is not None and cached[0] is index:
        return cached[1]
    mapping: dict[str, list[DomElement]] = {}
    for text, elements in index.by_text.items():
        mapping.setdefault(text, []).extend(elements)
    for element in index.elements:
        if element.tag == "svg":
            continue
        for value in (element.aria_label, element.title, element.placeholder, element.value):
            if not value:
                continue
            bucket = mapping.setdefault(text_key(value), [])
            if element not in bucket:
                bucket.append(element)
    _LABEL_MAPS[key] = (index, mapping)
    return mapping


def resolve_element(parsed: ParsedSnapshot, node: object, from_lxml: bool) -> DomElement:
    """Переводит найденный узел дерева в :class:`DomElement` из индекса снимка.

    Деревья bs4 и lxml структурно идентичны, поэтому индексный путь узла — общий ключ.
    Если узла в индексе почему-то нет (например матч пришёлся на служебный узел),
    элемент описывается на месте.

    :param parsed: Разобранный снимок.
    :param node: Узел дерева bs4 либо lxml.
    :param from_lxml: True, если узел получен от lxml (движок XPath).
    :return: Описанный элемент DOM.
    """
    path = dom_path_of(node)
    element = _path_map(parsed).get(path)
    if element is not None:
        return element
    snapshot_index = parsed.snapshot.index
    if from_lxml:
        return describe_lxml_element(node, snapshot_index)
    return describe_bs4_element(node, snapshot_index)


def owner_scopes(record: LocatorRecord) -> tuple[str, str]:
    """Возвращает области, по которым считается покрытие: файл целиком и класс-владелец.

    Файл локаторов держит по несколько страниц и форм сразу (``client_profile.py`` — это и карточка
    клиента, и форма редактирования, и вкладки), поэтому покрытие по файлу занижено и уводит
    сломанные локаторы в ``page_not_in_dump``. Класс-владелец — куда более честная единица «страницы».

    :param record: Проверяемый локатор.
    :return: Пара ключей (файл, файл::класс).
    """
    return (record.file, f"{record.file}::{record.class_name}")


def compute_owner_coverage(
    record: LocatorRecord,
    found_by_scope: Mapping[str, int],
    total_by_scope: Mapping[str, int],
    found_in_dump: Mapping[str, int] | None = None,
) -> float:
    """Считает долю селекторов владельца локатора, найденных в снимке.

    Это контекстный фильтр «страница локатора вообще есть в этом дампе»: без него
    сломанными объявятся почти все локаторы, просто потому что дамп снят с другой страницы.
    Берётся максимум трёх оценок:

    * покрытие файла в этом снимке — спасает класс, в котором всего пара локаторов;
    * покрытие класса-владельца в этом снимке — спасает файл, держащий несколько страниц сразу
      (``client_profile.py`` — это и карточка клиента, и форма редактирования, и вкладки);
    * покрытие класса-владельца по дампу целиком — статус ``page_not_in_dump`` выносится по всему
      дампу, а не по одному снимку, поэтому и мерить присутствие страницы надо по всему дампу.

    :param record: Проверяемый локатор.
    :param found_by_scope: Сколько уникальных селекторов области нашлось в снимке.
    :param total_by_scope: Сколько уникальных исполняемых селекторов у области всего.
    :param found_in_dump: Сколько уникальных селекторов области нашлось хоть в одном снимке дампа.
    :return: Доля от 0.0 до 1.0.
    """
    best = 0.0
    scopes = owner_scopes(record)
    for scope in scopes:
        total = total_by_scope.get(scope, 0)
        if total <= 0:
            continue
        best = max(best, found_by_scope.get(scope, 0) / total)
    class_scope = scopes[1]
    class_total = total_by_scope.get(class_scope, 0)
    if found_in_dump is not None and class_total > 0:
        best = max(best, found_in_dump.get(class_scope, 0) / class_total)
    return best


def extract_anchors(selector: str) -> tuple[frozenset[str], frozenset[str]]:
    """Достаёт из селектора точные якоря: значения id и data-testid.

    :param selector: Строка селектора (CSS или XPath).
    :return: Пара множеств (значения id, значения data-testid).
    """
    ids = {match for group in ANCHOR_ID_RE.findall(selector) for match in group if match}
    test_ids = {match for group in ANCHOR_TEST_ID_RE.findall(selector) for match in group if match}
    return frozenset(ids), frozenset(test_ids)


def anchor_present(anchors: tuple[frozenset[str], frozenset[str]], indexes: Iterable[SnapshotIndex]) -> bool:
    """Проверяет, встречается ли хотя бы один якорь селектора в снимках дампа.

    Если якорный ``#id`` или ``[data-testid=...]`` в дампе есть, то страница в дампе есть тоже,
    и молчать про такой локатор нельзя, каким бы ни было покрытие файла-владельца.

    :param anchors: Пара множеств (id, data-testid) из :func:`extract_anchors`.
    :param indexes: Индексы снимков дампа.
    :return: True, если якорь найден хотя бы в одном снимке.
    """
    ids, test_ids = anchors
    if not ids and not test_ids:
        return False
    for index in indexes:
        if any(value in index.by_id for value in ids):
            return True
        if any(value in index.by_test_id for value in test_ids):
            return True
    return False


def decide_status(
    record: LocatorRecord,
    results: Sequence[SnapshotMatchResult],
    compile_error: str | None,
    options: InspectionOptions,
    anchor_found: bool = False,
) -> MatchStatus:
    """Классифицирует итог проверки одного локатора по всем снимкам.

    :param record: Проверяемый локатор.
    :param results: Результаты по снимкам.
    :param compile_error: Текст ошибки компиляции селектора, если она была.
    :param options: Параметры запуска (нужен порог контекстного фильтра).
    :param anchor_found: True, если якорный id/data-testid селектора есть в дампе — тогда
        страница в дампе точно есть и порог покрытия не применяется.
    :return: Статус из :class:`MatchStatus`.
    """
    if compile_error is not None:
        return MatchStatus.COMPILE_ERROR
    if record.kind not in EXECUTABLE_KINDS:
        return MatchStatus.NOT_CHECKED
    max_matches = max((result.match_count for result in results), default=0)
    if max_matches == 0:
        if anchor_found:
            return MatchStatus.NOT_FOUND
        best_coverage = max((result.owner_coverage or 0.0 for result in results), default=0.0)
        if best_coverage >= options.owner_coverage_threshold:
            return MatchStatus.NOT_FOUND
        return MatchStatus.PAGE_NOT_IN_DUMP
    if max_matches == 1:
        return MatchStatus.UNIQUE
    max_rendered = max((result.rendered_count for result in results if result.match_count > 1), default=0)
    if max_rendered >= 2:
        return MatchStatus.MULTIPLE_VISIBLE
    return MatchStatus.UNIQUE_VISIBLE


def decide_severity(
    record: LocatorRecord,
    status: MatchStatus,
    results: Sequence[SnapshotMatchResult],
) -> Severity:
    """Определяет приоритет находки.

    Фильтр видимости служит только для понижения приоритета: Playwright strict mode
    считает все совпадения независимо от того, видит их пользователь или нет.
    Настоящий фильтр шума — тип обёртки: для списочных обёрток дубли ожидаемы.

    :param record: Проверяемый локатор.
    :param status: Статус проверки.
    :param results: Результаты по снимкам.
    :return: Приоритет из :class:`Severity`.
    """
    if status is MatchStatus.COMPILE_ERROR:
        return Severity.HIGH
    if status is MatchStatus.NOT_FOUND:
        return Severity.LOW if record.is_list else Severity.HIGH
    if status is MatchStatus.MULTIPLE_VISIBLE:
        return Severity.LOW if record.is_list else Severity.HIGH
    if status is MatchStatus.UNIQUE_VISIBLE:
        return Severity.INFO if record.is_list else Severity.MEDIUM
    return Severity.INFO


def _match_phrase(element: DomElement, phrase_key: str) -> str:
    """Определяет, как элемент соотносится с искомой фразой.

    :param element: Элемент DOM.
    :param phrase_key: Ключ искомой фразы (normalize_text + casefold).
    :return: Одно из :data:`MATCH_TEXT`, :data:`MATCH_ATTR`, :data:`MATCH_PARTIAL`, :data:`MATCH_NONE`.
    """
    if not phrase_key:
        return MATCH_NONE
    partial = False
    element_text = text_key(element.text)
    if element_text:
        if element_text == phrase_key:
            return MATCH_TEXT
        if _contains(element_text, phrase_key):
            partial = True
    for value in (element.aria_label, element.title, element.placeholder, element.value, element.own_text):
        if not value:
            continue
        key = text_key(value)
        if not key:
            continue
        if key == phrase_key:
            return MATCH_ATTR
        if _contains(key, phrase_key):
            partial = True
    return MATCH_PARTIAL if partial else MATCH_NONE


def _contains(first: str, second: str) -> bool:
    """Проверяет вхождение одной подписи в другую с защитой от слишком коротких слов.

    :param first: Первый ключ текста.
    :param second: Второй ключ текста.
    :return: True, если один ключ входит в другой и оба достаточно длинные.
    """
    if len(first) < MIN_CONTAINMENT_LENGTH or len(second) < MIN_CONTAINMENT_LENGTH:
        return False
    return first in second or second in first


def _candidate_score(element: DomElement, match_kind: str, ambiguity: int) -> tuple[float, list[str]]:
    """Оценивает пригодность элемента как замены локатора.

    :param element: Найденный элемент.
    :param match_kind: Как совпала подпись: текст, атрибут или частично.
    :param ambiguity: Сколько элементов снимка находит предлагаемый селектор.
    :return: Пара «оценка», «список причин для отчёта».
    """
    if match_kind == MATCH_TEXT:
        score, reasons = 3.0, ["текст совпал с описанием"]
    elif match_kind == MATCH_ATTR:
        score, reasons = 2.4, ["подпись элемента совпала с описанием"]
    else:
        score, reasons = 1.2, ["текст похож на описание"]
    if element.test_id:
        score += 2.0
        reasons.append("стабильный data-testid")
    elif element.element_id:
        score += 1.5
        reasons.append("есть id")
    elif element.name:
        score += 1.0
        reasons.append("есть name")
    elif element.aria_label:
        score += 0.5
        reasons.append("есть aria-label")
    if element.tag in LEAF_TAGS:
        score += 1.0
        reasons.append(f"тег {element.tag}")
    elif element.tag in WRAPPER_TAGS:
        score -= 0.5
        reasons.append(f"обёртка {element.tag}")
    if element.is_interactive:
        score += 0.5
    if element.rendered:
        score += 0.75
    else:
        score -= 0.75
        reasons.append(f"скрыт ({element.hidden_reason})")
    if ambiguity > 1:
        score -= 1.5
        reasons.append(f"осторожно: селектор находит {ambiguity} элементов в снимке")
    return score, reasons


def _selector_ambiguity(element: DomElement, index: SnapshotIndex) -> int:
    """Сколько элементов снимка находит предлагаемый селектор кандидата.

    Предлагать в замену селектор, который сам по себе даёт дубли, бессмысленно —
    Playwright упадёт на нём так же, как на исходном.

    :param element: Кандидат.
    :param index: Индекс снимка.
    :return: Количество элементов, попадающих под селектор кандидата.
    """
    if element.test_id:
        return len(index.by_test_id.get(element.test_id, ()))
    if element.element_id:
        return len(index.by_id.get(element.element_id, ()))
    return 1


def suggest_candidates(
    record: LocatorRecord,
    results: Sequence[SnapshotMatchResult],
    indexes: Mapping[int, SnapshotIndex],
    limit: int,
) -> list[ReplacementCandidate]:
    """Подбирает кандидатов на замену локатора по описанию из репозитория.

    Ищет элементы, чей текст (или aria-label / title / placeholder / value) совпадает
    с подписью из описания локатора, отбрасывает элементы без стабильного селектора
    и ранжирует по стабильности атрибута (data-testid > id > name > aria-label)
    и «листовости» тега (button/a/input выше div).

    :param record: Проверяемый локатор.
    :param results: Результаты по снимкам — задают порядок обхода (сначала «свои» страницы).
    :param indexes: Индексы снимков по их сквозному номеру.
    :param limit: Сколько кандидатов вернуть.
    :return: Кандидаты, отсортированные по убыванию оценки.
    """
    phrases = search_phrases(record)
    if not phrases or limit <= 0:
        return []
    preferred: list[int] = []
    for result in sorted(results, key=lambda item: (-(item.owner_coverage or 0.0), item.snapshot_index)):
        if result.snapshot_index in indexes:
            preferred.append(result.snapshot_index)
    order = preferred + [index for index in indexes if index not in preferred]
    best: dict[str, ReplacementCandidate] = {}
    for phrase_position, phrase in enumerate(phrases):
        phrase_key = text_key(phrase)
        if not phrase_key:
            continue
        for snapshot_index in order:
            index = indexes[snapshot_index]
            label_map = _label_map(index)
            bucket: list[DomElement] = list(label_map.get(phrase_key, ()))
            if not bucket:
                for key, elements in label_map.items():
                    if _contains(key, phrase_key):
                        bucket.extend(elements)
            for element in bucket:
                selector = element.stable_selector
                if selector is None or selector == record.selector:
                    continue
                match_kind = _match_phrase(element, phrase_key)
                if match_kind == MATCH_NONE:
                    continue
                score, reasons = _candidate_score(element, match_kind, _selector_ambiguity(element, index))
                score -= 0.25 * phrase_position
                current = best.get(selector)
                if current is not None and current.score >= score:
                    continue
                best[selector] = ReplacementCandidate(
                    element=element,
                    selector=selector,
                    score=round(score, 3),
                    reason=", ".join(reasons),
                    snapshot_index=snapshot_index,
                )
        if len(best) >= limit and phrase_position == 0:
            break
    ranked = sorted(best.values(), key=lambda item: (-item.score, item.snapshot_index, item.selector))
    return ranked[:limit]


@dataclass(slots=True)
class _SelectorRun:
    """Результат прогона одного уникального селектора по всем снимкам.

    :param selector: Строка селектора.
    :param kind: Тип селектора.
    :param compile_error: Текст ошибки компиляции, если селектор не скомпилировался.
    :param unavailable: True, если движок недоступен (нет lxml) либо тип не исполняется.
    :param per_snapshot: Результаты по снимкам, где были совпадения или ошибка движка.
    :param found_in: Номера снимков, где селектор нашёлся хотя бы раз.
    """

    selector: str
    kind: SelectorKind
    compile_error: str | None = None
    unavailable: bool = False
    per_snapshot: dict[int, SnapshotMatchResult] = field(default_factory=dict)
    found_in: set[int] = field(default_factory=set)


def _run_selectors(
    selectors: Mapping[str, SelectorKind],
    parsed: Sequence[ParsedSnapshot],
    max_elements: int,
) -> dict[str, _SelectorRun]:
    """Прогоняет каждый уникальный селектор по каждому снимку.

    :param selectors: Уникальные селекторы и их типы.
    :param parsed: Разобранные снимки.
    :param max_elements: Сколько найденных элементов сохранять на снимок. Сохраняются сначала
        видимые (в порядке документа), затем скрытые: иначе при обрезке образца в отчёт попадали
        одни скрытые элементы, хотя видимые в снимке есть. Счётчики считаются до обрезки.
    :return: Словарь селектор -> результат прогона.
    """
    runs: dict[str, _SelectorRun] = {}
    for selector, kind in selectors.items():
        runner = get_runner(selector, kind)
        run = _SelectorRun(
            selector=selector,
            kind=kind,
            compile_error=runner.error,
            unavailable=runner.unavailable,
        )
        runs[selector] = run
        if not runner.executable:
            continue
        for parsed_snapshot in parsed:
            elements = runner.run(parsed_snapshot)
            if not elements and runner.last_error is None:
                continue
            snapshot = parsed_snapshot.snapshot
            run.per_snapshot[snapshot.index] = SnapshotMatchResult(
                snapshot_index=snapshot.index,
                case_no=snapshot.case_no,
                start_line=snapshot.start_line,
                end_line=snapshot.end_line,
                match_count=len(elements),
                pw_visible_count=sum(1 for element in elements if element.pw_visible),
                rendered_count=sum(1 for element in elements if element.rendered),
                elements=sorted(elements, key=lambda element: not element.rendered)[:max_elements],
                error=runner.last_error,
            )
            if elements:
                run.found_in.add(snapshot.index)
    return runs


def _coverage_tables(
    records: Sequence[LocatorRecord],
    runs: Mapping[str, _SelectorRun],
    parsed: Sequence[ParsedSnapshot],
) -> tuple[dict[str, int], dict[int, dict[str, int]], dict[str, int]]:
    """Строит таблицы покрытия «область владения -> снимок».

    Областей две на каждый локатор: файл целиком и класс-владелец внутри файла (см.
    :func:`owner_scopes`). Класс нужен потому, что один файл локаторов описывает несколько
    страниц сразу, и покрытие по файлу занижает оценку присутствия страницы в дампе.

    :param records: Все собранные локаторы.
    :param runs: Результаты прогона уникальных селекторов.
    :param parsed: Разобранные снимки.
    :return: Тройка «всего исполняемых селекторов у области», «найдено селекторов области в снимке»,
        «найдено селекторов области хоть в одном снимке дампа».
    """
    selectors_by_scope: dict[str, set[str]] = {}
    for record in records:
        run = runs.get(record.selector)
        if run is None or run.compile_error is not None or run.unavailable:
            continue
        for scope in owner_scopes(record):
            selectors_by_scope.setdefault(scope, set()).add(record.selector)
    total_by_scope = {scope: len(selectors) for scope, selectors in selectors_by_scope.items()}
    found_by_snapshot: dict[int, dict[str, int]] = {parsed_snapshot.snapshot.index: {} for parsed_snapshot in parsed}
    found_in_dump: dict[str, int] = {}
    for scope, selectors in selectors_by_scope.items():
        for selector in selectors:
            found_in = runs[selector].found_in
            if found_in:
                found_in_dump[scope] = found_in_dump.get(scope, 0) + 1
            for snapshot_index in found_in:
                counters = found_by_snapshot.setdefault(snapshot_index, {})
                counters[scope] = counters.get(scope, 0) + 1
    return total_by_scope, found_by_snapshot, found_in_dump


def _observed_texts(results: Iterable[SnapshotMatchResult]) -> list[str]:
    """Собирает нормализованные подписи найденных элементов без повторов.

    :param results: Результаты по снимкам.
    :return: Список подписей в порядке появления.
    """
    texts: list[str] = []
    for result in results:
        for element in result.elements:
            label = element.label
            if label and label not in texts:
                texts.append(label)
    return texts


def _has_interactive_match(results: Sequence[SnapshotMatchResult]) -> bool:
    """Есть ли среди найденных элементов управляющий (кнопка, ссылка, вкладка, поле).

    Расхождение описания и текста особенно важно именно для управляющих элементов:
    у контейнеров и заголовков текст динамический, и там расхождение — обычное дело.

    :param results: Результаты по снимкам.
    :return: True, если хотя бы одно совпадение — интерактивный элемент или лист-тег.
    """
    for result in results:
        for element in result.elements:
            if element.is_interactive or element.tag in LEAF_TAGS:
                return True
    return False


def _detect_text_mismatch(expected: str | None, results: Sequence[SnapshotMatchResult]) -> bool:
    """Проверяет, расходится ли описание локатора с фактическим текстом элемента.

    Именно эта проверка ловит эталонный случай заказчика: локатор
    ``[data-testid=chm-ChmAgreementsList-tlb-1-create]`` описан как ``Кнопка 'Добавить' договор``,
    а в DOM это кнопка с текстом ``Создать``.

    :param expected: Подпись из описания локатора.
    :param results: Результаты по снимкам.
    :return: True, если ни один найденный элемент не имеет ожидаемой подписи.
    """
    if not expected or len(expected) < 2:
        return False
    expected_key = text_key(expected)
    if not expected_key:
        return False
    judged = False
    for result in results:
        for element in result.elements:
            if _match_phrase(element, expected_key) != MATCH_NONE:
                return False
            if element.label:
                judged = True
    return judged


def _build_message(
    record: LocatorRecord,
    status: MatchStatus,
    results: Sequence[SnapshotMatchResult],
    expected: str | None,
    observed: Sequence[str],
    text_mismatch: bool,
    compile_error: str | None,
    unavailable: bool,
    anchor_found: bool = False,
) -> str:
    """Собирает готовую строку-пояснение для отчёта.

    :param record: Проверяемый локатор.
    :param status: Статус проверки.
    :param results: Результаты по снимкам.
    :param expected: Подпись из описания локатора.
    :param observed: Фактические подписи найденных элементов.
    :param text_mismatch: Признак расхождения описания и текста.
    :param compile_error: Текст ошибки компиляции.
    :param unavailable: True, если движок был недоступен.
    :param anchor_found: True, если якорный id/data-testid селектора есть в дампе.
    :return: Одна строка на русском языке.
    """
    with_matches = [result for result in results if result.match_count]
    addresses = ", ".join(result.address for result in with_matches[:MAX_ADDRESSES_IN_MESSAGE]) or "нигде"
    if len(with_matches) > MAX_ADDRESSES_IN_MESSAGE:
        addresses = f"{addresses} и ещё снимков: {len(with_matches) - MAX_ADDRESSES_IN_MESSAGE}"
    if status is MatchStatus.COMPILE_ERROR:
        return f"Селектор не компилируется: {compile_error}"
    if status is MatchStatus.NOT_CHECKED:
        if unavailable and record.kind is SelectorKind.XPATH:
            return "XPath не проверен: в окружении нет lxml"
        return f"Селектор типа {record.kind} статически не проверяется"
    if status is MatchStatus.NOT_FOUND:
        coverage = max((result.owner_coverage or 0.0 for result in results), default=0.0)
        anchor_part = (
            "якорный id/data-testid селектора в дампе есть" if anchor_found else f"покрытие владельца {coverage:.0%}"
        )
        return (
            f"Не найден ни в одном снимке, хотя страница-владелец в дампе есть ({anchor_part}). "
            "Похоже на сломанный локатор."
        )
    if status is MatchStatus.PAGE_NOT_IN_DUMP:
        coverage = max((result.owner_coverage or 0.0 for result in results), default=0.0)
        return (
            f"Совпадений нет, и покрытие владельца всего {coverage:.0%} — считаем, что страница "
            "не в этом дампе, и в проблемы локатор не выносим (проверить всё равно — ключ --coverage 0)"
        )
    max_matches = max((result.match_count for result in results), default=0)
    max_rendered = max((result.rendered_count for result in results), default=0)
    if status is MatchStatus.MULTIPLE_VISIBLE:
        return (
            f"В одном снимке до {max_matches} совпадений, видимых до {max_rendered}: "
            f"{addresses}. Playwright упадёт по strict mode."
        )
    if status is MatchStatus.UNIQUE_VISIBLE:
        visible_part = (
            "все совпадения скрыты (выпадашка или модалка не открыта)" if max_rendered == 0 else "видимое из них одно"
        )
        return (
            f"В одном снимке до {max_matches} совпадений, {visible_part}: {addresses}. "
            "Strict mode считает все совпадения, поэтому клик всё равно упадёт."
        )
    if text_mismatch:
        return f"Найден ровно один раз ({addresses}), но текст элемента {observed} не совпадает с описанием"
    if expected:
        return f"Найден ровно один раз ({addresses}), текст совпадает с описанием"
    return f"Найден ровно один раз ({addresses})"


def check_locators(
    records: Sequence[LocatorRecord],
    parsed: Sequence[ParsedSnapshot],
    options: InspectionOptions,
) -> list[LocatorCheckResult]:
    """Прогоняет локаторы по снимкам и классифицирует результат.

    Уникальные селекторы исполняются по одному разу (2682 записи дают около 2522 уникальных
    строк), затем результат разворачивается на все места объявления.

    :param records: Локаторы, собранные из репозитория.
    :param parsed: Разобранные снимки DOM.
    :param options: Параметры запуска.
    :return: Результаты проверки по каждому локатору в порядке их объявления.
    """
    grouped = group_by_selector(records)
    selectors: dict[str, SelectorKind] = {}
    for selector, group in grouped.items():
        kind = next((item.kind for item in group if item.kind is not SelectorKind.UNKNOWN), SelectorKind.UNKNOWN)
        if kind is SelectorKind.UNKNOWN:
            kind = classify_selector(selector)
        selectors[selector] = kind
    runs = _run_selectors(selectors, parsed, options.max_elements_per_snapshot)
    total_by_scope, found_by_snapshot, found_in_dump = _coverage_tables(records, runs, parsed)
    indexes: dict[int, SnapshotIndex] = {
        parsed_snapshot.snapshot.index: parsed_snapshot.index for parsed_snapshot in parsed
    }
    anchors_by_selector: dict[str, bool] = {}
    for selector in selectors:
        anchors_by_selector[selector] = anchor_present(extract_anchors(selector), indexes.values())
    checked_snapshots = len(parsed)
    checks: list[LocatorCheckResult] = []
    for record in records:
        run = runs[record.selector]
        results: list[SnapshotMatchResult] = []
        for parsed_snapshot in parsed:
            snapshot = parsed_snapshot.snapshot
            coverage = compute_owner_coverage(
                record, found_by_snapshot.get(snapshot.index, {}), total_by_scope, found_in_dump
            )
            base = run.per_snapshot.get(snapshot.index)
            if base is not None:
                results.append(replace(base, owner_coverage=coverage))
            elif not run.found_in and run.compile_error is None and not run.unavailable:
                results.append(
                    SnapshotMatchResult(
                        snapshot_index=snapshot.index,
                        case_no=snapshot.case_no,
                        start_line=snapshot.start_line,
                        end_line=snapshot.end_line,
                        match_count=0,
                        owner_coverage=coverage,
                    )
                )
        anchor_found = anchors_by_selector.get(record.selector, False)
        if run.unavailable and record.kind is SelectorKind.XPATH:
            status = MatchStatus.NOT_CHECKED
        else:
            status = decide_status(record, results, run.compile_error, options, anchor_found)
        severity = decide_severity(record, status, results)
        if options.check_lists and record.is_list:
            if status is MatchStatus.MULTIPLE_VISIBLE:
                severity = Severity.HIGH
            elif status is MatchStatus.UNIQUE_VISIBLE:
                severity = Severity.MEDIUM
        expected = extract_expected_text(record.description)
        observed = _observed_texts(results)
        text_mismatch = _detect_text_mismatch(expected, results)
        if text_mismatch and severity in (Severity.LOW, Severity.INFO) and _has_interactive_match(results):
            severity = Severity.MEDIUM
        candidates: list[ReplacementCandidate] = []
        if status is MatchStatus.NOT_FOUND or text_mismatch:
            candidates = suggest_candidates(record, results, indexes, options.max_candidates)
        owner_coverage = max((result.owner_coverage or 0.0 for result in results), default=None)
        checks.append(
            LocatorCheckResult(
                locator=record,
                status=status,
                severity=severity,
                total_matches=sum(result.match_count for result in results),
                max_matches_in_snapshot=max((result.match_count for result in results), default=0),
                snapshots_with_matches=len(run.found_in),
                checked_snapshots=checked_snapshots if run.compile_error is None and not run.unavailable else 0,
                results=results,
                expected_text=expected,
                observed_texts=observed,
                text_mismatch=text_mismatch,
                candidates=candidates,
                compile_error=run.compile_error,
                owner_coverage=owner_coverage,
                owner_anchor_found=anchor_found,
                message=_build_message(
                    record,
                    status,
                    results,
                    expected,
                    observed,
                    text_mismatch,
                    run.compile_error,
                    run.unavailable,
                    anchor_found,
                ),
            )
        )
    return checks


def check_dump(options: InspectionOptions) -> InspectionReport:
    """Главная функция подкоманды html: разбор дампа, сбор локаторов, проверка, отчёт.

    :param options: Параметры запуска.
    :return: Машинный отчёт; текстовый рендер делает cli.py.
    """
    started = time.perf_counter()
    reset_caches()
    warnings: list[str] = []
    document: DumpDocument = parse_dump(options.dump_path)
    snapshots = list(iter_snapshots(document, options.only_cases, options.only_snapshots))
    if not snapshots:
        warnings.append("В дампе не найдено ни одного снимка DOM — проверять нечего.")
    for snapshot in snapshots:
        if snapshot.truncated:
            warnings.append(f"Снимок обрезан, закрывающий тег не найден: {snapshot.address}")
    parsed = [parse_snapshot(snapshot) for snapshot in snapshots]
    records, collector_warnings = collect_locators(
        options.locators_root,
        options.ui_elements_path,
        options.project_root,
    )
    warnings.extend(collector_warnings)
    if not LXML_AVAILABLE:
        xpath_total = len({record.selector for record in records if record.kind is SelectorKind.XPATH})
        warnings.append(
            f"lxml не установлен: {xpath_total} XPath-селекторов не проверены (статус not_checked). "
            "Установите lxml~=6.1.3, иначе XPath-локаторы остаются вне проверки."
        )
    checks = check_locators(records, parsed, options)
    status_counters: dict[MatchStatus, int] = {}
    for check in checks:
        status_counters[check.status] = status_counters.get(check.status, 0) + 1
    compile_errors = sum(1 for check in checks if check.status is MatchStatus.COMPILE_ERROR)
    if compile_errors:
        warnings.append(f"Селекторов с синтаксической ошибкой: {compile_errors} — их надо чинить в репозитории.")
    skipped = status_counters.get(MatchStatus.PAGE_NOT_IN_DUMP, 0)
    if skipped and checks:
        warnings.append(
            f"{skipped} локаторов из {len(checks)} ({skipped / len(checks):.0%}) НЕ проверялись: покрытие "
            f"владельца ниже порога {options.owner_coverage_threshold:.0%}, считаем их страницы отсутствующими "
            "в дампе. Поимённо — раздел «СТРАНИЦЫ, КОТОРЫХ НЕТ В ДАМПЕ»; проверить их всё равно — "
            "ключ --coverage 0."
        )
    return InspectionReport(
        options=options,
        dump=document,
        locators_total=len(records),
        selectors_total=len({record.selector for record in records}),
        checks=checks,
        status_counters=status_counters,
        duration_seconds=time.perf_counter() - started,
        warnings=warnings,
    )
