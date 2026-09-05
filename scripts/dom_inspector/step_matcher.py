"""Пошаговый разбор: сшивка снимков DOM с шагами конкретного теста и короткий отчёт по ним.

Модуль отвечает на вопрос «на каком шаге теста какой локатор не находится», а не на вопрос
«какие локаторы репозитория плохи вообще» — этим занимается подкоманда ``check``. Набор
проверяемых локаторов приходит из :mod:`scripts.dom_inspector.step_collector`, который
статически разбирает тело теста, и ограничен ровно тем, до чего дотягивается разобранный тест.

Что делает модуль:

* достаёт из дампа снимки нужного кейса и номера шагов, если человек их проставил;
* раскладывает снимки по шагам (явная разметка, иначе по порядку с честной пометкой «угадано»);
* гоняет локаторы шага по снимкам шага через готовый :func:`locator_checker.check_locators`;
* рендерит отчёт, где зелёный шаг занимает одну строку, а разворачивается только проблемный.

Формат пошагового дампа — старый плюс одна необязательная строка с номером шага перед снимком::

    case 15:
    2
    <body ...>...</body>
    4
    <body ...>...</body>

Распознаются написания ``3``, ``3:``, ``шаг 3``, ``step 3``, а также строка с текстом шага.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from scripts.dom_inspector.element_index import ParsedSnapshot, parse_snapshot
from scripts.dom_inspector.locator_checker import check_locators, reset_caches
from scripts.dom_inspector.models import (
    DumpDocument,
    InspectionOptions,
    LocatorCheckResult,
    LocatorRecord,
    MatchStatus,
    ReplacementCandidate,
    Snapshot,
)

#: Строка-номер шага перед снимком: ``3``, ``3:``, ``шаг 3``, ``step 3``.
#: Правило намеренно жёсткое — строка должна состоять только из номера, иначе любая
#: человеческая пометка с цифрой («14 кейсов проверено») стала бы номером шага.
STEP_MARKER_RE: re.Pattern[str] = re.compile(r"^\s*(?:шаг|step)?\s*[:.\-]?\s*(\d{1,3})\s*[:.\-)]?\s*$", re.IGNORECASE)

#: Номер кейса в начале заголовка allure: ``15. Перевод клиента ...``.
TITLE_CASE_RE: re.Pattern[str] = re.compile(r"^\s*(\d+)\s*[.)]")

#: Номер псевдо-шага для кода теста, который лежит вне блоков ``allure.step``.
OUTSIDE_STEP_NUMBER: int = 0

#: Сколько символов селектора печатать в строке проблемы.
MAX_SELECTOR_LENGTH: int = 62

#: Сколько символов заголовка шага печатать в сводной строке.
MAX_TITLE_LENGTH: int = 96

#: Ширина колонки со снимками в строке шага.
SNAPSHOT_COLUMN_WIDTH: int = 12

#: Ширина колонки с результатом в строке шага.
RESULT_COLUMN_WIDTH: int = 10

#: Минимальная ширина колонки с именем атрибута в строке проблемы.
MIN_ATTR_COLUMN_WIDTH: int = 26

#: С какого числа локаторов шаг, где не нашлось вообще ничего, сворачивается в две строки.
COLLAPSE_THRESHOLD: int = 3

#: Доля найденных локаторов, ниже которой шаг подозревается в том, что снимок ему достался чужой.
#: Не «не нашлось совсем ничего»: на снимке любого экрана карточки клиента находится CLIENT_STATUS
#: из шапки, и одного такого паразитного совпадения хватало, чтобы защита от сдвига выключилась.
SHIFT_SUSPECT_RATIO: float = 0.25

#: Сколько проблемных локаторов разворачивать на шаге без ключа -v. Один allure.step умеет
#: тянуть под сотню локаторов (шаг «создана продажа» — 58), и печатать их подряд бессмысленно:
#: отчёт перестаёт читаться за десять секунд, ради чего он и делался.
MAX_PROBLEMS_PER_STEP: int = 8

#: Сколько заметок разбора печатать на шаге без ключа -v.
MAX_GAPS_PER_STEP: int = 3

#: Признаки кандидата, которого показывать нельзя: слабое совпадение и неоднозначный селектор.
WEAK_CANDIDATE_MARKERS: tuple[str, ...] = ("осторожно:", "текст похож на описание")

#: Статусы, при которых локатор в снимке не найден.
BROKEN_STATUSES: frozenset[MatchStatus] = frozenset({MatchStatus.NOT_FOUND, MatchStatus.COMPILE_ERROR})

#: Статусы, при которых локатор нашёлся, но не один раз, — селектор ловит не тот элемент.
AMBIGUOUS_STATUSES: frozenset[MatchStatus] = frozenset({MatchStatus.MULTIPLE_VISIBLE, MatchStatus.UNIQUE_VISIBLE})

#: Статусы, которые статически не проверяются: относительные и playwright-специфичные селекторы.
SKIPPED_STATUSES: frozenset[MatchStatus] = frozenset({MatchStatus.NOT_CHECKED})


def _field_value(source: object, names: tuple[str, ...], default: Any = None) -> Any:
    """Читает первое непустое поле объекта из списка допустимых имён.

    Структуры ``TestCase`` и ``TestStep`` живут в соседнем модуле, поэтому доступ к полям
    намеренно терпимый: отчёт не должен падать из-за того, что поле названо ``label``,
    а не ``title``.

    :param source: Объект-источник (тест или шаг).
    :param names: Имена полей в порядке предпочтения.
    :param default: Значение, если ни одно поле не найдено.
    :return: Значение поля либо ``default``.
    """
    for name in names:
        value = getattr(source, name, None)
        if value is not None:
            return value
    return default


def test_name(test: object) -> str:
    """Имя тестового метода.

    :param test: Объект теста из ``step_collector``.
    :return: Имя метода, например ``test_organization_transition_from_potential_to_active``.
    """
    return str(_field_value(test, ("name", "test_name", "method"), "<без имени>"))


def test_title(test: object) -> str:
    """Заголовок теста из ``@allure.title``.

    :param test: Объект теста.
    :return: Заголовок либо пустая строка.
    """
    return str(_field_value(test, ("allure_title", "title"), ""))


def test_allure_id(test: object) -> str | None:
    """Идентификатор теста из ``@allure.id``.

    :param test: Объект теста.
    :return: Строковый идентификатор либо None.
    """
    value = _field_value(test, ("allure_id", "allure_number"))
    return None if value is None else str(value)


def test_case_no(test: object) -> int | None:
    """Номер кейса: из поля объекта либо из числа в начале заголовка allure.

    Именно это число совпадает с маркером ``case 15:`` в дампе.

    :param test: Объект теста.
    :return: Номер кейса либо None, если заголовок без номера.
    """
    value = _field_value(test, ("case_no", "case_number"))
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    match = TITLE_CASE_RE.match(test_title(test))
    return int(match.group(1)) if match is not None else None


def test_origin(test: object) -> str:
    """Адрес объявления теста для шапки отчёта.

    :param test: Объект теста.
    :return: Строка вида ``tests/nbss/.../test_client_status_transition.py:31`` либо пустая строка.
    """
    path = _field_value(test, ("file", "path"))
    if path is None:
        return ""
    line = _field_value(test, ("line", "lineno"))
    text = str(path).replace("\\", "/")
    return f"{text}:{line}" if line else text


def test_skip_reason(test: object) -> str | None:
    """Причина пропуска теста, если на нём висит ``@pytest.mark.skip``.

    :param test: Объект теста.
    :return: Текст причины, пустая строка при пропуске без причины, None — тест не пропущен.
    """
    reason = _field_value(test, ("skip_reason",))
    if reason is not None:
        return str(reason)
    return "" if bool(_field_value(test, ("skipped", "is_skipped"), False)) else None


def test_steps(test: object) -> list[object]:
    """Шаги теста в порядке их следования в исходнике.

    :param test: Объект теста.
    :return: Список объектов шагов; пустой список, если шагов нет.
    """
    return list(_field_value(test, ("steps",), []) or [])


def step_number(step: object, fallback: int) -> int:
    """Номер шага.

    :param step: Объект шага.
    :param fallback: Номер по порядку, если поле не задано.
    :return: Номер шага; 0 — псевдо-шаг с кодом вне ``allure.step``.
    """
    value = _field_value(step, ("number", "index"))
    return int(value) if isinstance(value, int) else fallback


def step_title(step: object) -> str:
    """Текст шага из ``allure.step``.

    :param step: Объект шага.
    :return: Текст шага либо ``[вне шагов]`` для псевдо-шага.
    """
    return str(_field_value(step, ("label", "title", "text"), "[вне шагов]"))


def step_gaps(step: object) -> list[str]:
    """Заметки разбора шага: неразрешённые обращения, предел глубины, рекурсия.

    Невычисленные ветки сюда не попадают: они не пробел разбора, а честная пометка,
    и её носят сами локаторы (``conditional``).

    :param step: Объект шага.
    :return: Список готовых строк для отчёта.
    """
    notes: list[str] = []
    for gap in _field_value(step, ("gaps", "warnings", "notes"), []) or []:
        if isinstance(gap, str):
            notes.append(gap)
            continue
        if not bool(_field_value(gap, ("is_blocking",), True)):
            continue
        notes.append(str(_field_value(gap, ("message", "reason"), gap)))
    return notes


@dataclass(slots=True)
class StepLocator:
    """Обращение шага к одному локатору.

    :param record: Запись локатора из ``locator_collector``.
    :param conditional: Обращение лежит в ветке ``if``, условие которой статически не вычислено:
        такой локатор законно может отсутствовать в DOM, красным его красить нельзя.
    :param subscripted: Обращение по индексу (``ROWS[2]``): сверять надо количество, а не единственность.
    """

    record: LocatorRecord
    conditional: bool = False
    subscripted: bool = False


def step_locators(step: object) -> list[StepLocator]:
    """Локаторы шага в порядке первого обращения, без повторов.

    :param step: Объект шага.
    :return: Список обращений; пустой список, если шаг DOM не трогает.
    """
    raw = _field_value(step, ("uses", "locators", "records"), []) or []
    items: list[StepLocator] = []
    seen: set[tuple[str, str]] = set()
    for entry in raw:
        record = entry if isinstance(entry, LocatorRecord) else _field_value(entry, ("record", "locator"))
        if not isinstance(record, LocatorRecord):
            continue
        key = (record.class_name, record.attr)
        if key in seen:
            continue
        seen.add(key)
        items.append(
            StepLocator(
                record=record,
                conditional=bool(_field_value(entry, ("conditional",), False)),
                subscripted=bool(_field_value(entry, ("subscripted",), False)),
            )
        )
    return items


def match_tests(tests: list[object], query: str) -> list[object]:
    """Отбирает тесты по строке ``--test``.

    Запасной отбор на случай, если в ``step_collector`` нет своего: принимает номер кейса,
    allure.id, подстроку имени метода и подстроку заголовка.

    :param tests: Все тесты сьюта.
    :param query: Строка запроса.
    :return: Кандидаты в порядке объявления; пустой список, если не нашлось.
    """
    wanted = query.strip()
    if not wanted:
        return list(tests)
    if wanted.isdigit():
        hits = [item for item in tests if test_case_no(item) == int(wanted) or test_allure_id(item) == wanted]
        if hits:
            return hits
    needle = wanted.casefold()
    return [item for item in tests if needle in test_name(item).casefold() or needle in test_title(item).casefold()]


def parse_step_marker(text: str) -> int | None:
    """Распознаёт строку-номер шага перед снимком.

    :param text: Текст пометки из дампа.
    :return: Номер шага либо None, если строка номером не является.
    """
    match = STEP_MARKER_RE.match(text)
    return int(match.group(1)) if match is not None else None


def _normalize(text: str) -> str:
    """Нормализует строку для нечёткого сравнения текста шага с пометкой в дампе.

    :param text: Исходный текст.
    :return: Текст без кавычек и лишних пробелов в нижнем регистре.
    """
    cleaned = re.sub(r"[\"'«»`]+", " ", text)
    return re.sub(r"\s+", " ", cleaned).strip().casefold()


def snapshot_step_numbers(document: DumpDocument, case_no: int | None, titles: dict[int, str]) -> dict[int, int]:
    """Сопоставляет снимкам номера шагов по разметке дампа.

    Номер берётся из строки-пометки, стоящей перед снимком: либо это число (``3``, ``шаг 3``),
    либо текст шага, совпавший с заголовком ``allure.step`` — алиас на случай, если человеку
    удобнее скопировать текст.

    :param document: Разобранный дамп.
    :param case_no: Номер кейса, снимки которого нас интересуют; None — весь дамп.
    :param titles: Заголовки шагов по их номерам — для распознавания текстового алиаса.
    :return: Отображение «сквозной номер снимка -> номер шага» только для размеченных снимков.
    """
    by_title = {_normalize(title): number for number, title in titles.items() if title}
    marks: dict[int, int] = {}
    for block in document.blocks:
        if case_no is not None and block.case_no != case_no:
            continue
        events: list[tuple[int, int, object]] = []
        events.extend((note.line, 0, note) for note in block.notes)
        events.extend((snapshot.start_line, 1, snapshot) for snapshot in block.snapshots)
        pending: int | None = None
        for _, _, item in sorted(events, key=lambda event: (event[0], event[1])):
            if isinstance(item, Snapshot):
                if pending is not None:
                    marks[item.index] = pending
                    pending = None
                continue
            text = str(getattr(item, "text", ""))
            number = parse_step_marker(text)
            if number is None:
                number = by_title.get(_normalize(text))
            if number is not None:
                pending = number
    return marks


@dataclass(slots=True)
class StepBinding:
    """Шаг теста вместе с привязанными к нему снимками.

    :param number: Номер шага; 0 — псевдо-шаг с кодом вне ``allure.step``.
    :param title: Текст шага.
    :param locators: Обращения к локаторам в порядке первого обращения.
    :param snapshots: Снимки, отнесённые к шагу; пустой список — снимка нет.
    :param guessed: True, если привязка угадана по порядку, а не взята из разметки дампа.
    :param gaps: Заметки разбора шага из ``step_collector``.
    """

    number: int
    title: str
    locators: list[StepLocator] = field(default_factory=list)
    snapshots: list[Snapshot] = field(default_factory=list)
    guessed: bool = False
    gaps: list[str] = field(default_factory=list)

    @property
    def has_dom(self) -> bool:
        """Трогает ли шаг DOM.

        :return: True, если у шага есть хотя бы одно обращение к локатору.
        """
        return bool(self.locators)


@dataclass(slots=True)
class StepCheck:
    """Результат проверки одного локатора шага.

    :param locator: Обращение шага к локатору.
    :param check: Итог прогона селектора по снимкам шага.
    """

    locator: StepLocator
    check: LocatorCheckResult

    @property
    def missing(self) -> bool:
        """Локатор в снимках шага не найден.

        :return: True для «не найден» и «селектор не компилируется».
        """
        return self.check.status in BROKEN_STATUSES

    @property
    def broken(self) -> bool:
        """Ненайденный локатор, который нельзя списать на невычисленную ветку.

        :return: True, если локатор не найден и обращение к нему безусловное.
        """
        return self.missing and not self.locator.conditional

    @property
    def ambiguous(self) -> bool:
        """Селектор нашёлся больше одного раза там, где ожидался один элемент.

        :return: True, если совпадений несколько и локатор не списочный.
        """
        if self.check.status not in AMBIGUOUS_STATUSES:
            return False
        return not (self.locator.record.is_list or self.locator.subscripted)

    @property
    def skipped(self) -> bool:
        """Селектор статически не проверяется.

        :return: True для относительных и playwright-специфичных селекторов.
        """
        return self.check.status in SKIPPED_STATUSES


@dataclass(slots=True)
class StepOutcome:
    """Результат проверки одного шага по его снимкам.

    :param binding: Шаг и его снимки.
    :param checks: Результаты по локаторам шага в порядке обращения.
    :param shift_hint: Текст подсказки о сдвиге разметки; пустая строка — сдвиг не заподозрен.
    """

    binding: StepBinding
    checks: list[StepCheck] = field(default_factory=list)
    shift_hint: str = ""

    @property
    def broken(self) -> list[StepCheck]:
        """Безусловные локаторы шага, которых в снимке нет.

        :return: Список результатов, роняющих код возврата.
        """
        return [item for item in self.checks if item.broken]

    @property
    def conditional_missing(self) -> list[StepCheck]:
        """Ненайденные локаторы из невычисленных веток ``if``.

        :return: Список результатов, которые красным красить нельзя.
        """
        return [item for item in self.checks if item.missing and item.locator.conditional]

    @property
    def ambiguous(self) -> list[StepCheck]:
        """Локаторы шага, нашедшиеся больше одного раза.

        :return: Список результатов с риском strict mode.
        """
        return [item for item in self.checks if item.ambiguous]

    @property
    def not_checked(self) -> list[StepCheck]:
        """Локаторы, которые статически не проверяются.

        :return: Список результатов со статусом «не проверен».
        """
        return [item for item in self.checks if item.skipped]

    @property
    def problems(self) -> list[StepCheck]:
        """Всё, что разворачивается в отчёте: сначала ненайденные, потом неоднозначные.

        :return: Список результатов для подробного вывода.
        """
        return [*self.broken, *self.ambiguous]

    @property
    def checkable(self) -> int:
        """Сколько локаторов шага реально проверялось.

        :return: Число локаторов без учёта непроверяемых селекторов.
        """
        return len(self.checks) - len(self.not_checked)

    @property
    def found(self) -> int:
        """Сколько локаторов шага нашлось в снимках шага.

        :return: Число проверенных локаторов с хотя бы одним совпадением.
        """
        return sum(1 for item in self.checks if not item.missing and not item.skipped)


@dataclass(slots=True)
class ExtraSnapshot:
    """Снимок, который не лёг ни на один шаг.

    :param snapshot: Сам снимок.
    :param found: Сколько локаторов теста в нём нашлось.
    :param total: Сколько локаторов теста проверялось.
    :param reason: Почему снимок оказался лишним.
    """

    snapshot: Snapshot
    found: int
    total: int
    reason: str


@dataclass(slots=True)
class StepsReport:
    """Итог пошагового разбора одного теста.

    :param dump_path: Путь к разобранному дампу.
    :param case_no: Номер кейса, снимки которого разбирались.
    :param name: Имя тестового метода.
    :param title: Заголовок теста из allure.
    :param allure_id: Идентификатор теста из allure.
    :param origin: Файл и строка объявления теста.
    :param skip_reason: Причина пропуска теста; None — тест не пропущен.
    :param outcomes: Результаты по шагам в порядке исходника.
    :param extras: Снимки, не привязанные ни к одному шагу.
    :param warnings: Предупреждения разбора: угаданная нумерация, чужой кейс, наследование номера.
    :param explicit_numbering: True, если номера шагов взяты из разметки дампа.
    :param snapshots_total: Сколько снимков нашлось у кейса.
    """

    dump_path: Path
    case_no: int | None
    name: str
    title: str
    allure_id: str | None
    origin: str
    skip_reason: str | None
    outcomes: list[StepOutcome] = field(default_factory=list)
    extras: list[ExtraSnapshot] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    explicit_numbering: bool = False
    snapshots_total: int = 0

    @property
    def problem_steps(self) -> list[int]:
        """Номера шагов, на которых есть проблемы.

        :return: Список номеров шагов в порядке следования.
        """
        return [item.binding.number for item in self.outcomes if item.problems]

    @property
    def has_broken(self) -> bool:
        """Есть ли хотя бы один ненайденный локатор вне условной ветки.

        :return: True, если на каком-то шаге локатор не найден.
        """
        return any(item.broken for item in self.outcomes)

    @property
    def has_problems(self) -> bool:
        """Есть ли на шагах хоть одна проблема: не найден ИЛИ найден больше одного раза.

        Именно это свойство определяет код возврата. Неоднозначный локатор роняет Playwright
        по strict mode ровно так же, как ненайденный, и выпускать его в CI зелёным нельзя.

        :return: True, если на каком-то шаге есть развёрнутая в отчёте проблема.
        """
        return any(item.problems for item in self.outcomes)

    @property
    def checked_locators(self) -> int:
        """Сколько локаторов реально сверялось со снимками за весь прогон.

        :return: Сумма проверенных локаторов по всем шагам.
        """
        return sum(item.checkable for item in self.outcomes)

    @property
    def nothing_checked(self) -> bool:
        """Сверять было нечего: снимков нет или ни один локатор не проверялся.

        Тест, который вообще не трогает DOM, сюда не относится: там сверять нечего по замыслу,
        и про это уже написано отдельным предупреждением. А вот дамп не того файла, пустой файл
        или снимки мимо кейса — это ошибка ввода, и выдавать её за «проблем нет» нельзя.

        :return: True, если ни один локатор теста со снимками не сверялся.
        """
        if not any(item.binding.has_dom for item in self.outcomes):
            return False
        return not self.snapshots_total or not self.checked_locators


class _SnapshotCache:
    """Кэш разобранных снимков: один снимок разбирается ровно один раз.

    Снимки бывают по мегабайту, а один и тот же снимок нужен и шагу, и проверке сдвига.
    """

    def __init__(self) -> None:
        """Создаёт пустой кэш."""
        self._parsed: dict[int, ParsedSnapshot] = {}

    def get(self, snapshot: Snapshot) -> ParsedSnapshot:
        """Возвращает разобранный снимок, разбирая его при первом обращении.

        :param snapshot: Снимок из дампа.
        :return: Разобранный снимок с деревьями и индексом.
        """
        parsed = self._parsed.get(snapshot.index)
        if parsed is None:
            parsed = parse_snapshot(snapshot)
            self._parsed[snapshot.index] = parsed
        return parsed


def _case_snapshots(document: DumpDocument, case_no: int | None) -> tuple[list[Snapshot], list[str]]:
    """Отбирает снимки нужного кейса.

    :param document: Разобранный дамп.
    :param case_no: Номер кейса; None — брать весь дамп.
    :return: Кортеж (снимки в порядке файла, предупреждения).
    """
    if case_no is None:
        return list(document.snapshots), []
    snapshots = [item for item in document.snapshots if item.case_no == case_no]
    if snapshots:
        return snapshots, []
    if any(block.case_no == case_no for block in document.blocks) or not document.snapshots:
        return [], [f"у кейса {case_no} в дампе нет ни одного снимка — сверять нечего"]
    warning = (
        f"в дампе нет маркера 'case {case_no}' — разбираются все {len(document.snapshots)} снимков файла; "
        f"поставьте перед снимками строку 'case {case_no}:', чтобы отделить их от чужих кейсов"
    )
    return list(document.snapshots), [warning]


def _bind_explicit(
    bindings: list[StepBinding],
    snapshots: list[Snapshot],
    marks: dict[int, int],
) -> tuple[list[ExtraSnapshot], list[str]]:
    """Раскладывает снимки по шагам согласно разметке дампа.

    Снимок без своего номера наследует номер предыдущего размеченного: человек мог снять
    два экрана на один шаг и подписать только первый.

    :param bindings: Шаги теста (заполняются снимками на месте).
    :param snapshots: Снимки кейса в порядке файла.
    :param marks: Отображение «номер снимка -> номер шага».
    :return: Кортеж (лишние снимки, предупреждения).
    """
    by_number = {item.number: item for item in bindings}
    extras: list[ExtraSnapshot] = []
    warnings: list[str] = []
    inherited: list[int] = []
    current: int | None = None
    for snapshot in snapshots:
        number = marks.get(snapshot.index)
        if number is None:
            number = current
            if number is not None:
                inherited.append(snapshot.index)
        if number is None:
            extras.append(ExtraSnapshot(snapshot=snapshot, found=0, total=0, reason="номер шага не указан"))
            continue
        target = by_number.get(number)
        if target is None:
            extras.append(ExtraSnapshot(snapshot=snapshot, found=0, total=0, reason=f"шага {number} в тесте нет"))
            continue
        target.snapshots.append(snapshot)
        current = number
    if inherited:
        listed = ", ".join(f"#{item}" for item in inherited)
        warnings.append(f"у снимков {listed} номер шага не указан — отнесены к предыдущему размеченному шагу")
    return extras, warnings


def _bind_by_order(bindings: list[StepBinding], snapshots: list[Snapshot]) -> list[ExtraSnapshot]:
    """Раскладывает снимки по шагам подряд, пропуская шаги без обращений к DOM.

    :param bindings: Шаги теста (заполняются снимками на месте).
    :param snapshots: Снимки кейса в порядке файла.
    :return: Снимки, которым шага не хватило.
    """
    queue = list(snapshots)
    for binding in bindings:
        if not binding.has_dom or not queue:
            continue
        binding.snapshots.append(queue.pop(0))
        binding.guessed = True
    return [ExtraSnapshot(snapshot=item, found=0, total=0, reason="шагов меньше, чем снимков") for item in queue]


def _options(dump_path: Path, project_root: Path, max_candidates: int) -> InspectionOptions:
    """Собирает параметры прогона для :func:`locator_checker.check_locators`.

    Порог покрытия владельца выставлен в ноль: набор локаторов уже сужен телом шага, и
    отфильтровывать их ещё и по «страницы нет в дампе» нельзя — иначе сломанный локатор
    молча исчезнет из отчёта.

    :param dump_path: Путь к дампу.
    :param project_root: Корень репозитория.
    :param max_candidates: Сколько кандидатов на замену подбирать.
    :return: Параметры прогона.
    """
    return InspectionOptions(
        dump_path=dump_path,
        locators_root=project_root / "pages" / "locators",
        ui_elements_path=project_root / "pages" / "ui_elements.py",
        project_root=project_root,
        owner_coverage_threshold=0.0,
        max_candidates=max_candidates,
        max_elements_per_snapshot=5,
    )


def _run(locators: list[StepLocator], parsed: list[ParsedSnapshot], options: InspectionOptions) -> list[StepCheck]:
    """Гоняет локаторы шага по его снимкам.

    :param locators: Обращения шага к локаторам.
    :param parsed: Разобранные снимки шага.
    :param options: Параметры прогона.
    :return: Результаты по локаторам в том же порядке.
    """
    checks = check_locators([item.record for item in locators], parsed, options)
    return [StepCheck(locator=locator, check=check) for locator, check in zip(locators, checks, strict=True)]


def build_report(
    test: object,
    document: DumpDocument,
    project_root: Path,
    max_candidates: int = 3,
) -> StepsReport:
    """Разбирает дамп по шагам выбранного теста.

    :param test: Тест из ``step_collector`` со списком шагов и их локаторами.
    :param document: Разобранный дамп.
    :param project_root: Корень репозитория.
    :param max_candidates: Сколько кандидатов на замену подбирать сломанному локатору.
    :return: Готовый отчёт; текстовый рендер делает :func:`render_report`.
    """
    reset_caches()
    case_no = test_case_no(test)
    snapshots, warnings = _case_snapshots(document, case_no)
    bindings = [
        StepBinding(
            number=step_number(step, position),
            title=step_title(step),
            locators=step_locators(step),
            gaps=step_gaps(step),
        )
        for position, step in enumerate(test_steps(test), start=1)
    ]
    titles = {item.number: item.title for item in bindings}
    known = {item.index for item in snapshots}
    marks = {
        index: number for index, number in snapshot_step_numbers(document, case_no, titles).items() if index in known
    }
    explicit = bool(marks)
    if explicit:
        extras, bind_warnings = _bind_explicit(bindings, snapshots, marks)
        warnings.extend(bind_warnings)
    else:
        extras = _bind_by_order(bindings, snapshots)
        if snapshots:
            warnings.append("нумерация шагов не указана — разложено по порядку")
    if bindings and not any(item.has_dom for item in bindings):
        warnings.append("тест не обращается ни к одному локатору — это чистое API, сверять с DOM нечего")
    report = StepsReport(
        dump_path=document.path,
        case_no=case_no,
        name=test_name(test),
        title=test_title(test),
        allure_id=test_allure_id(test),
        origin=test_origin(test),
        skip_reason=test_skip_reason(test),
        extras=extras,
        warnings=warnings,
        explicit_numbering=explicit,
        snapshots_total=len(snapshots),
    )
    cache = _SnapshotCache()
    options = _options(document.path, project_root, max_candidates)
    for binding in bindings:
        outcome = StepOutcome(binding=binding)
        if binding.locators and binding.snapshots:
            outcome.checks = _run(binding.locators, [cache.get(item) for item in binding.snapshots], options)
        report.outcomes.append(outcome)
    _mark_shift_hints(report, snapshots, cache, options)
    _fill_extras(report, bindings, cache, options)
    return report


def _looks_shifted(outcome: StepOutcome) -> bool:
    """Стоит ли проверять на этом шаге гипотезу сдвига разметки.

    Порог по доле, а не «не нашлось совсем ничего»: одного паразитного совпадения (шапка
    карточки клиента есть почти на каждом снимке) хватало, чтобы проверка не запускалась,
    и отчёт печатал восемь ложных «не найден» подряд.

    :param outcome: Результат шага.
    :return: True, если шаг подозрителен.
    """
    if not outcome.checks or not outcome.binding.snapshots or outcome.checkable < COLLAPSE_THRESHOLD:
        return False
    return outcome.found <= outcome.checkable * SHIFT_SUSPECT_RATIO


def _probe(
    locators: list[StepLocator],
    snapshot: Snapshot,
    cache: _SnapshotCache,
    options: InspectionOptions,
) -> tuple[int, int]:
    """Гоняет набор локаторов по одному снимку — для проверки гипотезы сдвига.

    :param locators: Обращения к локаторам.
    :param snapshot: Снимок, по которому гонять.
    :param cache: Кэш разобранных снимков.
    :param options: Параметры прогона.
    :return: Пара «нашлось, проверялось».
    """
    checks = _run(locators, [cache.get(snapshot)], options)
    found = sum(1 for item in checks if not item.missing and not item.skipped)
    return found, sum(1 for item in checks if not item.skipped)


def _mark_shift_hints(
    report: StepsReport,
    snapshots: list[Snapshot],
    cache: _SnapshotCache,
    options: InspectionOptions,
) -> None:
    """Проверяет гипотезу «разметка снимков съехала на шаг» для подозрительных шагов.

    Проверяются обе стороны: не лежат ли локаторы шага в соседнем снимке и не подходит ли
    снимок шага соседнему шагу. Вторая половина нужна для самой частой ошибки — «забыл снять
    первый экран»: своего снимка у шага тогда в дампе нет вообще, и одной первой проверки мало.

    Раскладка при этом не переставляется: молча переставленные снимки — это отчёт, которому
    нельзя верить. Печатается только подсказка.

    :param report: Отчёт, чьи шаги проверяются (помечается на месте).
    :param snapshots: Снимки кейса в порядке файла.
    :param cache: Кэш разобранных снимков.
    :param options: Параметры прогона.
    :return: Ничего.
    """
    order = {item.index: position for position, item in enumerate(snapshots)}
    outcomes = report.outcomes
    for index, outcome in enumerate(outcomes):
        if not _looks_shifted(outcome):
            continue
        snapshot = outcome.binding.snapshots[-1]
        position = order.get(snapshot.index)
        if position is None:
            continue
        for offset in (1, -1):
            neighbour = position + offset
            if not 0 <= neighbour < len(snapshots):
                continue
            found, _ = _probe(outcome.binding.locators, snapshots[neighbour], cache, options)
            if found > outcome.found and found * 2 >= outcome.checkable:
                outcome.shift_hint = (
                    f"локаторы шага ({found} из {outcome.checkable}) находятся в снимке "
                    f"#{snapshots[neighbour].index}, а не в своём"
                )
                break
        if outcome.shift_hint:
            continue
        for offset in (1, -1):
            other = outcomes[index + offset] if 0 <= index + offset < len(outcomes) else None
            if other is None or not other.binding.locators:
                continue
            found, checkable = _probe(other.binding.locators, snapshot, cache, options)
            if checkable >= COLLAPSE_THRESHOLD and found > outcome.found and found * 2 >= checkable:
                outcome.shift_hint = (
                    f"снимок #{snapshot.index} подходит шагу {other.binding.number} ({found} из {checkable}), а не этому"
                )
                break


def _fill_extras(
    report: StepsReport,
    bindings: list[StepBinding],
    cache: _SnapshotCache,
    options: InspectionOptions,
) -> None:
    """Гоняет лишние снимки по локаторам этого теста — чтобы было видно, к чему они ближе.

    Никакого аудита репозитория: берутся только локаторы разобранного теста.

    :param report: Отчёт с лишними снимками (заполняется на месте).
    :param bindings: Шаги теста — источник локаторов.
    :param cache: Кэш разобранных снимков.
    :param options: Параметры прогона.
    :return: Ничего.
    """
    if not report.extras:
        return
    locators: list[StepLocator] = []
    seen: set[tuple[str, str]] = set()
    for binding in bindings:
        for item in binding.locators:
            key = (item.record.class_name, item.record.attr)
            if key not in seen:
                seen.add(key)
                locators.append(item)
    if not locators:
        return
    for extra in report.extras:
        checks = _run(locators, [cache.get(extra.snapshot)], options)
        extra.found = sum(1 for item in checks if not item.missing and not item.skipped)
        extra.total = sum(1 for item in checks if not item.skipped)


def _shorten(text: str, limit: int) -> str:
    """Обрезает длинную строку многоточием.

    :param text: Исходный текст.
    :param limit: Предельная длина.
    :return: Текст не длиннее ``limit``.
    """
    collapsed = re.sub(r"\s+", " ", text).strip()
    return collapsed if len(collapsed) <= limit else f"{collapsed[: limit - 1]}…"


def status_text(item: StepCheck) -> str:
    """Человеческая формулировка результата по локатору.

    :param item: Результат проверки локатора шага.
    :return: Строка вида ``не найден`` или ``найдено 3, ожидался 1``.
    """
    check = item.check
    if check.status is MatchStatus.COMPILE_ERROR:
        return f"селектор не компилируется: {_shorten(check.compile_error or '', 60)}"
    if check.status is MatchStatus.NOT_FOUND:
        return "не найден в ветке if" if item.locator.conditional else "не найден"
    if check.status in AMBIGUOUS_STATUSES:
        return f"найдено {check.max_matches_in_snapshot}, ожидался 1"
    if check.status in SKIPPED_STATUSES:
        return "не проверен (относительный или playwright-селектор)"
    return "ок"


def best_candidate(check: LocatorCheckResult) -> ReplacementCandidate | None:
    """Выбирает кандидата на замену, которого не стыдно показать.

    Слабые кандидаты отбрасываются: совпадение «текст похож на описание» ловит шапку приложения
    по слову «Клиент», а селектор, который сам находит несколько элементов, заменой быть не может.
    Пустое место лучше ложного следа — по нему заказчик пойдёт править не тот локатор.

    :param check: Результат проверки локатора.
    :return: Лучший кандидат либо None, если все слабые.
    """
    for candidate in check.candidates:
        if not any(marker in candidate.reason for marker in WEAK_CANDIDATE_MARKERS):
            return candidate
    return None


def _problem_lines(item: StepCheck, width: int = MIN_ATTR_COLUMN_WIDTH) -> list[str]:
    """Разворачивает один проблемный локатор: селектор, описание, кандидат, адрес объявления.

    :param item: Результат проверки локатора шага.
    :param width: Ширина колонки с именем атрибута.
    :return: Строки отчёта с отступом.
    """
    locator = item.locator.record
    lines = [f"    {locator.attr:<{width}} {_shorten(locator.selector, MAX_SELECTOR_LENGTH):<64} {status_text(item)}"]
    if locator.description and locator.description != locator.attr:
        lines.append(f"        описание: {_shorten(locator.description, 80)}")
    candidate = best_candidate(item.check)
    if candidate is not None:
        label = _shorten(candidate.element.own_text or candidate.element.label or "", 40)
        tail = f"  текст '{label}'" if label else ""
        lines.append(f"        кандидат: {_shorten(candidate.selector, MAX_SELECTOR_LENGTH)}{tail}")
    lines.append(f"        {locator.file}:{locator.line}")
    return lines


def _attr_column_width(outcome: StepOutcome, verbose: bool) -> int:
    """Ширина колонки с именем атрибута для всех строк одного шага.

    Ширина считается один раз на шаг, чтобы проблемные строки и строки «ок» под ключом ``-v``
    стояли в одну колонку: разъехавшиеся колонки читаются как разные разделы отчёта.

    :param outcome: Результат шага.
    :param verbose: Печатаются ли и найденные локаторы.
    :return: Ширина колонки в символах, не меньше :data:`MIN_ATTR_COLUMN_WIDTH`.
    """
    printed = outcome.checks if verbose else list(outcome.problems[:MAX_PROBLEMS_PER_STEP])
    return max([MIN_ATTR_COLUMN_WIDTH, *(len(item.locator.record.attr) for item in printed)])


def _step_problem_lines(outcome: StepOutcome, verbose: bool, width: int = MIN_ATTR_COLUMN_WIDTH) -> list[str]:
    """Собирает строки по проблемам шага.

    Если в снимке нашлась в лучшем случае пара локаторов из десятка, разворачивать их все
    бессмысленно: это не десять сломанных селекторов, а один не тот снимок. Такой шаг
    сворачивается в две строки, а полный разбор остаётся под ключом ``-v``.

    :param outcome: Результат шага.
    :param verbose: Печатать полный разбор в любом случае.
    :param width: Ширина колонки с именем атрибута, общая для всех строк шага.
    :return: Строки отчёта с отступом.
    """
    problems = outcome.problems
    if not problems:
        return []
    listed = _shorten(", ".join(item.locator.record.attr for item in problems), 160)
    if not verbose and outcome.shift_hint:
        return [f"    не сверились ({len(problems)}), снимок чужой: {listed}"]
    if not verbose and _looks_shifted(outcome):
        return [
            f"    нашлось {outcome.found} из {outcome.checkable} локаторов шага — похоже, снимок "
            "не от этого шага, а не сломаны все селекторы сразу",
            f"    {listed}",
        ]
    shown = problems if verbose else problems[:MAX_PROBLEMS_PER_STEP]
    lines: list[str] = []
    for item in shown:
        lines.extend(_problem_lines(item, width))
    rest = problems[len(shown) :]
    if rest:
        listed = ", ".join(item.locator.record.attr for item in rest)
        lines.append(f"    и ещё {len(rest)} с той же бедой (полный разбор — ключ -v): {_shorten(listed, 140)}")
    return lines


def _snapshot_column(binding: StepBinding) -> str:
    """Колонка со снимками шага.

    :param binding: Шаг и его снимки.
    :return: Строка вида ``снимок #3``, ``снимки #3,#4`` или ``без снимка``.
    """
    if not binding.snapshots:
        return "без снимка"
    if len(binding.snapshots) == 1:
        return f"снимок #{binding.snapshots[0].index}"
    return "снимки " + ",".join(f"#{item.index}" for item in binding.snapshots)


def _result_column(outcome: StepOutcome) -> str:
    """Колонка с результатом шага.

    :param outcome: Результат шага.
    :return: Строка вида ``ок 4/4``, ``3/5`` либо пустая строка, если проверять было нечего.
    """
    if not outcome.checks:
        return ""
    total = outcome.checkable
    if not total:
        return "не проверен"
    return f"ок {outcome.found}/{total}" if not outcome.problems else f"{outcome.found}/{total}"


def plural(count: int, one: str, few: str, many: str) -> str:
    """Склоняет существительное при числе: 1 шаг, 2 шага, 5 шагов.

    :param count: Число.
    :param one: Форма для 1.
    :param few: Форма для 2-4.
    :param many: Форма для 0, 5 и больше.
    :return: Число и слово через пробел.
    """
    tail, hundred = count % 10, count % 100
    if tail == 1 and hundred != 11:
        return f"{count} {one}"
    if tail in (2, 3, 4) and hundred not in (12, 13, 14):
        return f"{count} {few}"
    return f"{count} {many}"


def _summary_line(report: StepsReport) -> str:
    """Строка «итог» в шапке отчёта.

    :param report: Отчёт.
    :return: Одна строка со сводкой.
    """
    problems = report.problem_steps
    listed = ", ".join(str(item) for item in problems)
    if report.nothing_checked:
        verdict = (
            "сверять нечего: снимков нет" if not report.snapshots_total else "сверять нечего: локаторы не проверялись"
        )
    elif not problems:
        verdict = "проблем нет"
    else:
        verdict = f"проблема на шаге {listed}" if len(problems) == 1 else f"проблемы на шагах {listed}"
    parts = [
        plural(len(report.outcomes), "шаг", "шага", "шагов"),
        plural(report.snapshots_total, "снимок", "снимка", "снимков"),
        verdict,
    ]
    return f"итог: {', '.join(parts)}"


def _step_lines(outcome: StepOutcome, verbose: bool, snapshot_width: int = SNAPSHOT_COLUMN_WIDTH) -> list[str]:
    """Строит строки одного шага: сводную и, если есть проблемы, подробные.

    :param outcome: Результат шага.
    :param verbose: Печатать и найденные локаторы.
    :param snapshot_width: Ширина колонки со снимками, общая для всего отчёта: у шага с двумя
        снимками колонка длиннее, и без общей ширины заголовки шагов разъезжаются.
    :return: Строки отчёта.
    """
    binding = outcome.binding
    attr_width = _attr_column_width(outcome, verbose)
    head = (
        f"шаг {binding.number:<2} {_snapshot_column(binding).ljust(snapshot_width)} "
        f"{_result_column(outcome).ljust(RESULT_COLUMN_WIDTH)} {_shorten(binding.title, MAX_TITLE_LENGTH)}"
    )
    if not binding.has_dom:
        head += "   (код вне шагов)" if binding.number == OUTSIDE_STEP_NUMBER else "   (API, DOM не нужен)"
    lines = [head.rstrip()]
    if outcome.shift_hint:
        lines.append(f"    похоже, разметка снимков съехала: {outcome.shift_hint}; проверьте разметку дампа")
    lines.extend(_step_problem_lines(outcome, verbose, attr_width))
    conditional = outcome.conditional_missing
    if conditional:
        listed = ", ".join(item.locator.record.attr for item in conditional)
        lines.append(f"    не найдены, но лежат в невычисленной ветке if — это законно: {_shorten(listed, 120)}")
    if outcome.not_checked and (outcome.problems or verbose):
        listed = ", ".join(item.locator.record.attr for item in outcome.not_checked)
        lines.append(f"    не проверялись ({len(outcome.not_checked)}): {_shorten(listed, 120)}")
    if verbose:
        for item in outcome.checks:
            if not item.missing and not item.ambiguous and not item.skipped:
                selector = _shorten(item.locator.record.selector, MAX_SELECTOR_LENGTH)
                lines.append(f"    {item.locator.record.attr:<{attr_width}} {selector:<64} ок")
    gaps = list(dict.fromkeys(binding.gaps))
    shown_gaps = gaps if verbose else gaps[:MAX_GAPS_PER_STEP]
    lines.extend(f"    заметка разбора: {_shorten(gap, 140)}" for gap in shown_gaps)
    if len(gaps) > len(shown_gaps):
        lines.append(f"    и ещё {len(gaps) - len(shown_gaps)} заметок разбора (ключ -v)")
    return lines


def render_report(report: StepsReport, verbose: bool = False) -> str:
    """Рендерит короткий отчёт: зелёный шаг — одна строка, проблемный разворачивается.

    :param report: Результат :func:`build_report`.
    :param verbose: Печатать и найденные локаторы, а не только проблемные.
    :return: Готовый текст отчёта.
    """
    case_part = f"case {report.case_no} -> " if report.case_no is not None else ""
    id_part = f"  (allure.id {report.allure_id})" if report.allure_id else ""
    lines = [f"{case_part}{report.name}{id_part}"]
    if report.origin:
        lines.append(report.origin)
    if report.skip_reason is not None:
        lines.append(f"ВНИМАНИЕ: тест помечен pytest.mark.skip{f': {report.skip_reason}' if report.skip_reason else ''}")
    lines.append(_summary_line(report))
    lines.extend(f"внимание: {_shorten(warning, 200)}" for warning in report.warnings)
    lines.append("")
    snapshot_width = max([SNAPSHOT_COLUMN_WIDTH, *(len(_snapshot_column(item.binding)) for item in report.outcomes)])
    for outcome in report.outcomes:
        lines.extend(_step_lines(outcome, verbose, snapshot_width))
    lines.append("")
    if report.extras:
        lines.append("лишние снимки:")
        for extra in report.extras:
            found = f" — из {extra.total} локаторов теста нашлось {extra.found}" if extra.total else ""
            lines.append(
                f"    снимок #{extra.snapshot.index} (строки {extra.snapshot.start_line}-"
                f"{extra.snapshot.end_line}), {extra.reason}{found}"
            )
    else:
        lines.append("лишних снимков нет")
    return "\n".join(lines)


def report_to_dict(report: StepsReport) -> dict[str, Any]:
    """Собирает машинный вид отчёта для ключа ``--json``.

    :param report: Результат :func:`build_report`.
    :return: Словарь, пригодный для json.dumps.
    """
    return {
        "dump": str(report.dump_path),
        "case_no": report.case_no,
        "test": report.name,
        "title": report.title,
        "allure_id": report.allure_id,
        "origin": report.origin,
        "skipped": report.skip_reason is not None,
        "skip_reason": report.skip_reason,
        "explicit_numbering": report.explicit_numbering,
        "snapshots_total": report.snapshots_total,
        "warnings": report.warnings,
        "steps": [
            {
                "number": outcome.binding.number,
                "title": outcome.binding.title,
                "snapshots": [item.index for item in outcome.binding.snapshots],
                "guessed": outcome.binding.guessed,
                "locators_total": len(outcome.binding.locators),
                "checked": outcome.checkable,
                "found": outcome.found,
                "shift_hint": outcome.shift_hint,
                "gaps": outcome.binding.gaps,
                "problems": [
                    {
                        "attr": item.locator.record.attr,
                        "class": item.locator.record.class_name,
                        "selector": item.locator.record.selector,
                        "description": item.locator.record.description,
                        "file": item.locator.record.file,
                        "line": item.locator.record.line,
                        "status": str(item.check.status),
                        "matches": item.check.max_matches_in_snapshot,
                        "conditional": item.locator.conditional,
                        "message": status_text(item),
                        "candidates": [
                            {"selector": candidate.selector, "score": candidate.score, "reason": candidate.reason}
                            for candidate in item.check.candidates
                        ],
                    }
                    for item in outcome.problems
                ],
                "conditional_missing": [item.locator.record.attr for item in outcome.conditional_missing],
                "not_checked": [item.locator.record.attr for item in outcome.not_checked],
            }
            for outcome in report.outcomes
        ],
        "extra_snapshots": [
            {
                "index": extra.snapshot.index,
                "start_line": extra.snapshot.start_line,
                "end_line": extra.snapshot.end_line,
                "reason": extra.reason,
                "found": extra.found,
                "total": extra.total,
            }
            for extra in report.extras
        ],
        "has_broken": report.has_broken,
        "has_problems": report.has_problems,
        "nothing_checked": report.nothing_checked,
    }
