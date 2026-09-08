import allure
import pytest

from common.enums.topic import SettlementServiceTopic
from models.context import test_context
from tests.nbss.e2e_57_reneval_contract_b2b.e2e_57_inquiry_context.inquiry_context_base import InquiryContextBase


@allure.epic("E2E_57 Переоформление договора B2B")
@allure.suite("Уточнение контекста договора/ЛС в форме создания заявки")
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestInquiryDebtRestructuringContext(InquiryContextBase):
    topic = SettlementServiceTopic.DebtRestructuring

    @allure.title("17. Реструктуризация долга (уточнение контекста договора)")
    @allure.id(859565)
    def test_clarify_agreement_context(self) -> None:
        self.create_agreement_with_account()
        self.client_profile_page.open_client_overview_page(test_context.client.user_id)

        self.panel_toolbar_page.open_create_request_form_with_topic(self.topic)
        self.check_agreement_field(expected="")

        self.client_profile_page.switch_to_agreement_context(test_context.client.agreement.number)
        self.check_agreement_field(expected=test_context.client.agreement.number)

    @allure.title("18. Реструктуризация долга (без изменения контекста договора)")
    @allure.id(859566)
    def test_without_agreement_context_change(self) -> None:
        self.create_agreement_with_account()
        self.client_profile_page.open_agreement_page(test_context.client.agreement.id)

        self.panel_toolbar_page.open_create_request_form_with_topic(self.topic)
        self.check_agreement_field(expected=test_context.client.agreement.number)

    @allure.title("19. Реструктуризация долга (с изменением контекста договора)")
    @allure.id(859567)
    def test_with_agreement_context_change(self) -> None:
        self.create_agreement_with_account(count=2)
        agreement_x, agreement_y = test_context.client.agreements

        self.client_profile_page.open_agreement_page(agreement_x.id)
        self.panel_toolbar_page.open_create_request_form_with_topic(self.topic)
        self.check_agreement_field(expected=agreement_x.number)

        self.client_profile_page.switch_to_agreement_context(agreement_y.number)
        self.check_agreement_field(expected=agreement_x.number)

    @allure.title("20. Реструктуризация долга (переоткрытие формы после изменения контекста договора)")
    @allure.id(859568)
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

    @allure.title("21. Реструктуризация долга (уточнение контекста ЛС)")
    @allure.id(859569)
    def test_clarify_account_context(self) -> None:
        self.create_agreement_with_account()
        self.client_profile_page.open_client_overview_page(test_context.client.user_id)

        self.panel_toolbar_page.open_create_request_form_with_topic(self.topic)
        self.check_agreement_field(expected="")
        self.check_account_field_not_visible()

        self.client_profile_page.switch_to_account_context(test_context.client.agreement.account.number)
        self.check_agreement_and_account_fields(agreement=test_context.client.agreement)

    @allure.title("22. Реструктуризация долга (без изменения контекста ЛС)")
    @allure.id(859570)
    def test_without_account_context_change(self) -> None:
        self.create_agreement_with_account()
        self.client_profile_page.open_account_page(test_context.client.agreement.account.id)

        self.panel_toolbar_page.open_create_request_form_with_topic(self.topic)
        self.check_agreement_and_account_fields(agreement=test_context.client.agreement)

    @allure.title("23. Реструктуризация долга (с изменением контекста ЛС)")
    @allure.id(859571)
    def test_with_account_context_change(self) -> None:
        self.create_agreement_with_account(count=2)
        agreement_x, agreement_y = test_context.client.agreements

        self.client_profile_page.open_account_page(agreement_x.account.id)
        self.panel_toolbar_page.open_create_request_form_with_topic(self.topic)
        self.check_agreement_and_account_fields(agreement=agreement_x)

        self.client_profile_page.switch_to_account_context(agreement_y.account.number)
        self.check_agreement_and_account_fields(agreement=agreement_x)

    @allure.title("24. Реструктуризация долга (переоткрытие формы после изменения контекста ЛС)")
    @allure.id(859572)
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
