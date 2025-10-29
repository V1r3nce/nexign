import os
import re
import sys
from pathlib import Path, WindowsPath
from typing import List, Set, Tuple

import toml

PROJECT_ROOT_PATH = Path(__file__).resolve().parent.parent.parent

DEFAULT_PYTEST_MARKERS = {"skip", "skipif", "xfail", "usefixtures", "parametrize"}
DEFAULT_SUITS = {"regress", "smoke", "extended_regress"}
EXCLUDED_MARKERS = {"nbss_portal_mock"}


def get_pyproject_toml_path() -> str:
    """Возвращает путь к файлу pyproject.toml в корневой директории проекта."""
    path = os.path.join(PROJECT_ROOT_PATH, "pyproject.toml")
    if os.path.exists(path):
        return path
    else:
        raise FileNotFoundError(f"pyproject.toml was not found at path: {path}")


def get_markers_from_pyproject() -> set[str]:
    """Возвращает список маркеров из pyproject.toml"""
    with open(get_pyproject_toml_path(), encoding="utf-8") as f:
        config = toml.load(f)

    markers_section = config.get("tool", {}).get("pytest", {}).get("ini_options", {}).get("markers", [])
    markers = set()

    for line in markers_section:
        line = line.strip()
        if not line or ":" not in line:
            continue
        marker = line.split(":")[0].strip()
        markers.add(marker)

    if not markers:
        print("Failed to get allowed markers from pyproject.toml:")
        sys.exit(1)

    return markers


def get_allowed_product_markers() -> set[str]:
    """Возвращает список разрешенных продуктовых маркеров"""
    markers = get_markers_from_pyproject() - DEFAULT_SUITS
    return markers | EXCLUDED_MARKERS


def get_all_allowed_markers() -> set[str]:
    """Возвращает список всех разрешенных маркеров"""
    return get_markers_from_pyproject() | DEFAULT_SUITS | DEFAULT_PYTEST_MARKERS | EXCLUDED_MARKERS


def is_test_file(file_path: str | WindowsPath) -> bool:
    """Проверяет, что файл является тестовым
    :param file_path: Путь к файлу
    :return: True если файл является тестовым, иначе False"""
    filename = os.path.basename(file_path) if isinstance(file_path, str) else file_path.name
    file_path = file_path if isinstance(file_path, str) else file_path.as_posix()
    return (
        (file_path.startswith("tests/") or "/tests/" in file_path)
        and (filename.startswith("test_") or filename.endswith("_test.py"))
        and file_path.endswith(".py")
    )


def find_markers(content: str) -> List[Tuple[str, int]]:
    """Находит маркеры в тестовом файле
    :param content: Содержимое файла
    :return: Список кортежей (маркер, номер строки)"""
    markers = []
    for line_num, line in enumerate(content.splitlines(), 1):
        matches = re.findall(r"@pytest\.mark\.(\w+)", line)
        for marker in matches:
            markers.append((marker, line_num))
    return markers


def check_invalid_markers(file_path: str) -> bool:
    """Проверяет, что в файле нет неразрешенных маркеров."""
    with open(file_path, encoding="utf-8") as f:
        content = f.read()
    abs_path = os.path.abspath(file_path)
    markers_with_lines = find_markers(content)

    invalid_markers = [
        marker
        for marker, _ in markers_with_lines
        if marker not in get_all_allowed_markers() and marker not in DEFAULT_PYTEST_MARKERS
    ]
    if invalid_markers:
        print("Error: Found invalid marker(s) in the test file:")
        for marker in set(invalid_markers):
            print(f"- '{marker}'")
        print(f'File "{abs_path}", line 1\n')
        return False

    return True


def check_required_markers(file_path: str, required_markers: Set[str], marker_type: str) -> bool:
    """Проверяет наличие хотя бы одного из требуемых маркеров в файле.

    :param file_path: Путь к файлу
    :param required_markers: Множество маркеров, которые должны быть найдены
    :param marker_type: Тип маркера для вывода сообщения
    :return: True, если условие выполнено, иначе False
    """
    with open(file_path, encoding="utf-8") as f:
        content = f.read()
    abs_path = os.path.abspath(file_path)
    markers_with_lines = find_markers(content)

    found_markers = [marker for marker, _ in markers_with_lines if marker in required_markers]
    has_required_marker = bool(found_markers)

    if not has_required_marker:
        print(f"Error: No any {marker_type} marker found in the test file.")
        print(f'File "{abs_path}", line 1\n')
        return False

    return True


def get_changed_files() -> List[str]:
    """Возвращает список измененных файлов в текущей ветке.
    :return: Список измененных файлов в текущей ветке"""
    try:
        staged_files = os.popen("git diff --cached --name-only --diff-filter=ACM").read().splitlines()
        return staged_files
    except Exception as e:
        print(f"Failed to get the list of changed files: {e}")
        return []


def main() -> None:
    """Основная функция. Если передан аргумент --all, то проверяются все тестовые файлы в папке tests.
    Иначе, проверяются только измененные файлы."""
    check_all = "--all" in sys.argv

    product_markers = get_allowed_product_markers()

    test_files = []

    if check_all:
        tests_dir = Path(PROJECT_ROOT_PATH) / "tests"
        for file in tests_dir.rglob("*"):
            if is_test_file(file):
                test_files.append(str(file))

    else:
        test_files = [f for f in get_changed_files() if is_test_file(f)]

    success = True
    for file_path in test_files:
        full_path = os.path.join(PROJECT_ROOT_PATH, file_path)
        if not os.path.exists(full_path):
            continue

        if not check_invalid_markers(full_path):
            success = False

        if not check_required_markers(full_path, product_markers, "product"):
            success = False

        if not check_required_markers(full_path, DEFAULT_SUITS | EXCLUDED_MARKERS, "suit"):
            success = False

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
