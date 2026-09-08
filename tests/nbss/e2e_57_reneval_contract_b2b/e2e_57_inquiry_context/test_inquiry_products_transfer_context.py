import allure
import pytest

from common.enums.topic import ActionTopic
from models.context import test_context
from tests.nbss.e2e_57_reneval_contract_b2b.e2e_57_inquiry_context.inquiry_context_base import InquiryContextBase


@allure.epic("E2E_57 Переоформление договора B2B")
@allure.suite("Уточнение контекста договора/ЛС в форме создания заявки")
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestInquiryAgreementContext(InquiryContextBase):
    topic = ActionTopic.TransferProducts

    @allure.title("01. Перенос продуктов на другие ЛС (уточнение контекста договора)")
    @allure.id(859549)
    def test_clarify_agreement_context(self) -> None:
        self.create_agreement_with_account()
        self.client_profile_page.open_client_overview_page(test_context.client.user_id)

        self.panel_toolbar_page.open_create_request_form_with_topic(self.topic)
        self.check_agreement_field(expected="")

        self.client_profile_page.switch_to_agreement_context(test_context.client.agreement.number)
        self.check_agreement_field(expected=test_context.client.agreement.number)

    @allure.title("02. Перенос продуктов на другие ЛС (без изменения контекста договора/ ЛС )")
    @allure.id(859550)
    def test_without_agreement_context_change(self) -> None:
        self.create_agreement_with_account()
        self.client_profile_page.open_agreement_page(test_context.client.agreement.id)

        self.panel_toolbar_page.open_create_request_form_with_topic(self.topic)
        self.check_agreement_field(expected=test_context.client.agreement.number)

    @allure.title("03. Перенос продуктов на другие ЛС (с изменением контекста договора/ ЛС )")
    @allure.id(859551)
    def test_with_agreement_context_change(self) -> None:
        self.create_agreement_with_account(count=2)
        agreement_x, agreement_y = test_context.client.agreements

        self.client_profile_page.open_agreement_page(agreement_x.id)
        self.panel_toolbar_page.open_create_request_form_with_topic(self.topic)
        self.check_agreement_field(expected=agreement_x.number)

        self.client_profile_page.switch_to_agreement_context(agreement_y.number)
        self.check_agreement_field(expected=agreement_x.number)

    @allure.title("04. Перенос продуктов на другие ЛС (переоткрытие формы после изменения контекста договора/ ЛС)")
    @allure.id(859552)
    def test_reopen_form_after_agreement_context_change(self) -> None:
        self.create_agreement_with_account(count=2)
        agreement_x, agreement_y = test_context.client.agreements

        self.client_profile_page.open_agreement_page(agreement_x.id)
        self.panel_toolbar_page.open_create_request_form_with_topic(self.topic)
        self.check_agreement_field(expected=agreement_x.number)

        self.client_profile_page.switch_to_agreement_context(agreement_y.number)
        self.check_agreement_field(expected=agreement_x.number)

        self.panel_toolbar_page.close_create_request_form()
        self.panel_toolbar_page.open_create_request_form_with_topic(self.topic)
        self.check_agreement_field(expected=agreement_y.number)
