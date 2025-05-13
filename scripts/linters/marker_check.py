import configparser
import os
import re
import sys
from pathlib import Path
from typing import List, Set, Tuple

PROJECT_ROOT_PATH = Path(__file__).resolve().parent.parent.parent

DEFAULT_PYTEST_MARKERS = {"skip", "skipif", "xfail", "usefixtures", "parametrize"}


def get_pytest_ini_path() -> str:
    """Возвращает путь к файлу pytest.ini в корневой директории проекта."""
    path = os.path.join(PROJECT_ROOT_PATH, "pytest.ini")
    if os.path.exists(path):
        return path
    else:
        raise FileNotFoundError(f"pytest.ini was not found at path: {path}")


def get_allowed_markers() -> Set[str]:
    """Возвращает список разрешенных маркеров из pytest.ini"""
    config = configparser.ConfigParser()
    config.read(get_pytest_ini_path())

    markers_section = config.get("pytest", "markers", fallback="")
    allowed_markers = set()

    for line in markers_section.split("\n"):
        line = line.strip()
        if not line or ":" not in line:
            continue
        marker = line.split(":")[0].strip()
        allowed_markers.add(marker)

    if not allowed_markers:
        print("Failed to get allowed markers from pytest.ini:")
        sys.exit(1)

    allowed_markers |= DEFAULT_PYTEST_MARKERS

    return allowed_markers


def is_test_file(file_path: str) -> bool:
    """Проверяет, что файл является тестовым
    :param file_path: Путь к файлу
    :return: True если файл является тестовым, иначе False"""
    filename = os.path.basename(file_path)
    return (
        file_path.startswith("tests/")
        or "/tests/" in file_path
        or filename.startswith("test_")
        or filename.endswith("_test.py")
    ) and file_path.endswith(".py")


def find_markers(content: str) -> List[Tuple[str, int]]:
    """Находит маркеры в тестовом файле
    :param content: Содержимое файла
    :return: Список кортежей (маркер, номер строки)"""
    markers = []
    for line_num, line in enumerate(content.splitlines(), 1):
        matches = re.findall(r"@pytest\.mark\.(\w+)", line)
        for marker in matches:
            if marker not in DEFAULT_PYTEST_MARKERS:
                markers.append((marker, line_num))
    return markers


def check_markers(file_path: str, allowed_markers: Set[str]) -> bool:
    """Проверяет маркеры в тестовом файле. Если есть хотя бы один разрешенный маркер, возвращает True.
    :param file_path: Путь к файлу
    :param allowed_markers: Разрешенные маркеры
    :return: True если есть хотя бы один разрешенный маркер, иначе False"""
    with open(file_path, encoding="utf-8") as f:
        content = f.read()
    abs_path = os.path.abspath(file_path)
    markers_with_lines = find_markers(content)
    if not markers_with_lines:
        print("Error: There are no pytest markers in the test file")
        print(f'File "{abs_path}", line 1\n')
        return False

    invalid_markers = []
    for marker, line_num in markers_with_lines:
        if marker not in allowed_markers:
            invalid_markers.append((marker, line_num))

    if invalid_markers:
        lines_with_error = []

        for marker, line_num in invalid_markers:
            clickable_link = f'File "{abs_path}", line {line_num}'

            lines_with_error.append(f"{clickable_link} - '{marker}'")
        print("Error: Invalid marker found:")
        for error in lines_with_error:
            print(error)
        print(f"Allowed markers: {', '.join(allowed_markers)}\n")
        return False
    return True


def get_changed_files() -> List[str]:
    """Возвращает список измененных файлов в текущей ветке.
    :return: Список измененных файлов в текущей ветке"""
    try:
        staged = os.popen("git diff --cached --name-only --diff-filter=ACM").read().splitlines()
        untracked = os.popen("git ls-files --others --exclude-standard").read().splitlines()

        all_files = set(untracked) | set(staged)
        return list(all_files)
    except Exception as e:
        print(f"Failed to get the list of changed files: {e}")
        return []


def main() -> None:
    """Основная функция. Если передан аргумент --all, то проверяются все тестовые файлы в папке tests.
    Иначе, проверяются только измененные файлы."""
    check_all = "--all" in sys.argv

    markers = get_allowed_markers()

    test_files = []
    if check_all:
        for root, _, files in os.walk(os.path.join(PROJECT_ROOT_PATH, "tests")):
            for file in files:
                if is_test_file(file):
                    file_path = os.path.join(root, file)
                    test_files.append(file_path)
    else:
        test_files = [f for f in get_changed_files() if is_test_file(f)]

    success = True
    for file_path in test_files:
        full_path = os.path.join(PROJECT_ROOT_PATH, file_path)
        if not os.path.exists(full_path):
            continue
        if not check_markers(full_path, markers):
            success = False

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
