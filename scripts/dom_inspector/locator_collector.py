"""Статический сбор локаторов репозитория через :mod:`ast`.

Импортировать ``pages.locators.*`` нельзя: корневой ``conftest`` тянет ``common/helpers/env_helper.py``,
который падает без ``.env``, а ``Element.__init__`` обращается к живой странице Playwright.
Поэтому единственный рабочий способ — разбор исходников.

Модуль умеет:

* читать сигнатуры классов-обёрток (``Element``, ``ElementsList``, ``SelectWithId`` и т.д.) прямо из кода,
  а не хардкодить индексы аргументов;
* собирать объявления вида ``self.ATTR = Wrapper(...)`` и ``self.ATTR: Wrapper = Wrapper(...)``;
* синтезировать реальный CSS для обёрток, принимающих не селектор, а фрагмент id
  (``SelectWithId``, ``DropdownWithId``);
* разворачивать наследование классов-страниц, включая базы из других модулей;
* возвращать отдельным списком всё, что не удалось вычислить статически, с причиной —
  молчаливое усечение недопустимо.

Зависимости: только stdlib и :mod:`scripts.dom_inspector.models`.
"""

from __future__ import annotations

import ast
import re
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass, field
from pathlib import Path

from scripts.dom_inspector.models import (
    LIST_WRAPPER_NAMES,
    LocatorRecord,
    SecondarySelector,
    SelectorKind,
    WrapperSpec,
)

# --------------------------------------------------------------------------------------
# Шаблоны синтеза селекторов для обёрток, которым передают фрагмент id, а не готовый путь.
# Источник: pages/ui_elements.py, SelectWithId.__init__ и DropdownWithId.__init__.
# --------------------------------------------------------------------------------------
SELECT_WITH_ID_TEMPLATE: str = "[id$={id}]{additional_restriction}"
SELECT_WITH_ID_OPTIONS_TEMPLATE: str = (
    "[class*=select-dropdown]:has([id*={id}]) [class*=virtual-list-holder-inner] > [class*=option]"
)
DROPDOWN_WITH_ID_TEMPLATE: str = "[class*=dropdown-trigger][id*={id}]"
DROPDOWN_WITH_ID_OPTIONS_TEMPLATE: str = "[class*=dropdown-menu-item][id*={id}][role=menuitem]"

# DatePicker.__init__ достраивает к пути два производных селектора (ui_elements.py:798-799).
DATE_PICKER_SECONDARY: tuple[str, ...] = (
    "//span[contains(@class, 'picker-clear')]",
    "//input[@placeholder]",
)
DATE_PICKER_SECONDARY_ROLES: tuple[str, ...] = ("clear", "input")

# --------------------------------------------------------------------------------------
# Классификация селекторов. Порядок проверок повторяет parseSelectorString из Playwright.
# --------------------------------------------------------------------------------------
PLAYWRIGHT_ENGINE_RE: re.Pattern[str] = re.compile(r"^\s*(?:css|xpath|text|id|data-testid|role|internal:[a-z-]+)=")
PLAYWRIGHT_PSEUDO_RE: re.Pattern[str] = re.compile(
    r":(?:has-text|text-is|text-matches|text|nth-match|right-of|left-of|above|below|near)\("
    r"|:(?:visible|hidden|light)(?![\w-])"
)
XPATH_PREFIX_RE: re.Pattern[str] = re.compile(r"^\s*(?:\(\s*)*(?:\.{0,2}/)")
# Playwright считает XPath'ом и путь, начинающийся с '..' без слэша (selectorParser.js).
XPATH_PARENT_RE: re.Pattern[str] = re.compile(r"^\s*(?:\(\s*)*\.\.(?![\w-])")
XPATH_AXIS_RE: re.Pattern[str] = re.compile(
    r"^\s*(?:ancestor|ancestor-or-self|parent|child|descendant|descendant-or-self"
    r"|following|following-sibling|preceding|preceding-sibling|self|attribute|namespace)::"
)
PLAYWRIGHT_CHAIN: str = ">>"

# Регрессионный ассерт на текущее состояние репозитория: любое расхождение означает
# либо новый локатор, либо новую синтаксическую форму, которую сборщик не понял.
EXPECTED_LOCATOR_COUNT: int = 2682

# Имя параметра обёртки -> роль производного селектора. Все они относительны родителю.
SECONDARY_ARG_ROLES: dict[str, str] = {
    "item_path": "item",
    "field_name": "field",
    "sub_field_path": "sub_field",
    "options_elements_path": "options",
    "checked_value_path": "checked",
}

# Имя параметра с первичным селектором и с человекочитаемым описанием — едины для всех обёрток.
SELECTOR_ARG_NAME: str = "path"
DESCRIPTION_ARG_NAME: str = "locator_name"
SYNTHESIZED_ID_ARG_NAME: str = "id"
SYNTHESIZED_WRAPPERS: frozenset[str] = frozenset({"SelectWithId", "DropdownWithId"})
WRAPPER_ROOT_CLASS: str = "Element"

_UPPER_ATTR_RE: re.Pattern[str] = re.compile(r"^[A-Z][A-Z0-9_]*$")
_MAX_SOURCE_IN_REASON: int = 160


@dataclass(slots=True)
class UnresolvedLocator:
    """Объявление, которое не удалось вычислить статически.

    :param file: Путь к файлу относительно корня репозитория (в posix-виде).
    :param line: Номер строки объявления (1-based).
    :param module: Точечный путь модуля.
    :param class_name: Класс-владелец.
    :param attr: Имя атрибута, например ``ADD_BTN``.
    :param wrapper: Имя класса-обёртки, если его удалось определить.
    :param reason: Причина, по которой селектор не вычислен.
    :param source: Исходный текст выражения (усечён), чтобы находку можно было глазами сверить с кодом.
    """

    file: str
    line: int
    module: str
    class_name: str
    attr: str
    wrapper: str | None
    reason: str
    source: str

    @property
    def origin(self) -> str:
        """Адрес объявления для отчёта.

        :return: Строка вида ``pages/locators/nbss/x.py:12 SomeElements.ADD_BTN``.
        """
        return f"{self.file}:{self.line} {self.class_name}.{self.attr}"


@dataclass(slots=True)
class CollectionResult:
    """Полный результат сбора локаторов.

    :param records: Плоский список объявленных локаторов в порядке файл/строка.
    :param unresolved: Объявления, которые не удалось вычислить статически, с причиной.
    :param warnings: Предупреждения сборщика (нерезолвящиеся базы, повторные присваивания).
    :param effective: Эффективные наборы локаторов по классам: ``{qualname: {attr: LocatorRecord}}``
        с учётом наследования и переопределений.
    :param class_files: Соответствие ``qualname -> файл`` для всех разобранных классов.
    :param skipped_assignments: Присваивания ``self.x = ...``, признанные не локаторами
        (композиция page-object'ов и служебные поля).
    """

    records: list[LocatorRecord] = field(default_factory=list)
    unresolved: list[UnresolvedLocator] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    effective: dict[str, dict[str, LocatorRecord]] = field(default_factory=dict)
    class_files: dict[str, str] = field(default_factory=dict)
    skipped_assignments: list[str] = field(default_factory=list)


@dataclass(slots=True)
class _ClassInfo:
    """Разобранный класс: его база, файл и объявленные прямо в нём локаторы."""

    name: str
    module: str
    file: str
    lineno: int
    bases: list[tuple[str, str]]
    unresolved_bases: list[str]
    records: list[LocatorRecord]


@dataclass(slots=True)
class _ParsedModule:
    """Разобранный python-модуль: дерево, точечное имя и карта импортов."""

    path: Path
    module: str
    file: str
    tree: ast.Module
    imports: dict[str, str]


_PARSE_CACHE: dict[tuple[str, int, int], ast.Module] = {}


def _parse_source(path: Path) -> ast.Module:
    """Разбирает файл в AST с кэшированием по пути, размеру и времени изменения.

    :param path: Путь к python-файлу.
    :return: Дерево модуля.
    """
    stat = path.stat()
    key = (str(path), stat.st_size, stat.st_mtime_ns)
    cached = _PARSE_CACHE.get(key)
    if cached is None:
        cached = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        _PARSE_CACHE[key] = cached
    return cached


def module_name_of(path: Path, project_root: Path) -> str:
    """Возвращает точечное имя модуля по пути к файлу.

    :param path: Путь к python-файлу.
    :param project_root: Корень репозитория.
    :return: Например ``pages.locators.nbss.client.client_profile``.
    """
    try:
        relative = path.resolve().relative_to(project_root.resolve())
    except ValueError:
        return path.stem
    parts = list(relative.with_suffix("").parts)
    if parts and parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def _relative_file(path: Path, project_root: Path) -> str:
    """Возвращает путь к файлу относительно корня репозитория в posix-виде.

    :param path: Путь к файлу.
    :param project_root: Корень репозитория.
    :return: Например ``pages/locators/nbss/client/client_profile.py``.
    """
    try:
        return path.resolve().relative_to(project_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _parse_module(path: Path, project_root: Path) -> _ParsedModule:
    """Разбирает модуль и собирает карту импортов верхнего уровня.

    :param path: Путь к python-файлу.
    :param project_root: Корень репозитория.
    :return: Контейнер с деревом, именем модуля и картой ``{локальное имя: модуль}``.
    """
    tree = _parse_source(path)
    module = module_name_of(path, project_root)
    imports: dict[str, str] = {}
    package = module.rsplit(".", 1)[0] if "." in module else module
    for node in tree.body:
        if isinstance(node, ast.ImportFrom):
            if node.level:
                base_parts = package.split(".") if package else []
                if node.level > 1:
                    base_parts = base_parts[: -(node.level - 1)] or []
                source_module = ".".join([*base_parts, node.module] if node.module else base_parts)
            else:
                source_module = node.module or ""
            for alias in node.names:
                imports[alias.asname or alias.name] = source_module
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports[alias.asname or alias.name] = alias.name
    return _ParsedModule(path=path, module=module, file=_relative_file(path, project_root), tree=tree, imports=imports)


# --------------------------------------------------------------------------------------
# Классификация селекторов
# --------------------------------------------------------------------------------------
def classify_selector(selector: str) -> SelectorKind:
    """Определяет, каким движком проверять селектор.

    Порядок проверок строго фиксирован: явный движок Playwright -> комбинатор ``>>`` ->
    XPath по префиксу (в том числе ``..`` без слэша, как в selectorParser.js) -> Playwright-псевдоклассы ->
    относительный путь (оси ``ancestor::`` и т.п.) -> CSS.
    «Сначала попробуем XPath» делать нельзя: lxml успешно компилирует ``div.foo`` как валидный XPath,
    и CSS-селектор молча уйдёт не в тот движок.

    :param selector: Строка селектора.
    :return: Тип селектора.
    """
    if not selector or not selector.strip():
        return SelectorKind.UNKNOWN
    if PLAYWRIGHT_ENGINE_RE.search(selector):
        return SelectorKind.PLAYWRIGHT
    if PLAYWRIGHT_CHAIN in selector:
        return SelectorKind.PLAYWRIGHT
    if XPATH_PREFIX_RE.search(selector) or XPATH_PARENT_RE.search(selector):
        return SelectorKind.XPATH
    if PLAYWRIGHT_PSEUDO_RE.search(selector):
        return SelectorKind.PLAYWRIGHT
    if XPATH_AXIS_RE.search(selector):
        return SelectorKind.RELATIVE
    return SelectorKind.CSS


# --------------------------------------------------------------------------------------
# Сигнатуры классов-обёрток
# --------------------------------------------------------------------------------------
def _init_arg_names(class_node: ast.ClassDef) -> tuple[str, ...] | None:
    """Возвращает имена позиционных параметров ``__init__`` без ``self``.

    :param class_node: Узел класса.
    :return: Кортеж имён либо None, если собственного ``__init__`` у класса нет.
    """
    for node in class_node.body:
        if isinstance(node, ast.FunctionDef) and node.name == "__init__":
            args = [*node.args.posonlyargs, *node.args.args]
            return tuple(arg.arg for arg in args[1:])
    return None


def load_wrapper_specs(ui_elements_path: Path, extra_paths: Sequence[Path] = ()) -> dict[str, WrapperSpec]:
    """Читает описания классов-обёрток из исходников.

    Обёрткой считается класс, чья цепочка наследования доходит до ``Element``. Имена параметров
    берутся из кода (в том числе унаследованные), семантика — из таблиц модуля: первичный селектор
    всегда лежит в параметре ``path``, описание — в ``locator_name``, производные селекторы —
    в параметрах из :data:`SECONDARY_ARG_ROLES`. Благодаря разбору по именам, а не по индексам,
    автоматически обрабатываются обёртки со «сдвинутым» описанием (``DynamicField``, ``ScrollableList``)
    и вызовы только именованными аргументами.

    :param ui_elements_path: Путь к ``pages/ui_elements.py``.
    :param extra_paths: Дополнительные файлы, где могут быть объявлены обёртки
        (например ``pages/locators/rfd_locators/base_elements_rfd.py`` с ``SelectRFD``).
    :return: Словарь ``{имя обёртки: WrapperSpec}``.
    """
    nodes: dict[str, ast.ClassDef] = {}
    bases: dict[str, list[str]] = {}
    for path in [ui_elements_path, *extra_paths]:
        if not path.is_file():
            continue
        for node in _parse_source(path).body:
            if not isinstance(node, ast.ClassDef) or node.name in nodes:
                continue
            nodes[node.name] = node
            bases[node.name] = [base.id for base in node.bases if isinstance(base, ast.Name)]

    def is_wrapper(name: str, seen: frozenset[str] = frozenset()) -> bool:
        if name == WRAPPER_ROOT_CLASS:
            return True
        if name in seen or name not in bases:
            return False
        return any(is_wrapper(parent, seen | {name}) for parent in bases[name])

    def arg_names_of(name: str, seen: frozenset[str] = frozenset()) -> tuple[str, ...]:
        own = _init_arg_names(nodes[name]) if name in nodes else None
        if own is not None:
            return own
        for parent in bases.get(name, []):
            if parent in nodes and parent not in seen:
                inherited = arg_names_of(parent, seen | {name})
                if inherited:
                    return inherited
        return ()

    specs: dict[str, WrapperSpec] = {}
    for name in nodes:
        if not is_wrapper(name):
            continue
        arg_names = arg_names_of(name)
        synthesized = name in SYNTHESIZED_WRAPPERS
        specs[name] = WrapperSpec(
            name=name,
            arg_names=arg_names,
            selector_arg=None if synthesized else (SELECTOR_ARG_NAME if SELECTOR_ARG_NAME in arg_names else None),
            description_arg=DESCRIPTION_ARG_NAME if DESCRIPTION_ARG_NAME in arg_names else None,
            secondary_args=tuple(arg for arg in arg_names if arg in SECONDARY_ARG_ROLES),
            is_list=name in LIST_WRAPPER_NAMES,
            synthesized=synthesized,
        )
    return specs


# --------------------------------------------------------------------------------------
# Разбор объявлений
# --------------------------------------------------------------------------------------
def _string_literal(node: ast.expr | None) -> str | None:
    """Возвращает значение строкового литерала.

    :param node: Узел выражения либо None.
    :return: Строка либо None, если это не строковая константа.
    """
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _describe_expr(node: ast.expr) -> str:
    """Человекочитаемое название вида выражения — для причины «не вычисляется статически».

    :param node: Узел выражения.
    :return: Например ``f-строка`` или ``переменная path``.
    """
    if isinstance(node, ast.JoinedStr):
        return "f-строка"
    if isinstance(node, ast.BinOp):
        return "выражение (конкатенация или форматирование)"
    if isinstance(node, ast.Name):
        return f"переменная {node.id}"
    if isinstance(node, ast.Attribute):
        return "обращение к атрибуту"
    if isinstance(node, ast.Call):
        func = node.func
        called = func.id if isinstance(func, ast.Name) else "вызов"
        return f"вызов {called}()"
    if isinstance(node, ast.IfExp):
        return "тернарное выражение"
    if isinstance(node, ast.Constant):
        return f"константа типа {type(node.value).__name__}"
    return type(node).__name__


def _source_of(node: ast.expr) -> str:
    """Возвращает усечённый исходный текст выражения.

    :param node: Узел выражения.
    :return: Текст выражения, обрезанный до :data:`_MAX_SOURCE_IN_REASON` символов.
    """
    try:
        text = ast.unparse(node)
    except Exception:  # pragma: no cover - ast.unparse не падает на валидном дереве
        text = _describe_expr(node)
    text = " ".join(text.split())
    if len(text) > _MAX_SOURCE_IN_REASON:
        text = text[: _MAX_SOURCE_IN_REASON - 3] + "..."
    return text


def _call_argument(call: ast.Call, spec: WrapperSpec, name: str) -> ast.expr | None:
    """Достаёт аргумент вызова обёртки по имени параметра.

    Читаются и позиционные аргументы (по индексу имени в сигнатуре), и именованные:
    ``ScrollableList`` вызывается только через kwargs, а ``additional_restriction``
    у ``SelectWithId`` тоже передан именованным.

    :param call: Узел вызова обёртки.
    :param spec: Описание обёртки.
    :param name: Имя параметра.
    :return: Узел значения либо None, если аргумент не передан.
    """
    for keyword in call.keywords:
        if keyword.arg == name:
            return keyword.value
    if name in spec.arg_names:
        index = spec.arg_names.index(name)
        if index < len(call.args):
            return call.args[index]
    return None


def _secondary_from_args(call: ast.Call, spec: WrapperSpec) -> tuple[list[SecondarySelector], list[str]]:
    """Собирает производные селекторы, переданные аргументами обёртки.

    :param call: Узел вызова обёртки.
    :param spec: Описание обёртки.
    :return: Список производных селекторов и список причин, если какие-то из них не литералы.
    """
    secondary: list[SecondarySelector] = []
    problems: list[str] = []
    for arg_name in spec.secondary_args:
        node = _call_argument(call, spec, arg_name)
        if node is None:
            continue
        value = _string_literal(node)
        if value is None:
            problems.append(f"производный селектор {arg_name} не является строковым литералом: {_source_of(node)}")
            continue
        secondary.append(
            SecondarySelector(
                selector=value,
                kind=classify_selector(value),
                role=SECONDARY_ARG_ROLES[arg_name],
                relative=True,
            )
        )
    return secondary, problems


def _date_picker_secondary(selector: str) -> list[SecondarySelector]:
    """Строит производные селекторы ``DatePicker`` (кнопка очистки и поле ввода даты).

    ``DatePicker.__init__`` склеивает путь с XPath-хвостом. Если путь — CSS, склейка сама по себе
    невалидна и проверять её от документа нельзя, поэтому она помечается относительной.

    :param selector: Первичный селектор датапикера.
    :return: Список производных селекторов.
    """
    base_kind = classify_selector(selector)
    secondary: list[SecondarySelector] = []
    for suffix, role in zip(DATE_PICKER_SECONDARY, DATE_PICKER_SECONDARY_ROLES, strict=True):
        combined = selector + suffix
        secondary.append(
            SecondarySelector(
                selector=combined,
                kind=classify_selector(combined),
                role=role,
                relative=base_kind is not SelectorKind.XPATH,
            )
        )
    return secondary


def _iter_assignments(init_node: ast.FunctionDef) -> Iterable[tuple[ast.expr, ast.expr, int]]:
    """Перебирает присваивания внутри ``__init__``.

    Обрабатываются и :class:`ast.Assign`, и :class:`ast.AnnAssign` — иначе молча теряется
    ровно один локатор (``self.INFO_MESSAGE: Element = Element(...)``).

    :param init_node: Узел метода ``__init__``.
    :return: Итератор кортежей ``(цель, значение, номер строки)``.
    """
    for node in ast.walk(init_node):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                yield target, node.value, node.lineno
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            yield node.target, node.value, node.lineno


def _self_attr(target: ast.expr) -> str | None:
    """Возвращает имя атрибута для цели вида ``self.ATTR``.

    :param target: Узел цели присваивания.
    :return: Имя атрибута либо None, если это не ``self.<имя>``.
    """
    if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == "self":
        return target.attr
    return None


def _collect_class_records(
    class_node: ast.ClassDef,
    parsed: _ParsedModule,
    specs: dict[str, WrapperSpec],
    unresolved: list[UnresolvedLocator],
    skipped: list[str],
    warnings: list[str],
) -> list[LocatorRecord]:
    """Собирает локаторы, объявленные непосредственно в классе.

    :param class_node: Узел класса.
    :param parsed: Разобранный модуль-владелец.
    :param specs: Описания обёрток.
    :param unresolved: Список, куда добавляются невычислимые объявления.
    :param skipped: Список, куда добавляются присваивания, признанные не локаторами.
    :param warnings: Список, куда добавляются предупреждения о повторных присваиваниях.
    :return: Список записей в порядке объявления.
    """
    records: list[LocatorRecord] = []
    for node in class_node.body:
        if not isinstance(node, ast.FunctionDef) or node.name != "__init__":
            continue
        for target, value, lineno in _iter_assignments(node):
            attr = _self_attr(target)
            if attr is None:
                if isinstance(target, ast.Attribute | ast.Tuple | ast.List):
                    skipped.append(f"{parsed.file}:{lineno} нестандартная цель присваивания: {_source_of(target)}")
                continue
            record = _build_record(
                attr=attr,
                value=value,
                lineno=lineno,
                class_node=class_node,
                parsed=parsed,
                specs=specs,
                unresolved=unresolved,
                skipped=skipped,
            )
            if record is not None:
                records.append(record)
    return _mark_overrides(records, parsed, warnings)


def _build_record(
    attr: str,
    value: ast.expr,
    lineno: int,
    class_node: ast.ClassDef,
    parsed: _ParsedModule,
    specs: dict[str, WrapperSpec],
    unresolved: list[UnresolvedLocator],
    skipped: list[str],
) -> LocatorRecord | None:
    """Строит запись локатора по одному присваиванию ``self.ATTR = ...``.

    :param attr: Имя атрибута.
    :param value: Узел присваиваемого значения.
    :param lineno: Номер строки.
    :param class_node: Класс-владелец.
    :param parsed: Разобранный модуль.
    :param specs: Описания обёрток.
    :param unresolved: Список невычислимых объявлений.
    :param skipped: Список присваиваний, признанных не локаторами.
    :return: Запись локатора либо None, если объявление локатором не является или не вычислимо.
    """
    is_locator_name = bool(_UPPER_ATTR_RE.match(attr))

    def add_unresolved(reason: str, wrapper: str | None) -> None:
        unresolved.append(
            UnresolvedLocator(
                file=parsed.file,
                line=lineno,
                module=parsed.module,
                class_name=class_node.name,
                attr=attr,
                wrapper=wrapper,
                reason=reason,
                source=_source_of(value),
            )
        )

    if isinstance(value, ast.Call) and isinstance(value.func, ast.Name) and value.func.id in specs:
        return _build_wrapped_record(
            attr=attr,
            call=value,
            spec=specs[value.func.id],
            lineno=lineno,
            class_node=class_node,
            parsed=parsed,
            add_unresolved=add_unresolved,
        )

    literal = _string_literal(value)
    if literal is not None:
        if not is_locator_name:
            skipped.append(f"{parsed.file}:{lineno} {class_node.name}.{attr} — служебная строка")
            return None
        return LocatorRecord(
            selector=literal,
            kind=classify_selector(literal),
            description="",
            attr=attr,
            class_name=class_node.name,
            module=parsed.module,
            file=parsed.file,
            line=lineno,
            wrapper=None,
            is_list=False,
        )

    if is_locator_name:
        add_unresolved(f"значение не вычисляется статически: {_describe_expr(value)}", None)
        return None

    skipped.append(f"{parsed.file}:{lineno} {class_node.name}.{attr} — не локатор ({_describe_expr(value)})")
    return None


def _build_wrapped_record(
    attr: str,
    call: ast.Call,
    spec: WrapperSpec,
    lineno: int,
    class_node: ast.ClassDef,
    parsed: _ParsedModule,
    add_unresolved: Callable[[str, str | None], None],
) -> LocatorRecord | None:
    """Строит запись локатора по вызову класса-обёртки.

    :param attr: Имя атрибута.
    :param call: Узел вызова обёртки.
    :param spec: Описание обёртки.
    :param lineno: Номер строки.
    :param class_node: Класс-владелец.
    :param parsed: Разобранный модуль.
    :param add_unresolved: Колбэк регистрации невычислимого объявления.
    :return: Запись локатора либо None, если селектор не вычислим.
    """
    description_node = _call_argument(call, spec, DESCRIPTION_ARG_NAME) if spec.description_arg else None
    description = _string_literal(description_node) or ""
    if description_node is not None and not description:
        if _string_literal(description_node) is None:
            add_unresolved(f"описание не является строковым литералом: {_describe_expr(description_node)}", spec.name)
    raw_first_arg: str | None = None
    secondary: list[SecondarySelector] = []

    if spec.synthesized:
        id_node = _call_argument(call, spec, SYNTHESIZED_ID_ARG_NAME)
        raw_first_arg = _string_literal(id_node)
        if raw_first_arg is None:
            reason = "фрагмент id не является строковым литералом"
            if id_node is not None:
                reason = f"{reason}: {_describe_expr(id_node)}"
            add_unresolved(reason, spec.name)
            return None
        if spec.name == "SelectWithId":
            restriction_node = _call_argument(call, spec, "additional_restriction")
            restriction = "" if restriction_node is None else (_string_literal(restriction_node) or "")
            if restriction_node is not None and _string_literal(restriction_node) is None:
                add_unresolved(
                    f"additional_restriction не является строковым литералом: {_describe_expr(restriction_node)}",
                    spec.name,
                )
                return None
            selector = SELECT_WITH_ID_TEMPLATE.format(id=raw_first_arg, additional_restriction=restriction)
            options = SELECT_WITH_ID_OPTIONS_TEMPLATE.format(id=raw_first_arg)
        else:
            selector = DROPDOWN_WITH_ID_TEMPLATE.format(id=raw_first_arg)
            options = DROPDOWN_WITH_ID_OPTIONS_TEMPLATE.format(id=raw_first_arg)
        secondary.append(
            SecondarySelector(selector=options, kind=classify_selector(options), role="options", relative=False)
        )
    else:
        selector_node = _call_argument(call, spec, SELECTOR_ARG_NAME) if spec.selector_arg else None
        if selector_node is None:
            add_unresolved(f"обёртка {spec.name}: аргумент '{SELECTOR_ARG_NAME}' не передан", spec.name)
            return None
        raw_first_arg = _string_literal(selector_node)
        if raw_first_arg is None:
            add_unresolved(f"селектор не является строковым литералом: {_describe_expr(selector_node)}", spec.name)
            return None
        selector = raw_first_arg
        if spec.name == "DatePicker":
            secondary.extend(_date_picker_secondary(selector))

    arg_secondary, problems = _secondary_from_args(call, spec)
    secondary.extend(arg_secondary)
    for problem in problems:
        add_unresolved(problem, spec.name)

    return LocatorRecord(
        selector=selector,
        kind=classify_selector(selector),
        description=description,
        attr=attr,
        class_name=class_node.name,
        module=parsed.module,
        file=parsed.file,
        line=lineno,
        wrapper=spec.name,
        is_list=spec.is_list,
        secondary_selectors=secondary,
        raw_first_arg=raw_first_arg,
    )


def _mark_overrides(records: list[LocatorRecord], parsed: _ParsedModule, warnings: list[str]) -> list[LocatorRecord]:
    """Отмечает повторные присваивания одного атрибута внутри класса.

    Побеждает последнее присваивание по порядку строк — оно и помечается ``overridden_in_class``.
    Проигравшие записи тоже возвращаются: как правило это опечатка или копипаста, и их полезно видеть.

    :param records: Записи класса в порядке объявления.
    :param parsed: Разобранный модуль (для текста предупреждения).
    :param warnings: Список, куда добавляется человекочитаемое предупреждение.
    :return: Тот же список записей.
    """
    by_attr: dict[str, list[LocatorRecord]] = {}
    for record in records:
        by_attr.setdefault(record.attr, []).append(record)
    for attr, group in by_attr.items():
        if len(group) < 2:
            continue
        group[-1].overridden_in_class = True
        lines = ", ".join(str(item.line) for item in group)
        warnings.append(
            f"{parsed.file} {group[0].class_name}.{attr} присваивается несколько раз (строки {lines}), "
            f"побеждает строка {group[-1].line}"
        )
    return records


# --------------------------------------------------------------------------------------
# Сбор по репозиторию и разворачивание наследования
# --------------------------------------------------------------------------------------
def _qualname(module: str, name: str) -> str:
    """Формирует уникальный ключ класса.

    Ключ обязан включать модуль: имена ``PersonalAccountForm`` и ``ConsumptionElements``
    объявлены в репозитории дважды в разных модулях.

    :param module: Точечный путь модуля.
    :param name: Имя класса.
    :return: Строка вида ``pages.locators.nbss.client.client_profile.ClientProfileElements``.
    """
    return f"{module}.{name}"


def _iter_python_files(root: Path) -> list[Path]:
    """Возвращает отсортированный список python-файлов каталога.

    :param root: Корневой каталог.
    :return: Список путей.
    """
    return sorted(path for path in root.rglob("*.py") if path.is_file())


def _linearize(key: tuple[str, str], registry: dict[tuple[str, str], _ClassInfo]) -> list[tuple[str, str]]:
    """Линеаризует цепочку наследования в глубину.

    :param key: Ключ класса ``(модуль, имя)``.
    :param registry: Реестр разобранных классов.
    :return: Список ключей от самого класса к дальним предкам, без повторов.
    """
    order: list[tuple[str, str]] = []
    stack: list[tuple[str, str]] = [key]
    seen: set[tuple[str, str]] = set()
    while stack:
        current = stack.pop(0)
        if current in seen:
            continue
        seen.add(current)
        order.append(current)
        info = registry.get(current)
        if info is None:
            continue
        stack = [base for base in info.bases if base not in seen] + stack
    return order


def collect_locator_index(
    locators_root: Path,
    ui_elements_path: Path,
    project_root: Path,
    extra_paths: Sequence[Path] = (),
    follow_external_bases: bool = True,
) -> CollectionResult:
    """Собирает локаторы репозитория и разворачивает наследование.

    :param locators_root: Каталог с локаторами (обычно ``<корень>/pages/locators``).
    :param ui_elements_path: Путь к ``pages/ui_elements.py`` — источник сигнатур обёрток.
    :param project_root: Корень репозитория.
    :param extra_paths: Дополнительные файлы для разбора помимо ``locators_root``.
    :param follow_external_bases: Догружать ли модули с базовыми классами вне ``locators_root``
        (например ``pages/base_page.py`` и ``pages/osa_pages/home_page_osa.py``).
    :return: Полный результат сбора: записи, невычислимые объявления, предупреждения, эффективные наборы.
    """
    result = CollectionResult()
    files = _iter_python_files(locators_root)
    files.extend(path for path in extra_paths if path.is_file())
    specs = load_wrapper_specs(ui_elements_path, files)

    registry: dict[tuple[str, str], _ClassInfo] = {}
    parsed_modules: dict[str, _ParsedModule] = {}
    queue: list[Path] = list(files)
    processed: set[Path] = set()

    while queue:
        path = queue.pop(0)
        resolved = path.resolve()
        if resolved in processed:
            continue
        processed.add(resolved)
        try:
            parsed = _parse_module(path, project_root)
        except (OSError, SyntaxError) as error:
            result.warnings.append(f"не удалось разобрать {path}: {error}")
            continue
        parsed_modules[parsed.module] = parsed
        for node in parsed.tree.body:
            if not isinstance(node, ast.ClassDef):
                continue
            key = (parsed.module, node.name)
            if key in registry:
                continue
            bases: list[tuple[str, str]] = []
            unresolved_bases: list[str] = []
            for base in node.bases:
                base_name = base.id if isinstance(base, ast.Name) else getattr(base, "attr", None)
                if base_name is None:
                    unresolved_bases.append(_source_of(base))
                    continue
                base_module = parsed.imports.get(base_name, parsed.module)
                bases.append((base_module, base_name))
                if follow_external_bases and base_module != parsed.module:
                    candidate = project_root.joinpath(*base_module.split(".")).with_suffix(".py")
                    if candidate.is_file() and candidate.resolve() not in processed:
                        queue.append(candidate)
            records = _collect_class_records(
                node, parsed, specs, result.unresolved, result.skipped_assignments, result.warnings
            )
            registry[key] = _ClassInfo(
                name=node.name,
                module=parsed.module,
                file=parsed.file,
                lineno=node.lineno,
                bases=bases,
                unresolved_bases=unresolved_bases,
                records=records,
            )

    # Классы-обёртки исключаются из отчёта: локаторов они не объявляют. Проверяется не только имя,
    # но и наличие базы-обёртки, иначе локаторный класс, случайно названный как обёртка, потеряется.
    wrapper_keys = {
        key
        for key, info in registry.items()
        if key[1] in specs and (not info.bases or any(base[1] in specs for base in info.bases))
    }
    for key, info in registry.items():
        result.class_files[_qualname(*key)] = info.file
        for base_key in info.bases:
            if base_key not in registry:
                result.warnings.append(
                    f"{info.file}:{info.lineno} класс {info.name}: базовый класс {base_key[1]} "
                    f"из модуля {base_key[0]} не найден, наследование не развёрнуто"
                )
        for raw in info.unresolved_bases:
            result.warnings.append(f"{info.file}:{info.lineno} класс {info.name}: база {raw} не разобрана")

    for key, info in registry.items():
        if key in wrapper_keys:
            continue
        chain = _linearize(key, registry)
        effective: dict[str, LocatorRecord] = {}
        for ancestor in reversed(chain):
            ancestor_info = registry.get(ancestor)
            if ancestor_info is None:
                continue
            for record in ancestor_info.records:
                effective[record.attr] = record
        result.effective[_qualname(*key)] = effective
        for record in effective.values():
            if (record.module, record.class_name) != key:
                record.inherited_by.append(_qualname(*key))

    for key in sorted(registry, key=lambda item: (registry[item].file, registry[item].lineno)):
        if key in wrapper_keys:
            continue
        result.records.extend(registry[key].records)
    result.records.sort(key=lambda record: (record.file, record.line, record.attr))
    result.unresolved.sort(key=lambda item: (item.file, item.line, item.attr))
    return result


def collect_locators(
    locators_root: Path, ui_elements_path: Path, project_root: Path
) -> tuple[list[LocatorRecord], list[str]]:
    """Собирает локаторы репозитория.

    Тонкая обёртка над :func:`collect_locator_index` для контракта пакета: невычислимые объявления
    добавляются в предупреждения текстом, чтобы они не пропали из отчёта.

    :param locators_root: Каталог с локаторами.
    :param ui_elements_path: Путь к ``pages/ui_elements.py``.
    :param project_root: Корень репозитория.
    :return: Плоский список локаторов и список предупреждений.
    """
    result = collect_locator_index(locators_root, ui_elements_path, project_root)
    warnings = list(result.warnings)
    warnings.extend(f"{item.origin}: {item.reason}" for item in result.unresolved)
    return result.records, warnings


def group_by_selector(records: Sequence[LocatorRecord]) -> dict[str, list[LocatorRecord]]:
    """Группирует записи по строке селектора.

    Нужна для дедупликации проверок: один и тот же селектор объявлен в нескольких классах,
    гонять его по DOM достаточно один раз, а результат разворачивать на все места объявления.

    :param records: Записи локаторов.
    :return: Словарь ``{селектор: [записи]}`` в порядке первого появления селектора.
    """
    grouped: dict[str, list[LocatorRecord]] = {}
    for record in records:
        grouped.setdefault(record.selector, []).append(record)
    return grouped


def filter_locators(
    records: Sequence[LocatorRecord],
    classes: Sequence[str] = (),
    files: Sequence[str] = (),
    modules: Sequence[str] = (),
    attrs: Sequence[str] = (),
) -> list[LocatorRecord]:
    """Отбирает локаторы по классам, файлам, модулям или именам атрибутов.

    Пустой набор условий означает «не фильтровать по этому признаку». Условия разных признаков
    объединяются по И, значения внутри одного признака — по ИЛИ.

    :param records: Записи локаторов.
    :param classes: Имена классов (простые или с модулем через точку).
    :param files: Пути или их окончания, например ``client_profile.py``.
    :param modules: Точечные пути модулей или их префиксы.
    :param attrs: Имена атрибутов.
    :return: Отфильтрованный список записей.
    """
    wanted_classes = set(classes)
    wanted_attrs = set(attrs)
    selected: list[LocatorRecord] = []
    for record in records:
        if wanted_classes and not (
            record.class_name in wanted_classes or _qualname(record.module, record.class_name) in wanted_classes
        ):
            continue
        if files and not any(record.file == item or record.file.endswith(item.replace("\\", "/")) for item in files):
            continue
        if modules and not any(record.module == item or record.module.startswith(f"{item}.") for item in modules):
            continue
        if wanted_attrs and record.attr not in wanted_attrs:
            continue
        selected.append(record)
    return selected


def effective_locators(result: CollectionResult, class_name: str, module: str | None = None) -> dict[str, LocatorRecord]:
    """Возвращает эффективный набор локаторов класса с учётом наследования.

    :param result: Результат :func:`collect_locator_index`.
    :param class_name: Имя класса (простое или полное).
    :param module: Точечный путь модуля, если простое имя неоднозначно.
    :return: Словарь ``{имя атрибута: запись}``; пустой словарь, если класс не найден.
    """
    if module is not None:
        return dict(result.effective.get(_qualname(module, class_name), {}))
    if class_name in result.effective:
        return dict(result.effective[class_name])
    matches = [key for key in result.effective if key.rsplit(".", 1)[-1] == class_name]
    if len(matches) != 1:
        return {}
    return dict(result.effective[matches[0]])
