from dataclasses import dataclass, field
from typing import List

from models.inquiry import InquiryInfo
from models.user import BaseClient


@dataclass
class TestContext:
    """Единый контекст для теста. Хранит информацию о клиенте, заявках и технической информации о тесте. Можно использовать как в самом тесте, так и в методах.
    Клиент заполняется при вызове фикстур и обогащается в процессе других методов. Заявка заполняется при продаже (по умолчанию имеет часто используемые категории и id продуктов)."""

    client: BaseClient = field(default_factory=lambda: None)
    inquiry: InquiryInfo = field(default_factory=lambda: InquiryInfo("mobile", 500012))
    inquiry_list: List[InquiryInfo] = field(
        default_factory=lambda: [InquiryInfo("mobile", 500012), InquiryInfo("internet", 500004)]
    )
    test_id: str = ""
    allure_id: str = ""
    test_name: str = ""


test_context = TestContext()
