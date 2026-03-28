from pathlib import Path
from typing import Optional

import allure

from common.helpers.env_helper import DOWNLOAD_DIR
from sftp.exceptions import SFTPFileNotFound
from sftp.requests.sftp_base import SFTPBaseRequests
from sftp.requests.sftp_helper import SFTPFileHelper


class SFTPRequests(SFTPBaseRequests):
    """
    Класс для работы с SFTP сервером.
    Используется в связке с фикстурой create_sftp_connection.
    Пример использования: в setup тестового класса "self.sftp_requests = create_sftp_connection"
    и потом уже у возвращенного инстанса вызывать методы данного класса
    """

    def __init__(self, product_name: str = "nwm_ocs") -> None:
        """
        :param product_name: название продукта для получения хоста из standhelper
        """
        super().__init__(product_name)

    @allure.step("SFTP: Открытие файла {file_name}")
    def open_file(self, file_name: str, local_dir: Optional[Path] = None) -> SFTPFileHelper:
        """
        Метод для открытия файла с SFTP сервера.
        Скачивает файл с сервера и возвращает SFTPFileHelper для работы с ним.
        :param file_name: имя файла на сервере
        :param local_dir: локальная директория для сохранения (по умолчанию DOWNLOAD_DIR)
        :return: экземпляр SFTPFileHelper для работы с файлом
        """
        local_dir = local_dir or DOWNLOAD_DIR
        local_dir.mkdir(parents=True, exist_ok=True)
        local_path = local_dir / file_name

        # Проверяем существование файла на сервере
        if not self.file_exists(file_name):
            raise SFTPFileNotFound(f"Файл {file_name} не найден на SFTP сервере")

        # Скачиваем файл
        self.download_file(file_name, str(local_path))

        # Возвращаем helper для работы с файлом
        return SFTPFileHelper(file_name, local_dir)

    @allure.step("SFTP: Открытие CSV файла {file_name}")
    def open_csv_file(self, file_name: str, local_dir: Optional[Path] = None) -> SFTPFileHelper:
        """
        Метод для открытия CSV файла с SFTP сервера.
        Скачивает файл, проверяет его тип и возвращает SFTPFileHelper для работы с ним.
        :param file_name: имя CSV файла на сервере
        :param local_dir: локальная директория для сохранения (по умолчанию DOWNLOAD_DIR)
        :return: экземпляр SFTPFileHelper для работы с файлом
        """
        file_helper = self.open_file(file_name, local_dir)
        file_helper.check_file_type(".csv")
        return file_helper

    @allure.step("SFTP: Получение текущей директории")
    def get_current_directory(self) -> str:
        """
        Метод для получения текущей директории на SFTP сервере
        :return: путь к текущей директории
        """
        return self.sftp_client.getcwd()
