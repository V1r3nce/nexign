import logging
from typing import Any, Tuple, Type

import allure
import paramiko
from bs4 import BeautifulSoup

from api.base_requests import BaseRequests
from common.helpers.checker import check_that
from common.helpers.env_helper import BASE_URL_STANDHELPER, get_var_from_env
from ssh.exceptions import SSHConnectionNotEstablished, StandhelperAppNotFound, StandhelperIsNotParsable


class SSHBaseRequests(BaseRequests):
    """
    Базовый класс для работы с SSH. Не надо создавать его инстанс!
    Требуется для наследования. Смотри SSHNWMRequests как пример использования.
    """

    def __init__(self, product_name: str) -> None:
        super().__init__()
        self.hostname = self.get_ssh_hostname(product_name)
        self.login = get_var_from_env("SSH_LOGIN")
        self.password = get_var_from_env("SSH_PASSWORD")
        paramiko_logger = logging.getLogger("paramiko")
        paramiko_logger.setLevel(logging.ERROR)
        self.curr_conn = None

    def __new__(cls: Type["SSHBaseRequests"], *args: Any, **kwargs: Any) -> "SSHBaseRequests":
        if cls is SSHBaseRequests:
            raise TypeError("Cannot instantiate SSHBase directly")
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
    def get_ssh_hostname(self, product_name: str) -> str:
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

    @allure.step("SSH: Установление соединения с хостом")
    def connect(self) -> None:
        """
        Метод для подключения. Используется в фикстуре
        """
        ssh = paramiko.SSHClient()
        # Костыль для автоматического добавления сертификата
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(self.hostname, username=self.login, password=self.password)
        except Exception:
            raise SSHConnectionNotEstablished(
                f"Не удалось установить соединение с хостом. Данные с которыми была попытка подключения: hostname:{self.hostname}\nuser:{self.login}\npassword:{self.password}\n"
            )
        self.curr_conn = ssh

    @allure.step("SSH: Выполнение команды")
    def process_single_cmd(self, cmd: str) -> Tuple[str, str]:
        """
        Метод для выполнения одной команды
        :param cmd: строчка - команда
        :return: std_out, std_err. Первая строчка - ответ на команду, если в ней или при ее выполнении не возникло ошибки. Вторая строчка - ошибки при выполнении.
        """
        ssh_stdin, ssh_stdout, ssh_stderr = self.curr_conn.exec_command(cmd)
        with ssh_stdin, ssh_stdout, ssh_stderr:
            result = ssh_stdout.read().decode()
            err = ssh_stderr.read().decode()
        return result, err

    @allure.step("SSH: Выполнение нескольких команд")
    def process_multiple_cmd(self, cmds: list) -> Tuple[str, str]:
        """
        Метод для выполнения нескольких команд последовательно
        :param cmds: список str. Каждая строчка - команда
        :return: std_out, std_err. Первая строчка - ответ на команды, если в них или при их выполнении не возникло ошибки. Вторая строчка - ошибки при выполнении.
        """
        ssh_stdin, ssh_stdout, ssh_stderr = self.curr_conn.exec_command(cmds[0])
        with ssh_stdin, ssh_stdout, ssh_stderr:
            for cmd_index in range(1, len(cmds)):
                ssh_stdin.write(cmds[cmd_index])
            ssh_stdin.flush()
            result = ssh_stdout.read().decode()
            err = ssh_stderr.read().decode()
        return result, err
