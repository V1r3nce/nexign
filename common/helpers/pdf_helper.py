from pathlib import Path

import pdfplumber

from common.exceptions import UnexpectedTextInPdfException
from common.helpers.checker import check_that


def parse_pdf_text(path: Path) -> str:
    """
    Функция для преобразования PDF-файла в строку
    :param path: путь к PDF-файлу
    :return: строковое представление PDF-файла
    """

    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text += page.extract_text()

    return text


def check_text_in_pdf(path: Path, expected_texts: list[str], search_string: str = None) -> None:
    """
    Проверка отображения цен в PDF-файле
    :param path: путь к PDF-файлу
    :param expected_texts: ожидаемый массив строк в pdf-файле
    :param search_string: подстрока для поиска строки, в которой будет осуществлен поиск ожидаемых строк
    """

    pdf_text = parse_pdf_text(path)
    search_scope = ""

    if search_string:
        pdf_lines = pdf_text.split("\n")
        search_scope = next(filter(lambda line: line.__contains__(search_string), pdf_lines), None)
    else:
        search_scope = pdf_text

    for text in expected_texts:
        check_that(
            lambda: (search_scope.__contains__(text)),
            exception=UnexpectedTextInPdfException,
            message="Текст в pdf-файле отличается от ожидаемого",
        )
