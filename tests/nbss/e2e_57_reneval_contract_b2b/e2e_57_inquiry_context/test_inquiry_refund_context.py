import allure
import pytest

from common.enums.topic import SettlementServiceTopic
from models.context import test_context
from tests.nbss.e2e_57_reneval_contract_b2b.e2e_57_inquiry_context.inquiry_context_base import InquiryContextBase


@allure.epic("E2E_57 Переоформление договора B2B")
@allure.suite("Уточнение контекста договора/ЛС в форме создания заявки")
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestInquiryRefundContext(InquiryContextBase):
    topic = SettlementServiceTopic.RefundOfFunds

    @allure.title("29. Возврат денежных средств (уточнение контекста ЛС)")
    @allure.id(859581)
    def test_clarify_account_context(self) -> None:
        self.create_agreement_with_account()
        self.client_profile_page.open_client_overview_page(test_context.client.user_id)

        self.panel_toolbar_page.open_create_request_form_with_topic(self.topic)
        self.check_account_field_not_visible()

        self.client_profile_page.switch_to_account_context(test_context.client.agreement.account.number)
        self.check_account_field(expected=test_context.client.agreement.account.number)

    @allure.title("30. Возврат денежных средств (без изменения контекста ЛС)")
    @allure.id(859582)
    def test_without_account_context_change(self) -> None:
        self.create_agreement_with_account()
        self.client_profile_page.open_account_page(test_context.client.agreement.account.id)

        self.panel_toolbar_page.open_create_request_form_with_topic(self.topic)
        self.check_account_field(expected=test_context.client.agreement.account.number)

    @allure.title("31. Возврат денежных средств (с изменением контекста ЛС)")
    @allure.id(859583)
    def test_with_account_context_change(self) -> None:
        self.create_agreement_with_account(count=2)
        agreement_x, agreement_y = test_context.client.agreements

        self.client_profile_page.open_account_page(agreement_x.account.id)
        self.panel_toolbar_page.open_create_request_form_with_topic(self.topic)
        self.check_account_field(expected=agreement_x.account.number)

        self.client_profile_page.switch_to_account_context(agreement_y.account.number)
        self.check_account_field(expected=agreement_x.account.number)

    @allure.title("32. Возврат денежных средств (переоткрытие формы после изменения контекста ЛС)")
    @allure.id(859584)
    def test_reopen_form_after_account_context_change(self) -> None:
        self.create_agreement_with_account(count=2)
        agreement_x, agreement_y = test_context.client.agreements

        self.client_profile_page.open_account_page(agreement_x.account.id)
        self.panel_toolbar_page.open_create_request_form_with_topic(self.topic)
        self.check_account_field(expected=agreement_x.account.number)

        self.client_profile_page.switch_to_account_context(agreement_y.account.number)
        self.check_account_field(expected=agreement_x.account.number)

        self.panel_toolbar_page.close_create_request_form()
        self.panel_toolbar_page.open_create_request_form_with_topic(self.topic)
        self.check_account_field(expected=agreement_y.account.number)
