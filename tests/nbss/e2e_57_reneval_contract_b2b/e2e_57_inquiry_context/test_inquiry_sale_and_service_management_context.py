import allure
import pytest

from common.enums.topic import ActionTopic
from models.context import test_context
from tests.nbss.e2e_57_reneval_contract_b2b.e2e_57_inquiry_context.inquiry_context_base import InquiryContextBase


@allure.epic("E2E_57 Переоформление договора B2B")
@allure.suite("Уточнение контекста договора/ЛС в форме создания заявки")
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestInquirySaleAndServiceManagementContext(InquiryContextBase):
    topic = ActionTopic.SaleTopic

    @allure.title("09. Продажа и управление услугами (уточнение контекста договора)")
    @allure.id(859557)
    def test_clarify_agreement_context(self) -> None:
        self.create_agreement_with_account()
        self.client_profile_page.open_client_overview_page(test_context.client.user_id)

        self.panel_toolbar_page.open_create_request_form_with_topic(self.topic)
        self.check_agreement_field(expected="")

        self.client_profile_page.switch_to_agreement_context(test_context.client.agreement.number)
        self.check_agreement_field(expected=test_context.client.agreement.number)

    @allure.title("10. Продажа и управление услугами (без изменения контекста договора)")
    @allure.id(859558)
    def test_without_agreement_context_change(self) -> None:
        self.create_agreement_with_account()
        self.client_profile_page.open_agreement_page(test_context.client.agreement.id)

        self.panel_toolbar_page.open_create_request_form_with_topic(self.topic)
        self.check_agreement_field(expected=test_context.client.agreement.number)

    @allure.title("11. Продажа и управление услугами (с изменением контекста договора)")
    @allure.id(859559)
    def test_with_agreement_context_change(self) -> None:
        self.create_agreement_with_account(count=2)
        agreement_x, agreement_y = test_context.client.agreements

        self.client_profile_page.open_agreement_page(agreement_x.id)
        self.panel_toolbar_page.open_create_request_form_with_topic(self.topic)
        self.check_agreement_field(expected=agreement_x.number)

        self.client_profile_page.switch_to_agreement_context(agreement_y.number)
        self.check_agreement_field(expected=agreement_x.number)

    @allure.title("12. Продажа и управление услугами (переоткрытие формы после изменения контекста договора)")
    @allure.id(859560)
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

    @allure.title("13. Продажа и управление услугами (уточнение контекста ЛС)")
    @allure.id(859561)
    def test_clarify_account_context(self) -> None:
        self.create_agreement_with_account()
        self.client_profile_page.open_client_overview_page(test_context.client.user_id)

        self.panel_toolbar_page.open_create_request_form_with_topic(self.topic)
        self.check_agreement_field(expected="")
        self.check_account_field_not_visible()

        self.client_profile_page.switch_to_account_context(test_context.client.agreement.account.number)
        self.check_agreement_and_account_fields(agreement=test_context.client.agreement)

    @allure.title("14. Продажа и управление услугами (без изменения контекста ЛС)")
    @allure.id(859562)
    def test_without_account_context_change(self) -> None:
        self.create_agreement_with_account()
        self.client_profile_page.open_account_page(test_context.client.agreement.account.id)

        self.panel_toolbar_page.open_create_request_form_with_topic(self.topic)
        self.check_agreement_and_account_fields(agreement=test_context.client.agreement)

    @allure.title("15. Продажа и управление услугами (с изменением контекста ЛС)")
    @allure.id(859563)
    def test_with_account_context_change(self) -> None:
        self.create_agreement_with_account(count=2)
        agreement_x, agreement_y = test_context.client.agreements

        self.client_profile_page.open_account_page(agreement_x.account.id)
        self.panel_toolbar_page.open_create_request_form_with_topic(self.topic)
        self.check_agreement_and_account_fields(agreement=agreement_x)

        self.client_profile_page.switch_to_account_context(agreement_y.account.number)
        self.check_agreement_and_account_fields(agreement=agreement_x)

    @allure.title("16. Продажа и управление услугами (переоткрытие формы после изменения контекста ЛС)")
    @allure.id(859564)
    def test_reopen_form_after_account_context_change(self) -> None:
        self.create_agreement_with_account(count=2)
        agreement_x, agreement_y = test_context.client.agreements

        self.client_profile_page.open_account_page(agreement_x.account.id)
        self.panel_toolbar_page.open_create_request_form_with_topic(self.topic)
        self.check_agreement_and_account_fields(agreement=agreement_x)

        self.client_profile_page.switch_to_account_context(agreement_y.account.number)
        self.check_agreement_and_account_fields(agreement=agreement_x)

        self.panel_toolbar_page.close_create_request_form()
        self.panel_toolbar_page.open_create_request_form_with_topic(self.topic)
        self.check_agreement_and_account_fields(agreement=agreement_y)
