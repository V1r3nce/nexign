"""Превращение снимка DOM в деревья и в компактный индекс опознаваемых элементов.

Единственное место в пакете, где HTML разбирается в дерево. Из одной и той же строки строятся
СРАЗУ ДВА дерева:

* ``BeautifulSoup(html, "lxml")`` — по нему работает soupsieve (CSS-локаторы репозитория);
* ``lxml.html.document_fromstring(html)`` — по нему работает ``lxml.etree.XPath`` (XPath-локаторы).

Почему парсер именно ``lxml``, а не ``html.parser`` из stdlib:

1. ``html.parser`` не достраивает корневой ``<html>`` (дампы заказчика начинаются сразу с ``<body``),
   поэтому его дерево отличается от дерева ``lxml.html.document_fromstring`` ровно на один узел —
   и индексные пути (:func:`dom_path_of`) двух движков перестают совпадать. Совпадение путей нужно,
   чтобы дедуплицировать совпадения CSS и XPath между собой.
2. На реальных снимках деревья ``BeautifulSoup(html, "lxml")`` и ``lxml.html.document_fromstring``
   структурно идентичны: одинаковое число элементов, одинаковые частоты тегов и одинаковые индексные
   пути каждого узла (проверено на снимках 70/95/146 КБ).
3. ``lxml`` заметно быстрее: разбор дампа 3,3 МБ занимает 0,07 с против 0,32 с у bs4 с тем же
   парсером и ещё дороже у ``html.parser``, а снимков в дампе 36.

Индексируются НЕ все узлы: обычный ``<div>`` без опознавательных знаков в индекс не попадает,
иначе индекс раздувается до размеров документа. В индекс идут интерактивные элементы, всё, у чего
есть ``data-testid`` / ``id`` / ``role`` / ``name`` / ``aria-label`` / ``title`` / ``placeholder``,
заголовки и текстовые узлы модальных окон и шторок (заголовок модалки в Ant Design лежит в
``div.ant-modal-title`` внутри генерируемого styled-components класса и никаких стабильных
атрибутов не имеет — без правила про модалки заголовок «Найден дубликат» в индекс бы не попал).

Видимость считается по двум шкалам (:class:`~scripts.dom_inspector.models.VisibilityScale`):
``pw_visible`` — приближение к Playwright ``is_visible()``, ``rendered`` — широкая эвристика
«пользователь реально не увидит». Полный набор правил и их приоритет описан в
:func:`self_hidden_reason`. Отдельно оговорено, чего в правилах НЕТ:

* ``aria-hidden="true"`` признаком скрытости НЕ считается: в дампах это 558 узлов, из них 290
  ``<span>`` и 50 ``<svg>`` внутри полностью видимых кнопок; Playwright его тоже не учитывает.
  Атрибут доступен через :func:`aria_hidden` как справочный сигнал.
* Одиночный ``opacity: 0`` признаком скрытости НЕ считается (234 вхождения, в том числе
  ``ant-select-selection-search-input``, куда тесты реально печатают) — только в связке с
  ``position: fixed|absolute`` и отрицательным ``z-index``.

Проверено на эталонном примере заказчика: ``[data-testid=chm-ChmAgreementsList-tlb-1-create]``
встречается в дампе 4 раза (по 2 в снимках #2 и #3), и в каждой паре второй экземпляр лежит внутри
измерительной обёртки ``clip-path: inset(100%); opacity: 0; position: fixed; z-index: -200``:
у него ``rendered=False``, но ``pw_visible=True`` — то есть strict mode Playwright он всё равно
сломает, и подавлять такие дубли по видимости нельзя.
"""

from __future__ import annotations

import re
import sys
from collections.abc import Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import lxml.html
from bs4 import BeautifulSoup
from bs4.element import Comment, Declaration, Doctype, NavigableString, ProcessingInstruction, Tag
from lxml.html import HtmlElement

PROJECT_ROOT_PATH = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT_PATH) not in sys.path:
    sys.path.append(str(PROJECT_ROOT_PATH))

from scripts.dom_inspector.models import DomElement, Snapshot, SnapshotIndex  # noqa: E402

#: Неразрывный пробел: в дампах его 60 вхождений, при сравнении текста он должен стать обычным.
NBSP: str = "\u00a0"

#: Теги, которые браузер не показывает вообще: их поддеревья не дают видимого текста.
NON_RENDERED_TAGS: frozenset[str] = frozenset(
    {"script", "style", "head", "template", "noscript", "title", "meta", "link"}
)

#: Теги, по которым элемент считается интерактивным без дополнительных признаков.
INTERACTIVE_TAGS: frozenset[str] = frozenset(
    {"button", "a", "input", "select", "textarea", "label", "summary", "option"}
)

#: Атрибуты, наличие которых само по себе делает элемент интерактивным.
INTERACTIVE_ATTRS: frozenset[str] = frozenset({"role", "tabindex", "onclick", "contenteditable"})

#: Атрибуты, по которым элемент считается опознаваемым и попадает в индекс.
IDENTITY_ATTRS: tuple[str, ...] = ("data-testid", "id", "name", "role", "aria-label", "title", "placeholder")

#: Заголовки: их текст нужен, чтобы понимать, что за экран в снимке.
HEADING_TAGS: frozenset[str] = frozenset({"h1", "h2", "h3", "h4", "h5", "h6", "legend", "caption"})

#: Класс-маркеры скрытости фреймворка. Внешнего CSS в дампе нет, поэтому это основной сигнал:
#: на классы приходится 4685 из 5480 скрытых совпадений, на инлайновые стили — только 795.
HIDDEN_CLASS_RE: re.Pattern[str] = re.compile(
    r"(?:^|[-_])(?:hidden|invisible)$|(?:^|[-_])(?:sr-only|visually-hidden)(?:$|[-_])",
    re.IGNORECASE,
)

#: Класс-маркеры контейнеров модалок, шторок и всплывающих окон.
MODAL_CLASS_RE: re.Pattern[str] = re.compile(
    r"(?:^|[-_])(?:modal|drawer|dialog|popconfirm|popover|notification)(?:$|[-_])",
    re.IGNORECASE,
)

#: Теги полей ввода: только им имеет смысл приписывать подпись объемлющего ``<label>``.
FORM_CONTROL_TAGS: frozenset[str] = frozenset({"input", "select", "textarea", "button"})

#: Роли контейнеров модальных окон.
MODAL_ROLES: frozenset[str] = frozenset({"dialog", "alertdialog"})

#: Генерируемые классы (styled-components, emotion) — в подсказку по классам не идут: это либо
#: префиксы sc-/css-, либо хеш без дефиса с заглавной буквой внутри (sc-ghWlax, css-rf91zg, immanA).
GENERATED_CLASS_RE: re.Pattern[str] = re.compile(r"^(?:(?:sc|css)-[A-Za-z0-9_-]+|[A-Za-z0-9]*[A-Z][A-Za-z0-9]*)$")

#: Корневой тег векторной графики: текста не даёт, в текстовый индекс не идёт.
SVG_TAGS: frozenset[str] = frozenset({"svg"})

#: Максимальная длина сохраняемого текста элемента.
MAX_TEXT_LENGTH: int = 200

#: Максимальная длина ключа текстового индекса: искать по тексту-простыне бессмысленно.
MAX_TEXT_KEY_LENGTH: int = 120

#: Причины скрытости, снимающие pw_visible (приближение Playwright is_visible()).
HARD_HIDDEN_REASONS: frozenset[str] = frozenset(
    {"attr:hidden", "attr:inert", "css:display-none", "css:visibility-hidden", "css:zero-box"}
)

_WHITESPACE_RE: re.Pattern[str] = re.compile(r"\s+")
_PX_RE: re.Pattern[str] = re.compile(r"^(-?\d+(?:\.\d+)?)\s*px$")
_SCALE_ZERO_RE: re.Pattern[str] = re.compile(r"scale(?:3d|x|y)?\(\s*0(?:\.0+)?\s*[,)]")
_CLIP_ZERO_RE: re.Pattern[str] = re.compile(r"rect\(\s*0(?:px)?[,\s]+0(?:px)?[,\s]+0(?:px)?[,\s]+0(?:px)?\s*\)")
_NEGATIVE_Z_RE: re.Pattern[str] = re.compile(r"^-\d+$")

#: Типы строковых узлов bs4, которые не являются видимым текстом.
_NON_TEXT_STRING_TYPES: tuple[type, ...] = (Comment, Declaration, Doctype, ProcessingInstruction)


@dataclass(slots=True)
class ParsedSnapshot:
    """Разобранный снимок: оба дерева и индекс элементов.

    :param snapshot: Исходный снимок из dump_parser.
    :param soup: Дерево BeautifulSoup с парсером "lxml" — по нему работает soupsieve (CSS).
    :param tree: Дерево lxml.html — по нему работает lxml.etree.XPath.
    :param index: Индекс опознаваемых элементов снимка.
    :param labels: Подписи полей: индексный путь элемента -> текст связанного ``<label>``
        (по атрибуту ``for``, по объемлющему ``<label>`` или по ``aria-labelledby``).
    """

    snapshot: Snapshot
    soup: BeautifulSoup
    tree: HtmlElement
    index: SnapshotIndex
    labels: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class _IndexState:
    """Состояние обхода дерева при построении индекса.

    :param snapshot_index: Сквозной номер снимка.
    :param index: Наполняемый индекс.
    :param labels: Итоговые подписи полей (индексный путь -> текст label).
    :param label_texts: Текст каждого встреченного ``<label>`` (ключ — id объекта узла).
    :param label_for: Текст ``<label for=...>`` по значению атрибута for.
    :param wrapping_label: Элементы внутри ``<label>``: индексный путь -> id объекта узла label.
    :param aria_labelledby: Элементы с aria-labelledby: индексный путь -> список id.
    """

    snapshot_index: int
    index: SnapshotIndex
    labels: dict[str, str] = field(default_factory=dict)
    label_texts: dict[int, str] = field(default_factory=dict)
    label_for: dict[str, str] = field(default_factory=dict)
    wrapping_label: dict[str, int] = field(default_factory=dict)
    aria_labelledby: dict[str, list[str]] = field(default_factory=dict)


def normalize_text(value: str) -> str:
    """Нормализует текст: NBSP в пробел, схлопывание пробельных символов, обрезка краёв.

    Регистр не меняется — для сравнения без учёта регистра есть :func:`text_key`.

    :param value: Исходный текст.
    :return: Нормализованный текст.
    """
    return _WHITESPACE_RE.sub(" ", value.replace(NBSP, " ")).strip()


def text_key(value: str) -> str:
    """Ключ текстового индекса.

    :param value: Исходный текст.
    :return: Нормализованный текст, приведённый через casefold.
    """
    return normalize_text(value).casefold()


def _truncate(value: str, limit: int = MAX_TEXT_LENGTH) -> str:
    """Обрезает текст до разумной длины, чтобы индекс не раздувался.

    :param value: Нормализованный текст.
    :param limit: Предельная длина.
    :return: Текст не длиннее limit (с многоточием в конце, если обрезали).
    """
    if len(value) <= limit:
        return value
    return value[: limit - 1].rstrip() + "…"


def _tag_of(node: Any) -> str | None:
    """Имя тега узла в нижнем регистре.

    :param node: Узел bs4 (Tag) или lxml (HtmlElement).
    :return: Имя тега либо None для документа, комментария и прочих не-элементов.
    """
    if isinstance(node, Tag):
        name = node.name
        if not name or name == "[document]":
            return None
        return str(name).lower()
    tag = getattr(node, "tag", None)
    if isinstance(tag, str):
        return tag.lower()
    return None


def _attrs_of(node: Any) -> dict[str, str]:
    """Атрибуты узла в виде словаря строк (значения-списки bs4 склеиваются пробелом).

    :param node: Узел bs4 или lxml.
    :return: Словарь атрибутов.
    """
    result: dict[str, str] = {}
    if isinstance(node, Tag):
        for key, value in node.attrs.items():
            if isinstance(value, (list, tuple)):
                result[str(key)] = " ".join(str(item) for item in value)
            else:
                result[str(key)] = str(value)
        return result
    for key, value in dict(getattr(node, "attrib", {})).items():
        result[str(key)] = str(value)
    return result


def _parent_of(node: Any) -> Any:
    """Родительский элемент узла.

    :param node: Узел bs4 или lxml.
    :return: Родительский элемент либо None, если узел корневой.
    """
    if isinstance(node, Tag):
        parent = node.parent
    else:
        parent = node.getparent() if hasattr(node, "getparent") else None
    if parent is None or _tag_of(parent) is None:
        return None
    return parent


def _element_children(node: Any) -> list[Any]:
    """Дочерние элементы узла (без текстовых узлов и комментариев).

    :param node: Узел bs4 или lxml.
    :return: Список дочерних элементов в порядке документа.
    """
    if isinstance(node, Tag):
        return [child for child in node.children if isinstance(child, Tag)]
    return [child for child in node if _tag_of(child) is not None]


def dom_path_of(node: object) -> str:
    """Индексный путь узла вида ``html[0]/body[0]/div[3]/button[1]``.

    Индекс — позиция среди элементов-братьев (0-based). Позиция ищется по тождеству (``is``),
    а не через ``list.index``: у bs4 ``Tag.__eq__`` сравнивает содержимое, и два одинаковых
    соседних узла дали бы один и тот же путь.

    :param node: Узел bs4 (Tag) или lxml (HtmlElement).
    :return: Индексный путь от корня документа.
    """
    parts: list[str] = []
    current: Any = node
    while current is not None:
        tag = _tag_of(current)
        if tag is None:
            break
        parent = _parent_of(current)
        if parent is None:
            parts.append(f"{tag}[0]")
            break
        position = 0
        for sibling_index, sibling in enumerate(_element_children(parent)):
            if sibling is current:
                position = sibling_index
                break
        parts.append(f"{tag}[{position}]")
        current = parent
    return "/".join(reversed(parts))


def _style_map(style: str) -> dict[str, str]:
    """Разбирает инлайновый style в словарь свойств.

    :param style: Значение атрибута style.
    :return: Словарь ``{свойство: значение}`` в нижнем регистре, без ``!important``.
    """
    result: dict[str, str] = {}
    for declaration in style.split(";"):
        if ":" not in declaration:
            continue
        name, _, value = declaration.partition(":")
        clean_name = _WHITESPACE_RE.sub(" ", name).strip().lower()
        clean_value = _WHITESPACE_RE.sub(" ", value).strip().lower().replace("!important", "").strip()
        if clean_name:
            result[clean_name] = clean_value
    return result


def _length_px(value: str) -> float | None:
    """Переводит длину вида ``0px`` в число.

    :param value: Значение CSS-свойства.
    :return: Число пикселей либо None, если значение задано не в пикселях.
    """
    match = _PX_RE.match(value.strip())
    return float(match.group(1)) if match else None


def self_hidden_reason(tag: str, attrs: Mapping[str, str]) -> str | None:
    """Причина, по которой САМ элемент не отрисован (без учёта предков).

    Порядок проверок фиксирован, побеждает первая сработавшая причина: нерендеримый тег,
    ``hidden``, ``inert``, ``display:none``, ``visibility:hidden|collapse``, нулевой бокс
    (``width:0px`` И ``height:0px`` одновременно), ``content-visibility:hidden``,
    ``transform:scale(0)``, ``clip:rect(0,0,0,0)``, ``clip-path:inset(100%``, sr-only (не больше
    1px по обеим сторонам вместе с ``overflow:hidden``), ``opacity:0`` в связке с
    ``position:fixed|absolute`` и отрицательным ``z-index``, класс-маркер :data:`HIDDEN_CLASS_RE`.

    Одиночные ``width:0px``, ``height:0px`` (134 и 155 вхождений у flex-обёрток), одиночный
    ``opacity:0`` и ``aria-hidden="true"`` признаками скрытости не являются.

    :param tag: Имя тега в нижнем регистре.
    :param attrs: Атрибуты элемента.
    :return: Строка-причина (например ``css:clip-path-inset-100`` или ``class:ant-tooltip-hidden``)
        либо None, если элемент отрисован.
    """
    if tag in NON_RENDERED_TAGS:
        return f"tag:{tag}"
    if "hidden" in attrs and attrs.get("hidden", "").strip().lower() != "false":
        return "attr:hidden"
    if "inert" in attrs and attrs.get("inert", "").strip().lower() != "false":
        return "attr:inert"

    style = _style_map(attrs.get("style", ""))
    if style.get("display") == "none":
        return "css:display-none"
    if style.get("visibility") in ("hidden", "collapse"):
        return "css:visibility-hidden"

    width = _length_px(style.get("width", ""))
    height = _length_px(style.get("height", ""))
    if width == 0 and height == 0:
        return "css:zero-box"
    if style.get("content-visibility") == "hidden":
        return "css:content-visibility-hidden"
    if _SCALE_ZERO_RE.search(style.get("transform", "")):
        return "css:transform-scale-0"
    if _CLIP_ZERO_RE.search(style.get("clip", "")):
        return "css:clip-rect-0"
    if "inset(100%" in style.get("clip-path", ""):
        return "css:clip-path-inset-100"
    if width is not None and height is not None and width <= 1 and height <= 1 and style.get("overflow") == "hidden":
        return "css:sr-only-1px"
    if (
        style.get("opacity") == "0"
        and style.get("position") in ("fixed", "absolute")
        and _NEGATIVE_Z_RE.match(style.get("z-index", ""))
    ):
        return "css:offscreen-negative-z"

    for token in attrs.get("class", "").split():
        if HIDDEN_CLASS_RE.search(token):
            return f"class:{token}"
    return None


def is_hard_reason(reason: str | None) -> bool:
    """Снимает ли причина видимость по жёсткой шкале pw_visible.

    Жёсткие причины — те, из-за которых у элемента нет бокса или он явно скрыт: нерендеримый тег,
    ``hidden``/``inert``, ``display:none``, ``visibility:hidden``, нулевой бокс. Остальные
    (clip-path, sr-only, класс-маркеры) для Playwright видимы, а для человека нет.

    :param reason: Причина из :func:`self_hidden_reason`.
    :return: True, если причина жёсткая.
    """
    if reason is None:
        return False
    return reason.startswith("tag:") or reason in HARD_HIDDEN_REASONS


def classify_visibility(node: object) -> tuple[bool, bool, str | None, bool]:
    """Классифицирует видимость элемента с учётом всех его предков.

    :param node: Узел bs4 или lxml.
    :return: Кортеж ``(pw_visible, rendered, hidden_reason, hidden_by_ancestor)``. ``pw_visible`` —
        приближение Playwright ``is_visible()``; ``rendered`` — широкая эвристика; ``hidden_reason`` —
        первая сработавшая причина (сначала на самом элементе, затем вверх по предкам);
        ``hidden_by_ancestor`` — найдена ли причина не на элементе, а на предке.
    """
    first_reason: str | None = None
    first_on_ancestor = False
    has_hard = False
    current: Any = node
    depth = 0
    while current is not None:
        tag = _tag_of(current)
        if tag is None:
            break
        reason = self_hidden_reason(tag, _attrs_of(current))
        if reason is not None:
            if first_reason is None:
                first_reason = reason
                first_on_ancestor = depth > 0
            if is_hard_reason(reason):
                has_hard = True
                break
        current = _parent_of(current)
        depth += 1
    return (not has_hard, first_reason is None, first_reason, first_on_ancestor)


def aria_hidden(node: object) -> bool:
    """Стоит ли на элементе или его предке ``aria-hidden="true"``.

    Справочный сигнал: в шкалы видимости он НЕ входит — в дампах это 558 узлов, из них 290
    ``<span>`` и 50 ``<svg>`` внутри полностью видимых кнопок. Playwright его тоже игнорирует.

    :param node: Узел bs4 или lxml.
    :return: True, если атрибут найден на элементе или выше по дереву.
    """
    current: Any = node
    while current is not None and _tag_of(current) is not None:
        if _attrs_of(current).get("aria-hidden", "").strip().lower() == "true":
            return True
        current = _parent_of(current)
    return False


def _is_interactive_raw(tag: str, attrs: Mapping[str, str]) -> bool:
    """Быстрая версия :func:`is_interactive` для уже разобранных тега и атрибутов.

    :param tag: Имя тега в нижнем регистре.
    :param attrs: Атрибуты элемента.
    :return: True, если элемент интерактивный.
    """
    if tag in INTERACTIVE_TAGS:
        return True
    return any(attr in attrs for attr in INTERACTIVE_ATTRS)


def is_interactive(node: object) -> bool:
    """Интерактивен ли элемент.

    :param node: Узел bs4 или lxml.
    :return: True для button/a/input/select/textarea/label/summary/option и для элементов
        с role/tabindex/onclick/contenteditable.
    """
    tag = _tag_of(node)
    if tag is None:
        return False
    return _is_interactive_raw(tag, _attrs_of(node))


def class_hint(element: DomElement) -> str:
    """Осмысленные классы элемента без генерируемых styled-components/emotion.

    :param element: Элемент индекса.
    :return: Строка вида ``ant-btn ant-btn-primary``; пустая строка, если осмысленных классов нет.
    """
    tokens = [token for token in element.attrs.get("class", "").split() if not GENERATED_CLASS_RE.match(token)]
    return " ".join(tokens)


def _build_dom_element(
    snapshot_index: int,
    dom_path: str,
    tag: str,
    attrs: dict[str, str],
    text: str,
    own_text: str,
    pw_visible: bool,
    rendered: bool,
    hidden_reason: str | None,
    hidden_by_ancestor: bool,
) -> DomElement:
    """Собирает :class:`~scripts.dom_inspector.models.DomElement` из уже вычисленных частей.

    :param snapshot_index: Сквозной номер снимка.
    :param dom_path: Индексный путь элемента.
    :param tag: Имя тега.
    :param attrs: Атрибуты элемента.
    :param text: Нормализованный текст поддерева.
    :param own_text: Нормализованный текст собственных текстовых узлов.
    :param pw_visible: Видимость по жёсткой шкале.
    :param rendered: Видимость по широкой шкале.
    :param hidden_reason: Причина скрытости.
    :param hidden_by_ancestor: Найдена ли причина на предке.
    :return: Готовый элемент индекса.
    """
    return DomElement(
        snapshot_index=snapshot_index,
        dom_path=dom_path,
        tag=tag,
        attrs=attrs,
        element_id=attrs.get("id"),
        test_id=attrs.get("data-testid"),
        role=attrs.get("role"),
        text=_truncate(text),
        own_text=_truncate(own_text),
        aria_label=attrs.get("aria-label"),
        title=attrs.get("title"),
        placeholder=attrs.get("placeholder"),
        name=attrs.get("name"),
        value=attrs.get("value"),
        is_interactive=_is_interactive_raw(tag, attrs),
        pw_visible=pw_visible,
        rendered=rendered,
        hidden_reason=hidden_reason,
        hidden_by_ancestor=hidden_by_ancestor,
    )


def _visible_strings(node: Tag, own_only: bool) -> Iterator[str]:
    """Видимые текстовые узлы элемента bs4.

    Комментарии, doctype и содержимое нерендеримых тегов пропускаются.

    :param node: Узел bs4.
    :param own_only: Брать только собственные текстовые узлы, без потомков.
    :return: Итератор строк.
    """
    for child in node.children:
        if isinstance(child, Tag):
            if own_only or _tag_of(child) in NON_RENDERED_TAGS:
                continue
            yield from _visible_strings(child, own_only=False)
        elif isinstance(child, NavigableString) and not isinstance(child, _NON_TEXT_STRING_TYPES):
            yield str(child)


def _lxml_text(node: Any, own_only: bool = False) -> str:
    """Видимый текст поддерева lxml без содержимого нерендеримых тегов.

    :param node: Узел lxml.
    :param own_only: Брать только собственные текстовые узлы, без потомков.
    :return: Сырой текст (нормализацию делает вызывающий).
    """
    if _tag_of(node) in NON_RENDERED_TAGS:
        return ""
    parts: list[str] = [node.text or ""]
    for child in node:
        if not own_only and _tag_of(child) is not None:
            parts.append(_lxml_text(child))
        parts.append(child.tail or "")
    return "".join(parts)


def describe_bs4_element(node: Tag, snapshot_index: int) -> DomElement:
    """Описывает узел дерева BeautifulSoup.

    :param node: Узел bs4.
    :param snapshot_index: Сквозной номер снимка.
    :return: Элемент индекса; ``dom_path`` совпадает с :func:`describe_lxml_element` для того же узла.
    """
    tag = _tag_of(node) or ""
    attrs = _attrs_of(node)
    pw_visible, rendered, reason, by_ancestor = classify_visibility(node)
    own_text = normalize_text("".join(_visible_strings(node, own_only=True)))
    text = normalize_text("".join(_visible_strings(node, own_only=False)))
    return _build_dom_element(
        snapshot_index, dom_path_of(node), tag, attrs, text, own_text, pw_visible, rendered, reason, by_ancestor
    )


def describe_lxml_element(node: HtmlElement, snapshot_index: int) -> DomElement:
    """Описывает узел дерева lxml.html.

    :param node: Узел lxml.
    :param snapshot_index: Сквозной номер снимка.
    :return: Элемент индекса; ``dom_path`` совпадает с :func:`describe_bs4_element` для того же узла.
    """
    tag = _tag_of(node) or ""
    attrs = _attrs_of(node)
    pw_visible, rendered, reason, by_ancestor = classify_visibility(node)
    own_text = normalize_text(_lxml_text(node, own_only=True))
    text = normalize_text(_lxml_text(node))
    return _build_dom_element(
        snapshot_index, dom_path_of(node), tag, attrs, text, own_text, pw_visible, rendered, reason, by_ancestor
    )


def _is_modal_container(tag: str, attrs: Mapping[str, str]) -> bool:
    """Является ли элемент контейнером модалки, шторки или всплывающего окна.

    :param tag: Имя тега.
    :param attrs: Атрибуты элемента.
    :return: True для ``<dialog>``, ``role=dialog`` и классов вида ``ant-modal-content``,
        ``ant-drawer-body``, ``ant-notification-notice``.
    """
    if tag == "dialog" or attrs.get("role", "").strip().lower() in MODAL_ROLES:
        return True
    return any(MODAL_CLASS_RE.search(token) for token in attrs.get("class", "").split())


def _is_significant(tag: str, attrs: Mapping[str, str], own_text: str, inside_modal: bool, inside_svg: bool) -> bool:
    """Стоит ли класть элемент в индекс.

    :param tag: Имя тега.
    :param attrs: Атрибуты элемента.
    :param own_text: Собственный текст элемента.
    :param inside_modal: Находится ли элемент внутри модалки/шторки.
    :param inside_svg: Находится ли элемент внутри svg.
    :return: True, если элемент опознаваемый и полезен в индексе.
    """
    if inside_svg:
        return "data-testid" in attrs or "id" in attrs
    if any(attr in attrs for attr in IDENTITY_ATTRS) or _is_interactive_raw(tag, attrs):
        return True
    if tag in HEADING_TAGS and own_text:
        return True
    if _is_modal_container(tag, attrs):
        return True
    return bool(inside_modal and own_text)


def _text_indexable(tag: str, attrs: Mapping[str, str], inside_modal: bool) -> bool:
    """Стоит ли класть элемент в текстовый индекс by_text.

    :param tag: Имя тега.
    :param attrs: Атрибуты элемента.
    :param inside_modal: Находится ли элемент внутри модалки/шторки.
    :return: True для интерактивных элементов, заголовков, элементов с data-testid и текста модалок.
    """
    if _is_interactive_raw(tag, attrs) or tag in HEADING_TAGS:
        return True
    return inside_modal or "data-testid" in attrs


def _register(state: _IndexState, element: DomElement, inside_modal: bool, inside_svg: bool) -> None:
    """Кладёт элемент в индекс и во вспомогательные словари.

    :param state: Состояние обхода.
    :param element: Элемент индекса.
    :param inside_modal: Находится ли элемент внутри модалки/шторки.
    :param inside_svg: Находится ли элемент внутри svg.
    :return: Ничего.
    """
    index = state.index
    index.elements.append(element)
    if element.test_id:
        index.by_test_id.setdefault(element.test_id, []).append(element)
    if element.element_id:
        index.by_id.setdefault(element.element_id, []).append(element)
    if inside_svg or not _text_indexable(element.tag, element.attrs, inside_modal):
        return
    for value in {element.text, element.own_text}:
        if value and len(value) <= MAX_TEXT_KEY_LENGTH:
            index.by_text.setdefault(text_key(value), []).append(element)


def _walk(
    node: Tag,
    parent_path: str,
    position: int,
    state: _IndexState,
    inherited_reason: str | None,
    inherited_hard: bool,
    inside_modal: bool,
    inside_svg: bool,
    label_node: Tag | None,
) -> str:
    """Рекурсивно обходит поддерево, наполняя индекс, и возвращает видимый текст поддерева.

    Текст считается один раз снизу вверх, видимость наследуется от предков через параметры —
    поэтому построение индекса линейно по числу узлов и не пересчитывает цепочку предков.

    :param node: Текущий узел bs4.
    :param parent_path: Индексный путь родителя.
    :param position: Позиция узла среди элементов-братьев.
    :param state: Состояние обхода.
    :param inherited_reason: Причина скрытости, унаследованная от предков.
    :param inherited_hard: Есть ли среди предков жёсткая причина скрытости.
    :param inside_modal: Находится ли узел внутри модалки/шторки.
    :param inside_svg: Находится ли узел внутри svg.
    :param label_node: Ближайший объемлющий ``<label>``.
    :return: Сырой (ненормализованный) видимый текст поддерева.
    """
    tag = _tag_of(node) or ""
    attrs = _attrs_of(node)
    path = f"{parent_path}/{tag}[{position}]" if parent_path else f"{tag}[{position}]"
    state.index.element_count += 1

    own_reason = self_hidden_reason(tag, attrs)
    reason = inherited_reason if inherited_reason is not None else own_reason
    by_ancestor = inherited_reason is not None
    hard = inherited_hard or is_hard_reason(own_reason)
    node_is_svg = inside_svg or tag in SVG_TAGS
    node_in_modal = inside_modal or _is_modal_container(tag, attrs)
    next_label = node if tag == "label" else label_node

    own_parts: list[str] = []
    text_parts: list[str] = []
    child_position = 0
    for child in node.children:
        if isinstance(child, Tag):
            child_text = _walk(
                child,
                path,
                child_position,
                state,
                inherited_reason=reason,
                inherited_hard=hard,
                inside_modal=node_in_modal,
                inside_svg=node_is_svg,
                label_node=next_label,
            )
            child_position += 1
            text_parts.append(child_text)
        elif isinstance(child, NavigableString) and not isinstance(child, _NON_TEXT_STRING_TYPES):
            own_parts.append(str(child))
            text_parts.append(str(child))

    own_text = normalize_text("".join(own_parts))
    subtree_text = "".join(text_parts)

    if tag == "label":
        label_text = normalize_text(subtree_text)
        state.label_texts[id(node)] = label_text
        for_value = attrs.get("for")
        if for_value:
            state.label_for.setdefault(for_value, label_text)

    if _is_significant(tag, attrs, own_text, node_in_modal, node_is_svg):
        element = _build_dom_element(
            state.snapshot_index,
            path,
            tag,
            attrs,
            normalize_text(subtree_text),
            own_text,
            not hard,
            reason is None,
            reason,
            by_ancestor,
        )
        _register(state, element, node_in_modal, node_is_svg)
        if label_node is not None and tag in FORM_CONTROL_TAGS:
            state.wrapping_label[path] = id(label_node)
        labelled_by = attrs.get("aria-labelledby")
        if labelled_by:
            state.aria_labelledby[path] = labelled_by.split()

    return "" if tag in NON_RENDERED_TAGS else subtree_text


def _attach_labels(state: _IndexState) -> None:
    """Достраивает подписи полей после обхода дерева.

    Порядок источников: объемлющий ``<label>`` (только для полей ввода — иначе подпись достанется
    и самому тексту подписи), затем ``<label for=id>``, затем ``aria-labelledby``.

    :param state: Состояние обхода.
    :return: Ничего.
    """
    for element in state.index.elements:
        path = element.dom_path
        wrapping = state.wrapping_label.get(path)
        if wrapping is not None and state.label_texts.get(wrapping):
            state.labels[path] = state.label_texts[wrapping]
            continue
        if element.element_id and element.element_id in state.label_for:
            state.labels[path] = state.label_for[element.element_id]
            continue
        referenced = state.aria_labelledby.get(path)
        if not referenced:
            continue
        texts = [state.index.by_id[ref][0].text for ref in referenced if state.index.by_id.get(ref)]
        joined = normalize_text(" ".join(item for item in texts if item))
        if joined:
            state.labels[path] = joined


def _index_snapshot(snapshot: Snapshot, soup: BeautifulSoup) -> _IndexState:
    """Один проход по дереву: индекс элементов и подписи полей.

    :param snapshot: Снимок, к которому относится дерево.
    :param soup: Дерево BeautifulSoup.
    :return: Состояние обхода с наполненными индексом и подписями.
    """
    state = _IndexState(snapshot_index=snapshot.index, index=SnapshotIndex(snapshot_index=snapshot.index))
    position = 0
    for child in soup.children:
        if isinstance(child, Tag):
            _walk(
                child,
                "",
                position,
                state,
                inherited_reason=None,
                inherited_hard=False,
                inside_modal=False,
                inside_svg=False,
                label_node=None,
            )
            position += 1
    _attach_labels(state)
    return state


def build_index(snapshot: Snapshot, soup: BeautifulSoup) -> SnapshotIndex:
    """Строит индекс опознаваемых элементов снимка одним проходом по дереву.

    :param snapshot: Снимок, к которому относится дерево.
    :param soup: Дерево BeautifulSoup, построенное парсером "lxml".
    :return: Индекс снимка. ``element_count`` — общее число узлов документа, ``elements`` — только
        отобранные опознаваемые элементы (обычные ``div`` без атрибутов и текста в индекс не идут).
    """
    return _index_snapshot(snapshot, soup).index


def parse_snapshot(snapshot: Snapshot) -> ParsedSnapshot:
    """Разбирает снимок: строит оба дерева из одной строки и индекс элементов.

    Единственная точка парсинга HTML в пакете: снимки бывают по мегабайту, повторно один и тот же
    снимок парсить нельзя.

    :param snapshot: Снимок из dump_parser.
    :return: Контейнер с деревьями и индексом.
    :raises ValueError: Если снимок пустой и дерево строить не из чего.
    """
    if not snapshot.html.strip():
        raise ValueError(f"Пустой снимок: {snapshot.address}")
    soup = BeautifulSoup(snapshot.html, "lxml")
    tree = lxml.html.document_fromstring(snapshot.html)
    state = _index_snapshot(snapshot, soup)
    return ParsedSnapshot(snapshot=snapshot, soup=soup, tree=tree, index=state.index, labels=state.labels)


def parse_snapshots(snapshots: Iterable[Snapshot]) -> list[ParsedSnapshot]:
    """Разбирает несколько снимков подряд.

    :param snapshots: Снимки из dump_parser.
    :return: Список разобранных снимков в том же порядке.
    """
    return [parse_snapshot(snapshot) for snapshot in snapshots]


def duplicate_test_ids(index: SnapshotIndex) -> dict[str, int]:
    """data-testid, встречающиеся в снимке более одного раза.

    Прямой сигнал риска strict mode: Playwright считает все совпадения независимо от видимости.

    :param index: Индекс снимка.
    :return: Словарь ``data-testid -> количество``, отсортированный по убыванию количества.
    """
    duplicates = {key: len(items) for key, items in index.by_test_id.items() if len(items) > 1}
    return dict(sorted(duplicates.items(), key=lambda item: (-item[1], item[0])))


def find_by_text(index: SnapshotIndex, text: str, exact: bool = True, limit: int = 0) -> list[DomElement]:
    """Ищет элементы по видимому тексту.

    :param index: Индекс снимка.
    :param text: Искомый текст (регистр, NBSP и лишние пробелы не важны).
    :param exact: True — точное совпадение по ключу, False — поиск по подстроке.
    :param limit: Максимум результатов; 0 — без ограничения.
    :return: Найденные элементы в порядке обхода документа.
    """
    wanted = text_key(text)
    if exact:
        found = list(index.by_text.get(wanted, []))
    else:
        found = [element for key, items in index.by_text.items() if wanted in key for element in items]
    return found[:limit] if limit else found


def find_by_attr_substring(
    index: SnapshotIndex,
    needle: str,
    attrs: Sequence[str] = ("data-testid", "id"),
    limit: int = 0,
) -> list[DomElement]:
    """Ищет элементы по подстроке значения атрибута.

    :param index: Индекс снимка.
    :param needle: Искомая подстрока (регистр не важен).
    :param attrs: Атрибуты, в которых искать.
    :param limit: Максимум результатов; 0 — без ограничения.
    :return: Найденные элементы в порядке обхода документа.
    """
    wanted = needle.casefold()
    found = [
        element for element in index.elements if any(wanted in element.attrs.get(attr, "").casefold() for attr in attrs)
    ]
    return found[:limit] if limit else found


def find_by_tag(index: SnapshotIndex, tag: str, limit: int = 0) -> list[DomElement]:
    """Ищет элементы по имени тега.

    :param index: Индекс снимка.
    :param tag: Имя тега (регистр не важен).
    :param limit: Максимум результатов; 0 — без ограничения.
    :return: Найденные элементы в порядке обхода документа.
    """
    wanted = tag.strip().lower()
    found = [element for element in index.elements if element.tag == wanted]
    return found[:limit] if limit else found


def find_by_role(index: SnapshotIndex, role: str, limit: int = 0) -> list[DomElement]:
    """Ищет элементы по значению атрибута role.

    :param index: Индекс снимка.
    :param role: Значение role (регистр не важен).
    :param limit: Максимум результатов; 0 — без ограничения.
    :return: Найденные элементы в порядке обхода документа.
    """
    wanted = role.strip().casefold()
    found = [element for element in index.elements if (element.role or "").casefold() == wanted]
    return found[:limit] if limit else found
