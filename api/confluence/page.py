from atlassian import Confluence
from bs4 import BeautifulSoup

from common.helpers.env_helper import get_var_from_env


class ConfluencePage:
    """Класс для работы со страницами в Confluence"""

    CONFLUENCE_URL = get_var_from_env("CONFLUENCE_ENDPOINT")
    CONFLUENCE_USERNAME = get_var_from_env("CONFLUENCE_USERNAME")
    CONFLUENCE_PASSWORD = get_var_from_env("CONFLUENCE_PASSWORD")
    CONFLUENCE_PAGE_ID = get_var_from_env("CONFLUENCE_PAGE_ID")

    def __init__(self) -> None:
        self.conf = Confluence(
            url=self.CONFLUENCE_URL, username=self.CONFLUENCE_USERNAME, password=self.CONFLUENCE_PASSWORD
        )
        self.soup = BeautifulSoup(self.get_page_content_by_id(), "html.parser")

    def get_page_content_by_id(self) -> str:
        """Получение содержимого страницы по ID"""
        page = self.conf.get_page_by_id(self.CONFLUENCE_PAGE_ID, expand="body.storage")
        return str(page["body"]["storage"]["value"])

    def prepare_new_page_content(self, new_content: dict) -> str:
        """Подготовка нового содержимого страницы
        :param new_content: Словарь с данными для новой строки
        """
        table = self.soup.find("tbody")
        new_row = self.soup.new_tag("tr")

        for data_list in new_content.values():
            td = self.soup.new_tag("td")
            iterable = data_list if isinstance(data_list, list) else [data_list]

            for index, data in enumerate(iterable):
                if isinstance(data, dict):
                    for key, value in data.items():
                        a = self.soup.new_tag("a", href=value, string=f"{index}. " + key)
                        td.append(a)

                elif "http" in str(data):
                    a = self.soup.new_tag("a", href=data, string=data)
                    td.append(a)

                else:
                    td.append(str(data))

                td.append(self.soup.new_tag("br"))
                new_row.append(td)

        table.append(new_row)

        return str(self.soup)

    def update_page(self, new_content: str, page_title: str) -> dict:
        """Обновление содержимого страницы Confluence
        :param new_content: Строка с новым содержимым страницы
        :param page_title: Заголовок страницы"""
        result = self.conf.update_page(
            self.CONFLUENCE_PAGE_ID,
            page_title,
            new_content,
        )
        return result
