"""Бизнес-состояние страницы по снимку DOM и сверка его с ожиданием шага.

Проверка локаторов отвечает на вопрос «селектор находится?». Этого мало: тест может пройти
по зелёному, а бизнес-результат шага не наступить — договор не сменил статус, модалка открылась
не та, клиент остался в прежнем состоянии. Этот модуль отвечает на второй вопрос:
«что на странице после шага и совпадает ли это с тем, что шаг обещает».

Ожидания берутся из текста самого шага: всё, что автор написал в кавычках, — это и есть
ожидаемое значение. Для шага::

    with allure.step("Договор создан в статусе 'Оформлен', клиент остался в статусе 'Потенциальный'")

ожидания — «Оформлен» и «Потенциальный»; модуль ищет их в тексте снимка и сообщает,
какое из них на странице не подтвердилось.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Sequence

from scripts.dom_inspector.element_index import normalize_text

if TYPE_CHECKING:
    from scripts.dom_inspector.element_index import ParsedSnapshot
    from scripts.dom_inspector.models import DomElement

QUOTED_RE = re.compile(r"[«'\"]([^«»'\"]{2,60})[»'\"]")
STATUS_WORDS = ("Потенциальный", "Действующий", "Оформлен", "Закрыт", "Расторгнут", "Заблокирован")
IGNORED_EXPECTATIONS = frozenset({"Далее", "Создать", "Сохранить", "Закрыть", "Отмена", "Добавить"})
ACTION_VERBS = (
    "нажать",
    "нажмите",
    "заполнить",
    "выбрать",
    "загрузить",
    "указать",
    "ввести",
    "открыть",
    "перейти",
    "кликнуть",
    "отредактировать",
    "изменить",
    "сохранить",
)
ACTION_LOOKBEHIND = 40

TAG_SELECTOR = "[class*=tag]"
MODAL_TITLE_SELECTOR = "[class*=modal-title]"
MODAL_BODY_SELECTOR = "[class*=modal-body]"
DRAWER_TITLE_SELECTOR = "[class*=drawer-open] [class*=drawer-title]"
HEADING_SELECTOR = "h3[class*=title], h3[class*=summary]"
ACTIVE_TAB_SELECTOR = "[role=tab][aria-selected=true]"

MAX_ITEMS = 4
MAX_VALUE = 60


@dataclass(slots=True)
class SnapshotState:
    """Краткий слепок бизнес-состояния одного снимка.

    :param heading: Заголовок карточки или страницы.
    :param statuses: Тексты статус-тегов (Оформлен, Действующий и т.п.).
    :param modal_title: Заголовок открытого модального окна, если оно есть.
    :param modal_body: Текст модального окна.
    :param drawer_title: Заголовок открытой боковой формы.
    :param active_tab: Название активной вкладки.
    """

    heading: str | None = None
    statuses: list[str] = field(default_factory=list)
    modal_title: str | None = None
    modal_body: str | None = None
    drawer_title: str | None = None
    active_tab: str | None = None

    def as_line(self) -> str:
        """Собирает слепок в одну строку для отчёта.

        :return: Строка вида "карточка «...» · статусы: ... · модалка «...»"; пустая, если ничего не опознано.
        """
        parts: list[str] = []
        if self.heading:
            parts.append(f"карточка «{_cut(self.heading)}»")
        if self.active_tab:
            parts.append(f"вкладка «{_cut(self.active_tab)}»")
        if self.statuses:
            parts.append("статусы: " + ", ".join(_cut(value) for value in self.statuses[:MAX_ITEMS]))
        if self.modal_title:
            parts.append(f"модалка «{_cut(self.modal_title)}»")
        if self.drawer_title:
            parts.append(f"форма «{_cut(self.drawer_title)}»")
        return " · ".join(parts)


@dataclass(slots=True)
class Expectation:
    """Ожидание шага и результат его сверки со снимком.

    :param value: Ожидаемое значение из текста шага.
    :param found: Найдено ли значение в тексте снимков шага.
    :param where: Как именно найдено: статус, модалка, текст страницы.
    """

    value: str
    found: bool
    where: str | None = None


def _cut(value: str, limit: int = MAX_VALUE) -> str:
    """Обрезает значение до разумной длины для отчёта.

    :param value: Исходная строка.
    :param limit: Предельная длина.
    :return: Строка не длиннее limit.
    """
    text = normalize_text(value)
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _first_text(parsed: ParsedSnapshot, selector: str) -> str | None:
    """Возвращает текст первого видимого элемента по CSS-селектору.

    :param parsed: Разобранный снимок.
    :param selector: CSS-селектор.
    :return: Текст или None, если ничего не нашлось.
    """
    for node in parsed.soup.select(selector):
        text = normalize_text(node.get_text(" ", strip=True))
        if text:
            return text
    return None


def _all_texts(parsed: ParsedSnapshot, selector: str) -> list[str]:
    """Возвращает непустые тексты всех элементов по CSS-селектору без повторов.

    :param parsed: Разобранный снимок.
    :param selector: CSS-селектор.
    :return: Список текстов в порядке документа.
    """
    seen: list[str] = []
    for node in parsed.soup.select(selector):
        text = normalize_text(node.get_text(" ", strip=True))
        if text and text not in seen:
            seen.append(text)
    return seen


def describe_snapshot(parsed: ParsedSnapshot) -> SnapshotState:
    """Собирает слепок бизнес-состояния снимка.

    :param parsed: Разобранный снимок.
    :return: Слепок состояния.
    """
    return SnapshotState(
        heading=_first_text(parsed, HEADING_SELECTOR),
        statuses=_all_texts(parsed, TAG_SELECTOR),
        modal_title=_first_text(parsed, MODAL_TITLE_SELECTOR),
        modal_body=_first_text(parsed, MODAL_BODY_SELECTOR),
        drawer_title=_first_text(parsed, DRAWER_TITLE_SELECTOR),
        active_tab=_first_text(parsed, ACTIVE_TAB_SELECTOR),
    )


def expectations_from_step(title: str) -> list[str]:
    """Достаёт из текста шага значения, которые шаг обещает увидеть на странице.

    Берётся то, что автор шага написал в кавычках, плюс известные бизнес-статусы,
    даже если они написаны без кавычек. Названия кнопок отбрасываются: «Нажать "Далее"» —
    это действие, а не ожидаемое состояние.

    :param title: Текст шага из allure.step.
    :return: Список ожидаемых значений без повторов, в порядке появления.
    """
    found: list[str] = []
    for match in QUOTED_RE.finditer(title):
        value = normalize_text(match.group(1))
        if not value or value in found or value in IGNORED_EXPECTATIONS:
            continue
        if _is_action_target(title, match.start()):
            continue
        found.append(value)
    for word in STATUS_WORDS:
        if word in title and word not in found:
            found.append(word)
    return found


def _is_action_target(title: str, quote_start: int) -> bool:
    """Проверяет, что закавыченное значение — это то, на что жмут, а не ожидаемый результат.

    «Нажать 'Подписать договор'» — действие, состояния страницы оно не описывает;
    «в статусе 'Оформлен'» — ожидание. Отличаем по глаголу слева от кавычки.

    :param title: Текст шага.
    :param quote_start: Позиция открывающей кавычки.
    :return: True, если значение относится к действию.
    """
    left = title[max(0, quote_start - ACTION_LOOKBEHIND) : quote_start].casefold()
    tail = left.rsplit(",", 1)[-1].rsplit(";", 1)[-1]
    return any(verb in tail for verb in ACTION_VERBS)


def check_expectations(title: str, snapshots: Sequence[ParsedSnapshot]) -> list[Expectation]:
    """Сверяет ожидания шага с содержимым его снимков.

    :param title: Текст шага.
    :param snapshots: Снимки, привязанные к шагу.
    :return: Список ожиданий с отметкой, подтвердилось ли каждое.
    """
    values = expectations_from_step(title)
    if not values or not snapshots:
        return [Expectation(value=value, found=False, where=None) for value in values] if not snapshots else []
    results: list[Expectation] = []
    for value in values:
        where = _locate(value, snapshots)
        results.append(Expectation(value=value, found=where is not None, where=where))
    return results


def _locate(value: str, snapshots: Sequence[ParsedSnapshot]) -> str | None:
    """Ищет значение в снимках и говорит, в какой части страницы оно нашлось.

    :param value: Искомое значение.
    :param snapshots: Снимки шага.
    :return: Где нашлось ("статус", "модалка", "на странице") или None.
    """
    needle = value.casefold()
    for parsed in snapshots:
        state = describe_snapshot(parsed)
        if any(needle == status.casefold() for status in state.statuses):
            return "статус"
        if state.modal_title and needle in state.modal_title.casefold():
            return "заголовок модалки"
        if state.modal_body and needle in state.modal_body.casefold():
            return "текст модалки"
        if _in_elements(needle, parsed):
            return "на странице"
    return None


def _in_elements(needle: str, parsed: ParsedSnapshot) -> bool:
    """Проверяет наличие значения среди текстов и значений полей снимка.

    Ищем по индексу элементов, а не по сырому HTML: совпадение в имени класса
    или в служебном атрибуте — не подтверждение того, что человек увидел это на экране.

    :param needle: Искомое значение в нижнем регистре.
    :param parsed: Разобранный снимок.
    :return: True, если значение видно на странице.
    """
    for element in parsed.index.elements:
        if _element_matches(needle, element):
            return True
    return False


def _element_matches(needle: str, element: DomElement) -> bool:
    """Проверяет один элемент на совпадение с искомым значением.

    :param needle: Искомое значение в нижнем регистре.
    :param element: Элемент снимка.
    :return: True, если совпало по тексту, значению поля, подписи или заголовку.
    """
    if not element.rendered:
        return False
    for candidate in (element.own_text, element.value, element.aria_label, element.title, element.placeholder):
        if candidate and needle in candidate.casefold():
            return True
    return False
