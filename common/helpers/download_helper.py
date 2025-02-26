import os
import allure
import pandas as pd
from waiting import wait
from openpyxl.utils.exceptions import InvalidFileException
from common.helpers.env_helper import DOWNLOAD_DIR


class CheckFile:
    """Класс для проверки загрузки и проверки файлов скачиваемых в браузере."""

    def __init__(self, file_name):
        self.file_name = file_name
        self.path = self.get_download_file_path()

    def __str__(self):
        return self.file_name

    def __repr__(self):
        return self.file_name

    @property
    def name(self):
        return self.path.name

    @property
    def format(self):
        return self.path.suffix

    def get_download_file_path(self):
        """Получить путь к файлу в папке download"""
        DOWNLOAD_DIR.mkdir(exist_ok=True)
        return DOWNLOAD_DIR / self.file_name

    def remove_file_from_download(self):
        """Удалить файл в папке download"""
        os.remove(self.path)

    @allure.step("Проверить, что файл '{0}' загрузился")
    def is_exist(self):
        wait(
            lambda: os.path.exists(self.path),
            timeout_seconds=10, sleep_seconds=0.5,
            waiting_for=f"Не сохранился файл {self.file_name} в установленное время")

    @allure.step("Проверить, что файл '{0}' типа Excel")
    def is_excel_file(self):
        """Проверяет, что файл имеет формат для работы в excel."""
        excel_formats = [".xlsx", ".xls", ".csv"]
        assert self.format in excel_formats, f"Файл {self.file_name} не Excel формата"

    def _read_excel_file(self, sheet_name: int | str = 0):
        try:
            df = pd.read_excel(self.path, engine="openpyxl", sheet_name=sheet_name, header=None)
        except InvalidFileException:
            df = pd.read_excel(self.path, engine="xlrd", sheet_name=sheet_name, header=None)
        return df

    @allure.step("Проверить, что файл {0} в полях '{fields}' содержит значения '{expected_values}'")
    def check_excel_file_group_of_fields_contains(self, fields: list, expected_values: list,
                                                  sheet_name: int | str = 0):
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
        result_list = []
        for item in fields:
            cell_field_value = df.iloc[item[0], item[1]]
            result_list.append(cell_field_value)
        assert result_list == expected_values, (f"Некорректное значение в ячейке '{result_list}',"
                                                f" ожидаемое '{expected_values}'")

    @allure.step("Проверить, что файл {0}  содержит '{expected_row_numbers}' заполненных строк на листе '{sheet_name}'")
    def check_excel_file_contain_filled_rows(self, expected_row_numbers: int, sheet_name: int | str = 0):
        """Проверяет количество заполненных строк файла Excel
        param:
            expected_row_numbers: ожидаемое значения заполненных строк
            sheet_name: название листа или индекс
        """
        self.is_exist()
        self.is_excel_file()
        df = self._read_excel_file(sheet_name)
        assert df.shape[0] == expected_row_numbers, (f"Некорректное количество строк в Excel,"
                                                     f" ожидаемое {expected_row_numbers} фактическое {df.shape[0]}")
