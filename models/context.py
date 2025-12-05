from dataclasses import MISSING, dataclass, field, fields
from typing import List, Union

from playwright.sync_api import APIRequestContext, Page

from models.user import EntrepreneurClient, IndividualClient, OrganizationClient


@dataclass
class TestContext:
    """Единый контекст для теста. Хранит информацию о клиенте, заявках, продуктах и технической информации о тесте. Можно использовать как в самом тесте, так и в методах.
    Клиент заполняется при вызове фикстур и обогащается в процессе других методов. Клиент содержит заявку. Заявка содержит продукт. Заявка заполняется по умолчанию одним продуктом категории mobile.
    Клиентов может быть несколько.
    client - это текущий клиент (поинтер), с которым работает тест. По умолчанию это первый элемент client_list.
    client_list - список клиентов. Для работы с одним из клиентов, переключается поинтер client на нужного из списка."""

    client: Union[EntrepreneurClient, IndividualClient, OrganizationClient] | None = None
    client_list: List[Union[EntrepreneurClient, IndividualClient, OrganizationClient]] = field(default_factory=list)
    allure_id: str = ""
    test_name: str = ""
    api_context: APIRequestContext = None
    api_context_list: List[APIRequestContext] = field(default_factory=list)
    page: Page = None
    page_list: List[Page] = field(default_factory=list)

    def __getattribute__(self, name: str) -> object:
        """По умолчанию client - первый элемент списка client_list."""
        value = super().__getattribute__(name)
        if name == "client":
            client = super().__getattribute__("client")
            client_list = super().__getattribute__("client_list")
            if client is None and client_list:
                return client_list[0]
        if name == "api_context":
            api_context = super().__getattribute__("api_context")
            api_context_list = super().__getattribute__("api_context_list")
            if api_context is None and api_context_list:
                return api_context_list[0]
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


test_context: TestContext = TestContext()
