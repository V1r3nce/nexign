"""Общие структуры данных пакета scripts/dom_inspector.

Модуль намеренно не имеет внешних зависимостей (только stdlib) и не содержит логики разбора:
здесь описан контракт между dump_parser, element_index, locator_collector, locator_checker,
api_parser и cli. Исполнители модулей импортируют эти структуры и НЕ меняют их.

Все перечисления наследуют :class:`enum.StrEnum`, поэтому ``json.dumps(dataclasses.asdict(obj))``
работает без дополнительных энкодеров.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path

# Обёртки из pages/ui_elements.py, для которых несколько совпадений в DOM — норма,
# а не риск strict mode. Используется locator_collector для заполнения LocatorRecord.is_list.
LIST_WRAPPER_NAMES: frozenset[str] = frozenset(
    {
        "ElementsList",
        "ScrollableList",
        "VirtualTable",
        "VirtualTableCheckbox",
        "CheckboxBlock",
        "RadioOrCheckboxBlock",
        "MultySelect",
    }
)

# Значение по умолчанию для контекстного фильтра «страница локатора есть в снимке».
# Это доля селекторов файла-владельца, найденных в снимке. Проверено на реальных дампах:
# 0.65 / 0.45 / 0.45 у «своих» страниц, поэтому выше 0.5 порог поднимать нельзя.
DEFAULT_OWNER_COVERAGE_THRESHOLD: float = 0.35


class SelectorKind(StrEnum):
    """Тип селектора, определяющий движок проверки."""

    CSS = "css"
    XPATH = "xpath"
    RELATIVE = "relative"
    """Относительный путь (``ancestor::``, ``//span`` в довесок к родителю) — от document не проверяется."""
    PLAYWRIGHT = "playwright"
    """Специфика Playwright (``>>``, ``text=``, ``:has-text()``, ``:visible``) — статически не проверяется."""
    UNKNOWN = "unknown"


class NoteStatus(StrEnum):
    """Классификация человеческой пометки автора дампа."""

    DONE = "done"
    """«Все есть» / «всё есть» (сравнение через casefold)."""
    OUTDATED = "outdated"
    SKIP = "skip"
    """Есть ссылка на баг в Jira — кейс пропускается."""
    NOTE = "note"
    """Свободный комментарий с инструкцией, что делать."""


class MatchStatus(StrEnum):
    """Итог проверки одного селектора по всем снимкам дампа."""

    UNIQUE = "unique"
    """Ровно одно совпадение во всех снимках, где селектор вообще нашёлся."""
    UNIQUE_VISIBLE = "unique_visible"
    """Совпадений несколько, но видимое ровно одно — Playwright всё равно упадёт по strict mode."""
    MULTIPLE_VISIBLE = "multiple_visible"
    """Несколько видимых совпадений — реальный риск strict mode."""
    NOT_FOUND = "not_found"
    """0 совпадений при том, что страница-владелец локатора в дампе присутствует — сломанный локатор."""
    PAGE_NOT_IN_DUMP = "page_not_in_dump"
    """0 совпадений, но и остальные локаторы файла-владельца не нашлись — судить не о чем."""
    COMPILE_ERROR = "compile_error"
    """Селектор не скомпилировался ни soupsieve, ни lxml — синтаксическая ошибка в репозитории."""
    NOT_CHECKED = "not_checked"
    """Относительный или Playwright-специфичный селектор: статически не проверяется."""


class Severity(StrEnum):
    """Приоритет находки в отчёте."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class VisibilityScale(StrEnum):
    """Шкала видимости элемента."""

    PW_VISIBLE = "pw_visible"
    """Приближение к Playwright is_visible(): непустой бокс и visibility != hidden."""
    RENDERED = "rendered"
    """Широкая эвристика «пользователь реально видит»: плюс clip-path, sr-only, класс-маркеры."""


@dataclass(slots=True)
class Note:
    """Свободная пометка автора дампа.

    :param line: Номер строки в файле дампа (1-based).
    :param text: Текст пометки целиком, без нормализации.
    :param status: Классификация пометки.
    :param jira_key: Ключ задачи Jira, если в тексте была ссылка (например ``RMBSS-18239``).
    :param after_snapshot_index: Индекс снимка, после которого стоит «висячая» пометка,
        либо None, если пометка идёт сразу за маркером кейса.
    """

    line: int
    text: str
    status: NoteStatus = NoteStatus.NOTE
    jira_key: str | None = None
    after_snapshot_index: int | None = None


@dataclass(slots=True)
class Snapshot:
    """Один снимок DOM (``document.body.outerHTML``) внутри файла дампа.

    :param index: Сквозной порядковый номер снимка в файле, начиная с 1.
    :param case_no: Номер тест-кейса из ближайшего маркера выше; None — снимок до первого маркера.
    :param start_line: Номер первой строки снимка в файле (1-based, включительно).
    :param end_line: Номер последней строки снимка (1-based, включительно); может равняться start_line.
    :param html: Текст снимка целиком, внутренние переводы строк сохранены как есть.
    :param truncated: True, если закрывающий ``</body>`` не найден и снимок закрыт по fallback-правилу.
    """

    index: int
    case_no: int | None
    start_line: int
    end_line: int
    html: str
    truncated: bool = False

    @property
    def address(self) -> str:
        """Человекочитаемый адрес снимка для отчёта.

        :return: Строка вида ``снимок #17, строки 236-247, case 30``.
        """
        case_part = f", case {self.case_no}" if self.case_no is not None else ", вне кейсов"
        return f"снимок #{self.index}, строки {self.start_line}-{self.end_line}{case_part}"


@dataclass(slots=True)
class CaseBlock:
    """Блок дампа, относящийся к одному тест-кейсу.

    Кейс может не иметь ни одного снимка (в реальном дампе так у case 15-18, 24, 27, 31),
    а также может иметь пометку «все есть» и при этом снимок — это не противоречие.

    :param case_no: Номер кейса; None — корзина для снимков и пометок до первого маркера.
    :param marker_line: Номер строки маркера (1-based); None для корзины.
    :param marker_raw: Сырой текст строки-маркера, например ``case 30: (Только создание договора вручную)``.
    :param inline_note: Хвост маркера после номера кейса; пустая строка, если хвоста нет.
    :param notes: Пометки, относящиеся к кейсу, в порядке появления в файле.
    :param snapshots: Снимки кейса в порядке появления в файле.
    """

    case_no: int | None
    marker_line: int | None = None
    marker_raw: str = ""
    inline_note: str = ""
    notes: list[Note] = field(default_factory=list)
    snapshots: list[Snapshot] = field(default_factory=list)

    @property
    def status(self) -> NoteStatus:
        """Сводный статус кейса по его пометкам.

        :return: Первый из статусов SKIP / OUTDATED / DONE, встретившийся в пометках, иначе NOTE.
        """
        for wanted in (NoteStatus.SKIP, NoteStatus.OUTDATED, NoteStatus.DONE):
            if any(note.status is wanted for note in self.notes):
                return wanted
        return NoteStatus.NOTE


@dataclass(slots=True)
class DumpDocument:
    """Результат разбора файла-дампа целиком.

    :param path: Путь к разобранному файлу.
    :param line_count: Количество значимых строк файла (без завершающего пустого элемента).
    :param blocks: Блоки кейсов в порядке появления в файле; сортировать по номеру кейса нельзя.
    :param snapshots: Плоский список всех снимков в порядке появления, index соответствует позиции + 1.
    """

    path: Path
    line_count: int
    blocks: list[CaseBlock] = field(default_factory=list)
    snapshots: list[Snapshot] = field(default_factory=list)

    def snapshot_by_index(self, index: int) -> Snapshot | None:
        """Возвращает снимок по его сквозному номеру.

        :param index: Сквозной номер снимка (1-based).
        :return: Снимок либо None, если такого номера нет.
        """
        for snapshot in self.snapshots:
            if snapshot.index == index:
                return snapshot
        return None


@dataclass(slots=True)
class DomElement:
    """Элемент DOM, извлечённый из снимка.

    :param snapshot_index: Сквозной номер снимка, из которого взят элемент.
    :param dom_path: Индексный путь вида ``html[0]/body[0]/div[3]/button[1]`` — позиция среди
        элементов-братьев. Позволяет дедуплицировать совпадения CSS (soupsieve) и XPath (lxml):
        деревья BeautifulSoup(html, "lxml") и lxml.html.document_fromstring структурно идентичны.
    :param tag: Имя тега в нижнем регистре.
    :param attrs: Все атрибуты элемента (значения — строки, класс хранится как есть).
    :param element_id: Значение атрибута id, если есть.
    :param test_id: Значение data-testid, если есть.
    :param role: Значение атрибута role, если есть.
    :param text: Нормализованный текст элемента: get_text() с заменой NBSP на пробел и схлопыванием пробелов.
    :param own_text: Текст только собственных текстовых узлов (без потомков), нормализованный так же.
    :param aria_label: Значение aria-label.
    :param title: Значение title.
    :param placeholder: Значение placeholder.
    :param name: Значение name.
    :param value: Значение атрибута value (для React-полей может расходиться с живым свойством).
    :param is_interactive: True для button/a/input/select/textarea и элементов с role/tabindex/onclick.
    :param pw_visible: Видимость по жёсткой шкале (приближение Playwright is_visible()).
    :param rendered: Видимость по широкой эвристике (пользователь реально видит).
    :param hidden_reason: Первая сработавшая причина скрытости, например ``clip-path:inset(100%)``
        или ``class:ant-select-dropdown-hidden``; None, если элемент виден по обеим шкалам.
    :param hidden_by_ancestor: True, если причина скрытости найдена не на самом элементе, а на предке.
    """

    snapshot_index: int
    dom_path: str
    tag: str
    attrs: dict[str, str] = field(default_factory=dict)
    element_id: str | None = None
    test_id: str | None = None
    role: str | None = None
    text: str = ""
    own_text: str = ""
    aria_label: str | None = None
    title: str | None = None
    placeholder: str | None = None
    name: str | None = None
    value: str | None = None
    is_interactive: bool = False
    pw_visible: bool = True
    rendered: bool = True
    hidden_reason: str | None = None
    hidden_by_ancestor: bool = False

    @property
    def stable_selector(self) -> str | None:
        """Наиболее устойчивый CSS-селектор элемента.

        Порядок стабильности: data-testid > id > name > aria-label.

        :return: CSS-селектор либо None, если ни одного стабильного атрибута нет.
        """
        if self.test_id:
            return f"[data-testid={self.test_id}]"
        if self.element_id:
            return f"#{self.element_id}"
        if self.name:
            return f"[name={self.name}]"
        if self.aria_label:
            return f'[aria-label="{self.aria_label}"]'
        return None

    @property
    def label(self) -> str:
        """Человекочитаемая подпись элемента для отчёта.

        :return: Первое непустое из text / aria-label / title / placeholder / value; иначе пустая строка.
        """
        for candidate in (self.text, self.aria_label, self.title, self.placeholder, self.value):
            if candidate:
                return candidate
        return ""


@dataclass(slots=True)
class SnapshotIndex:
    """Индекс элементов одного снимка, построенный element_index.

    Ключи текстовых индексов нормализованы: NBSP заменён пробелом, пробелы схлопнуты, применён casefold.

    :param snapshot_index: Сквозной номер снимка.
    :param elements: Все элементы снимка в порядке обхода документа.
    :param by_test_id: Элементы по data-testid (повторы значений — это и есть сигнал strict mode).
    :param by_id: Элементы по id.
    :param by_text: Интерактивные элементы по нормализованному тексту.
    :param element_count: Общее число элементов снимка.
    """

    snapshot_index: int
    elements: list[DomElement] = field(default_factory=list)
    by_test_id: dict[str, list[DomElement]] = field(default_factory=dict)
    by_id: dict[str, list[DomElement]] = field(default_factory=dict)
    by_text: dict[str, list[DomElement]] = field(default_factory=dict)
    element_count: int = 0


@dataclass(slots=True)
class WrapperSpec:
    """Описание класса-обёртки из pages/ui_elements.py, нужное сборщику локаторов.

    :param name: Имя класса-обёртки, например ``Element`` или ``SelectWithId``.
    :param arg_names: Имена параметров __init__ по порядку — нужны для чтения kwargs
        (``ScrollableList`` вызывается только именованными аргументами).
    :param selector_arg: Имя параметра с первичным селектором; None, если селектор синтезируется.
    :param description_arg: Имя параметра с человекочитаемым описанием.
    :param secondary_args: Имена параметров с дополнительными селекторами (item_path, sub_field_path и т.п.).
    :param is_list: True для списочных обёрток — для них несколько совпадений это норма.
    :param synthesized: True для SelectWithId/DropdownWithId, где первый аргумент — фрагмент id,
        а реальный CSS собирается по шаблону.
    """

    name: str
    arg_names: tuple[str, ...]
    selector_arg: str | None
    description_arg: str | None
    secondary_args: tuple[str, ...] = ()
    is_list: bool = False
    synthesized: bool = False


@dataclass(slots=True)
class SecondarySelector:
    """Производный селектор локатора (опции выпадашки, поле ввода датапикера, элемент списка).

    :param selector: Строка селектора.
    :param kind: Тип селектора.
    :param role: Назначение: ``options`` / ``input`` / ``clear`` / ``item`` / ``field`` / ``sub_field``.
    :param relative: True, если селектор применяется к найденному родителю, а не к документу.
    """

    selector: str
    kind: SelectorKind
    role: str
    relative: bool = False


@dataclass(slots=True)
class LocatorRecord:
    """Локатор репозитория, собранный статически через ast.

    :param selector: Готовый селектор (для SelectWithId/DropdownWithId — уже синтезированный CSS).
    :param kind: Тип селектора, определённый по правилам Playwright.
    :param description: Человекочитаемое описание (аргумент locator_name); пустая строка,
        если описание не задано — тогда для сопоставления использовать attr.
    :param attr: Имя атрибута, например ``ADD_BTN``.
    :param class_name: Класс-владелец, в котором объявлен локатор.
    :param module: Точечный путь модуля, например ``pages.locators.nbss.client.client_profile``.
    :param file: Путь к файлу объявления относительно корня репозитория.
    :param line: Номер строки объявления (1-based).
    :param wrapper: Имя класса-обёртки; None для «голых» строковых локаторов.
    :param is_list: True, если обёртка списочная (дубли — норма).
    :param secondary_selectors: Производные селекторы этого же локатора.
    :param inherited_by: Классы-потомки, которым локатор достался по наследству и которые его не переопределяют.
    :param overridden_in_class: True, если тот же атрибут присваивается в этом классе повторно
        (побеждает последнее присваивание, первое — вероятный мёртвый код).
    :param raw_first_arg: Сырой первый аргумент вызова обёртки (для SelectWithId — фрагмент id).
    """

    selector: str
    kind: SelectorKind
    description: str
    attr: str
    class_name: str
    module: str
    file: str
    line: int
    wrapper: str | None = None
    is_list: bool = False
    secondary_selectors: list[SecondarySelector] = field(default_factory=list)
    inherited_by: list[str] = field(default_factory=list)
    overridden_in_class: bool = False
    raw_first_arg: str | None = None

    @property
    def origin(self) -> str:
        """Адрес объявления для отчёта.

        :return: Строка вида ``pages/locators/nbss/client/client_profile.py:300 ClientProfileElements.ADD_BTN``.
        """
        return f"{self.file}:{self.line} {self.class_name}.{self.attr}"

    @property
    def display_name(self) -> str:
        """Название локатора для человека.

        :return: Описание, если оно непустое, иначе имя атрибута.
        """
        return self.description or self.attr


@dataclass(slots=True)
class ReplacementCandidate:
    """Кандидат на замену сломанного или неоднозначного локатора.

    :param element: Найденный в DOM элемент.
    :param selector: Предлагаемый селектор (как правило ``[data-testid=...]``).
    :param score: Оценка пригодности, чем больше тем лучше.
    :param reason: Пояснение, например ``текст совпал с описанием, стабильный data-testid, тег button``.
    :param snapshot_index: Снимок, в котором найден кандидат.
    """

    element: DomElement
    selector: str
    score: float
    reason: str
    snapshot_index: int


@dataclass(slots=True)
class SnapshotMatchResult:
    """Результат применения одного селектора к одному снимку.

    :param snapshot_index: Сквозной номер снимка.
    :param case_no: Номер кейса снимка.
    :param start_line: Первая строка снимка в файле.
    :param end_line: Последняя строка снимка в файле.
    :param match_count: Число совпадений (все, независимо от видимости — так считает strict mode).
    :param pw_visible_count: Сколько совпадений видимы по жёсткой шкале.
    :param rendered_count: Сколько совпадений видимы по широкой эвристике.
    :param elements: Найденные элементы (список может быть усечён по лимиту отчёта).
    :param owner_coverage: Доля селекторов файла-владельца локатора, найденных в этом снимке (0..1).
    :param error: Текст runtime-ошибки движка, если она была.
    """

    snapshot_index: int
    case_no: int | None
    start_line: int
    end_line: int
    match_count: int
    pw_visible_count: int = 0
    rendered_count: int = 0
    elements: list[DomElement] = field(default_factory=list)
    owner_coverage: float | None = None
    error: str | None = None

    @property
    def address(self) -> str:
        """Адрес снимка для отчёта.

        :return: Строка вида ``снимок #2, строки 19-34, case 29``.
        """
        case_part = f", case {self.case_no}" if self.case_no is not None else ", вне кейсов"
        return f"снимок #{self.snapshot_index}, строки {self.start_line}-{self.end_line}{case_part}"


@dataclass(slots=True)
class LocatorCheckResult:
    """Итог проверки одного локатора по всем снимкам дампа.

    :param locator: Проверенный локатор.
    :param status: Классификация результата.
    :param severity: Приоритет находки для отчёта.
    :param total_matches: Суммарное число совпадений по всем снимкам.
    :param max_matches_in_snapshot: Максимум совпадений в пределах одного снимка — именно он даёт strict mode.
    :param snapshots_with_matches: Число снимков, где селектор нашёлся хотя бы раз.
    :param checked_snapshots: Число снимков, по которым реально гоняли селектор.
    :param results: Детали по снимкам (обычно только те, где были совпадения или ошибки).
    :param expected_text: Текст, вытащенный из кавычек в описании локатора, например ``Добавить``.
    :param observed_texts: Нормализованные тексты найденных элементов, например ``["Создать"]``.
    :param text_mismatch: True, если expected_text задан и ни один найденный элемент его не имеет.
    :param candidates: Кандидаты на замену, отсортированные по убыванию score.
    :param compile_error: Сообщение движка, если селектор не скомпилировался.
    :param owner_coverage: Максимальная по снимкам доля найденных селекторов владельца — берётся
        лучшее из покрытия по файлу и по классу-владельцу (см. locator_checker.owner_scopes).
    :param owner_anchor_found: True, если точный якорь селектора (``#id`` или ``[data-testid=...]``)
        встречается в дампе: тогда страница в дампе есть независимо от покрытия.
    :param message: Готовая строка-пояснение для отчёта.
    """

    locator: LocatorRecord
    status: MatchStatus
    severity: Severity = Severity.INFO
    total_matches: int = 0
    max_matches_in_snapshot: int = 0
    snapshots_with_matches: int = 0
    checked_snapshots: int = 0
    results: list[SnapshotMatchResult] = field(default_factory=list)
    expected_text: str | None = None
    observed_texts: list[str] = field(default_factory=list)
    text_mismatch: bool = False
    candidates: list[ReplacementCandidate] = field(default_factory=list)
    compile_error: str | None = None
    owner_coverage: float | None = None
    owner_anchor_found: bool = False
    message: str = ""

    @property
    def is_problem(self) -> bool:
        """Нужно ли показывать находку в основном разделе отчёта и падать с кодом 1.

        :return: True для NOT_FOUND, MULTIPLE_VISIBLE, UNIQUE_VISIBLE, COMPILE_ERROR и при несовпадении текста.
        """
        problem_statuses = {
            MatchStatus.NOT_FOUND,
            MatchStatus.MULTIPLE_VISIBLE,
            MatchStatus.UNIQUE_VISIBLE,
            MatchStatus.COMPILE_ERROR,
        }
        return self.status in problem_statuses or self.text_mismatch


@dataclass(slots=True)
class ApiRequest:
    """Один HTTP-запрос, восстановленный из curl-дампа devtools.

    :param index: Порядковый номер запроса в файле, начиная с 1.
    :param method: HTTP-метод в верхнем регистре.
    :param url: Полный URL как в дампе.
    :param scheme: Схема URL.
    :param host: Хост URL.
    :param path: Путь URL без query.
    :param query: Параметры query в исходном порядке (ключ, значение) — повторы сохраняются.
    :param headers: Заголовки в исходном порядке (имя, значение) — повторы сохраняются.
    :param body_raw: Тело запроса из --data-raw / --data-binary, если было.
    :param body_json: Разобранное тело, если это валидный JSON; иначе None.
    :param content_type: Значение заголовка content-type, если был.
    :param is_noise: True для служебного трафика (например домен kaspersky-labs.com).
    :param noise_reason: Причина отнесения к мусору.
    :param source_line: Номер строки дампа, с которой начинается команда curl (1-based).
    :param raw_command: Исходная команда целиком после снятия cmd-экранирования и склейки строк.
    """

    index: int
    method: str
    url: str
    scheme: str = ""
    host: str = ""
    path: str = ""
    query: list[tuple[str, str]] = field(default_factory=list)
    headers: list[tuple[str, str]] = field(default_factory=list)
    body_raw: str | None = None
    body_json: object | None = None
    content_type: str | None = None
    is_noise: bool = False
    noise_reason: str | None = None
    source_line: int = 0
    raw_command: str = ""

    def header(self, name: str) -> str | None:
        """Возвращает первое значение заголовка без учёта регистра имени.

        :param name: Имя заголовка.
        :return: Значение либо None, если заголовка нет.
        """
        wanted = name.casefold()
        for header_name, header_value in self.headers:
            if header_name.casefold() == wanted:
                return header_value
        return None


@dataclass(slots=True)
class ApiDump:
    """Результат разбора curl-дампа сети.

    :param path: Путь к разобранному файлу.
    :param requests: Полезные запросы в порядке появления.
    :param noise: Отфильтрованный служебный трафик.
    :param failed: Команды, которые не удалось разобрать (сырой текст).
    """

    path: Path
    requests: list[ApiRequest] = field(default_factory=list)
    noise: list[ApiRequest] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)


@dataclass(slots=True)
class InspectionOptions:
    """Параметры запуска проверки: контракт между cli и locator_checker.

    :param dump_path: Путь к файлу дампа DOM.
    :param locators_root: Каталог с локаторами (по умолчанию <корень>/pages/locators).
    :param ui_elements_path: Путь к pages/ui_elements.py — источник сигнатур обёрток.
    :param project_root: Корень репозитория.
    :param report_path: Куда писать текстовый отчёт; None — только stdout.
    :param json_path: Куда писать машинный отчёт в JSON; None — не писать.
    :param only_cases: Проверять только эти номера кейсов; пустое множество — все.
    :param only_snapshots: Проверять только эти номера снимков; пустое множество — все.
    :param owner_coverage_threshold: Порог контекстного фильтра «страница локатора есть в снимке».
    :param check_lists: Проверять ли на дубли списочные обёртки (по умолчанию только понижается severity).
    :param max_candidates: Сколько кандидатов на замену показывать на один локатор.
    :param max_elements_per_snapshot: Сколько найденных элементов сохранять в SnapshotMatchResult.
    :param fail_on_problems: Выходить с кодом 1, если найдены проблемы.
    :param verbose: Печатать подробности по каждому снимку.
    """

    dump_path: Path
    locators_root: Path
    ui_elements_path: Path
    project_root: Path
    report_path: Path | None = None
    json_path: Path | None = None
    only_cases: frozenset[int] = frozenset()
    only_snapshots: frozenset[int] = frozenset()
    owner_coverage_threshold: float = DEFAULT_OWNER_COVERAGE_THRESHOLD
    check_lists: bool = False
    max_candidates: int = 5
    max_elements_per_snapshot: int = 10
    fail_on_problems: bool = True
    verbose: bool = False


@dataclass(slots=True)
class InspectionReport:
    """Полный результат работы подкоманды html.

    :param options: С какими параметрами гоняли проверку.
    :param dump: Разобранный дамп.
    :param locators_total: Сколько локаторов собрано из репозитория.
    :param selectors_total: Сколько уникальных селекторов проверялось.
    :param checks: Результаты проверки по каждому локатору.
    :param status_counters: Счётчики по статусам.
    :param duration_seconds: Время работы.
    :param warnings: Предупреждения сборщика и парсеров (нерезолвящиеся базовые классы, усечённые снимки).
    """

    options: InspectionOptions
    dump: DumpDocument
    locators_total: int = 0
    selectors_total: int = 0
    checks: list[LocatorCheckResult] = field(default_factory=list)
    status_counters: dict[MatchStatus, int] = field(default_factory=dict)
    duration_seconds: float = 0.0
    warnings: list[str] = field(default_factory=list)

    @property
    def problems(self) -> list[LocatorCheckResult]:
        """Находки, требующие внимания.

        :return: Список результатов с is_problem, отсортированный по убыванию приоритета.
        """
        order = {Severity.HIGH: 0, Severity.MEDIUM: 1, Severity.LOW: 2, Severity.INFO: 3}
        return sorted((check for check in self.checks if check.is_problem), key=lambda item: order[item.severity])

    @property
    def exit_code(self) -> int:
        """Код возврата процесса.

        :return: 1, если найдены проблемы и включён fail_on_problems, иначе 0.
        """
        return 1 if self.options.fail_on_problems and self.problems else 0
