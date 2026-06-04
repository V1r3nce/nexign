from dataclasses import MISSING, dataclass, field, fields

import allure
from httpx import Client
from playwright.sync_api import APIRequestContext, Page

from common.enums.user import User
from models.client import EntrepreneurClient, IndividualClient, OrganizationClient


@dataclass
class TestContext:
    """Единый контекст для теста. Хранит информацию о клиенте, заявках, продуктах и технической информации о тесте. Можно использовать как в самом тесте, так и в методах.
    Клиент заполняется при вызове фикстур и обогащается в процессе других методов. Клиент содержит заявку. Заявка содержит продукт. Заявка заполняется по умолчанию одним продуктом категории mobile.
    Клиентов может быть несколько.
    client - это текущий клиент (поинтер), с которым работает тест. По умолчанию это первый элемент client_list.
    client_list - список клиентов. Для работы с одним из клиентов, переключается поинтер client на нужного из списка.
    api_context - контекст для работы с API.
    api_context_dict - словарь контекстов для работы с API. Где ключ это пользователь, а значение - контекст.
    page - страница браузера.
    page_list - список страниц браузера."""

    client: EntrepreneurClient | IndividualClient | OrganizationClient | None = None
    client_list: list[EntrepreneurClient | IndividualClient | OrganizationClient] = field(default_factory=list)
    allure_id: str = ""
    test_name: str = ""
    api_context: APIRequestContext | Client = None
    api_context_dict: dict[User, APIRequestContext | Client] = field(default_factory=dict)
    page: Page | None = None
    page_list: list[Page] = field(default_factory=list)

    def __getattribute__(self, name: str) -> object:
        """По умолчанию client - первый элемент списка client_list."""
        value = super().__getattribute__(name)
        if name == "client":
            client = super().__getattribute__("client")
            client_list = super().__getattribute__("client_list")
            if client is None and client_list:
                return client_list[0]
        if name == "page":
            page = super().__getattribute__("page")
            page_list = super().__getattribute__("page_list")
            if page is None and page_list:
                return page_list[0]
        return value

    def reset(self) -> None:
        """Сбрасывает все поля в значения по умолчанию."""
        for context_field in fields(self):
            if context_field.default_factory is not MISSING:
                value = context_field.default_factory()
            elif context_field.default is not MISSING:
                value = context_field.default
            else:
                value = None
            setattr(self, context_field.name, value)

    @allure.step("Переключение API контекста на пользователя {user}")
    def switch_api_context_to_user(self, user: User) -> None:
        if user in self.api_context_dict:
            self.api_context = self.api_context_dict[user]
        else:
            raise ValueError(f"Контекст для {user} не найден")


test_context: TestContext = TestContext()
