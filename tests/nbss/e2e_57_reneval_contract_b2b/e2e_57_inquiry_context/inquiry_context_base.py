import allure
import pytest

from api.nbss.personal_account_requests import PersonalAccountRequests
from common.enums.topic import BaseTopic
from models.client import Agreement, OrganizationClient
from models.context import test_context
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.dynamic_forms.panel_toolbar.choose_request_topic_page import ChooseRequestTopicPage
from pages.nbss.dynamic_forms.panel_toolbar.panel_toolbar_page import PanelToolbarPage


class InquiryContextBase:
    """
    Базовый класс для тестов "E2E_57 Переоформление договора B2B (При переоформлении список Договоров ограничить
    контекстом лицевого счета)".

    Содержит общий сетап и вспомогательные методы, чтобы отдельные тест-кейсы не дублировали этот код.
    Построен по образцу DebtRestructuringBase
    """

    topic: BaseTopic = ""

    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login, create_organization: OrganizationClient) -> None:
        self.client_profile_page = ClientProfilePage()
        self.panel_toolbar_page = PanelToolbarPage()
        self.choose_request_topic_page = ChooseRequestTopicPage()
        self.personal_account_requests = PersonalAccountRequests()
        self.client = create_organization

    @allure.step("Создание договора с ЛС для клиента")
    def create_agreement_with_account(self, count: int = 1) -> None:
        for _ in range(count):
            self.personal_account_requests.create_agreement_and_account(test_context.client, status_id=1)

    def check_agreement_field(self, expected: str) -> None:
        self.choose_request_topic_page.check_agreement_field(self.topic, expected=expected)

    def check_account_field(self, expected: str) -> None:
        self.choose_request_topic_page.check_account_field(self.topic, expected=expected)

    def check_account_field_not_visible(self) -> None:
        self.choose_request_topic_page.check_account_field_not_visible(self.topic)

    def check_agreement_and_account_fields(self, agreement: Agreement) -> None:
        self.check_agreement_field(expected=agreement.number)
        self.check_account_field(expected=agreement.account.number)
