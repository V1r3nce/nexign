import os
from contextlib import contextmanager
from pathlib import Path

import allure
import pandas as pd
from openpyxl.utils.exceptions import InvalidFileException
from playwright.sync_api import Download

from common.helpers.checker import assert_that, wait_that
from common.helpers.env_helper import DOWNLOAD_DIR
from models.lis_resources import RangeValue, SIMTemplate
from models.stand_context import stand_context


class CheckFile:
    """Класс для проверки загрузки и проверки локальных файлов (браузер, SFTP и т.д.)."""

    def __init__(self, file_name: str, directory: Path | None = None) -> None:
        self.file_name = file_name
        self.directory = directory if directory is not None else DOWNLOAD_DIR
        self.path = self.get_download_file_path()

    def __str__(self) -> str:
        return self.file_name

    def __repr__(self) -> str:
        return self.file_name

    @property
    def name(self) -> str:
        return self.path.name

    @property
    def format(self) -> str:
        return self.path.suffix

    def get_download_file_path(self) -> Path:
        """Получить полный путь к файлу (по умолчанию в папке download)."""
        full_path = self.directory / self.file_name
        full_path.parent.mkdir(parents=True, exist_ok=True)
        return full_path

    @property
    def exists_locally(self) -> bool:
        return self.path.exists()

    def remove_file_if_exists(self) -> None:
        """Удалить файл, если он есть на диске."""
        if self.exists_locally:
            os.remove(self.path)

    def remove_file_from_download(self) -> None:
        """Удалить файл в папке download"""
        os.remove(self.path)

    @allure.step("Проверить тип загруженного файла")
    def check_file_type(self, expect_type: str) -> None:
        assert_that(
            lambda: self.format == expect_type,
            message=f"Неверный тип файла: ожидался {expect_type}, получен {self.format}",
        )

    @allure.step("Проверить, что файл '{0}' загрузился")
    def is_exist(self) -> None:
        wait_that(
            lambda: os.path.exists(self.path),
            exception=FileNotFoundError,
            timeout=10,
            sleep_seconds=0.5,
            message=f"Не сохранился файл {self.file_name} в установленное время",
        )

    @allure.step("Проверить, что файл '{0}' типа Excel")
    def is_excel_file(self) -> None:
        """Проверяет, что файл имеет формат для работы в excel."""
        excel_formats = [".xlsx", ".xls", ".csv"]
        assert self.format in excel_formats, f"Файл {self.file_name} не Excel формата"

    def _read_excel_file(self, sheet_name: int | str = 0) -> pd.DataFrame:
        try:
            df = pd.read_excel(self.path, engine="openpyxl", sheet_name=sheet_name, header=None)
        except InvalidFileException:
            df = pd.read_excel(self.path, engine="xlrd", sheet_name=sheet_name, header=None)
        return df

    @allure.step("Проверить, что файл {0} в полях '{fields}' содержит значения '{expected_values}'")
    def check_excel_file_group_of_fields_contains(
        self, fields: list, expected_values: list, sheet_name: int | str = 0
    ) -> None:
        """Проверяет значения из ячеек файла Excel
        param:
            fields: координаты ячеек списком, где первое значение строка, второе - столбец,
            например [[0, 1], [2, 1]] для B1 и B3
            expected_values: ожидаемые значения в ячейках
            sheet_name: название листа или индекс
        """
        self.is_exist()
        self.is_excel_file()
        df = self._read_excel_file(sheet_name)
        result_list = []  # type: list[str | None]
        for item in fields:
            cell_field_value = df.iloc[item[0], item[1]]
            if pd.isnull(cell_field_value):
                result_list.append(None)
            else:
                result_list.append(str(cell_field_value))
        assert result_list == expected_values, (
            f"Некорректное значение в ячейке '{result_list}',\nожидаемое '{expected_values}'"
        )

    @allure.step("Проверить, что файл {0}  содержит '{expected_row_numbers}' заполненных строк на листе '{sheet_name}'")
    def check_excel_file_contain_filled_rows(self, expected_row_numbers: int, sheet_name: int | str = 0) -> None:
        """Проверяет количество заполненных строк файла Excel
        param:
            expected_row_numbers: ожидаемое значения заполненных строк
            sheet_name: название листа или индекс
        """
        self.is_exist()
        self.is_excel_file()
        df = self._read_excel_file(sheet_name)
        assert df.shape[0] == expected_row_numbers, (
            f"Некорректное количество строк в Excel, ожидаемое {expected_row_numbers} фактическое {df.shape[0]}"
        )

    @allure.step(
        "Проверить, что файл {0}  содержит значение '{expected_value}' в столбце {column} на листе '{sheet_name}'"
    )
    def check_excel_file_contain_value_in_column(
        self, expected_value: str | int, column: int, sheet_name: int | str = 0
    ) -> None:
        """Проверяет, что столбец файла Excel содержит определенное значение
        param:
            expected_value: ожидаемое значения в столбце
            column: номер столбца
            sheet_name: название листа или индекс
        """
        self.is_exist()
        self.is_excel_file()
        df = self._read_excel_file(sheet_name)
        assert expected_value in df.iloc[:, column].values, f"Значение {expected_value} отсутствует в столбце {column}"

    @allure.step("Проверка таблицы в Excel файле {0}")
    def check_excel_file_table(self, headers: list[str], value_list: list[list[str]]) -> None:
        self.check_excel_file_contain_filled_rows(len(value_list) + 1)
        first_line = [[0, i] for i in range(len(headers))]
        self.check_excel_file_group_of_fields_contains(first_line, headers)
        for line_index in range(1, len(value_list) + 1):
            line = [[line_index, i] for i in range(len(headers))]
            self.check_excel_file_group_of_fields_contains(line, value_list[line_index - 1])

    @allure.step("Проверить, что файл '{0}' типа PDF")
    def check_pdf(self, min_size: int = 200) -> None:
        """Проверяет, что файл корректный pdf."""
        self.is_exist()
        self.check_file_type(".pdf")

        with allure.step("Проверить минимальный размер PDF"):
            assert self.size >= min_size, f"PDF файл слишком маленький ({self.size} байт), возможно поврежден"

        with allure.step("Проверить сигнатуру PDF"):
            assert self.signature == b"%PDF", (
                f"Файл {self.file_name} имеет расширение PDF, но сигнатура {self.signature!r} — поврежден или не PDF"
            )

    @property
    def size(self) -> int:
        """Размер файла в байтах"""
        return os.path.getsize(self.path)

    @property
    def signature(self) -> bytes:
        """Первые 4 байта файла - сигнатура"""
        with open(self.path, "rb") as pdf_file:
            return pdf_file.read(4)

    @allure.step("Обработать скачанный ПДФ файл")
    def process_downloaded_pdf(self, download: Download, delete_after_check: bool = True) -> Path:
        """
        Принимает объект download из Playwright:
        - сохраняет файл в DOWNLOAD_DIR
        - проверяет, что файл валидный PDF
        - при необходимости удаляет файл после проверки
        :param download: объект Playwright Download
        :param delete_after_check: если True — удалить файл сразу после проверки
        :return: путь к сохраненному файлу
        """
        with allure.step("Сохранить файл в директорию загрузок"):
            if self.path.exists():
                self.path.unlink()
            download.save_as(self.path)

        with allure.step("Проверить, что скачанный файл — валидный PDF"):
            self.check_pdf()

        if delete_after_check:
            with allure.step("Удалить файл после проверки"):
                self.remove_file_from_download()

        return self.path


@allure.step("Создать файл для загрузки SIM")
def create_txt_file_to_upload_sim(
    file_name: str, imsi_list: list, icc_list: list, amount: int = 2, template: SIMTemplate | None = None
) -> CheckFile:
    if template is None:
        template = stand_context.stand_equipment.sim_template
    template_dict = {k: v for k, v in template.__dict__.items() if isinstance(v, RangeValue)}
    sorted_template_elements = dict(sorted(template_dict.items(), key=lambda item: item[1].min_value))
    file_check = CheckFile(file_name)
    file_path = file_check.get_download_file_path()
    data = {}
    for index, (key, value) in enumerate(sorted_template_elements.items()):
        match key:
            case "IMSI":
                data[f"Column{index + 1}"] = imsi_list
            case "ICC":
                data[f"Column{index + 1}"] = icc_list
            case _:
                data[f"Column{index + 1}"] = "0" * (value.max_value - value.min_value + 1)
    df = pd.DataFrame(data)
    df.to_csv(file_path, sep=" ", index=False, header=False)
    file_check.is_exist()
    return file_check


@contextmanager
def wrap_file_and_delete_after(file: CheckFile) -> CheckFile:
    try:
        yield file
    finally:
        file.remove_file_if_exists()
