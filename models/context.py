from dataclasses import dataclass, field
from typing import List, Union

from models.user import EntrepreneurClient, IndividualClient, OrganizationClient


@dataclass
class TestContext:
    """Единый контекст для теста. Хранит информацию о клиенте, заявках, продуктах и технической информации о тесте. Можно использовать как в самом тесте, так и в методах.
    Клиент заполняется при вызове фикстур и обогащается в процессе других методов. Клиент содержит заявку. Заявка содержит продукт. Заявка заполняется по умолчанию одним продуктом категории mobile.
    Клиентов может быть несколько.
    client - это текущий клиент (поинтер), с которым работает тест. По умолчанию это первый элемент client_list.
    client_list - список клиентов. Для работы с одним из клиентов, переключается поинтер client на нужного из списка."""

    client: Union[EntrepreneurClient, IndividualClient, OrganizationClient] | None = field(default_factory=lambda: None)
    client_list: List[Union[EntrepreneurClient, IndividualClient, OrganizationClient]] = field(
        default_factory=lambda: []
    )
    allure_id: str = ""
    test_name: str = ""

    def __getattribute__(self, name: str) -> object:
        """По умолчанию client - первый элемент списка client_list."""
        value = super().__getattribute__(name)
        if name == "client":
            client = super().__getattribute__("client")
            client_list = super().__getattribute__("client_list")
            if client is None and client_list:
                return client_list[0]
        return value


test_context = TestContext()
