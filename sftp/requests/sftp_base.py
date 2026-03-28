import logging
from typing import Any, Optional, Tuple, Type

import allure
import paramiko
from bs4 import BeautifulSoup

from api.base_requests import BaseRequests
from common.helpers.checker import check_that
from common.helpers.env_helper import BASE_URL_STANDHELPER, get_var_from_env
from sftp.exceptions import SFTPConnectionNotEstablished, SFTPDirectoryNotFound, SFTPFileNotFound, SFTPOperationFailed
from ssh.exceptions import StandhelperAppNotFound, StandhelperIsNotParsable


class SFTPBaseRequests(BaseRequests):
    """
    Базовый класс для работы с SFTP. Не надо создавать его инстанс!
    Требуется для наследования. Смотри SFTPRequests как пример использования.
    """

    def __init__(self, product_name: str) -> None:
        super().__init__()
        self.hostname = self.get_sftp_hostname(product_name)
        self.login = get_var_from_env("SSH_LOGIN")
        self.password = get_var_from_env("SSH_PASSWORD")
        paramiko_logger = logging.getLogger("paramiko")
        paramiko_logger.setLevel(logging.ERROR)
        self.curr_conn: Optional[paramiko.SSHClient] = None
        self.sftp_client: Optional[paramiko.SFTPClient] = None

    def __new__(cls: Type["SFTPBaseRequests"], *args: Any, **kwargs: Any) -> "SFTPBaseRequests":
        if cls is SFTPBaseRequests:
            raise TypeError("Cannot instantiate SFTPBase directly")
        return super().__new__(cls)

    @allure.step("API: Парсинг данных со standhelper")
    def _parse_standhelper_apps(self, page_html: str) -> Tuple[list, list]:
        """
        Внутренний метод для получения данных о распределении продуктов по хостам, а также названиях самих хостов.
        :param page_html: Страница apps standhelper
        :return: список хостов, список продуктов. Оба списка сформированы по столбцам
        """
        products = []
        soup = BeautifulSoup(page_html, "html.parser")
        table_header = soup.find("thead")
        check_that(
            lambda: table_header is not None, StandhelperIsNotParsable, "Не удалось получить таблицу из standhelper"
        )
        cells_header = table_header.find_all(["th"])
        hostnames = [cell.get_text() for cell in cells_header]
        table_body = soup.find("tbody")
        check_that(
            lambda: table_body is not None, StandhelperIsNotParsable, "Не удалось получить таблицу из standhelper"
        )
        rows = table_body.find_all("tr")
        for row_index, row in enumerate(rows):
            cells = row.find_all(["td", "th"])
            products.append([cell.get_text(strip=True) for cell in cells])
        return hostnames, products

    @allure.step("API: Получение данных о хосте")
    def get_sftp_hostname(self, product_name: str) -> str:
        """
        Метод для получения хоста по названию продукта
        :param product_name: название продукта
        :return: хост
        """
        response = self.get(f"{BASE_URL_STANDHELPER}/apps")
        self.check_response_status(response, 200, "Не удалось получить данные standhelper")
        hostnames, products = self._parse_standhelper_apps(response.text())
        for line in products:
            for index, product in enumerate(line):
                if product_name.upper() in product:
                    hostname = hostnames[index]
                    hostname = hostname.split(sep=" ")[2]
                    if "srv-app" in hostname:
                        hostname += ".nbss-redos-root.cloud.billing.ru"
                    return hostname
        raise StandhelperAppNotFound("Не удалось найти указанный продукт в реквизитах")

    @allure.step("SFTP: Установление соединения с хостом")
    def connect(self) -> None:
        """
        Метод для подключения. Используется в фикстуре
        """
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(self.hostname, username=self.login, password=self.password)
            self.curr_conn = ssh
            self.sftp_client = ssh.open_sftp()
        except Exception:
            raise SFTPConnectionNotEstablished(
                f"Не удалось установить соединение с хостом. Данные с которыми была попытка подключения: hostname:{self.hostname}\nuser:{self.login}\npassword:{self.password}\n"
            )

    @allure.step("SFTP: Закрытие соединения")
    def disconnect(self) -> None:
        """
        Метод для закрытия SFTP и SSH соединений
        """
        sftp = self.sftp_client
        self.sftp_client = None
        if sftp is not None:
            sftp.close()
        conn = self.curr_conn
        self.curr_conn = None
        if conn is not None:
            conn.close()

    @allure.step("SFTP: Переход в директорию {directory}")
    def change_directory(self, directory: str) -> None:
        """
        Метод для перехода в указанную директорию
        :param directory: путь к директории
        """
        try:
            self.sftp_client.chdir(directory)
        except OSError as e:
            raise SFTPDirectoryNotFound(f"Не удалось перейти в директорию {directory}: {str(e)}")

    @allure.step("SFTP: Получение списка файлов в текущей директории")
    def list_files(self) -> list:
        """
        Метод для получения списка файлов в текущей директории
        :return: список имен файлов
        """
        try:
            return self.sftp_client.listdir()
        except OSError as e:
            raise SFTPOperationFailed(f"Не удалось получить список файлов: {str(e)}")

    @allure.step("SFTP: Скачивание файла {remote_path} в {local_path}")
    def download_file(self, remote_path: str, local_path: str) -> None:
        """
        Метод для скачивания файла с SFTP сервера
        :param remote_path: путь к файлу на сервере
        :param local_path: локальный путь для сохранения
        """
        try:
            self.sftp_client.get(remote_path, local_path)
        except OSError as e:
            raise SFTPFileNotFound(f"Не удалось скачать файл {remote_path}: {str(e)}")

    @allure.step("SFTP: Загрузка файла {local_path} в {remote_path}")
    def upload_file(self, local_path: str, remote_path: str) -> None:
        """
        Метод для загрузки файла на SFTP сервер
        :param local_path: локальный путь к файлу
        :param remote_path: путь на сервере для сохранения
        """
        try:
            self.sftp_client.put(local_path, remote_path)
        except OSError as e:
            raise SFTPOperationFailed(f"Не удалось загрузить файл {local_path}: {str(e)}")

    @allure.step("SFTP: Проверка существования файла {filepath}")
    def file_exists(self, filepath: str) -> bool:
        """
        Метод для проверки существования файла на сервере
        :param filepath: путь к файлу
        :return: True если файл существует, False иначе
        """
        try:
            self.sftp_client.stat(filepath)
            return True
        except OSError:
            return False

    @allure.step("SFTP: Удаление файла {filepath}")
    def delete_file(self, filepath: str) -> None:
        """
        Метод для удаления файла с сервера
        :param filepath: путь к файлу
        """
        try:
            self.sftp_client.remove(filepath)
        except OSError as e:
            raise SFTPOperationFailed(f"Не удалось удалить файл {filepath}: {str(e)}")

    @allure.step("SFTP: Переименование/перемещение файла {old_path} в {new_path}")
    def rename_file(self, old_path: str, new_path: str) -> None:
        """
        Метод для переименования или перемещения файла
        :param old_path: старый путь к файлу
        :param new_path: новый путь к файлу
        """
        try:
            self.sftp_client.rename(old_path, new_path)
        except OSError as e:
            raise SFTPOperationFailed(f"Не удалось переименовать файл {old_path}: {str(e)}")
