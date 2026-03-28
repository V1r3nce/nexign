import csv
from pathlib import Path
from typing import Any, Dict, List, Optional

import allure
import pandas as pd

from common.helpers.download_helper import CheckFile
from sftp.exceptions import SFTPCSVValidationError, SFTPFileNotFound


class SFTPFileHelper(CheckFile):
    """
    Локальная работа с файлом после того, как его скачали с SFTP.

    Здесь нет SFTP-клиента и сетевых операций, сессию и ``download_file``
    выполняет ``SFTPRequests`` (``open_file`` / ``open_csv_file`` возвращают этот хелпер).
    В этом классе — CSV (чтение/запись), валидация строк и файл конфликтов.
    Общие операции с путём на диске — в базовом ``CheckFile``.

    Префикс SFTP в имени — про сценарий тестов (выгрузка с сервера), а не про то,
    что протокол реализован внутри класса.
    """

    def __init__(self, file_name: str, local_dir: Path | None = None) -> None:
        super().__init__(file_name, directory=local_dir)

    def __repr__(self) -> str:
        return f"SFTPFileHelper(file_name='{self.file_name}')"

    @allure.step("SFTP: Удаление локального файла {0}")
    def remove_local_file(self) -> None:
        self.remove_file_if_exists()

    @allure.step("SFTP: Проверка типа файла {0}")
    def check_file_type(self, expected_type: str) -> None:
        super().check_file_type(expect_type=expected_type)

    @allure.step("SFTP: Чтение CSV файла {0}")
    def read_csv(self, encoding: str = "utf-8", delimiter: str = ",") -> pd.DataFrame:
        """
        Прочитать CSV файл в DataFrame
        :param encoding: кодировка файла
        :param delimiter: разделитель полей
        :return: DataFrame с содержимым файла
        """
        if not self.exists_locally:
            raise SFTPFileNotFound(f"Файл {self.file_name} не найден локально")

        try:
            df = pd.read_csv(self.path, encoding=encoding, delimiter=delimiter)
            return df
        except Exception as e:
            raise SFTPCSVValidationError(f"Ошибка чтения CSV файла: {str(e)}")

    @allure.step("SFTP: Чтение CSV файла {0} как список словарей")
    def read_csv_as_dicts(self, encoding: str = "utf-8", delimiter: str = ",") -> List[Dict[str, Any]]:
        """
        Прочитать CSV файл как список словарей (каждая строка - словарь)
        :param encoding: кодировка файла
        :param delimiter: разделитель полей
        :return: список словарей
        """
        if not self.exists_locally:
            raise SFTPFileNotFound(f"Файл {self.file_name} не найден локально")

        try:
            with open(self.path, encoding=encoding, newline="") as csvfile:
                reader = csv.DictReader(csvfile, delimiter=delimiter)
                return list(reader)
        except Exception as e:
            raise SFTPCSVValidationError(f"Ошибка чтения CSV файла: {str(e)}")

    @allure.step("SFTP: Запись данных в CSV файл {0}")
    def write_csv(
        self,
        data: List[Dict[str, Any]],
        fieldnames: Optional[List[str]] = None,
        encoding: str = "utf-8",
        delimiter: str = ",",
    ) -> None:
        """
        Записать данные в CSV файл
        :param data: список словарей для записи
        :param fieldnames: список имен полей (если None, берутся из первой записи)
        :param encoding: кодировка файла
        :param delimiter: разделитель полей
        """
        if not data:
            raise SFTPCSVValidationError("Нет данных для записи в CSV")

        if fieldnames is None:
            fieldnames = list(data[0].keys())

        try:
            with open(self.path, "w", encoding=encoding, newline="") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=delimiter)
                writer.writeheader()
                writer.writerows(data)
        except Exception as e:
            raise SFTPCSVValidationError(f"Ошибка записи CSV файла: {str(e)}")

    @allure.step("SFTP: Добавление колонки 'Ошибка' к записям с конфликтами")
    def add_error_column_to_conflicts(
        self,
        conflict_records: List[Dict[str, Any]],
        conflicts_map: Dict[int, List[str]],
        encoding: str = "utf-8",
        delimiter: str = ",",
    ) -> None:
        """
        Создать новый файл с записями, у которых есть конфликты, добавив колонку 'Ошибка'
        :param conflict_records: записи с конфликтами
        :param conflicts_map: словарь {индекс_записи_в_исходном_файле: [список_конфликтов]}
        :param encoding: кодировка файла
        :param delimiter: разделитель полей
        """
        if not conflict_records:
            return

        original_indices = sorted(conflicts_map.keys())

        for conflict_idx, original_idx in enumerate(original_indices):
            if original_idx in conflicts_map:
                conflict_records[conflict_idx]["Ошибка"] = "; ".join(conflicts_map[original_idx])

        fieldnames = list(conflict_records[0].keys())
        if "Ошибка" not in fieldnames:
            fieldnames.append("Ошибка")

        conflict_file_name = self.file_name.replace(".csv", "_conflicts.csv")
        conflict_path = self.directory / conflict_file_name

        try:
            with open(conflict_path, "w", encoding=encoding, newline="") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=delimiter)
                writer.writeheader()
                writer.writerows(conflict_records)
        except Exception as e:
            raise SFTPCSVValidationError(f"Ошибка записи файла конфликтов: {str(e)}")

    @allure.step("SFTP: Валидация наличия обязательных полей")
    def validate_required_fields(
        self, records: List[Dict[str, Any]], required_fields: List[str]
    ) -> Dict[int, List[str]]:
        """
        Проверить наличие обязательных полей в записях
        :param records: список записей для проверки
        :param required_fields: список обязательных полей
        :return: словарь {индекс_записи: [список_ошибок]}
        """
        errors = {}
        for idx, record in enumerate(records):
            record_errors = []
            for field in required_fields:
                if field not in record or not record[field] or str(record[field]).strip() == "":
                    record_errors.append(f"Отсутствует обязательное поле '{field}'")

            if record_errors:
                errors[idx] = record_errors

        return errors

    @allure.step("SFTP: Валидация значений по справочнику")
    def validate_against_reference(
        self, records: List[Dict[str, Any]], field_name: str, valid_values: List[str]
    ) -> Dict[int, List[str]]:
        """
        Проверить значения поля по справочнику допустимых значений
        :param records: список записей для проверки
        :param field_name: имя поля для проверки
        :param valid_values: список допустимых значений
        :return: словарь {индекс_записи: [список_ошибок]}
        """
        errors = {}
        for idx, record in enumerate(records):
            if field_name in record:
                value = str(record[field_name]).strip()
                if value and value not in valid_values:
                    error_msg = f"Значение '{value}' поля '{field_name}' отсутствует в справочнике"
                    errors[idx] = [error_msg]

        return errors

    @allure.step("SFTP: Формирование конфликтов из API")
    def format_api_conflicts(self, api_response: Dict[str, Any], record_id_field: str = "id") -> Dict[int, List[str]]:
        """
        Преобразовать конфликты из API в формат {индекс_записи: [конфликты]}
        :param api_response: ответ API с конфликтами
        :param record_id_field: имя поля с идентификатором записи
        :return: словарь конфликтов
        """
        conflicts = {}

        if "conflicts" in api_response:
            for conflict in api_response["conflicts"]:
                record_id = conflict.get(record_id_field)
                errors = conflict.get("errors", [])
                if record_id is not None:
                    conflicts[int(record_id)] = errors

        return conflicts

    @allure.step("SFTP: Полная валидация CSV файла с конфликтами")
    def validate_csv_with_conflicts(
        self,
        required_fields: List[str] = None,
        reference_validations: Dict[str, List[str]] = None,
        api_conflicts: Dict[int, List[str]] = None,
        encoding: str = "utf-8",
        delimiter: str = ",",
    ) -> bool:
        """
        Выполнить полную валидацию CSV файла и создать файл с конфликтами
        :param required_fields: список обязательных полей
        :param reference_validations: словарь {имя_поля: [допустимые_значения]}
        :param api_conflicts: конфликты из API {индекс: [ошибки]}
        :param encoding: кодировка файла
        :param delimiter: разделитель полей
        :return: True если есть конфликты, False иначе
        """
        records = self.read_csv_as_dicts(encoding=encoding, delimiter=delimiter)
        all_conflicts: Dict[int, List[str]] = {}

        if required_fields:
            field_errors = self.validate_required_fields(records, required_fields)
            for idx, errors in field_errors.items():
                all_conflicts.setdefault(idx, []).extend(errors)

        if reference_validations:
            for field_name, valid_values in reference_validations.items():
                ref_errors = self.validate_against_reference(records, field_name, valid_values)
                for idx, errors in ref_errors.items():
                    all_conflicts.setdefault(idx, []).extend(errors)

        if api_conflicts:
            for idx, errors in api_conflicts.items():
                all_conflicts.setdefault(idx, []).extend(errors)

        if all_conflicts:
            conflict_records = [records[idx] for idx in sorted(all_conflicts.keys())]
            self.add_error_column_to_conflicts(conflict_records, all_conflicts, encoding=encoding, delimiter=delimiter)
            return True

        return False

    def get_conflict_file_path(self) -> Path:
        """Получить путь к файлу с конфликтами"""
        conflict_file_name = self.file_name.replace(".csv", "_conflicts.csv")
        return self.directory / conflict_file_name
