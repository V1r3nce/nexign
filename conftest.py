import ast
import logging
import os
import shutil
import urllib.parse
from importlib.metadata import version
from pathlib import Path
from typing import List

import allure
import pytest
from _pytest.config import Config
from _pytest.terminal import TerminalReporter
from httpx import Client
from playwright.sync_api import APIRequestContext, Browser, BrowserContext, Page, Playwright
from pytest import ExitCode

from common.const import Constants
from common.custom_allure_step import step_decorator
from common.enums.user import User
from common.helpers.download_helper import CheckFile
from common.helpers.env_helper import (
    BASE_URL,
    BASE_URL_API,
    HAR_DIR,
    LOGS_FOLDER,
    TEMP_DIR,
    get_var_from_env,
)
from common.helpers.time_helpers import get_now_time
from common.logging import create_logger
from models.context import test_context

test_run_mode = get_var_from_env("TEST_RUN_MODE")
remote_driver = get_var_from_env("REMOTE_DRIVER") if test_run_mode == "remote" else None

if remote_driver == "SELENOID" and test_run_mode == "remote":
    os.environ["SELENIUM_REMOTE_URL"] = f"http://{get_var_from_env('SELENOID_HOST')}:4444/wd/hub"
    os.environ["SELENIUM_REMOTE_CAPABILITIES"] = f'''
        {{"selenoid:options":
            {{
                "name":"{get_now_time()}",
                "enableVNC": true,
                "enableVideo": false,
                "sessionTimeout": "10m"
            }}
        }}
        '''


@pytest.fixture(scope="session")
def moon_url_with_params(request: pytest.FixtureRequest) -> str | None:
    if remote_driver == "MOON":
        remote_driver_host = get_var_from_env(f"{remote_driver}_HOST")

        moon_url = f"ws://{remote_driver_host}/playwright/chrome/playwright-{version('playwright')}"

        params = {
            "headless": f"{request.config.getoption('--headless')}",
            "name": get_now_time(),
        }
        url_params = urllib.parse.urlencode(params, doseq=True)
        ws_url = f"{moon_url}?{url_params}"
        return ws_url
    return None


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--headless", action="store_true", default=False, help="headless mode")
    parser.addoption(
        "--dump-dom",
        action="store_true",
        default=False,
        help="снимать DOM после каждого шага теста в scripts/dom_inspector/dumps/<тест>.txt "
        "для последующего разбора: python -m scripts.dom_inspector.cli steps <дамп>",
    )


@pytest.fixture(scope="function")
def get_browser(request: pytest.FixtureRequest, playwright: Playwright, moon_url_with_params: str | None) -> Browser:
    """Фикстура отвечающая за запуск браузера, в зависимости от режима запуска (локальный или удаленный)
    и удаленного драйвера (если выбран удаленный режим)"""

    if test_run_mode == "remote" and remote_driver == "MOON":
        browser = playwright.chromium.connect(moon_url_with_params)
    else:
        browser = playwright.chromium.launch(
            channel="chrome", headless=request.config.getoption("--headless"), args=["--start-maximized"]
        )
    yield browser
    browser.close()


@pytest.fixture(scope="function")
def context(request: pytest.FixtureRequest, get_browser: Browser, test_name: str) -> BrowserContext:
    browser = get_browser
    context = browser.new_context(
        no_viewport=False if remote_driver == "MOON" and test_run_mode == "remote" else True,
        record_har_path=HAR_DIR / f"{test_name}.har",
        record_har_url_filter="**/openapi/**",
        record_har_mode="minimal",
    )
    context.set_default_timeout(Constants.DEFAULT_TIMEOUT)
    yield context
    context.close()


@pytest.fixture()
def page(context: BrowserContext, cleanup_test_context: None) -> Page:
    """cleanup_test_context обязателен: иначе pytest может выполнить page раньше reset() и очистить page_list после append."""
    page = context.new_page()
    if remote_driver == "MOON":
        page.set_viewport_size({"width": 1920, "height": 1080})
    test_context.page_list.append(page)
    yield test_context.page
    page.close()


@pytest.fixture()
def api_context(cleanup_test_context: None, user: User) -> Client:
    """Получение контекста для API запросов. По умолчанию берется текущий контекст страницы, но если пользователь не админ,
    то создается новый независимый контекст специально для роли админа."""
    logging.getLogger("httpx").setLevel(logging.WARNING)
    context = Client()
    if user != User.ADMIN:
        test_context.api_context_dict[User.ADMIN] = Client()

    test_context.api_context_dict[user] = context
    test_context.api_context = context
    yield context


@pytest.fixture()
def api_request_context(cleanup_test_context: None, page: Page, user: User) -> APIRequestContext:
    """Получение контекста для API запросов. По умолчанию берется текущий контекст страницы, но если пользователь не админ,
    то создается новый независимый контекст специально для роли админа."""
    context = page.request

    if user != User.ADMIN:
        test_context.api_context_dict[User.ADMIN] = page.context.browser.new_context().request

    test_context.api_context_dict[user] = context
    test_context.api_context = context
    yield context
    context.dispose()


@pytest.fixture()
def cleanup_test_context() -> None:
    """Очищает test_context перед и после каждого теста"""
    test_context.reset()
    yield
    test_context.reset()


@pytest.fixture(scope="session")
def base_url_api() -> str:
    return BASE_URL_API


@pytest.fixture(scope="session")
def base_url() -> str:
    return BASE_URL


DEPENDENCY_CACHE = {}


def _extract_marks_from_decorator(decorator: ast.AST) -> str | None:
    if not isinstance(decorator, ast.Attribute):
        return None

    value = decorator.value
    # Обрабатываем структуру pytest.mark.product
    if (
        isinstance(value, ast.Attribute)
        and isinstance(value.value, ast.Name)
        and value.attr == "mark"
        and value.value.id == "pytest"
    ):
        return decorator.attr

    # Поддержка сокращённого импорта: from pytest import mark
    if isinstance(value, ast.Name) and value.id.startswith("mark"):
        mark_name = value.id[5:]
        return mark_name

    return None


def _is_fixture_decorator(decorator: ast.AST) -> bool:
    """Проверяет, является ли декоратор @pytest.fixture."""
    if not isinstance(decorator, ast.Call):
        return False
    func = decorator.func
    if isinstance(func, ast.Attribute):
        return isinstance(func.value, ast.Name) and func.value.id == "pytest" and func.attr == "fixture"
    return False


def _collect_all_fixtures(root_path: Path) -> set[str]:
    """Собирает все имена фикстур из проекта (из @pytest.fixture)."""
    IGNORE_DIRS = {".venv", ".git", "__pycache__", "dist", "build"}
    fixture_names = set()
    for file_path in root_path.rglob("conftest.py"):
        if any(part in IGNORE_DIRS for part in file_path.parts):
            continue
        try:
            with open(file_path, encoding="utf-8") as f:
                tree = ast.parse(f.read())
        except Exception:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for decorator in node.decorator_list:
                    if _is_fixture_decorator(decorator):
                        fixture_names.add(node.name)
    return fixture_names


def _node_parse_for_assigns(node: ast.AST) -> dict:
    dependencies = dict()
    if isinstance(node, ast.AnnAssign):
        if isinstance(node.annotation, ast.Name) and isinstance(node.target, ast.Name):
            attr_name = node.target.id
            attr_type = node.annotation.id
            dependencies[attr_name] = attr_type

    # Присваивания в теле класса
    elif isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name):
                attr_name = target.id
                if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name):
                    dependencies[attr_name] = node.value.func.id
                else:
                    dependencies[attr_name] = "unknown"
    if hasattr(node, "body"):
        for child in ast.iter_child_nodes(node):
            dependencies.update(_node_parse_for_assigns(child))
    return dependencies


def _collect_class_attributes(class_node: ast.ClassDef) -> dict:
    """Собирает атрибуты класса с их типами из:
    - аннотаций (page: Page)
    - присваиваний в теле класса (page = Page())
    - инициализации в __init__/setup методах
    """
    class_scope = {"self": class_node.name}

    # 1. Аннотации атрибутов (Python 3.6+)
    class_scope.update(_node_parse_for_assigns(class_node))

    # 2. Поиск методов инициализации: __init__, setup
    init_methods = []
    for method in class_node.body:
        if isinstance(method, ast.FunctionDef) and method.name in ("__init__", "setup"):
            init_methods.append(method)

    # 3. Анализ методов инициализации
    for init_method in init_methods:
        for stmt in ast.walk(init_method):
            # Проверяем, что это присваивание и что у него есть поле value
            if not isinstance(stmt, ast.Assign) or not hasattr(stmt, "value"):
                continue

            # Ищем присваивания self.attr = ...
            if (
                len(stmt.targets) == 1
                and isinstance(stmt.targets[0], ast.Attribute)
                and isinstance(stmt.targets[0].value, ast.Name)
                and stmt.targets[0].value.id == "self"
            ):
                attr_name = stmt.targets[0].attr
                attr_type = None

                # Извлекаем тип из вызова конструктора
                if isinstance(stmt.value, ast.Call):
                    if isinstance(stmt.value.func, ast.Name):
                        attr_type = stmt.value.func.id

                # Для случаев типа self.page = other_obj.page
                elif isinstance(stmt.value, ast.Attribute):
                    if isinstance(stmt.value.value, ast.Name):
                        attr_type = f"{stmt.value.value.id}.{stmt.value.attr}"

                if attr_type is not None:
                    class_scope[attr_name] = attr_type

    return class_scope


def _find_deps(node: ast.AST, node_scope: dict | None = None, fixture_names: set | None = None) -> set[str]:
    """Находит зависимости в AST-узле."""
    dependencies = set()
    if node_scope is None:
        node_scope = {}
    if fixture_names is None:
        fixture_names = set()

    if isinstance(node, ast.FunctionDef):
        for arg in node.args.args:
            if arg.arg in fixture_names:
                dependencies.add(arg.arg)
    for child in ast.iter_child_nodes(node):
        # 1. Обработка self.attr
        if isinstance(child, ast.Attribute):
            chain = []
            child_value = child
            prev = child_value
            while isinstance(child_value, ast.Attribute):
                chain.append(child_value.attr)
                prev = child_value
                child_value = child_value.value
            if isinstance(child_value, ast.Name) and child_value.id == "self" and prev.attr in node_scope:  # type: ignore[unreachable]
                resolved_type = node_scope[prev.attr]
                if len(chain) > 1:
                    dependencies.add(f"{resolved_type}.{'.'.join(reversed(chain[:-1]))}")
                else:
                    dependencies.add(f"{resolved_type}.__init__")
                return dependencies

        # 2. Обработка вызовов obj.method()
        elif isinstance(child, ast.Call):
            func = child.func
            if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
                if func.value.id in node_scope:
                    obj_type = node_scope[func.value.id]
                    dependencies.add(f"{obj_type}.{func.attr}")
        # 3. Обработка параметров функции (фикстуры)
        elif isinstance(child, ast.FunctionDef):
            for arg in child.args.args:
                if arg.arg in fixture_names:
                    dependencies.add(arg.arg)
        # Рекурсивный обход
        dependencies.update(_find_deps(child, node_scope, fixture_names))
    return dependencies


def analyze_test_dependencies(root_dir: Path) -> dict:
    """Анализирует зависимости тестов в директории."""
    root = Path(root_dir)
    functions = {}
    IGNORE_DIRS = {".venv", ".git", "__pycache__", "dist", "build"}

    # Собираем все фикстуры проекта
    all_fixture_names = _collect_all_fixtures(root)

    for file_path in root.rglob("*.py"):
        # Анализируем файл
        if any(part in IGNORE_DIRS for part in file_path.parts):
            continue

        try:
            with open(file_path, encoding="utf-8") as f:
                tree = ast.parse(f.read())
        except Exception as e:
            print(f"[ERROR] Не удалось прочитать {file_path}: {e}")
            continue

        for node in ast.walk(tree):
            # Анализ классов
            if isinstance(node, ast.ClassDef):
                class_scope = _collect_class_attributes(node)
                class_name = node.name
                for method in node.body:
                    method_scope = dict(class_scope)
                    if isinstance(method, ast.FunctionDef):
                        method_name = f"{class_name}.{method.name}"

                        # Извлекаем метки
                        marks = set()
                        for decorator in method.decorator_list:
                            mark_name = _extract_marks_from_decorator(decorator)
                            if mark_name:
                                marks.add(mark_name)

                        # Объявления внутри метода
                        method_scope.update(_node_parse_for_assigns(method))

                        # Находим зависимости
                        deps = _find_deps(method, method_scope, all_fixture_names)
                        functions[method_name] = {"marks": marks, "dependencies": deps, "scope": method_scope}

            # Анализ функций вне классов
            elif isinstance(node, ast.FunctionDef):
                func_name = node.name
                marks = set()
                function_scope = _node_parse_for_assigns(node)

                for decorator in node.decorator_list:
                    mark_name = _extract_marks_from_decorator(decorator)
                    if mark_name:
                        marks.add(mark_name)

                deps = _find_deps(node, function_scope, all_fixture_names)
                functions[func_name] = {"marks": marks, "dependencies": deps, "scope": function_scope}

    return functions


def propagate_labels_to_dict(data: dict) -> dict:
    """
    Распространяет метки по словарю с зависимостями
    :param data: словарь с метками и зависимостями
    :return: словарь. Ключ — название элемента, значение — список всех меток (с распространением).

    """
    cache: dict[str, set] = {}

    def resolve_dependencies_chain(dependency: str, scope: dict) -> str | None:
        curr_scope = scope
        parts = dependency.split(".")
        if len(parts) < 3:
            return None
        cur_class = parts[0]
        attr = parts[1]
        for i in range(1, len(parts) - 1):
            if attr in curr_scope:
                cur_class = curr_scope.get(attr)
                curr_scope = data.get(f"{cur_class}.__init__", {})
                attr = parts[i + 1]
            else:
                return None
        return f"{cur_class}.{attr}"

    def get_all_labels(element_name: str) -> set[str]:
        """Рекурсивно получает все метки для элемента и его зависимостей."""
        if element_name in cache:
            return cache[element_name]

        element = data[element_name]
        current_labels = set(element["marks"])
        delete_dependencies = []
        # Собираем метки из зависимостей
        for dep_name in element["dependencies"]:
            if dep_name not in data:
                chain_result = resolve_dependencies_chain(dep_name, element["scope"])
                if chain_result is not None and chain_result in data:
                    dep_name = chain_result
                else:
                    delete_dependencies.append(dep_name)
                    continue
            # Рекурсивно получаем метки зависимости
            dep_labels = get_all_labels(dep_name)
            current_labels.update(dep_labels)

        for dependency in delete_dependencies:
            element["dependencies"].remove(dependency)
        cache[element_name] = current_labels
        return current_labels

    # Формируем итоговый словарь: элемент -> список меток
    result = {}
    for name in data.keys():
        all_labels = sorted(get_all_labels(name))
        result[name] = all_labels

    return result


def pytest_configure(config: pytest.Config) -> None:
    """Ранний анализ зависимостей при запуске pytest."""
    marks = config.getoption("-m")
    if len(marks) != 0:
        functions = analyze_test_dependencies(config.rootpath)
        DEPENDENCY_CACHE.update(propagate_labels_to_dict(functions))


def pytest_collection_modifyitems(config: pytest.Config, items: List[pytest.Item]) -> None:
    """Применяет метки к тестам после сбора."""
    marks = config.getoption("-m")
    if len(marks) == 0:
        return None
    if not DEPENDENCY_CACHE:
        functions = analyze_test_dependencies(config.rootpath)
        DEPENDENCY_CACHE.update(propagate_labels_to_dict(functions))

    for item in items:
        # Для методов класса: TestSuite.test_method
        func_key = f"{item.cls.__name__}.{item.name}"
        setup_key = f"{item.cls.__name__}.setup"
        init_key = f"{item.cls.__name__}.__init__"

        inherited_marks = list(
            set(
                DEPENDENCY_CACHE.get(func_key, [])
                + DEPENDENCY_CACHE.get(setup_key, [])
                + DEPENDENCY_CACHE.get(init_key, [])
            )
        )

        # Применяем метки
        for mark_name in inherited_marks:
            try:
                marker = getattr(pytest.mark, mark_name)
                item.add_marker(marker)
            except AttributeError:
                print(f"[WARNING] Метка '{mark_name}' не найдена в pytest.mark")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo) -> None:
    """Прикрепляет скриншот после падения теста к allure отчету."""
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call":
        if rep.failed:
            try:
                page_fixture = item.funcargs.get("page")
                if page_fixture is not None:
                    page_context = page_fixture.context
                    page = page_context.pages[-1]
                    if page:
                        allure.attach(
                            page.screenshot(),
                            name=f"screenshot-{item.nodeid}.png",
                            attachment_type=allure.attachment_type.PNG,
                        )
            except Exception as e:
                print(f"Failed to attach screenshot: {e}")
    elif rep.when == "teardown":
        log_file = Path(os.path.join(LOGS_FOLDER, item.name.replace("/", "_") + ".log"))
        har_file = Path(os.path.join(HAR_DIR, item.name.replace("/", "_") + ".har"))
        if log_file.exists():
            allure.attach.file(log_file, name=log_file.name, attachment_type=allure.attachment_type.TEXT)
        if har_file.exists():
            allure.attach.file(har_file, name=har_file.name, attachment_type=allure.attachment_type.JSON)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_call(item: pytest.Item) -> None:
    outcome = yield
    if hasattr(outcome, "exception") and hasattr(outcome.exception, "name") and outcome.exception.name == "TimeoutError":
        page = get_page_from_test(item)
        if page:
            locator = page.locator("[class*=modal-content]")
            if locator.count() > 0:
                if hasattr(outcome.exception, "message") and hasattr(outcome, "excinfo") and len(outcome.excinfo) > 2:
                    tb = outcome.excinfo[2]
                    raise AssertionError("[Modal] Unexpected modal window\n" + outcome.exception.message).with_traceback(
                        tb
                    )
                else:
                    raise AssertionError("[Modal] Unexpected modal window")


def get_page_from_test(item: pytest.Item) -> Page | None:
    if hasattr(item, "funcargs"):
        for arg_name, arg_value in item.funcargs.items():
            if isinstance(arg_value, Page):
                return arg_value
    return None


def pytest_terminal_summary(terminalreporter: TerminalReporter, exitstatus: ExitCode, config: Config) -> None:
    try:
        if get_var_from_env("GENERATE_SUMMARY") != "true":
            return
    except ValueError:
        return
    try:
        if not hasattr(config, "workerinput"):
            passed = len(terminalreporter.stats.get("passed", []))
            failed = len(terminalreporter.stats.get("failed", []))
            error = len(terminalreporter.stats.get("error", []))
            skipped = len(terminalreporter.stats.get("skipped", []))
            total = passed + failed + error + skipped
            file_name = "session-result.txt"
            if os.path.exists(file_name):
                with open(file_name) as f:
                    first_line = f.readline()
                    nums = [item.split(" ")[0] for item in first_line.split(", ")]
                    total += int(nums[0])
                    passed += int(nums[1])
                    failed += int(nums[2])
                    error += int(nums[3])
                    skipped += int(nums[4])
            with open(file_name, "w") as f:
                f.write(f"{total} tests, {passed} passed, {failed} failed, {error} error, {skipped} skipped\n")
    except Exception as e:
        print(f"\nПри попытке сделать статистику возникла ошибка:\n{e}")


@pytest.fixture
def remove_file_from_download_folder() -> list:
    """Фикстура для удаления файла после теста из папки root/download"""
    file_names: list = []
    yield file_names
    for item in file_names:
        file_check = CheckFile(item)
        file_check.remove_file_from_download()


@pytest.fixture
def test_name(request: pytest.FixtureRequest) -> str:
    if request.node.name:
        name = request.node.name.replace("/", "_")
        test_context.test_name = name
        return name
    else:
        return ""


@pytest.fixture(autouse=True)
def create_log_file(request: pytest.FixtureRequest, test_name: str) -> None:
    create_logger(log_level=get_var_from_env("LOG_LEVEL", "INFO"), log_file_name=test_name + ".log")

    allure.step = step_decorator(allure.step)


@pytest.fixture(autouse=True)
def dump_dom(request: pytest.FixtureRequest, test_name: str) -> None:
    """Пишет DOM после каждого шага теста, если pytest запущен с ключом --dump-dom.

    Снимок делается на выходе из каждого `with allure.step(...)` теста; шаги внутри
    пейдж-объектов вложены и отдельных снимков не дают. Файл кладётся в
    scripts/dom_inspector/dumps и разбирается командой
    `python -m scripts.dom_inspector.cli steps <файл>`.
    """
    if not request.config.getoption("--dump-dom"):
        yield
        return

    from scripts.dom_inspector.dom_recorder import case_no_from_title, start_recording, stop_recording

    title = None
    for marker in request.node.own_markers:
        if marker.kwargs.get("label_type") == "as_title" and marker.args:
            title = marker.args[0]
    dumps_dir = Path(__file__).resolve().parent / "scripts" / "dom_inspector" / "dumps"
    dump_path = dumps_dir / f"{test_name}.txt"
    recorder = start_recording(dump_path, case_no_from_title(title), request.node.name)
    try:
        yield
    finally:
        stop_recording(recorder)
        print(f"[dump-dom] снимков записано: {recorder.written} -> {dump_path}")
        for reason in recorder.skipped:
            print(f"[dump-dom] пропущено: {reason}")


@pytest.fixture(autouse=True, scope="session")
def clear_temp_dir() -> None:
    try:
        shutil.rmtree(TEMP_DIR)
    except Exception:
        pass


@pytest.fixture
def user(request: pytest.FixtureRequest) -> User:
    """Фикстура для получения пользователя из маркера @pytest.mark.user

    Пользователи хранятся в Enum common.enums.user.User
    Доступные пользователи: Admin (по умолчанию), ADMIN_TEST, SELLER_JR_TEST, SELLER_TEST, SELLER_SR_TEST,
    CUSTOMER_CARE_TEST, SP_MANAGER_TEST, SECURITY_TEST, FINANCE_TEST
    """
    marker = request.node.get_closest_marker("user")
    if not marker:
        return User.get_default()

    user_arg = marker.args[0]
    if isinstance(user_arg, User):
        return user_arg

    raise TypeError(
        "Маркер @pytest.mark.user должен принимать Enum User. Пример: @pytest.mark.user(User.SP_MANAGER_TEST)"
    )
