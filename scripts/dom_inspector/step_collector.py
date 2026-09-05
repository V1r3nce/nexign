"""Сборщик «шаг теста -> локаторы в порядке обращения».

Модуль отвечает на жалобу заказчика «мне нужно править конкретно свой сьют, а не все локаторы»:
вместо аудита всех 2682 локаторов репозитория он строит статически точный набор локаторов,
до которых дотягивается КОНКРЕТНЫЙ тест, и раскладывает его по блокам ``with allure.step(...)``.
Дальше step_report сверяет набор шага со снимком DOM того же шага.

Как это работает (только ast, ни один модуль проекта не импортируется — ``common/helpers/env_helper.py``
падает без ``.env``):

* локаторы берутся у :func:`scripts.dom_inspector.locator_collector.collect_locator_index`
  (второй сборщик писать нельзя), уже с развёрнутым наследованием: ``effective[qualname][ATTR]``;
* реестр классов ``pages/**`` строится здесь: базы, карта композиции ``self.<attr> = Класс()``,
  методы. Имена классов резолвятся ТОЛЬКО по карте импортов конкретного модуля — в репозитории
  есть тёзки (``PersonalAccountForm``, ``ConsumptionElements``), и глобальный словарь имён
  подсунул бы чужие селекторы;
* тест разбирается по setup-фикстуре (``self.<attr> = Пейдж()``), тело шага обходится рекурсивно
  с заходом в методы пейджей до ``max_depth`` (замер по сьюту: реально нужна глубина 4);
* при заходе в метод в качестве ``self`` передаётся ФАКТИЧЕСКИЙ класс объекта, а не класс,
  где метод объявлен (позднее связывание). Иначе ``DynamicForms.go_to_contacts_page`` вернул бы
  унаследованный ``NEXT_BTN``, тогда как ``IndividualCustomerCreate`` его переопределяет —
  отчёт показал бы правильное имя атрибута с чужим селектором;
* ветки ``if`` с вычислимым по литералам условием отсекаются (замер: 121 -> 99 локаторов на тесте),
  но ТОЛЬКО при достоверном вычислении: при любом сомнении берутся обе ветки, а локаторы из них
  помечаются ``conditional=True`` и красным не красятся.

Код вне ``allure.step``. Верхнеуровневые инструкции теста (``client = create_potential_organization``,
а в ``test_oapi_maintain_client.py`` — вообще всё тело) не выбрасываются, а собираются в псевдошаг
номер 0 «подготовка», который стоит в списке шагов первым. Решение взято из разведки: такой код
почти всегда является подготовкой данных перед первым шагом, а для сшивки со снимками псевдошаг
всё равно безопасен — он либо не трогает DOM вовсе, либо его локаторы повторно встретятся в шагах.
Локальные переменные-конструкторы, объявленные вне шагов, видны всем шагам теста.

Публичный интерфейс: :func:`collect_tests` и :func:`find_test` (плюс :func:`match_tests`
для отчёта о неоднозначности и :func:`load_locator_index` как обёртка над сборщиком локаторов).
"""

from __future__ import annotations

import ast
import re
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from pathlib import Path

from scripts.dom_inspector.locator_collector import CollectionResult, collect_locator_index, module_name_of
from scripts.dom_inspector.models import GapKind, LocatorRecord, LocatorUse, StepGap, TestCase, TestStep

#: Предел глубины захода в методы пейджей. Замер по сьюту e2e_64_13: максимум реально нужен 4
#: (``start_sale_with_product`` и ``create_customer_with_type``), поэтому 6 — запас с предупреждением.
DEFAULT_MAX_DEPTH: int = 6

#: Префиксы модулей, которые считаются пейджами и классами локаторов (по ним ходит обход).
PAGE_MODULE_PREFIXES: tuple[str, ...] = ("pages.",)

#: Префиксы модулей, обращения к которым пропускаются молча: это API-клиенты, не DOM.
SILENT_MODULE_PREFIXES: tuple[str, ...] = ("api.", "common.", "models.", "conftest")

#: Сентинел «self теста»: атрибуты берутся из карты setup-фикстуры, а не из реестра классов.
TEST_SELF: str = "<test>"

#: Метка псевдошага для кода вне ``allure.step``.
LOOSE_STEP_LABEL: str = "подготовка (код вне allure.step)"

#: Имя fixture-метода, в котором тест раздаёт себе пейдж-объекты. Приоритетное, но не единственное:
#: если метода с таким именем нет, разбираются все ``@pytest.fixture(autouse=True)`` класса.
SETUP_FIXTURE_NAME: str = "setup"

_UPPER_ATTR_RE: re.Pattern[str] = re.compile(r"^[A-Z][A-Z0-9_]*$")
_CASE_NO_RE: re.Pattern[str] = re.compile(r"^\s*(\d+)\s*[.)]")
_QUOTES_RE: re.Pattern[str] = re.compile(r"[«»“”„‘’'\"`]")
_MAX_SOURCE_LENGTH: int = 90

#: Значение параметра, которое статически не вычисляется.
_UNKNOWN: object = object()

#: Кэш реестра классов: разбор ``pages/**`` занимает заметное время, а cli зовёт сборщик не один раз.
_INDEX_CACHE: dict[str, ClassIndex] = {}


def _is_locator_attr(name: str) -> bool:
    """Похоже ли имя атрибута на локатор.

    :param name: Имя атрибута.
    :return: True для ``ADD_BTN`` и ``TITLE``, False для ``locators`` и ``create_agreement``.
    """
    return bool(_UPPER_ATTR_RE.match(name))


def _short(qualname: str) -> str:
    """Короткое имя класса из полного.

    :param qualname: Полное имя, например ``pages.nbss.client.client_profile_page.ClientProfilePage``.
    :return: Короткое имя, например ``ClientProfilePage``.
    """
    return qualname.rsplit(".", 1)[-1]


def _source_of(node: ast.AST) -> str:
    """Исходный текст выражения для отчёта.

    :param node: Узел ast.
    :return: Усечённая строка исходника.
    """
    try:
        text = ast.unparse(node)
    except (AttributeError, ValueError):
        return ""
    text = " ".join(text.split())
    return text if len(text) <= _MAX_SOURCE_LENGTH else f"{text[:_MAX_SOURCE_LENGTH]}..."


def normalize_title(text: str) -> str:
    """Нормализует заголовок для нечёткого сравнения.

    Кавычки в заголовках сьюта встречаются в четырёх начертаниях, поэтому все они схлопываются
    в один символ, пробелы схлопываются, регистр снимается.

    :param text: Исходный текст.
    :return: Нормализованный текст.
    """
    return " ".join(_QUOTES_RE.sub("'", text).split()).casefold()


@dataclass(slots=True)
class ClassNode:
    """Класс из ``pages/**``, разобранный через ast.

    :param qualname: Полное имя ``модуль.Класс``.
    :param module: Точечное имя модуля.
    :param name: Короткое имя класса.
    :param file: Путь к файлу относительно корня репозитория (posix).
    :param line: Строка объявления класса.
    :param bases: Полные имена базовых классов в порядке объявления.
    :param composition: Карта ``self.<attr> = Класс()`` из ``__init__`` -> полное имя класса.
    :param plain_attrs: Карта ``self.<attr> = <не конструктор>`` -> исходный текст (нужна,
        чтобы отличать ``self.page`` и ``self.category_map`` от потерянного пейдж-объекта).
    :param methods: Методы класса по имени.
    :param imports: Карта импортов модуля: локальное имя -> полное имя.
    """

    qualname: str
    module: str
    name: str
    file: str
    line: int
    bases: list[str] = field(default_factory=list)
    composition: dict[str, str] = field(default_factory=dict)
    plain_attrs: dict[str, str] = field(default_factory=dict)
    methods: dict[str, ast.FunctionDef | ast.AsyncFunctionDef] = field(default_factory=dict)
    imports: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class ClassIndex:
    """Реестр классов ``pages/**`` с линеаризацией наследования.

    :param classes: Классы по полному имени.
    :param by_name: Полные имена по короткому имени (для fallback при неоднозначном импорте).
    :param warnings: Предупреждения разбора (нечитаемые файлы, нерезолвящиеся базы).
    """

    classes: dict[str, ClassNode] = field(default_factory=dict)
    by_name: dict[str, list[str]] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    def mro(self, qualname: str) -> list[str]:
        """Линеаризует цепочку наследования в глубину.

        :param qualname: Полное имя класса.
        :return: Список полных имён от самого класса к дальним предкам, без повторов.
        """
        order: list[str] = []
        seen: set[str] = set()
        stack: list[str] = [qualname]
        while stack:
            current = stack.pop(0)
            if current in seen or current not in self.classes:
                continue
            seen.add(current)
            order.append(current)
            stack = [base for base in self.classes[current].bases if base not in seen] + stack
        return order

    def find_method(self, qualname: str, method: str) -> tuple[str, ast.FunctionDef | ast.AsyncFunctionDef] | None:
        """Ищет метод по цепочке наследования.

        :param qualname: Полное имя класса объекта.
        :param method: Имя метода.
        :return: Пара «класс, где метод объявлен» и его узел; None, если метода нет.
        """
        for ancestor in self.mro(qualname):
            node = self.classes[ancestor].methods.get(method)
            if node is not None:
                return ancestor, node
        return None

    def attr_class(self, qualname: str, attr: str) -> str | None:
        """Возвращает класс, присвоенный атрибуту композиции.

        :param qualname: Полное имя класса-владельца.
        :param attr: Имя атрибута, например ``locators``.
        :return: Полное имя класса либо None.
        """
        for ancestor in self.mro(qualname):
            found = self.classes[ancestor].composition.get(attr)
            if found is not None:
                return found
        return None

    def is_plain_attr(self, qualname: str, attr: str) -> bool:
        """Известно ли, что атрибут не является пейдж-объектом.

        :param qualname: Полное имя класса-владельца.
        :param attr: Имя атрибута.
        :return: True, если атрибут присваивается не конструктором класса.
        """
        return any(attr in self.classes[ancestor].plain_attrs for ancestor in self.mro(qualname))

    def file_of(self, qualname: str) -> str:
        """Файл, в котором объявлен класс.

        :param qualname: Полное имя класса.
        :return: Путь относительно корня репозитория; пустая строка, если класс неизвестен.
        """
        node = self.classes.get(qualname)
        return node.file if node is not None else ""

    def resolve_name(self, name: str, module: str, imports: dict[str, str]) -> str | None:
        """Резолвит имя класса в полное имя ТОЛЬКО через карту импортов модуля.

        Глобальный словарь «короткое имя -> класс» здесь запрещён: в репозитории есть тёзки
        ``PersonalAccountForm`` и ``ConsumptionElements``, и он подсунул бы чужие селекторы.

        :param name: Локальное имя класса в модуле.
        :param module: Точечное имя модуля, где встретилось имя.
        :param imports: Карта импортов этого модуля.
        :return: Полное имя класса либо None.
        """
        imported = imports.get(name)
        if imported and imported in self.classes:
            return imported
        same_module = f"{module}.{name}"
        if same_module in self.classes:
            return same_module
        if imported:
            return imported if imported.rsplit(".", 1)[-1] == name else None
        candidates = self.by_name.get(name, [])
        return candidates[0] if len(candidates) == 1 else None


def _imports_of(tree: ast.Module) -> dict[str, str]:
    """Собирает карту импортов модуля.

    :param tree: Разобранный модуль.
    :return: Карта «локальное имя -> полное точечное имя».
    """
    imports: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            for alias in node.names:
                imports[alias.asname or alias.name] = f"{node.module}.{alias.name}"
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports[alias.asname or alias.name] = alias.name
    return imports


def _self_attr_target(target: ast.expr) -> str | None:
    """Возвращает имя атрибута для присваивания вида ``self.<attr> = ...``.

    :param target: Левая часть присваивания.
    :return: Имя атрибута либо None.
    """
    if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == "self":
        return target.attr
    return None


def _iter_self_assignments(node: ast.AST) -> Iterable[tuple[str, ast.expr]]:
    """Перебирает присваивания ``self.<attr> = <выражение>`` внутри функции.

    :param node: Узел функции.
    :return: Пары «имя атрибута, выражение».
    """
    for statement in ast.walk(node):
        if isinstance(statement, ast.Assign):
            for target in statement.targets:
                attr = _self_attr_target(target)
                if attr is not None:
                    yield attr, statement.value
        elif isinstance(statement, ast.AnnAssign) and statement.value is not None:
            attr = _self_attr_target(statement.target)
            if attr is not None:
                yield attr, statement.value


def _constructor_name(value: ast.expr) -> str | None:
    """Возвращает имя класса для выражения-конструктора.

    :param value: Правая часть присваивания.
    :return: Локальное имя класса либо None, если это не вызов конструктора.
    """
    if not isinstance(value, ast.Call):
        return None
    if isinstance(value.func, ast.Name):
        return value.func.id
    if isinstance(value.func, ast.Attribute) and value.func.attr[:1].isupper():
        return value.func.attr
    return None


def build_class_index(pages_root: Path, project_root: Path, use_cache: bool = True) -> ClassIndex:
    """Строит реестр классов каталога ``pages/**``.

    Разбираются только классы верхнего уровня: композиция из ``__init__``, методы, базы.
    Атрибуты в ВЕРХНЕМ РЕГИСТРЕ из ``__init__`` пропускаются — это локаторы, ими занимается
    locator_collector.

    :param pages_root: Каталог ``pages`` репозитория.
    :param project_root: Корень репозитория.
    :param use_cache: Использовать ли кэш по пути каталога.
    :return: Реестр классов.
    """
    cache_key = str(pages_root.resolve())
    if use_cache and cache_key in _INDEX_CACHE:
        return _INDEX_CACHE[cache_key]

    index = ClassIndex()
    for path in sorted(pages_root.rglob("*.py")):
        if not path.is_file():
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (OSError, SyntaxError, UnicodeDecodeError) as error:
            index.warnings.append(f"{path}: не разобран ({error})")
            continue
        module = module_name_of(path, project_root)
        imports = _imports_of(tree)
        file = _relative_posix(path, project_root)
        for node in tree.body:
            if not isinstance(node, ast.ClassDef):
                continue
            info = ClassNode(
                qualname=f"{module}.{node.name}",
                module=module,
                name=node.name,
                file=file,
                line=node.lineno,
                imports=imports,
            )
            for base in node.bases:
                base_name = base.id if isinstance(base, ast.Name) else getattr(base, "attr", None)
                if base_name:
                    info.bases.append(imports.get(base_name, f"{module}.{base_name}"))
            for item in node.body:
                if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
                    info.methods[item.name] = item
            init = info.methods.get("__init__")
            if init is not None:
                _fill_composition(init, info, imports, module)
            index.classes[info.qualname] = info
            index.by_name.setdefault(node.name, []).append(info.qualname)
    if use_cache:
        _INDEX_CACHE[cache_key] = index
    return index


def _fill_composition(
    init: ast.FunctionDef | ast.AsyncFunctionDef, info: ClassNode, imports: dict[str, str], module: str
) -> None:
    """Заполняет карты композиции и «не пейджей» по телу ``__init__``.

    :param init: Узел ``__init__``.
    :param info: Заполняемый класс.
    :param imports: Карта импортов модуля.
    :param module: Точечное имя модуля.
    :return: Ничего.
    """
    for attr, value in _iter_self_assignments(init):
        if _is_locator_attr(attr):
            continue
        class_name = _constructor_name(value)
        if class_name is None:
            info.plain_attrs[attr] = _source_of(value)
            continue
        info.composition[attr] = imports.get(class_name, f"{module}.{class_name}")


def _relative_posix(path: Path, project_root: Path) -> str:
    """Путь относительно корня репозитория в posix-виде.

    :param path: Путь к файлу.
    :param project_root: Корень репозитория.
    :return: Например ``pages/nbss/client/client_profile_page.py``.
    """
    try:
        return path.resolve().relative_to(project_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


@dataclass(slots=True)
class _Frame:
    """Контекст обхода одного тела метода.

    :param self_class: Полное имя класса, который является ``self`` в этом теле
        (для тела теста — сентинел :data:`TEST_SELF`).
    :param locals_map: Локальные переменные-конструкторы: имя -> полное имя класса.
    :param binds: Значения параметров метода, вычисленные по литералам вызова.
    :param file: Файл, из которого взято тело (для адресов в отчёте).
    :param via: Цепочка методов, по которой сюда пришли.
    :param dicts: Локальные словари-диспетчеры: имя переменной -> {литеральный ключ: выражение}.
        Нужны для ``forms = {"individual": self.individual_customer_create_form, ...}``
        с последующим ``forms[customer_type]`` — без них теряется вся форма создания клиента.
    :param module: Точечное имя модуля, из которого взято тело (для резолва имён классов).
    :param imports: Карта импортов этого модуля.
    :param unknown_returns: Локальные переменные, класс которых определить не удалось,
        с заготовленной записью о пробеле. Запись превращается в находку отчёта только тогда,
        когда через такую переменную реально пытаются достать локатор или вызвать метод —
        иначе ``file_name = self.create_agreement_text_file(...)`` шумел бы на ровном месте.
    """

    self_class: str
    locals_map: dict[str, str]
    binds: dict[str, object]
    file: str
    via: tuple[str, ...] = ()
    dicts: dict[str, dict[object, ast.expr]] = field(default_factory=dict)
    module: str = ""
    imports: dict[str, str] = field(default_factory=dict)
    unknown_returns: dict[str, StepGap] = field(default_factory=dict)


class _StepWalker:
    """Обходчик тела шага: собирает обращения к локаторам в порядке исходника."""

    def __init__(
        self,
        index: ClassIndex,
        locators: CollectionResult,
        test_attrs: dict[str, str],
        max_depth: int = DEFAULT_MAX_DEPTH,
        test_skipped: dict[str, str] | None = None,
        test_class: str = "",
    ) -> None:
        """Готовит обходчик.

        :param index: Реестр классов ``pages/**``.
        :param locators: Результат сбора локаторов.
        :param test_attrs: Карта ``self.<attr> -> класс`` из setup-фикстуры теста.
        :param max_depth: Предел глубины захода в методы.
        :param test_skipped: Атрибуты setup, про которые уже известно, что это не пейдж.
        :param test_class: Имя тест-класса — нужно только для текста заметки разбора.
        """
        self.index = index
        self.locators = locators
        self.test_attrs = test_attrs
        self.test_skipped = test_skipped or {}
        self.test_class = test_class
        self.max_depth = max_depth
        self.uses: list[LocatorUse] = []
        self.gaps: list[StepGap] = []
        self.calls_walked: int = 0
        self.max_depth_seen: int = 0
        self._seen_uses: set[tuple[str, str]] = set()
        self._seen_gaps: set[tuple[str, str, int, str]] = set()
        self._active: set[tuple[str, str]] = set()
        self._call_returns: dict[int, str] = {}
        self._call_return_gaps: dict[int, StepGap] = {}

    # ------------------------------------------------------------------ запись результатов
    def _emit_use(self, use: LocatorUse) -> None:
        """Добавляет обращение к локатору с дедупликацией «первое вхождение побеждает».

        :param use: Обращение.
        :return: Ничего.
        """
        key = (use.owner_class, use.record.attr)
        if key in self._seen_uses:
            return
        self._seen_uses.add(key)
        self.uses.append(use)

    def _emit_gap(self, gap: StepGap) -> None:
        """Добавляет неразрешённое обращение с дедупликацией.

        :param gap: Описание проблемы.
        :return: Ничего.
        """
        key = (gap.kind.value, gap.source_file, gap.line, gap.source or gap.attr)
        if key in self._seen_gaps:
            return
        self._seen_gaps.add(key)
        self.gaps.append(gap)

    # ------------------------------------------------------------------ разрешение владельца
    def _owner_of(self, node: ast.expr, frame: _Frame) -> str | None:
        """Рекурсивно разрешает выражение в полное имя класса-владельца.

        Рекурсия обязательна: в тестах цепочки трёхзвенные
        (``self.client_profile_page.locators.CLIENT_STATUS``).

        :param node: Выражение слева от атрибута.
        :param frame: Текущий контекст обхода.
        :return: Полное имя класса, сентинел :data:`TEST_SELF` либо None.
        """
        if isinstance(node, ast.Name):
            if node.id == "self":
                return frame.self_class
            return frame.locals_map.get(node.id)
        if isinstance(node, ast.Attribute):
            base = self._owner_of(node.value, frame)
            if base is None:
                return None
            if base == TEST_SELF:
                return self.test_attrs.get(node.attr)
            return self.index.attr_class(base, node.attr)
        if isinstance(node, ast.Call):
            class_name = _constructor_name(node)
            if class_name is None:
                return None
            return self._resolve_class(class_name, frame)
        if isinstance(node, ast.Subscript):
            return self._subscript_owner(node, frame)
        return None

    def _subscript_owner(self, node: ast.Subscript, frame: _Frame) -> str | None:
        """Разрешает обращение по индексу.

        Для локального словаря-диспетчера (``forms[customer_type]``) ключ вычисляется по
        связанным литералам и берётся ровно одно значение; если ключ неизвестен, гадать нельзя —
        возвращается None. Для списочных локаторов (``ROWS[2]``) владельцем остаётся сам объект.

        :param node: Узел обращения по индексу.
        :param frame: Текущий контекст обхода.
        :return: Полное имя класса либо None.
        """
        if isinstance(node.value, ast.Name):
            mapping = frame.dicts.get(node.value.id)
            if mapping is not None:
                key = self._value_of(node.slice, frame.binds)
                if key is _UNKNOWN:
                    return None
                target = mapping.get(key)
                return self._owner_of(target, frame) if target is not None else None
        return self._owner_of(node.value, frame)

    def _resolve_class(self, class_name: str, frame: _Frame) -> str | None:
        """Резолвит имя класса, встреченное в теле метода, по карте импортов его модуля.

        Глобальный словарь имён здесь запрещён: у тёзок ``PersonalAccountForm``
        и ``ConsumptionElements`` он подсунет чужой класс и чужие селекторы.

        :param class_name: Локальное имя класса.
        :param frame: Текущий контекст обхода.
        :return: Полное имя класса либо None.
        """
        if frame.module:
            return self.index.resolve_name(class_name, frame.module, frame.imports)
        node = self.index.classes.get(frame.self_class)
        if node is None:
            return None
        return self.index.resolve_name(class_name, node.module, node.imports)

    def _chain_root(self, node: ast.expr) -> ast.expr:
        """Возвращает самый левый узел цепочки атрибутов.

        :param node: Выражение.
        :return: Корневой узел (обычно ``ast.Name``).
        """
        current = node
        while isinstance(current, ast.Attribute | ast.Subscript):
            current = current.value
        return current

    def _touches_locator(self, node: ast.expr) -> bool:
        """Является ли выражение обращением к самому локатору (а не к пейджу).

        Нужно, чтобы ``self.locators.X.wait_to_be_visible()`` не превращалось в «метод не найден»:
        получатель здесь — обёртка Element из ``pages/ui_elements.py``, а не пейдж-объект.

        :param node: Выражение-получатель вызова.
        :return: True, если в цепочке есть атрибут в ВЕРХНЕМ РЕГИСТРЕ.
        """
        current = node
        while True:
            if isinstance(current, ast.Attribute):
                if _is_locator_attr(current.attr):
                    return True
                current = current.value
            elif isinstance(current, ast.Subscript):
                current = current.value
            elif isinstance(current, ast.Call):
                current = current.func
            else:
                return False

    # ------------------------------------------------------------------ вычисление веток
    def _value_of(self, node: ast.expr, binds: dict[str, object]) -> object:
        """Вычисляет значение выражения по литералам и связанным параметрам.

        :param node: Выражение.
        :param binds: Карта «параметр -> значение».
        :return: Значение либо сентинел «неизвестно».
        """
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.Name):
            return binds.get(node.id, _UNKNOWN)
        return _UNKNOWN

    def _truth(self, test: ast.expr, binds: dict[str, object]) -> bool | None:
        """Пытается достоверно вычислить условие ветвления.

        Правило жёсткое: при любом сомнении возвращается None и берутся ОБЕ ветки —
        ложный минус (умолчали про сломанный локатор) хуже лишней строки в отчёте.

        :param test: Условие ``if``.
        :param binds: Карта «параметр -> значение».
        :return: True / False либо None, если вычислить достоверно нельзя.
        """
        if isinstance(test, ast.Constant):
            return bool(test.value)
        if isinstance(test, ast.Name):
            value = self._value_of(test, binds)
            return None if value is _UNKNOWN else bool(value)
        if isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not):
            inner = self._truth(test.operand, binds)
            return None if inner is None else not inner
        if isinstance(test, ast.Compare) and len(test.ops) == 1:
            left = self._value_of(test.left, binds)
            right = self._value_of(test.comparators[0], binds)
            if left is _UNKNOWN or right is _UNKNOWN:
                return None
            operator = test.ops[0]
            if isinstance(operator, ast.Eq):
                return left == right
            if isinstance(operator, ast.NotEq):
                return left != right
            if isinstance(operator, ast.Is):
                return left is right
            if isinstance(operator, ast.IsNot):
                return left is not right
            return None
        if isinstance(test, ast.BoolOp):
            verdicts = [self._truth(value, binds) for value in test.values]
            if isinstance(test.op, ast.And):
                if any(verdict is False for verdict in verdicts):
                    return False
                return True if all(verdict is True for verdict in verdicts) else None
            if any(verdict is True for verdict in verdicts):
                return True
            return False if all(verdict is False for verdict in verdicts) else None
        return None

    # ------------------------------------------------------------------ связывание аргументов
    def _bind_args(
        self,
        function: ast.FunctionDef | ast.AsyncFunctionDef,
        call: ast.Call,
        caller_binds: dict[str, object],
    ) -> dict[str, object]:
        """Строит карту «параметр метода -> литеральное значение».

        :param function: Узел вызываемого метода.
        :param call: Узел вызова.
        :param caller_binds: Карта параметров вызывающего (чтобы прокидывать значения дальше).
        :return: Карта параметров вызываемого метода.
        """
        positional = [arg.arg for arg in function.args.posonlyargs] + [arg.arg for arg in function.args.args]
        binds: dict[str, object] = {name: _UNKNOWN for name in positional}
        defaults = function.args.defaults
        if defaults:
            for name, default in zip(positional[len(positional) - len(defaults) :], defaults, strict=False):
                binds[name] = default.value if isinstance(default, ast.Constant) else _UNKNOWN
        for keyword_arg, default in zip(function.args.kwonlyargs, function.args.kw_defaults, strict=False):
            binds[keyword_arg.arg] = default.value if isinstance(default, ast.Constant) else _UNKNOWN

        bindable = [name for name in positional if name != "self"]
        for position, argument in enumerate(call.args):
            if position < len(bindable):
                binds[bindable[position]] = self._value_of(argument, caller_binds)
        for keyword in call.keywords:
            if keyword.arg:
                binds[keyword.arg] = self._value_of(keyword.value, caller_binds)
        return binds

    # ------------------------------------------------------------------ обход
    def walk(self, body: Sequence[ast.stmt], frame: _Frame, depth: int = 0, conditional: bool = False) -> None:
        """Обходит список инструкций.

        :param body: Инструкции.
        :param frame: Контекст обхода.
        :param depth: Текущая глубина.
        :param conditional: True, если инструкции лежат в невычисленной ветке.
        :return: Ничего.
        """
        self.max_depth_seen = max(self.max_depth_seen, depth)
        for statement in body:
            self._walk_statement(statement, frame, depth, conditional)

    def _walk_statement(self, statement: ast.stmt, frame: _Frame, depth: int, conditional: bool) -> None:
        """Обходит одну инструкцию, разворачивая составные конструкции.

        :param statement: Инструкция.
        :param frame: Контекст обхода.
        :param depth: Текущая глубина.
        :param conditional: True, если инструкция лежит в невычисленной ветке.
        :return: Ничего.
        """
        if isinstance(statement, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
            return
        if isinstance(statement, ast.If):
            self._walk_expression(statement.test, frame, depth, conditional)
            verdict = self._truth(statement.test, frame.binds)
            if verdict is True:
                self.walk(statement.body, frame, depth, conditional)
                return
            if verdict is False:
                self.walk(statement.orelse, frame, depth, conditional)
                return
            self._emit_gap(
                StepGap(
                    kind=GapKind.BRANCH_UNKNOWN,
                    reason="ветка не определена статически, взяты обе",
                    source=_source_of(statement.test),
                    line=statement.lineno,
                    source_file=frame.file,
                    depth=depth,
                )
            )
            self.walk(statement.body, frame, depth, True)
            self.walk(statement.orelse, frame, depth, True)
            return
        if isinstance(statement, ast.For | ast.AsyncFor):
            self._walk_expression(statement.iter, frame, depth, conditional)
            self.walk(statement.body, frame, depth, conditional)
            self.walk(statement.orelse, frame, depth, conditional)
            return
        if isinstance(statement, ast.While):
            self._walk_expression(statement.test, frame, depth, conditional)
            self.walk(statement.body, frame, depth, conditional)
            self.walk(statement.orelse, frame, depth, conditional)
            return
        if isinstance(statement, ast.With | ast.AsyncWith):
            for item in statement.items:
                self._walk_expression(item.context_expr, frame, depth, conditional)
            self.walk(statement.body, frame, depth, conditional)
            return
        if isinstance(statement, ast.Try):
            self.walk(statement.body, frame, depth, conditional)
            for handler in statement.handlers:
                self.walk(handler.body, frame, depth, True)
            self.walk(statement.orelse, frame, depth, True)
            self.walk(statement.finalbody, frame, depth, conditional)
            return
        if isinstance(statement, ast.Match):
            self._walk_match(statement, frame, depth, conditional)
            return
        self._register_locals(statement, frame)
        self._walk_expression(statement, frame, depth, conditional)
        self._bind_call_return(statement, frame)

    def _walk_match(self, statement: ast.Match, frame: _Frame, depth: int, conditional: bool) -> None:
        """Обходит ``match`` с отсечением заведомо мёртвых веток.

        Ветка берётся одна, только если значение subject достоверно вычислено по литералам
        (``open_create_customer_form_and_fill("individual", ...)``). Во всех прочих случаях
        берутся все ветки, в отчёт идёт пометка о невычисленном ветвлении, а локаторы
        помечаются условными.

        :param statement: Узел ``match``.
        :param frame: Контекст обхода.
        :param depth: Текущая глубина.
        :param conditional: True, если ``match`` лежит в невычисленной ветке.
        :return: Ничего.
        """
        self._walk_expression(statement.subject, frame, depth, conditional)
        subject = self._value_of(statement.subject, frame.binds)
        if subject is not _UNKNOWN:
            for case in statement.cases:
                if case.guard is not None:
                    break
                pattern = case.pattern
                if isinstance(pattern, ast.MatchValue) and isinstance(pattern.value, ast.Constant):
                    if pattern.value.value == subject:
                        self.walk(case.body, frame, depth, conditional)
                        return
                    continue
                if isinstance(pattern, ast.MatchAs) and pattern.pattern is None:
                    self.walk(case.body, frame, depth, conditional)
                    return
                break
            else:
                return
        self._emit_gap(
            StepGap(
                kind=GapKind.BRANCH_UNKNOWN,
                reason="ветка match не определена статически, взяты все",
                source=_source_of(statement.subject),
                line=statement.lineno,
                source_file=frame.file,
                depth=depth,
            )
        )
        for case in statement.cases:
            self.walk(case.body, frame, depth, True)

    def _register_locals(self, statement: ast.stmt, frame: _Frame) -> None:
        """Запоминает локальные переменные-конструкторы и словари-диспетчеры.

        Конструкторов в ``pages/`` 25 штук (например ``create_request_form = CreateSalesAndServiceManagement()``
        внутри ``InquiriesPage.fill_inquiry_create_form``); без этой карты из шага «создана продажа»
        выпадают десятки локаторов формы. Словари вида ``forms = {"individual": self.form, ...}``
        нужны, чтобы разрешить ``forms[customer_type]``.

        :param statement: Инструкция.
        :param frame: Контекст обхода.
        :return: Ничего.
        """
        if not isinstance(statement, ast.Assign):
            return
        if isinstance(statement.value, ast.Dict):
            mapping = {
                key.value: value
                for key, value in zip(statement.value.keys, statement.value.values, strict=False)
                if isinstance(key, ast.Constant)
            }
            for target in statement.targets:
                if isinstance(target, ast.Name) and mapping:
                    frame.dicts[target.id] = mapping
            return
        class_name = _constructor_name(statement.value)
        if class_name is None:
            return
        resolved = self._resolve_class(class_name, frame)
        if resolved is None:
            return
        for target in statement.targets:
            if isinstance(target, ast.Name):
                frame.locals_map[target.id] = resolved

    def _bind_call_return(self, statement: ast.stmt, frame: _Frame) -> None:
        """Связывает локальную переменную с классом, который вернул вызванный метод пейджа.

        Без этого ``form = self.get_customer_create_form(customer_type)`` теряет всю форму
        создания клиента: последующие ``form.fill_...`` не резолвятся и молча дают ноль локаторов.

        :param statement: Инструкция присваивания.
        :param frame: Контекст обхода.
        :return: Ничего.
        """
        if not isinstance(statement, ast.Assign) or not isinstance(statement.value, ast.Call):
            return
        inferred = self._call_returns.pop(id(statement.value), None)
        pending = self._call_return_gaps.pop(id(statement.value), None)
        for target in statement.targets:
            if not isinstance(target, ast.Name):
                continue
            if inferred is not None:
                frame.locals_map[target.id] = inferred
            elif pending is not None:
                frame.unknown_returns[target.id] = pending

    def _walk_expression(self, node: ast.AST, frame: _Frame, depth: int, conditional: bool) -> None:
        """Обходит выражения одной инструкции в порядке исходника.

        Порядок: сортировка по ``(строка, колонка)``, а при равной позиции сначала ``Attribute``
        (сам локатор), потом ``Call`` (заход в метод) — иначе у ``self.x.LOC.wait_to_have_text(...)``
        порядок узлов неустойчив и аргументы вызова могут дать локаторы раньше получателя.

        :param node: Узел инструкции или выражения.
        :param frame: Контекст обхода.
        :param depth: Текущая глубина.
        :param conditional: True, если выражение лежит в невычисленной ветке.
        :return: Ничего.
        """
        subscripted = {id(item.value) for item in ast.walk(node) if isinstance(item, ast.Subscript)}
        dispatched = self._dispatch_values(node)
        nodes = [item for item in ast.walk(node) if isinstance(item, ast.Attribute | ast.Call)]
        nodes.sort(
            key=lambda item: (
                getattr(item, "lineno", 0),
                getattr(item, "col_offset", 0),
                0 if isinstance(item, ast.Attribute) else 1,
            )
        )
        for item in nodes:
            if isinstance(item, ast.Attribute):
                self._handle_attribute(
                    item,
                    frame,
                    depth,
                    conditional or id(item) in dispatched,
                    id(item) in subscripted,
                )
            else:
                self._handle_call(item, frame, depth, conditional)

    def _dispatch_values(self, node: ast.AST) -> set[int]:
        """Помечает локаторы, лежащие значениями словаря-диспетчера.

        В ``buttons = {"individual": self.locators.CREATE_CUSTOMER_BTN, ...}`` реально нажимается
        ровно одна кнопка, а в набор шага попадают все три. Красить их красным нельзя —
        такие обращения помечаются условными.

        :param node: Узел инструкции.
        :return: Множество ``id`` узлов-значений словарей.
        """
        marked: set[int] = set()
        for item in ast.walk(node):
            if not isinstance(item, ast.Dict):
                continue
            for value in item.values:
                marked.update(id(inner) for inner in ast.walk(value))
        return marked

    def _handle_attribute(
        self,
        node: ast.Attribute,
        frame: _Frame,
        depth: int,
        conditional: bool,
        subscripted: bool,
    ) -> None:
        """Обрабатывает обращение к атрибуту в ВЕРХНЕМ РЕГИСТРЕ — кандидату в локаторы.

        :param node: Узел атрибута.
        :param frame: Контекст обхода.
        :param depth: Текущая глубина.
        :param conditional: True, если обращение лежит в невычисленной ветке.
        :param subscripted: True, если к атрибуту обращаются по индексу.
        :return: Ничего.
        """
        if not _is_locator_attr(node.attr):
            return
        owner = self._owner_of(node.value, frame)
        if owner is None or owner == TEST_SELF:
            root = self._chain_root(node.value)
            if isinstance(root, ast.Name) and self._report_unknown_return(root.id, frame):
                return
            if isinstance(root, ast.Name) and root.id == "self":
                self._emit_gap(
                    StepGap(
                        kind=GapKind.OWNER_UNRESOLVED,
                        reason="не разрешён владелец локатора",
                        source=_source_of(node),
                        line=node.lineno,
                        source_file=frame.file,
                        attr=node.attr,
                        depth=depth,
                    )
                )
            return
        record = self._locator_of(owner, node.attr)
        if record is None:
            self._emit_gap(
                StepGap(
                    kind=GapKind.LOCATOR_UNKNOWN,
                    reason=f"локатор {_short(owner)}.{node.attr} не найден среди собранных",
                    source=_source_of(node),
                    line=node.lineno,
                    source_file=frame.file,
                    owner=owner,
                    attr=node.attr,
                    depth=depth,
                )
            )
            return
        self._emit_use(
            LocatorUse(
                record=record,
                owner_class=owner,
                depth=depth,
                line=node.lineno,
                source_file=frame.file,
                conditional=conditional,
                via=frame.via,
                subscripted=subscripted or record.is_list,
            )
        )

    def _report_unknown_self_attr(self, node: ast.expr, frame: _Frame, call: ast.Call, depth: int) -> None:
        """Печатает заметку о вызове ``self.<attr>.<метод>()``, чей пейдж-объект не разрешён.

        Без неё потеря молчаливая: если у класса нет setup-фикстуры или в ней нет этого атрибута,
        весь вызов вместе с его локаторами просто выпадает, а шаг выглядит зелёным и пустым.

        :param node: Выражение слева от вызванного метода.
        :param frame: Контекст обхода.
        :param call: Узел вызова — для адреса и текста заметки.
        :param depth: Текущая глубина.
        :return: Ничего.
        """
        if not isinstance(node, ast.Attribute) or self._owner_of(node.value, frame) != TEST_SELF:
            return
        if node.attr in self.test_attrs or node.attr in self.test_skipped:
            return
        where = f"в {self.test_class}" if self.test_class else "в тест-классе"
        method = f".{call.func.attr}()" if isinstance(call.func, ast.Attribute) else "()"
        reason = (
            f"self.{node.attr} не разрешён: {where} нет setup-фикстуры с таким атрибутом — "
            f"вызов {method} и его локаторы в шаг не попали"
        )
        self._emit_gap(
            StepGap(
                kind=GapKind.SETUP_ATTR,
                reason=reason,
                source=_source_of(call),
                line=call.lineno,
                source_file=frame.file,
                attr=node.attr,
                depth=depth,
            )
        )

    def _report_unknown_return(self, name: str, frame: _Frame) -> bool:
        """Печатает отложенную запись о неопределённом классе результата.

        Запись превращается в находку только здесь — в момент, когда через такую переменную
        реально пытаются достать локатор или вызвать метод. Пока переменная лежит без дела
        (имя файла, номер, флаг), шуметь не о чем.

        :param name: Имя локальной переменной.
        :param frame: Контекст обхода.
        :return: True, если запись нашлась и была напечатана.
        """
        pending = frame.unknown_returns.get(name)
        if pending is None:
            return False
        self._emit_gap(pending)
        return True

    def _locator_of(self, owner: str, attr: str) -> LocatorRecord | None:
        """Достаёт запись локатора из эффективного набора класса.

        :param owner: Полное имя класса-владельца.
        :param attr: Имя атрибута.
        :return: Запись локатора либо None.
        """
        effective = self.locators.effective.get(owner)
        if effective is None:
            return None
        return effective.get(attr)

    def _handle_call(self, node: ast.Call, frame: _Frame, depth: int, conditional: bool) -> None:
        """Обрабатывает вызов метода: заходит внутрь метода пейджа или класса локаторов.

        :param node: Узел вызова.
        :param frame: Контекст обхода.
        :param depth: Текущая глубина.
        :param conditional: True, если вызов лежит в невычисленной ветке.
        :return: Ничего.
        """
        function = node.func
        if not isinstance(function, ast.Attribute) or _is_locator_attr(function.attr):
            return
        if self._touches_locator(function.value):
            return
        owner = self._owner_of(function.value, frame)
        if owner is None or owner == TEST_SELF:
            root = self._chain_root(function.value)
            if isinstance(root, ast.Name):
                self._report_unknown_return(root.id, frame)
            self._report_unknown_self_attr(function.value, frame, node, depth)
            return
        if not owner.startswith(PAGE_MODULE_PREFIXES):
            return
        found = self.index.find_method(owner, function.attr)
        if found is None:
            if owner in self.index.classes:
                self._emit_gap(
                    StepGap(
                        kind=GapKind.METHOD_UNKNOWN,
                        reason=f"метод {_short(owner)}.{function.attr} не разобран",
                        source=_source_of(node),
                        line=node.lineno,
                        source_file=frame.file,
                        owner=owner,
                        attr=function.attr,
                        depth=depth,
                    )
                )
            return
        declaring, method_node = found
        key = (owner, function.attr)
        if key in self._active:
            self._emit_gap(
                StepGap(
                    kind=GapKind.RECURSION,
                    reason=f"рекурсивный вызов {_short(owner)}.{function.attr} отсечён",
                    source=_source_of(node),
                    line=node.lineno,
                    source_file=frame.file,
                    owner=owner,
                    attr=function.attr,
                    depth=depth,
                )
            )
            return
        if depth + 1 > self.max_depth:
            self._emit_gap(
                StepGap(
                    kind=GapKind.DEPTH_LIMIT,
                    reason=f"предел глубины {self.max_depth}: {_short(owner)}.{function.attr} не раскрыт",
                    source=_source_of(node),
                    line=node.lineno,
                    source_file=frame.file,
                    owner=owner,
                    attr=function.attr,
                    depth=depth,
                )
            )
            return
        declaring_node = self.index.classes.get(declaring)
        child = _Frame(
            self_class=owner,
            locals_map={},
            binds=self._bind_args(method_node, node, frame.binds),
            file=self.index.file_of(declaring) or frame.file,
            via=frame.via + (f"{_short(owner)}.{function.attr}",),
            module=declaring_node.module if declaring_node is not None else "",
            imports=declaring_node.imports if declaring_node is not None else {},
        )
        self.calls_walked += 1
        self._active.add(key)
        try:
            self.walk(method_node.body, child, depth + 1, conditional)
        finally:
            self._active.discard(key)
        self._infer_return(node, method_node, child, depth)

    def _infer_return(
        self,
        call: ast.Call,
        method_node: ast.FunctionDef | ast.AsyncFunctionDef,
        child: _Frame,
        depth: int,
    ) -> None:
        """Определяет класс возвращаемого методом объекта и запоминает его для присваивания.

        Порядок: сначала само выражение ``return`` (оно разрешается уже после обхода тела,
        когда известны локальные переменные и словари-диспетчеры), затем аннотация возврата,
        если она называет ровно один известный класс. Если вернуть класс не удалось,
        а по виду возвращается объект — это записывается в пробелы, а не проглатывается.

        :param call: Узел вызова.
        :param method_node: Узел вызванного метода.
        :param child: Контекст тела метода после обхода.
        :param depth: Текущая глубина.
        :return: Ничего.
        """
        returns = [item for item in ast.walk(method_node) if isinstance(item, ast.Return) and item.value is not None]
        for item in returns:
            resolved = self._owner_of(item.value, child)
            if resolved is not None and resolved in self.index.classes:
                self._call_returns[id(call)] = resolved
                return
        annotated = self._annotation_classes(method_node.returns, child)
        if len(annotated) == 1:
            self._call_returns[id(call)] = annotated[0]
            return
        if not returns:
            return
        variants = f" (кандидаты: {', '.join(_short(name) for name in annotated)})" if annotated else ""
        self._call_return_gaps[id(call)] = StepGap(
            kind=GapKind.RETURN_UNRESOLVED,
            reason=f"класс результата {_short(child.self_class)}.{method_node.name} не определён{variants}",
            source=_source_of(call),
            line=call.lineno,
            source_file=child.file,
            owner=child.self_class,
            attr=method_node.name,
            depth=depth,
        )

    def _annotation_classes(self, annotation: ast.expr | None, frame: _Frame) -> list[str]:
        """Возвращает классы ``pages/**``, названные в аннотации возврата.

        :param annotation: Узел аннотации (``-> IndividualCustomerCreate`` или ``-> Union[...]``).
        :param frame: Контекст тела метода (нужны модуль и его импорты).
        :return: Полные имена найденных классов без повторов, в порядке появления.
        """
        if annotation is None:
            return []
        found: list[str] = []
        for item in ast.walk(annotation):
            name = item.id if isinstance(item, ast.Name) else item.attr if isinstance(item, ast.Attribute) else None
            if not name or not name[:1].isupper():
                continue
            resolved = self._resolve_class(name, frame)
            if resolved is not None and resolved in self.index.classes and resolved not in found:
                found.append(resolved)
        return found


def _decorator_argument(decorator: ast.expr, name: str) -> str | None:
    """Возвращает первый аргумент декоратора ``allure.<name>(...)``.

    :param decorator: Узел декоратора.
    :param name: Имя декоратора (``id``, ``title``, ``epic``, ``suite``).
    :return: Значение строкой либо None.
    """
    if not isinstance(decorator, ast.Call) or not isinstance(decorator.func, ast.Attribute):
        return None
    if decorator.func.attr != name or not decorator.args:
        return None
    argument = decorator.args[0]
    if isinstance(argument, ast.Constant):
        return str(argument.value)
    return _source_of(argument)


def _skip_reason(decorators: Sequence[ast.expr]) -> str | None:
    """Ищет ``@pytest.mark.skip`` и возвращает причину.

    Скипнутые тесты обязаны быть видны в отчёте: в сьюте есть
    ``test_fill_individual_attributes_and_repeat_agreement_check`` с багом RMBSS-18239.

    :param decorators: Декораторы тест-метода.
    :return: Текст причины (или пустая строка, если причина не указана); None, если скипа нет.
    """
    for decorator in decorators:
        target = decorator.func if isinstance(decorator, ast.Call) else decorator
        if not isinstance(target, ast.Attribute) or target.attr not in {"skip", "skipif"}:
            continue
        if not isinstance(decorator, ast.Call):
            return ""
        for keyword in decorator.keywords:
            if keyword.arg == "reason" and isinstance(keyword.value, ast.Constant):
                return str(keyword.value.value)
        if decorator.args and isinstance(decorator.args[0], ast.Constant):
            return str(decorator.args[0].value)
        return ""
    return None


def _case_no_of(title: str) -> int | None:
    """Достаёт номер кейса из начала заголовка allure.

    Именно это число заказчик пишет в дампе маркером ``case 15:`` — проверено на реальном дампе,
    все 14 номеров совпали с номерами в заголовках сьюта.

    :param title: Значение ``@allure.title(...)``.
    :return: Номер кейса либо None.
    """
    match = _CASE_NO_RE.match(title)
    return int(match.group(1)) if match else None


def _allure_step_label(statement: ast.stmt) -> str | None:
    """Возвращает текст шага, если инструкция — это ``with allure.step(...)``.

    :param statement: Инструкция верхнего уровня тела теста.
    :return: Текст шага либо None.
    """
    if not isinstance(statement, ast.With | ast.AsyncWith) or not statement.items:
        return None
    context = statement.items[0].context_expr
    if not isinstance(context, ast.Call) or not isinstance(context.func, ast.Attribute):
        return None
    if context.func.attr != "step" or not context.args:
        return None
    argument = context.args[0]
    return str(argument.value) if isinstance(argument, ast.Constant) else _source_of(argument)


def _is_docstring(statement: ast.stmt) -> bool:
    """Является ли инструкция докстрингом.

    :param statement: Инструкция.
    :return: True для строкового литерала-выражения.
    """
    return (
        isinstance(statement, ast.Expr)
        and isinstance(statement.value, ast.Constant)
        and isinstance(statement.value.value, str)
    )


def _body_lines(body: Sequence[ast.stmt]) -> tuple[int, int]:
    """Диапазон строк набора инструкций.

    :param body: Инструкции.
    :return: Пара «первая строка, последняя строка»; ``(0, 0)`` для пустого набора.
    """
    if not body:
        return 0, 0
    start = min(statement.lineno for statement in body)
    end = max(getattr(statement, "end_lineno", statement.lineno) or statement.lineno for statement in body)
    return start, end


def _is_autouse_fixture(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """Помечен ли метод декоратором ``@pytest.fixture(autouse=True)``.

    Имя метода при этом любое: в репозитории есть классы, где раздача пейдж-объектов лежит
    не в ``setup``, а, например, в ``prepare`` — искать строго по имени значит молча потерять
    все ``self.<пейдж>`` такого класса.

    :param node: Узел метода тест-класса.
    :return: True, если это autouse-фикстура pytest.
    """
    for decorator in node.decorator_list:
        if not isinstance(decorator, ast.Call):
            continue
        target = decorator.func
        name = target.attr if isinstance(target, ast.Attribute) else getattr(target, "id", "")
        if name != "fixture":
            continue
        if any(word.arg == "autouse" and getattr(word.value, "value", False) is True for word in decorator.keywords):
            return True
    return False


def _parse_setup(
    class_node: ast.ClassDef,
    imports: dict[str, str],
    module: str,
    index: ClassIndex,
    file: str,
) -> tuple[dict[str, str], dict[str, str], list[StepGap]]:
    """Разбирает setup-фикстуры тест-класса: ``setup`` и любые ``@pytest.fixture(autouse=True)``.

    Классы из ``pages/**`` (пейджи И классы локаторов — в сьюте в setup встречаются оба)
    попадают в карту атрибутов; ``api.*`` пропускается молча; остальное записывается
    в исключения, а объекты неизвестного происхождения дополнительно дают запись в gaps.

    :param class_node: Узел тест-класса.
    :param imports: Карта импортов файла теста.
    :param module: Точечное имя модуля теста.
    :param index: Реестр классов ``pages/**``.
    :param file: Путь к файлу теста относительно корня репозитория.
    :return: Кортеж «карта атрибутов, исключения, проблемы».
    """
    attrs: dict[str, str] = {}
    skipped: dict[str, str] = {}
    gaps: list[StepGap] = []
    methods = [item for item in class_node.body if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef)]
    fixtures = [item for item in methods if item.name == SETUP_FIXTURE_NAME or _is_autouse_fixture(item)]
    assignments = [pair for setup in fixtures for pair in _iter_self_assignments(setup)]
    for attr, value in assignments:
        class_name = _constructor_name(value)
        if class_name is None:
            skipped[attr] = _source_of(value)
            continue
        qualname = index.resolve_name(class_name, module, imports) or imports.get(class_name, f"{module}.{class_name}")
        if qualname in index.classes or qualname.startswith(PAGE_MODULE_PREFIXES):
            attrs[attr] = qualname
            continue
        skipped[attr] = _source_of(value)
        if not qualname.startswith(SILENT_MODULE_PREFIXES):
            gaps.append(
                StepGap(
                    kind=GapKind.SETUP_ATTR,
                    reason=f"self.{attr} = {class_name}() не найден в pages/ — локаторы этого объекта не собраны",
                    source=_source_of(value),
                    line=getattr(value, "lineno", 0),
                    source_file=file,
                    attr=attr,
                )
            )
    return attrs, skipped, gaps


def _split_steps(
    function: ast.FunctionDef | ast.AsyncFunctionDef,
) -> tuple[list[ast.stmt], list[tuple[str, ast.With | ast.AsyncWith]]]:
    """Нарезает тело теста на блоки ``allure.step`` и код вне шагов.

    Обход идёт по телу ВЕРХНЕГО УРОВНЯ, а не через ``ast.walk``: вложенные ``allure.step``
    внутри методов пейджей шагами теста не являются.

    :param function: Узел тест-метода.
    :return: Кортеж «инструкции вне шагов, список пар (текст шага, узел with)».
    """
    loose: list[ast.stmt] = []
    steps: list[tuple[str, ast.With | ast.AsyncWith]] = []
    for statement in function.body:
        label = _allure_step_label(statement)
        if label is not None and isinstance(statement, ast.With | ast.AsyncWith):
            steps.append((label, statement))
            continue
        if _is_docstring(statement):
            continue
        loose.append(statement)
    return loose, steps


def _build_test_case(
    function: ast.FunctionDef | ast.AsyncFunctionDef,
    class_node: ast.ClassDef,
    context: _ModuleContext,
    index: ClassIndex,
    locators: CollectionResult,
    max_depth: int,
) -> TestCase:
    """Собирает разбор одного тест-метода.

    :param function: Узел тест-метода.
    :param class_node: Узел тест-класса.
    :param context: Контекст модуля теста (пути, импорты, шапка allure, setup).
    :param index: Реестр классов ``pages/**``.
    :param locators: Результат сбора локаторов.
    :param max_depth: Предел глубины захода в методы.
    :return: Разобранный тест со списком шагов.
    """
    title = next(
        (value for decorator in function.decorator_list if (value := _decorator_argument(decorator, "title"))), ""
    )
    allure_id = next(
        (value for decorator in function.decorator_list if (value := _decorator_argument(decorator, "id"))), None
    )
    case = TestCase(
        path=context.path,
        file=context.file,
        module=context.module,
        class_name=class_node.name,
        name=function.name,
        line=function.lineno,
        allure_id=allure_id,
        allure_title=title,
        case_no=_case_no_of(title),
        epic=context.epic,
        suite=context.suite,
        skip_reason=_skip_reason(function.decorator_list),
        fixtures=[argument.arg for argument in function.args.args if argument.arg != "self"],
        setup_attrs=dict(context.setup_attrs),
        setup_skipped=dict(context.setup_skipped),
        gaps=list(context.setup_gaps),
    )
    loose, steps = _split_steps(function)
    shared_locals: dict[str, str] = {}

    def run(body: Sequence[ast.stmt], number: int, label: str, synthetic: bool) -> TestStep:
        """Обходит тело одного шага.

        :param body: Инструкции шага.
        :param number: Номер шага.
        :param label: Текст шага.
        :param synthetic: True для псевдошага 0.
        :return: Разобранный шаг.
        """
        walker = _StepWalker(
            index,
            locators,
            context.setup_attrs,
            max_depth,
            test_skipped=context.setup_skipped,
            test_class=class_node.name,
        )
        frame = _Frame(
            self_class=TEST_SELF,
            locals_map=shared_locals,
            binds={},
            file=context.file,
            module=context.module,
            imports=context.imports,
        )
        walker.walk(body, frame)
        start, end = _body_lines(body)
        return TestStep(
            number=number,
            label=label,
            line_start=start,
            line_end=end,
            uses=walker.uses,
            gaps=walker.gaps,
            calls_walked=walker.calls_walked,
            max_depth=walker.max_depth_seen,
            synthetic=synthetic,
        )

    if loose:
        case.steps.append(run(loose, 0, LOOSE_STEP_LABEL, True))
    for number, (label, node) in enumerate(steps, start=1):
        step = run(node.body, number, label, False)
        step.line_start = node.lineno
        case.steps.append(step)
    return case


@dataclass(slots=True)
class _ModuleContext:
    """Разобранная шапка модуля теста.

    :param path: Путь к файлу теста.
    :param file: Путь относительно корня репозитория.
    :param module: Точечное имя модуля.
    :param imports: Карта импортов файла теста.
    :param epic: Значение ``@allure.epic(...)`` тест-класса.
    :param suite: Значение ``@allure.suite(...)`` тест-класса.
    :param setup_attrs: Карта ``self.<attr> -> класс`` из setup-фикстуры.
    :param setup_skipped: Атрибуты setup, не являющиеся классами ``pages/``.
    :param setup_gaps: Проблемы разбора setup.
    """

    path: Path
    file: str
    module: str
    imports: dict[str, str]
    epic: str = ""
    suite: str = ""
    setup_attrs: dict[str, str] = field(default_factory=dict)
    setup_skipped: dict[str, str] = field(default_factory=dict)
    setup_gaps: list[StepGap] = field(default_factory=list)


def _detect_project_root(start: Path) -> Path:
    """Определяет корень репозитория по наличию каталогов ``pages`` и ``tests``.

    :param start: Путь, от которого идти вверх.
    :return: Корень репозитория; если не найден — родитель ``start``.
    """
    current = start.resolve()
    if current.is_file():
        current = current.parent
    for candidate in [current, *current.parents]:
        if (candidate / "pages").is_dir() and (candidate / "tests").is_dir():
            return candidate
    return current


def load_locator_index(project_root: Path) -> CollectionResult:
    """Собирает локаторы репозитория штатным сборщиком пакета.

    ``pages/base_page.py`` передаётся в ``extra_paths`` обязательно: ``BasePage.__init__``
    заводит ``self.base_elements = BaseElements()``, и без этого файла из набора выпадают
    локаторы, которые трогают ``open_home_page`` и ``click_tab``.

    :param project_root: Корень репозитория.
    :return: Результат сбора локаторов.
    """
    return collect_locator_index(
        project_root / "pages" / "locators",
        project_root / "pages" / "ui_elements.py",
        project_root,
        extra_paths=[project_root / "pages" / "base_page.py"],
    )


def collect_tests(
    suite_path: Path,
    locators: CollectionResult,
    project_root: Path | None = None,
    pages_root: Path | None = None,
    max_depth: int = DEFAULT_MAX_DEPTH,
) -> list[TestCase]:
    """Разбирает тесты сьюта и строит для каждого шага список локаторов в порядке обращения.

    :param suite_path: Каталог сьюта (например ``tests/nbss/e2e_64_13_maintain_client_status``)
        либо один файл теста.
    :param locators: Результат :func:`scripts.dom_inspector.locator_collector.collect_locator_index`
        (можно получить через :func:`load_locator_index`).
    :param project_root: Корень репозитория; по умолчанию определяется по каталогам ``pages`` и ``tests``.
    :param pages_root: Каталог ``pages``; по умолчанию ``<project_root>/pages``.
    :param max_depth: Предел глубины захода в методы пейджей.
    :return: Список разобранных тестов в порядке файлов и объявлений.
    """
    root = project_root or _detect_project_root(suite_path)
    index = build_class_index(pages_root or root / "pages", root)
    files = sorted(suite_path.rglob("test_*.py")) if suite_path.is_dir() else [suite_path]

    tests: list[TestCase] = []
    for path in files:
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (OSError, SyntaxError, UnicodeDecodeError):
            continue
        module = module_name_of(path, root)
        context_base = _ModuleContext(
            path=path,
            file=_relative_posix(path, root),
            module=module,
            imports=_imports_of(tree),
        )
        for class_node in tree.body:
            if not isinstance(class_node, ast.ClassDef) or not class_node.name.startswith("Test"):
                continue
            attrs, skipped, gaps = _parse_setup(class_node, context_base.imports, module, index, context_base.file)
            context = _ModuleContext(
                path=context_base.path,
                file=context_base.file,
                module=module,
                imports=context_base.imports,
                epic=next(
                    (
                        value
                        for decorator in class_node.decorator_list
                        if (value := _decorator_argument(decorator, "epic"))
                    ),
                    "",
                ),
                suite=next(
                    (
                        value
                        for decorator in class_node.decorator_list
                        if (value := _decorator_argument(decorator, "suite"))
                    ),
                    "",
                ),
                setup_attrs=attrs,
                setup_skipped=skipped,
                setup_gaps=gaps,
            )
            for item in class_node.body:
                if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef) and item.name.startswith("test"):
                    tests.append(_build_test_case(item, class_node, context, index, locators, max_depth))
    return tests


def match_tests(tests: Sequence[TestCase], selector: str) -> list[TestCase]:
    """Ищет тесты по одному пользовательскому селектору.

    Порядок приоритетов: allure.id -> номер кейса -> точное имя метода -> подстрока имени ->
    подстрока заголовка. Возвращается ПЕРВЫЙ непустой уровень: номера кейсов не уникальны
    внутри сьюта (``21.`` есть и в ФЛ-тесте, и в OAPI), и cli должен показать оба кандидата.

    :param tests: Разобранные тесты.
    :param selector: Номер кейса, allure.id, подстрока имени метода или заголовка.
    :return: Список подходящих тестов (пустой, если ничего не подошло).
    """
    raw = selector.strip()
    if not raw:
        return list(tests)
    tiers: list[list[TestCase]] = []
    if raw.isdigit():
        tiers.append([test for test in tests if test.allure_id == raw])
        tiers.append([test for test in tests if test.case_no == int(raw)])
    lowered = raw.casefold()
    tiers.append([test for test in tests if test.name == raw])
    tiers.append([test for test in tests if lowered in test.name.casefold()])
    normalized = normalize_title(raw)
    tiers.append([test for test in tests if normalized and normalized in normalize_title(test.allure_title)])
    for tier in tiers:
        if tier:
            return tier
    return []


def find_test(tests: Sequence[TestCase], selector: str) -> TestCase | None:
    """Находит единственный тест по селектору.

    :param tests: Разобранные тесты.
    :param selector: Номер кейса, allure.id, подстрока имени метода или заголовка.
    :return: Тест, если он ровно один; None, если совпадений нет или их несколько
        (список кандидатов в этом случае берётся из :func:`match_tests`).
    """
    matches = match_tests(tests, selector)
    return matches[0] if len(matches) == 1 else None
